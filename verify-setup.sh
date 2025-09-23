#!/bin/bash

# Ghost MCP Setup Verification Script
# This script verifies that the Ghost Docker setup is working correctly

set -e

echo "🔍 Ghost MCP Setup Verification"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if Docker Compose is available
echo "1. Checking Docker Compose..."
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    print_status 0 "Docker Compose is available"
else
    print_status 1 "Docker Compose is not available"
    exit 1
fi

# Check if containers are running
echo -e "\n2. Checking container status..."
if docker compose ps | grep -q "ghost-mcp-dev.*Up"; then
    print_status 0 "Ghost container is running"
else
    print_status 1 "Ghost container is not running"
    echo "   Run: docker compose up -d"
    exit 1
fi

if docker compose ps | grep -q "ghost-db-dev.*Up.*healthy"; then
    print_status 0 "MySQL database is running and healthy"
else
    print_status 1 "MySQL database is not running or unhealthy"
    echo "   Check logs: docker compose logs ghost-db"
    exit 1
fi

# Check if Ghost is responding
echo -e "\n3. Checking Ghost accessibility..."

# Test main site
if curl -s -f http://localhost:2368/ > /dev/null; then
    print_status 0 "Ghost main site is accessible (http://localhost:2368)"
else
    print_status 1 "Ghost main site is not accessible"
    exit 1
fi

# Test admin interface
if curl -s -f http://localhost:2368/ghost/ > /dev/null; then
    print_status 0 "Ghost admin interface is accessible (http://localhost:2368/ghost)"
else
    print_status 1 "Ghost admin interface is not accessible"
    exit 1
fi

# Test Content API (should return auth error, which means it's working)
content_api_response=$(curl -s http://localhost:2368/ghost/api/content/settings/ 2>/dev/null || echo "")
if echo "$content_api_response" | grep -q "Authorization failed"; then
    print_status 0 "Ghost Content API is responding (authentication required)"
elif echo "$content_api_response" | grep -q "posts\|settings"; then
    print_status 0 "Ghost Content API is responding (no auth required - dev mode?)"
else
    print_status 1 "Ghost Content API is not responding correctly"
    echo "   Response: $content_api_response"
    exit 1
fi

# Check volumes
echo -e "\n4. Checking data persistence..."
if docker volume ls | grep -q "ghost_mcp_content"; then
    print_status 0 "Ghost content volume exists"
else
    print_status 1 "Ghost content volume missing"
fi

if docker volume ls | grep -q "ghost_mcp_mysql"; then
    print_status 0 "MySQL data volume exists"
else
    print_status 1 "MySQL data volume missing"
fi

# Check if setup is completed
echo -e "\n5. Checking Ghost setup status..."
setup_response=$(curl -s http://localhost:2368/ghost/api/admin/site/ 2>/dev/null || echo "")
if echo "$setup_response" | grep -q '"setup":false'; then
    print_warning "Ghost setup is not completed yet"
    print_info "Visit http://localhost:2368/ghost to complete the initial setup"
    print_info "After setup, create a custom integration to get API keys"
elif echo "$setup_response" | grep -q '"setup":true'; then
    print_status 0 "Ghost setup appears to be completed"
    print_info "Visit http://localhost:2368/ghost to access admin panel"
    print_info "Go to Settings > Integrations to create API keys"
else
    print_warning "Could not determine Ghost setup status"
    print_info "Visit http://localhost:2368/ghost to check setup"
fi

echo -e "\n🎉 Setup Verification Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Visit http://localhost:2368/ghost to complete Ghost setup (if not done)"
echo "2. Create a custom integration to get API keys:"
echo "   - Go to Settings → Integrations → Add custom integration"
echo "   - Copy both Content API Key and Admin API Key"
echo "3. Test the APIs using the keys"
echo ""
echo "Useful commands:"
echo "• View logs: docker compose logs -f ghost"
echo "• Stop services: docker compose down"
echo "• Restart services: docker compose restart"
echo "• Reset everything: docker compose down -v"
echo ""

# Show running containers summary
echo "Currently running containers:"
docker compose ps --format table

exit 0