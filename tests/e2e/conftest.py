"""Fixtures for end-to-end tests."""

import asyncio
import json
import os
import uuid
from typing import AsyncGenerator, Dict, List, Any

import pytest
import httpx

from ghost_mcp.server import mcp
from ghost_mcp.client import GhostClient
from ghost_mcp.config import config


@pytest.fixture(scope="session")
def ensure_ghost_running():
    """Ensure Ghost container is running before tests."""
    import subprocess

    try:
        # Check if Ghost is accessible
        response = httpx.get("http://localhost:2368", timeout=5)
        if response.status_code != 200:
            raise Exception("Ghost not accessible")
    except Exception:
        # Try to start Ghost containers
        result = subprocess.run(
            ["docker", "compose", "ps", "-q", "ghost"],
            capture_output=True,
            text=True,
            cwd="/var/home/luiz/projects/thenets/ghost-mcp"
        )

        if not result.stdout.strip():
            pytest.skip("Ghost container not running. Run 'make start-ghost' first.")

    # Verify environment configuration
    if not os.getenv("GHOST_CONTENT_API_KEY") or not os.getenv("GHOST_ADMIN_API_KEY"):
        pytest.skip("Ghost API keys not configured. Run 'make setup-tokens' first.")


@pytest.fixture
async def ghost_client() -> AsyncGenerator[GhostClient, None]:
    """Provide a Ghost client for tests."""
    async with GhostClient() as client:
        yield client


_tools_registered = False

@pytest.fixture
def mcp_server():
    """Provide the MCP server instance."""
    global _tools_registered
    if not _tools_registered:
        from ghost_mcp.server import register_tools
        # Ensure tools are registered for testing
        register_tools()
        _tools_registered = True
    return mcp


@pytest.fixture
async def test_post_data() -> Dict[str, Any]:
    """Provide test data for creating posts."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "title": f"Test Post {unique_id}",
        "content": json.dumps({
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "detail": 0,
                                "format": 0,
                                "mode": "normal",
                                "style": "",
                                "text": f"This is a test post content for e2e testing. ID: {unique_id}",
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
        }),
        "content_format": "lexical",
        "status": "draft"
    }


@pytest.fixture
async def test_page_data() -> Dict[str, Any]:
    """Provide test data for creating pages."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "title": f"Test Page {unique_id}",
        "content": json.dumps({
            "root": {
                "children": [
                    {
                        "children": [
                            {
                                "detail": 0,
                                "format": 0,
                                "mode": "normal",
                                "style": "",
                                "text": f"This is a test page content for e2e testing. ID: {unique_id}",
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
        }),
        "content_format": "lexical",
        "status": "draft"
    }


@pytest.fixture
async def test_tag_data() -> Dict[str, str]:
    """Provide test data for creating tags."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"test-tag-{unique_id}",
        "description": f"Test tag for e2e testing {unique_id}"
    }


@pytest.fixture
async def cleanup_test_content(ghost_client: GhostClient):
    """Clean up test content after each test."""
    created_posts = []
    created_pages = []
    created_tags = []

    def track_post(post_id: str):
        created_posts.append(post_id)

    def track_page(page_id: str):
        created_pages.append(page_id)

    def track_tag(tag_id: str):
        created_tags.append(tag_id)

    # Provide tracking functions
    yield {
        "track_post": track_post,
        "track_page": track_page,
        "track_tag": track_tag
    }

    # Cleanup after test
    for post_id in created_posts:
        try:
            await ghost_client._make_request("DELETE", f"posts/{post_id}/", api_type="admin")
        except Exception:
            pass  # Ignore cleanup errors

    for page_id in created_pages:
        try:
            await ghost_client._make_request("DELETE", f"pages/{page_id}/", api_type="admin")
        except Exception:
            pass  # Ignore cleanup errors

    for tag_id in created_tags:
        try:
            await ghost_client._make_request("DELETE", f"tags/{tag_id}/", api_type="admin")
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture
async def sample_post(ghost_client: GhostClient, test_post_data: Dict[str, Any], cleanup_test_content):
    """Create a sample post for testing."""
    # Create a post
    response = await ghost_client._make_request(
        "POST",
        "posts/",
        api_type="admin",
        json_data={"posts": [test_post_data]}
    )

    post_data = response["posts"][0]
    cleanup_test_content["track_post"](post_data["id"])

    return post_data


@pytest.fixture
async def sample_published_post(ghost_client: GhostClient, test_post_data: Dict[str, Any], cleanup_test_content):
    """Create a sample published post for testing."""
    # Modify data for published post
    test_post_data["status"] = "published"

    # Create a published post
    response = await ghost_client._make_request(
        "POST",
        "posts/",
        api_type="admin",
        json_data={"posts": [test_post_data]}
    )

    post_data = response["posts"][0]
    cleanup_test_content["track_post"](post_data["id"])

    return post_data


@pytest.fixture
async def sample_page(ghost_client: GhostClient, test_page_data: Dict[str, Any], cleanup_test_content):
    """Create a sample page for testing."""
    # Create a page
    response = await ghost_client._make_request(
        "POST",
        "pages/",
        api_type="admin",
        json_data={"pages": [test_page_data]}
    )

    page_data = response["pages"][0]
    cleanup_test_content["track_page"](page_data["id"])

    return page_data


@pytest.fixture
async def sample_tag(ghost_client: GhostClient, test_tag_data: Dict[str, str], cleanup_test_content):
    """Create a sample tag for testing."""
    # Create a tag
    response = await ghost_client._make_request(
        "POST",
        "tags/",
        api_type="admin",
        json_data={"tags": [test_tag_data]}
    )

    tag_data = response["tags"][0]
    cleanup_test_content["track_tag"](tag_data["id"])

    return tag_data


@pytest.mark.e2e
class BaseE2ETest:
    """Base class for e2e tests."""

    @pytest.fixture(autouse=True)
    def setup_test(self, ensure_ghost_running):
        """Auto-use the Ghost running check."""
        pass

    async def get_mcp_tool(self, mcp_server, tool_name: str):
        """Get an MCP tool by name from the server."""
        tools = await mcp_server.get_tools()
        if tool_name not in tools:
            available_tools = list(tools.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
        return tools[tool_name]

    async def call_mcp_tool(self, mcp_server, tool_name: str, **kwargs):
        """Call an MCP tool with the given arguments."""
        tool = await self.get_mcp_tool(mcp_server, tool_name)
        result = await tool.run(kwargs)
        # Return the text content if it's a ToolResult with content list, otherwise return as-is
        if hasattr(result, 'content') and isinstance(result.content, list) and len(result.content) > 0:
            if hasattr(result.content[0], 'text'):
                return result.content[0].text
            return result.content[0]
        elif hasattr(result, 'content'):
            return result.content
        return result