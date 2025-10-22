"""
TLS/HTTPS Configuration Module
Provides utilities for running FastProxy with SSL/TLS support
"""
import os
import ssl
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def create_ssl_context(
    certfile: Optional[str] = None,
    keyfile: Optional[str] = None
) -> Optional[ssl.SSLContext]:
    """
    Create SSL context for HTTPS support
    
    Args:
        certfile: Path to SSL certificate file (default: from env FASTPROXY_SSL_CERT)
        keyfile: Path to SSL key file (default: from env FASTPROXY_SSL_KEY)
    
    Returns:
        SSLContext if certificates are available, None otherwise
    
    Environment Variables:
        FASTPROXY_SSL_CERT: Path to SSL certificate
        FASTPROXY_SSL_KEY: Path to SSL key
        FASTPROXY_SSL_CA_BUNDLE: Optional path to CA bundle
    
    Example:
        # Using environment variables
        export FASTPROXY_SSL_CERT=/path/to/cert.pem
        export FASTPROXY_SSL_KEY=/path/to/key.pem
        
        # Run with SSL
        python main.py  # Will detect env vars and enable HTTPS
    """
    # Get certificate paths from environment or parameters
    cert_path = certfile or os.getenv("FASTPROXY_SSL_CERT")
    key_path = keyfile or os.getenv("FASTPROXY_SSL_KEY")
    ca_bundle = os.getenv("FASTPROXY_SSL_CA_BUNDLE")
    
    # Check if SSL is configured
    if not cert_path or not key_path:
        logger.warning(
            "⚠️  SSL/TLS not configured. Running in HTTP mode. "
            "Set FASTPROXY_SSL_CERT and FASTPROXY_SSL_KEY for HTTPS."
        )
        return None
    
    # Validate certificate files exist
    cert_file = Path(cert_path)
    key_file = Path(key_path)
    
    if not cert_file.exists():
        logger.error(f"❌ SSL certificate not found: {cert_path}")
        return None
    
    if not key_file.exists():
        logger.error(f"❌ SSL key not found: {key_path}")
        return None
    
    # Create SSL context
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Set minimum TLS version (TLS 1.2+)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Load certificate and key
        ssl_context.load_cert_chain(
            certfile=str(cert_file),
            keyfile=str(key_file)
        )
        
        # Load CA bundle if provided
        if ca_bundle and Path(ca_bundle).exists():
            ssl_context.load_verify_locations(cafile=ca_bundle)
            logger.info(f"✅ Loaded CA bundle: {ca_bundle}")
        
        # Set secure cipher suites
        ssl_context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")
        
        logger.info(f"✅ SSL/TLS enabled with certificate: {cert_path}")
        logger.info(f"   Minimum TLS version: {ssl_context.minimum_version.name}")
        
        return ssl_context
        
    except Exception as e:
        logger.error(f"❌ Failed to create SSL context: {e}")
        return None


def get_ssl_port() -> int:
    """
    Get SSL port from environment or default to 8443
    
    Returns:
        Port number for HTTPS
    """
    return int(os.getenv("FASTPROXY_SSL_PORT", "8443"))


def is_ssl_enabled() -> bool:
    """
    Check if SSL/TLS is configured
    
    Returns:
        True if SSL certificates are configured
    """
    cert_path = os.getenv("FASTPROXY_SSL_CERT")
    key_path = os.getenv("FASTPROXY_SSL_KEY")
    
    return bool(cert_path and key_path)


# Self-signed certificate generation (for development only!)
def generate_self_signed_cert(
    cert_file: str = "certs/cert.pem",
    key_file: str = "certs/key.pem",
    days: int = 365
):
    """
    Generate self-signed certificate for development/testing
    
    ⚠️  WARNING: NEVER use self-signed certificates in production!
    
    Args:
        cert_file: Output path for certificate
        key_file: Output path for private key
        days: Certificate validity in days
    
    Requires:
        pip install cryptography
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from datetime import datetime, timedelta
        
        # Create output directory
        cert_path = Path(cert_file)
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FastProxy Dev"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        logger.info(f"✅ Generated self-signed certificate:")
        logger.info(f"   Certificate: {cert_file}")
        logger.info(f"   Private Key: {key_file}")
        logger.warning("⚠️  Self-signed certificate for DEVELOPMENT ONLY!")
        
    except ImportError:
        logger.error("❌ cryptography package not installed. Run: pip install cryptography")
    except Exception as e:
        logger.error(f"❌ Failed to generate certificate: {e}")


if __name__ == "__main__":
    # For testing - generate self-signed cert
    import ipaddress
    generate_self_signed_cert()

