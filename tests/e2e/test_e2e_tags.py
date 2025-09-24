"""End-to-end tests for Ghost tags functionality."""

import json

import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestTagsContentAPIE2E(BaseE2ETest):
    """Test tags Content API functionality end-to-end."""

    async def test_get_tags(self, mcp_server, sample_tag):  # noqa: ARG002
        """Test getting tags."""
        # Get tags
        result = await self.call_mcp_tool(mcp_server, "get_tags")
        response = json.loads(result)

        # Verify response structure
        assert "tags" in response
        assert "meta" in response
        assert isinstance(response["tags"], list)

        # Note: Content API only returns tags with posts or that are otherwise visible
        # Our test tag won't appear unless it has posts, which is expected behavior

    async def test_get_tags_with_pagination(self, mcp_server):
        """Test getting tags with pagination parameters."""
        # Get tags with limit
        result = await self.call_mcp_tool(mcp_server, "get_tags", limit=5)
        response = json.loads(result)

        assert "tags" in response
        assert len(response["tags"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_tags_with_include_count(self, mcp_server):
        """Test getting tags with post count included."""
        # Get tags with count.posts included
        result = await self.call_mcp_tool(
            mcp_server, "get_tags", include="count.posts",
        )
        response = json.loads(result)

        # Verify tags include count information
        if response["tags"]:
            tag = response["tags"][0]
            assert "count" in tag
            assert "posts" in tag["count"]
            assert isinstance(tag["count"]["posts"], int)

    async def test_get_tags_with_filter(self, mcp_server, sample_tag):  # noqa: ARG002
        """Test getting tags with filter."""
        # Filter tags by visibility
        result = await self.call_mcp_tool(
            mcp_server, "get_tags", filter="visibility:public",
        )
        response = json.loads(result)

        # Verify filtering works
        assert "tags" in response
        if response["tags"]:
            for tag in response["tags"]:
                assert tag.get("visibility", "public") == "public"

    async def test_get_tags_with_order(self, mcp_server):
        """Test getting tags with custom ordering."""
        # Get tags ordered by name
        result = await self.call_mcp_tool(mcp_server, "get_tags", order="name asc")
        response = json.loads(result)

        # Verify ordering (should be alphabetical)
        if len(response["tags"]) > 1:
            tag_names = [tag["name"] for tag in response["tags"]]
            assert tag_names == sorted(tag_names)

    async def test_get_tag_by_id(self, mcp_server, sample_tag):
        """Test getting a tag by ID."""
        # Get tag by ID - Content API may not return tags without posts
        result = await self.call_mcp_tool(
            mcp_server, "get_tag_by_id", tag_id=sample_tag["id"],
        )
        response = json.loads(result)

        # Content API may return an error for tags without posts, which is expected
        if "error" in response:
            assert "not found" in response["error"].lower()
        else:
            # If tag is returned, verify it's correct
            assert "tags" in response
            assert len(response["tags"]) == 1
            tag = response["tags"][0]
            assert tag["id"] == sample_tag["id"]
            assert tag["name"] == sample_tag["name"]

    async def test_get_tag_by_slug(self, mcp_server, sample_tag):
        """Test getting a tag by slug."""
        # Get tag by slug - Content API may not return tags without posts
        result = await self.call_mcp_tool(
            mcp_server, "get_tag_by_slug", slug=sample_tag["slug"],
        )
        response = json.loads(result)

        # Content API may return an error for tags without posts, which is expected
        if "error" in response:
            assert "not found" in response["error"].lower()
        else:
            # If tag is returned, verify it's correct
            assert "tags" in response
            assert len(response["tags"]) == 1
            tag = response["tags"][0]
            assert tag["slug"] == sample_tag["slug"]
            assert tag["name"] == sample_tag["name"]

    async def test_get_tag_by_nonexistent_id(self, mcp_server):
        """Test getting a tag with non-existent ID returns proper error."""
        result = await self.call_mcp_tool(
            mcp_server, "get_tag_by_id", tag_id="nonexistent-id",
        )

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())

    async def test_get_tag_by_nonexistent_slug(self, mcp_server):
        """Test getting a tag with non-existent slug returns proper error."""
        result = await self.call_mcp_tool(
            mcp_server, "get_tag_by_slug", slug="nonexistent-slug",
        )

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        assert ("not found" in response["error"].lower() or
                "validation error" in response["error"].lower())


@pytest.mark.e2e
@pytest.mark.admin
class TestTagsAdminAPIE2E(BaseE2ETest):
    """Test tags Admin API functionality end-to-end."""

    async def test_create_tag_basic(self, mcp_server, test_tag_data, cleanup_test_content):
        """Test creating a basic tag."""
        # Create tag
        result = await self.call_mcp_tool(
            mcp_server, "create_tag",
            name=test_tag_data["name"],
            description=test_tag_data["description"],
        )
        response = json.loads(result)

        # Verify response
        assert "tags" in response
        assert len(response["tags"]) == 1

        tag = response["tags"][0]
        assert tag["name"] == test_tag_data["name"]
        assert tag["description"] == test_tag_data["description"]
        assert "id" in tag
        assert "slug" in tag

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_create_tag_minimal(self, mcp_server, cleanup_test_content):
        """Test creating a tag with minimal data (name only)."""
        tag_name = "minimal-test-tag"

        # Create tag with only name
        result = await self.call_mcp_tool(mcp_server, "create_tag", name=tag_name)
        response = json.loads(result)

        # Verify tag was created
        tag = response["tags"][0]
        assert tag["name"] == tag_name
        assert tag["description"] == "" or tag["description"] is None  # Ghost may return None for empty
        assert "slug" in tag

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_create_tag_with_special_characters(self, mcp_server, cleanup_test_content):
        """Test creating a tag with special characters."""
        special_name = "Special Tag éñ中文 🏷️"
        special_description = "Description with émojis 🎯 and unicode: 中文字符"

        # Create tag with special characters
        result = await self.call_mcp_tool(
            mcp_server, "create_tag",
            name=special_name,
            description=special_description,
        )
        response = json.loads(result)

        # Verify special characters are preserved
        tag = response["tags"][0]
        assert tag["name"] == special_name
        assert tag["description"] == special_description

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_tag_slug_generation(self, mcp_server, cleanup_test_content):
        """Test that tag slugs are generated correctly from names."""
        tag_name = "Test Tag With Spaces And Special-Characters!"

        # Create tag and check slug generation
        result = await self.call_mcp_tool(
            mcp_server, "create_tag", name=tag_name,
        )
        response = json.loads(result)

        tag = response["tags"][0]
        slug = tag["slug"]

        # Verify slug is URL-friendly
        assert " " not in slug
        assert slug.islower()
        assert "test-tag-with-spaces" in slug

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_create_duplicate_tag_name(self, mcp_server, sample_tag, cleanup_test_content):
        """Test creating a tag with duplicate name - Ghost allows this by modifying the slug."""
        # Try to create a tag with the same name as sample_tag
        result = await self.call_mcp_tool(
            mcp_server, "create_tag", name=sample_tag["name"],
        )

        # Ghost allows duplicate tag names by creating a unique slug
        response = json.loads(result)
        if "error" in response:
            # Some Ghost configurations might prevent duplicates
            error_msg = response["error"].lower()
            assert ("duplicate" in error_msg or "already exists" in error_msg or
                    "422" in response["error"])
        else:
            # Ghost created a tag with unique slug
            assert "tags" in response
            new_tag = response["tags"][0]
            assert new_tag["name"] == sample_tag["name"]
            assert new_tag["slug"] != sample_tag["slug"]  # Slug should be different
            # Track for cleanup
            cleanup_test_content["track_tag"](new_tag["id"])

    async def test_create_tag_empty_name(self, mcp_server):
        """Test creating a tag with empty name returns proper error."""
        # Try to create a tag with empty name
        result = await self.call_mcp_tool(mcp_server, "create_tag", name="")

        # MCP tools return JSON error responses instead of raising exceptions
        response = json.loads(result)
        assert "error" in response
        error_msg = response["error"].lower()
        assert ("validation" in error_msg or "required" in error_msg or
                "400" in response["error"])

    async def test_tag_visibility_public_by_default(self, mcp_server, cleanup_test_content):
        """Test that tags are public by default."""
        # Create a tag
        result = await self.call_mcp_tool(
            mcp_server, "create_tag", name="public-visibility-test",
        )
        response = json.loads(result)

        tag = response["tags"][0]
        # Tags should be public by default (visibility field might be omitted or set to "public")
        assert tag.get("visibility", "public") == "public"

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_tag_creation_fields(self, mcp_server, cleanup_test_content):
        """Test that created tags have all expected fields."""
        # Create a tag
        result = await self.call_mcp_tool(
            mcp_server, "create_tag",
            name="fields-test-tag",
            description="Test description for field validation",
        )
        response = json.loads(result)

        tag = response["tags"][0]

        # Verify essential fields are present
        essential_fields = ["id", "name", "slug", "description", "created_at", "updated_at"]
        for field in essential_fields:
            assert field in tag

        # Verify data types
        assert isinstance(tag["id"], str)
        assert isinstance(tag["name"], str)
        assert isinstance(tag["slug"], str)
        assert isinstance(tag["description"], str)

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_long_tag_name(self, mcp_server, cleanup_test_content):
        """Test creating a tag with a very long name."""
        # Create a tag with a long name (but within reasonable limits)
        long_name = ("This is a very long tag name that tests the system's ability to "
                     "handle longer tag names without breaking")

        result = await self.call_mcp_tool(mcp_server, "create_tag", name=long_name)
        response = json.loads(result)

        tag = response["tags"][0]
        assert tag["name"] == long_name

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_tag_with_long_description(self, mcp_server, cleanup_test_content):
        """Test creating a tag with a very long description."""
        long_description = ("This is a very long description that tests the system's ability to handle "
                          "longer tag descriptions without breaking. " * 10)

        result = await self.call_mcp_tool(
            mcp_server, "create_tag",
            name="long-description-tag",
            description=long_description,
        )
        response = json.loads(result)

        # Ghost may reject very long descriptions
        if "error" in response:
            # Expected if description is too long
            assert "422" in response["error"] or "validation" in response["error"].lower()
        else:
            # If accepted, verify it was stored correctly
            tag = response["tags"][0]
            assert tag["description"] == long_description
            # Track for cleanup
            cleanup_test_content["track_tag"](tag["id"])
