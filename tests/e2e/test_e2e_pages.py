"""End-to-end tests for Ghost pages functionality."""

import json

import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestPagesContentAPIE2E(BaseE2ETest):
    """Test pages Content API functionality end-to-end."""

    async def test_get_pages(self, mcp_server, sample_page):  # noqa: ARG002
        """Test getting pages."""
        # Get pages
        result = await self.call_mcp_tool(mcp_server, "get_pages")
        response = json.loads(result)

        # Verify response structure
        assert "pages" in response
        assert "meta" in response
        assert isinstance(response["pages"], list)

    async def test_get_pages_with_pagination(self, mcp_server):
        """Test getting pages with pagination parameters."""
        # Get pages with limit
        result = await self.call_mcp_tool(mcp_server, "get_pages", limit=5)
        response = json.loads(result)

        assert "pages" in response
        assert len(response["pages"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_pages_with_include_fields(self, mcp_server):
        """Test getting pages with include fields."""
        # Get pages with tags and authors included
        result = await self.call_mcp_tool(
            mcp_server, "get_pages", include="tags,authors",
        )
        response = json.loads(result)

        # Verify pages structure
        assert "pages" in response
        if response["pages"]:
            page = response["pages"][0]
            assert "tags" in page
            assert "authors" in page

    async def test_get_page_by_id(self, mcp_server, sample_page):
        """Test getting a page by ID."""
        # First, let's make sure the sample page is published so it's accessible via Content API
        if sample_page.get("status") == "draft":
            # If it's a draft, the Content API won't return it, which is expected
            result = await self.call_mcp_tool(
                mcp_server, "get_page_by_id", page_id=sample_page["id"],
            )
            response = json.loads(result)
            # Should get an error for draft pages
            assert "error" in response
            assert ("not found" in response["error"].lower() or
                    "resource not found" in response["error"].lower())
        else:
            # Get published page by ID
            result = await self.call_mcp_tool(
                mcp_server, "get_page_by_id", page_id=sample_page["id"],
            )
            response = json.loads(result)

            # Verify response
            assert "pages" in response
            assert len(response["pages"]) == 1

            page = response["pages"][0]
            assert page["id"] == sample_page["id"]
            assert page["title"] == sample_page["title"]

    async def test_get_page_by_slug(self, mcp_server, sample_page):
        """Test getting a page by slug."""
        # First, let's make sure the sample page is published so it's accessible via Content API
        if sample_page.get("status") == "draft":
            # If it's a draft, the Content API won't return it, which is expected
            result = await self.call_mcp_tool(
                mcp_server, "get_page_by_slug", slug=sample_page["slug"],
            )
            response = json.loads(result)
            # Should get an error for draft pages
            assert "error" in response
            assert ("not found" in response["error"].lower() or
                    "resource not found" in response["error"].lower())
        else:
            # Get published page by slug
            result = await self.call_mcp_tool(
                mcp_server, "get_page_by_slug", slug=sample_page["slug"],
            )
            response = json.loads(result)

            # Verify response
            assert "pages" in response
            assert len(response["pages"]) == 1

            page = response["pages"][0]
            assert page["slug"] == sample_page["slug"]
            assert page["title"] == sample_page["title"]

    async def test_get_page_by_nonexistent_id(self, mcp_server):
        """Test getting a page with non-existent ID returns proper error."""
        result = await self.call_mcp_tool(
            mcp_server, "get_page_by_id", page_id="nonexistent-id",
        )

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())

    async def test_get_page_by_nonexistent_slug(self, mcp_server):
        """Test getting a page with non-existent slug returns proper error."""
        result = await self.call_mcp_tool(
            mcp_server, "get_page_by_slug", slug="nonexistent-slug",
        )

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())


