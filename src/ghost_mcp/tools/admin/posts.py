"""Admin API tools for posts management."""

import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_id_parameter
from ...utils.content_validation import (
    validate_post_title,
    validate_post_content,
    validate_content_format,
    validate_post_status,
    validate_published_at,
    get_content_format_examples,
)
from ...types.errors import ValidationError


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
        Create a new post via Ghost Admin API with comprehensive validation.

        This tool creates a new blog post with rich content support. Ghost uses Lexical
        format as the primary content format, which provides better structure and
        rendering than HTML.

        Args:
            title: Post title (required, max 255 characters)
                Example: "My Amazing Blog Post"

            content: Post content in specified format (optional)
                - For Lexical format: JSON string with structured content
                - For HTML format: Valid HTML markup
                - If not provided, creates post with empty content

            content_format: Content format (default: 'lexical', recommended)
                - 'lexical': JSON-based structured content (preferred)
                - 'html': HTML markup (for simple content or migration)

            status: Post status (default: 'draft')
                - 'draft': Saves as draft (not published)
                - 'published': Publishes immediately
                - 'scheduled': Schedules for future (requires published_at)

            slug: URL slug for the post (optional, auto-generated if not provided)
                Example: "my-amazing-blog-post"

            excerpt: Custom excerpt/summary (optional)
                Used for SEO and post previews

            featured: Whether post is featured (default: False)
                Featured posts appear prominently on the site

            tags: Comma-separated tag names (optional)
                Example: "tutorial,javascript,web-development"

            authors: Comma-separated author names (optional)
                Example: "John Doe,Jane Smith"

            published_at: Publish date for scheduled posts (optional)
                ISO datetime format: "2024-01-01T10:00:00.000Z"
                Required when status is 'scheduled'

            meta_title: SEO meta title (optional, max 300 characters)
                Used in search results and social shares

            meta_description: SEO meta description (optional, max 500 characters)
                Used in search results and social shares

        Content Format Examples:

        Lexical (Simple):
        ```json
        {
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "detail": 0,
                                "format": 0,
                                "mode": "normal",
                                "style": "",
                                "text": "Hello world!",
                                "type": "text",
                                "version": 1
                            }
                        ],
                        "direction": "ltr",
                        "format": "",
                        "indent": 0,
                        "type": "paragraph",
                        "version": 1
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        }
        ```

        Lexical (Rich Content):
        ```json
        {
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "text": "My Heading",
                                "type": "text",
                                "version": 1
                            }
                        ],
                        "type": "heading",
                        "tag": "h1",
                        "version": 1
                    },
                    {
                        "children": [
                            {
                                "text": "Paragraph with ",
                                "type": "text",
                                "version": 1
                            },
                            {
                                "text": "a link",
                                "type": "link",
                                "url": "https://example.com",
                                "version": 1
                            }
                        ],
                        "type": "paragraph",
                        "version": 1
                    }
                ],
                "type": "root",
                "version": 1
            }
        }
        ```

        HTML (Simple):
        ```html
        <p>Hello world!</p>
        ```

        HTML (Rich Content):
        ```html
        <h1>My Heading</h1>
        <p>Paragraph with <a href="https://example.com">a link</a>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        ```

        Usage Guidelines:
        - Use Lexical format for rich, structured content
        - Use HTML format for simple content or when migrating from HTML systems
        - Always validate your content before submission
        - For scheduled posts, provide published_at in ISO format
        - Use meaningful titles and excerpts for better SEO

        Returns:
            JSON string containing created post data with ID, URL, and metadata

        Raises:
            Returns error JSON if validation fails with detailed error message
        """
        try:
            # Comprehensive validation
            validated_title = validate_post_title(title)
            validated_status = validate_post_status(status)
            validated_format = validate_content_format(content_format)
            validated_published_at = validate_published_at(published_at)

            # Validate content if provided
            validated_content = None
            if content:
                validated_content = validate_post_content(content, validated_format)

            # Special validation for scheduled posts
            if validated_status == "scheduled" and not validated_published_at:
                return json.dumps({
                    "error": "Scheduled posts require a published_at date",
                    "context": "Provide published_at in ISO format: '2024-01-01T10:00:00.000Z'",
                    "examples": get_content_format_examples()
                })

            # Build post data
            post_data: Dict[str, Any] = {
                "posts": [{
                    "title": validated_title,
                    "status": validated_status,
                    "featured": featured,
                }]
            }

            post = post_data["posts"][0]

            # Add validated content in appropriate format
            if validated_content:
                if validated_format == "html":
                    post["html"] = validated_content
                elif validated_format == "lexical":
                    # For Lexical, we store the JSON string, not the parsed object
                    if isinstance(validated_content, dict):
                        post["lexical"] = json.dumps(validated_content)
                    else:
                        post["lexical"] = validated_content

            # Add optional validated fields
            if slug:
                post["slug"] = slug.strip()
            if excerpt:
                post["custom_excerpt"] = excerpt.strip()
            if validated_published_at:
                post["published_at"] = validated_published_at
            if meta_title:
                if len(meta_title) > 300:
                    return json.dumps({
                        "error": f"Meta title too long: {len(meta_title)} characters (max: 300)",
                        "context": "Shorten the meta title for better SEO"
                    })
                post["meta_title"] = meta_title.strip()
            if meta_description:
                if len(meta_description) > 500:
                    return json.dumps({
                        "error": f"Meta description too long: {len(meta_description)} characters (max: 500)",
                        "context": "Shorten the meta description for better SEO"
                    })
                post["meta_description"] = meta_description.strip()

            # Handle tags with validation
            if tags:
                tag_names = [tag.strip() for tag in tags.split(",") if tag.strip()]
                if tag_names:
                    # Validate tag names
                    for tag_name in tag_names:
                        if len(tag_name) > 191:
                            return json.dumps({
                                "error": f"Tag name too long: '{tag_name}' ({len(tag_name)} characters, max: 191)",
                                "context": "Shorten tag names or use fewer tags"
                            })
                    post["tags"] = [{"name": name} for name in tag_names]

            # Handle authors with validation
            if authors:
                author_names = [author.strip() for author in authors.split(",") if author.strip()]
                if author_names:
                    post["authors"] = [{"name": name} for name in author_names]

            # Create the post
            async with GhostClient() as client:
                result = await client.create_post(post_data)
                return json.dumps(result, indent=2, default=str)

        except ValidationError as e:
            return json.dumps({
                "error": str(e),
                "context": e.context,
                "category": e.category.value,
                "examples": get_content_format_examples()
            })
        except Exception as e:
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "context": "Please check your input parameters and try again"
            })

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
        Update an existing post via Ghost Admin API with comprehensive validation.

        This tool updates an existing blog post with the same validation and content
        format support as create_post. Only provided fields will be updated.

        Args:
            post_id: Post ID to update (required)
                Example: "64f1a2b3c4d5e6f7a8b9c0d1"

            title: New post title (optional, max 255 characters)
                Example: "Updated: My Amazing Blog Post"

            content: New post content in specified format (optional)
                - For Lexical format: JSON string with structured content
                - For HTML format: Valid HTML markup
                See create_post for format examples

            content_format: Content format (default: 'lexical')
                - 'lexical': JSON-based structured content (preferred)
                - 'html': HTML markup

            status: New post status (optional)
                - 'draft': Saves as draft
                - 'published': Publishes immediately
                - 'scheduled': Schedules for future (requires published_at)

            slug: New URL slug (optional)
                Example: "updated-amazing-blog-post"

            excerpt: New custom excerpt/summary (optional)

            featured: Whether post is featured (optional)

            published_at: New publish date for scheduled posts (optional)
                ISO datetime format: "2024-01-01T10:00:00.000Z"

            meta_title: New SEO meta title (optional, max 300 characters)

            meta_description: New SEO meta description (optional, max 500 characters)

        Usage:
            - Only provide fields you want to update
            - Content validation same as create_post
            - For format examples, see create_post documentation

        Returns:
            JSON string containing updated post data

        Raises:
            Returns error JSON if validation fails or post not found
        """
        try:
            validated_post_id = validate_id_parameter(post_id, "post_id")

            # Build update data with only provided fields after validation
            post_data: Dict[str, Any] = {"posts": [{}]}
            post = post_data["posts"][0]

            # Validate and add fields only if provided
            if title is not None:
                validated_title = validate_post_title(title)
                post["title"] = validated_title

            if status is not None:
                validated_status = validate_post_status(status)
                post["status"] = validated_status

                # Check if scheduled status requires published_at
                if validated_status == "scheduled" and published_at is None:
                    return json.dumps({
                        "error": "Scheduled posts require a published_at date",
                        "context": "Provide published_at in ISO format: '2024-01-01T10:00:00.000Z'",
                        "examples": get_content_format_examples()
                    })

            if content is not None:
                validated_format = validate_content_format(content_format)
                validated_content = validate_post_content(content, validated_format)

                if validated_format == "html":
                    post["html"] = validated_content
                elif validated_format == "lexical":
                    # For Lexical, store JSON string
                    if isinstance(validated_content, dict):
                        post["lexical"] = json.dumps(validated_content)
                    else:
                        post["lexical"] = validated_content

            if slug is not None:
                post["slug"] = slug.strip()

            if excerpt is not None:
                post["custom_excerpt"] = excerpt.strip()

            if featured is not None:
                post["featured"] = featured

            if published_at is not None:
                validated_published_at = validate_published_at(published_at)
                post["published_at"] = validated_published_at

            if meta_title is not None:
                if len(meta_title) > 300:
                    return json.dumps({
                        "error": f"Meta title too long: {len(meta_title)} characters (max: 300)",
                        "context": "Shorten the meta title for better SEO"
                    })
                post["meta_title"] = meta_title.strip()

            if meta_description is not None:
                if len(meta_description) > 500:
                    return json.dumps({
                        "error": f"Meta description too long: {len(meta_description)} characters (max: 500)",
                        "context": "Shorten the meta description for better SEO"
                    })
                post["meta_description"] = meta_description.strip()

            # Must have at least one field to update
            if not post:
                return json.dumps({
                    "error": "At least one field must be provided for update",
                    "context": "Provide title, content, status, or other fields to update"
                })

            async with GhostClient() as client:
                result = await client.update_post(validated_post_id, post_data)
                return json.dumps(result, indent=2, default=str)

        except ValidationError as e:
            return json.dumps({
                "error": str(e),
                "context": e.context,
                "category": e.category.value,
                "examples": get_content_format_examples()
            })
        except Exception as e:
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "context": "Please check your input parameters and try again"
            })

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