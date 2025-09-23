"""Content API authentication using query parameter keys."""

from typing import Dict, Optional

from ..config import config
from ..types.errors import AuthenticationError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ContentAuth:
    """Content API authentication handler."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize with optional API key override."""
        self.api_key = api_key or config.ghost.content_api_key
        if not self.api_key:
            logger.warning("No Content API key configured")

    def get_auth_params(self, request_id: Optional[str] = None) -> Dict[str, str]:
        """Get authentication parameters for Content API requests."""
        if not self.api_key:
            raise AuthenticationError(
                "Content API key not configured",
                context="Content API requires an API key",
                request_id=request_id,
            )

        return {"key": self.api_key}

    def is_configured(self) -> bool:
        """Check if Content API authentication is properly configured."""
        return bool(self.api_key)

    def validate_key_format(self) -> bool:
        """Validate the API key format."""
        if not self.api_key:
            return False

        # Content API keys are typically 26 character hex strings
        return len(self.api_key) == 26 and all(
            c in "0123456789abcdef" for c in self.api_key.lower()
        )