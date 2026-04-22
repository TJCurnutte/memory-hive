# Integration Patterns

> Compiled by API-Expert agent — 2026-04-22

---

## 1. Webhook Integration Patterns

### Webhook Security — HMAC Signatures
```
# Server generates:
signature = HMAC-SHA256(secret, request_body)
# Sends in header:
X-Signature-256: sha256=<hex_digest>

# Client verifies:
expected = HMAC-SHA256(webhook_secret, raw_body)
if (!secureCompare(expected, received_signature)) reject();
```

### Secret Token + Signature Pattern
```
# Simpler alternative — header-based:
X-Webhook-Secret: <pre-shared-secret>

# Best practice: use both
X-Webhook-Secret: <secret-id>
X-Signature-256: sha256=<hmac>
```

### Retry Strategies & Dead Letter Queues
- **Exponential backoff**: 1s → 2s → 4s → 8s → 16s → max 1 hour
- **Jitter**: add random `±50%` to prevent thundering herd
- **Max retries**: 5-7 attempts before moving to DLQ
- **DLQ processing**: manual review, replay tooling, alerting

```javascript
// Retry with exponential backoff + jitter
function retryWithBackoff(fn, maxAttempts = 5) {
  return async function(...args) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        return await fn(...args);
      } catch (err) {
        if (attempt === maxAttempts - 1) throw err;
        const baseDelay = Math.pow(2, attempt) * 1000;
        const jitter = baseDelay * (0.5 + Math.random());
        await sleep(jitter);
      }
    }
  };
}
```

### Idempotency Keys
```http
POST /payments
Idempotency-Key: <uuid>
Content-Type: application/json

{ "amount": 100, "currency": "USD", "recipient": "acc_123" }
```
- Store idempotency key + response in DB with TTL (24-48h)
- Return cached response on duplicate key
- Keys should be UUID v4 or similar high-entropy values

### Delivery Confirmation
- Return **200** quickly, process async
- Include delivery ID for tracing
- Webhook endpoint should be stateless
- Use a queue (SQS, Redis) between reception and processing

---

## 2. OAuth 2.0 Flows

### Authorization Code Flow (3-legged)
```
1. User clicks "Connect" → redirect to /oauth/authorize
2. User consents → redirect back with ?code=AUTH_CODE
3. Backend exchanges code for tokens:
   POST /oauth/token
   { grant_type: "authorization_code", code, redirect_uri, client_id, client_secret }
4. Receive: access_token, refresh_token, expires_in
```

### PKCE (Proof Key for Code Exchange)
```
# Used by SPAs and mobile apps (no client_secret)
1. Generate random `code_verifier` (43-128 chars)
2. Hash it → `code_challenge` (BASE64URL of SHA256)
3. Redirect to /oauth/authorize?code_challenge=<>&code_challenge_method=S256
4. Exchange code + `code_verifier` (server verifies hash matches)
```

### Client Credentials Flow (2-legged)
```
# Machine-to-machine, no user context
POST /oauth/token
{ grant_type: "client_credentials", client_id, client_secret }

# Response:
{ "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }
```

### Token Refresh Strategies
```javascript
// Proactive refresh — refresh when token is X minutes from expiry
if (token.expiresAt - Date.now() < 5 * 60 * 1000) {
  token = await refreshToken(token.refreshToken);
}

// Lazy refresh — refresh on 401
async function authenticatedFetch(url, options) {
  const res = await fetch(url, addAuth(options));
  if (res.status === 401) {
    await refreshTokens();
    return fetch(url, addAuth(options));
  }
  return res;
}
```

### Scope Design
- **Principle of least privilege**: request only scopes needed
- **Readable scope names**: `read:users`, `write:orders`, `read:billing`
- **Document scope requirements** per endpoint
- **Support incremental auth**: request scopes progressively

---

## 3. Pagination Strategies

### Offset-Based Pagination
```json
GET /v1/users?page=3&per_page=20

{
  "data": [...],
  "pagination": {
    "page": 3,
    "perPage": 20,
    "totalItems": 1000,
    "totalPages": 50
  }
}
```
- **Pros**: Simple, user can jump to any page
- **Cons**: Inconsistent results with inserts/deletes; slow on large offsets

### Cursor-Based Pagination (Keyset)
```json
GET /v1/users?after=cursor_xyz&limit=20

{
  "data": [...],
  "pagination": {
    "nextCursor": "cursor_abc",
    "hasMore": true
  }
}
```
- **Pros**: Consistent during inserts/deletes, fast on large datasets
- **Cons**: Cannot jump to arbitrary page, only forward/back
- **Use for**: feeds, timelines, large tables

