# Ghost MCP

This is the spec for the Ghost Blog platform MCP server.

## Goal

- The main goal is to implement the MCP tools for all https://docs.ghost.org/content-api REST actions
- Provide a comprehensive MCP server that allows Claude to interact with Ghost blog content
- Support all major Ghost Content API endpoints for reading published content

## Requirements

### Infrastructure
- Deploy a local Ghost instance using `docker compose` and figure out a way to create an API key
- Set up proper authentication using Ghost Content API keys
- Configure the MCP server to connect to the Ghost instance

### Development
- Implement MCP server using Node.js/TypeScript
- Follow MCP protocol specifications
- Include comprehensive error handling and validation
- Support proper filtering, pagination, and query parameters

## Ghost Content API Endpoints

The Ghost Content API provides read-only access to published content. All endpoints support the following:
- Content API key authentication (query parameter)
- JSON response format with consistent structure
- Filtering, pagination, and field selection
- Full caching support

### Posts
- `GET /posts/` - List all published posts
- `GET /posts/{id}/` - Get a specific post by ID
- `GET /posts/slug/{slug}/` - Get a specific post by slug

### Pages
- `GET /pages/` - List all published pages
- `GET /pages/{id}/` - Get a specific page by ID
- `GET /pages/slug/{slug}/` - Get a specific page by slug

### Tags
- `GET /tags/` - List all tags
- `GET /tags/{id}/` - Get a specific tag by ID
- `GET /tags/slug/{slug}/` - Get a specific tag by slug

### Authors
- `GET /authors/` - List all authors
- `GET /authors/{id}/` - Get a specific author by ID
- `GET /authors/slug/{slug}/` - Get a specific author by slug

### Tiers
- `GET /tiers/` - List all membership tiers

### Settings
- `GET /settings/` - Get public settings

## API Response Format

All Ghost Content API responses follow this structure:
```json
{
    "resource_type": [{ ... }],
    "meta": {
        "pagination": {
            "page": 1,
            "limit": 15,
            "pages": 1,
            "total": 1,
            "next": null,
            "prev": null
        }
    }
}
```

## MCP Tools Specification

The following MCP tools should be implemented to provide comprehensive access to the Ghost Content API:

### Posts Tools
- **`ghost_list_posts`** - List all published posts
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of post objects with pagination metadata

- **`ghost_get_post_by_id`** - Get a specific post by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single post object

- **`ghost_get_post_by_slug`** - Get a specific post by slug
  - Parameters: `slug` (required string), `include?` (string), `fields?` (string)
  - Returns: Single post object

### Pages Tools
- **`ghost_list_pages`** - List all published pages
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of page objects with pagination metadata

- **`ghost_get_page_by_id`** - Get a specific page by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single page object

- **`ghost_get_page_by_slug`** - Get a specific page by slug
  - Parameters: `slug` (required string), `include?` (string), `fields?` (string)
  - Returns: Single page object

### Tags Tools
- **`ghost_list_tags`** - List all tags
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of tag objects with pagination metadata

- **`ghost_get_tag_by_id`** - Get a specific tag by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single tag object

- **`ghost_get_tag_by_slug`** - Get a specific tag by slug
  - Parameters: `slug` (required string), `include?` (string), `fields?` (string)
  - Returns: Single tag object

### Authors Tools
- **`ghost_list_authors`** - List all authors
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of author objects with pagination metadata

- **`ghost_get_author_by_id`** - Get a specific author by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single author object

- **`ghost_get_author_by_slug`** - Get a specific author by slug
  - Parameters: `slug` (required string), `include?` (string), `fields?` (string)
  - Returns: Single author object

### Other Tools
- **`ghost_list_tiers`** - List all membership tiers
  - Parameters: `limit?` (number), `page?` (number), `include?` (string), `fields?` (string)
  - Returns: Array of tier objects

- **`ghost_get_settings`** - Get public settings
  - Parameters: None
  - Returns: Settings object

### Common Parameters
- `limit`: Number of resources to return (default: 15, max: 50)
- `page`: Page number for pagination (default: 1)
- `filter`: Filter string using Ghost's filtering syntax
- `include`: Comma-separated list of related resources to include
- `fields`: Comma-separated list of fields to return

## Docker Compose Setup

Create a `docker-compose.yml` file to run Ghost locally:

