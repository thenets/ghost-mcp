#!/usr/bin/env python3
"""Test Ghost API connectivity script."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ghost_mcp.client import GhostClient


async def test_connection():
    """Test Ghost API connection."""
    print("🧪 Testing Ghost API connection...")

    async with GhostClient() as client:
        # Test Content API
        try:
            result = await client._make_request("GET", "settings/", api_type="content")
            title = result.get("settings", {}).get("title", "Unknown")
            print(f"✅ Content API: Connected to '{title}'")
        except Exception as e:
            print(f"❌ Content API: {e}")

        # Test Admin API
        try:
            result = await client._make_request("GET", "site/", api_type="admin")
            print("✅ Admin API: Connected successfully")
        except Exception as e:
            print(f"❌ Admin API: {e}")

        # Test posts endpoint
        try:
            result = await client.get_posts(limit=1)
            posts_count = len(result.get("posts", []))
            print(f"✅ Posts: Found {posts_count} posts")
        except Exception as e:
            print(f"❌ Posts: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())