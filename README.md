# Ghost MCP Server

A comprehensive Model Context Protocol (MCP) server for Ghost CMS, providing both read-only Content API and read/write Admin API access through FastMCP.

## ⚡ Quick Start

For Claude Code:
```bash
claude mcp add ghost --scope user \
  -e GHOST_URL=http://localhost:2368 \
  -e GHOST_CONTENT_API_KEY=your_key_here \
  -e GHOST_ADMIN_API_KEY=your_key_here \
  -- uvx ghost-mcp
```

## 🌟 Getting Started

### Standard Configuration

For most MCP clients, use this configuration:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": [
        "--refresh",
        "--from",
        "git+https://github.com/thenets/ghost-mcp.git",
        "ghost-mcp"
      ],
      "env": {
        "GHOST_URL": "http://localhost:2368",
        "GHOST_CONTENT_API_KEY": "your_content_api_key_here",
        "GHOST_ADMIN_API_KEY": "your_admin_api_key_here"
      }
    }
  }
}
```

### Creating API Keys

To create the required API keys for your Ghost instance:

1. **Content API Key**: In your Ghost admin panel, go to **Settings** → **Integrations** → **Add custom integration**
2. **Admin API Key**: The same custom integration will provide both Content and Admin API keys
3. Set the environment variables in your configuration as shown above

For local development, you can use the automated setup:

```bash
make setup  # This will start Ghost, create tokens, and configure everything
```

## 🎯 Features

- **Complete Ghost API Coverage**: Both Content API (read-only) and Admin API (read/write)
- **15+ MCP Tools**: Posts, pages, tags, authors, settings, and more
- **Modern Python Implementation**: FastMCP 2.12.3 with async/await
- **JWT Authentication**: Secure Admin API access with token caching
- **Robust Error Handling**: 5 error categories with comprehensive logging
- **Configuration Management**: Environment variables with precedence
- **Development Tools**: Complete Docker setup and automation scripts

## 🛠️ Development

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (with uv recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/thenets/ghost-mcp.git
cd ghost-mcp

# Complete setup from scratch
make setup

# Or step by step:
make install-uv         # Install uv package manager
make install            # Install Python dependencies
make start-ghost        # Start Ghost and database
make setup-tokens       # Extract API keys and create .env
make test               # Test the implementation
```

### Usage

```bash
# Run the MCP server
make run

# Development mode with auto-reload
make dev

# Check system status
make status

# View container logs
make logs
```

### Project Structure

```
ghost-mcp/
├── src/ghost_mcp/
│   ├── server.py           # FastMCP server entry point
│   ├── client.py           # Ghost API client
│   ├── config.py           # Configuration management
│   ├── auth/               # Authentication modules
│   ├── tools/
│   │   ├── content/        # Content API tools
│   │   └── admin/          # Admin API tools
│   ├── types/              # Type definitions
│   └── utils/              # Utilities
├── scripts/                # Setup and test scripts
├── contracts/              # API documentation
├── docker-compose.yml      # Ghost + MySQL setup
├── Makefile               # Development commands
└── pyproject.toml         # Python project config
```

### Available Commands

```bash
make help               # Show all commands
make setup              # Complete setup from scratch
make install            # Install dependencies with uv
make start-ghost        # Start Ghost containers
make setup-tokens       # Generate API keys
make test               # Run tests
make test-connection    # Test API connectivity
make run                # Run MCP server
make status             # Check system status
make clean              # Clean up everything
```

## 📋 Available MCP Tools

### Content API Tools (Read-only)

- `get_posts` - Get published posts with filtering/pagination
- `get_post_by_id` - Get single post by ID
- `get_post_by_slug` - Get single post by slug
- `search_posts` - Search posts by title/content
- `get_pages` - Get published pages
- `get_page_by_id` - Get single page by ID
- `get_page_by_slug` - Get single page by slug
- `get_tags` - Get tags with filtering
- `get_tag_by_id` - Get single tag by ID
- `get_tag_by_slug` - Get single tag by slug
- `get_authors` - Get authors
- `get_author_by_id` - Get single author by ID
- `get_author_by_slug` - Get single author by slug
- `get_settings` - Get public settings
- `get_site_info` - Get basic site information

### Admin API Tools (Read/Write)

- `create_post` - Create new posts with full options
- `update_post` - Update existing posts
- `delete_post` - Delete posts
- `get_admin_posts` - Get posts including drafts
- `create_page` - Create new pages
- `create_tag` - Create new tags

### Utility Tools

- `check_ghost_connection` - Test connectivity and configuration

## 🔧 Configuration

Configuration is managed through environment variables with precedence:

1. Environment variables
2. `.env` file
3. Default values

### Required Variables

```bash
GHOST_URL=http://localhost:2368
GHOST_CONTENT_API_KEY=your_content_api_key_here
GHOST_ADMIN_API_KEY=your_admin_api_key_here
```

### Optional Variables

```bash
GHOST_VERSION=v5.0
GHOST_MODE=auto          # auto, readonly, readwrite
GHOST_TIMEOUT=30
GHOST_MAX_RETRIES=3
GHOST_RETRY_BACKOFF_FACTOR=2.0

LOG_LEVEL=info           # debug, info, warning, error
LOG_STRUCTURED=true
LOG_REQUEST_ID=true
```


## 🐳 Docker Environment

The project includes a complete Docker Compose setup:

- **Ghost**: Latest Ghost 5.x with Alpine Linux
- **MySQL 8.0**: Database with health checks
- **Development optimized**: Logging, auto-restart, volume persistence

### URLs

- **Ghost Admin**: http://localhost:2368/ghost/
- **Ghost Site**: http://localhost:2368/
- **Database**: localhost:3306

## 🔐 API Authentication

### Content API
- Uses query parameter authentication
- 26-character hex API key
- Read-only access to published content

### Admin API
- Uses JWT token authentication
- Format: `id:secret` (24-char + 64-char hex)
- 5-minute token expiration with automatic renewal
- Full read/write access

## 📊 Error Handling

Comprehensive error handling with 5 categories:

1. **Network Errors**: Connection timeouts, DNS failures
2. **Authentication Errors**: Invalid keys, expired tokens
3. **Ghost API Errors**: Ghost-specific errors with codes
4. **Validation Errors**: Invalid parameters, malformed data
5. **File Upload Errors**: Media upload failures

All errors include:
- Unique error ID
- Category classification
- Context information
- Request ID for tracing

## 🧪 Testing

```bash
# Test Ghost API connectivity
make test-connection

# Run all tests
make test

# Test specific functionality
make test-connection
```

## 📝 Logging

Structured logging with configurable levels:

- **Request IDs**: Track requests across components
- **Structured format**: JSON output for production
- **Context preservation**: Error context and debugging info
- **Performance metrics**: Request timing and retry information

## 🔄 Retry Logic

Robust retry mechanism:

- **Exponential backoff**: Configurable base delay and multiplier
- **Jitter**: Prevents thundering herd problems
- **Max retries**: Configurable retry limits
- **Circuit breaker**: Fail fast after repeated failures

## 📚 Documentation

- **API Contracts**: Complete Ghost API documentation in `contracts/`
- **Type Definitions**: Full type coverage with Pydantic models
- **Examples**: Working examples for all tools
- **Development Guide**: Step-by-step setup and usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make test` to verify
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub issues for bugs and features
- **Documentation**: Check `contracts/` for API details
- **Logs**: Use `make logs` for troubleshooting
- **Status**: Use `make status` for system health

---

**Built with FastMCP 2.12.3 and Ghost 5.x** 🚀