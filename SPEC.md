# Ghost MCP

This is the spec for the Ghost Blog platform MCP server.

## Goal

- The main goal is to implement the MCP tools for all Ghost REST API actions (both Content and Admin APIs)
- Provide a comprehensive MCP server that allows Claude to interact with Ghost blog content for both reading and writing
- Support all major Ghost Content API endpoints for reading published content
- Support all major Ghost Admin API endpoints for creating, updating, and deleting content

## Requirements

### Infrastructure
- Deploy a local Ghost instance using `docker compose` and figure out a way to create API keys
- Set up proper authentication using both Ghost Content API keys (read-only) and Admin API keys (read/write)
- Configure the MCP server to connect to the Ghost instance with appropriate permissions

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

## Ghost Admin API Endpoints

The Ghost Admin API provides full read/write access to all Ghost content. All endpoints require Admin API authentication.

### Posts (Admin)
- `GET /admin/posts/` - Browse posts (including drafts)
- `GET /admin/posts/{id}/` - Read a specific post
- `POST /admin/posts/` - Create a new post
- `PUT /admin/posts/{id}/` - Update an existing post
- `POST /admin/posts/{id}/copy/` - Copy a post
- `DELETE /admin/posts/{id}/` - Delete a post

### Pages (Admin)
- `GET /admin/pages/` - Browse pages (including drafts)
- `GET /admin/pages/{id}/` - Read a specific page
- `POST /admin/pages/` - Create a new page
- `PUT /admin/pages/{id}/` - Update an existing page
- `POST /admin/pages/{id}/copy/` - Copy a page
- `DELETE /admin/pages/{id}/` - Delete a page

### Tags (Admin)
- `GET /admin/tags/` - Browse all tags
- `GET /admin/tags/{id}/` - Read a specific tag
- `POST /admin/tags/` - Create a new tag
- `PUT /admin/tags/{id}/` - Update an existing tag
- `DELETE /admin/tags/{id}/` - Delete a tag

### Tiers (Admin)
- `GET /admin/tiers/` - Browse membership tiers
- `GET /admin/tiers/{id}/` - Read a specific tier
- `POST /admin/tiers/` - Create a new tier
- `PUT /admin/tiers/{id}/` - Update an existing tier

### Members (Admin)
- `GET /admin/members/` - Browse members
- `GET /admin/members/{id}/` - Read a specific member
- `POST /admin/members/` - Create a new member
- `PUT /admin/members/{id}/` - Update an existing member

### Users (Admin)
- `GET /admin/users/` - Browse users
- `GET /admin/users/{id}/` - Read a specific user

### Media (Admin)
- `POST /admin/images/upload/` - Upload images
- `POST /admin/media/upload/` - Upload media files

### Themes (Admin)
- `POST /admin/themes/upload/` - Upload theme
- `PUT /admin/themes/{name}/activate/` - Activate theme

### Webhooks (Admin)
- `GET /admin/webhooks/` - Browse webhooks
- `POST /admin/webhooks/` - Create webhook
- `PUT /admin/webhooks/{id}/` - Update webhook
- `DELETE /admin/webhooks/{id}/` - Delete webhook

### Newsletters (Admin)
- `GET /admin/newsletters/` - Browse newsletters
- `GET /admin/newsletters/{id}/` - Read newsletter
- `POST /admin/newsletters/` - Create newsletter
- `PUT /admin/newsletters/{id}/` - Update newsletter

### Offers (Admin)
- `GET /admin/offers/` - Browse offers
- `GET /admin/offers/{id}/` - Read offer
- `POST /admin/offers/` - Create offer
- `PUT /admin/offers/{id}/` - Update offer

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

## Admin API MCP Tools

The following MCP tools provide full read/write access to Ghost content via the Admin API:

### Posts Admin Tools
- **`ghost_admin_list_posts`** - Browse all posts (including drafts)
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of post objects with pagination metadata

- **`ghost_admin_get_post`** - Read a specific post by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single post object

- **`ghost_admin_create_post`** - Create a new post
  - Parameters: `title` (required string), `html?` (string), `mobiledoc?` (string), `lexical?` (string), `status?` (string), `slug?` (string), `excerpt?` (string), `meta_title?` (string), `meta_description?` (string), `tags?` (array), `authors?` (array), `featured?` (boolean), `published_at?` (string)
  - Returns: Created post object

- **`ghost_admin_update_post`** - Update an existing post
  - Parameters: `id` (required string), `title?` (string), `html?` (string), `mobiledoc?` (string), `lexical?` (string), `status?` (string), `slug?` (string), `excerpt?` (string), `meta_title?` (string), `meta_description?` (string), `tags?` (array), `authors?` (array), `featured?` (boolean), `published_at?` (string), `updated_at` (required string)
  - Returns: Updated post object

- **`ghost_admin_copy_post`** - Copy an existing post
  - Parameters: `id` (required string)
  - Returns: Copied post object