@pytest.mark.e2e
@pytest.mark.admin
class TestPagesAdminAPIE2E(BaseE2ETest):
    """Test pages Admin API functionality end-to-end."""

    async def test_create_page_draft(self, mcp_server, test_page_data, cleanup_test_content):
        """Test creating a draft page."""
        # Create page
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status=test_page_data["status"],
        )
        response = json.loads(result)

        # Verify response
        assert "pages" in response
        assert len(response["pages"]) == 1

        page = response["pages"][0]
        assert page["title"] == test_page_data["title"]
        assert page["status"] == "draft"
        assert "id" in page
        assert "slug" in page

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_published(self, mcp_server, test_page_data, cleanup_test_content):
        """Test creating a published page."""
        # Create published page
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status="published",
        )
        response = json.loads(result)

        # Verify response
        assert "pages" in response
        page = response["pages"][0]
        assert page["status"] == "published"
        assert "published_at" in page
        assert page["published_at"] is not None

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_with_custom_slug(self, mcp_server, test_page_data, cleanup_test_content):
        """Test creating a page with custom slug."""
        custom_slug = "custom-test-page-slug"

        # Create page with custom slug
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status=test_page_data["status"],
            slug=custom_slug,
        )
        response = json.loads(result)

        # Verify custom slug
        page = response["pages"][0]
        assert page["slug"] == custom_slug

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_with_special_characters(self, mcp_server, cleanup_test_content):
        """Test creating a page with special characters in title and content."""
        # Title and content with special characters
        special_title = "Test Page with Special Characters: éñ中文 📄"
        special_content = json.dumps({
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "detail": 0,
                                "format": 0,
                                "mode": "normal",
                                "style": "",
                                "text": "Page content with émojis 📖 and unicode: 中文字符",
                                "type": "text",
                                "version": 1,
                            },
                        ],
                        "direction": "ltr",
                        "format": "",
                        "indent": 0,
                        "type": "paragraph",
                        "version": 1,
                    },
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1,
            },
        })

        # Create page with special characters
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title=special_title,
            content=special_content,
            content_format="lexical",
            status="draft",
        )
        response = json.loads(result)

        # Verify special characters are preserved
        page = response["pages"][0]
        assert page["title"] == special_title

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_minimal_data(self, mcp_server, cleanup_test_content):
        """Test creating a page with minimal required data."""
        # Create page with only title
        result = await self.call_mcp_tool(
            mcp_server, "create_page", title="Minimal Test Page",
        )
        response = json.loads(result)

        # Verify page was created with defaults
        page = response["pages"][0]
        assert page["title"] == "Minimal Test Page"
        assert page["status"] == "draft"  # Should default to draft
        assert "slug" in page

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_page_slug_generation(self, mcp_server, cleanup_test_content):
        """Test that page slugs are generated correctly from titles."""
        test_title = "Test Page Title With Spaces And Special-Characters!"

        # Create page and check slug generation
        result = await self.call_mcp_tool(
            mcp_server, "create_page", title=test_title,
        )
        response = json.loads(result)

        page = response["pages"][0]
        slug = page["slug"]

        # Verify slug is URL-friendly
        assert " " not in slug
        assert slug.islower()
        assert "test-page-title" in slug

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_empty_content(self, mcp_server, cleanup_test_content):
        """Test creating a page with empty content."""
        # Create page with empty content
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Empty Content Page",
            content="",
            status="draft",
        )
        response = json.loads(result)

        # Verify page was created
        page = response["pages"][0]
        assert page["title"] == "Empty Content Page"
        assert "id" in page

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_pages_vs_posts_distinction(
        self, mcp_server, sample_page, sample_published_post,  # noqa: ARG002
    ):
        """Test that pages and posts are properly distinguished."""
        # Get pages and posts via Content API (only returns published content)
        pages_result = await self.call_mcp_tool(mcp_server, "get_pages")
        posts_result = await self.call_mcp_tool(mcp_server, "get_posts")

        pages_response = json.loads(pages_result)
        posts_response = json.loads(posts_result)

        # Get IDs from both
        page_ids = [page["id"] for page in pages_response["pages"]]
        post_ids = [post["id"] for post in posts_response["posts"]]

        # The sample_page is a draft, so it won't appear in Content API results
        # But we can still verify that posts and pages are distinct by checking:
        # 1. No overlap between page and post IDs
        # 2. Our published post appears in posts, not pages
        overlap = set(page_ids) & set(post_ids)
        assert len(overlap) == 0, (
            f"Found overlapping IDs between pages and posts: {overlap}"
        )

        # Verify our sample published post is in posts, not pages
        assert sample_published_post["id"] in post_ids
        assert sample_published_post["id"] not in page_ids

        # If there are any published pages, verify they're only in pages
        if page_ids:
            for page_id in page_ids:
                assert page_id not in post_ids, (
                    f"Page ID {page_id} found in posts list"
                )
