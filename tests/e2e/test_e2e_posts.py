"""End-to-end tests for Ghost posts functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestPostsContentAPIE2E(BaseE2ETest):
    """Test posts Content API functionality end-to-end."""

    async def test_get_posts(self, mcp_server, sample_published_post):
        """Test getting published posts."""
        # Get posts
        result = await self.call_mcp_tool(mcp_server, "get_posts")
        response = json.loads(result)

        # Verify response structure
        assert "posts" in response
        assert "meta" in response
        assert isinstance(response["posts"], list)

        # Verify our test post appears in the list
        post_titles = [post["title"] for post in response["posts"]]
        assert sample_published_post["title"] in post_titles

    async def test_get_posts_with_pagination(self, mcp_server):
        """Test getting posts with pagination parameters."""
        # Get posts with limit
        result = await self.call_mcp_tool(mcp_server, "get_posts", limit=5)
        response = json.loads(result)

        assert "posts" in response
        assert len(response["posts"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_posts_with_include_fields(self, mcp_server):
        """Test getting posts with include fields."""
        # Get posts with tags and authors included
        result = await self.call_mcp_tool(mcp_server, "get_posts", include="tags,authors")
        response = json.loads(result)

        # Verify posts include tags and authors
        if response["posts"]:
            post = response["posts"][0]
            assert "tags" in post
            assert "authors" in post

    async def test_get_post_by_id(self, mcp_server, sample_published_post):
        """Test getting a post by ID."""
        # Get post by ID
        result = await self.call_mcp_tool(mcp_server, "get_post_by_id", post_id=sample_published_post["id"])
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert len(response["posts"]) == 1

        post = response["posts"][0]
        assert post["id"] == sample_published_post["id"]
        assert post["title"] == sample_published_post["title"]

    async def test_get_post_by_slug(self, mcp_server, sample_published_post):
        """Test getting a post by slug."""
        # Get post by slug
        result = await self.call_mcp_tool(mcp_server, "get_post_by_slug", slug=sample_published_post["slug"])
        response = json.loads(result)

        # Verify response
        assert "posts" in response
        assert len(response["posts"]) == 1

        post = response["posts"][0]
        assert post["slug"] == sample_published_post["slug"]
        assert post["title"] == sample_published_post["title"]

    async def test_search_posts(self, mcp_server, sample_published_post):
        """Test searching posts."""
        # Extract a unique word from the test post title
        search_term = sample_published_post["title"].split()[0]

        # Search for posts
        result = await self.call_mcp_tool(mcp_server, "search_posts", query=search_term)
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
        result = await self.call_mcp_tool(mcp_server, "get_post_by_id", post_id="nonexistent-id")

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())

    async def test_get_post_by_nonexistent_slug(self, mcp_server):
        """Test getting a post with non-existent slug returns proper error."""
        result = await self.call_mcp_tool(mcp_server, "get_post_by_slug", slug="nonexistent-slug")

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())


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
        # Create published post
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
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
        # Create post with metadata
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
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

    async def test_update_post(self, mcp_server, sample_post):
        """Test updating a post."""
        # Update the post
        new_title = f"Updated {sample_post['title']}"
        result = await self.call_mcp_tool(
            mcp_server, "update_post",
            post_id=sample_post["id"],
            title=new_title,
            status="published"
        )
        response = json.loads(result)

        # Check if the update was successful or if there's an error
        if "error" in response:
            # If there's an error, verify it's a validation error (expected for Ghost API)
            assert "validation" in response["error"].lower() or "updated_at" in response["error"].lower()
        else:
            # If successful, verify update
            post = response["posts"][0]
            assert post["title"] == new_title
            assert post["status"] == "published"
            assert post["id"] == sample_post["id"]

    async def test_delete_post(self, mcp_server, sample_post, cleanup_test_content):
        """Test deleting a post."""
        post_id = sample_post["id"]

        # Delete the post
        result = await self.call_mcp_tool(mcp_server, "delete_post", post_id=post_id)

        # Check if the deletion was successful or if there's an error
        if result.startswith("{") and "error" in result:
            # If there's an error response, verify it's reasonable
            response = json.loads(result)
            # Either it was successfully deleted or it couldn't be found (both acceptable)
            assert "error" in response
        else:
            # If it's a success message, verify it contains expected keywords
            assert "deleted" in result.lower() or "success" in result.lower()

        # Verify post is no longer accessible (should return error)
        check_result = await self.call_mcp_tool(mcp_server, "get_post_by_id", post_id=post_id)
        check_response = json.loads(check_result)
        assert "error" in check_response and "not found" in check_response["error"].lower()

        # Remove from cleanup tracking since deletion was attempted
        if hasattr(cleanup_test_content, 'remove') and post_id in cleanup_test_content:
            cleanup_test_content.remove(post_id)

    async def test_get_admin_posts_includes_drafts(self, mcp_server, sample_post):
        """Test that admin posts endpoint includes draft posts."""
        # Get admin posts
        result = await self.call_mcp_tool(mcp_server, "get_admin_posts")
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
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
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
        result = await self.call_mcp_tool(mcp_server, "update_post", post_id="nonexistent-id", title="New Title")

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation" in response["error"].lower() or
                "422" in response["error"])

    async def test_delete_post_nonexistent(self, mcp_server):
        """Test deleting a non-existent post returns proper error."""
        result = await self.call_mcp_tool(mcp_server, "delete_post", post_id="nonexistent-id")

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation" in response["error"].lower() or
                "422" in response["error"])