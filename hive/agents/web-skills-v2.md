# Web Dev Skills — Practical Reference (2026)

> 15 production-ready skills for modern Next.js + React + Tailwind development.

---

### Skill 1: Component Architecture & Colocation

**What it is:** Organizing components so data fetching, styles, and logic live as close as possible to where they're used, reducing prop drilling and bundle bloat.

**When to use:** Building any page with multiple data dependencies — fetch at the component that needs it rather than in a parent and drilling down.

**How to do it:**

```tsx
// app/dashboard/page.tsx — Page fetches only page-level data
export default async function Page() {
  const user = await getUser()  // only page-level fetch

  return (
    <div>
      <UserHeader user={user} />  {/* pass only what children can't fetch themselves */}
      <StatsGrid />
      <ActivityFeed />
    </div>
  )
}

// app/dashboard/components/StatsGrid.tsx — fetches its own data
async function StatsGrid() {
  const stats = await db.query.stats.findMany()  // colocation!
  return <div>{stats.map(s => <StatCard key={s.id} stat={s} />)}</div>
}

// app/dashboard/components/ActivityFeed.tsx — fetches its own data
async function ActivityFeed() {
  const activity = await db.query.activity.findMany({ limit: 20 })
  return <ul>{activity.map(a => <ActivityItem key={a.id} item={a} />)}</ul>
}
```

**Rules:**
- Server Components can `await` directly — no `useEffect`, no loading state needed
- Pass only what a child genuinely can't fetch itself (auth, IDs from URL)
- Keep components small and single-purpose

**Example — File structure:**
```
app/
  dashboard/
    page.tsx              ← only fetches dashboard-level data
    loading.tsx           ← streaming skeleton for whole page
    components/
      StatsGrid.tsx       ← fetches its own stats
      ActivityFeed.tsx    ← fetches its own activity
      StatCard.tsx        ← presentational, no fetch, receives props
```

---

### Skill 2: Server vs. Client Component Decisions

**What it is:** Choosing whether a component renders on the server (default) or the client (with interactivity). Wrong decisions cause unnecessary JS bundles and performance issues.

**When to use:** Every time you create a new component — ask this first.

**Decision tree:**

```
Does it need:
  - useState, useEffect, useRef?
  - Browser APIs (window, document)?
  - Event listeners (onClick, onChange)?
  - Animation/motion?
→ YES → Client Component ('use client')

Is it a leaf in the tree? (button, input, card, text)
→ Make it a Client Component only if it needs interactivity.
→ Otherwise, keep it Server.

Does it fetch data from a DB or API?
→ Server Component (default, no directive needed)

Is it the shell (layout, page) that holds children?
→ Server Component.
```

**How to do it:**

```tsx
// ✅ Server Component (default — no directive needed)
// Can: fetch data, access DB, render children
async function BlogPost({ id }: { id: string }) {
  const post = await db.posts.findUnique({ where: { id } })
  return (
    <article>
      <h1>{post.title}</h1>
      {/* Interactive like button → needs "use client" */}
      <LikeButton postId={id} initialCount={post.likes} />
    </article>
  )
}

// ✅ Client Component — needs browser interactivity
'use client'

import { useState } from 'react'

function LikeButton({ postId, initialCount }: { postId: string; initialCount: number }) {
  const [count, setCount] = useState(initialCount)

  async function handleLike() {
    setCount(c => c + 1)
    await fetch(`/api/posts/${postId}/like`, { method: 'POST' })
  }

  return <button onClick={handleLike}>❤️ {count}</button>
}
```

**Best practice:** Push `'use client'` as low in the tree as possible. A single interactive button doesn't need to make its parent a client component.

---

### Skill 3: Streaming and Suspense

**What it is:** Progressive rendering that shows a fast shell immediately while slower data fetches complete, eliminating full-page loading spinners.

**When to use:** Pages with slow data (external API calls, large DB queries) where you don't want users staring at a blank screen.

**How to do it:**

**Approach A — Route-level loading.tsx (simplest):**
```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-48 animate-pulse rounded bg-slate-200" />
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 animate-pulse rounded bg-slate-100" />
        ))}
      </div>
    </div>
  )
}
```

**Approach B — Component-level Suspense (more control):**
```tsx
import { Suspense } from 'react'
import HeavyChart from './HeavyChart'
import ChartSkeleton from './ChartSkeleton'

export default function AnalyticsPage() {
  return (
    <div className="grid gap-6">
      {/* Fast — no API call, renders immediately */}
      <QuickStats />

      {/* Slow — streams in when ready */}
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart />
      </Suspense>

      {/* Another slow component */}
      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />
      </Suspense>
    </div>
  )
}
```