```yaml
version: '3.8'
services:
  ghost:
    image: ghost:5-alpine
    restart: always
    ports:
      - "2368:2368"
    environment:
      database__client: mysql
      database__connection__host: db
      database__connection__user: root
      database__connection__password: yourpassword
      database__connection__database: ghost
      url: http://localhost:2368
    volumes:
      - ghost_content:/var/lib/ghost/content
    depends_on:
      - db

  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: yourpassword
      MYSQL_DATABASE: ghost
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  ghost_content:
  mysql_data:
```

### API Key Creation Process

1. Start the Ghost instance: `docker compose up -d`
2. Visit `http://localhost:2368/ghost` to set up your admin account
3. Navigate to Settings → Integrations → Custom Integrations
4. Create a new integration to get your Content API key
5. Save the Content API key for MCP server configuration

## Configuration

The MCP server should support configuration via:

### Environment Variables
- `GHOST_URL`: Ghost instance URL (default: http://localhost:2368)
- `GHOST_CONTENT_API_KEY`: Content API key (required)
- `GHOST_VERSION`: API version (default: v5.0)

### Configuration File
Alternative JSON configuration file:
```json
{
  "ghost": {
    "url": "http://localhost:2368",
    "contentApiKey": "your-content-api-key",
    "version": "v5.0"
  }
}
```

## Implementation Details

### Project Structure
```
ghost-mcp/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── ghost-client.ts       # Ghost API client
│   ├── tools/
│   │   ├── posts.ts          # Post-related tools
│   │   ├── pages.ts          # Page-related tools
│   │   ├── tags.ts           # Tag-related tools
│   │   ├── authors.ts        # Author-related tools
│   │   └── settings.ts       # Settings and tiers tools
│   ├── types/
│   │   ├── ghost.ts          # Ghost API response types
│   │   └── mcp.ts            # MCP-specific types
│   └── utils/
│       ├── validation.ts     # Parameter validation
│       └── errors.ts         # Error handling utilities
├── package.json
├── tsconfig.json
├── docker-compose.yml
└── README.md
```

### Technology Stack
- **Node.js** (v18+) with **TypeScript**
- **@modelcontextprotocol/sdk** for MCP implementation
- **axios** or **fetch** for HTTP requests
- **zod** for runtime type validation
- **dotenv** for environment variable management

### Error Handling
- Validate all input parameters using Zod schemas
- Handle Ghost API errors gracefully with meaningful messages
- Implement retry logic for transient network errors
- Return proper MCP error responses with error codes

### Testing Strategy
- Unit tests for individual tools and utilities
- Integration tests with local Ghost instance
- Mock Ghost API responses for reliable testing
- Test parameter validation and error scenarios

### Performance Considerations
- Implement request caching where appropriate
- Use connection pooling for HTTP requests
- Support streaming responses for large datasets
- Add request rate limiting to respect Ghost API limits

## Questions for Clarification

Before proceeding with implementation, please clarify the following:

### 1. API Scope
- **Question**: Should this MCP server be read-only (Content API) or also include write operations (Admin API)?
- **Impact**: Admin API would require different authentication and additional tools for creating/updating content
- **Recommendation**: Start with read-only Content API for initial implementation

### 2. Authentication Strategy
- **Question**: Do you want to support both Content API keys and Admin API keys?
- **Impact**: Different authentication methods have different capabilities and security considerations
- **Recommendation**: Begin with Content API keys only

### 3. Filtering and Pagination
- **Question**: Should all Ghost API filtering/pagination options be exposed as tool parameters?
- **Impact**: More parameters provide flexibility but increase complexity
- **Options**:
  - Full parameter exposure (complete flexibility)
  - Simplified parameter set (easier to use)
  - Progressive enhancement (start simple, add more later)

### 4. Error Handling Strategy
- **Question**: Any specific error handling or retry logic requirements?
- **Impact**: Affects reliability and user experience
- **Considerations**: Network timeouts, rate limits, API downtime

### 5. Configuration Management
- **Question**: How should the Ghost instance URL and API keys be configured?
- **Options**:
  - Environment variables only
  - Configuration file only
  - Both (with precedence order)
  - Runtime configuration via MCP parameters

### 6. Additional Features
- **Question**: Are there any additional features beyond basic CRUD operations?
- **Examples**:
  - Content search across posts/pages
  - Bulk operations
  - Content analytics/statistics
  - Webhook support for real-time updates

### 7. Development Environment
- **Question**: Should the development setup include sample Ghost content for testing?
- **Impact**: Makes testing and development easier but increases setup complexity

Please provide guidance on these questions to ensure the implementation meets your specific needs and use cases.
