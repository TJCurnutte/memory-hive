# Next.js & React Best Practices Research (2026)

> Research compiled: April 2026. Based on Next.js 15/16, React 19, Tailwind CSS v4, and real GitHub patterns.

---

## React Server Components (RSC) Patterns

React Server Components allow components to render on the server and stream HTML to the client with zero client-side JS.

### Pattern 1: Direct async server component with no wrapper

```tsx
// app/blog/page.tsx
export default async function Page() {
  const data = await fetch('https://api.vercel.app/blog')
  const posts = await data.json()
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```
- Identical `fetch` requests in a component tree are **memoized automatically** — you can fetch at the component level instead of prop-drilling
- `fetch` requests are **NOT cached by default** in Next.js 15+ (caching changed from v14)
- Return Date, Map, Set directly — no serialization needed across the server/client boundary

### Pattern 2: Database ORM access (no API layer needed)

```tsx
import { db, posts } from '@/lib/db'

export default async function Page() {
  const allPosts = await db.select().from(posts)
  return (
    <ul>
      {allPosts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```
- Credentials and query logic stay on the server — never shipped to the client
- No need for API routes for data fetching — query directly in Server Components

### Pattern 3: Parallel data fetching

```tsx
// Fetch multiple things in parallel — no waterfall
async function getUserData(userId: string) {
  const [user, posts, followers] = await Promise.all([
    fetch(`/api/users/${userId}`).then(r => r.json()),
    fetch(`/api/users/${userId}/posts`).then(r => r.json()),
    fetch(`/api/users/${userId}/followers`).then(r => r.json()),
  ])
  return { user, posts, followers }
}
```

### Pattern 4: Colocation — keep data fetching near the component that needs it

```tsx
// app/dashboard/page.tsx — page fetches dashboard-level data
async function DashboardPage() {
  const metrics = await getDashboardMetrics()
  return (
    <div>
      <MetricCard data={metrics} />
      {/* These children fetch their own data — no prop drilling */}
      <RecentActivity />
      <TopProducts />
    </div>
  )
}

// app/dashboard/components/RecentActivity.tsx — own fetch, own data
async function RecentActivity() {
  const activity = await db.query.activity.findMany({ limit: 10 })
  return <ActivityList items={activity} />
}
```

---

## Next.js App Router Best Practices

### 1. Async Request APIs (Next.js 15+ Breaking Change)

`cookies()`, `headers()`, `params`, and `searchParams` are now **async**. This unblocks parallel rendering optimizations.

```tsx
import { cookies } from 'next/headers'

export async function AdminPanel() {
  const cookieStore = await cookies()  // now async!
  const token = cookieStore.get('token')
  // ...
}

// params is now async
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  // ...
}

// searchParams is now async
export default async function Page({ searchParams }: { searchParams: Promise<{ q: string }> }) {
  const { q } = await searchParams
  // ...
}
```

### 2. Streaming & Suspense

Streaming means breaking the page into chunks and sending them to the client as they complete — no waiting for slow data.

```tsx
import { Suspense } from 'react'
import BlogList from '@/components/BlogList'
import BlogListSkeleton from '@/components/BlogListSkeleton'

export default async function Page() {
  return (
    <div>
      {/* This renders immediately — outside Suspense */}
      <Header />

      {/* This streams in when ready */}
      <Suspense fallback={<BlogListSkeleton />}>
        <BlogList />
      </Suspense>
    </div>
  )
}
```

**`loading.js` shorthand**: Place a `loading.tsx` in any route folder — it automatically wraps the page in `<Suspense>`:

```tsx
// app/dashboard/loading.tsx — instant loading UI
export default function Loading() {
  return <div className="animate-pulse">Loading...</div>
}
```

### 3. Caching Model Changes (Next.js 15+)

- **`GET` Route Handlers** are no longer cached by default. Opt in with `export const dynamic = 'force-static'`
- **Client Router Cache** no longer caches page components by default
- `fetch` requests are uncached by default — use `use cache` directive or route config to cache:

```tsx
// Cache this fetch for 1 hour
export const revalidate = 3600

// Or use the cache directive
import { cache } from 'react'
const getUser = cache(async (id: string) => {
  const res = await fetch(`/api/users/${id}`)
  return res.json()
})
```

### 4. `next.config.ts` (TypeScript support)

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [{ hostname: 'images.unsplash.com' }],
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
}