**Skeleton component example:**
```tsx
// ChartSkeleton.tsx
export function ChartSkeleton() {
  return (
    <div className="space-y-2">
      <div className="h-4 w-32 animate-pulse rounded bg-slate-200" />
      <div className="h-64 animate-pulse rounded-lg bg-slate-100" />
      <div className="flex justify-between">
        {[1,2,3,4,5,6].map(i => (
          <div key={i} className="h-2 w-4 animate-pulse rounded bg-slate-200" />
        ))}
      </div>
    </div>
  )
}
```

**Key rule:** Put slow data fetches **inside** the Suspense boundary, not above it. A slow parent blocks all children from streaming.

---

### Skill 4: Tailwind Design System Setup

**What it is:** Defining your brand tokens (colors, fonts, spacing, radii) in a central place so the whole UI is consistent and one change propagates everywhere.

**When to use:** Starting a new project or refactoring to unify design language.

**How to do it:**

**Tailwind v4 CSS-native approach (2026 recommended):**
```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  /* Colors — use oklch for perceptually uniform gradients */
  --color-brand-50:  oklch(0.98 0.02 250);
  --color-brand-100: oklch(0.96 0.04 250);
  --color-brand-500: oklch(0.55 0.25 250);
  --color-brand-600: oklch(0.50 0.28 250);
  --color-brand-900: oklch(0.20 0.12 250);

  --color-surface:    oklch(0.99 0 0);
  --color-surface-soft: oklch(0.97 0.01 240);
  --color-border:      oklch(0.92 0.01 240);

  --color-text-primary:   oklch(0.15 0.03 250);
  --color-text-secondary: oklch(0.45 0.02 250);
  --color-text-muted:     oklch(0.55 0.02 250);

  /* Typography */
  --font-sans: "DM Sans", "system-ui", sans-serif;
  --font-display: "Satoshi", "DM Sans", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", monospace;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  /* Easing */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-smooth: cubic-bezier(0.3, 0, 0, 1);
}
```

**Build reusable component classes:**
```css
@layer components {
  .btn {
    @apply inline-flex items-center justify-center gap-2 rounded-lg
           px-4 py-2 text-sm font-medium transition-all duration-200
           focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500
           disabled:opacity-50 disabled:pointer-events-none;
  }

  .btn-primary {
    @apply btn bg-brand-500 text-white hover:bg-brand-600 active:scale-95;
  }

  .btn-ghost {
    @apply btn text-text-secondary hover:bg-surface-soft hover:text-text-primary;
  }

  .card {
    @apply rounded-xl border border-border bg-surface p-6 shadow-sm;
  }

  .input {
    @apply flex h-10 w-full rounded-lg border border-border bg-surface
           px-3 py-2 text-sm placeholder:text-text-muted
           focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
           disabled:cursor-not-allowed disabled:opacity-50;
  }
}
```

**Usage in components:**
```tsx
<button className="btn-primary">
  <PlusIcon className="h-4 w-4" />
  Add Item
</button>

<div className="card">
  <h3 className="font-display text-lg">Dashboard</h3>
  <p className="text-text-secondary">Welcome back.</p>
</div>

<input className="input" placeholder="Search..." />
```

---

### Skill 5: Dark/Light Mode with next-themes

**What it is:** A theme provider that persists user preference (localStorage), respects system preference, and applies a CSS class to the `<html>` element.

**When to use:** Any site with a dark mode toggle. Works with Tailwind's `dark:` variant.

**How to do it:**

**Step 1: Install**
```bash
npm install next-themes
```

**Step 2: Create a ThemeProvider**
```tsx
// components/theme-provider.tsx
'use client'

import { ThemeProvider as NextThemesProvider } from 'next-themes'

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

**Step 3: Wrap root layout**
```tsx
// app/layout.tsx
import { ThemeProvider } from '@/components/theme-provider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**Step 4: Use in components**
```tsx
'use client'
import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch — theme not known until client
  useEffect(() => setMounted(true), [])

  if (!mounted) return <div className="h-9 w-9" /> // placeholder same size

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="rounded-lg p-2 hover:bg-surface-soft transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  )
}
```

