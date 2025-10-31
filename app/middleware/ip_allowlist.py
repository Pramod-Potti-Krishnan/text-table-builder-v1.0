"""
IP Allowlist Middleware
=======================

Restricts API access to authorized IP addresses only.

Security feature to prevent unauthorized access to the Text Service API.
Health check endpoint (/health) is always accessible for Railway monitoring.
"""

import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class IPAllowlistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict API access to allowed IP addresses.

    Features:
    - IP-based access control
    - Health check exemption
    - X-Forwarded-For header support (Railway proxy)
    - Detailed logging for security audit
    """

    def __init__(self, app, allowed_ips: list[str]):
        """
        Initialize IP allowlist middleware.

        Args:
            app: FastAPI application
            allowed_ips: List of allowed IP addresses
        """
        super().__init__(app)
        self.allowed_ips = set(allowed_ips)
        logger.info(f"🔒 IP Allowlist enabled with {len(self.allowed_ips)} allowed IPs: {', '.join(self.allowed_ips)}")

    async def dispatch(self, request: Request, call_next):
        """
        Process each request and check IP authorization.

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response or HTTPException
        """
        # Get client IP (handle both direct and proxy scenarios)
        client_ip = request.client.host if request.client else "unknown"

        # Check X-Forwarded-For header (Railway uses this)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain (original client IP)
            client_ip = forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header (alternative proxy header)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip.strip()

        # Always allow health check endpoint (for Railway monitoring)
        if request.url.path == "/health":
            logger.debug(f"✅ Health check allowed from IP: {client_ip}")
            return await call_next(request)

        # Check if IP is in allowlist
        if client_ip not in self.allowed_ips:
            logger.warning(f"🚫 Access denied for IP: {client_ip} | Path: {request.url.path} | Method: {request.method}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Access Denied",
                    "message": f"Your IP address ({client_ip}) is not authorized to access this service.",
                    "hint": "Contact the service administrator to whitelist your IP address."
                }
            )

        logger.debug(f"✅ Access granted for IP: {client_ip} | Path: {request.url.path}")
        return await call_next(request)
