"""
Automatic SSL Certificate Management (Caddy-like)
Automatically obtains and renews Let's Encrypt certificates

Features:
- Zero-configuration SSL
- Automatic certificate provisioning
- Automatic renewal (60 days before expiry)
- HTTP-01 challenge support
- Certificate caching
"""
import os
import ssl
import logging
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import threading

logger = logging.getLogger(__name__)


class AutoSSL:
    """
    Automatic SSL certificate manager (Caddy-like)
    
    Usage:
        auto_ssl = AutoSSL(domain="example.com", email="admin@example.com")
        ssl_context = auto_ssl.get_ssl_context()
    """
    
    def __init__(
        self,
        domain: Optional[str] = None,
        email: Optional[str] = None,
        cert_dir: str = "./certs",
        auto_renew: bool = True
    ):
        """
        Initialize AutoSSL
        
        Args:
            domain: Domain name (e.g., "example.com")
            email: Email for Let's Encrypt notifications
            cert_dir: Directory to store certificates
            auto_renew: Enable automatic renewal
        """
        self.domain = domain or os.getenv("FASTPROXY_DOMAIN")
        self.email = email or os.getenv("FASTPROXY_SSL_EMAIL")
        self.cert_dir = Path(cert_dir)
        self.auto_renew = auto_renew
        
        # Certificate paths
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        self.cert_file = self.cert_dir / f"{self.domain}.crt"
        self.key_file = self.cert_dir / f"{self.domain}.key"
        self.fullchain_file = self.cert_dir / f"{self.domain}.fullchain.crt"
        
        # Renewal settings
        self.renewal_days = 30  # Renew 30 days before expiry
        self.renewal_thread = None
        
        logger.info(f"AutoSSL initialized for domain: {self.domain}")
    
    def is_enabled(self) -> bool:
        """Check if auto-SSL is enabled"""
        return bool(self.domain and self.email)
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Get SSL context (auto-provisions certificate if needed)
        
        Returns:
            SSLContext or None if provisioning fails
        """
        if not self.is_enabled():
            logger.warning("AutoSSL not enabled. Set FASTPROXY_DOMAIN and FASTPROXY_SSL_EMAIL")
            return None
        
        # Check if certificate exists and is valid
        if self._has_valid_certificate():
            logger.info("✅ Using existing valid certificate")
            return self._create_ssl_context()
        
        # Provision new certificate
        logger.info("📜 No valid certificate found. Provisioning new certificate...")
        if self._provision_certificate():
            logger.info("✅ Certificate provisioned successfully!")
            
            # Start auto-renewal thread
            if self.auto_renew:
                self._start_renewal_thread()
            
            return self._create_ssl_context()
        else:
            logger.error("❌ Failed to provision certificate")
            return None
    
    def _has_valid_certificate(self) -> bool:
        """Check if certificate exists and is valid"""
        if not self.cert_file.exists() or not self.key_file.exists():
            return False
        
        try:
            # Check certificate expiry
            cert_expiry = self._get_certificate_expiry()
            if cert_expiry is None:
                return False
            
            days_until_expiry = (cert_expiry - datetime.now()).days
            
            if days_until_expiry <= self.renewal_days:
                logger.warning(
                    f"⚠️  Certificate expires in {days_until_expiry} days. "
                    f"Renewal needed."
                )
                return False
            
            logger.info(f"✅ Certificate valid for {days_until_expiry} more days")
            return True
            
        except Exception as e:
            logger.error(f"Error checking certificate: {e}")
            return False
    
    def _get_certificate_expiry(self) -> Optional[datetime]:
        """Get certificate expiration date"""
        try:
            import OpenSSL
            
            with open(self.cert_file, 'rb') as f:
                cert_data = f.read()
            
            cert = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM,
                cert_data
            )
            
            expiry_str = cert.get_notAfter().decode('utf-8')
            expiry = datetime.strptime(expiry_str, '%Y%m%d%H%M%SZ')
            
            return expiry
            
        except ImportError:
            logger.warning("pyOpenSSL not installed. Cannot check expiry.")
            return None
        except Exception as e:
            logger.error(f"Error reading certificate expiry: {e}")
            return None
    
    def _provision_certificate(self) -> bool:
        """
        Provision new certificate using certbot
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"🔒 Requesting Let's Encrypt certificate for {self.domain}...")
        
        # Check if certbot is installed
        if not self._is_certbot_installed():
            logger.error(
                "❌ certbot not found. Install it with: "
                "sudo apt-get install certbot (Linux) or brew install certbot (macOS)"
            )
            return False
        
        # Use certbot in standalone mode
        # Note: This requires port 80 to be available
        try:
            cmd = [
                "certbot", "certonly",
                "--standalone",
                "--non-interactive",
                "--agree-tos",
                "--email", self.email,
                "--domains", self.domain,
                "--cert-path", str(self.cert_file),
                "--key-path", str(self.key_file),
                "--fullchain-path", str(self.fullchain_file),
            ]
            
            # If not running as root, use --config-dir for user-owned certs
            if os.geteuid() != 0:
                config_dir = self.cert_dir / "letsencrypt"
                config_dir.mkdir(exist_ok=True)
                cmd.extend([
                    "--config-dir", str(config_dir),
                    "--work-dir", str(config_dir / "work"),
                    "--logs-dir", str(config_dir / "logs"),
                ])
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✅ Certificate obtained successfully!")
                
                # Copy certs to our directory (if using system certbot)
                self._copy_system_certs()
                
                return True
            else:
                logger.error(f"❌ certbot failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ certbot timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error provisioning certificate: {e}")
            return False
    
    def _copy_system_certs(self):
        """Copy certificates from system certbot location"""
        try:
            system_cert_dir = Path(f"/etc/letsencrypt/live/{self.domain}")
            
            if system_cert_dir.exists():
                import shutil
                
                # Copy certificate files
                if (system_cert_dir / "fullchain.pem").exists():
                    shutil.copy(
                        system_cert_dir / "fullchain.pem",
                        self.fullchain_file
                    )
                    shutil.copy(
                        system_cert_dir / "fullchain.pem",
                        self.cert_file
                    )
                
                if (system_cert_dir / "privkey.pem").exists():
                    shutil.copy(
                        system_cert_dir / "privkey.pem",
                        self.key_file
                    )
                
                logger.info(f"✅ Copied certificates to {self.cert_dir}")
        except Exception as e:
            logger.warning(f"Could not copy system certs: {e}")
    
    def _is_certbot_installed(self) -> bool:
        """Check if certbot is installed"""
        try:
            result = subprocess.run(
                ["certbot", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context from certificate files"""
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Use fullchain if available, otherwise regular cert
            cert_path = self.fullchain_file if self.fullchain_file.exists() else self.cert_file
            
            ssl_context.load_cert_chain(
                certfile=str(cert_path),
                keyfile=str(self.key_file)
            )
            
            # Set secure cipher suites
            ssl_context.set_ciphers(
                "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
            )
            
            logger.info(f"✅ SSL context created successfully")
            return ssl_context
            
        except Exception as e:
            logger.error(f"❌ Failed to create SSL context: {e}")
            raise
    
    def _start_renewal_thread(self):
        """Start background thread for automatic renewal"""
        if self.renewal_thread and self.renewal_thread.is_alive():
            logger.info("Renewal thread already running")
            return
        
        def renewal_loop():
            logger.info("🔄 Starting automatic renewal thread")
            
            while True:
                try:
                    # Check every 24 hours
                    import time
                    time.sleep(86400)  # 24 hours
                    
                    logger.info("🔍 Checking certificate expiry...")
                    
                    if not self._has_valid_certificate():
                        logger.info("🔄 Certificate needs renewal. Renewing...")
                        
                        if self._provision_certificate():
                            logger.info("✅ Certificate renewed successfully!")
                        else:
                            logger.error("❌ Certificate renewal failed!")
                    
                except Exception as e:
                    logger.error(f"Error in renewal thread: {e}")
        
        self.renewal_thread = threading.Thread(
            target=renewal_loop,
            daemon=True,
            name="AutoSSL-Renewal"
        )
        self.renewal_thread.start()
        
        logger.info("✅ Automatic renewal thread started")
    
    def renew_now(self) -> bool:
        """Manually trigger certificate renewal"""
        logger.info("🔄 Manual renewal triggered")
        return self._provision_certificate()


# Simplified interface for easy integration
def get_auto_ssl_context(
    domain: Optional[str] = None,
    email: Optional[str] = None
) -> Optional[ssl.SSLContext]:
    """
    Get SSL context with automatic certificate provisioning
    
    Environment Variables:
        FASTPROXY_DOMAIN: Your domain name
        FASTPROXY_SSL_EMAIL: Email for Let's Encrypt
        FASTPROXY_AUTO_SSL: Enable auto-SSL (default: true if domain/email set)
    
    Args:
        domain: Domain name (optional, uses env var)
        email: Email address (optional, uses env var)
    
    Returns:
        SSLContext or None
    
    Example:
        # Set environment variables
        export FASTPROXY_DOMAIN=example.com
        export FASTPROXY_SSL_EMAIL=admin@example.com
        
        # Get SSL context (automatically provisions cert)
        ssl_context = get_auto_ssl_context()
    """
    auto_ssl = AutoSSL(domain=domain, email=email)
    
    if not auto_ssl.is_enabled():
        logger.warning(
            "⚠️  Auto-SSL not enabled. Set FASTPROXY_DOMAIN and FASTPROXY_SSL_EMAIL"
        )
        return None
    
    return auto_ssl.get_ssl_context()


if __name__ == "__main__":
    # Test auto-SSL
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing AutoSSL...")
    print("Note: This will attempt to get a real Let's Encrypt certificate!")
    print("Requirements:")
    print("  1. certbot must be installed")
    print("  2. Port 80 must be available")
    print("  3. Domain must point to this server")
    print()
    
    domain = input("Enter domain name (e.g., example.com): ")
    email = input("Enter email address: ")
    
    auto_ssl = AutoSSL(domain=domain, email=email)
    ssl_context = auto_ssl.get_ssl_context()
    
    if ssl_context:
        print("✅ Success! SSL context created.")
        print(f"Certificate: {auto_ssl.cert_file}")
        print(f"Key: {auto_ssl.key_file}")
    else:
        print("❌ Failed to create SSL context")

