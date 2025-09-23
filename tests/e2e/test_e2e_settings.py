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
        assert isinstance(response["settings"], list)

        # Should have multiple settings
        assert len(response["settings"]) > 0

        # Verify settings structure
        setting = response["settings"][0]
        essential_fields = ["key", "value"]
        for field in essential_fields:
            assert field in setting

    async def test_get_settings_essential_keys(self, mcp_server):
        """Test that essential settings keys are present."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Extract all setting keys
        setting_keys = [setting["key"] for setting in response["settings"]]

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
        for setting in response["settings"]:
            assert isinstance(setting["key"], str), f"Setting key should be string: {setting}"
            # Value can be string, bool, or null
            assert setting["value"] is None or isinstance(setting["value"], (str, bool, int))

    async def test_get_settings_site_title(self, mcp_server):
        """Test that site title setting is accessible."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Find title setting
        title_settings = [s for s in response["settings"] if s["key"] == "title"]
        assert len(title_settings) == 1, "Should have exactly one title setting"

        title_setting = title_settings[0]
        assert isinstance(title_setting["value"], str)
        assert len(title_setting["value"]) > 0, "Site title should not be empty"

    async def test_get_settings_site_url(self, mcp_server):
        """Test that site URL setting is accessible and valid."""
        from ghost_mcp.tools.content.settings import get_settings

        # Get settings
        result = await get_settings()
        response = json.loads(result)

        # Find url setting
        url_settings = [s for s in response["settings"] if s["key"] == "url"]
        assert len(url_settings) == 1, "Should have exactly one url setting"

        url_setting = url_settings[0]
        assert isinstance(url_setting["value"], str)
        assert url_setting["value"].startswith("http"), "Site URL should start with http"
        assert "localhost:2368" in url_setting["value"], "Should be localhost test instance"

    async def test_get_site_info(self, mcp_server):
        """Test getting basic site information."""
        from ghost_mcp.tools.content.settings import get_site_info

        # Get site info
        result = await get_site_info()
        response = json.loads(result)

        # Verify response structure
        assert "site" in response
        site = response["site"]

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
        site_title = site_info_response["site"]["title"]

        title_settings = [s for s in settings_response["settings"] if s["key"] == "title"]
        settings_title = title_settings[0]["value"]

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
        site_url = site_info_response["site"]["url"]

        url_settings = [s for s in settings_response["settings"] if s["key"] == "url"]
        settings_url = url_settings[0]["value"]

        # URLs should match
        assert site_url == settings_url, "Site info URL should match settings URL"

    async def test_get_site_info_version_format(self, mcp_server):
        """Test that site info includes valid Ghost version."""
        from ghost_mcp.tools.content.settings import get_site_info

        # Get site info
        result = await get_site_info()
        response = json.loads(result)

        site = response["site"]
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
        setting_keys = [setting["key"] for setting in response["settings"]]

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

        # Find timezone setting
        timezone_settings = [s for s in response["settings"] if s["key"] == "timezone"]

        if timezone_settings:  # timezone might not always be present
            timezone_setting = timezone_settings[0]
            timezone_value = timezone_setting["value"]

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

        # Find locale setting
        locale_settings = [s for s in response["settings"] if s["key"] == "locale"]

        if locale_settings:  # locale might not always be present
            locale_setting = locale_settings[0]
            locale_value = locale_setting["value"]

            # Should be a string
            assert isinstance(locale_value, str)
            assert len(locale_value) >= 2, "Locale should be at least 2 characters"

            # Common locale formats (en, en-US, etc.)
            # Should contain only letters, hyphens, and underscores
            import re
            assert re.match(r'^[a-zA-Z_-]+$', locale_value), f"Invalid locale format: {locale_value}"