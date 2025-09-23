"""Content API tools for read-only access to Ghost content."""

from fastmcp import FastMCP

from .posts import register_post_tools
from .pages import register_page_tools
from .tags import register_tag_tools
from .authors import register_author_tools
from .settings import register_settings_tools

def register_content_tools(mcp: FastMCP) -> None:
    """Register all Content API tools."""
    register_post_tools(mcp)
    register_page_tools(mcp)
    register_tag_tools(mcp)
    register_author_tools(mcp)
    register_settings_tools(mcp)

__all__ = ["register_content_tools"]