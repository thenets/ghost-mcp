"""Admin API tools for tags management."""

import json
from typing import Any, Dict

from fastmcp import FastMCP

from ...client import GhostClient


def register_admin_tag_tools(mcp: FastMCP) -> None:
    """Register tag management Admin API tools."""

    @mcp.tool()
    async def create_tag(name: str, description: str = "") -> str:
        """Create a new tag via Ghost Admin API."""
        if not name or not name.strip():
            return json.dumps({"error": "Tag name is required"})

        try:
            tag_data: Dict[str, Any] = {
                "tags": [{
                    "name": name.strip(),
                    "description": description,
                }]
            }

            async with GhostClient() as client:
                result = await client._make_request(
                    method="POST",
                    endpoint="tags/",
                    api_type="admin",
                    json_data=tag_data,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})