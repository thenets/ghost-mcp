"""Content API tools for tags."""

import json
from typing import Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_filter_syntax, validate_id_parameter, validate_slug_parameter


def register_tag_tools(mcp: FastMCP) -> None:
    """Register tag-related Content API tools."""

    @mcp.tool()
    async def get_tags(
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """
        Get tags from Ghost Content API.

        Args:
            limit: Number of tags to return (1-50, default: 15)
            page: Page number for pagination (default: 1)
            filter: Ghost filter syntax for filtering tags
            include: Comma-separated list of fields to include (count.posts, etc.)
            fields: Comma-separated list of fields to return
            order: Order of tags (name asc, count.posts desc, etc.)

        Returns:
            JSON string containing tags data with metadata
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
                    endpoint="tags/",
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
    async def get_tag_by_id(
        tag_id: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single tag by ID from Ghost Content API.

        Args:
            tag_id: The tag ID
            include: Comma-separated list of fields to include (count.posts, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing tag data
        """
        try:
            tag_id = validate_id_parameter(tag_id, "tag_id")

            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint=f"tags/{tag_id}/",
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
    async def get_tag_by_slug(
        slug: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single tag by slug from Ghost Content API.

        Args:
            slug: The tag slug
            include: Comma-separated list of fields to include (count.posts, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing tag data
        """
        try:
            slug = validate_slug_parameter(slug)

            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint=f"tags/slug/{slug}/",
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