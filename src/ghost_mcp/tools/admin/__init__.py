"""Admin API tools for read/write access to Ghost content."""

from fastmcp import FastMCP

from .posts import register_admin_post_tools
from .pages import register_admin_page_tools
from .tags import register_admin_tag_tools
from .authors import register_admin_author_tools
from .members import register_admin_member_tools
from .settings import register_admin_settings_tools
from .media import register_admin_media_tools


def register_admin_tools(mcp: FastMCP) -> None:
    """Register all Admin API tools."""
    register_admin_post_tools(mcp)
    register_admin_page_tools(mcp)
    register_admin_tag_tools(mcp)
    register_admin_author_tools(mcp)
    register_admin_member_tools(mcp)
    register_admin_settings_tools(mcp)
    register_admin_media_tools(mcp)


__all__ = ["register_admin_tools"]