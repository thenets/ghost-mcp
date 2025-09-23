"""Content API tools for pages."""

import json
from typing import Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_filter_syntax, validate_id_parameter, validate_slug_parameter


def register_page_tools(mcp: FastMCP) -> None:
    """Register page-related Content API tools."""

    @mcp.tool()
    async def get_pages(
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """
        Get published pages from Ghost Content API.

        Args:
            limit: Number of pages to return (1-50, default: 15)
            page: Page number for pagination (default: 1)
            filter: Ghost filter syntax for filtering pages
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return
            order: Order of pages (published_at desc, etc.)

        Returns:
            JSON string containing pages data with metadata
        """
        # Validate parameters
        if limit is not None and (limit < 1 or limit > 50):
            return json.dumps({"error": "Limit must be between 1 and 50"})

        if page is not None and page < 1:
            return json.dumps({"error": "Page must be 1 or greater"})

        if filter and not validate_filter_syntax(filter):
            return json.dumps({"error": "Invalid filter syntax"})

        try:
            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint="pages/",
                    api_type="content",
                    params={
                        k: v for k, v in {
                            "limit": limit,
                            "page": page,
                            "filter": filter,
                            "include": include,
                            "fields": fields,
                            "order": order,
                        }.items() if v is not None
                    }
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def get_page_by_id(
        page_id: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single page by ID from Ghost Content API.

        Args:
            page_id: The page ID
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing page data
        """
        try:
            page_id = validate_id_parameter(page_id, "page_id")

            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint=f"pages/{page_id}/",
                    api_type="content",
                    params={
                        k: v for k, v in {
                            "include": include,
                            "fields": fields,
                        }.items() if v is not None
                    }
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def get_page_by_slug(
        slug: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single page by slug from Ghost Content API.

        Args:
            slug: The page slug
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing page data
        """
        try:
            slug = validate_slug_parameter(slug)

            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint=f"pages/slug/{slug}/",
                    api_type="content",
                    params={
                        k: v for k, v in {
                            "include": include,
                            "fields": fields,
                        }.items() if v is not None
                    }
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})