**Step 5: CSS design tokens for both modes:**
```css
/* Define semantic tokens in @theme */
@theme {
  --color-bg:         oklch(0.99 0 0);
  --color-bg-dark:    oklch(0.13 0.02 250);
  --color-text:       oklch(0.15 0.03 250);
  --color-text-dark:  oklch(0.92 0.01 250);
}

/* Use dark: variant in components */
.button {
  background-color: var(--color-bg);
  color: var(--color-text);
}

.dark .button {
  background-color: var(--color-bg-dark);
  color: var(--color-text-dark);
}
```

---

### Skill 6: Image Optimization with next/image

**What it is:** Automatic image optimization (WebP/AVIF conversion, lazy loading, blur placeholder, responsive sizes) that eliminates manual resizing and improves LCP.

**When to use:** Any `<img>` tag in a Next.js app. There's almost never a reason to use a raw `<img>`.

**How to do it:**

**Basic usage:**
```tsx
import Image from 'next/image'

// ALWAYS set width and height to prevent CLS
// priority = true for above-the-fold images (LCP fix!)
export function HeroSection() {
  return (
    <div className="relative h-[500px] w-full">
      <Image
        src="/hero.jpg"
        alt="Product hero shot"
        fill
        className="object-cover"
        priority  // Preloads the image — critical for LCP
        sizes="100vw"
      />
    </div>
  )
}
```

**With remote images — configure allowed domains:**
```ts
// next.config.ts
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { hostname: 'images.unsplash.com' },
      { hostname: 'picsum.photos' },
      { protocol: 'https', hostname: '*.amazon.com' },
    ],
  },
}
export default nextConfig
```

**Avatar with fallback:**
```tsx
export function Avatar({ src, alt, size = 40 }: { src?: string; alt: string; size?: number }) {
  return (
    <div className="relative overflow-hidden rounded-full" style={{ width: size, height: size }}>
      {src ? (
        <Image src={src} alt={alt} fill className="object-cover" />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-brand-500 text-white text-sm font-medium">
          {alt.slice(0, 1).toUpperCase()}
        </div>
      )}
    </div>
  )
}
```

**Responsive sizes:**
```tsx
<Image
  src={post.thumbnail}
  alt={post.title}
  fill
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  // On mobile: 100vw, on tablet: 50vw, on desktop: 33vw
  className="object-cover"
/>
```

---

### Skill 7: Font Optimization with next/font

**What it is:** Self-hosted Google Fonts via `next/font` that eliminates layout shift (CLS) from font swapping by measuring and preloading fonts at build time.

**When to use:** Any text on the page. Replace `<link>` font tags with `next/font` always.

**How to do it:**

```tsx
// app/layout.tsx
import { DM_Sans, Satoshi, JetBrains_Mono } from 'next/font/google'

const dmSans = DM_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  display: 'swap',       // Shows fallback font immediately, swaps when loaded
  variable: '--font-sans',  // CSS variable injected on <html>
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${dmSans.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
```

```css
/* app/globals.css */
@theme {
  --font-sans: var(--dm-sans), "system-ui", sans-serif;
  --font-mono: var(--jetbrains-mono), "Fira Code", monospace;
}
```

**Result:** No external network request for fonts, no FOUT (flash of unstyled text), zero CLS from fonts.

---

### Skill 8: API Routes and Server Actions

**What it is:** Two patterns for handling form submissions and API calls — Route Handlers for REST-style APIs, Server Actions for form mutations.

**When to use:** 
- Route Handlers: external API calls, webhook receivers, mobile app backends
- Server Actions: form submissions, mutations, anything triggered by user interaction

**How to do it:**

**Server Actions (preferred for forms):**
```tsx
// app/actions.ts
'use server'

import { z } from 'zod'

const CreatePostSchema = z.object({
  title: z.string().min(3).max(100),
  content: z.string().min(10),
  tags: z.array(z.string()).max(5),
})

export async function createPost(data: unknown) {
  const parsed = CreatePostSchema.safeParse(data)
  if (!parsed.success) {
    return { error: parsed.error.flatten().fieldErrors }
  }

  const post = await db.insert(posts).values(parsed.data).returning()
  revalidatePath('/posts')
  return { success: true, post }
}
```

