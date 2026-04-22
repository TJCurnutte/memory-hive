# Next.js 15 Deep Dive

> Comprehensive technical reference for Next.js 15 (React 19) — App Router, Server Components, caching, edge deployment, and modern patterns.

---

## Table of Contents

1. [React Server Components](#1-react-server-components)
2. [Async Request APIs (Breaking Change)](#2-async-request-apis-breaking-change)
3. [Streaming SSR & Suspense](#3-streaming-ssr--suspense)
4. [Partial Pre-Rendering (PPR)](#4-partial-pre-rendering-ppr)
5. [Server Actions](#5-server-actions)
6. [Next.js Caching Strategies](#6-nextjs-caching-strategies)
7. [Middleware → Proxy (Edge)](#7-middleware--proxy-edge)
8. [App Router Best Practices](#8-app-router-best-practices)
9. [Deployment to Edge / Vercel](#9-deployment-to-edge--vercel)
10. [Turbopack (Stable)](#10-turbopack-stable)

---

## 1. React Server Components

### The Mental Model

React Server Components (RSC) run exclusively on the server. They have zero client-side JavaScript bundle impact. This fundamental shift changes how you architect UI:

- **Server Components**: Run on the server, can `await` anything (DB, file system, external APIs), render to HTML/React trees, cannot use browser APIs or `useState`/`useEffect`.
- **Client Components** (`'use client'`): Hydrate in the browser, can use React state/lifecycle, receive serialized props from server components.

### When to Use `'use client'`

Mark a component `'use client'` when it needs:
- React state (`useState`, `useReducer`)
- Browser effects (`useEffect`)
- Event listeners / interactivity
- Client-only browser APIs (`window`, `localStorage`, `navigator`)
- Context providers (though you can compose with a server component shell)

```tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Component Composition Patterns

The key insight: pass server component children into client components to keep large subtrees on the server:

```tsx
// ✅ GOOD: Heavy rendering stays on server
export default function Page() {
  return (
    <ExpensiveInteractiveWrapper>
      <HeavyDataComponent /> {/* Server component — zero JS sent */}
    </ExpensiveInteractiveWrapper>
  );
}

// ❌ BAD: Forcing everything through client
'use client';
export function Page() {
  const [data] = useState(fetchData()); // Client-side data fetching
  return <ExpensiveList data={data} />;
}
```

### Data Fetching in Server Components

```tsx
// app/blog/page.tsx
export default async function BlogPage() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 3600 } // ISR — revalidate every hour
  });
  const posts = await res.json();

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </li>
      ))}
    </ul>
  );
}
```

Or with an ORM (credentials never shipped to client):

```tsx
import { db, posts } from '@/lib/db';

export default async function Page() {
  const allPosts = await db.select().from(posts);
  return <PostList posts={allPosts} />;
}
```

---

## 2. Async Request APIs (Breaking Change)

Next.js 15 made several request-specific APIs asynchronous. This is a **breaking change** but simplifies the mental model.

### Affected APIs

| API | Old | New |
|-----|-----|-----|
| `cookies()` | Synchronous | `async` — `await cookies()` |
| `headers()` | Synchronous | `async` — `await headers()` |
| `draftMode()` | Synchronous | `async` |
| `params` | Synchronous | `async` in layouts/pages/routes |
| `searchParams` | Synchronous | `async` in page components |

### Migration Example

```tsx
// Next.js 14 (sync — now shows deprecation warning)
import { cookies } from 'next/headers';

export function AdminPanel() {
  const cookieStore = cookies();
  const token = cookieStore.get('token');
  // ...
}

// Next.js 15 (async — recommended)
import { cookies } from 'next/headers';

export async function AdminPanel() {
  const cookieStore = await cookies();
  const token = cookieStore.get('token');
  // ...
}
```

Use the codemod for automated migration:

```bash
npx @next/codemod@canary next-async-request-api .
```

---

## 3. Streaming SSR & Suspense

### The Problem Without Streaming

When a Server Component fetches slow data, the **entire page** blocks until that data resolves. The user sees a blank screen.

### Streaming Solution

Break the page into **chunks** that stream independently. Fast static parts render immediately; slow dynamic parts fill in as they resolve.

### Approach 1: `loading.tsx` — Route-Level Streaming

```tsx
// app/blog/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="animate-pulse h-24 bg-gray-200 rounded" />
      ))}
    </div>
  );
}
```

This wraps the entire route segment in a `<Suspense>` boundary automatically. The layout renders immediately; the page content streams when ready.

### Approach 2: `<Suspense>` — Component-Level Streaming

```tsx
import { Suspense } from 'react';
import BlogList from '@/components/BlogList';
import BlogListSkeleton from '@/components/BlogListSkeleton';

