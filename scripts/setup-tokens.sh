#!/bin/bash
set -e

# Ghost MCP API Token Setup Script
echo "🔑 Setting up Ghost MCP API tokens..."

# Check if Docker containers are running
if ! docker-compose ps | grep -q "ghost-mcp-dev.*Up"; then
    echo "❌ Error: Ghost container is not running"
    echo "Please run: make start-ghost"
    exit 1
fi

if ! docker-compose ps | grep -q "ghost-db-dev.*Up"; then
    echo "❌ Error: Ghost database container is not running"
    echo "Please run: make start-ghost"
    exit 1
fi

echo "✅ Ghost containers are running"

# Wait for Ghost to be fully ready
echo "⏳ Waiting for Ghost API to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s "http://localhost:2368/ghost/api/content/" >/dev/null 2>&1; then
        break
    fi
    echo "   Attempt $((attempt + 1))/$max_attempts - waiting for Ghost..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: Ghost API did not become ready in time"
    exit 1
fi

echo "✅ Ghost API is ready"

# Extract API keys from database
echo "🔍 Extracting API keys from Ghost database..."

CONTENT_API_KEY=$(docker exec ghost-db-dev mysql -u root -prootpassword ghost_dev -e "SELECT secret FROM api_keys WHERE type='content' LIMIT 1;" 2>/dev/null | tail -n 1)
ADMIN_API_DATA=$(docker exec ghost-db-dev mysql -u root -prootpassword ghost_dev -e "SELECT id, secret FROM api_keys WHERE type='admin' LIMIT 1;" 2>/dev/null | tail -n 1)

if [ -z "$CONTENT_API_KEY" ] || [ "$CONTENT_API_KEY" = "secret" ]; then
    echo "❌ Error: Could not retrieve Content API key"
    exit 1
fi

if [ -z "$ADMIN_API_DATA" ] || [ "$ADMIN_API_DATA" = "id	secret" ]; then
    echo "❌ Error: Could not retrieve Admin API key"
    exit 1
fi

# Parse admin API data (format: "id secret")
ADMIN_API_ID=$(echo "$ADMIN_API_DATA" | cut -f1)
ADMIN_API_SECRET=$(echo "$ADMIN_API_DATA" | cut -f2)
ADMIN_API_KEY="${ADMIN_API_ID}:${ADMIN_API_SECRET}"

echo "✅ API keys extracted successfully"
echo "   Content API Key: ${CONTENT_API_KEY:0:10}..."
echo "   Admin API Key: ${ADMIN_API_ID:0:10}:${ADMIN_API_SECRET:0:10}..."

# Create .env file
echo "📝 Creating .env file..."

cat > .env << EOF
# Ghost MCP Server Configuration
# Generated on $(date)

# Ghost instance configuration
GHOST_URL=http://localhost:2368
GHOST_CONTENT_API_KEY=$CONTENT_API_KEY
GHOST_ADMIN_API_KEY=$ADMIN_API_KEY
GHOST_VERSION=v5.0
GHOST_MODE=auto
GHOST_TIMEOUT=30
GHOST_MAX_RETRIES=3
GHOST_RETRY_BACKOFF_FACTOR=2.0

# Logging configuration
LOG_LEVEL=info
LOG_STRUCTURED=true
LOG_REQUEST_ID=true
EOF

echo "✅ .env file created successfully"

# Test the configuration
echo "🧪 Testing API connectivity..."

# Test Content API
echo "   Testing Content API..."
CONTENT_TEST=$(curl -s "http://localhost:2368/ghost/api/content/settings/?key=$CONTENT_API_KEY" | grep -o '"title"' || echo "")
if [ -n "$CONTENT_TEST" ]; then
    echo "   ✅ Content API: Working"
else
    echo "   ❌ Content API: Failed"
fi

# Test Admin API (using Python to generate JWT and test)
echo "   Testing Admin API..."
python3 -c "
import asyncio
import sys
import os
sys.path.insert(0, 'src')

async def test_admin():
    try:
        from ghost_mcp.client import GhostClient
        async with GhostClient() as client:
            result = await client._make_request('GET', 'site/', api_type='admin')
            print('   ✅ Admin API: Working')
    except Exception as e:
        print(f'   ❌ Admin API: Failed - {e}')

asyncio.run(test_admin())
" 2>/dev/null || echo "   ⚠️  Admin API: Could not test (install dependencies first)"

echo ""
echo "🎉 Ghost MCP API tokens setup complete!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: make install"
echo "2. Test the implementation: make test"
echo "3. Run the MCP server: make run"
echo ""
echo "Configuration file: .env"
echo "Ghost admin interface: http://localhost:2368/ghost/"
echo "Ghost public site: http://localhost:2368/"