**In a form component:**
```tsx
'use client'
import { createPost } from './actions'
import { useFormState, useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  )
}

export function CreatePostForm() {
  const [state, formAction] = useFormState(createPost, {})

  return (
    <form action={formAction} className="space-y-4">
      <input name="title" placeholder="Title" className="input w-full" />
      <textarea name="content" placeholder="Content" className="input w-full min-h-[120px]" />
      <SubmitButton />
      {state.error && <p className="text-sm text-red-500">{state.error}</p>}
    </form>
  )
}
```

**Route Handlers (for external APIs or webhooks):**
```ts
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = headers().get('stripe-signature')

  try {
    const event = stripe.webhooks.constructEvent(
      body,
      signature!,
      process.env.STRIPE_WEBHOOK_SECRET!
    )

    if (event.type === 'checkout.session.completed') {
      const session = event.data.object
      await db.users.update({
        where: { stripeCustomerId: session.customer },
        data: { plan: 'pro' },
      })
    }

    return NextResponse.json({ received: true })
  } catch (err) {
    return NextResponse.json({ error: 'Webhook failed' }, { status: 400 })
  }
}
```

---

### Skill 9: Middleware Patterns

**What it is:** Edge middleware that intercepts every request before it reaches your app — used for auth checks, redirects, geolocation, A/B testing, and rate limiting.

**When to use:** Protecting routes, redirecting based on auth state, adding geo headers, token refresh.

**How to do it:**

**Auth protection:**
```ts
// middleware.ts (at project root)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session-token')?.value
  const isAuthPage = request.nextUrl.pathname.startsWith('/login')
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard')

  // If on login page with a token → redirect to dashboard
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // If on protected route without token → redirect to login
  if (isProtected && !token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Add geo headers for personalization
  const country = request.geo?.country
  const response = NextResponse.next()
  response.headers.set('x-geo-country', country || 'unknown')
  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/settings/:path*'],
}
```

**A/B testing:**
```ts
export function middleware(request: NextRequest) {
  const variant = request.cookies.get('ab-variant')?.value || Math.random() > 0.5 ? 'A' : 'B'
  const response = NextResponse.next()
  response.headers.set('x-ab-variant', variant)
  return response
}
```

**Rate limiting (with Upstash):**
```ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),  // 10 requests per 10 seconds
})

export async function middleware(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? 'anonymous'
  const { success } = await ratelimit.limit(ip)

  if (!success) {
    return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 })
  }

  return NextResponse.next()
}
```

---

### Skill 10: Error Boundaries and Loading States

**What it is:** Graceful handling of async errors and loading states at both the route level (error.tsx) and component level (Suspense fallback + try/catch).

**When to use:** Any async data fetch — wrap in try/catch or Suspense to prevent white-screen crashes.

**How to do it:**

**Route-level error boundary:**
```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-text-primary">Something went wrong</h2>
        <p className="text-text-secondary mt-2">{error.message}</p>
      </div>
      <button
        onClick={reset}
        className="rounded-lg bg-brand-500 px-4 py-2 text-white hover:bg-brand-600"
      >
        Try again
      </button>
    </div>
  )
}
```

**Route-level not-found:**
```tsx
// app/dashboard/not-found.tsx
export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 className="text-6xl font-bold text-brand-500">404</h1>
      <h2 className="text-2xl font-display mt-4">Page not found</h2>
      <a href="/" className="mt-6 text-brand-600 hover:underline">Go home</a>
    </div>
  )
}
```

**Component-level error handling:**
```tsx
async function UserProfile({ userId }: { userId: string }) {
  let user: User | null = null
  let posts: Post[] = []

  try {
    ;[user, posts] = await Promise.all([
      db.users.findUnique({ where: { id: userId } }),
      db.posts.findMany({ where: { authorId: userId } }),
    ])
  } catch (err) {
    // Log to error tracking service
    console.error('Failed to load user profile', err)
  }

  if (!user) {
    return <div>User not found</div>
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  )
}
```

**Loading states per component:**
```tsx
// Skeleton for a card list
function CardListSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {[1,2,3,4,5,6].map(i => (
        <div key={i} className="rounded-xl border border-border p-6 space-y-3">
          <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
          <div className="h-3 w-1/2 animate-pulse rounded bg-slate-100" />
          <div className="h-3 w-full animate-pulse rounded bg-slate-100" />
        </div>
      ))}
    </div>
  )
}
```

---

### Skill 11: Accessibility (ARIA, Keyboard Nav)

**What it is:** Making UIs navigable and understandable for all users — screen reader support, keyboard-only navigation, color contrast, focus management.

**When to use:** Every interactive element. Accessibility is not optional — it's a legal requirement and good UX.