```sql
-- Cursor = last item's sort column value
SELECT * FROM users 
WHERE created_at < :cursor 
ORDER BY created_at DESC 
LIMIT 20;
```

### Link Header Pagination (RFC 8288)
```http
HTTP/1.1 200 OK
Link: <https://api.example.com/users?page=2>; rel="next",
      <https://api.example.com/users?page=5>; rel="last",
      <https://api.example.com/users?page=1>; rel="first"

Pagination-Count: 100
Pagination-Limit: 20
Pagination-Cursor-Next: abc123
```

### Best Practices
- Default `per_page` = 20, max = 100
- Validate `per_page` server-side (reject > max)
- Return total count only when requested (`?include_count=true`)

---

## 4. Caching Strategies

### HTTP Caching Headers

**Cache-Control**
```
Cache-Control: public, max-age=3600, stale-while-revalidate=60
```
- `public`: CDN cacheable
- `private`: browser only
- `no-cache`: revalidate every time
- `no-store`: never cache
- `max-age`: cache duration in seconds
- `stale-while-revalidate`: serve stale while fetching fresh

**ETag / Last-Modified**
```http
GET /v1/users/123
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT

# Subsequent request:
GET /v1/users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

# 304 Not Modified if unchanged — saves bandwidth
```

### Client-Side Caching Patterns
```javascript
// SWR / React Query pattern
const { data, error, isValidating } = useSWR('/api/users', fetcher, {
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  dedupingInterval: 2000,
  fallbackData: cachedData,
});
```

### CDN Considerations
- Cache static assets at CDN (`Cache-Control: public, max-age=31536000, immutable`)
- Use `Cache-Control: private` for user-specific data
- Invalidate on update: purge URL + tagged cache (`Cache-Tag: user-profile`)
- Edge caching with stale-while-revalidate for API responses

### Cache Invalidation
- **Tag-based invalidation**: `PURGE` by tag, not URL
- **Time-based expiry** as safety net
- **Event-driven invalidation**: invalidate on write (webhook to CDN)
- **UGC data**: short TTL (60-300s) or no-cache

---

## 5. Additional Patterns

### Batch API Requests
```graphql
# GraphQL batch
POST /graphql
[
  { "query": "{ user(id: 1) { name } }" },
  { "query": "{ product(id: 42) { price } }" }
]
```

```http
# REST batch (example: JSON:API)
POST /v1/batch
Content-Type: application/json

{ "requests": [
    { "method": "GET", "path": "/v1/users/123" },
    { "method": "GET", "path": "/v1/orders?userId=123" }
  ]}
```

### Async Job / Queue Patterns

**Poll Model**:
```http
POST /v1/exports
→ 202 Accepted
{ "jobId": "job_abc", "status": "processing", "pollUrl": "/v1/jobs/job_abc" }

GET /v1/jobs/job_abc
→ { "status": "completed", "downloadUrl": "https://..." }
```

**Push/Webhook Model**:
```http
POST /v1/exports
{ "callbackUrl": "https://myapp.com/webhooks/export-done" }
→ 202 Accepted
```

**Best practices**:
- Return `202 Accepted` with job ID immediately
- Include `X-Job-Id` header for tracking
- Set reasonable job timeout (e.g., 5 minutes)
- Implement job progress events for long-running tasks

### Circuit Breaker Pattern
```javascript
const circuitBreaker = new CircuitBreaker(fetch, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
});

circuitBreaker.fallback = () => ({ data: cachedData, stale: true });

// On 50%+ failures, circuit "opens" — fast-fail for 30s
const data = await circuitBreaker.fire(externalApiUrl);
```

### API Gateway Patterns
- **Rate limiting** at gateway layer (upstream APIs protected)
- **Authentication/Authorization** (JWT validation, scope checking)
- **Request routing** (A/B, canary, regional)
- **Request/response transformation** (header manipulation, body reshape)
- **Logging and observability** (request tracing, metrics)
- **Protocol translation** (REST → gRPC, GraphQL federation)

---

## Quick Reference Card

| Pattern | When to Use |
|---------|-------------|
| Webhooks | Event-driven, push notifications |
| OAuth 2.0 | Third-party access, user-delegated auth |
| Cursor pagination | Large/dynamic datasets, feeds |
| Offset pagination | Small/stable datasets, UI page selectors |
| ETag caching | Read-heavy, rarely-changed resources |
| Token bucket rate limiting | API gateway, burst allowance |
| Circuit breaker | External API calls, fault isolation |
| Async jobs (queue) | Long-running operations |
| Batch requests | Reduce round trips, GraphQL |
