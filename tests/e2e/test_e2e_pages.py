"""End-to-end tests for Ghost pages functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestPagesContentAPIE2E(BaseE2ETest):
    """Test pages Content API functionality end-to-end."""

    async def test_get_pages(self, mcp_server, sample_page):
        """Test getting pages."""
        from ghost_mcp.tools.content.pages import get_pages

        # Get pages
        result = await get_pages()
        response = json.loads(result)

        # Verify response structure
        assert "pages" in response
        assert "meta" in response
        assert isinstance(response["pages"], list)

    async def test_get_pages_with_pagination(self, mcp_server):
        """Test getting pages with pagination parameters."""
        from ghost_mcp.tools.content.pages import get_pages

        # Get pages with limit
        result = await get_pages(limit=5)
        response = json.loads(result)

        assert "pages" in response
        assert len(response["pages"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_pages_with_include_fields(self, mcp_server):
        """Test getting pages with include fields."""
        from ghost_mcp.tools.content.pages import get_pages

        # Get pages with tags and authors included
        result = await get_pages(include="tags,authors")
        response = json.loads(result)

        # Verify pages structure
        assert "pages" in response
        if response["pages"]:
            page = response["pages"][0]
            assert "tags" in page
            assert "authors" in page

    async def test_get_page_by_id(self, mcp_server, sample_page):
        """Test getting a page by ID."""
        from ghost_mcp.tools.content.pages import get_page_by_id

        # Get page by ID
        result = await get_page_by_id(sample_page["id"])
        response = json.loads(result)

        # Verify response
        assert "pages" in response
        assert len(response["pages"]) == 1

        page = response["pages"][0]
        assert page["id"] == sample_page["id"]
        assert page["title"] == sample_page["title"]

    async def test_get_page_by_slug(self, mcp_server, sample_page):
        """Test getting a page by slug."""
        from ghost_mcp.tools.content.pages import get_page_by_slug

        # Get page by slug
        result = await get_page_by_slug(sample_page["slug"])
        response = json.loads(result)

        # Verify response
        assert "pages" in response
        assert len(response["pages"]) == 1

        page = response["pages"][0]
        assert page["slug"] == sample_page["slug"]
        assert page["title"] == sample_page["title"]

    async def test_get_page_by_nonexistent_id(self, mcp_server):
        """Test getting a page with non-existent ID returns proper error."""
        from ghost_mcp.tools.content.pages import get_page_by_id

        with pytest.raises(Exception) as exc_info:
            await get_page_by_id("nonexistent-id")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    async def test_get_page_by_nonexistent_slug(self, mcp_server):
        """Test getting a page with non-existent slug returns proper error."""
        from ghost_mcp.tools.content.pages import get_page_by_slug

        with pytest.raises(Exception) as exc_info:
            await get_page_by_slug("nonexistent-slug")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


@pytest.mark.e2e
@pytest.mark.admin
class TestPagesAdminAPIE2E(BaseE2ETest):
    """Test pages Admin API functionality end-to-end."""

    async def test_create_page_draft(self, mcp_server, test_page_data, cleanup_test_content):
        """Test creating a draft page."""
        from ghost_mcp.tools.admin.pages import create_page

        # Create page
        result = await create_page(
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status=test_page_data["status"]
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
        from ghost_mcp.tools.admin.pages import create_page

        # Create published page
        result = await create_page(
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status="published"
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
        from ghost_mcp.tools.admin.pages import create_page

        custom_slug = "custom-test-page-slug"

        # Create page with custom slug
        result = await create_page(
            title=test_page_data["title"],
            content=test_page_data["content"],
            content_format=test_page_data["content_format"],
            status=test_page_data["status"],
            slug=custom_slug
        )
        response = json.loads(result)

        # Verify custom slug
        page = response["pages"][0]
        assert page["slug"] == custom_slug

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_with_special_characters(self, mcp_server, cleanup_test_content):
        """Test creating a page with special characters in title and content."""
        from ghost_mcp.tools.admin.pages import create_page

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
        })

        # Create page with special characters
        result = await create_page(
            title=special_title,
            content=special_content,
            content_format="lexical",
            status="draft"
        )
        response = json.loads(result)

        # Verify special characters are preserved
        page = response["pages"][0]
        assert page["title"] == special_title

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_create_page_minimal_data(self, mcp_server, cleanup_test_content):
        """Test creating a page with minimal required data."""
        from ghost_mcp.tools.admin.pages import create_page

        # Create page with only title
        result = await create_page(title="Minimal Test Page")
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
        from ghost_mcp.tools.admin.pages import create_page

        test_title = "Test Page Title With Spaces And Special-Characters!"

        # Create page and check slug generation
        result = await create_page(title=test_title)
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
        from ghost_mcp.tools.admin.pages import create_page

        # Create page with empty content
        result = await create_page(
            title="Empty Content Page",
            content="",
            status="draft"
        )
        response = json.loads(result)

        # Verify page was created
        page = response["pages"][0]
        assert page["title"] == "Empty Content Page"
        assert "id" in page

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_pages_vs_posts_distinction(self, mcp_server, sample_page, sample_published_post):
        """Test that pages and posts are properly distinguished."""
        from ghost_mcp.tools.content.pages import get_pages
        from ghost_mcp.tools.content.posts import get_posts

        # Get pages and posts
        pages_result = await get_pages()
        posts_result = await get_posts()

        pages_response = json.loads(pages_result)
        posts_response = json.loads(posts_result)

        # Get IDs from both
        page_ids = [page["id"] for page in pages_response["pages"]]
        post_ids = [post["id"] for post in posts_response["posts"]]

        # Verify our sample page is in pages, not posts
        assert sample_page["id"] in page_ids
        assert sample_page["id"] not in post_ids

        # Verify our sample post is in posts, not pages
        assert sample_published_post["id"] in post_ids
        assert sample_published_post["id"] not in page_ids