**How to do it:**

**Focus management — visible focus ring:**
```css
/* Always-visible focus indicator */
:focus-visible {
  outline: 2px solid var(--color-brand-500);
  outline-offset: 2px;
  border-radius: 4px;
}

button, a, input, [tabindex]:not([tabindex="-1"]) {
  outline: none;  /* Remove default, replace with custom above */
}
```

**ARIA labels:**
```tsx
// Icon-only button needs a label
<button
  onClick={handleDelete}
  aria-label="Delete item"
  className="p-2 rounded hover:bg-slate-100"
>
  <TrashIcon className="h-4 w-4" />
</button>

// Loading state announcement
<div role="status" aria-live="polite">
  {isLoading ? 'Loading posts...' : `${posts.length} posts loaded`}
</div>

// Dropdown disclosure
<button aria-haspopup="listbox" aria-expanded={isOpen}>
  {value}
</button>
<nav id="main-nav" aria-label="Main navigation">
  {/* ...nav items */}
</nav>
```

**Keyboard navigation:**
```tsx
// Keyboard-accessible dropdown
function Dropdown({ options, value, onChange }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') setOpen(false)
          if (e.key === 'ArrowDown' && !open) setOpen(true)
        }}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        {value}
      </button>

      {open && (
        <ul role="listbox">
          {options.map(opt => (
            <li
              key={opt.id}
              role="option"
              aria-selected={opt.id === value}
              tabIndex={0}
              onClick={() => onChange(opt.id)}
              onKeyDown={(e) => e.key === 'Enter' && onChange(opt.id)}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

**Skip navigation link:**
```tsx
// First element in body — lets keyboard users skip to main content
export function SkipLink() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-brand-500 focus:text-white focus:rounded"
    >
      Skip to main content
    </a>
  )
}
```

**Color contrast:** All text must meet WCAG AA (4.5:1 for body, 3:1 for large text). Use `oklch` in Tailwind for perceptually correct contrast.

---

### Skill 12: Responsive Design Breakpoints

**What it is:** Designing layouts that adapt to screen sizes using Tailwind's breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`).

**When to use:** Every layout. Start mobile-first — design for small screens first, add complexity at larger breakpoints.

**How to do it:**

**Mobile-first breakpoints:**
```tsx
// Default = mobile (no prefix needed)
// sm = 640px, md = 768px, lg = 1024px, xl = 1280px, 2xl = 1536px

function ProductGrid({ products }: { products: Product[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {products.map(p => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  )
}

// Sidebar: stacked on mobile, side-by-side on desktop
function PageLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col md:flex-row">
      <aside className="w-full md:w-64 shrink-0">
        <Navigation />
      </aside>
      <main className="flex-1 min-w-0">
        {children}
      </main>
    </div>
  )
}
```

**Container queries (modern alternative):**
```css
/* Apply styles based on element width, not viewport */
@supports (container-type: inline-size) {
  .card-container {
    container-type: inline-size;
  }

  @container (min-width: 400px) {
    .card {
      grid-template-columns: auto 1fr;
    }
  }
}
```

**Fluid typography:**
```tsx
// CSS clamp — smooth scaling between min and max
<h1 className="text-[clamp(1.5rem,4vw,3rem)] leading-tight font-bold">
  Fluid Heading
</h1>

<p className="text-[clamp(0.875rem,0.8rem+0.5vw,1.125rem)] text-text-secondary">
  Responsive body text
</p>
```

**Hide/show based on breakpoint:**
```tsx
// Show on mobile only
<div className="md:hidden">Mobile menu button</div>

// Show on desktop only
<div className="hidden md:block">Desktop nav</div>
```

---

### Skill 13: CSS Animation Patterns

**What it is:** Transitions and animations that communicate state, guide attention, and create a polished feel — using Tailwind's built-in utilities and custom CSS for complex sequences.

**When to use:** Button interactions, page transitions, loading indicators, collapsible panels, skeleton pulses.

**How to do it:**

**Tailwind transition utilities:**
```tsx
<button className="
  px-4 py-2 rounded-lg
  bg-brand-500 text-white
  transition-all duration-200 ease-out
  hover:bg-brand-600 hover:scale-105 hover:shadow-lg
  active:scale-95
  focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2
  disabled:opacity-50 disabled:pointer-events-none
">
  Click me
</button>

// Fade in on mount
<div className="animate-in fade-in duration-300">
  Content fades in when rendered
</div>

// Slide in from right
<div className="animate-in slide-in-from-right-4 fade-in duration-300">
  Panel slides in from right
</div>
```