- **`ghost_admin_delete_post`** - Delete a post
  - Parameters: `id` (required string)
  - Returns: Success confirmation

### Pages Admin Tools
- **`ghost_admin_list_pages`** - Browse all pages (including drafts)
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of page objects with pagination metadata

- **`ghost_admin_get_page`** - Read a specific page by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single page object

- **`ghost_admin_create_page`** - Create a new page
  - Parameters: `title` (required string), `html?` (string), `mobiledoc?` (string), `lexical?` (string), `status?` (string), `slug?` (string), `excerpt?` (string), `meta_title?` (string), `meta_description?` (string), `tags?` (array), `authors?` (array), `featured?` (boolean), `published_at?` (string)
  - Returns: Created page object

- **`ghost_admin_update_page`** - Update an existing page
  - Parameters: `id` (required string), `title?` (string), `html?` (string), `mobiledoc?` (string), `lexical?` (string), `status?` (string), `slug?` (string), `excerpt?` (string), `meta_title?` (string), `meta_description?` (string), `tags?` (array), `authors?` (array), `featured?` (boolean), `published_at?` (string), `updated_at` (required string)
  - Returns: Updated page object

- **`ghost_admin_copy_page`** - Copy an existing page
  - Parameters: `id` (required string)
  - Returns: Copied page object

- **`ghost_admin_delete_page`** - Delete a page
  - Parameters: `id` (required string)
  - Returns: Success confirmation

### Tags Admin Tools
- **`ghost_admin_list_tags`** - Browse all tags
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of tag objects with pagination metadata

- **`ghost_admin_get_tag`** - Read a specific tag by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single tag object

- **`ghost_admin_create_tag`** - Create a new tag
  - Parameters: `name` (required string), `slug?` (string), `description?` (string), `feature_image?` (string), `meta_title?` (string), `meta_description?` (string), `visibility?` (string)
  - Returns: Created tag object

- **`ghost_admin_update_tag`** - Update an existing tag
  - Parameters: `id` (required string), `name?` (string), `slug?` (string), `description?` (string), `feature_image?` (string), `meta_title?` (string), `meta_description?` (string), `visibility?` (string), `updated_at` (required string)
  - Returns: Updated tag object

- **`ghost_admin_delete_tag`** - Delete a tag
  - Parameters: `id` (required string)
  - Returns: Success confirmation

### Members Admin Tools
- **`ghost_admin_list_members`** - Browse all members
  - Parameters: `limit?` (number), `page?` (number), `filter?` (string), `include?` (string), `fields?` (string)
  - Returns: Array of member objects with pagination metadata

- **`ghost_admin_get_member`** - Read a specific member by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single member object

- **`ghost_admin_create_member`** - Create a new member
  - Parameters: `email` (required string), `name?` (string), `note?` (string), `subscribed?` (boolean), `comped?` (boolean), `labels?` (array), `newsletters?` (array)
  - Returns: Created member object

- **`ghost_admin_update_member`** - Update an existing member
  - Parameters: `id` (required string), `email?` (string), `name?` (string), `note?` (string), `subscribed?` (boolean), `comped?` (boolean), `labels?` (array), `newsletters?` (array), `updated_at` (required string)
  - Returns: Updated member object

### Media Admin Tools
- **`ghost_admin_upload_image`** - Upload an image
  - Parameters: `file` (required file/base64), `purpose?` (string), `ref?` (string)
  - Returns: Uploaded image URL and metadata

- **`ghost_admin_upload_media`** - Upload media file
  - Parameters: `file` (required file/base64), `purpose?` (string), `ref?` (string)
  - Returns: Uploaded media URL and metadata

### Tiers Admin Tools
- **`ghost_admin_list_tiers`** - Browse membership tiers
  - Parameters: `limit?` (number), `page?` (number), `include?` (string), `fields?` (string)
  - Returns: Array of tier objects

- **`ghost_admin_get_tier`** - Read a specific tier by ID
  - Parameters: `id` (required string), `include?` (string), `fields?` (string)
  - Returns: Single tier object

- **`ghost_admin_create_tier`** - Create a new membership tier
  - Parameters: `name` (required string), `description?` (string), `monthly_price?` (number), `yearly_price?` (number), `currency?` (string), `trial_days?` (number), `visibility?` (string), `welcome_page_url?` (string), `benefits?` (array)
  - Returns: Created tier object

- **`ghost_admin_update_tier`** - Update an existing tier
  - Parameters: `id` (required string), `name?` (string), `description?` (string), `monthly_price?` (number), `yearly_price?` (number), `currency?` (string), `trial_days?` (number), `visibility?` (string), `welcome_page_url?` (string), `benefits?` (array), `updated_at` (required string)
  - Returns: Updated tier object

### Webhooks Admin Tools
- **`ghost_admin_list_webhooks`** - Browse webhooks
  - Parameters: `limit?` (number), `page?` (number)
  - Returns: Array of webhook objects