export default nextConfig
```

### 5. Server Actions

```tsx
// app/actions.ts
'use server'

export async function submitForm(formData: FormData) {
  const name = formData.get('name')
  const email = formData.get('email')

  await db.insert(users).values({ name, email })
  revalidatePath('/users')
}
```

```tsx
// In a component
import { submitForm } from './actions'

export function SignupForm() {
  return (
    <form action={submitForm}>
      <input name="name" />
      <input name="email" type="email" />
      <button type="submit">Sign Up</button>
    </form>
  )
}
```

### 6. Middleware Pattern

```ts
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
}
```

---

## Tailwind CSS Mastery (v4)

Tailwind v4 moved config to CSS with `@theme` directive:

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --font-display: "Satoshi", "sans-serif";
  --color-brand-50: oklch(0.98 0.02 250);
  --color-brand-500: oklch(0.55 0.25 250);
  --color-brand-900: oklch(0.20 0.12 250);
  --breakpoint-3xl: 120rem;
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);
}
```

### Dynamic values with arbitrary syntax

```html
<!-- Arbitrary values -->
<div class="p-[calc(--spacing(4)-1px)]">
<div class="text-[clamp(1.5rem,4vw,3rem)]">
<div class="bg-[linear-gradient(135deg,#667eea,#764ba2)]">

<!-- Arbitrary properties -->
<div style={{ "--tw-translate-x": "100%" }}>
```

### Dark mode with `darkMode: 'class'` or `darkMode: 'selector'`

```html
<!-- Class-based -->
<div class="dark:bg-slate-900 dark:text-white">

<!-- Color scheme based -->
<div class="@media (prefers-color-scheme: dark) { ... }">
```

### `@apply` in components

```css
.btn-primary {
  @apply px-4 py-2 rounded-lg bg-brand-500 text-white font-medium
         hover:bg-brand-600 active:scale-95 transition-all duration-200;
}
```

### Custom utilities and variants

```css
@utility tab-4 {
  tab-size: 4;
}

@custom-variant theme-midnight (&:where([data-theme="midnight"] *));

/* Usage: theme-midnight:bg-black */
```

---

## Core Web Vitals: LCP, CLS, INP

### LCP (Largest Contentful Paint) — Target: < 2.5s

**What causes poor LCP:**
- Slow server response times
- Render-blocking JS/CSS
- Large unoptimized images (hero images are the usual LCP element)
- Client-side rendering delays content behind JS

**How to fix:**
```tsx
// Use next/image for automatic optimization
import Image from 'next/image'

export function Hero() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority  // ← CRITICAL: tell Next.js to preload this
      className="w-full h-auto"
    />
  )
}
```
- `priority` prop on hero images → adds `<link rel="preload">`
- Preconnect to critical origins: `<link rel="preconnect" href="https://fonts.googleapis.com">`
- Minimize TTFB: use edge caching, static generation where possible
- Remove unused JS blocking render

### CLS (Cumulative Layout Shift) — Target: < 0.1

**What causes CLS:**
- Images without explicit `width`/`height` (browser reserves no space)
- Late-loading fonts causing text reflow
- Ads or iframes without reserved space
- Dynamic content injected above existing content

**How to fix:**
```tsx
// ALWAYS define dimensions on images
<Image src="/img.jpg" width={800} height={400} />

// Reserve space for dynamic content
<div style={{ minHeight: '100px' }}>
  {dynamicContent || <Skeleton />}
</div>

// next/font handles font CLS automatically
```

### INP (Interaction to Next Paint) — Target: < 200ms

INP replaced FID (First Input Delay) in March 2024. Measures responsiveness across all interactions.

**What causes poor INP:**
- Heavy JS execution on main thread during interaction
- Long tasks (>50ms) blocking input response
- Synchronous state updates causing full re-renders
- Large component trees re-rendering on interaction

**How to fix:**
```tsx
// Break up heavy work with requestIdleCallback
function handleClick() {
  requestIdleCallback(() => {
    trackAnalytics()
  })
}

// Use useTransition for non-urgent updates
import { useTransition } from 'react'

function SearchComponent() {
  const [isPending, startTransition] = useTransition()
  const [query, setQuery] = useState('')

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    startTransition(() => {
      setQuery(e.target.value)
    })
  }
}

// Virtualize long lists
import { FixedSizeList } from 'react-window'

function VirtualizedList({ items }: { items: string[] }) {
  return (
    <FixedSizeList height={600} itemCount={items.length} itemSize={50}>
      {({ index, style }) => (
        <div style={style}>{items[index]}</div>
      )}
    </FixedSizeList>
  )
}
```

