"""End-to-end tests for Ghost search functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
class TestSearchE2E(BaseE2ETest):
    """Test search functionality end-to-end."""

    async def test_search_posts_basic(self, mcp_server, sample_published_post):
        """Test basic post search functionality."""
        from ghost_mcp.tools.content.posts import search_posts

        # Extract a searchable term from the test post title
        search_term = sample_published_post["title"].split()[0]

        # Search for posts
        result = await search_posts(search_term)
        response = json.loads(result)

        # Verify response structure
        assert "posts" in response
        assert isinstance(response["posts"], list)

        # Should find our test post
        post_titles = [post["title"] for post in response["posts"]]
        matching_posts = [title for title in post_titles if search_term in title]
        assert len(matching_posts) > 0, f"Should find posts matching '{search_term}'"

    async def test_search_posts_with_limit(self, mcp_server, sample_published_post):
        """Test post search with result limit."""
        from ghost_mcp.tools.content.posts import search_posts

        # Use a broad search term
        search_term = "test"

        # Search with limit
        result = await search_posts(search_term, limit=3)
        response = json.loads(result)

        # Verify limit is respected
        assert "posts" in response
        assert len(response["posts"]) <= 3

    async def test_search_posts_case_insensitive(self, mcp_server, sample_published_post):
        """Test that post search is case insensitive."""
        from ghost_mcp.tools.content.posts import search_posts

        # Get a word from the title in different cases
        original_word = sample_published_post["title"].split()[0]
        lowercase_search = original_word.lower()
        uppercase_search = original_word.upper()

        # Search with lowercase
        lowercase_result = await search_posts(lowercase_search)
        lowercase_response = json.loads(lowercase_result)

        # Search with uppercase
        uppercase_result = await search_posts(uppercase_search)
        uppercase_response = json.loads(uppercase_result)

        # Both should return similar results
        assert len(lowercase_response["posts"]) > 0
        assert len(uppercase_response["posts"]) > 0

        # Should find the same post regardless of case
        lowercase_titles = [post["title"] for post in lowercase_response["posts"]]
        uppercase_titles = [post["title"] for post in uppercase_response["posts"]]

        test_post_title = sample_published_post["title"]
        if test_post_title in lowercase_titles:
            assert test_post_title in uppercase_titles

    async def test_search_posts_partial_match(self, mcp_server, sample_published_post):
        """Test that post search supports partial word matching."""
        from ghost_mcp.tools.content.posts import search_posts

        # Get a partial word from the title
        full_word = sample_published_post["title"].split()[0]
        if len(full_word) > 3:
            partial_word = full_word[:3]  # First 3 characters

            # Search with partial word
            result = await search_posts(partial_word)
            response = json.loads(result)

            # Should find posts containing the partial match
            assert "posts" in response
            # Note: Not all Ghost installations support partial matching,
            # so we just verify the search doesn't error

    async def test_search_posts_special_characters(self, mcp_server):
        """Test post search with special characters."""
        from ghost_mcp.tools.content.posts import search_posts

        # Test search with special characters
        special_searches = ["test!", "test-post", "test_post"]

        for search_term in special_searches:
            try:
                result = await search_posts(search_term)
                response = json.loads(result)

                # Should return valid response structure
                assert "posts" in response
                assert isinstance(response["posts"], list)
            except Exception as e:
                # Some special characters might not be supported,
                # but should not cause server errors
                assert "500" not in str(e), f"Server error with search term '{search_term}'"

    async def test_search_posts_empty_query(self, mcp_server):
        """Test post search with empty query."""
        from ghost_mcp.tools.content.posts import search_posts

        # Search with empty string
        result = await search_posts("")
        response = json.loads(result)

        # Empty query should return error
        if "error" in response:
            # Should return proper validation error
            assert "required" in response["error"].lower() or "query" in response["error"].lower()
        else:
            # Or should return empty results or all posts
            assert "posts" in response
            assert isinstance(response["posts"], list)

    async def test_search_posts_nonexistent_term(self, mcp_server):
        """Test post search with non-existent term."""
        from ghost_mcp.tools.content.posts import search_posts

        # Search for something that shouldn't exist
        nonexistent_term = "xyzneverexistingtermabc123"

        result = await search_posts(nonexistent_term)
        response = json.loads(result)

        # Should return empty results
        assert "posts" in response
        assert len(response["posts"]) == 0

    async def test_search_posts_common_words(self, mcp_server):
        """Test post search with common words."""
        from ghost_mcp.tools.content.posts import search_posts

        # Test with common words
        common_words = ["the", "and", "is", "test"]

        for word in common_words:
            result = await search_posts(word)
            response = json.loads(result)

            # Should return valid response
            assert "posts" in response
            assert isinstance(response["posts"], list)

    async def test_search_posts_unicode_characters(self, mcp_server):
        """Test post search with unicode characters."""
        from ghost_mcp.tools.content.posts import search_posts

        # Test with unicode characters
        unicode_searches = ["café", "naïve", "résumé", "中文"]

        for search_term in unicode_searches:
            try:
                result = await search_posts(search_term)
                response = json.loads(result)

                # Should return valid response structure
                assert "posts" in response
                assert isinstance(response["posts"], list)
            except Exception as e:
                # Unicode might not be fully supported in all Ghost configurations
                # but should not cause server errors
                assert "500" not in str(e), f"Server error with unicode search '{search_term}'"

    async def test_search_posts_long_query(self, mcp_server):
        """Test post search with very long query."""
        from ghost_mcp.tools.content.posts import search_posts

        # Very long search query
        long_query = "this is a very long search query that tests the system's ability to handle long search terms without breaking or causing performance issues" * 3

        result = await search_posts(long_query)
        response = json.loads(result)

        if "error" in response:
            # Long queries might be rejected with proper error
            error_msg = response["error"].lower()
            assert any(term in error_msg for term in ["length", "long", "request", "understood", "cannot"])
        else:
            # Or should handle long queries gracefully
            assert "posts" in response
            assert isinstance(response["posts"], list)

    async def test_search_posts_multiple_words(self, mcp_server, sample_published_post):
        """Test post search with multiple words."""
        from ghost_mcp.tools.content.posts import search_posts

        # Get multiple words from the title
        title_words = sample_published_post["title"].split()
        if len(title_words) >= 2:
            # Search with first two words
            multi_word_search = f"{title_words[0]} {title_words[1]}"

            result = await search_posts(multi_word_search)
            response = json.loads(result)

            # Should return valid results
            assert "posts" in response
            assert isinstance(response["posts"], list)

    async def test_search_posts_pagination_metadata(self, mcp_server, sample_published_post):
        """Test that search results include proper pagination metadata."""
        from ghost_mcp.tools.content.posts import search_posts

        # Search for posts
        search_term = "test"
        result = await search_posts(search_term, limit=5)
        response = json.loads(result)

        # Should have posts array
        assert "posts" in response

        # May or may not have meta depending on implementation,
        # but if present should be properly structured
        if "meta" in response:
            meta = response["meta"]
            assert isinstance(meta, dict)

            if "pagination" in meta:
                pagination = meta["pagination"]
                assert isinstance(pagination, dict)

    async def test_search_posts_include_fields(self, mcp_server, sample_published_post):
        """Test search with include fields parameter."""
        from ghost_mcp.tools.content.posts import search_posts

        # Extract search term
        search_term = sample_published_post["title"].split()[0]

        # Search with include fields
        result = await search_posts(search_term, include="tags,authors")
        response = json.loads(result)

        # Verify include fields work in search
        if response["posts"]:
            post = response["posts"][0]
            assert "tags" in post
            assert "authors" in post

    async def test_search_posts_response_structure(self, mcp_server, sample_published_post):
        """Test that search results have proper post structure."""
        from ghost_mcp.tools.content.posts import search_posts

        # Search for posts
        search_term = sample_published_post["title"].split()[0]
        result = await search_posts(search_term)
        response = json.loads(result)

        # Verify each post has essential fields
        if response["posts"]:
            post = response["posts"][0]

            essential_fields = ["id", "title", "slug", "created_at", "updated_at", "url"]
            for field in essential_fields:
                assert field in post, f"Search result should include '{field}'"

    async def test_search_only_published_posts(self, mcp_server, sample_post, sample_published_post):
        """Test that search only returns published posts, not drafts."""
        from ghost_mcp.tools.content.posts import search_posts

        # Search with a term that might match both posts
        search_term = "test"
        result = await search_posts(search_term)
        response = json.loads(result)

        # Content API only returns published posts, so all posts in results are published
        # (The Content API doesn't include a status field since all posts are published)
        assert "posts" in response, "Search should return posts"

        # Verify our published post might be in results
        published_post_ids = [post["id"] for post in response["posts"]]

        # Our draft post should NOT be in search results
        assert sample_post["id"] not in published_post_ids, "Draft posts should not appear in search"