**Custom keyframe animations:**
```css
/* app/globals.css */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@layer utilities {
  .animate-shimmer {
    background: linear-gradient(
      90deg,
      transparent 0%,
      oklch(0.97 0 0) 50%,
      transparent 100%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
  }

  .animate-float {
    animation: float 3s ease-in-out infinite;
  }
}
```

**Staggered list animations:**
```tsx
function AnimatedList({ items }: { items: string[] }) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div
          key={item}
          className="animate-in fade-in slide-in-from-bottom-2"
          style={{ animationDelay: `${i * 50}ms`, animationFillMode: 'backwards' } as React.CSSProperties}
        >
          {item}
        </div>
      ))}
    </div>
  )
}
```

---

### Skill 14: Form Handling and Validation

**What it is:** Robust form submission with client-side validation (instant feedback) and server-side validation (security), using Zod for schema validation and react-hook-form for form state management.

**When to use:** Any form — signup, login, settings, checkout, contact.

**How to do it:**

**Zod schema (single source of truth):**
```ts
import { z } from 'zod'

export const SignupSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

type SignupInput = z.infer<typeof SignupSchema>
```

**react-hook-form + Zod:**
```tsx
'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { SignupSchema, type SignupInput } from '@/lib/validations'

export function SignupForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<SignupInput>({
    resolver: zodResolver(SignupSchema),
  })

  async function onSubmit(data: SignupInput) {
    const res = await fetch('/api/auth/signup', { method: 'POST', body: JSON.stringify(data) })

    if (!res.ok) {
      const { error } = await res.json()
      setError('email', { message: error })
      return
    }

    router.push('/dashboard')
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium mb-1">Name</label>
        <input id="name" {...register('name')} className="input w-full" />
        {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name.message}</p>}
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
        <input id="email" type="email" {...register('email')} className="input w-full" />
        {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-1">Password</label>
        <input id="password" type="password" {...register('password')} className="input w-full" />
        {errors.password && <p className="mt-1 text-sm text-red-500">{errors.password.message}</p>}
      </div>

      <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
        {isSubmitting ? 'Signing up...' : 'Sign Up'}
      </button>
    </form>
  )
}
```

**Server-side validation (same Zod schema):**
```ts
// app/api/auth/signup/route.ts
import { SignupSchema } from '@/lib/validations'

export async function POST(request: Request) {
  const body = await request.json()
  const parsed = SignupSchema.safeParse(body)

  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten().fieldErrors }, { status: 400 })
  }

  const user = await db.users.create({
    data: { name: parsed.data.name, email: parsed.data.email },
  })

  return NextResponse.json({ success: true }, { status: 201 })
}
```

---

### Skill 15: Deployment to Vercel (and alternatives)

**What it is:** Taking your Next.js app from local development to a production URL on Vercel (the native Next.js hosting platform) or alternatives like Netlify, Railway, and Fly.io.

**When to use:** When ready to ship — every feature branch gets a preview deployment, main branch gets production.

**How to do it:**

**Deploy to Vercel (recommended for Next.js):**
```bash
npm i -g vercel
vercel  # From project root

# Or push to GitHub — Vercel auto-detects Next.js and deploys
# Every PR gets a preview URL automatically
```

**Environment variables:**
```bash
vercel env add DATABASE_URL
vercel env add STRIPE_SECRET_KEY
vercel env add OPENAI_API_KEY
```

**vercel.json configuration:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

**Static export (for Netlify CDN):**
```ts
// next.config.ts — use only for fully static sites
const nextConfig: NextConfig = {
  output: 'export',
  images: { unoptimized: true },  // Required for static export
}
```
⚠️ Static export disables ISR, server-side rendering, and API routes. Only use for fully static sites.

**Netlify alternative (netlify.toml):**
```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

**Build optimizations:**
```ts
// next.config.ts — reduce bundle size
const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ['lucide-react', 'recharts', 'framer-motion'],
  },
  serverExternalPackages: ['@sparticuz/chromium'],
}
```

**Monitor Core Web Vitals in Vercel:**
- Vercel Analytics dashboard shows LCP, CLS, INP per page
- Add `<SpeedInsights />` from `@vercel/speed-insights` for real-user data

---

*Skills compiled from Next.js 15, React 19, Tailwind v4, and production patterns — April 2026.*