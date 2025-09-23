"""Tests for Ghost MCP models and types."""

import pytest
from pydantic import ValidationError

from ghost_mcp.types.ghost import GhostPost, PostStatus, VisibilityType
from ghost_mcp.types.errors import GhostMCPError, ErrorCategory
from ghost_mcp.config import GhostConfig, LogLevel


class TestGhostModels:
    """Test Ghost data models."""

    def test_post_status_enum(self):
        """Test post status enumeration."""
        assert PostStatus.DRAFT == "draft"
        assert PostStatus.PUBLISHED == "published"
        assert PostStatus.SCHEDULED == "scheduled"

    def test_visibility_enum(self):
        """Test visibility enumeration."""
        assert VisibilityType.PUBLIC == "public"
        assert VisibilityType.MEMBERS == "members"


class TestErrorModels:
    """Test error models."""

    def test_ghost_mcp_error(self):
        """Test base error class."""
        error = GhostMCPError("Test error", ErrorCategory.NETWORK)
        assert error.category == ErrorCategory.NETWORK
        assert str(error) == "Test error"
        assert error.id is not None

    def test_error_to_dict(self):
        """Test error serialization."""
        error = GhostMCPError("Test error", ErrorCategory.VALIDATION, code="TEST_001")
        error_dict = error.to_dict()
        assert error_dict["message"] == "Test error"
        assert error_dict["category"] == "VALIDATION"
        assert error_dict["code"] == "TEST_001"


class TestConfig:
    """Test configuration models."""

    def test_ghost_config_defaults(self):
        """Test Ghost configuration defaults."""
        config = GhostConfig()
        assert str(config.url) == "http://localhost:2368"
        assert config.version == "v5.0"
        assert config.timeout == 30

    def test_log_level_enum(self):
        """Test log level enumeration."""
        assert LogLevel.INFO == "info"
        assert LogLevel.DEBUG == "debug"
        assert LogLevel.ERROR == "error"