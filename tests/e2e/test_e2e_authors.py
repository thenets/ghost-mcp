"""End-to-end tests for Ghost authors functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestAuthorsContentAPIE2E(BaseE2ETest):
    """Test authors Content API functionality end-to-end."""

    async def test_get_authors(self, mcp_server):
        """Test getting authors."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors
        result = await get_authors()
        response = json.loads(result)

        # Verify response structure
        assert "authors" in response
        assert "meta" in response
        assert isinstance(response["authors"], list)

        # Should have at least the default Ghost author
        assert len(response["authors"]) >= 1

        # Verify author structure
        if response["authors"]:
            author = response["authors"][0]
            essential_fields = ["id", "name", "slug"]
            for field in essential_fields:
                assert field in author

    async def test_get_authors_with_pagination(self, mcp_server):
        """Test getting authors with pagination parameters."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors with limit
        result = await get_authors(limit=5)
        response = json.loads(result)

        assert "authors" in response
        assert len(response["authors"]) <= 5

        # Test pagination metadata
        assert "meta" in response
        assert "pagination" in response["meta"]

    async def test_get_authors_with_include_count(self, mcp_server):
        """Test getting authors with post count included."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors with count.posts included
        result = await get_authors(include="count.posts")
        response = json.loads(result)

        # Verify authors include count information
        if response["authors"]:
            author = response["authors"][0]
            assert "count" in author
            assert "posts" in author["count"]
            assert isinstance(author["count"]["posts"], int)

    async def test_get_authors_with_filter(self, mcp_server):
        """Test getting authors with filter."""
        from ghost_mcp.tools.content.authors import get_authors

        # Filter authors by status
        result = await get_authors(filter="status:active")
        response = json.loads(result)

        # Verify filtering works
        assert "authors" in response
        if response["authors"]:
            for author in response["authors"]:
                # Status field might be omitted for active authors in some versions
                status = author.get("status", "active")
                assert status == "active"

    async def test_get_authors_with_order(self, mcp_server):
        """Test getting authors with custom ordering."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors ordered by name
        result = await get_authors(order="name asc")
        response = json.loads(result)

        # Verify ordering (should be alphabetical)
        if len(response["authors"]) > 1:
            author_names = [author["name"] for author in response["authors"]]
            assert author_names == sorted(author_names)

    async def test_get_author_by_id(self, mcp_server):
        """Test getting an author by ID."""
        from ghost_mcp.tools.content.authors import get_authors, get_author_by_id

        # First get all authors to find an existing ID
        all_authors_result = await get_authors()
        all_authors_response = json.loads(all_authors_result)

        if not all_authors_response["authors"]:
            pytest.skip("No authors available for testing")

        # Use the first author's ID
        test_author = all_authors_response["authors"][0]
        author_id = test_author["id"]

        # Get author by ID
        result = await get_author_by_id(author_id)
        response = json.loads(result)

        # Verify response
        assert "authors" in response
        assert len(response["authors"]) == 1

        author = response["authors"][0]
        assert author["id"] == author_id
        assert author["name"] == test_author["name"]

    async def test_get_author_by_slug(self, mcp_server):
        """Test getting an author by slug."""
        from ghost_mcp.tools.content.authors import get_authors, get_author_by_slug

        # First get all authors to find an existing slug
        all_authors_result = await get_authors()
        all_authors_response = json.loads(all_authors_result)

        if not all_authors_response["authors"]:
            pytest.skip("No authors available for testing")

        # Use the first author's slug
        test_author = all_authors_response["authors"][0]
        author_slug = test_author["slug"]

        # Get author by slug
        result = await get_author_by_slug(author_slug)
        response = json.loads(result)

        # Verify response
        assert "authors" in response
        assert len(response["authors"]) == 1

        author = response["authors"][0]
        assert author["slug"] == author_slug
        assert author["name"] == test_author["name"]

    async def test_get_author_by_nonexistent_id(self, mcp_server):
        """Test getting an author with non-existent ID returns proper error."""
        from ghost_mcp.tools.content.authors import get_author_by_id

        result = await get_author_by_id("nonexistent-id")
        response = json.loads(result)

        # Should return an error response
        assert "error" in response
        error_msg = response["error"].lower()
        assert "not found" in error_msg or "404" in error_msg or "resource not found" in error_msg or "validation error" in error_msg

    async def test_get_author_by_nonexistent_slug(self, mcp_server):
        """Test getting an author with non-existent slug returns proper error."""
        from ghost_mcp.tools.content.authors import get_author_by_slug

        result = await get_author_by_slug("nonexistent-slug")
        response = json.loads(result)

        # Should return an error response
        assert "error" in response
        error_msg = response["error"].lower()
        assert "not found" in error_msg or "404" in error_msg or "resource not found" in error_msg or "validation error" in error_msg

    async def test_author_fields_structure(self, mcp_server):
        """Test that authors have expected field structure."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors
        result = await get_authors()
        response = json.loads(result)

        if not response["authors"]:
            pytest.skip("No authors available for testing")

        author = response["authors"][0]

        # Verify essential fields are present
        essential_fields = [
            "id", "name", "slug", "url"
        ]
        for field in essential_fields:
            assert field in author, f"Field '{field}' missing from author"

        # Verify data types
        assert isinstance(author["id"], str)
        assert isinstance(author["name"], str)
        assert isinstance(author["slug"], str)
        assert isinstance(author["url"], str)

    async def test_author_with_posts_count(self, mcp_server, sample_published_post):
        """Test author post count when author has posts."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors with post count
        result = await get_authors(include="count.posts")
        response = json.loads(result)

        if not response["authors"]:
            pytest.skip("No authors available for testing")

        # Find an author with posts
        authors_with_posts = [
            author for author in response["authors"]
            if author.get("count", {}).get("posts", 0) > 0
        ]

        # There should be at least one author with posts (the author of our sample post)
        assert len(authors_with_posts) > 0

        author_with_posts = authors_with_posts[0]
        assert author_with_posts["count"]["posts"] > 0

    async def test_author_profile_fields(self, mcp_server):
        """Test that authors include profile-related fields."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors
        result = await get_authors()
        response = json.loads(result)

        if not response["authors"]:
            pytest.skip("No authors available for testing")

        author = response["authors"][0]

        # These fields may be null but should be present
        profile_fields = [
            "bio", "website", "location", "facebook", "twitter",
            "profile_image", "cover_image"
        ]

        for field in profile_fields:
            assert field in author

    async def test_default_ghost_author_exists(self, mcp_server):
        """Test that the default Ghost author exists."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get all authors
        result = await get_authors()
        response = json.loads(result)

        # Should have at least one author (the default Ghost author)
        assert len(response["authors"]) >= 1

        # Look for the default Ghost author
        ghost_authors = [
            author for author in response["authors"]
            if "ghost" in author["name"].lower() or "ghost" in author["slug"].lower()
        ]

        # There should be at least one Ghost-related author
        assert len(ghost_authors) >= 1

    async def test_author_url_format(self, mcp_server):
        """Test that author URLs follow expected format."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get authors
        result = await get_authors()
        response = json.loads(result)

        if not response["authors"]:
            pytest.skip("No authors available for testing")

        author = response["authors"][0]

        # Verify URL format
        assert "url" in author
        author_url = author["url"]
        assert author_url.startswith("http")
        assert "/author/" in author_url
        assert author["slug"] in author_url

    async def test_authors_unique_slugs(self, mcp_server):
        """Test that all authors have unique slugs."""
        from ghost_mcp.tools.content.authors import get_authors

        # Get all authors
        result = await get_authors()
        response = json.loads(result)

        if len(response["authors"]) <= 1:
            pytest.skip("Not enough authors to test uniqueness")

        # Extract all slugs
        slugs = [author["slug"] for author in response["authors"]]

        # Verify uniqueness
        assert len(slugs) == len(set(slugs)), "Author slugs are not unique"

    async def test_authors_unique_emails(self, mcp_server):
        """Test that all authors have unique email addresses."""
        # Skip this test since Content API doesn't expose author emails
        pytest.skip("Content API doesn't expose author email addresses")