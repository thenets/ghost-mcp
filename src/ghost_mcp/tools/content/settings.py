"""Content API tools for settings."""

import json
from typing import Optional

from fastmcp import FastMCP

from ...client import GhostClient


async def get_settings() -> str:
    """
    Get public settings from Ghost Content API.

    Returns:
        JSON string containing public settings data
    """
    try:
        async with GhostClient() as client:
            result = await client._make_request(
                method="GET",
                endpoint="settings/",
                api_type="content",
            )
            return json.dumps(result, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


async def get_site_info() -> str:
    """
    Get basic site information from Ghost.

    Returns:
        JSON string containing site title, description, URL, and other public info
    """
    try:
        async with GhostClient() as client:
            result = await client._make_request(
                method="GET",
                endpoint="settings/",
                api_type="content",
            )

            # Extract key site information
            if "settings" in result:
                settings = result["settings"]
                site_info = {
                    "title": settings.get("title"),
                    "description": settings.get("description"),
                    "url": settings.get("url"),
                    "logo": settings.get("logo"),
                    "icon": settings.get("icon"),
                    "cover_image": settings.get("cover_image"),
                    "accent_color": settings.get("accent_color"),
                    "timezone": settings.get("timezone"),
                    "lang": settings.get("lang"),
                    "version": settings.get("version"),
                }
                return json.dumps({"site_info": site_info}, indent=2, default=str)

            return json.dumps(result, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def register_settings_tools(mcp: FastMCP) -> None:
    """Register settings-related Content API tools."""

    # Register the standalone functions as MCP tools
    mcp.tool()(get_settings)
    mcp.tool()(get_site_info)