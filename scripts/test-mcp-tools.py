#!/usr/bin/env python3
"""Test Ghost MCP tools functionality."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ghost_mcp.tools.content.posts import get_posts
from ghost_mcp.tools.content.settings import get_settings
from ghost_mcp.server import check_ghost_connection


async def test_mcp_tools():
    """Test MCP tools functionality."""
    print("🧪 Testing Ghost MCP tools...")

    # Test connection check tool
    print("\n1. Testing connection check tool...")
    try:
        result = await check_ghost_connection()
        data = json.loads(result)
        print(f"✅ Connection check: {data.get('connection_test', 'unknown')}")
        print(f"   Ghost URL: {data.get('ghost_url')}")
        print(f"   Content API: {'✅' if data.get('content_api_configured') else '❌'}")
        print(f"   Admin API: {'✅' if data.get('admin_api_configured') else '❌'}")
    except Exception as e:
        print(f"❌ Connection check failed: {e}")

    # Test get settings
    print("\n2. Testing get_settings tool...")
    try:
        result = await get_settings()
        data = json.loads(result)
        if "settings" in data:
            settings = data["settings"]
            print(f"✅ Settings: Site title is '{settings.get('title')}'")
            print(f"   Description: {settings.get('description')}")
            print(f"   URL: {settings.get('url')}")
        else:
            print(f"❌ Settings: {data}")
    except Exception as e:
        print(f"❌ Settings failed: {e}")

    # Test get posts
    print("\n3. Testing get_posts tool...")
    try:
        result = await get_posts(limit=2)
        data = json.loads(result)
        if "posts" in data:
            posts = data["posts"]
            print(f"✅ Posts: Found {len(posts)} posts")
            for post in posts:
                print(f"   - '{post.get('title')}' (status: {post.get('status')})")
        else:
            print(f"❌ Posts: {data}")
    except Exception as e:
        print(f"❌ Posts failed: {e}")

    print("\n🎉 MCP tools test completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())