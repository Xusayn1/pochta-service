"""
Django request utilities for extracting host and client IP information.
"""

from typing import Optional

from django.http import HttpRequest


def get_current_host(request: HttpRequest) -> Optional[str]:
    """
    Get the full host URL (scheme + host) from a Django request.
    Args:
        request: Django HttpRequest object
    Returns:
        Full URL with scheme (e.g., 'https://example.com') or None if request is invalid
    """
    if not request:
        return None

    # Determine protocol based on request security
    scheme = 'https' if request.is_secure() else 'http'

    # Get host from request (includes port if non-standard)
    host = request.get_host()

    return f"{scheme}://{host}"


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Extract the real client IP address from a Django request.
    Args:
        request: Django HttpRequest object
    Returns:
        Client IP address as string, or None if not found

    """
    if not request:
        return None

    # Check X-Forwarded-For header first (for proxied requests)
    # Format: "client_ip, proxy1_ip, proxy2_ip"
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        # Take the first IP (original client) and clean whitespace
        return x_forwarded_for.split(',')[0].strip()

    # Fallback to direct connection IP
    return request.META.get('REMOTE_ADDR')