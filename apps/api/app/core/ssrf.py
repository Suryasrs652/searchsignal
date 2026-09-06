import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "instance-data",
    "169.254.169.254",
}

class SSRFSecurityError(Exception):
    pass

def is_ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP is private, loopback, link-local, multicast, or reserved."""
    return (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )

def validate_target_url(url: str, allow_local_test: bool = False) -> Tuple[bool, str]:
    """
    Validates a URL against SSRF attacks according to OWASP guidelines:
    - Enforces HTTP/HTTPS scheme only
    - Disallows userinfo (username:password@)
    - Rejects cloud metadata endpoints & localhost
    - Resolves DNS and blocks private/reserved IP ranges
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Invalid scheme: {parsed.scheme}. Only HTTP and HTTPS are permitted."

    if parsed.username or parsed.password:
        return False, "Credential-bearing URLs are strictly forbidden."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL."

    hostname_lower = hostname.lower()

    # If allow_local_test is True, permit localhost/127.0.0.1 for local synthetic testing
    if allow_local_test and (hostname_lower in ("localhost", "127.0.0.1", "::1")):
        return True, "Permitted for local test environment"

    if hostname_lower in BLOCKED_HOSTNAMES:
        return False, f"Access to restricted hostname '{hostname}' is blocked."

    # Try resolving hostname to IP addresses
    try:
        addr_infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
        for addr_info in addr_infos:
            ip_str = addr_info[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_blocked(ip_obj):
                return False, f"Destination resolves to blocked/internal IP: {ip_str}"
    except socket.gaierror:
        return False, f"Failed to resolve hostname: {hostname}"
    except Exception as e:
        return False, f"SSRF validation error: {e}"

    return True, "Safe"