---

## AI Agent UI Patterns from GitHub

### Obsidian / Logseq-style Dashboards
- Left sidebar with collapsible sections
- Command palette (`Cmd+K`) for quick actions
- Contextual panels that slide in from right
- Markdown-first content editing
- Real-time sync indicators (green dots, "Saving...")

### Linear-style Issue Trackers
- Clean table/kanban hybrid view
- Keyboard-first navigation (j/k to move, e to edit)
- Inline editing without modals
- Status pills with drag-to-reorder
- Filter bar with instant search

### Vercel / Railway Dashboard Patterns
- Global command bar (Cmd+K)
- Collapsible sidebar with nested sections
- Tab-based content panels
- Toast notifications bottom-right
- Modal dialogs with keyboard trap
- Real-time log streaming panels

### Copilot-style Chat UIs
- Sticky input at bottom
- Streaming message output with markdown rendering
- Code blocks with copy button
- Conversation branching / fork
- Context windows showing attached files

### Agent Orchestration Panels (like OpenClaw)
- Agent roster with status indicators (active/idle/error)
- Task queue with progress bars
- Activity feed / event log
- Canvas/workspace area for visual output
- Split-pane layouts (agent list | workspace | details)
- Inline configuration without modal navigation

---

## Top GitHub Repos (by relevance)

### 1. [shadcn/ui](https://github.com/shadcn-ui/ui)
- **Stars: 85k+**
- Not a component library — a code distribution system. You copy-paste actual component code into your project and own it.
- Radix UI primitives + Tailwind. Fully accessible, composable, customizable.
- AI-Ready: open code is LLM-friendly
- Best for: building design systems on top of shadcn's primitives

### 2. [vercel/next.js](https://github.com/vercel/next.js)
- **Stars: 120k+**
- React framework for production. App Router, Server Components, streaming.
- Version 15: async request APIs, React 19 support, Turbopack stable

### 3. [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss)
- **Stars: 85k+**
- Version 4: CSS-native config, no JS config file needed
- `@theme` directive for design tokens in CSS

### 4. [radix-ui/primitives](https://github.com/radix-ui/primitives)
- **Stars: 14k+**
- Unstyled, accessible UI components. Headless — you add your own styles.
- Used by shadcn/ui under the hood.
- Components: Dialog, Dropdown, Select, Tabs, Tooltip, etc.

### 5. [tanstack/query](https://github.com/tanstack/query)
- **Stars: 38k+**
- Server state management for React. Caching, background refetching, optimistic updates.
- Essential for client-side data fetching in Next.js

### 6. [leeerob/next-saas-starter](https://github.com/leeerob/next-saas-starter)
- **Stars: 14k+**
- Production-ready Next.js SaaS starter. Auth (NextAuth), database (Postgres/Prisma), Stripe billing, landing page.
- Good reference for real-world App Router patterns

### 7. [react-hook-form/react-hook-form](https://github.com/react-hook-form/react-hook-form)
- **Stars: 45k+**
- Performant form handling with Yup/Zod validation
- Integrates with shadcn/ui via @hookform/resolvers

### 8. [t3-oss/create-t3-app](https://github.com/t3-oss/create-t3-app)
- **Stars: 20k+**
- T3 Stack: Next.js + TypeScript + Tailwind + tRPC + Prisma + NextAuth
- Opinionated full-stack TypeScript boilerplate

### 9. [upstash/ratelimit](https://github.com/upstash/ratelimit)
- **Stars: 5k+**
- Edge-ready rate limiting for Next.js API routes
- Uses Upstash Redis, works on Vercel Edge Functions

### 10. [colinhacks/zod](https://github.com/colinhacks/zod)
- **Stars: 27k+**
- TypeScript-first schema validation. Used everywhere in the modern stack.
- Powers Next.js server action validation, tRPC type inference

---

## Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **shadcn/ui Docs**: https://ui.shadcn.com/docs
- **Tailwind CSS**: https://tailwindcss.com
- **Web Vitals**: https://web.dev/vitals
- **React 19**: https://react.dev/blog/2024/12/04/react-19