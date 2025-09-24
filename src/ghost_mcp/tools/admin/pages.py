"""Admin API tools for pages management."""

import json
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ...client import GhostClient
from ...utils.validation import validate_id_parameter
from ...utils.content_validation import (
    validate_title,
    validate_content,
    validate_content_format,
    validate_status,
    validate_published_at,
    validate_meta_title,
    validate_meta_description,
    get_content_format_examples,
)
from ...types.errors import ValidationError


def register_admin_page_tools(mcp: FastMCP) -> None:
    """Register page management Admin API tools."""

    @mcp.tool()
    async def create_page(
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
        """Create a new page via Ghost Admin API with comprehensive validation.

        This tool creates a new page with rich content support. Ghost uses Lexical
        format as the primary content format, which provides better structure and
        rendering than HTML.

        Args:
            title: Page title (required, max 255 characters)
                Example: "My Amazing Page"

            content: Page content in specified format (optional)
                - For Lexical format: JSON string with structured content
                - For HTML format: Valid HTML markup
                - If not provided, creates page with empty content

            content_format: Content format (default: 'lexical', recommended)
                - 'lexical': JSON-based structured content (preferred)
                - 'html': HTML markup (for simple content or migration)

            status: Page status (default: 'draft')
                - 'draft': Saves as draft (not published)
                - 'published': Publishes immediately
                - 'scheduled': Schedules for future (requires published_at)

            slug: URL slug for the page (optional, auto-generated if not provided)
                Example: "my-amazing-page"

            excerpt: Custom excerpt/summary (optional)
                Used for SEO and page previews

            featured: Whether page is featured (default: False)
                Featured pages appear prominently on the site

            tags: Comma-separated tag names (optional)
                Example: "tutorial,javascript,web-development"

            authors: Comma-separated author names (optional)
                Example: "John Doe,Jane Smith"

            published_at: Publish date for scheduled pages (optional)
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
        - For scheduled pages, provide published_at in ISO format
        - Use meaningful titles and excerpts for better SEO

        Returns:
            JSON string containing created page data with ID, URL, and metadata

        Raises:
            Returns error JSON if validation fails with detailed error message
        """
        try:
            # Validate all parameters
            validated_title = validate_title(title)
            validated_format = validate_content_format(content_format)
            validated_status = validate_status(status)

            # Validate content if provided
            validated_content = None
            if content is not None:
                validated_content = validate_content(content, validated_format)

            # Validate scheduled publishing
            validated_published_at = validate_published_at(published_at)
            if validated_status == "scheduled" and not validated_published_at:
                return json.dumps({
                    "error": "Scheduled pages must have a published_at date",
                    "context": "Provide published_at in ISO format: '2024-01-01T10:00:00.000Z'"
                })

            # Build page data
            page_data: Dict[str, Any] = {
                "pages": [{
                    "title": validated_title,
                    "status": validated_status,
                }]
            }

            page = page_data["pages"][0]

            # Add content based on format
            if validated_content is not None:
                if validated_format == "html":
                    page["html"] = validated_content
                elif validated_format == "lexical":
                    page["lexical"] = json.dumps(validated_content) if isinstance(validated_content, dict) else validated_content

            # Add optional fields with validation
            if slug:
                page["slug"] = slug.strip()

            if excerpt:
                page["custom_excerpt"] = excerpt.strip()

            page["featured"] = featured

            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                for tag_name in tag_list:
                    if len(tag_name) > 191:
                        return json.dumps({
                            "error": f"Tag name too long: '{tag_name}' ({len(tag_name)} characters, max: 191)",
                            "context": "Keep tag names under 191 characters"
                        })
                page["tags"] = tag_list

            if authors:
                author_list = [author.strip() for author in authors.split(",") if author.strip()]
                page["authors"] = author_list

            if validated_published_at:
                page["published_at"] = validated_published_at

            # Validate and add meta fields
            if meta_title:
                validated_meta_title = validate_meta_title(meta_title)
                page["meta_title"] = validated_meta_title

            if meta_description:
                validated_meta_description = validate_meta_description(meta_description)
                page["meta_description"] = validated_meta_description

            # Create the page
            async with GhostClient() as client:
                result = await client._make_request(
                    method="POST",
                    endpoint="pages/",
                    api_type="admin",
                    json_data=page_data,
                )
                return json.dumps(result, indent=2, default=str)

        except ValidationError as e:
            return json.dumps({
                "error": str(e),
                "context": e.context
            })
        except Exception as e:
            return json.dumps({
                "error": f"Failed to create page: {str(e)}",
                "context": "Check your input parameters and try again"
            })

    @mcp.tool()
    async def update_page(
        page_id: str,
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
        """Update an existing page via Ghost Admin API with comprehensive validation.

        This tool updates an existing page with the same validation and content
        format support as create_page. Only provided fields will be updated.

        Args:
            page_id: Page ID to update (required)
                Example: "64f1a2b3c4d5e6f7a8b9c0d1"

            title: New page title (optional, max 255 characters)
                Example: "Updated: My Amazing Page"

            content: New page content in specified format (optional)
                - For Lexical format: JSON string with structured content
                - For HTML format: Valid HTML markup
                See create_page for format examples

            content_format: Content format (default: 'lexical')
                - 'lexical': JSON-based structured content (preferred)
                - 'html': HTML markup

            status: New page status (optional)
                - 'draft': Saves as draft
                - 'published': Publishes immediately
                - 'scheduled': Schedules for future (requires published_at)

            slug: New URL slug (optional)
                Example: "updated-amazing-page"

            excerpt: New custom excerpt/summary (optional)

            featured: Whether page is featured (optional)

            published_at: New publish date for scheduled pages (optional)
                ISO datetime format: "2024-01-01T10:00:00.000Z"

            meta_title: New SEO meta title (optional, max 300 characters)

            meta_description: New SEO meta description (optional, max 500 characters)

        Usage:
            - Only provide fields you want to update
            - Content validation same as create_page
            - For format examples, see create_page documentation

        Returns:
            JSON string containing updated page data

        Raises:
            Returns error JSON if validation fails or page not found
        """
        try:
            # Validate required ID parameter
            if not page_id or not isinstance(page_id, str):
                return json.dumps({
                    "error": "Page ID is required for updates",
                    "context": "Provide the ID of the page to update"
                })

            validated_page_id = validate_id_parameter(page_id.strip())
            validated_format = validate_content_format(content_format)

            # Get current page data and perform the update
            async with GhostClient() as client:
                # Get the current page data to obtain updated_at (required for page updates)
                current_page_result = await client._make_request(
                    method="GET",
                    endpoint=f"pages/{validated_page_id}/",
                    api_type="admin",
                )
                if not current_page_result.get("pages") or len(current_page_result["pages"]) == 0:
                    return json.dumps({
                        "error": f"Page with ID {validated_page_id} not found",
                        "context": "Verify the page ID exists"
                    })

                current_page = current_page_result["pages"][0]

                # Build update data (include required updated_at field)
                page_data: Dict[str, Any] = {
                    "pages": [{
                        "updated_at": current_page["updated_at"]  # Required for page updates
                    }]
                }
                page = page_data["pages"][0]

                # Validate and add fields only if provided
                if title is not None:
                    page["title"] = validate_title(title)

                if content is not None:
                    validated_content = validate_content(content, validated_format)
                    if validated_format == "html":
                        page["html"] = validated_content
                    elif validated_format == "lexical":
                        page["lexical"] = json.dumps(validated_content) if isinstance(validated_content, dict) else validated_content

                if status is not None:
                    validated_status = validate_status(status)
                    page["status"] = validated_status

                    # Validate scheduled publishing
                    if validated_status == "scheduled" and not published_at:
                        return json.dumps({
                            "error": "Scheduled pages must have a published_at date",
                            "context": "Provide published_at when setting status to 'scheduled'"
                        })

                if slug is not None:
                    page["slug"] = slug.strip()

                if excerpt is not None:
                    page["custom_excerpt"] = excerpt.strip()

                if featured is not None:
                    page["featured"] = featured

                if published_at is not None:
                    validated_published_at = validate_published_at(published_at)
                    page["published_at"] = validated_published_at

                if meta_title is not None:
                    validated_meta_title = validate_meta_title(meta_title)
                    page["meta_title"] = validated_meta_title

                if meta_description is not None:
                    validated_meta_description = validate_meta_description(meta_description)
                    page["meta_description"] = validated_meta_description

                # Update the page
                result = await client._make_request(
                    method="PUT",
                    endpoint=f"pages/{validated_page_id}/",
                    api_type="admin",
                    json_data=page_data,
                )
                return json.dumps(result, indent=2, default=str)

        except ValidationError as e:
            return json.dumps({
                "error": str(e),
                "context": e.context
            })
        except Exception as e:
            return json.dumps({
                "error": f"Failed to update page: {str(e)}",
                "context": "Check the page ID and input parameters"
            })

    @mcp.tool()
    async def delete_page(page_id: str) -> str:
        """Delete a page via Ghost Admin API.

        Args:
            page_id: Page ID to delete (required)

        Returns:
            JSON string containing deletion confirmation
        """
        try:
            # Validate page ID
            if not page_id or not isinstance(page_id, str):
                return json.dumps({
                    "error": "Page ID is required for deletion",
                    "context": "Provide the ID of the page to delete"
                })

            validated_page_id = validate_id_parameter(page_id.strip())

            # Delete the page
            async with GhostClient() as client:
                result = await client._make_request(
                    method="DELETE",
                    endpoint=f"pages/{validated_page_id}/",
                    api_type="admin",
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to delete page: {str(e)}",
                "context": "Check the page ID and try again"
            })

    @mcp.tool()
    async def get_admin_pages(
        limit: Optional[int] = None,
        page: Optional[int] = None,
        filter: Optional[str] = None,
        include: Optional[str] = None,
        fields: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """Get pages from Ghost Admin API (includes drafts and all statuses).

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
        try:
            # Build query parameters
            params = {}
            if limit is not None:
                params['limit'] = min(max(1, limit), 50)
            if page is not None:
                params['page'] = max(1, page)
            if filter:
                params['filter'] = filter
            if include:
                params['include'] = include
            if fields:
                params['fields'] = fields
            if order:
                params['order'] = order

            async with GhostClient() as client:
                result = await client._make_request(
                    method="GET",
                    endpoint="pages/",
                    api_type="admin",
                    params=params,
                )
                return json.dumps(result, indent=2, default=str)

        except Exception as e:
            return json.dumps({
                "error": f"Failed to fetch pages: {str(e)}",
                "context": "Check your query parameters and try again"
            })