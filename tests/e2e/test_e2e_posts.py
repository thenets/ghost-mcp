"""End-to-end tests for Ghost posts functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestPostsContentAPIE2E(BaseE2ETest):
    """Test posts Content API functionality end-to-end."""

    async def test_get_posts(self, mcp_server, sample_published_post):
        """Test getting published posts."""
        from ghost_mcp.tools.content.posts import get_posts

        # Get posts
        result = await get_posts()
        response = json.loads(result)

        # Verify response structure
        assert "posts" in response
        assert "meta" in response
        assert isinstance(response["posts"], list)

        # Verify our test post appears in the list
        post_titles = [post["title"] for post in response["posts"]]
        assert sample_published_post["title"] in post_titles

    async def test_get_posts_with_pagination(self, mcp_server, sample_published_post):
        """Test getting posts with pagination parameters."""
        from ghost_mcp.tools.content.posts import get_posts

        # Get posts with limit
        result = await get_posts(limit=5)
        response = json.loads(result)

        assert "posts" in response
        assert len(response["posts"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_posts_with_include_fields(self, mcp_server, sample_published_post):
        """Test getting posts with include fields."""
        from ghost_mcp.tools.content.posts import get_posts

        # Get posts with tags and authors included
        result = await get_posts(include="tags,authors")
        response = json.loads(result)

        # Verify posts include tags and authors
        if response["posts"]:
            post = response["posts"][0]
            assert "tags" in post
            assert "authors" in post

    async def test_get_post_by_id(self, mcp_server, sample_published_post):
        """Test getting a post by ID."""
        from ghost_mcp.tools.content.posts import get_post_by_id

        # Get post by ID
        result = await get_post_by_id(sample_published_post["id"])
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert len(response["posts"]) == 1

        post = response["posts"][0]
        assert post["id"] == sample_published_post["id"]
        assert post["title"] == sample_published_post["title"]

    async def test_get_post_by_slug(self, mcp_server, sample_published_post):
        """Test getting a post by slug."""
        from ghost_mcp.tools.content.posts import get_post_by_slug

        # Get post by slug
        result = await get_post_by_slug(sample_published_post["slug"])
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert len(response["posts"]) == 1

        post = response["posts"][0]
        assert post["slug"] == sample_published_post["slug"]
        assert post["title"] == sample_published_post["title"]

    async def test_search_posts(self, mcp_server, sample_published_post):
        """Test searching posts."""
        from ghost_mcp.tools.content.posts import search_posts

        # Extract a unique word from the test post title
        search_term = sample_published_post["title"].split()[0]

        # Search for posts
        result = await search_posts(search_term)
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert isinstance(response["posts"], list)

        # Verify our test post appears in search results
        if response["posts"]:
            post_titles = [post["title"] for post in response["posts"]]
            matching_posts = [title for title in post_titles if search_term in title]
            assert len(matching_posts) > 0

    async def test_get_post_by_nonexistent_id(self, mcp_server):
        """Test getting a post with non-existent ID returns proper error."""
        with pytest.raises(Exception) as exc_info:
            await self.call_mcp_tool(mcp_server, "get_post_by_id", post_id="nonexistent-id")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    async def test_get_post_by_nonexistent_slug(self, mcp_server):
        """Test getting a post with non-existent slug returns proper error."""
        with pytest.raises(Exception) as exc_info:
            await self.call_mcp_tool(mcp_server, "get_post_by_slug", slug="nonexistent-slug")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


@pytest.mark.e2e
@pytest.mark.admin
class TestPostsAdminAPIE2E(BaseE2ETest):
    """Test posts Admin API functionality end-to-end."""

    async def test_create_post_draft(self, mcp_server, test_post_data, cleanup_test_content):
        """Test creating a draft post."""
        # Create post
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title=test_post_data["title"],
            content=test_post_data["content"],
            content_format=test_post_data["content_format"],
            status=test_post_data["status"]
        )
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert len(response["posts"]) == 1

        post = response["posts"][0]
        assert post["title"] == test_post_data["title"]
        assert post["status"] == "draft"
        assert "id" in post

        # Track for cleanup
        cleanup_test_content["track_post"](post["id"])

    async def test_create_post_published(self, mcp_server, test_post_data, cleanup_test_content):
        """Test creating a published post."""
        from ghost_mcp.tools.admin.posts import create_post

        # Create published post
        result = await create_post(
            title=test_post_data["title"],
            content=test_post_data["content"],
            content_format=test_post_data["content_format"],
            status="published"
        )
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        post = response["posts"][0]
        assert post["status"] == "published"
        assert "published_at" in post
        assert post["published_at"] is not None

        # Track for cleanup
        cleanup_test_content["track_post"](post["id"])

    async def test_create_post_with_metadata(self, mcp_server, test_post_data, cleanup_test_content):
        """Test creating a post with metadata fields."""
        from ghost_mcp.tools.admin.posts import create_post

        # Create post with metadata
        result = await create_post(
            title=test_post_data["title"],
            content=test_post_data["content"],
            content_format=test_post_data["content_format"],
            status=test_post_data["status"],
            excerpt="Test excerpt for e2e testing",
            featured=True,
            meta_title="Test Meta Title",
            meta_description="Test meta description"
        )
        response = json.loads(result)

        # Verify metadata
        post = response["posts"][0]
        assert post["excerpt"] == "Test excerpt for e2e testing"
        assert post["featured"] is True
        assert post["meta_title"] == "Test Meta Title"
        assert post["meta_description"] == "Test meta description"

        # Track for cleanup
        cleanup_test_content["track_post"](post["id"])

    async def test_update_post(self, mcp_server, sample_post, cleanup_test_content):
        """Test updating a post."""
        from ghost_mcp.tools.admin.posts import update_post

        # Update the post
        new_title = f"Updated {sample_post['title']}"
        result = await update_post(
            post_id=sample_post["id"],
            title=new_title,
            status="published"
        )
        response = json.loads(result)

        # Verify update
        post = response["posts"][0]
        assert post["title"] == new_title
        assert post["status"] == "published"
        assert post["id"] == sample_post["id"]

    async def test_delete_post(self, mcp_server, sample_post, cleanup_test_content):
        """Test deleting a post."""
        from ghost_mcp.tools.admin.posts import delete_post

        post_id = sample_post["id"]

        # Delete the post
        result = await delete_post(post_id)

        # Verify deletion message
        assert "deleted" in result.lower() or "success" in result.lower()

        # Verify post is actually deleted by trying to get it
        from ghost_mcp.tools.content.posts import get_post_by_id
        with pytest.raises(Exception):
            await get_post_by_id(post_id)

        # Remove from cleanup tracking since it's already deleted
        if post_id in cleanup_test_content:
            cleanup_test_content.remove(post_id)

    async def test_get_admin_posts_includes_drafts(self, mcp_server, sample_post):
        """Test that admin posts endpoint includes draft posts."""
        from ghost_mcp.tools.admin.posts import get_admin_posts

        # Get admin posts
        result = await get_admin_posts()
        response = json.loads(result)

        # Verify response includes posts
        assert "posts" in response
        assert isinstance(response["posts"], list)

        # Find our draft post
        post_ids = [post["id"] for post in response["posts"]]
        assert sample_post["id"] in post_ids

        # Verify we can see draft status
        draft_posts = [post for post in response["posts"] if post["status"] == "draft"]
        assert len(draft_posts) > 0

    async def test_create_post_with_special_characters(self, mcp_server, cleanup_test_content):
        """Test creating a post with special characters in title and content."""
        from ghost_mcp.tools.admin.posts import create_post

        # Title and content with special characters
        special_title = "Test Post with Special Characters: éñ中文 🚀"
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
                                "text": "Content with émojis 🎉 and unicode: 中文字符",
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

        # Create post with special characters
        result = await create_post(
            title=special_title,
            content=special_content,
            content_format="lexical",
            status="draft"
        )
        response = json.loads(result)

        # Verify special characters are preserved
        post = response["posts"][0]
        assert post["title"] == special_title

        # Track for cleanup
        cleanup_test_content["track_post"](post["id"])

    async def test_update_post_nonexistent(self, mcp_server):
        """Test updating a non-existent post returns proper error."""
        with pytest.raises(Exception) as exc_info:
            await self.call_mcp_tool(mcp_server, "update_post", post_id="nonexistent-id", title="New Title")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    async def test_delete_post_nonexistent(self, mcp_server):
        """Test deleting a non-existent post returns proper error."""
        with pytest.raises(Exception) as exc_info:
            await self.call_mcp_tool(mcp_server, "delete_post", post_id="nonexistent-id")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()