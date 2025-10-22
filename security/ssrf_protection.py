"""
SSRF (Server-Side Request Forgery) Protection
Validates target URLs to prevent attacks on internal infrastructure
"""
import socket
import ipaddress
import logging
from urllib.parse import urlparse
from typing import List

logger = logging.getLogger(__name__)

# Blocked IP ranges (RFC 1918 private networks + special use)
BLOCKED_CIDRS = [
    ipaddress.ip_network('0.0.0.0/8'),       # "This" network
    ipaddress.ip_network('10.0.0.0/8'),      # Private network
    ipaddress.ip_network('127.0.0.0/8'),     # Loopback
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local (AWS/GCP metadata!)
    ipaddress.ip_network('172.16.0.0/12'),   # Private network
    ipaddress.ip_network('192.168.0.0/16'),  # Private network
    ipaddress.ip_network('224.0.0.0/4'),     # Multicast
    ipaddress.ip_network('240.0.0.0/4'),     # Reserved
    ipaddress.ip_network('::1/128'),         # IPv6 loopback
    ipaddress.ip_network('fe80::/10'),       # IPv6 link-local
    ipaddress.ip_network('fc00::/7'),        # IPv6 private
]

# Blocked hostnames
BLOCKED_HOSTNAMES = [
    'localhost',
    'metadata.google.internal',  # GCP metadata
    '169.254.169.254',            # AWS/Azure metadata
]


class SSRFValidationError(Exception):
    """Raised when URL fails SSRF validation"""
    pass


def validate_target_url(url: str) -> bool:
    """
    Validate target URL against SSRF attacks
    
    Prevents access to:
    - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Loopback addresses (127.0.0.0/8, ::1)
    - Link-local addresses (169.254.0.0/16) - AWS/GCP metadata!
    - Blocked hostnames
    
    Args:
        url: Target URL to validate
    
    Returns:
        True if URL is safe
    
    Raises:
        SSRFValidationError: If URL is potentially malicious
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise SSRFValidationError(
                f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed."
            )
        
        hostname = parsed.hostname
        if not hostname:
            raise SSRFValidationError("URL must contain a hostname")
        
        # Check against blocked hostnames
        hostname_lower = hostname.lower()
        for blocked in BLOCKED_HOSTNAMES:
            if blocked in hostname_lower:
                raise SSRFValidationError(
                    f"Blocked hostname detected: {hostname}"
                )
        
        # Resolve hostname to IP address
        try:
            ip_str = socket.gethostbyname(hostname)
        except socket.gaierror as e:
            raise SSRFValidationError(
                f"Unable to resolve hostname {hostname}: {e}"
            )
        
        # Parse IP address
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError as e:
            raise SSRFValidationError(
                f"Invalid IP address {ip_str}: {e}"
            )
        
        # Check against blocked CIDR ranges
        for cidr in BLOCKED_CIDRS:
            if ip_obj in cidr:
                raise SSRFValidationError(
                    f"Target URL resolves to blocked IP range: {ip_str} in {cidr}"
                )
        
        logger.info(f"✅ SSRF validation passed for {url} → {ip_str}")
        return True
        
    except SSRFValidationError:
        raise
    except Exception as e:
        raise SSRFValidationError(f"URL validation error: {e}")


def validate_route_targets(routes: List[dict]) -> bool:
    """
    Validate all route targets in configuration
    
    Args:
        routes: List of route dictionaries with 'target' keys
    
    Returns:
        True if all targets are valid
    
    Raises:
        SSRFValidationError: If any target is invalid
    """
    for idx, route in enumerate(routes):
        target = route.get('target')
        if not target:
            continue
        
        try:
            validate_target_url(target)
        except SSRFValidationError as e:
            raise SSRFValidationError(
                f"Route {idx} has invalid target: {e}"
            )
    
    return True