export default async function Page() {
  return (
    <div>
      {/* Static header renders immediately */}
      <Header />

      {/* Streaming content — shows skeleton while loading */}
      <Suspense fallback={<BlogListSkeleton />}>
        <BlogList /> {/* fetches data internally */}
      </Suspense>

      {/* Another independent stream */}
      <Suspense fallback={<CommentsSkeleton />}>
        <Comments />
      </Suspense>
    </div>
  );
}
```

### Key Insight: Independent Streams in Parallel

Since these Suspense boundaries are siblings, their data fetches run in parallel on the server:

```tsx
// Both fetches happen simultaneously
<Suspense fallback={<ReviewsSkeleton />}>
  <Reviews />     // fetchReviews() — runs in parallel
</Suspense>
<Suspense fallback={<RatingsSkeleton />}>
  <Ratings />    // fetchRatings() — runs in parallel
</Suspense>
```

---

## 4. Partial Pre-Rendering (PPR)

Partial Pre-Rendering (PTR) is Next.js's approach to combining static shells with dynamic content. As of Next.js 15, PPR is the foundation for how Next.js handles rendering.

### The Core Idea

A single route renders as a **static shell** (cached, fast) with **dynamic holes** (uncached, streamed in). The user gets the fastest possible first response while dynamic data streams.

### How It Works

1. The static portions of the page are pre-rendered at build time or request time
2. Dynamic Suspense boundaries create "holes" in the static shell
3. The shell is served immediately; holes stream in as data resolves
4. React (with Suspense) stitches everything together on the client

### Cache Semantics Changed in Next.js 15

Next.js 15 changed defaults:
- **`GET` Route Handlers**: No longer cached by default (was cached in Next.js 14)
- **Client Router Cache**: Page components no longer cached by default
- `fetch()` requests are **not cached** by default

```tsx
// Next.js 15 — explicit opt-in to caching
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 0 }          // 0 = always fresh (default in v15)
  // next: { revalidate: 3600 }   // ISR — revalidate every hour
  // cache: 'no-store'            // never cache
});

// To force static caching:
export const dynamic = 'force-static';
```

---

## 5. Server Actions

Server Actions are async functions that run on the server but can be called from client components. They replace the need for separate API routes for many mutations.

### Defining a Server Action

```tsx
// app/actions.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  await db.insert(posts).values({ title, content });

  // Invalidate cached pages
  revalidatePath('/blog');
  revalidatePath('/'); // Homepage list
}
```

### Calling from a Client Component

```tsx
'use client';

import { createPost } from '@/app/actions';

export function PostForm() {
  return (
    <form action={createPost}>
      <input name="title" type="text" placeholder="Post title" />
      <textarea name="content" placeholder="Post content" />
      <button type="submit">Publish</button>
    </form>
  );
}
```

### Optimistic Updates

Use `useOptimistic` for instant feedback before the server confirms:

```tsx
'use client';

import { useOptimistic } from 'react';
import { toggleLike } from '@/app/actions';

export function LikeButton({ initialLikes, postId }: Props) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (state, newLike) => state + 1
  );

  async function handleClick() {
    addOptimisticLike(initialLikes + 1);
    await toggleLike(postId);
  }

  return (
    <button onClick={handleClick}>
      ❤️ {optimisticLikes}
    </button>
  );
}
```

### Security: Unguessable Endpoints

Server Actions in Next.js 15 use **unguessable endpoint paths** generated at build time. This prevents CSRF attacks where an attacker guesses action URLs. Unused actions are also automatically removed from client bundles.

---

## 6. Next.js Caching Strategies

Next.js maintains **four layers of caching** that stack together:

### Cache Layers (outermost to innermost)

```
Request → Router Cache → Data Cache → Full Route Cache
```

### 1. Full Route Cache (Build/Deploy Time)

- Stores pre-rendered React component trees as static HTML + RSC payload
- Populated by: `generateStaticParams`, `force-static` export, or default static routes
- Invalidated by: rebuild, on-demand ISR revalidation

```tsx
// Force a route to be statically generated
export const dynamic = 'force-static';

