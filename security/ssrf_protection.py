"""
SSRF (Server-Side Request Forgery) Protection
Validates target URLs to prevent attacks on internal infrastructure
"""
import socket
import ipaddress
import logging
import os
from urllib.parse import urlparse
from typing import List

logger = logging.getLogger(__name__)

# Check if private IPs should be allowed (for internal proxying)
ALLOW_PRIVATE_IPS = os.environ.get('FASTPROXY_ALLOW_PRIVATE_IPS', 'false').lower() == 'true'

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

# Always block metadata endpoints
ALWAYS_BLOCKED_CIDRS = [
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local (AWS/GCP metadata!)
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
    - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) - unless ALLOW_PRIVATE_IPS=true
    - Loopback addresses (127.0.0.0/8, ::1) - unless ALLOW_PRIVATE_IPS=true
    - Link-local addresses (169.254.0.0/16) - ALWAYS BLOCKED (metadata!)
    - Blocked hostnames
    
    Args:
        url: Target URL to validate
        
    Returns:
        True if URL is safe
        
    Raises:
        SSRFValidationError: If URL fails validation
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        raise SSRFValidationError("Invalid URL: no hostname")
    
    # Check blocked hostnames
    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise SSRFValidationError(f"Blocked hostname: {hostname}")
    
    try:
        # Resolve hostname to IP
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        
        # Always block metadata endpoints
        for cidr in ALWAYS_BLOCKED_CIDRS:
            if ip in cidr:
                raise SSRFValidationError(
                    f"Target URL resolves to blocked IP range: {ip} in {cidr}"
                )
        
        # If private IPs are allowed, skip other checks
        if ALLOW_PRIVATE_IPS:
            logger.info(f"Private IP access allowed for {ip}")
            return True
        
        # Check against blocked CIDR ranges
        for cidr in BLOCKED_CIDRS:
            if ip in cidr:
                raise SSRFValidationError(
                    f"Target URL resolves to blocked IP range: {ip} in {cidr}"
                )
                
    except socket.gaierror:
        raise SSRFValidationError(f"Could not resolve hostname: {hostname}")
    except ValueError as e:
        raise SSRFValidationError(f"Invalid IP address: {e}")
    
    return True


def validate_route_targets(routes: List[dict]) -> bool:
    """
    Validate all route targets in configuration
    
    Args:
        routes: List of route dictionaries with 'target' keys
        
    Returns:
        True if all targets are safe
        
    Raises:
        SSRFValidationError: If any target fails validation
    """
    for idx, route in enumerate(routes):
        target = route.get('target')
        if not target:
            continue
            
        try:
            validate_target_url(target)
        except SSRFValidationError as e:
            raise SSRFValidationError(f"Route {idx} has invalid target: {e}")
    
    return True
