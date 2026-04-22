# Cloud Architecture Deep Dive

> Comprehensive technical reference covering Vercel vs AWS vs Cloudflare, serverless architectures, edge computing, CDN strategies, global data replication, multi-region deployments, and cost optimization.

---

## Table of Contents

1. [Platform Comparison](#1-platform-comparison)
   - [Vercel](#vercel)
   - [AWS](#aws)
   - [Cloudflare Pages & Workers](#cloudflare)
   - [Alternatives: Fly.io, Render, Railway](#alternatives)
2. [Serverless Architectures](#2-serverless-architectures)
3. [Edge Computing](#3-edge-computing)
4. [CDN Strategies](#4-cdn-strategies)
5. [Global Data Replication](#5-global-data-replication)
6. [Multi-Region Deployments](#6-multi-region-deployments)
7. [Cost Optimization](#7-cost-optimization)

---

## 1. Platform Comparison

### Vercel

**Philosophy**: Zero-config DX. Vercel owns the developer experience as the primary product. It is optimized for frontend frameworks (Next.js, Nuxt, SvelteKit, etc.) and abstracts away infrastructure decisions.

#### Core Architecture

```
Git Push → Build → Edge Network (126+ PoPs) → Serverless Functions
                         ↓
                   ISR Cache (TTL-based or on-demand)
```

- **Automatic SSL** (Let's Encrypt) on all deployments
- **Preview Deployments** for every PR (unique URL)
- **Production Deployments** from `main` branch
- **Framework Awareness**: Reads your framework's rendering config at build time to set cache headers automatically

#### Serverless vs Edge

| | Serverless Functions | Edge Functions |
|-|---------------------|----------------|
| Runtime | Node.js 18 | V8 Isolates |
| Memory | 1024-3008 MB | 128 MB |
| Cold start | 100-500ms | ~0ms |
| Max execution | 10s (CPU) | 50ms (CPU) |
| Regions | 20+ | Global (126 PoPs) |
| Cost | $0.40/1M invocations | Free (within generous limits) |

```typescript
// Vercel Serverless Function
export const config = { runtime: 'nodejs' }; // default

export default async function handler(req: Request) {
  // Heavy computation OK here
  const result = await processLargeData();
  return Response.json(result);
}

// Vercel Edge Function
export const runtime = 'edge';

export default async function handler(req: Request) {
  // Instant startup, runs at CDN edge
  const country = req.headers.get('x-vercel-ip-country');
  return Response.json({ region: country });
}
```

#### Streaming Responses

```typescript
export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of generateLargeDataset()) {
        controller.enqueue(encoder.encode(JSON.stringify(chunk) + '\n'));
        await new Promise(r => setTimeout(r, 100)); // Simulate processing
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  });
}
```

#### Vercel ISR (Incremental Static Regeneration)

```typescript
// Re-generate at most once per hour
export const revalidate = 3600;

// Per-path on-demand revalidation (for CMS webhooks)
import { revalidateTag, revalidatePath } from 'next/cache';

// In a webhook handler
revalidateTag('posts');        // Revalidate all routes tagged 'posts'
revalidatePath('/blog');       // Revalidate specific path
revalidatePath('/blog/[slug]', 'page'); // Dynamic path
```

#### Pricing

- **Hobby**: Free (100GB bandwidth, 100 hours serverless)
- **Pro**: $20/month + usage (1000GB bandwidth, $0.40/100K serverless invocations)
- **Enterprise**: Custom pricing, SLA, SSO, audit logs

---

### AWS

**Philosophy**: Maximum flexibility and control. You own every layer. Great for large organizations with dedicated DevOps teams, cost-sensitive workloads, or workloads that need specific compliance certifications.

#### Core Services

| Service | Use Case | Pricing Model |
|---------|----------|--------------|
| Lambda | Serverless compute | $0.20/1M requests + compute time |
| CloudFront | CDN | $0.0085-0.02/GB data transfer |
| S3 | Object storage | $0.023/GB (standard) |
| API Gateway | API management | $3.50/1M API calls |
| ECS/EKS | Container orchestration | EC2 instances + ECS fees |
| RDS | Managed databases | Instance hours + storage |
| Aurora | Serverless/Serverlessv2 databases | Request units + storage |
| CloudFormation/CDK | Infrastructure as code | Free |

#### Lambda Deep Dive

```typescript
// AWS CDK — define Lambda with infrastructure as code
import { aws_lambda as lambda, aws_apigateway as apigw } from 'aws-cdk-lib';

const handler = new lambda.Function(this, 'MyHandler', {
  runtime: lambda.Runtime.NODEJS_18_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('dist'),
  memorySize: 512,
  timeout: Duration.seconds(10),
  environment: {
    NODE_ENV: 'production',
  },
  // Provisioned concurrency — pay to keep warm
  provisionedConcurrentExecutions: 5,
});

new apigw.LambdaRestApi(this, 'api', {
  handler,
  binaryMediaTypes: ['*/*'],  // Support binary responses
});
```

```typescript
// Lambda function with streaming response
export const handler = awslambda.streamifyResponse(
  async (event, responseStream) => {
    const encoder = new TextEncoder();

    responseStream.write('event: message\ndata: ');
    for (const item of await fetchLargeDataset()) {
      responseStream.write(`data: ${JSON.stringify(item)}\n\n`);
    }
    responseStream.end();
  }
);
```

#### Lambda Cold Start Mitigation

```typescript
// 1. Provisioned Concurrency — pay to keep functions warm
// (CDK)
new lambda.Alias(this, 'alias', {
  aliasName: 'live',
  version: handler.currentVersion,
  provisionedConcurrentExecutions: 3,
});

// 2. SnapStart (Java) — snapshot execution environment
@LambdaScope
public class Handler {
  @SnapStart
  public String handleRequest(String input) {
    // Initialized once, snapshotted, restored in ~200ms
    return heavyInitialization() + process(input);
  }
}

// 3. SnapStart for Node.js (via AWSDistroForOpenTelemetry)
```

#### Amplify Hosting

```yaml
# amplify.yml — build specification
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
        - npm run test
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  buildRuntime: nodejs
  nodeVersion: 18
```

Amplify is to AWS what Vercel is to Vercel — a streamlined DX for frontend deployment — but with full access to AWS services.

---

### Cloudflare

**Philosophy**: The network IS the product. Cloudflare runs the largest network in the world (300+ PoPs) and puts compute directly on it. Workers run on V8 isolates (not containers), eliminating cold starts entirely.

#### Cloudflare Workers

```typescript
// workers/api.ts
export interface Env {
  DB: D1Database;
  AI: Ai;
  R2: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/api/posts' && request.method === 'GET') {
      const { results } = await env.DB
        .prepare('SELECT * FROM posts ORDER BY created_at DESC LIMIT 10')
        .all();
      return Response.json(results);
    }

    return new Response('Not found', { status: 404 });
  },
};

export const config = {
  runtime: 'warn',
  // Bindings available in env:
  // env.DB — D1 database
  // env.AI — AI Gateway (LLM routing)
  // env.R2 — Object storage (S3-compatible)
  // env.KV — Key-value store
  // env.QUEUE — Message queue
  // env.DURABLE_OBJECT — Stateful single-threaded actor
};
```

#### Durable Objects — Stateful Edge

The killer feature for stateful workloads. A Durable Object is a **single-threaded actor** that runs at the edge, maintaining state in memory:

```typescript
// durable_object.ts
export class GameSession implements DurableObject {
  private state: DurableObjectState;
  private players: Map<string, WebSocket> = new Map();

  constructor(state: DurableObjectState) {
    this.state = state;
  }

  async fetch(request: Request): Promise<Response> {
    const playerId = request.headers.get('X-Player-ID');

    if (request.headers.get('Upgrade') === 'websocket') {
      const { socket, response } = await this.state.acceptWebSocket({ id: playerId });
      this.players.set(playerId, socket);
      this.broadcast({ type: 'player_joined', playerId });
    }

    return new Response('OK');
  }

  private broadcast(message: object) {
    const data = JSON.stringify(message);
    for (const socket of this.players.values()) {
      socket.send(data);
    }
  }
}
```

#### Workers KV — Distributed Key-Value

```typescript
// Write
await KV.put('user:123:session', JSON.stringify(sessionData), {
  expirationTtl: 86400,  // 24 hours
  metadata: { userId: 123 },
});

// Atomic counter
const newCount = await KV.increment('pageviews:/blog/intro', 1);

// Read with fallback
const cache = await KV.getWithMetadata('config:theme');
console.log(cache.value, cache.metadata);
```

#### Cloudflare Platform Summary

| Feature | Description |
|---------|-------------|
| Workers KV | Global key-value (eventually consistent, ~60ms reads) |
| D1 | SQLite at the edge (read replicas globally) |
| R2 | S3-compatible object storage (no egress fees) |
| Durable Objects | Single-threaded stateful actors |
| Queues | Message queue (consumer = Workers) |
| AI Gateway | LLM routing, caching, rate limiting |
| Turnstile | Privacy-first CAPTCHA alternative |
| Zero Trust | SASE/Zero Trust network access |
| **Pricing** | **$5/month flat for Workers** (with 10M requests, 100K CPU-hours) |

---

### Alternatives

#### Fly.io

- Runs **Firecracker VMs** (micro-VMs like containers but with hardware isolation)
- Supports **any language/runtime** — not just serverless functions
- **Closer to metal** than Vercel/Cloudflare but with simpler ops than AWS
- Best for: apps needing long-running processes, WebSockets, background workers, region-specific latency
- Free tier: 3 shared VMs, 160GB outbound

```bash
# fly launch — creates Dockerfile or detects framework
fly launch --image ghcr.io/myapp:latest

# Scale to specific regions
fly scale count 2 --region lax    # Los Angeles
fly scale count 3 --region ams    # Amsterdam

# Secrets
fly secrets set DATABASE_URL=$DATABASE_URL
```

#### Render

- Simpler than AWS, more opinionated than Fly
- Managed services: PostgreSQL, Redis, background workers
- Auto-sleep on free tier (like Heroku)
- Best for: teams wanting managed DBs without AWS complexity
- Free tier: 750 hours/month, sleep after 15 min inactivity

#### Railway

- Modern DX, inline with Vercel but with broader backend support
- Spins up containers per deployment
- Supports: Node.js, Python, Go, Rust, Ruby, Dockerfiles
- Pay per resource (not per-seat)
- Best for: rapid prototyping, startups wanting full-stack without AWS

---

## 2. Serverless Architectures

### The Serverless Mental Model

**You don't manage servers** — the cloud provider handles provisioning, scaling, and capacity planning. You write stateless functions that:
- Are triggered by events
- Scale from 0 to thousands instantly
- Execute in isolated environments
- Cost nothing when idle

### Event-Driven Patterns

```typescript
// AWS EventBridge → Lambda pattern
// event.json from EventBridge
{
  "version": "0",
  "id": "12345678-1234-1234-1234-111122223333",
  "detail-type": "ORDER_PLACED",
  "source": "ecommerce.orders",
  "account": "123456789012",
  "time": "2024-01-15T10:00:00Z",
  "region": "us-east-1",
  "detail": {
    "orderId": "ORD-12345",
    "customerId": "CUST-678",
    "total": 149.99,
    "items": ["SKU-001", "SKU-002"]
  }
}
```

```typescript
// Lambda handler
export const handler = async (event: EventBridgeEvent<OrderPlaced>) => {
  const { orderId, customerId, total } = event.detail;

  // 1. Save to database
  await db.orders.create({ data: { orderId, customerId, total } });

  // 2. Send confirmation email (async)
  await sendEmail({ to: customerId, subject: `Order ${orderId} confirmed` });

  // 3. Update inventory (async)
  await Promise.all(event.detail.items.map(sku =>
    inventoryService.decrement(sku)
  ));

  // 4. Publish to SNS for other consumers
  await sns.publish({
    TopicArn: process.env.ORDER_EVENTS_TOPIC,
    Message: JSON.stringify({ orderId, customerId, total }),
  }).promise();

  return { statusCode: 200, body: JSON.stringify({ processed: true }) };
};
```

### Step Functions / EventBridge Pipes

For complex workflows, orchestrate with state machines:

```json
// Step Functions state machine definition
{
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:validate-order",
      "Next": "CheckInventory"
    },
    "CheckInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:check-inventory",
      "Choice": {
        "Variable": "$.inStock",
        "BooleanEquals": true,
        "Next": "ProcessPayment",
        "Next": "NotifyOutOfStock"
      }
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:process-payment",
      "Next": "FulfillOrder"
    },
    "FulfillOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:fulfill-order",
      "End": true
    }
  }
}
```

### Stateless Design Patterns

Key rules for serverless:
1. **No local state** — every request must be self-contained
2. **Externalize state** — use DynamoDB, Redis, S3 for persistence
3. **Idempotency** — same input should produce same output (use idempotency keys)
4. **Timeout awareness** — set appropriate timeouts, handle partial failures

```typescript
// Idempotent payment processing
export const handler = async (event: APIGatewayEvent) => {
  const { orderId, amount, idempotencyKey } = JSON.parse(event.body);

  // Check if already processed (use DynamoDB or Redis)
  const existing = await redis.get(`processed:${idempotencyKey}`);
  if (existing) {
    return { statusCode: 200, body: JSON.stringify(JSON.parse(existing)) };
  }

  // Process payment...
  const result = await paymentGateway.charge(amount);

  // Store result with idempotency key (24h TTL)
  await redis.setEx(
    `processed:${idempotencyKey}`,
    86400,
    JSON.stringify(result)
  );

  return { statusCode: 200, body: JSON.stringify(result) };
};
```

---

## 3. Edge Computing

### What Edge Means

Traditional architecture: Client → CDN (static assets) → Origin Server (dynamic)
Edge architecture: Client → Edge PoP (runs code) → Origin (optional)

The **edge PoP** (Point of Presence) is a data center run by the CDN/provider. Instead of just serving cached files, it can run arbitrary code at the network edge.

### When to Use Edge

| Use Case | Edge Appropriate? |
|----------|-------------------|
| A/B testing | ✅ Yes — instant routing at edge |
| Auth/cookie checks | ✅ Yes — redirect before origin hit |
| Geolocation routing | ✅ Yes — detect country, redirect |
| Personalization | ✅ Yes — lightweight HTML modifications |
| Heavy DB queries | ❌ No — keep at origin |
| AI model inference | ❌ No (unless using edge-optimized models) |
| Large data processing | ❌ No — use serverless or origin |
| Real-time chat | ⚠️ Maybe — use WebSockets (Fly.io, or Durable Objects) |

### Edge vs Origin Decision Framework

```
Request arrives at edge PoP
         ↓
Does it need user-specific data from a database?
  → YES: Can we serve cached version with user data injected?
      → YES: Edge (cache with personalized headers/cookies)
      → NO: Pass to origin (serverless or traditional server)
  → NO: Is it a simple redirect/rewrite/auth check?
      → YES: Edge (near-instant)
      → NO: Pass to origin
```

### Cache-Control at Edge

```typescript
// Edge handler — set smart cache headers
export default async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const country = req.headers.get('x-vercel-ip-country') ?? 'US';

  const response = await fetch(req); // Forward to origin

  return new Response(response.body, {
    headers: {
      ...Object.fromEntries(response.headers),
      // Cache at edge for 1 hour, serve stale for up to 1 day while revalidating
      'Cache-Control': url.pathname.startsWith('/api/')
        ? 'no-cache'  // Never cache API responses
        : 'public, s-maxage=3600, stale-while-revalidate=86400',
      // Add country header for downstream caching
      'X-Served-Country': country,
    },
  });
}
```

### Stale-While-Revalidate

The most powerful edge caching directive — serve stale content while fetching fresh in the background:

```
Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400
```

- **s-maxage=3600**: Cache at CDN for 1 hour
- **stale-while-revalidate=86400**: Serve stale (expired) content for up to 24 hours after expiry while fetching fresh
- **Result**: User always gets a fast response (no waiting for origin), content is eventually consistent

---

## 4. CDN Strategies

### Cache Invalidation

```typescript
// Vercel — invalidate by tag (instant, across all PoPs)
import { revalidateTag } from 'next/cache';
// Called from webhook handler

// Cloudflare — purge by URL or tag
await fetch(`https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${CLOUDFLARE_TOKEN}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    files: ['https://example.com/images/hero.jpg'],
    // or tags: ['blog-post'], for Cache-Tag based purge
  }),
});

// AWS CloudFront — invalidation (slower, use sparingly)
const cf = new AWS.CloudFront();
await cf.createInvalidation({
  DistributionId: process.env.CF_DIST_ID,
  InvalidationBatch: {
    CallerReference: `${Date.now()}`,
    Paths: {
      Quantity: 1,
      Items: ['/images/*'],
    },
  },
}).promise();
// Note: avoid large invalidations; use cache versioning instead
```

### Cache-Busting via Filename Hashing

```typescript
// Next.js with webpack — filenames include content hashes
// next.config.js
module.exports = {
  output: 'export',  // For static export
  images: {
    unoptimized: true,  // Required for static export
  },
};
// Generated: /_next/static/chunks/app/page-abc123.js
// Cache forever (immutable) — new deploy = new URL
```

### SWR (Stale-While-Revalidate) on the Client

```typescript
// Client-side SWR — prefer cache, revalidate in background
import useSWR from 'swr';

function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher, {
    revalidateOnFocus: true,      // Revalidate when tab regains focus
    revalidateOnReconnect: true,   // Revalidate on network reconnect
    refreshInterval: 0,           // No polling (use for real-time instead)
    dedupingInterval: 2000,        // Dedupe requests within 2s
    fallbackData: { name: 'Loading...' },  // Pre-populate from SSR
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorState error={error} />;
  return <ProfileCard user={data} />;
}
```

---

## 5. Global Data Replication

### Read Replicas

```typescript
// Route reads to replicas, writes to primary
class DatabaseRouter {
  private primary: Pool;
  private replicas: Pool[];

  async query(sql: string, params: any[], isRead: boolean) {
    const pool = isRead
      ? this.replicas[Math.floor(Math.random() * this.replicas.length)]
      : this.primary;
    return pool.query(sql, params);
  }
}

// Usage
await db.query('SELECT * FROM posts WHERE id = $1', [id], true);  // Replica
await db.query('INSERT INTO posts VALUES ($1, $2)', [id, data], false); // Primary
```

### Multi-Region Active-Active

Data written to any region is replicated to all other regions. Conflicts are inevitable — must handle them.

#### Conflict Resolution Strategies

```typescript
// Last-Write-Wins (simplest, default for many DBs)
const result = await db
  .update(users)
  .set({ name: newName, updatedAt: new Date() })
  .where(eq(users.id, userId));
// Uses updatedAt as tiebreaker (must be indexed)

// Automatic with Supabase Realtime + Conflict Handling
// Configure per-table conflict resolution in Supabase
// e.g., "Use the row with the latest updated_at"

// CRDTs — Conflict-free Replicated Data Types (best for collaborative apps)
// Yjs, Automerge for collaborative editing
// Redis CRDT module for distributed counters/sets
```

#### Distributed Databases

| Database | Replication Model | Use Case |
|----------|------------------|---------|
| **PlanetScale** | MySQL-compatible, Vitess-based, regional reads | Large-scale read-heavy apps |
| **Turso** | SQLite at edge, libSQL fork | Edge-heavy, latency-sensitive |
| **Neon** | PostgreSQL, serverless branching | CI/CD with DB branches |
| **Fauna** | Document + relational, global transactions | Complex queries, multi-region |
| **CockroachDB** | Distributed PostgreSQL, strong consistency | Financial/transactional apps |

```typescript
// Turso — embedded SQLite at the edge
import { createClient } from '@libsql/client';

const turso = createClient({
  url: 'libsql://my-db-user.turso.io',
  authToken: process.env.TURSO_TOKEN,
});

// Fetch nearest edge DB
const nearestDb = await turso.execute({
  sql: 'SELECT * FROM config WHERE key = ?',
  args: ['feature_flags'],
});
```

---

## 6. Multi-Region Deployments

### Data Sovereignty

GDPR, CCPA, and other regulations may require:
- EU user data stays in EU
- Data never crosses certain borders
- Audit logs for data access

```yaml
# Vercel — regional configuration
# vercel.json
{
  "regions": ["fra1", "ams1", "cdg1"],  # EU only
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1",
      "headers": {
        "X-Data-Region": "eu-west"
      }
    }
  ]
}
```

### Traffic Failover

```typescript
// Multi-region with failover using Cloudflare Health Checks
// 1. Set up health check on primary origin
// 2. If primary fails, Cloudflare automatically routes to secondary

// Manual failover logic (for custom setup)
async function getData(key: string): Promise<Data> {
  const regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1'];

  // Try regions in parallel, use first successful response
  const results = await Promise.anySettled(
    regions.map(region => fetchFromRegion(region, key))
  );

  const successful = results.filter(r => r.status === 'fulfilled');
  if (successful.length === 0) throw new Error('All regions failed');

  return (successful[0] as PromiseFulfilledResult<Data>).value;
}
```

### Disaster Recovery

```yaml
# AWS — multi-region DR setup
# Infrastructure
Resources:
  PrimaryDB:
    Type: AWS::RDS::DBCluster
    Properties:
      MultiAz: true
      Region: us-east-1
      BackupRetentionPeriod: 30
      PreferredBackupWindow: "03:00-04:00"

  ReadReplicaEU:
    Type: AWS::RDS::DBCluster
    Properties:
      Region: eu-west-1
      SourceRegion: us-east-1
      # Promote to primary if primary fails
```

---

## 7. Cost Optimization

### Serverless Cost Model

```typescript
// Lambda cost calculation
// $0.20 per 1M requests + $0.0000166667 per GB-second
// Compute: 128MB * 100ms = 0.000016667 GB-seconds
// Cost per 1M invocations, 128MB, 100ms each:
// = $0.20 + (1,000,000 * 0.0000166667) = $0.20 + $16.67 = $16.87/M

// If using 1024MB, 1GB * 1s = $0.0000166667 per invocation
// vs 128MB: 10x cost for 8x memory

// Estimating with provisioned concurrency
// $0.000015 per GB-second × instances × duration × hours
```

### Cost Optimization Strategies

```typescript
// 1. Right-size Lambda memory
// Monitor actual memory usage with CloudWatch
// Increase memory incrementally until CPU-bound (not I/O bound)
// CPU scales with memory in Lambda

// 2. Batch processing — process multiple items per invocation
export const handler = async (event: S3Event) => {
  const records = event.Records;
  // Process all records in one invocation (up to 1000)
  const items = records.map(r => JSON.parse(r.s3.object.key));

  await Promise.all(items.map(item => processItem(item)));
  // vs calling Lambda once per item = 1000x the cost
};

// 3. Use SQS for decoupling (Lambda polls SQS)
// Lambda processes messages in batches
// Pay for processing time, not idle polling

// 4. Edge caching to reduce origin/serverless invocations
// Cache aggressively at CDN
// Every cached request = $0 serverless cost
```

### Egress Cost Awareness

Data transfer OUT of cloud providers is expensive:

| Provider | Egress (per GB) |
|----------|----------------|
| AWS CloudFront | $0.0085-0.02 |
| AWS EC2 (direct) | $0.09 |
| Vercel | Included in plan |
| Cloudflare | Free (usually) |
| R2 (S3-compatible) | Free |

**Rule**: Always route through CDN for egress-heavy apps. Never serve files directly from S3 to users — go through CloudFront/R2.

### Reserved Capacity vs On-Demand

| Strategy | Savings | Risk |
|----------|---------|------|
| On-demand Lambda | Pay per use | No upfront, full flexibility |
| Reserved concurrency (1yr) | ~44% savings | Capacity locked |
| Savings Plans (AWS) | 30-70% | Commitment required |
| Vercel Pro (fixed) | Predictable | Overage risk |
| Cloudflare Workers | Flat $5/mo | Excellent value |

### Cost Monitoring & Alerts

```typescript
// AWS — set cost alerts
import { CloudWatchClient, PutMetricAlarmCommand } from '@aws-sdk/client-cloudwatch';

const alarm = new PutMetricAlarmCommand({
  AlarmName: 'MonthlySpendAlert',
  MetricName: 'EstimatedCharges',
  Namespace: 'AWS/Billing',
  Statistic: 'Maximum',
  Period: 3600,
  Threshold: 500,  // Alert at $500/month
  ComparisonOperator: 'GreaterThanThreshold',
  EvaluationPeriods: 1,
  TreatMissingData: 'notBreaching',
});
await cw.send(alarm);
```

---

## Platform Selection Decision Matrix

| Need | Best Platform |
|------|--------------|
| Next.js app, fastest DX | Vercel |
| Full AWS integration, compliance needs | AWS |
| Global low-latency, AI apps, cheap Workers | Cloudflare |
| Long-running processes, WebSockets, region-specific | Fly.io |
| Managed DB + hosting, simple ops | Render / Railway |
| Edge SQLite, offline-first apps | Turso |
| MySQL at scale with branching | PlanetScale |
| Distributed PostgreSQL, strong consistency | CockroachDB |

---

*Sources: [Vercel Docs](https://vercel.com/docs), [AWS Docs](https://docs.aws.amazon.com/), [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/), [Fly.io Docs](https://fly.io/docs/), [PlanetScale Docs](https://planetscale.com/docs)*
