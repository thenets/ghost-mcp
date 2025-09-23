"""Ghost MCP server entry point."""

import asyncio
from typing import Any

from fastmcp import FastMCP

from .config import config
from .tools import register_admin_tools, register_content_tools
from .utils.logging import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Create FastMCP server
mcp = FastMCP("Ghost MCP Server")


@mcp.tool()
async def check_ghost_connection() -> str:
    """
    Check connection to Ghost instance and API key configuration.

    Returns:
        JSON string with connection status and configuration info
    """
    import json
    from .client import GhostClient

    status = {
        "ghost_url": str(config.ghost.url),
        "content_api_configured": bool(config.ghost.content_api_key),
        "admin_api_configured": bool(config.ghost.admin_api_key),
        "mode": config.ghost.mode.value,
        "connection_test": "pending",
    }

    try:
        async with GhostClient() as client:
            # Test Content API if configured
            if client.content_auth.is_configured():
                try:
                    await client._make_request("GET", "settings/", api_type="content")
                    status["content_api_status"] = "connected"
                except Exception as e:
                    status["content_api_status"] = f"error: {e}"

            # Test Admin API if configured
            if client.admin_auth.is_configured():
                try:
                    await client._make_request("GET", "site/", api_type="admin")
                    status["admin_api_status"] = "connected"
                except Exception as e:
                    status["admin_api_status"] = f"error: {e}"

            status["connection_test"] = "completed"

    except Exception as e:
        status["connection_test"] = f"failed: {e}"

    return json.dumps(status, indent=2)


def register_tools() -> None:
    """Register all MCP tools based on configuration."""
    logger.info("Registering MCP tools", mode=config.ghost.mode.value)

    # Always register Content API tools (read-only)
    if config.ghost.content_api_key:
        logger.info("Registering Content API tools")
        register_content_tools(mcp)
    else:
        logger.warning("Content API key not configured - Content tools not available")

    # Register Admin API tools based on mode and configuration
    if config.ghost.mode.value in ["readwrite", "auto"]:
        if config.ghost.admin_api_key:
            logger.info("Registering Admin API tools")
            register_admin_tools(mcp)
        elif config.ghost.mode.value == "readwrite":
            logger.warning("Admin API key not configured - Admin tools not available in readwrite mode")
        else:
            logger.info("Admin API key not configured - running in read-only mode")
    else:
        logger.info("Running in read-only mode - Admin tools not registered")


def main() -> None:
    """Main entry point for the Ghost MCP server."""
    logger.info(
        "Starting Ghost MCP server",
        ghost_url=str(config.ghost.url),
        mode=config.ghost.mode.value,
        content_api_configured=bool(config.ghost.content_api_key),
        admin_api_configured=bool(config.ghost.admin_api_key),
    )

    # Register tools
    register_tools()

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()