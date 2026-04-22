# API Best Practices

> Compiled by API-Expert agent — 2026-04-22

---

## 1. REST API Design Best Practices

### Resource Naming Conventions
- Use **plural nouns** for collections: `/users`, `/orders`, `/products`
- Use **kebab-case** or **snake_case** consistently (pick one, document it)
- Nest resources for ownership: `/users/{id}/orders`
- Avoid verbs in URLs — let HTTP methods convey action

### HTTP Method Semantics

| Method | Semantics | Idempotent | Safe |
|--------|-----------|-----------|------|
| GET | Read resource(s) | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource (full update) | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |

### Request/Response Body Design
```json
// Good: singular resource in response
{
  "data": {
    "id": "usr_abc123",
    "type": "user",
    "attributes": {
      "name": "Travis Curnutte",
      "email": "travis@example.com",
      "createdAt": "2026-01-15T10:30:00Z"
    }
  },
  "meta": {
    "requestId": "req_xyz789"
  }
}

// Error response (RFC 7807)
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/users",
  "errors": [
    { "field": "email", "code": "INVALID_FORMAT", "message": "Must match RFC 5322" }
  ]
}
```

### URL Structure
```
GET    /v1/users              → list users
POST   /v1/users              → create user
GET    /v1/users/{id}         → get user
PUT    /v1/users/{id}         → replace user
PATCH  /v1/users/{id}         → update user
DELETE /v1/users/{id}         → delete user
GET    /v1/users/{id}/orders   → user's orders
```

---

## 2. GraphQL Best Practices

### Schema Design Principles
- Use **PascalCase** for types and fields, **camelCase** for query/mutation names
- Use interfaces for shared behavior; unions for polymorphic types
- Keep mutations focused — one mutation per logical operation
- Use input types for mutation variables

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order!]!
}

type Order {
  id: ID!
  status: OrderStatus!
  totalAmount: Float!
  user: User!
}

enum OrderStatus {
  PENDING
  CONFIRMED
  SHIPPED
  DELIVERED
  CANCELLED
}

input CreateUserInput {
  name: String!
  email: String!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

union SearchResult = User | Order | Product
```

### Query Complexity Limits
- Set depth limits (max nesting level)
- Set complexity scores per field
- Reject queries exceeding thresholds

```graphql
# Example: complexity annotation
# @cost(complexity: 2, multipliers: ["orders"])
```

### N+1 Problem Solutions
- **DataLoader pattern**: batch and cache requests per request cycle
- Implement at the resolver layer, not at the schema level
- Consider persisted queries for production to avoid dynamic introspection

### Subscriptions
- Use for real-time updates (WebSocket transport)
- Define subscription types separately from queries/mutations
- Implement connection keep-alive and reconnection logic

---

## 3. API Versioning Strategies

### URL Path Versioning (Most Common)
```
/v1/users
/v2/users
```
- Pros: Easy to route, visible in logs, explicit
- Cons: URL pollution, full duplication for minor changes

### Header Versioning
```
GET /users
API-Version: 2024-01-01
```
- Pros: Cleaner URLs, temporal versioning
- Cons: Less visible, routing complexity

### Query Parameter Versioning
```
GET /users?version=2
```
- Pros: Simple for opt-in upgrades
- Cons: Easy to forget, caching complications

### Deprecation Strategy
1. Announce deprecation in response headers: `Deprecation: true`, `Sunset: Sat, 01 Jan 2027 00:00:00 GMT`
2. Include `Link: <url>; rel="deprecation"` header
3. Notify via email/API changelog
4. Maintain old version for minimum 12 months post-announcement
5. Provide migration tooling when possible

---

## 4. Error Handling Patterns

### RFC 7807 Problem Details
```json
{
  "type": "https://api.example.com/errors/validation-failed",
  "title": "Validation Failed",
  "status": 400,
  "detail": "Request body contains invalid fields.",
  "instance": "/users",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

### HTTP Status Code Selection Guide

| Code | Use Case |
|------|----------|
| 200 | Successful GET/PATCH/DELETE |
| 201 | Resource created (POST) |
| 202 | Accepted for async processing |
| 204 | Successful, no content (DELETE, etc.) |
| 400 | Malformed request / validation error |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state mismatch) |
| 422 | Semantically invalid input |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 502 | Bad gateway (upstream failure) |
| 503 | Service unavailable |

### Error Code Taxonomy
```json
{
  "errors": [
    { "code": "RESOURCE_NOT_FOUND", "field": null, "message": "User with id '123' not found" },
    { "code": "VALIDATION_ERROR", "field": "email", "message": "Invalid email format" },
    { "code": "RATE_LIMIT_EXCEEDED", "field": null, "message": "Too many requests, retry in 60s" }
  ]
}
```

### Graceful Degradation
- Return partial data with `meta.partial = true` when full data unavailable
- Use feature flags to control error surface
- Log errors server-side; return sanitized messages to clients

---

## 5. Rate Limiting Strategies

### Standard Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1745356800
Retry-After: 60
```

### Algorithms

**Token Bucket**
- Tokens added at fixed rate (e.g., 100/minute)
- Each request consumes a token
- Allows bursts up to bucket capacity
- Simple implementation, good for API gateways

**Sliding Window Log**
- Track timestamp of each request
- Count requests in last N seconds
- More accurate but higher memory cost

**Sliding Window Counter**
- Two fixed windows, interpolate
- Memory-efficient approximation
- Good balance of accuracy and cost

### Limit Tiers
```http
X-RateLimit-Limit: 100         # per minute
X-RateLimit-Limit: 1000        # per hour  
X-RateLimit-Limit: 10000       # per day
```

### Client-Side 429 Handling
```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const res = await fetch(url, options);
    if (res.status !== 429) return res;
    
    const retryAfter = parseInt(res.headers.get('Retry-After') || '60');
    await new Promise(r => setTimeout(r, retryAfter * 1000));
  }
  throw new Error('Rate limit exceeded after retries');
}
```

---

## Quick Reference Card

| Concern | Recommendation |
|---------|---------------|
| Naming | Plural nouns, kebab-case or snake_case |
| Errors | RFC 7807 Problem Details |
| Versioning | URL path (`/v1/`) |
| Auth | Bearer token / OAuth 2.0 |
| Pagination | Cursor-based for large sets |
| Rate Limits | Return headers, 429 + Retry-After |
| Caching | ETag / Cache-Control |
| Body format | JSON, snake_case keys |
| Dates | ISO 8601 UTC |
