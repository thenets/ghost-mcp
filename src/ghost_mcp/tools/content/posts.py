"""Content API tools for posts."""

import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_filter_syntax, validate_id_parameter, validate_slug_parameter


async def search_posts(
    query: str,
    limit: Optional[int] = None,
    include: Optional[str] = None,
) -> str:
    """
    Search posts by title and content.

    Args:
        query: Search query string
        limit: Number of results to return (1-50, default: 15)
        include: Comma-separated list of fields to include

    Returns:
        JSON string containing matching posts
    """
    if not query or not query.strip():
        return json.dumps({"error": "Query parameter is required"})

    if limit is not None and (limit < 1 or limit > 50):
        return json.dumps({"error": "Limit must be between 1 and 50"})

    try:
        # Use Ghost's filter syntax for searching
        search_filter = f"title:~'{query}',plaintext:~'{query}'"

        async with GhostClient() as client:
            result = await client.get_posts(
                limit=limit,
                filter=search_filter,
                include=include,
            )
            return json.dumps(result, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)})


def register_post_tools(mcp: FastMCP) -> None:
    """Register post-related Content API tools."""

    @mcp.tool()
    async def get_posts(
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """
        Get published posts from Ghost Content API.

        Args:
            limit: Number of posts to return (1-50, default: 15)
            page: Page number for pagination (default: 1)
            filter: Ghost filter syntax for filtering posts
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return
            order: Order of posts (published_at desc, etc.)

        Returns:
            JSON string containing posts data with metadata
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
                result = await client.get_posts(
                    limit=limit,
                    page=page,
                    filter=filter,
                    include=include,
                    fields=fields,
                    order=order,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def get_post_by_id(
        post_id: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single post by ID from Ghost Content API.

        Args:
            post_id: The post ID
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing post data
        """
        try:
            post_id = validate_id_parameter(post_id, "post_id")

            async with GhostClient() as client:
                result = await client.get_post_by_id(
                    post_id=post_id,
                    include=include,
                    fields=fields,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def get_post_by_slug(
        slug: str,
        include: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> str:
        """
        Get a single post by slug from Ghost Content API.

        Args:
            slug: The post slug
            include: Comma-separated list of fields to include (tags, authors, etc.)
            fields: Comma-separated list of fields to return

        Returns:
            JSON string containing post data
        """
        try:
            slug = validate_slug_parameter(slug)

            async with GhostClient() as client:
                result = await client.get_post_by_slug(
                    slug=slug,
                    include=include,
                    fields=fields,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    # Register the standalone search_posts function as an MCP tool
    mcp.tool()(search_posts)