# Ghost API Error Responses Documentation

## Observed Error Response Format

### Standard Error Structure
```json
{
    "errors": [
        {
            "message": "Error description",
            "context": "Additional context or details",
            "type": "ErrorType",
            "details": "Additional details if available",
            "property": "field_name",
            "help": "Help text",
            "code": "ERROR_CODE",
            "id": "error_id"
        }
    ]
}
```

## Documented Error Types

### 1. Authentication Errors

#### Content API - Missing API Key
**Request**: `GET /ghost/api/content/settings/`
**Response**:
```json
{
    "errors": [
        {
            "message": "Authorization failed",
            "context": "Unable to determine the authenticated member or integration. Check the supplied Content API Key and ensure cookies are being passed through if making a request from the browser.",
            "type": "UnauthorizedError",
            "details": null,
            "property": null,
            "help": null,
            "code": null,
            "id": "error_id"
        }
    ]
}
```
**Status Code**: 401

#### Admin API - Missing Authentication
**Request**: `GET /ghost/api/admin/users/me/`
**Response**:
```json
{
    "errors": [
        {
            "message": "Authorization failed",
            "context": "Unable to determine the authenticated user or integration. Check that cookies are being passed through if making a request from the browser. For more information see https://ghost.org/docs/admin-api/#authentication.",
            "type": "UnauthorizedError"
        }
    ]
}
```
**Status Code**: 401

### 2. Resource Not Found Errors
**Status Code**: 404
**Format**: TBD (pending testing with valid API keys)

### 3. Validation Errors
**Status Code**: 422
**Format**: TBD (pending testing with create/update operations)

### 4. Rate Limiting Errors
**Status Code**: 429
**Format**: TBD (pending rate limit testing)

### 5. Server Errors
**Status Code**: 5xx
**Format**: TBD (pending error scenario testing)

## Error Categories for MCP Implementation

### Network Errors
- Connection timeouts
- DNS resolution failures
- Network connectivity issues
- SSL/TLS certificate problems

### Authentication Errors
- Invalid API keys (Content/Admin)
- JWT token generation failures
- Token expiration
- Permission denied errors

### Ghost API Errors
- Rate limiting (429 status)
- Server errors (5xx status)
- Client errors (4xx status)
- Invalid request format
- Resource not found (404)
- Validation errors (422)

### MCP Protocol Errors
- Invalid tool parameters
- Schema validation failures
- Unsupported operations

### File Upload Errors
- File size limits exceeded
- Unsupported file types
- Storage failures

## Research Status
- ✅ Basic error structure identified
- ✅ Authentication error formats documented
- ⏳ Complete error catalog pending API key testing
- ⏳ Rate limiting behavior pending
- ⏳ Validation error formats pending
- ⏳ Error mapping to MCP responses pending