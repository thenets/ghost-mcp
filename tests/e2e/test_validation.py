"""End-to-end tests for Ghost MCP validation functionality."""

import json
import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
@pytest.mark.admin
class TestPostValidationE2E(BaseE2ETest):
    """Test post validation functionality end-to-end."""

    async def test_validate_title_required(self, mcp_server):
        """Test that title is required for post creation."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title=""
        )
        response = json.loads(result)

        assert "error" in response
        assert "title" in response["error"].lower()
        assert "required" in response["error"].lower()

    async def test_validate_title_too_long(self, mcp_server):
        """Test that overly long titles are rejected."""
        long_title = "A" * 300  # Exceeds 255 character limit
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title=long_title
        )
        response = json.loads(result)

        assert "error" in response
        assert "too long" in response["error"].lower()
        assert "255" in response["error"]

    async def test_validate_invalid_status(self, mcp_server):
        """Test that invalid status values are rejected."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            status="invalid_status"
        )
        response = json.loads(result)

        assert "error" in response
        assert "invalid" in response["error"].lower() or "status" in response["error"].lower()
        assert "context" in response

    async def test_validate_scheduled_without_date(self, mcp_server):
        """Test that scheduled posts require published_at."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Scheduled Post",
            status="scheduled"
        )
        response = json.loads(result)

        assert "error" in response
        assert "scheduled" in response["error"].lower()
        assert "published_at" in response["error"].lower()
        assert "context" in response

    async def test_validate_invalid_published_at(self, mcp_server):
        """Test that invalid datetime formats are rejected."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            status="scheduled",
            published_at="invalid-date-format"
        )
        response = json.loads(result)

        assert "error" in response
        assert "invalid" in response["error"].lower()
        assert "datetime" in response["error"].lower() or "format" in response["error"].lower()
        assert "ISO" in response.get("context", "")

    async def test_validate_invalid_content_format(self, mcp_server):
        """Test that invalid content formats are rejected."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content="Some content",
            content_format="invalid_format"
        )
        response = json.loads(result)

        assert "error" in response
        assert "content format" in response["error"].lower() or "format" in response["error"].lower()
        assert "context" in response

    async def test_validate_invalid_lexical_json(self, mcp_server):
        """Test that malformed Lexical JSON is rejected."""
        invalid_lexical = '{"root": {"invalid": json}}'  # Invalid JSON
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "json" in response["error"].lower()
        assert "context" in response

    async def test_validate_lexical_missing_root(self, mcp_server):
        """Test that Lexical JSON without root is rejected."""
        invalid_lexical = json.dumps({"notroot": {"children": []}})
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "root" in response["error"].lower()
        assert "context" in response

    async def test_validate_lexical_missing_required_props(self, mcp_server):
        """Test that Lexical JSON with missing required properties is rejected."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [],
                # Missing required properties like direction, format, indent, type, version
            }
        })
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "missing" in response["error"].lower() or "property" in response["error"].lower()
        assert "context" in response

    async def test_validate_lexical_invalid_node_type(self, mcp_server):
        """Test that Lexical nodes with invalid types are rejected."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "type": "invalid_node_type",
                        "version": 1,
                        "children": []
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        })
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "invalid" in response["error"].lower()
        assert "type" in response["error"].lower()

    async def test_validate_lexical_heading_without_tag(self, mcp_server):
        """Test that heading nodes without tag property are rejected."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "type": "heading",
                        "version": 1,
                        "children": [
                            {
                                "type": "text",
                                "text": "Heading text",
                                "version": 1
                            }
                        ]
                        # Missing "tag" property for heading
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        })
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "heading" in response["error"].lower()
        assert "tag" in response["error"].lower()

    async def test_validate_lexical_link_without_url(self, mcp_server):
        """Test that link nodes without URL property are rejected."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "type": "paragraph",
                        "version": 1,
                        "direction": "ltr",
                        "format": "",
                        "indent": 0,
                        "children": [
                            {
                                "type": "link",
                                "text": "Link text",
                                "version": 1
                                # Missing "url" property for link
                            }
                        ]
                    }
                ],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        })
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "link" in response["error"].lower()
        assert "url" in response["error"].lower()

    async def test_validate_html_malformed(self, mcp_server):
        """Test that malformed HTML is rejected."""
        invalid_html = "<p>Unclosed paragraph<div>Nested div</p></div>"
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_html,
            content_format="html"
        )
        response = json.loads(result)

        assert "error" in response
        assert ("html" in response["error"].lower() or
                "tag" in response["error"].lower() or
                "validation" in response["error"].lower())

    async def test_validate_html_invalid_tags(self, mcp_server):
        """Test that HTML with invalid tags is rejected."""
        invalid_html = "<script>alert('xss')</script><custom-tag>Invalid</custom-tag>"
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            content=invalid_html,
            content_format="html"
        )
        response = json.loads(result)

        assert "error" in response
        assert ("invalid" in response["error"].lower() and "tag" in response["error"].lower())

    async def test_validate_meta_title_too_long(self, mcp_server):
        """Test that overly long meta titles are rejected."""
        long_meta_title = "A" * 350  # Exceeds 300 character limit
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            meta_title=long_meta_title
        )
        response = json.loads(result)

        assert "error" in response
        assert "meta title" in response["error"].lower()
        assert "too long" in response["error"].lower()
        assert "300" in response["error"]

    async def test_validate_meta_description_too_long(self, mcp_server):
        """Test that overly long meta descriptions are rejected."""
        long_meta_desc = "A" * 550  # Exceeds 500 character limit
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            meta_description=long_meta_desc
        )
        response = json.loads(result)

        assert "error" in response
        assert "meta description" in response["error"].lower()
        assert "too long" in response["error"].lower()
        assert "500" in response["error"]

    async def test_validate_tag_name_too_long(self, mcp_server):
        """Test that overly long tag names are rejected."""
        long_tag = "A" * 200  # Exceeds 191 character limit
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Test Post",
            tags=f"valid-tag,{long_tag},another-valid-tag"
        )
        response = json.loads(result)

        assert "error" in response
        assert "tag" in response["error"].lower()
        assert "too long" in response["error"].lower()
        assert "191" in response["error"]

    async def test_validate_successful_creation_with_valid_data(self, mcp_server, cleanup_test_content):
        """Test that properly formatted content passes validation."""
        valid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "detail": 0,
                                "format": 0,
                                "mode": "normal",
                                "style": "",
                                "text": "Valid Content",
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

        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="Valid Test Post",
            content=valid_lexical,
            content_format="lexical",
            status="draft",
            excerpt="Test excerpt",
            featured=False,
            meta_title="Valid Meta Title",
            meta_description="Valid meta description",
            tags="test,validation,success"
        )
        response = json.loads(result)

        # Should succeed without errors
        assert "error" not in response
        assert "posts" in response
        post = response["posts"][0]
        assert post["title"] == "Valid Test Post"
        assert post["status"] == "draft"

        # Track for cleanup
        cleanup_test_content["track_post"](post["id"])

    async def test_validate_update_post_validation(self, mcp_server, sample_post):
        """Test that update_post also validates input properly."""
        # Test with invalid status
        result = await self.call_mcp_tool(
            mcp_server, "update_post",
            post_id=sample_post["id"],
            status="invalid_status"
        )
        response = json.loads(result)

        assert "error" in response
        assert ("invalid" in response["error"].lower() or "status" in response["error"].lower())

    async def test_validate_error_response_structure(self, mcp_server):
        """Test that validation errors return proper structure with examples."""
        result = await self.call_mcp_tool(
            mcp_server, "create_post",
            title="",  # Invalid title
            content_format="invalid"  # Invalid format
        )
        response = json.loads(result)

        # Verify error response structure
        assert "error" in response
        assert "context" in response or "examples" in response

        # Should include examples for content formats
        if "examples" in response:
            examples = response["examples"]
            assert "lexical_simple" in examples
            assert "html_simple" in examples