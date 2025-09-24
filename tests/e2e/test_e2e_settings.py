"""End-to-end tests for Ghost settings functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestSettingsContentAPIE2E(BaseE2ETest):
    """Test settings Content API functionality end-to-end."""

    async def test_get_settings(self, mcp_server):
        """Test getting public settings."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Verify response structure
        assert "settings" in response
        assert isinstance(response["settings"], dict)

        # Should have multiple settings
        assert len(response["settings"]) > 0

        # Verify settings structure - settings is a dict with direct key-value pairs
        settings = response["settings"]
        # Check for some expected settings keys
        expected_keys = ["title", "description", "url"]
        for key in expected_keys:
            assert key in settings

    async def test_get_settings_essential_keys(self, mcp_server):
        """Test that essential settings keys are present."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Extract all setting keys
        setting_keys = list(response["settings"].keys())

        # Essential settings that should be present
        essential_keys = [
            "title",
            "description",
            "url",
            "timezone",
            "locale"
        ]

        # Verify essential keys are present
        for key in essential_keys:
            assert key in setting_keys, f"Essential setting '{key}' not found"

    async def test_get_settings_data_types(self, mcp_server):
        """Test that settings have correct data types."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Check data types for each setting
        for key, value in response["settings"].items():
            assert isinstance(key, str), f"Setting key should be string: {key}"
            # Value can be string, bool, int, list, or null
            assert value is None or isinstance(value, (str, bool, int, list, dict))

    async def test_get_settings_site_title(self, mcp_server):
        """Test that site title setting is accessible."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Check title setting
        assert "title" in response["settings"], "Should have title setting"

        title_value = response["settings"]["title"]
        assert isinstance(title_value, str)
        assert len(title_value) > 0, "Site title should not be empty"

    async def test_get_settings_site_url(self, mcp_server):
        """Test that site URL setting is accessible and valid."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Check url setting
        assert "url" in response["settings"], "Should have url setting"

        url_value = response["settings"]["url"]
        assert isinstance(url_value, str)
        assert url_value.startswith("http"), "Site URL should start with http"
        assert "localhost:2368" in url_value, "Should be localhost test instance"

    async def test_get_site_info(self, mcp_server):
        """Test getting basic site information."""
        from ghost_mcp.tools.content.settings import get_site_info

        # Get site info
        result = await get_site_info()
        response = json.loads(result)

        # Verify response structure
        assert "site_info" in response
        site = response["site_info"]

        # Verify essential site info fields
        essential_fields = ["title", "url", "version"]
        for field in essential_fields:
            assert field in site, f"Site info should include '{field}'"

    async def test_get_site_info_title_matches_settings(self, mcp_server):
        """Test that site info title matches settings title."""
        from ghost_mcp.tools.content.settings import get_site_info, get_settings

        # Get both site info and settings
        site_info_result = await get_site_info()
        settings_result = await get_settings()

        site_info_response = json.loads(site_info_result)
        settings_response = json.loads(settings_result)

        # Extract titles
        site_title = site_info_response["site_info"]["title"]
        settings_title = settings_response["settings"]["title"]

        # Titles should match
        assert site_title == settings_title, "Site info title should match settings title"

    async def test_get_site_info_url_matches_settings(self, mcp_server):
        """Test that site info URL matches settings URL."""
        from ghost_mcp.tools.content.settings import get_site_info, get_settings

        # Get both site info and settings
        site_info_result = await get_site_info()
        settings_result = await get_settings()

        site_info_response = json.loads(site_info_result)
        settings_response = json.loads(settings_result)

        # Extract URLs
        site_url = site_info_response["site_info"]["url"]
        settings_url = settings_response["settings"]["url"]

        # URLs should match
        assert site_url == settings_url, "Site info URL should match settings URL"

    async def test_get_site_info_version_format(self, mcp_server):
        """Test that site info includes valid Ghost version."""
        from ghost_mcp.tools.content.settings import get_site_info

        # Get site info
        result = await get_site_info()
        response = json.loads(result)

        site = response["site_info"]
        version = site["version"]

        # Version should be a non-empty string
        assert isinstance(version, str)
        assert len(version) > 0

        # Should contain a dot (version format like 5.x.x)
        assert "." in version, "Version should be in x.y.z format"

    async def test_settings_no_sensitive_data(self, mcp_server):
        """Test that settings don't expose sensitive information."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Extract all setting keys
        setting_keys = list(response["settings"].keys())

        # Keys that should NOT be present in public settings
        sensitive_keys = [
            "db_password",
            "mailgun_api_key",
            "admin_api_key",
            "content_api_key",
            "smtp_password",
            "oauth_client_secret"
        ]

        # Verify sensitive keys are not exposed
        for sensitive_key in sensitive_keys:
            assert sensitive_key not in setting_keys, f"Sensitive key '{sensitive_key}' should not be exposed"

    async def test_settings_readonly_access(self, mcp_server):
        """Test that Content API only provides read access to settings."""
        from ghost_mcp.tools.content.settings import get_settings

        # This test verifies that we can read settings but not modify them
        # through the Content API (which is read-only)

        # Get settings should work
        result = await get_settings()
        response = json.loads(result)

        # Should return valid settings
        assert "settings" in response
        assert len(response["settings"]) > 0

        # Note: Write operations would be through Admin API, which requires
        # separate authentication and is not typically exposed through MCP tools

    async def test_get_settings_pagination_metadata(self, mcp_server):
        """Test that settings include proper metadata structure."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Should have settings array
        assert "settings" in response

        # May or may not have meta depending on Ghost version,
        # but if present should be properly structured
        if "meta" in response:
            meta = response["meta"]
            assert isinstance(meta, dict)

    async def test_settings_timezone_format(self, mcp_server):
        """Test that timezone setting is in valid format."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Check timezone setting
        if "timezone" in response["settings"]:  # timezone might not always be present
            timezone_value = response["settings"]["timezone"]

            # Should be a string
            assert isinstance(timezone_value, str)

            # Common timezone formats
            valid_formats = [
                timezone_value.startswith("Etc/"),
                timezone_value.startswith("America/"),
                timezone_value.startswith("Europe/"),
                timezone_value.startswith("Asia/"),
                timezone_value == "UTC",
                "/" in timezone_value  # General timezone format
            ]

            assert any(valid_formats), f"Invalid timezone format: {timezone_value}"

    async def test_settings_locale_format(self, mcp_server):
        """Test that locale setting is in valid format."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Check locale setting
        if "locale" in response["settings"]:  # locale might not always be present
            locale_value = response["settings"]["locale"]

            # Should be a string
            assert isinstance(locale_value, str)
            assert len(locale_value) >= 2, "Locale should be at least 2 characters"

            # Common locale formats (en, en-US, etc.)
            # Should contain only letters, hyphens, and underscores
            import re
            assert re.match(r'^[a-zA-Z_-]+$', locale_value), f"Invalid locale format: {locale_value}"