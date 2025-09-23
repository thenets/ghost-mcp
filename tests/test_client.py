"""Tests for Ghost API client."""

import pytest
from unittest.mock import AsyncMock, patch

from ghost_mcp.client import GhostClient
from ghost_mcp.config import config


class TestGhostClient:
    """Test Ghost API client."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = GhostClient()
        assert client.base_url.endswith("/")
        assert client.timeout == config.ghost.timeout

    def test_build_url(self):
        """Test URL building."""
        client = GhostClient()
        url = client._build_url("posts/", "content")
        assert url.endswith("ghost/api/content/posts/")

    def test_build_admin_url(self):
        """Test Admin API URL building."""
        client = GhostClient()
        url = client._build_url("posts/", "admin")
        assert url.endswith("ghost/api/admin/posts/")