"""Admin API tools for posts management."""

import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_id_parameter


def register_admin_post_tools(mcp: FastMCP) -> None:
    """Register post management Admin API tools."""

    @mcp.tool()
    async def create_post(
        title: str,
        content: Optional[str] = None,
        content_format: str = "lexical",
        status: str = "draft",
        slug: Optional[str] = None,
        excerpt: Optional[str] = None,
        featured: bool = False,
        tags: Optional[str] = None,
        authors: Optional[str] = None,
        published_at: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
    ) -> str:
        """
        Create a new post via Ghost Admin API.

        Args:
            title: Post title (required)
            content: Post content (HTML or Lexical JSON)
            content_format: Content format ('html', 'lexical', default: 'lexical')
            status: Post status ('draft', 'published', 'scheduled', default: 'draft')
            slug: Post slug (auto-generated if not provided)
            excerpt: Custom excerpt
            featured: Whether post is featured (default: False)
            tags: Comma-separated tag names or IDs
            authors: Comma-separated author names or IDs
            published_at: Publish date (ISO format, for scheduled posts)
            meta_title: SEO meta title
            meta_description: SEO meta description

        Returns:
            JSON string containing created post data
        """
        if not title or not title.strip():
            return json.dumps({"error": "Title is required"})

        try:
            # Build post data
            post_data: Dict[str, Any] = {
                "posts": [{
                    "title": title.strip(),
                    "status": status,
                    "featured": featured,
                }]
            }

            post = post_data["posts"][0]

            # Add content in appropriate format
            if content:
                if content_format == "html":
                    post["html"] = content
                elif content_format == "lexical":
                    # Assume content is already Lexical JSON string
                    post["lexical"] = content
                else:
                    return json.dumps({"error": "Content format must be 'html' or 'lexical'"})

            # Add optional fields
            if slug:
                post["slug"] = slug
            if excerpt:
                post["custom_excerpt"] = excerpt
            if published_at:
                post["published_at"] = published_at
            if meta_title:
                post["meta_title"] = meta_title
            if meta_description:
                post["meta_description"] = meta_description

            # Handle tags (simplified - in real implementation would resolve tag names to IDs)
            if tags:
                tag_list = [{"name": tag.strip()} for tag in tags.split(",") if tag.strip()]
                if tag_list:
                    post["tags"] = tag_list

            # Handle authors (simplified)
            if authors:
                author_list = [{"name": author.strip()} for author in authors.split(",") if author.strip()]
                if author_list:
                    post["authors"] = author_list

            async with GhostClient() as client:
                result = await client.create_post(post_data)
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def update_post(
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        content_format: str = "lexical",
        status: Optional[str] = None,
        slug: Optional[str] = None,
        excerpt: Optional[str] = None,
        featured: Optional[bool] = None,
        published_at: Optional[str] = None,
        meta_title: Optional[str] = None,
        meta_description: Optional[str] = None,
    ) -> str:
        """
        Update an existing post via Ghost Admin API.

        Args:
            post_id: Post ID to update (required)
            title: New post title
            content: New post content (HTML or Lexical JSON)
            content_format: Content format ('html', 'lexical', default: 'lexical')
            status: New post status ('draft', 'published', 'scheduled')
            slug: New post slug
            excerpt: New custom excerpt
            featured: Whether post is featured
            published_at: New publish date (ISO format)
            meta_title: New SEO meta title
            meta_description: New SEO meta description

        Returns:
            JSON string containing updated post data
        """
        try:
            post_id = validate_id_parameter(post_id, "post_id")

            # Build update data with only provided fields
            post_data: Dict[str, Any] = {"posts": [{}]}
            post = post_data["posts"][0]

            if title is not None:
                post["title"] = title.strip()
            if status is not None:
                post["status"] = status
            if slug is not None:
                post["slug"] = slug
            if excerpt is not None:
                post["custom_excerpt"] = excerpt
            if featured is not None:
                post["featured"] = featured
            if published_at is not None:
                post["published_at"] = published_at
            if meta_title is not None:
                post["meta_title"] = meta_title
            if meta_description is not None:
                post["meta_description"] = meta_description

            # Add content in appropriate format
            if content is not None:
                if content_format == "html":
                    post["html"] = content
                elif content_format == "lexical":
                    post["lexical"] = content
                else:
                    return json.dumps({"error": "Content format must be 'html' or 'lexical'"})

            # Must have at least one field to update
            if not post:
                return json.dumps({"error": "At least one field must be provided for update"})

            async with GhostClient() as client:
                result = await client.update_post(post_id, post_data)
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def delete_post(post_id: str) -> str:
        """
        Delete a post via Ghost Admin API.

        Args:
            post_id: Post ID to delete (required)

        Returns:
            JSON string containing deletion confirmation
        """
        try:
            post_id = validate_id_parameter(post_id, "post_id")

            async with GhostClient() as client:
                result = await client.delete_post(post_id)
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    async def get_admin_posts(
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """
        Get posts from Ghost Admin API (includes drafts and all statuses).

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
        try:
            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint="posts/",
                    api_type="admin",
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