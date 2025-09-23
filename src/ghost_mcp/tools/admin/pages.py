"""Admin API tools for pages management."""

import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_id_parameter


def register_admin_page_tools(mcp: FastMCP) -> None:
    """Register page management Admin API tools."""

    @mcp.tool()
    async def create_page(
        title: str,
        content: Optional[str] = None,
        content_format: str = "lexical",
        status: str = "draft",
        slug: Optional[str] = None,
    ) -> str:
        """Create a new page via Ghost Admin API."""
        if not title or not title.strip():
            return json.dumps({"error": "Title is required"})

        try:
            page_data: Dict[str, Any] = {
                "pages": [{
                    "title": title.strip(),
                    "status": status,
                }]
            }

            page = page_data["pages"][0]

            if content:
                if content_format == "html":
                    page["html"] = content
                elif content_format == "lexical":
                    page["lexical"] = content

            if slug:
                page["slug"] = slug

            async with GhostClient() as client:
                result = await client._make_request(
                    method="POST",
                    endpoint="pages/",
                    api_type="admin",
                    json_data=page_data,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})