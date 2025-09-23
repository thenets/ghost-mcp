"""Error types and categories for Ghost MCP server."""

import uuid
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCategory(str, Enum):
    """Error categories for comprehensive error handling."""
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    GHOST_API = "GHOST_API"
    MCP_PROTOCOL = "MCP_PROTOCOL"
    FILE_UPLOAD = "FILE_UPLOAD"
    VALIDATION = "VALIDATION"


class GhostMCPError(Exception):
    """Base error class for Ghost MCP server."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        code: Optional[str] = None,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.id = str(uuid.uuid4())
        self.category = category
        self.code = code
        self.context = context
        self.request_id = request_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging."""
        return {
            "id": self.id,
            "message": str(self),
            "category": self.category.value,
            "code": self.code,
            "context": self.context,
            "request_id": self.request_id,
        }


class NetworkError(GhostMCPError):
    """Network-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, ErrorCategory.NETWORK, "NETWORK_ERROR", context, request_id
        )


class AuthenticationError(GhostMCPError):
    """Authentication-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, ErrorCategory.AUTHENTICATION, "AUTH_ERROR", context, request_id
        )


class GhostApiError(GhostMCPError):
    """Ghost API-related errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, ErrorCategory.GHOST_API, code, context, request_id)


class ValidationError(GhostMCPError):
    """Validation-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, ErrorCategory.VALIDATION, "VALIDATION_ERROR", context, request_id
        )


class FileUploadError(GhostMCPError):
    """File upload-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, ErrorCategory.FILE_UPLOAD, "FILE_UPLOAD_ERROR", context, request_id
        )


class MCPProtocolError(GhostMCPError):
    """MCP protocol-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, ErrorCategory.MCP_PROTOCOL, "MCP_ERROR", context, request_id
        )