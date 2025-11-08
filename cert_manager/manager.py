"""
Certificate Manager - Automatic HTTPS with Let's Encrypt
Handles certificate acquisition, renewal, and management
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import OpenSSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from acme import client, messages
from acme import challenges as acme_challenges
import josepy as jose

logger = logging.getLogger(__name__)


class CertificateManager:
    """
    Manages SSL/TLS certificates with automatic Let's Encrypt integration
    """
    
    def __init__(
        self,
        domain: str,
        email: str,
        cert_dir: str = "ssl/certs",
        account_dir: str = "ssl/accounts",
        staging: bool = False
    ):
        """
        Initialize certificate manager
        
        Args:
            domain: Domain name for certificate
            email: Email for Let's Encrypt account
            cert_dir: Directory to store certificates
            account_dir: Directory to store account keys
            staging: Use Let's Encrypt staging environment (for testing)
        """
        self.domain = domain
        self.email = email
        self.cert_dir = Path(cert_dir)
        self.account_dir = Path(account_dir)
        self.staging = staging
        
        # Create directories
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        self.account_dir.mkdir(parents=True, exist_ok=True)
        
        # Let's Encrypt URLs
        if staging:
            self.directory_url = "https://acme-staging-v02.api.letsencrypt.org/directory"
        else:
            self.directory_url = "https://acme-v02.api.letsencrypt.org/directory"
        
        # File paths
        self.cert_path = self.cert_dir / f"{domain}.crt"
        self.key_path = self.cert_dir / f"{domain}.key"
        self.chain_path = self.cert_dir / f"{domain}-chain.crt"
        self.fullchain_path = self.cert_dir / f"{domain}-fullchain.crt"
        self.account_key_path = self.account_dir / "account.key"
        
        # ACME client
        self.acme_client: Optional[client.ClientV2] = None
        
        # Challenge token storage (for HTTP-01 challenge)
        self.challenge_tokens: Dict[str, str] = {}
        
        logger.info(f"Certificate manager initialized for domain: {domain}")
    
    def get_account_key(self) -> jose.JWKRSA:
        """
        Get or create ACME account key
        """
        if self.account_key_path.exists():
            logger.info("Loading existing account key")
            with open(self.account_key_path, 'rb') as f:
                return jose.JWKRSA.load(f.read())
        else:
            logger.info("Generating new account key")
            rsa_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Save private key
            pem = rsa_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(self.account_key_path, 'wb') as f:
                f.write(pem)
            
            return jose.JWKRSA(key=rsa_key)
    
    def initialize_acme_client(self):
        """
        Initialize ACME client and register account if needed
        """
        account_key = self.get_account_key()
        
        # Create network client
        net = client.ClientNetwork(account_key, user_agent="FastProxy/1.0")
        
        # Get directory
        directory = client.ClientV2.get_directory(self.directory_url, net)
        self.acme_client = client.ClientV2(directory, net)
        
        # Register account
        try:
            registration = messages.NewRegistration.from_data(
                email=self.email,
                terms_of_service_agreed=True
            )
            account = self.acme_client.new_account(registration)
            logger.info(f"ACME account registered/retrieved: {account.uri}")
        except Exception as e:
            logger.error(f"Failed to register ACME account: {e}")
            raise
    
    def generate_csr(self) -> bytes:
        """
        Generate Certificate Signing Request (CSR)
        """
        # Generate private key if not exists
        if not self.key_path.exists():
            logger.info("Generating private key for certificate")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Save private key
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(self.key_path, 'wb') as f:
                f.write(pem)
        else:
            # Load existing key
            with open(self.key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        
        # Create CSR
        csr = x509.CertificateSigningRequestBuilder().subject_name(
            x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, self.domain),
            ])
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(self.domain),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), backend=default_backend())
        
        return csr.public_bytes(serialization.Encoding.DER)
    
    def request_certificate(self) -> bool:
        """
        Request certificate from Let's Encrypt using HTTP-01 challenge
        
        Returns:
            True if certificate was successfully obtained
        """
        if not self.acme_client:
            self.initialize_acme_client()
        
        logger.info(f"Requesting certificate for {self.domain}")
        
        # Create order
        order = self.acme_client.new_order(
            csr_pem=self.generate_csr()
        )
        
        # Process authorizations
        for authz in order.authorizations:
            # Get HTTP-01 challenge
            http_challenge = None
            for challenge in authz.body.challenges:
                if isinstance(challenge.chall, acme_challenges.HTTP01):
                    http_challenge = challenge
                    break
            
            if not http_challenge:
                logger.error("No HTTP-01 challenge found")
                return False
            
            # Store challenge token for HTTP server to serve
            token = http_challenge.chall.encode("token")
            key_authorization = http_challenge.chall.key_authorization(
                self.acme_client.net.key
            )
            self.challenge_tokens[token] = key_authorization
            
            logger.info(f"HTTP-01 challenge token: {token}")
            logger.info(f"Challenge should be accessible at: http://{self.domain}/.well-known/acme-challenge/{token}")
            
            # Answer challenge
            try:
                response = self.acme_client.answer_challenge(
                    http_challenge,
                    http_challenge.chall.response(self.acme_client.net.key)
                )
                logger.info(f"Challenge answered: {response}")
            except Exception as e:
                logger.error(f"Failed to answer challenge: {e}")
                return False
        
        # Finalize order
        try:
            finalized_order = self.acme_client.poll_and_finalize(order)
        except Exception as e:
            logger.error(f"Failed to finalize order: {e}")
            return False
        
        # Download certificate
        cert_pem = finalized_order.fullchain_pem
        
        # Save certificate
        with open(self.fullchain_path, 'w') as f:
            f.write(cert_pem)
        
        # Split into cert and chain
        certs = cert_pem.split('\n\n')
        if len(certs) >= 2:
            with open(self.cert_path, 'w') as f:
                f.write(certs[0] + '\n')
            with open(self.chain_path, 'w') as f:
                f.write('\n\n'.join(certs[1:]))
        
        logger.info(f"Certificate saved to {self.fullchain_path}")
        return True
    
    def get_challenge_response(self, token: str) -> Optional[str]:
        """
        Get challenge response for HTTP-01 validation
        
        Args:
            token: Challenge token
        
        Returns:
            Challenge response or None
        """
        return self.challenge_tokens.get(token)
    
    def certificate_exists(self) -> bool:
        """Check if certificate files exist"""
        return self.fullchain_path.exists() and self.key_path.exists()
    
    def get_certificate_expiry(self) -> Optional[datetime]:
        """
        Get certificate expiration date
        
        Returns:
            Expiration datetime or None if certificate doesn't exist
        """
        if not self.cert_path.exists():
            return None
        
        try:
            with open(self.cert_path, 'rb') as f:
                cert = x509.load_pem_x509_certificate(f.read(), default_backend())
                return cert.not_valid_after_utc
        except Exception as e:
            logger.error(f"Failed to read certificate expiry: {e}")
            return None
    
    def needs_renewal(self, days_before_expiry: int = 30) -> bool:
        """
        Check if certificate needs renewal
        
        Args:
            days_before_expiry: Renew certificate this many days before expiry
        
        Returns:
            True if renewal is needed
        """
        if not self.certificate_exists():
            return True
        
        expiry = self.get_certificate_expiry()
        if not expiry:
            return True
        
        renewal_date = expiry - timedelta(days=days_before_expiry)
        return datetime.now() >= renewal_date
    
    def renew_certificate(self) -> bool:
        """
        Renew certificate if needed
        
        Returns:
            True if renewal was successful or not needed
        """
        if not self.needs_renewal():
            logger.info(f"Certificate for {self.domain} doesn't need renewal yet")
            expiry = self.get_certificate_expiry()
            if expiry:
                logger.info(f"Certificate expires: {expiry}")
            return True
        
        logger.info(f"Renewing certificate for {self.domain}")
        return self.request_certificate()
    
    async def auto_renewal_task(self, check_interval_hours: int = 24):
        """
        Background task for automatic certificate renewal
        
        Args:
            check_interval_hours: Hours between renewal checks
        """
        logger.info(f"Starting auto-renewal task (checking every {check_interval_hours} hours)")
        
        while True:
            try:
                await asyncio.sleep(check_interval_hours * 3600)
                
                if self.needs_renewal():
                    logger.info("Certificate needs renewal, requesting new certificate...")
                    success = self.renew_certificate()
                    if success:
                        logger.info("✅ Certificate renewed successfully!")
                        # TODO: Reload server to use new certificate
                    else:
                        logger.error("❌ Certificate renewal failed!")
                else:
                    expiry = self.get_certificate_expiry()
                    if expiry:
                        days_left = (expiry - datetime.now()).days
                        logger.info(f"Certificate is valid for {days_left} more days")
            except Exception as e:
                logger.error(f"Error in auto-renewal task: {e}")
    
    def get_ssl_context(self):
        """
        Get SSL context for HTTPS server
        
        Returns:
            SSL context or None if certificates don't exist
        """
        if not self.certificate_exists():
            return None
        
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            str(self.fullchain_path),
            str(self.key_path)
        )
        
        # Configure for TLS 1.2+ and modern ciphers
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        
        return context
