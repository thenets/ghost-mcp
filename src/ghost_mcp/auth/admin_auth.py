"""Admin API authentication using JWT tokens."""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt

from ..config import config
from ..types.errors import AuthenticationError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AdminAuth:
    """Admin API JWT authentication handler."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize with optional API key override."""
        self.api_key = api_key or config.ghost.admin_api_key
        self._cached_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        if not self.api_key:
            logger.warning("No Admin API key configured")

    def get_auth_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        """Get authentication headers for Admin API requests."""
        token = self._get_jwt_token(request_id)
        return {"Authorization": f"Ghost {token}"}

    def _get_jwt_token(self, request_id: Optional[str] = None) -> str:
        """Get or generate JWT token for Admin API."""
        if not self.api_key:
            raise AuthenticationError(
                "Admin API key not configured",
                context="Admin API requires an API key for JWT generation",
                request_id=request_id,
            )

        # Check if we have a valid cached token
        if self._cached_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at - timedelta(seconds=30):
                logger.debug("Using cached JWT token", request_id=request_id)
                return self._cached_token

        # Generate new token
        token = self._generate_jwt_token(request_id)
        self._cached_token = token

        # JWT tokens expire after 5 minutes
        self._token_expires_at = datetime.now() + timedelta(minutes=5)

        logger.debug("Generated new JWT token", request_id=request_id)
        return token

    def _generate_jwt_token(self, request_id: Optional[str] = None) -> str:
        """Generate JWT token for Admin API authentication."""
        try:
            # Split the admin key (id:secret format)
            if ":" not in self.api_key:
                raise AuthenticationError(
                    "Invalid Admin API key format",
                    context="Admin API key must be in 'id:secret' format",
                    request_id=request_id,
                )

            key_id, secret = self.api_key.split(":", 1)

            # Current timestamp
            now = int(time.time())

            # JWT payload
            payload = {
                "iat": now,
                "exp": now + 300,  # 5 minutes from now
                "aud": "/admin/",
            }

            # JWT header
            header = {"alg": "HS256", "typ": "JWT", "kid": key_id}

            # Generate token
            token = jwt.encode(
                payload,
                bytes.fromhex(secret),
                algorithm="HS256",
                headers=header,
            )

            return token

        except Exception as e:
            raise AuthenticationError(
                f"Failed to generate JWT token: {e}",
                context="JWT token generation failed",
                request_id=request_id,
            ) from e

    def is_configured(self) -> bool:
        """Check if Admin API authentication is properly configured."""
        return bool(self.api_key and ":" in self.api_key)

    def validate_key_format(self) -> bool:
        """Validate the Admin API key format."""
        if not self.api_key:
            return False

        try:
            # Admin keys should be in 'id:secret' format
            if ":" not in self.api_key:
                return False

            key_id, secret = self.api_key.split(":", 1)

            # Key ID should be 24 character hex string
            if len(key_id) != 24 or not all(c in "0123456789abcdef" for c in key_id.lower()):
                return False

            # Secret should be 64 character hex string
            if len(secret) != 64 or not all(c in "0123456789abcdef" for c in secret.lower()):
                return False

            return True

        except Exception:
            return False

    def invalidate_cache(self) -> None:
        """Invalidate cached JWT token to force regeneration."""
        self._cached_token = None
        self._token_expires_at = None
        logger.debug("JWT token cache invalidated")