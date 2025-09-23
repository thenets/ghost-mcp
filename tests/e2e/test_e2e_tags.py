"""End-to-end tests for Ghost tags functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestTagsContentAPIE2E(BaseE2ETest):
    """Test tags Content API functionality end-to-end."""

    async def test_get_tags(self, mcp_server, sample_tag):
        """Test getting tags."""
        from ghost_mcp.tools.content.tags import get_tags

        # Get tags
        result = await get_tags()
        response = json.loads(result)

        # Verify response structure
        assert "tags" in response
        assert "meta" in response
        assert isinstance(response["tags"], list)

        # Verify our test tag appears in the list
        tag_names = [tag["name"] for tag in response["tags"]]
        assert sample_tag["name"] in tag_names

    async def test_get_tags_with_pagination(self, mcp_server):
        """Test getting tags with pagination parameters."""
        from ghost_mcp.tools.content.tags import get_tags

        # Get tags with limit
        result = await get_tags(limit=5)
        response = json.loads(result)

        assert "tags" in response
        assert len(response["tags"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_tags_with_include_count(self, mcp_server):
        """Test getting tags with post count included."""
        from ghost_mcp.tools.content.tags import get_tags

        # Get tags with count.posts included
        result = await get_tags(include="count.posts")
        response = json.loads(result)

        # Verify tags include count information
        if response["tags"]:
            tag = response["tags"][0]
            assert "count" in tag
            assert "posts" in tag["count"]
            assert isinstance(tag["count"]["posts"], int)

    async def test_get_tags_with_filter(self, mcp_server, sample_tag):
        """Test getting tags with filter."""
        from ghost_mcp.tools.content.tags import get_tags

        # Filter tags by visibility
        result = await get_tags(filter="visibility:public")
        response = json.loads(result)

        # Verify filtering works
        assert "tags" in response
        if response["tags"]:
            for tag in response["tags"]:
                assert tag.get("visibility", "public") == "public"

    async def test_get_tags_with_order(self, mcp_server):
        """Test getting tags with custom ordering."""
        from ghost_mcp.tools.content.tags import get_tags

        # Get tags ordered by name
        result = await get_tags(order="name asc")
        response = json.loads(result)

        # Verify ordering (should be alphabetical)
        if len(response["tags"]) > 1:
            tag_names = [tag["name"] for tag in response["tags"]]
            assert tag_names == sorted(tag_names)

    async def test_get_tag_by_id(self, mcp_server, sample_tag):
        """Test getting a tag by ID."""
        from ghost_mcp.tools.content.tags import get_tag_by_id

        # Get tag by ID
        result = await get_tag_by_id(sample_tag["id"])
        response = json.loads(result)

        # Verify response
        assert "tags" in response
        assert len(response["tags"]) == 1

        tag = response["tags"][0]
        assert tag["id"] == sample_tag["id"]
        assert tag["name"] == sample_tag["name"]

    async def test_get_tag_by_slug(self, mcp_server, sample_tag):
        """Test getting a tag by slug."""
        from ghost_mcp.tools.content.tags import get_tag_by_slug

        # Get tag by slug
        result = await get_tag_by_slug(sample_tag["slug"])
        response = json.loads(result)

        # Verify response
        assert "tags" in response
        assert len(response["tags"]) == 1

        tag = response["tags"][0]
        assert tag["slug"] == sample_tag["slug"]
        assert tag["name"] == sample_tag["name"]

    async def test_get_tag_by_nonexistent_id(self, mcp_server):
        """Test getting a tag with non-existent ID returns proper error."""
        from ghost_mcp.tools.content.tags import get_tag_by_id

        with pytest.raises(Exception) as exc_info:
            await get_tag_by_id("nonexistent-id")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()

    async def test_get_tag_by_nonexistent_slug(self, mcp_server):
        """Test getting a tag with non-existent slug returns proper error."""
        from ghost_mcp.tools.content.tags import get_tag_by_slug

        with pytest.raises(Exception) as exc_info:
            await get_tag_by_slug("nonexistent-slug")

        # Verify we get an appropriate error
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()


@pytest.mark.e2e
@pytest.mark.admin
class TestTagsAdminAPIE2E(BaseE2ETest):
    """Test tags Admin API functionality end-to-end."""

    async def test_create_tag_basic(self, mcp_server, test_tag_data, cleanup_test_content):
        """Test creating a basic tag."""
        from ghost_mcp.tools.admin.tags import create_tag

        # Create tag
        result = await create_tag(
            name=test_tag_data["name"],
            description=test_tag_data["description"]
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
        from ghost_mcp.tools.admin.tags import create_tag

        tag_name = "minimal-test-tag"

        # Create tag with only name
        result = await create_tag(name=tag_name)
        response = json.loads(result)

        # Verify tag was created
        tag = response["tags"][0]
        assert tag["name"] == tag_name
        assert tag["description"] == ""  # Should default to empty
        assert "slug" in tag

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_create_tag_with_special_characters(self, mcp_server, cleanup_test_content):
        """Test creating a tag with special characters."""
        from ghost_mcp.tools.admin.tags import create_tag

        special_name = "Special Tag éñ中文 🏷️"
        special_description = "Description with émojis 🎯 and unicode: 中文字符"

        # Create tag with special characters
        result = await create_tag(
            name=special_name,
            description=special_description
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
        from ghost_mcp.tools.admin.tags import create_tag

        tag_name = "Test Tag With Spaces And Special-Characters!"

        # Create tag and check slug generation
        result = await create_tag(name=tag_name)
        response = json.loads(result)

        tag = response["tags"][0]
        slug = tag["slug"]

        # Verify slug is URL-friendly
        assert " " not in slug
        assert slug.islower()
        assert "test-tag-with-spaces" in slug

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_create_duplicate_tag_name(self, mcp_server, sample_tag):
        """Test creating a tag with duplicate name returns proper error."""
        from ghost_mcp.tools.admin.tags import create_tag

        # Try to create a tag with the same name as sample_tag
        with pytest.raises(Exception) as exc_info:
            await create_tag(name=sample_tag["name"])

        # Verify we get an appropriate error
        error_msg = str(exc_info.value).lower()
        assert "duplicate" in error_msg or "already exists" in error_msg or "422" in str(exc_info.value)

    async def test_create_tag_empty_name(self, mcp_server):
        """Test creating a tag with empty name returns proper error."""
        from ghost_mcp.tools.admin.tags import create_tag

        # Try to create a tag with empty name
        with pytest.raises(Exception) as exc_info:
            await create_tag(name="")

        # Verify we get a validation error
        error_msg = str(exc_info.value).lower()
        assert "validation" in error_msg or "required" in error_msg or "400" in str(exc_info.value)

    async def test_tag_visibility_public_by_default(self, mcp_server, cleanup_test_content):
        """Test that tags are public by default."""
        from ghost_mcp.tools.admin.tags import create_tag

        # Create a tag
        result = await create_tag(name="public-visibility-test")
        response = json.loads(result)

        tag = response["tags"][0]
        # Tags should be public by default (visibility field might be omitted or set to "public")
        assert tag.get("visibility", "public") == "public"

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_tag_creation_fields(self, mcp_server, cleanup_test_content):
        """Test that created tags have all expected fields."""
        from ghost_mcp.tools.admin.tags import create_tag

        # Create a tag
        result = await create_tag(
            name="fields-test-tag",
            description="Test description for field validation"
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
        from ghost_mcp.tools.admin.tags import create_tag

        # Create a tag with a long name (but within reasonable limits)
        long_name = "This is a very long tag name that tests the system's ability to handle longer tag names without breaking"

        result = await create_tag(name=long_name)
        response = json.loads(result)

        tag = response["tags"][0]
        assert tag["name"] == long_name

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])

    async def test_tag_with_long_description(self, mcp_server, cleanup_test_content):
        """Test creating a tag with a very long description."""
        from ghost_mcp.tools.admin.tags import create_tag

        long_description = ("This is a very long description that tests the system's ability to handle "
                          "longer tag descriptions without breaking. " * 10)

        result = await create_tag(
            name="long-description-tag",
            description=long_description
        )
        response = json.loads(result)

        tag = response["tags"][0]
        assert tag["description"] == long_description

        # Track for cleanup
        cleanup_test_content["track_tag"](tag["id"])