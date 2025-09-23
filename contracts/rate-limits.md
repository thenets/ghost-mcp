# Ghost API Rate Limiting Documentation

## Overview
Documentation of Ghost API rate limiting behavior and best practices for the MCP server implementation.

## Current Knowledge
Based on initial research, Ghost APIs do not have strict documented rate limits, but reasonable usage is expected.

## Content API Rate Limiting

### Observed Behavior
- No strict rate limits documented
- Designed for public consumption
- Responses are fully cacheable
- No rate limit headers observed in initial testing

### Best Practices
- Implement caching for repeated requests
- Use appropriate cache headers
- Avoid excessive concurrent requests
- Monitor response times

## Admin API Rate Limiting

### Observed Behavior
- No strict rate limits documented
- Server-side usage expected
- JWT tokens expire after 5 minutes (natural rate limiting)

### Best Practices
- Reuse JWT tokens within validity period
- Avoid generating new tokens for each request
- Implement request queuing for bulk operations
- Monitor API response times and errors

## Implementation Recommendations

### Caching Strategy
```javascript
// TODO: Phase 1 - Implement request caching
class GhostApiCache {
  constructor(ttl = 300000) { // 5 minutes default
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (item && Date.now() < item.expiry) {
      return item.data;
    }
    this.cache.delete(key);
    return null;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }
}
```

### Rate Limiting Detection
- Monitor for 429 status codes
- Watch for response time degradation
- Implement backoff on authentication errors

### Connection Pooling
- Use HTTP connection pooling
- Limit concurrent requests
- Queue requests during high load

## Research Status
- ⏳ Rate limit testing pending API keys
- ⏳ Load testing pending implementation
- ⏳ Cache strategy pending Phase 1
- ⏳ Performance monitoring pending implementation

## Future Research Areas
1. Test actual rate limits with API keys
2. Measure response times under load
3. Test cache effectiveness
4. Monitor for any undocumented limits