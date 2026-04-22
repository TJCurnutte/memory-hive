# API Playbook V2
**Session:** api-expert  
**Date:** 2026-04-22  
**Capability Level:** 15+ skills

---

# SKILL 1: REST API Design
## Principles
- Resource nouns: `/users`, `/orders`, `/products`
- HTTP methods: GET (read), POST (create), PUT (replace), PATCH (update), DELETE (delete)
- Status codes: 200, 201, 204, 400, 401, 403, 404, 429, 500

## Best Practices
```
GET    /users          → list users
GET    /users/123      → get user
POST   /users          → create user
PUT    /users/123      → replace user
PATCH  /users/123      → update user
DELETE /users/123      → delete user
```

## Filtering & Search
- Field selection: `?fields=name,email`
- Search: `?q=keyword`
- Filters: `?status=active&role=admin`
- Sorting: `?sort=created_at&order=desc`

---

# SKILL 2: GraphQL API Design
## Core Concepts
- Single endpoint: `POST /graphql`
- Three operations: Queries, Mutations, Subscriptions
- Strongly typed schema with SDL
- Resolvers map fields to data

## Schema Example
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order!]!
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

## Pagination (Relay Connections)
```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}
```

---

# SKILL 3: Webhook Implementation
## Signature Verification
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret, timestamp) {
  // Replay protection
  const tolerance = 300; // 5 minutes
  if (Date.now() / 1000 - timestamp > tolerance) {
    throw new Error('Timestamp too old');
  }
  
  // HMAC verification
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(`${timestamp}.${payload}`)
    .digest('hex');
  
  // Timing-safe comparison
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${expectedSig}`)
  );
}
```

## Event Handling
1. Return 200 immediately
2. Process asynchronously
3. Store event ID for idempotency
4. Retry with exponential backoff (1s → 2s → 4s → ... → max 7 days)

---

# SKILL 4: OAuth 2.0 Implementation
## Flows
| Flow | Use Case |
|------|----------|
| Authorization Code + PKCE | Web apps, SPAs, mobile |
| Client Credentials | Server-to-server (M2M) |
| Device Code | CLI, smart TV apps |
| Refresh Token | Extend sessions |

## JWT Access Token Claims
```json
{
  "sub": "user_123",
  "aud": "api.example.com",
  "exp": 1713840000,
  "iat": 1713836400,
  "scope": "read:users write:orders"
}
```

---

# SKILL 5: Error Handling
## RFC 7807 Problem Details
```json
{
  "type": "https://api.example.com/errors/VALIDATION_ERROR",
  "title": "Validation Error",
  "status": 400,
  "detail": "The email field must be a valid email address.",
  "instance": "/users/POST",
  "extensions": {
    "code": "INVALID_EMAIL",
    "field": "email"
  }
}
```

## Standard Error Codes
- `VALIDATION_ERROR` - Invalid input
- `NOT_FOUND` - Resource doesn't exist
- `UNAUTHORIZED` - Missing/invalid auth
- `FORBIDDEN` - Insufficient permissions
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

# SKILL 6: API Versioning
## Strategies
| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL Path | `/v1/users` | Explicit, cacheable | URL changes |
| Header | `Accept: vnd.api.v2+json` | Clean URLs | Hidden, tool support varies |
| Query | `?version=2` | Easy | Pollutes URLs |

## Deprecation
```http
HTTP/1.1 299 Deprecated
Sunset: Sat, 31 Dec 2026 23:59:59 GMT
Link: <https://api.example.com/v2>; rel="successor-version"
Deprecation: true
```

---

# SKILL 7: Rate Limiting
## Algorithms
1. **Token Bucket** - Allows bursts, common
2. **Leaky Bucket** - Smooths traffic
3. **Sliding Window** - Most accurate
4. **Fixed Window** - Simplest

## Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1713840060
```

## 429 Response
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

## Redis Sliding Window (Distributed)
```
ZADD ratelimit:{key} {timestamp} {request_id}
ZREMRANGEBYSCORE ratelimit:{key} 0 {timestamp - window}
ZCARD ratelimit:{key}  → count
```

---

# SKILL 8: Pagination Patterns
## Offset-Based (Simple)
```
GET /users?page=2&per_page=20
Response: { data: [...], meta: { page: 2, per_page: 20, total: 100 } }
```

## Cursor-Based (Stable)
```
GET /users?after=eyJpZCI6MTIzfQ==
Response: { data: [...], meta: { next_cursor: "eyJpZCI6MTQ3fQ==" } }
```

## Keyset Pagination (High Performance)
```
GET /users?after_id=123&sort=created_at
```

---

# SKILL 9: API Caching
## Cache-Control Headers
```http
Cache-Control: private, max-age=3600
Cache-Control: public, s-maxage=86400, stale-while-revalidate=60
```

## ETag / Conditional Requests
```http
ETag: "33a64df551425fcc55e4d42a148795d9"
If-None-Match: "33a64df551425fcc55e4d42a148795d9"
→ 304 Not Modified (if match)
```

## Application Caching Pattern
```javascript
const cacheKey = `user:${id}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

const user = await db.users.find(id);
await redis.setex(cacheKey, 300, JSON.stringify(user)); // 5 min TTL
return user;
```

---

# SKILL 10: API Documentation
## OpenAPI 3.0 Structure
```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

## Documentation Tools
- **Scalar** - Beautiful, modern
- **Redocly** - Professional reference
- **Swagger UI** - Interactive testing
- **Stoplight** - Design + docs

---

# SKILL 11: API Security
## Essentials Checklist
- [ ] TLS 1.2+ (prefer TLS 1.3)
- [ ] OAuth 2.0 + PKCE for public clients
- [ ] API key encryption at rest
- [ ] Input validation (Zod, Yup, Pydantic)
- [ ] Parameterized queries (no SQL injection)
- [ ] CORS policy for browser clients
- [ ] Request size limits
- [ ] Sensitive data sanitization in logs

---

# SKILL 12: API Testing
## Test Categories
1. **Contract Tests** - Pact, Dredd (OpenAPI validation)
2. **Property-Based** - Schemathesis (fuzz from spec)
3. **Load Tests** - k6, Artillery
4. **Integration** - Supertest, Playwright API
5. **Mocking** - MSW (Mock Service Worker)

## k6 Load Test Example
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,
  duration: '30s',
};

export default function() {
  const res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'has users': (r) => JSON.parse(r.body).data.length > 0,
  });
  sleep(0.1);
}
```

---

# SKILL 13: API Monitoring & Observability
## Health Endpoints
```javascript
// /health - basic liveness
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// /ready - readiness (all dependencies up)
app.get('/ready', async (req, res) => {
  const db = await checkDatabase();
  const redis = await checkRedis();
  res.json({ 
    status: db && redis ? 'ready' : 'not_ready',
    checks: { db, redis }
  });
});
```

## Metrics to Track
- Request rate (requests/second)
- Latency percentiles (p50, p95, p99)
- Error rate (4xx, 5xx)
- Saturation (CPU, memory, connections)

## Structured Logging
```json
{
  "timestamp": "2026-04-22T18:24:00Z",
  "level": "info",
  "request_id": "req_abc123",
  "method": "GET",
  "path": "/users/123",
  "status": 200,
  "duration_ms": 45,
  "user_id": "user_456"
}
```

---

# SKILL 14: GraphQL Schema Design
## Best Practices
- Use Input types for mutations
- Enums for finite sets
- Interfaces for polymorphism
- Custom scalars for domain types
- Deprecate with reason
- Add descriptions for docs

```graphql
scalar Email
scalar DateTime

enum UserRole {
  ADMIN
  USER
  GUEST
}

interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  email: Email!
  role: UserRole!
  createdAt: DateTime!
  
  """@deprecated Use orders connection instead"""
  recentOrders: [Order!]!
}
```

---

# SKILL 15: Event-Driven APIs
## Webhooks vs WebSockets vs SSE
| Pattern | Direction | Use Case |
|---------|-----------|----------|
| Webhooks | Server → Client | Async notifications |
| WebSockets | Bidirectional | Real-time chat, games |
| SSE | Server → Client | Feeds, live updates |

## CloudEvents Spec
```json
{
  "specversion": "1.0",
  "type": "com.example.user.created",
  "source": "https://api.example.com",
  "id": "evt_abc123",
  "time": "2026-04-22T18:24:00Z",
  "data": { ... }
}
```

## Idempotent Event Processing
```javascript
async function processEvent(event) {
  const processed = await redis.get(`processed:${event.id}`);
  if (processed) return; // Already handled
  
  // Process the event
  await handleEvent(event);
  
  // Mark as processed (with TTL for cleanup)
  await redis.setex(`processed:${event.id}`, 86400, '1');
}
```

---

# QUICK REFERENCE

## Status Codes
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Error |

## Response Envelope
```json
{
  "data": { ... },
  "meta": { ... },
  "error": { ... }
}
```

---

*Generated: 2026-04-22 | Session: api-expert*