// Or with time-based revalidation
export const revalidate = 3600; // Revalidate every hour
```

### 2. Data Cache (Per-Request)

- Stores data from `fetch()` calls and ORM queries
- Keyed by: URL + fetch options
- `fetch()` with `cache: 'force-cache'` (default for explicit fetches)
- `fetch()` with `cache: 'no-store'` = bypass data cache

### 3. Request Memoization

- In-memory cache for identical fetches within a single request
- React deduplicates identical `fetch()` calls in the same component tree
- Automatically garbage collected after the request

### 4. Router Cache (Client-Side)

- Stores RSC payloads in the browser (service worker)
- Navigations use this cache before network requests
- Configurable with `staleTimes`:

```js
// next.config.js
module.exports = {
  experimental: {
    staleTimes: {
      dynamic: 30,   // Private — dynamic segment stale time (seconds)
      static: 300,   // Shared — static segment stale time (seconds)
    }
  }
}
```

### Caching Decision Matrix

| Scenario | Caching Strategy |
|----------|----------------|
| Static marketing page | `force-static`, build-time rendering |
| Blog post (update on content change) | ISR with `revalidate` |
| User-specific dashboard | Dynamic (no caching), `export const dynamic = 'force-dynamic'` |
| API route | `GET` not cached by default in v15; opt-in with `force-static` |
| Real-time data (stock prices) | Dynamic, or client polling with SWR |

---

## 7. Middleware → Proxy (Edge)

In Next.js 15, the `middleware.ts` file has been **renamed to `proxy.ts`** (though `middleware.ts` still works with a deprecation warning). The new naming better reflects what it actually does — acting as a proxy layer before routes render.

### Core Pattern: Auth Check at Edge

```tsx
// proxy.ts (or middleware.ts)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const token = request.cookies.get('session')?.value;

  // Protect authenticated routes
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
};
```

### Geolocation Routing

```tsx
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const country = request.geo?.country;
  const url = request.nextUrl.clone();

  if (country === 'EU') {
    url.pathname = `/eu${url.pathname}`;
  }

  return NextResponse.rewrite(url);
}
```

### A/B Testing at Edge

```tsx
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const response = NextResponse.next();

  // Assign variant if not already assigned
  let variant = request.cookies.get('ab_variant')?.value;
  if (!variant) {
    variant = Math.random() > 0.5 ? 'A' : 'B';
    response.cookies.set('ab_variant', variant, { maxAge: 60 * 60 * 24 * 30 });
  }

  response.headers.set('x-ab-variant', variant);
  return response;
}
```

### Matcher Syntax

```ts
export const config = {
  // Match specific paths
  matcher: ['/about', '/contact'],

  // Match with wildcards
  matcher: ['/about/:path*', '/blog/:slug'],

  // Regex exclusions (exclude static files)
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],

  // With conditions (has/missing)
  matcher: [{
    source: '/api/:path*',
    has: [{ type: 'header', key: 'Authorization' }],
    missing: [{ type: 'cookie', key: 'auth-token' }],
  }],
};
```

---

## 8. App Router Best Practices

### File Conventions & Hierarchy

```
app/
├── layout.tsx          # Root layout — wraps all pages
├── page.tsx            # Homepage
├── loading.tsx         # Loading UI for this segment
├── error.tsx           # Error boundary for this segment
├── not-found.tsx       # 404 UI for this segment
├── route.ts            # Route Handler (GET/POST/PUT/DELETE)
├── proxy.ts            # Edge proxy/middleware
├── (marketing)/
│   ├── layout.tsx      # Shared layout for marketing routes
│   ├── about/page.tsx
│   └── pricing/page.tsx
└── (app)/
    ├── layout.tsx      # Authenticated app layout
    ├── dashboard/
    │   ├── page.tsx    # /dashboard
    │   └── loading.tsx
    └── settings/
        └── page.tsx    # /settings
```

### Route Groups `(marketing)` vs `(app)`

Route groups (folders in parentheses) don't affect the URL path. Use them to:
- Group layouts (shared `layout.tsx`)
- Group routes by auth requirement
- Organize code without changing URLs

### Parallel Routes `@folder`

```tsx
// app/@modal/(.)photo/[id]/page.tsx
// Accessible at: /photo/123 (rendered alongside @sidebar)
// Uses intercepting routes to show modal overlay
```

### Metadata API

```tsx
// app/blog/[slug]/page.tsx
import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      images: [post.coverImage],
    },
  };
}
```

### `generateStaticParams` — Pre-render Dynamic Routes

```tsx
export async function generateStaticParams() {
  const posts = await db.select().from(postsTable);
  return posts.map(post => ({ slug: post.slug }));
}
```

### `notFound()` and Error Boundaries

```tsx
// Trigger 404
import { notFound } from 'next/navigation';