- **`ghost_admin_create_webhook`** - Create a new webhook
  - Parameters: `event` (required string), `target_url` (required string), `name?` (string), `secret?` (string), `api_version?` (string), `integration_id?` (string)
  - Returns: Created webhook object

- **`ghost_admin_update_webhook`** - Update an existing webhook
  - Parameters: `id` (required string), `event?` (string), `target_url?` (string), `name?` (string), `secret?` (string), `api_version?` (string), `updated_at` (required string)
  - Returns: Updated webhook object

- **`ghost_admin_delete_webhook`** - Delete a webhook
  - Parameters: `id` (required string)
  - Returns: Success confirmation

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
4. Create a new custom integration which provides:
   - **Content API Key**: For read-only access to published content
   - **Admin API Key**: For full read/write access to all Ghost content
5. Save both API keys for MCP server configuration

### Authentication Types

#### Content API Authentication
- **Purpose**: Read-only access to published content
- **Security**: Safe for browser/public environments
- **Authentication**: Content API key passed as query parameter
- **Scope**: Posts, pages, tags, authors, tiers, settings (published content only)

#### Admin API Authentication
- **Purpose**: Full read/write access to all Ghost content
- **Security**: Must remain secret, server-side only
- **Authentication**: Admin API key with JWT token generation
- **Scope**: All Ghost resources including drafts, members, webhooks, media uploads

## Configuration

The MCP server should support configuration via:

### Environment Variables
- `GHOST_URL`: Ghost instance URL (default: http://localhost:2368)
- `GHOST_CONTENT_API_KEY`: Content API key (required for read operations)
- `GHOST_ADMIN_API_KEY`: Admin API key (required for write operations)
- `GHOST_VERSION`: API version (default: v5.0)
- `MCP_GHOST_MODE`: Operation mode - "readonly", "readwrite", or "auto" (default: "auto")

### Configuration File
Alternative JSON configuration file:
```json
{
  "ghost": {
    "url": "http://localhost:2368",
    "contentApiKey": "your-content-api-key",
    "adminApiKey": "your-admin-api-key",
    "version": "v5.0",
    "mode": "readwrite"
  }
}
```

### Operation Modes
- **readonly**: Only Content API tools are available (requires Content API key)
- **readwrite**: All tools available (requires both Content and Admin API keys)
- **auto**: Automatically detects available keys and enables appropriate tools

## Implementation Details

### Project Structure
```
ghost-mcp/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── ghost-client.ts       # Ghost API client (both Content and Admin)
│   ├── auth/
│   │   ├── content-auth.ts   # Content API authentication
│   │   └── admin-auth.ts     # Admin API JWT authentication
│   ├── tools/
│   │   ├── content/          # Content API tools (read-only)
│   │   │   ├── posts.ts
│   │   │   ├── pages.ts
│   │   │   ├── tags.ts
│   │   │   ├── authors.ts
│   │   │   └── settings.ts
│   │   └── admin/           # Admin API tools (read/write)
│   │       ├── posts.ts
│   │       ├── pages.ts
│   │       ├── tags.ts
│   │       ├── members.ts
│   │       ├── media.ts
│   │       ├── tiers.ts
│   │       └── webhooks.ts
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
- **jsonwebtoken** for Admin API JWT authentication
- **zod** for runtime type validation
- **dotenv** for environment variable management
- **multer** or equivalent for file upload handling

### Error Handling
- Validate all input parameters using Zod schemas
- Handle Ghost API errors gracefully with meaningful messages
- Implement retry logic for transient network errors
- Return proper MCP error responses with error codes
- Handle authentication failures for both Content and Admin APIs
- Graceful degradation when only one API key is available

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

### 1. Filtering and Pagination
- **Question**: Should all Ghost API filtering/pagination options be exposed as tool parameters?
- **Impact**: More parameters provide flexibility but increase complexity
- **Options**:
  - Full parameter exposure (complete flexibility)
  - Simplified parameter set (easier to use)
  - Progressive enhancement (start simple, add more later)

### 2. Error Handling Strategy
- **Question**: Any specific error handling or retry logic requirements?
- **Impact**: Affects reliability and user experience
- **Considerations**: Network timeouts, rate limits, API downtime

### 3. Configuration Management
- **Question**: How should the Ghost instance URL and API keys be configured?
- **Options**:
  - Environment variables only
  - Configuration file only
  - Both (with precedence order)
  - Runtime configuration via MCP parameters

### 4. Additional Features
- **Question**: Are there any additional features beyond basic CRUD operations?
- **Examples**:
  - Content search across posts/pages
  - Bulk operations
  - Content analytics/statistics
  - Webhook support for real-time updates

### 5. Development Environment
- **Question**: Should the development setup include sample Ghost content for testing?
- **Impact**: Makes testing and development easier but increases setup complexity

Please provide guidance on these questions to ensure the implementation meets your specific needs and use cases.
