# Ghost API Endpoints Documentation

## Content API Endpoints (Read-Only)

### Base URL Structure
- **Base URL**: `http://localhost:2368/ghost/api/content/`
- **Authentication**: Content API key as query parameter
- **Version**: v5.0 (current)

### Documented Endpoints

#### Posts
- `GET /posts/` - List all published posts
- `GET /posts/{id}/` - Get specific post by ID
- `GET /posts/slug/{slug}/` - Get specific post by slug

#### Pages
- `GET /pages/` - List all published pages
- `GET /pages/{id}/` - Get specific page by ID
- `GET /pages/slug/{slug}/` - Get specific page by slug

#### Tags
- `GET /tags/` - List all tags
- `GET /tags/{id}/` - Get specific tag by ID
- `GET /tags/slug/{slug}/` - Get specific tag by slug

#### Authors
- `GET /authors/` - List all authors
- `GET /authors/{id}/` - Get specific author by ID
- `GET /authors/slug/{slug}/` - Get specific author by slug

#### Other
- `GET /tiers/` - List membership tiers
- `GET /settings/` - Get public settings

## Admin API Endpoints (Read/Write)

### Base URL Structure
- **Base URL**: `http://localhost:2368/ghost/api/admin/`
- **Authentication**: JWT token in Authorization header
- **Version**: v5.0 (current)

### Documented Endpoints

#### Site Information
- `GET /site/` - Get site information (tested - requires auth)

#### Users
- `GET /users/me/` - Get current user (tested - requires auth)

#### Posts (Admin)
- `GET /posts/` - Browse all posts (including drafts)
- `GET /posts/{id}/` - Read specific post
- `POST /posts/` - Create new post
- `PUT /posts/{id}/` - Update existing post
- `POST /posts/{id}/copy/` - Copy post
- `DELETE /posts/{id}/` - Delete post

#### Pages (Admin)
- `GET /pages/` - Browse all pages
- `GET /pages/{id}/` - Read specific page
- `POST /pages/` - Create new page
- `PUT /pages/{id}/` - Update existing page
- `POST /pages/{id}/copy/` - Copy page
- `DELETE /pages/{id}/` - Delete page

#### Tags (Admin)
- `GET /tags/` - Browse all tags
- `GET /tags/{id}/` - Read specific tag
- `POST /tags/` - Create new tag
- `PUT /tags/{id}/` - Update existing tag
- `DELETE /tags/{id}/` - Delete tag

#### Members (Admin)
- `GET /members/` - Browse members
- `GET /members/{id}/` - Read specific member
- `POST /members/` - Create new member
- `PUT /members/{id}/` - Update existing member

#### Media (Admin)
- `POST /images/upload/` - Upload images
- `POST /media/upload/` - Upload media files

#### Integrations (Admin)
- `GET /integrations/` - List integrations
- `POST /integrations/` - Create integration (for API keys)

## Research Status
- ✅ Base URL structure identified
- ✅ Authentication requirements confirmed
- ⏳ Individual endpoint testing pending API keys
- ⏳ Parameter documentation pending
- ⏳ Response format documentation pending