if (!post) notFound();

// Custom 404 UI: app/not-found.tsx
export default function NotFound() {
  return <h1>Page not found</h1>;
}

// Error boundary: app/error.tsx
'use client';
export function ErrorBoundary({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

## 9. Deployment to Edge / Vercel

### Vercel Edge Network

- **126+ PoPs** across 51 countries
- **Framework-aware caching**: routing and cache policies are derived from your Next.js config automatically
- **Automatic HTTPS** with TLS 1.2/1.3 on every deployment
- **DDoS protection** included on all plans
- **Zero config required** for supported frameworks

### Edge Functions vs Serverless Functions

| Feature | Edge Functions | Serverless Functions |
|---------|---------------|---------------------|
| Runtime | V8 (Edge) | Node.js |
| Cold start | ~0ms | 100-500ms |
| Memory | 128MB | 1024-3008MB |
| Execution time | 50ms (CPU) | 10s (CPU) |
| Use case | Auth, redirects, A/B tests | Heavy computation, file I/O |

Edge functions run on **V8 isolates** — not containers — making them near-instant to start.

```tsx
// Deployed to edge automatically if no heavy deps
import { NextResponse } from 'next/server';

export const runtime = 'edge'; // or 'nodejs' (default for serverless)

export async function GET(request: Request) {
  const url = new URL(request.url);
  return NextResponse.json({
    region: request.headers.get('x-vercel-ip-country') ?? 'unknown',
    cacheStatus: 'MISS',
  }, {
    headers: {
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  });
}
```

### Incremental Static Regeneration (ISR)

ISR combines static performance with dynamic freshness:

```tsx
// Re-generate at most once per hour
export const revalidate = 3600;

// On-demand revalidation (webhook)
import { revalidateTag } from 'next/cache';

// Triggered by CMS webhook
revalidateTag('posts');
```

### Image Optimization

```tsx
import Image from 'next/image';

// Images served from Vercel's edge-optimized CDN
// WebP/AVIF auto-negotiated
// Responsive sizes generated automatically
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority         // Preload for LCP optimization
  placeholder="blur"
  blurDataURL={base64}
/>
```

### Self-Hosting Improvements

Next.js 15 gives more control over `Cache-Control` headers when self-hosting:

```js
// next.config.js
module.exports = {
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
      ],
    },
  ],
};
```

---

## 10. Turbopack (Stable)

Turbopack is the Rust-based successor to Webpack, now **stable in Next.js 15** for development. It provides:

- **5x faster cold starts** compared to Webpack
- **10x faster hot module replacement** (HMR)
- **Better incremental compilation** — only recompiles changed modules

```bash
# Next.js 15 enables Turbopack by default
npm run dev  # Uses Turbopack automatically

# To use Webpack (fallback)
npx next dev --no-turbopack
```

### Turbopack Limitations (as of Next.js 15)

- Production builds still use Webpack/Rspack (Turbopack for production is experimental)
- Some webpack plugins may not be compatible
- CSS modules with custom loaders have limited support

---

## Quick Reference: Migration Checklist for Next.js 15

```bash
# 1. Upgrade
npx @next/codemod@canary upgrade latest

# 2. Run async request API migration
npx @next/codemod@canary next-async-request-api .

# 3. Audit caching — add explicit cache options where needed
#    GET Route Handlers no longer cached by default

# 4. Rename middleware.ts → proxy.ts (optional but recommended)
#    The old name still works with a deprecation warning

# 5. Enable Turbopack (it's stable now!)
npm run dev  # Turbopack is now the default

# 6. Verify Server Actions are secure
#    Unguessable endpoints are now enforced by default
```

---

## Recommended Learning Path

1. Start with **React Server Components** — the foundational shift
2. Master **Suspense + streaming** for perceived performance
3. Learn **Server Actions** for mutation patterns
4. Deep-dive **caching layers** — this is where most performance bugs live
5. Learn **proxy (middleware)** for auth, geolocation, and routing
6. Explore **edge functions** for global-scale performance

---

*Sources: [Next.js 15 Blog](https://nextjs.org/blog/next-15), [Next.js Docs](https://nextjs.org/docs), [React Documentation](https://react.dev)*
