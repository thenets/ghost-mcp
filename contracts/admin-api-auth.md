# Ghost Admin API JWT Authentication Documentation

## Overview
Ghost Admin API uses JWT (JSON Web Token) authentication for secure, server-side access to read/write operations.

## Authentication Flow

### 1. API Key Structure
**Format**: `{id}:{secret}`
- **ID**: Used as the `kid` (key identifier) in JWT header
- **Secret**: Used to sign the JWT token
- **Source**: Generated from Ghost Admin → Settings → Integrations → Custom Integration

**Example**: `507f1f77bcf86cd799439011:1234567890abcdef1234567890abcdef12345678`

### 2. JWT Token Generation

#### Required Headers
```json
{
  "alg": "HS256",
  "kid": "{api_key_id}",
  "typ": "JWT"
}
```

#### Required Payload
```json
{
  "exp": {timestamp_plus_5_minutes},
  "iat": {current_timestamp},
  "aud": "/admin/"
}
```

#### Constraints
- **Token Expiration**: Maximum 5 minutes from generation
- **Algorithm**: HS256 (HMAC SHA-256)
- **Audience**: Must be `/admin/`
- **Key ID**: Must match the API key ID

### 3. HTTP Request Format

#### Required Headers
```http
Authorization: Ghost {jwt_token}
Accept-Version: v5.0
Content-Type: application/json
```

#### Example Request
```http
GET /ghost/api/admin/posts/ HTTP/1.1
Host: localhost:2368
Authorization: Ghost eyJhbGciOiJIUzI1NiIsImtpZCI6IjUwN2YxZjc3YmNmODZjZDc5OTQzOTAxMSIsInR5cCI6IkpXVCJ9...
Accept-Version: v5.0
```

## Implementation Requirements

### Node.js Implementation (for MCP Server)

#### Dependencies
```json
{
  "jsonwebtoken": "^9.0.0"
}
```

#### Token Generation Function
```javascript
const jwt = require('jsonwebtoken');

function generateAdminApiToken(apiKey) {
  // Split the key into ID and secret
  const [id, secret] = apiKey.split(':');

  // Prepare header
  const header = {
    alg: 'HS256',
    kid: id,
    typ: 'JWT'
  };

  // Prepare payload
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    exp: now + (5 * 60), // 5 minutes from now
    iat: now,
    aud: '/admin/'
  };

  // Generate token
  const token = jwt.sign(payload, Buffer.from(secret, 'hex'), { header });
  return token;
}
```

#### Usage Example
```javascript
const adminApiKey = 'your_admin_api_key_here';
const token = generateAdminApiToken(adminApiKey);

const response = await fetch('http://localhost:2368/ghost/api/admin/posts/', {
  headers: {
    'Authorization': `Ghost ${token}`,
    'Accept-Version': 'v5.0',
    'Content-Type': 'application/json'
  }
});
```

### Token Refresh Strategy
Since tokens expire after 5 minutes:
1. **Generate new token for each request** (simplest)
2. **Cache token with expiration tracking** (more efficient)
3. **Regenerate on 401 response** (error-driven)

### Recommended Approach for MCP Server
```javascript
class GhostAdminAuth {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.token = null;
    this.tokenExpiry = null;
  }

  generateToken() {
    const [id, secret] = this.apiKey.split(':');
    const now = Math.floor(Date.now() / 1000);

    const payload = {
      exp: now + (4 * 60), // 4 minutes (buffer)
      iat: now,
      aud: '/admin/'
    };

    this.token = jwt.sign(payload, Buffer.from(secret, 'hex'), {
      header: { alg: 'HS256', kid: id, typ: 'JWT' }
    });
    this.tokenExpiry = now + (4 * 60);

    return this.token;
  }

  getValidToken() {
    const now = Math.floor(Date.now() / 1000);
    if (!this.token || now >= this.tokenExpiry) {
      return this.generateToken();
    }
    return this.token;
  }

  getAuthHeaders() {
    return {
      'Authorization': `Ghost ${this.getValidToken()}`,
      'Accept-Version': 'v5.0',
      'Content-Type': 'application/json'
    };
  }
}
```

## Error Handling

### Invalid Token
**Response**: 401 Unauthorized
```json
{
  "errors": [
    {
      "message": "Authorization failed",
      "context": "Unable to determine the authenticated user or integration...",
      "type": "UnauthorizedError"
    }
  ]
}
```

### Expired Token
**Response**: 401 Unauthorized
**Action**: Generate new token and retry

### Invalid API Key
**Response**: 401 Unauthorized
**Action**: Verify API key format and permissions

## Security Considerations

1. **Keep API Key Secret**: Never expose in client-side code
2. **Server-Side Only**: JWT generation must happen server-side
3. **Short Token Lifespan**: Maximum 5 minutes reduces exposure window
4. **HTTPS in Production**: Always use HTTPS for API requests
5. **Key Rotation**: Regularly rotate API keys in production

## Testing Strategy

### Manual Testing
1. Generate API key from Ghost Admin
2. Create JWT token using the implementation
3. Test various Admin API endpoints
4. Verify token expiration handling

### Automated Testing
1. Mock JWT generation for unit tests
2. Use test API keys for integration tests
3. Test token refresh logic
4. Test error handling scenarios

## Implementation Status
- ✅ Authentication flow documented
- ✅ JWT generation requirements identified
- ✅ Node.js implementation planned
- ⏳ Implementation pending API key generation
- ⏳ Testing pending API key availability