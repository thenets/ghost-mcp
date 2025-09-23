# Ghost Content API Authentication Documentation

## Overview
Ghost Content API provides read-only access to published content using simple query parameter authentication. It's designed for public consumption and is safe for client-side use.

## Authentication Method

### API Key Format
- **Type**: Content API Key (different from Admin API Key)
- **Source**: Ghost Admin → Settings → Integrations → Custom Integration
- **Security**: Safe for browser/public environments
- **Access**: Read-only to published content only

### Request Authentication

#### Query Parameter Method
```http
GET /ghost/api/content/posts/?key={content_api_key}
```

#### Required Headers
```http
Accept-Version: v5.0
```

#### Example Request
```http
GET /ghost/api/content/posts/?key=22444f78cc7a3e8d0b5eaa18&limit=5 HTTP/1.1
Host: localhost:2368
Accept-Version: v5.0
```

## Implementation for MCP Server

### Node.js Implementation

#### Simple Request Function
```javascript
class GhostContentAuth {
  constructor(apiKey, ghostUrl = 'http://localhost:2368') {
    this.apiKey = apiKey;
    this.baseUrl = `${ghostUrl}/ghost/api/content`;
  }

  buildUrl(endpoint, params = {}) {
    const url = new URL(`${this.baseUrl}${endpoint}`);

    // Add API key
    url.searchParams.set('key', this.apiKey);

    // Add additional parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, value);
      }
    });

    return url.toString();
  }

  getHeaders() {
    return {
      'Accept-Version': 'v5.0',
      'Accept': 'application/json'
    };
  }

  async request(endpoint, params = {}) {
    const url = this.buildUrl(endpoint, params);
    const response = await fetch(url, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error(`Content API request failed: ${response.status}`);
    }

    return response.json();
  }
}
```

#### Usage Examples
```javascript
const contentAuth = new GhostContentAuth('your_content_api_key');

// Get all posts
const posts = await contentAuth.request('/posts/', {
  limit: 10,
  include: 'tags,authors'
});

// Get specific post by slug
const post = await contentAuth.request('/posts/slug/welcome/', {
  include: 'tags,authors'
});

// Get site settings
const settings = await contentAuth.request('/settings/');
```

## Available Endpoints

### Core Resources
- `GET /posts/` - All published posts
- `GET /posts/{id}/` - Specific post by ID
- `GET /posts/slug/{slug}/` - Specific post by slug
- `GET /pages/` - All published pages
- `GET /pages/{id}/` - Specific page by ID
- `GET /pages/slug/{slug}/` - Specific page by slug
- `GET /tags/` - All public tags
- `GET /tags/{id}/` - Specific tag by ID
- `GET /tags/slug/{slug}/` - Specific tag by slug
- `GET /authors/` - All authors
- `GET /authors/{id}/` - Specific author by ID
- `GET /authors/slug/{slug}/` - Specific author by slug
- `GET /tiers/` - Membership tiers
- `GET /settings/` - Public site settings

## Query Parameters

### Common Parameters
- `key` (required): Content API key
- `limit`: Number of resources (default: 15, max: 50)
- `page`: Page number for pagination
- `fields`: Comma-separated list of fields to include
- `include`: Related resources to include (e.g., 'tags,authors')
- `filter`: Filter resources using Ghost's filter syntax

### Filter Examples
```javascript
// Featured posts only
const featured = await contentAuth.request('/posts/', {
  filter: 'featured:true'
});

// Posts with specific tag
const newsPosts = await contentAuth.request('/posts/', {
  filter: 'tag:news'
});

// Posts by specific author
const authorPosts = await contentAuth.request('/posts/', {
  filter: 'author:john-doe'
});
```

## Response Format

### Standard Response Structure
```json
{
  "posts": [
    {
      "id": "post_id",
      "title": "Post Title",
      "slug": "post-slug",
      "html": "<p>Post content...</p>",
      "feature_image": "image_url",
      "published_at": "2023-01-01T00:00:00.000Z",
      "created_at": "2023-01-01T00:00:00.000Z",
      "updated_at": "2023-01-01T00:00:00.000Z",
      "tags": [...],
      "authors": [...]
    }
  ],
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

## Error Handling

### Missing API Key
**Request**: Without `key` parameter
**Response**: 401 Unauthorized
```json
{
  "errors": [
    {
      "message": "Authorization failed",
      "context": "Unable to determine the authenticated member or integration. Check the supplied Content API Key...",
      "type": "UnauthorizedError"
    }
  ]
}
```

### Invalid API Key
**Response**: 401 Unauthorized
**Action**: Verify key is correct and active

### Resource Not Found
**Response**: 404 Not Found
```json
{
  "errors": [
    {
      "message": "Resource not found",
      "type": "NotFoundError"
    }
  ]
}
```

## Security Considerations

### Safe for Public Use
- Content API keys only access published content
- No sensitive data exposure
- Can be used in browsers, mobile apps, etc.

### Private Sites
- Be cautious with key distribution on private Ghost sites
- Consider access restrictions if content should be limited

### Key Management
- Keys can be regenerated in Ghost Admin
- Multiple integrations can have different keys
- Monitor key usage if needed

## Rate Limiting & Caching

### Caching Behavior
- Content API responses are fully cacheable
- Cache headers provided in responses
- Recommended to implement caching in client

### Rate Limiting
- No strict rate limits documented
- Reasonable usage expected
- Monitor response times and adjust accordingly

## Testing Strategy

### Manual Testing
```bash
# Test with curl
curl "http://localhost:2368/ghost/api/content/posts/?key=YOUR_KEY&limit=1" \
  -H "Accept-Version: v5.0"
```

### Automated Testing
```javascript
// Test basic authentication
test('Content API authentication', async () => {
  const response = await contentAuth.request('/settings/');
  expect(response.settings).toBeDefined();
});

// Test error handling
test('Invalid key handling', async () => {
  const invalidAuth = new GhostContentAuth('invalid_key');
  await expect(invalidAuth.request('/posts/')).rejects.toThrow();
});
```

## Implementation Status
- ✅ Authentication method documented
- ✅ Request format identified
- ✅ Error handling patterns documented
- ✅ Node.js implementation designed
- ⏳ Implementation pending API key generation
- ⏳ Testing pending API key availability