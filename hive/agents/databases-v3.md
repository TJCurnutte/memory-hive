# Database Engineering Deep Dive

> Comprehensive technical reference covering PostgreSQL advanced patterns, Redis for AI apps, Prisma vs Drizzle, Supabase internals, and connection pooling.

---

## Table of Contents

1. [PostgreSQL Advanced Patterns](#1-postgresql-advanced-patterns)
   - [Common Table Expressions (CTEs)](#ctes)
   - [Recursive CTEs](#recursive-ctes)
   - [Window Functions](#window-functions)
   - [Table Partitioning](#table-partitioning)
   - [Query Optimization with EXPLAIN ANALYZE](#explain-analyze)
2. [Redis for AI Applications](#2-redis-for-ai-applications)
   - [Caching Vector Embeddings](#caching-vector-embeddings)
   - [Rate Limiting Patterns](#rate-limiting-patterns)
   - [Redis Modules: RediSearch & RedisJSON](#redis-modules)
3. [Prisma vs Drizzle ORM](#3-prisma-vs-drizzle-orm)
4. [Supabase Internals](#4-supabase-internals)
5. [Database Connection Pooling](#5-database-connection-pooling)

---

## 1. PostgreSQL Advanced Patterns

### A. Common Table Expressions (CTEs)

CTEs (the `WITH` clause) improve query readability and enable patterns impossible with subqueries alone.

#### Basic (Non-Recursive) CTEs

```sql
-- Break complex queries into named steps
WITH regional_sales AS (
  SELECT region, SUM(amount) AS total_sales
  FROM orders
  GROUP BY region
),
top_regions AS (
  SELECT region
  FROM regional_sales
  WHERE total_sales > (SELECT SUM(total_sales) / 10 FROM regional_sales)
)
SELECT region, product, SUM(quantity) AS units, SUM(amount) AS revenue
FROM orders
WHERE region IN (SELECT region FROM top_regions)
GROUP BY region, product
ORDER BY revenue DESC;
```

**Key benefit**: Each CTE is named, documented, and computed once. You can reference prior CTEs in subsequent CTEs within the same query.

#### Writeable CTEs

CTEs can include `INSERT`, `UPDATE`, and `DELETE` with the results used in the main query:

```sql
-- Move old orders to archive, return affected rows
WITH archived AS (
  DELETE FROM orders
  WHERE created_at < NOW() - INTERVAL '2 years'
  RETURNING *
)
INSERT INTO orders_archive
SELECT * FROM archived;
```

#### Lateral Joins with CTEs

```sql
-- Get top 3 products per category
WITH category_products AS (
  SELECT category, product_name, revenue,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) as rank
  FROM product_sales
)
SELECT * FROM category_products WHERE rank <= 3;
```

---

### B. Recursive CTEs

Recursive CTEs can reference themselves, enabling traversal of hierarchical data.

#### Sum 1 to 100

```sql
WITH RECURSIVE t(n) AS (
  VALUES (1)
  UNION ALL
  SELECT n + 1 FROM t WHERE n < 100
)
SELECT SUM(n) FROM t;  -- Returns 5050
```

#### Org Chart Traversal

```sql
WITH RECURSIVE org_tree(id, name, manager_id, depth, path) AS (
  -- Base case: top-level employees (no manager)
  SELECT id, name, manager_id, 0, ARRAY[name]
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive case: employees who report to someone in the tree
  SELECT e.id, e.name, e.manager_id, ot.depth + 1, ot.path || e.name
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT
  REPEAT('  ', depth) || name AS indented_name,
  depth,
  array_size(path, 1) AS level
FROM org_tree
ORDER BY path;
```

#### Materialized Path for Hierarchies

```sql
-- Store path as array: root→parent→child
WITH RECURSIVE tree AS (
  SELECT id, name, parent_id, ARRAY[id] AS path
  FROM categories WHERE parent_id IS NULL

  UNION ALL

  SELECT c.id, c.name, c.parent_id, t.path || c.id
  FROM categories c
  JOIN tree t ON c.parent_id = t.id
)
SELECT * FROM tree;
```

#### Breadth-First vs Depth-First Search

```sql
-- Depth-first (default with ORDER BY path)
WITH RECURSIVE search AS (
  SELECT id, name, parent_id, 0 AS depth, ARRAY[id] AS path
  FROM tree WHERE parent_id IS NULL

  UNION ALL

  SELECT t.id, t.name, t.parent_id, s.depth + 1, s.path || t.id
  FROM tree t
  JOIN search s ON t.parent_id = s.id
)
SELECT *, depth FROM search ORDER BY path;  -- Depth-first

-- Breadth-first using LEVEL
WITH RECURSIVE search AS (
  SELECT id, name, parent_id, 0 AS depth
  FROM tree WHERE parent_id IS NULL

  UNION ALL

  SELECT t.id, t.name, t.parent_id, s.depth + 1
  FROM tree t
  JOIN search s ON t.parent_id = s.id
)
SELECT * FROM search ORDER BY depth;  -- Breadth-first
```

---

### C. Window Functions

Window functions compute aggregate-like values over a set of rows **relative to the current row**, without collapsing the result set.

#### Core Window Function Examples

```sql
-- ROW_NUMBER: Unique row identifier within partition
SELECT
  employee_id,
  department,
  salary,
  ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank_in_dept,
  RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rank_with_gaps,
  DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees;
-- RANK: 1, 2, 2, 4 (gap after tied rows)
-- DENSE_RANK: 1, 2, 2, 3 (no gap)

-- LAG / LEAD: Previous and next row values
SELECT
  order_date,
  amount,
  LAG(amount, 1)  OVER (ORDER BY order_date) AS prev_amount,
  LEAD(amount, 1) OVER (ORDER BY order_date) AS next_amount,
  amount - LAG(amount, 1) OVER (ORDER BY order_date) AS delta
FROM daily_sales;
-- Useful for: period-over-period comparisons, detecting changes

-- Running totals with aggregate-as-window
SELECT
  order_date,
  amount,
  SUM(amount) OVER (ORDER BY order_date) AS running_total,
  AVG(amount) OVER (
    ORDER BY order_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7_day_avg
FROM daily_sales;
```

#### Frame Specifications

Control which rows the window frame includes:

```sql
-- Default frame (UNBOUNDED PRECEDING to CURRENT ROW)
SELECT SUM(amount) OVER (ORDER BY date) FROM sales;

-- Full partition (entire group)
SELECT SUM(amount) OVER (PARTITION BY month ORDER BY date
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) AS month_total FROM sales;

-- Moving average: 3 preceding rows + current
SELECT AVG(amount) OVER (ORDER BY date
  ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
) AS moving_avg FROM sales;

-- GROUPS mode (treats peer rows as groups)
SELECT MAX(amount) OVER (ORDER BY amount
  GROUPS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
) FROM sales;
```

#### NTILE: Percentiles and Buckets

```sql
-- Divide customers into quartiles by spend
SELECT
  customer_id,
  total_spend,
  NTILE(4) OVER (ORDER BY total_spend) AS quartile,
  NTILE(100) OVER (ORDER BY total_spend) AS percentile
FROM customers;

-- Decile analysis
SELECT
  quartile,
  MIN(total_spend) AS min_spend,
  MAX(total_spend) AS max_spend,
  COUNT(*) AS customers
FROM (
  SELECT total_spend, NTILE(10) OVER (ORDER BY total_spend) AS quartile
  FROM customers
) t
GROUP BY quartile;
```

#### CUME_DIST and PERCENT_RANK

```sql
-- CUME_DIST: What fraction of rows fall at or below current row
SELECT
  score,
  CUME_DIST() OVER (ORDER BY score) AS cumulative_pct,
  PERCENT_RANK() OVER (ORDER BY score) AS percent_rank
FROM exam_scores;
-- PERCENT_RANK: (rank - 1) / (total - 1): 0.0 to 1.0
```

---

### D. Table Partitioning

Partitioning splits a large table into smaller, more manageable pieces, while allowing queries to transparently access all partitions.

#### Range Partitioning

```sql
-- Partition by date range
CREATE TABLE orders (
  id BIGSERIAL,
  customer_id BIGINT,
  order_date DATE NOT NULL,
  total DECIMAL(10, 2),
  status TEXT
) PARTITION BY RANGE (order_date);

-- Create monthly partitions
CREATE TABLE orders_2024_01 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Default partition for anything outside defined ranges
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- Indexes on partitioned tables
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_orders_customer ON orders (customer_id);
-- Indexes are automatically created on all partitions
```

#### List Partitioning

```sql
-- Partition by categorical value
CREATE TABLE sales (
  id BIGSERIAL,
  region TEXT NOT NULL,
  amount DECIMAL(10, 2),
  sale_date DATE
) PARTITION BY LIST (region);

CREATE TABLE sales_us PARTITION OF sales
  FOR VALUES IN ('US-North', 'US-South', 'US-East', 'US-West');

CREATE TABLE sales_eu PARTITION OF sales
  FOR VALUES IN ('UK', 'Germany', 'France', 'Netherlands');
```

#### Hash Partitioning

```sql
-- Distribute evenly across N partitions
CREATE TABLE events (
  id BIGSERIAL,
  event_type TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ
) PARTITION BY HASH (id);

-- Create 8 hash partitions
CREATE TABLE events_0 PARTITION OF events
  FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE events_1 PARTITION OF events
  FOR VALUES WITH (MODULUS 8, REMAINDER 1);
-- ... events_2 through events_7
```

#### Partition Management

```sql
-- Detach a partition (keeps data, removes from query planning)
ALTER TABLE orders DETACH PARTITION orders_2022_q4;

-- Attach a partition
ALTER TABLE orders ATTACH PARTITION orders_2025_q1
  FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- Drop old partitions (fast — no vacuum needed on parent)
DROP TABLE orders_2022_q4;

-- Partition pruning: check query plans
EXPLAIN SELECT * FROM orders WHERE order_date = '2024-06-15';
-- Should show "Partitions pruned: ..." in the plan
```

#### Partition Best Practices

- Partition on columns used in `WHERE` clauses
- Keep partition counts manageable (tens to low hundreds, not thousands)
- Use `pg_partman` for automatic partition creation/maintenance
- Avoid over-partitioning (too many small partitions = overhead)

---

### E. EXPLAIN ANALYZE — Reading Query Plans

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
  u.name,
  COUNT(o.id) AS order_count,
  SUM(o.total) AS lifetime_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '1 year'
GROUP BY u.id;
```

#### Key Terms to Look For

| Term | Meaning |
|------|---------|
| `Seq Scan` | Full table scan — often needs an index |
| `Index Scan` | Uses an index, retrieves full rows |
| `Index Only Scan` | Uses index only (no heap fetch) — ideal |
| `Bitmap Heap/Index Scan` | Uses bitmap for multiple index matches |
| `Hash Join` | Builds hash table for join — good for large sets |
| `Nested Loop` | Row-by-row — fine for small sets, bad for large |
| `Sort` | In-memory or disk sort — check `Sort Method` |
| `Aggregate` | GROUP BY / COUNT / SUM operation |
| `Parallel Seq Scan` | Multi-core full table scan |

#### Interpreting Costs

```sql
-- cost=startup..total
-- startup: cost before first row can be returned
-- total: cost to return all rows
-- rows=X: planner's estimate of rows (compare to actual)

-- "actual time=0.015..0.893" = first row at 15ms, all at 893ms
-- "rows=1523 loops=1" = 1523 rows returned, scanned once
-- "Rows Removed by Filter: 0" = perfect filter
```

#### Common Performance Problems

```sql
-- Problem: Seq Scan on large table without index
-- Solution: Add index
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Problem: N+1 (multiple nested loops)
-- Solution: Use JOIN or batch fetch

-- Problem: Hash join with very large estimated rows
-- Solution: Increase work_mem (temporarily):
SET work_mem = '256MB';

-- Problem: Slow sort (disk)
-- Solution: Increase work_mem or add index on ORDER BY column
```

---

## 2. Redis for AI Applications

### A. Caching Vector Embeddings

When serving AI apps, embeddings are expensive to compute and large to store. Redis stores them efficiently for fast retrieval.

#### Storing Embeddings with RedisJSON

```typescript
import { createClient } from 'redis';

const redis = createClient({ url: process.env.REDIS_URL });

await redis.json.set(`embedding:doc:${docId}`, '.', {
  content: 'The meaning of life is 42.',
  model: 'openai/text-embedding-3-small',
  vector: embeddingFloat32Array,  // Float32Array from AI model
  dimensions: 1536,
  createdAt: Date.now(),
});

// Set TTL (embeddings can become stale)
await redis.expire(`embedding:doc:${docId}`, 60 * 60 * 24 * 30); // 30 days
```

#### Similarity Search with RediSearch

```sql
-- Create index on document embeddings
FT.CREATE docs_index ON JSON
  SCHEMA
    $.content AS content TEXT
    $.vector AS vector VECTOR HNSW
      FLAT DIM 1536 DISTANCE_METRIC COSINE
      TYPE FLOAT32
      INITIAL_CAP 100000
```

```typescript
// Search for similar documents
const queryEmbedding = await getEmbedding('search query');

const results = await redis.ft.search('docs_index', '*', {
  DIALECT: 2,
  RETURN: ['$.content', '$.docId'],
  params: {
    vec: Buffer.from(queryEmbedding).toString('base64'),
  },
  query: `(*)=>[KNN 10 @vector $vec AS score]`,
  sortBy: { BY: 'score', DIRECTION: 'ASC' },
});
```

#### Caching LLM Responses

```typescript
import { createHash } from 'crypto';

function cacheKey(messages: any[]) {
  return 'llm:response:' + createHash('sha256')
    .update(JSON.stringify(messages))
    .digest('hex').substring(0, 32);
}

async function cachedCompletion(messages: any[]) {
  const key = cacheKey(messages);

  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const response = await openai.chat.completions.create({
    model: 'gpt-4-turbo',
    messages,
  });

  await redis.setEx(key, 3600, JSON.stringify(response)); // 1hr TTL
  return response;
}
```

---

### B. Rate Limiting Patterns

#### Sliding Window Rate Limiter

More accurate than fixed windows — no burst at window boundaries.

```typescript
async function slidingWindowRateLimit(
  key: string,
  limit: number,
  windowMs: number
): Promise<{ allowed: boolean; remaining: number; resetAt: number }> {
  const now = Date.now();
  const windowStart = now - windowMs;
  const multi = redis.multi();

  // Remove expired entries
  multi.zRemRangeByScore(key, 0, windowStart);

  // Count current requests in window
  multi.zCard(key);

  // Add this request
  multi.zAdd(key, { score: now, value: `${now}:${Math.random()}` });

  // Set expiry on the key
  multi.expire(key, Math.ceil(windowMs / 1000));

  const [, currentCount] = await multi.exec() as [null, number];

  const allowed = currentCount < limit;
  const remaining = Math.max(0, limit - currentCount - (allowed ? 1 : 0));
  const resetAt = now + windowMs;

  return { allowed, remaining, resetAt };
}

// Usage
const { allowed, remaining, resetAt } = await slidingWindowRateLimit(
  `ratelimit:api:${userId}`,
  100,        // 100 requests
  60 * 1000   // per minute
);

if (!allowed) {
  res.set('X-RateLimit-Remaining', '0');
  res.set('X-RateLimit-Reset', String(Math.ceil(resetAt / 1000)));
  return res.status(429).json({ error: 'Rate limit exceeded' });
}
```

#### Token Bucket (Smooth Rate Limiting)

```typescript
// Redis Lua script for atomic token bucket
const TOKEN_BUCKET_SCRIPT = `
  local key = KEYS[1]
  local limit = tonumber(ARGV[1])
  local refillRate = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])
  local requested = tonumber(ARGV[4])

  local bucket = redis.call('HMGET', key, 'tokens', 'lastRefill')
  local tokens = tonumber(bucket[1]) or limit
  local lastRefill = tonumber(bucket[2]) or now

  -- Refill tokens based on time elapsed
  local elapsed = now - lastRefill
  local refill = math.floor(elapsed * refillRate / 1000)
  tokens = math.min(limit, tokens + refill)
  lastRefill = now

  if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', lastRefill)
    redis.call('EXPIRE', key, 3600)
    return {1, tokens}
  else
    redis.call('HMSET', key, 'tokens', tokens, 'lastRefill', lastRefill)
    return {0, tokens}
  end
`;

async function tokenBucket(
  key: string,
  limit: number,
  refillPerSecond: number,
  requested: number = 1
): Promise<{ allowed: boolean; remaining: number }> {
  const result = await redis.eval(
    TOKEN_BUCKET_SCRIPT, 1, key,
    limit, refillPerSecond, Date.now(), requested
  ) as [number, number];

  return { allowed: result[0] === 1, remaining: result[1] };
}
```

---

### C. Redis Modules

#### RediSearch (Full-Text Search)

```sql
FT.CREATE products_idx ON HASH
  PREFIX 1 "product:"
  SCHEMA
    name TEXT WEIGHT 5
    description TEXT
    category TAG
    price NUMERIC SORTABLE
    rating NUMERIC SORTABLE
```

```typescript
// Full-text search with facets
const results = await redis.ft.search('products_idx', 'wireless headphones', {
  WITHSCORES: true,
  HIGHLIGHT: { TAGS: { before: '**', after: '**' } },
  FILTER: ['@price', 50, 200],  // Price between $50-$200
  SORTBY: { BY: 'rating', DIRECTION: 'DESC' },
  LIMIT: { from: 0, size: 20 },
});
```

#### RedisJSON (JSON Storage)

```typescript
// Nested JSON access with JSONPath
await redis.json.set('user:123', '$', {
  name: 'Alice',
  preferences: {
    theme: 'dark',
    notifications: { email: true, push: false },
    interests: ['AI', 'music', 'hiking'],
  },
});

// Update specific path
await redis.json.set('user:123', '$.preferences.theme', '"light"');

// Query nested fields
const theme = await redis.json.get('user:123', { path: '$.preferences.theme' });

// Array operations
await redis.json.arrAppend('user:123', '$.preferences.interests', '"photography"');
```

#### Distributed Locks

```typescript
async function withLock<T>(
  key: string,
  fn: () => Promise<T>,
  ttlMs: number = 10000
): Promise<T> {
  const lockKey = `lock:${key}`;
  const lockValue = `${process.pid}:${Date.now()}`;

  const acquired = await redis.set(lockKey, lockValue, {
    NX: true,   // Only set if not exists
    PX: ttlMs,  // TTL in milliseconds
  });

  if (!acquired) {
    throw new Error(`Lock not acquired: ${key}`);
  }

  try {
    return await fn();
  } finally {
    // Only release if we still own the lock (value matches)
    const script = `
      if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
      else
        return 0
      end
    `;
    await redis.eval(script, 1, lockKey, lockValue);
  }
}
```

---

## 3. Prisma vs Drizzle ORM

### Prisma

**Approach**: Schema-first, generates type-safe client from `.prisma` file. High abstraction, excellent DX.

```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}
```

```typescript
// Query builder with full type safety
const posts = await prisma.post.findMany({
  where: { published: true, author: { email: { contains: '@company.com' } } },
  include: { author: true },
  orderBy: { createdAt: 'desc' },
  take: 10,
});

// Relation loading strategy (fixes N+1)
const posts = await prisma.post.findMany({
  relationLoadStrategy: 'join',  // Uses SQL JOIN instead of separate queries
  where: { authorId: 1 },
});
```

**Pros**:
- Best-in-class TypeScript inference
- Intuitive schema migrations (`prisma migrate dev`)
- `prisma studio` — GUI for data browsing
- Excellent documentation and community

**Cons**:
- Heavier runtime (generated client has overhead)
- Single PrismaClient instance in serverless = connection pool exhaustion
- Less flexible for complex raw SQL needs

**Prisma Accelerate**: Global edge database proxy — handles connection pooling, caching, and rate limiting globally. ~$4/month per million API calls.

### Drizzle ORM

**Approach**: Lightweight, SQL-like, schema defined in TypeScript. More control, less magic.

```typescript
// schema.ts
import { pgTable, serial, text, boolean, timestamp } from 'drizzle-orm/pg-core';

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content'),
  published: boolean('published').default(false).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
});
```

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { eq, desc, sql } from 'drizzle-orm';

// SQL-like queries — feels close to raw SQL
const posts = await db
  .select({
    id: posts.id,
    title: posts.title,
    authorName: users.name,
  })
  .from(posts)
  .leftJoin(users, eq(posts.authorId, users.id))
  .where(eq(posts.published, true))
  .orderBy(desc(posts.createdAt))
  .limit(10);

// Transactions
const result = await db.transaction(async (tx) => {
  const [newPost] = await tx.insert(posts).values({ title: 'Hello', authorId: 1 }).returning();
  await tx.update(users).set({ postCount: sql`${users.postCount} + 1` }).where(eq(users.id, 1));
  return newPost;
});
```

**Pros**:
- Nearly zero runtime overhead — compiles to optimized SQL
- Full control over queries (escape hatch to raw SQL easily)
- Works great with serverless (no connection pooling issues)
- Schema as TypeScript code — version control friendly
- Drizzle Kit for migrations

**Cons**:
- Steeper learning curve for complex relations
- Less intuitive for beginners
- Smaller community than Prisma

### Comparison Summary

| Feature | Prisma | Drizzle |
|---------|--------|---------|
| Schema definition | `.prisma` file (DSL) | TypeScript tables |
| Type safety | Excellent | Excellent |
| Performance | Good | Excellent (lower overhead) |
| Migrations | `prisma migrate` | `drizzle-kit generate/push` |
| Raw SQL | Via `$queryRaw` | Native support |
| Learning curve | Gentle | Moderate |
| Serverless | Use Accelerate | Native support |
| Bundle size | Larger (~200KB) | Smaller (~10KB) |

---

## 4. Supabase Internals

### Architecture Overview

Supabase is **PostgreSQL as a service** with a rich application layer built on top:

```
Client SDK (JS/Python/Dart)
        ↓
PostgREST API (auto-generated REST from Postgres schema)
        ↓
PostgreSQL + Row Level Security
        ↓
Auth (GoTrue) + Realtime (Elixir) + Storage + Edge Functions
```

### Row Level Security (RLS)

RLS enforces access control at the database level — every row-level policy is checked for every query.

```sql
-- Enable RLS on a table
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Only authors can see their own unpublished posts
CREATE POLICY "Authors see own unpublished posts"
  ON posts FOR SELECT
  USING (
    auth.uid() = author_id  -- auth.uid() from JWT token
    OR published = true    -- Everyone sees published posts
  );

-- Only authors can update their own posts
CREATE POLICY "Authors update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = author_id)
  WITH CHECK (auth.uid() = author_id);  -- Row must satisfy this to be written

-- Public read, authenticated users can insert
CREATE POLICY "Anyone can read profiles"
  ON profiles FOR SELECT TO authenticated, anon
  USING (true);

CREATE POLICY "Users create own profile"
  ON profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

### Auth Internals (GoTrue)

GoTrue is Supabase's auth server (written in Go):

- Issues JWTs signed with a secret key
- Stores users in the `auth.users` table
- Supports: email/password, magic link, OAuth providers, SSO (SAML/OIDC)

```typescript
// Sign up with email/password
const { data, error } = await supabase.auth.signUp({
  email: 'alice@example.com',
  password: 'secure-password',
});

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'alice@example.com',
  password: 'secure-password',
});

// Access the user ID in RLS
-- auth.uid() returns the UUID from the JWT's sub claim
SELECT auth.uid();  -- e.g., 'a1b2c3d4-...'
```

### Realtime Subscriptions

```typescript
// Subscribe to INSERT events on posts
const channel = supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'posts',
      filter: 'author_id=eq.' + userId,
    },
    (payload) => {
      console.log('New post:', payload.new);
    }
  )
  .subscribe();

// Cleanup
supabase.removeChannel(channel);
```

### Edge Functions

Supabase Edge Functions run on Deno Deploy (Cloudflare's edge runtime):

```typescript
// supabase/functions/generate-summary/index.ts
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { documentId } = await req.json();
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!  // Service role = bypass RLS
  );

  const { data: doc } = await supabase
    .from('documents')
    .select('*')
    .eq('id', documentId)
    .single();

  // Call AI API for summary...
  const summary = await generateSummary(doc.content);

  return Response.json({ summary });
});
```

---

## 5. Database Connection Pooling

### The Serverless Problem

Each Lambda/Edge function invocation creates a new process. Without pooling:
- PostgreSQL max connections (default: 100) exhaust immediately
- Connection overhead (~5-50ms per connection) kills performance

### PgBouncer

PgBouncer is a lightweight connection pooler that sits between your app and PostgreSQL:

```ini
; pgbouncer.ini
[databases]
myapp = host=pg-host.com port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction  ; Critical for serverless
max_client_conn = 10000
default_pool_size = 20   ; Connections to actual Postgres
```

**Pool modes**:
| Mode | Description | Use case |
|------|-------------|----------|
| `session` | One DB connection per client session | Traditional apps |
| `transaction` | Connection per transaction, returned to pool after commit | **Serverless** — key feature |
| `statement` | No transaction support, executes and returns | OLTP stress testing |

### Prisma Data Proxy / Accelerate

```typescript
// prisma/schema.prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
}

generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}
```

```typescript
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pg from 'pg';

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });
```

### Drizzle with Connection Pooler

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,          // Max connections from pool
  idleTimeout: 30000,
  connectionTimeoutMillis: 2000,
});

const db = drizzle({ client: pool });

// Drizzle handles connection management automatically
const users = await db.select().from(usersTable).limit(10);
```

### Connection Pool Best Practices

```sql
-- Monitor connection usage
SELECT
  numbackends AS active_connections,
  (SELECT setting FROM pg_settings WHERE name = 'max_connections') AS max_connections,
  (SELECT setting FROM pg_settings WHERE name = 'max_connections')::int -
    numbackends AS available
FROM pg_stat_database
WHERE datname = current_database();

-- Long-running queries
SELECT
  pid,
  now() - query_start AS duration,
  state,
  left(query, 200) AS query_preview
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

---

*Sources: [PostgreSQL Documentation](https://www.postgresql.org/docs/current/), [Redis Docs](https://redis.io/docs/), [Prisma Docs](https://prisma.io/docs), [Supabase Docs](https://supabase.com/docs), [Drizzle Docs](https://orm.drizzle.team)*
