"""MCP tools for Ghost API access."""

from .content import *
from .admin import *

__all__ = [
    # Content API tools
    "register_content_tools",
    # Admin API tools
    "register_admin_tools",
]