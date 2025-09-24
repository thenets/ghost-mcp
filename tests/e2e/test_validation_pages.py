"""End-to-end validation tests for Ghost pages functionality."""

import json

import pytest

from .conftest import BaseE2ETest


@pytest.mark.e2e
@pytest.mark.admin
class TestPageValidationE2E(BaseE2ETest):
    """Test page validation functionality end-to-end."""

    async def test_validate_title_required(self, mcp_server):
        """Test that page title is required."""
        result = await self.call_mcp_tool(mcp_server, "create_page", title="")
        response = json.loads(result)

        assert "error" in response
        assert "title" in response["error"].lower()
        assert "required" in response["error"].lower() or "empty" in response["error"].lower()

    async def test_validate_title_too_long(self, mcp_server):
        """Test that page title length is validated."""
        long_title = "A" * 256  # Exceeds 255 character limit

        result = await self.call_mcp_tool(mcp_server, "create_page", title=long_title)
        response = json.loads(result)

        assert "error" in response
        assert "too long" in response["error"].lower()
        assert "255" in response["error"]

    async def test_validate_invalid_status(self, mcp_server):
        """Test validation of invalid page status."""
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            status="invalid_status"
        )
        response = json.loads(result)

        assert "error" in response
        assert "status" in response["error"].lower()
        assert "draft" in response["context"] or "published" in response["context"]

    async def test_validate_scheduled_without_date(self, mcp_server):
        """Test that scheduled pages require published_at date."""
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Scheduled Page",
            status="scheduled"
        )
        response = json.loads(result)

        assert "error" in response
        assert "scheduled" in response["error"].lower()
        assert "published_at" in response["error"].lower()

    async def test_validate_invalid_published_at(self, mcp_server):
        """Test validation of invalid published_at format."""
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Scheduled Page",
            status="scheduled",
            published_at="invalid-date-format"
        )
        response = json.loads(result)

        assert "error" in response
        assert "datetime" in response["error"].lower() or "format" in response["error"].lower()

    async def test_validate_invalid_content_format(self, mcp_server):
        """Test validation of invalid content format."""
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content="Some content",
            content_format="invalid_format"
        )
        response = json.loads(result)

        assert "error" in response
        assert "content format" in response["error"].lower()
        assert "lexical" in response["context"] or "html" in response["context"]

    async def test_validate_invalid_lexical_json(self, mcp_server):
        """Test validation of malformed Lexical JSON."""
        invalid_lexical = "{invalid json"

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "json" in response["error"].lower()

    async def test_validate_lexical_missing_root(self, mcp_server):
        """Test validation of Lexical content missing root."""
        invalid_lexical = json.dumps({"no_root": {}})

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "root" in response["error"].lower()

    async def test_validate_lexical_missing_required_props(self, mcp_server):
        """Test validation of Lexical content missing required properties."""
        invalid_lexical = json.dumps({
            "root": {
                "children": []  # Missing other required properties
            }
        })

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "missing" in response["error"].lower()

    async def test_validate_lexical_invalid_node_type(self, mcp_server):
        """Test validation of Lexical content with invalid node type."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "type": "invalid_node_type",
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
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "node type" in response["error"].lower()

    async def test_validate_lexical_heading_without_tag(self, mcp_server):
        """Test validation of Lexical heading node without tag property."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "type": "heading",
                        "version": 1,
                        "children": []
                        # Missing "tag" property
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
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "heading" in response["error"].lower()
        assert "tag" in response["error"].lower()

    async def test_validate_lexical_link_without_url(self, mcp_server):
        """Test validation of Lexical link node without URL property."""
        invalid_lexical = json.dumps({
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "type": "link",
                                "version": 1,
                                "text": "Link text"
                                # Missing "url" property
                            }
                        ],
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
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_lexical,
            content_format="lexical"
        )
        response = json.loads(result)

        assert "error" in response
        assert "link" in response["error"].lower()
        assert "url" in response["error"].lower()

    async def test_validate_html_malformed(self, mcp_server):
        """Test validation of malformed HTML content."""
        malformed_html = "<div><p>Unclosed div and paragraph tags"

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content=malformed_html,
            content_format="html"
        )
        response = json.loads(result)

        assert "error" in response
        assert "html" in response["error"].lower()
        assert "unclosed" in response["error"].lower() or "validation" in response["error"].lower()

    async def test_validate_html_invalid_tags(self, mcp_server):
        """Test validation of HTML with invalid tags."""
        invalid_html = "<script>alert('xss')</script><p>Valid paragraph</p>"

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            content=invalid_html,
            content_format="html"
        )
        response = json.loads(result)

        assert "error" in response
        assert "html" in response["error"].lower()
        assert "invalid" in response["error"].lower() or "tag" in response["error"].lower()

    async def test_validate_meta_title_too_long(self, mcp_server):
        """Test validation of meta title length."""
        long_meta_title = "A" * 301  # Exceeds 300 character limit

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            meta_title=long_meta_title
        )
        response = json.loads(result)

        assert "error" in response
        assert "meta title" in response["error"].lower()
        assert "300" in response["error"]

    async def test_validate_meta_description_too_long(self, mcp_server):
        """Test validation of meta description length."""
        long_meta_description = "A" * 501  # Exceeds 500 character limit

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            meta_description=long_meta_description
        )
        response = json.loads(result)

        assert "error" in response
        assert "meta description" in response["error"].lower()
        assert "500" in response["error"]

    async def test_validate_tag_name_too_long(self, mcp_server):
        """Test validation of tag name length."""
        long_tag = "A" * 192  # Exceeds 191 character limit

        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Test Page",
            tags=f"valid_tag,{long_tag}"
        )
        response = json.loads(result)

        assert "error" in response
        assert "tag name" in response["error"].lower()
        assert "191" in response["error"]

    async def test_validate_successful_creation_with_valid_data(self, mcp_server, cleanup_test_content):
        """Test that validation passes with all valid data."""
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
                                "text": "Valid page content",
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
            mcp_server, "create_page",
            title="Valid Test Page",
            content=valid_lexical,
            content_format="lexical",
            status="draft",
            excerpt="A test page excerpt",
            featured=True,
            tags="test,validation",
            meta_title="SEO Page Title",
            meta_description="SEO page description"
        )
        response = json.loads(result)

        # Should not contain error
        assert "error" not in response
        assert "pages" in response
        page = response["pages"][0]
        assert page["title"] == "Valid Test Page"
        assert page["status"] == "draft"

        # Track for cleanup
        cleanup_test_content["track_page"](page["id"])

    async def test_validate_update_page_validation(self, mcp_server, cleanup_test_content):
        """Test validation during page updates."""
        # First create a valid page
        result = await self.call_mcp_tool(
            mcp_server, "create_page",
            title="Original Page",
            status="draft"
        )
        response = json.loads(result)
        page_id = response["pages"][0]["id"]

        # Track for cleanup
        cleanup_test_content["track_page"](page_id)

        # Try to update with invalid data
        update_result = await self.call_mcp_tool(
            mcp_server, "update_page",
            page_id=page_id,
            title="A" * 256,  # Too long
        )
        update_response = json.loads(update_result)

        assert "error" in update_response
        assert "too long" in update_response["error"].lower()

        # Try valid update
        valid_update_result = await self.call_mcp_tool(
            mcp_server, "update_page",
            page_id=page_id,
            title="Updated Valid Page"
        )
        valid_update_response = json.loads(valid_update_result)

        assert "error" not in valid_update_response
        assert valid_update_response["pages"][0]["title"] == "Updated Valid Page"

    async def test_validate_error_response_structure(self, mcp_server):
        """Test that validation errors have consistent response structure."""
        result = await self.call_mcp_tool(mcp_server, "create_page", title="")
        response = json.loads(result)

        # All validation errors should have error and context fields
        assert "error" in response
        assert "context" in response
        assert isinstance(response["error"], str)
        assert isinstance(response["context"], str)
        assert len(response["error"]) > 0
        assert len(response["context"]) > 0