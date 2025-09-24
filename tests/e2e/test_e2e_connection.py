"""End-to-end tests for Ghost connection functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestConnectionE2E(BaseE2ETest):
    """Test Ghost connection functionality end-to-end."""

    async def test_check_ghost_connection_success(self, mcp_server):
        """Test successful Ghost connection check."""
        # Call the MCP tool
        result = await self.call_mcp_tool(mcp_server, "check_ghost_connection")

        # Parse the JSON result
        status = json.loads(result)

        # Verify connection status
        assert status["ghost_url"] == "http://localhost:2368/"
        assert status["content_api_configured"] is True
        assert status["admin_api_configured"] is True
        assert status["connection_test"] == "completed"
        assert status["content_api_status"] == "connected"
        assert status["admin_api_status"] == "connected"

    async def test_check_ghost_connection_config_fields(self, mcp_server):
        """Test that connection check returns all expected configuration fields."""
        result = await self.call_mcp_tool(mcp_server, "check_ghost_connection")
        status = json.loads(result)

        # Verify all expected fields are present
        expected_fields = {
            "ghost_url",
            "content_api_configured",
            "admin_api_configured",
            "mode",
            "connection_test",
            "content_api_status",
            "admin_api_status"
        }

        assert set(status.keys()) >= expected_fields

    async def test_connection_with_ghost_client(self, ghost_client):
        """Test direct connection using Ghost client."""
        # Test Content API connection
        response = await ghost_client._make_request("GET", "settings/", api_type="content")
        assert "settings" in response

        # Test Admin API connection
        response = await ghost_client._make_request("GET", "site/", api_type="admin")
        assert "site" in response

    async def test_ghost_instance_health(self, ghost_client):
        """Test that Ghost instance is healthy and responsive."""
        # Test getting site settings to verify the instance is functional
        response = await ghost_client._make_request("GET", "settings/", api_type="content")

        # Verify we get expected settings structure
        assert "settings" in response
        settings = response["settings"]

        # Check for some expected settings - settings is a dict, not a list
        expected_keys = ["title", "description", "url"]

        for key in expected_keys:
            assert key in settings

    async def test_api_version_compatibility(self, ghost_client):
        """Test that the API version is compatible."""
        # Make a request to test API version response headers
        response = await ghost_client._make_request("GET", "site/", api_type="admin")

        # Verify we get a proper response structure
        assert "site" in response
        site = response["site"]

        # Check for expected site fields
        expected_fields = ["title", "url", "version"]
        for field in expected_fields:
            assert field in site