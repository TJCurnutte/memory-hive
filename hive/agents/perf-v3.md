# Web Performance — v3 (Web-Dev Agent)
> Last updated: 2026-04-22 | Maintainer: web-dev agent

---

## Table of Contents
1. [Core Web Vitals Overview](#1-core-web-vitals-overview)
2. [LCP — Largest Contentful Paint](#2-lcp--largest-contentful-paint)
3. [CLS — Cumulative Layout Shift](#3-cls--cumulative-layout-shift)
4. [INP — Interaction to Next Paint](#4-inp--interaction-to-next-paint)
5. [Bundle Analysis](#5-bundle-analysis)
6. [Image Optimization](#6-image-optimization)
7. [Caching Strategies](#7-caching-strategies)
8. [Code Splitting & Lazy Loading](#8-code-splitting--lazy-loading)
9. [Critical Rendering Path](#9-critical-rendering-path)
10. [Resource Hints](#10-resource-hints)
11. [Performance Monitoring](#11-performance-monitoring)
12. [Real-User Monitoring (RUM)](#12-real-user-monitoring-rum)
13. [Tools & Budgets](#13-tools--budgets)
14. [Resources & References](#14-resources--references)

---

## 1. Core Web Vitals Overview

### 1.1 What Are Core Web Vitals?
Core Web Vitals (CWV) are a set of specific metrics that Google uses to measure real-world user experience for page speed and visual stability. They are part of Google's page experience ranking signal.

### 1.2 The Three Pillars (2024+)

| Metric | What it measures | Good | Needs Improvement | Poor |
|--------|-----------------|------|-------------------|------|
| LCP | Loading performance | ≤2.5s | ≤4.0s | >4.0s |
| CLS | Visual stability | ≤0.1 | ≤0.25 | >0.25 |
| INP | Interactivity | ≤200ms | ≤500ms | >500ms |

Note: INP replaced FID (First Input Delay) in March 2024 as the official CWV. FID only measured the delay of the first interaction; INP measures all interactions throughout the page lifecycle.

### 1.3 Field vs Lab Data
- **Lab data**: measured in a controlled environment (Chrome DevTools, Lighthouse) — good for debugging
- **Field data (CrUX)**: real-user data collected from Chrome users in the wild — used for ranking
- Always use field data as the source of truth; use lab data for development feedback

---

## 2. LCP — Largest Contentful Paint

### 2.1 Definition
LCP measures when the largest image or text block visible in the viewport is rendered. It approximates when the main content is visible.

### 2.2 What Elements Can Be LCP?
- `<img>` elements
- `<svg>` with image children
- `<video>` poster images
- Background images via `url()` in CSS
- Block-level elements with text content
- Block-level elements with child `<img>` elements

### 2.3 LCP Thresholds
- **Good**: ≤2.5 seconds (75th percentile of page loads)
- **Needs improvement**: ≤4.0 seconds
- **Poor**: >4.0 seconds

### 2.4 How to Optimize LCP

**Priority #1: Identify your LCP element**
Use Chrome DevTools Performance panel or WebPageTest to identify the LCP element. Common culprits:
- Hero images
- Above-the-fold banners
- Large text blocks

**Strategy 1: Preload the LCP image**
```html
<!-- If LCP image is referenced in CSS -->
<link rel="preload" as="image" href="hero.webp" fetchpriority="high">

<!-- If LCP image is background-image -->
<link rel="preload" as="image" href="hero.webp" fetchpriority="high"
      media="(min-width: 800px)">
```

**Strategy 2: Use fetchpriority="high" on the img tag**
```html
<img src="hero.webp"
     alt="Hero image"
     width="1200" height="600"
     fetchpriority="high"
     loading="eager">
```

**Strategy 3: Serve optimized, properly sized images**
- Use WebP or AVIF
- Use `srcset` and `sizes` for responsive images
- Serve at actual rendered size (don't resize with CSS)
- Use a CDN with image transformation (Cloudflare Images, Cloudinary, imgix)

**Strategy 4: Reduce server response time**
- Use a CDN/edge network
- Enable HTTP/2 or HTTP/3
- Optimize server-side rendering
- Use edge caching

**Strategy 5: Eliminate render-blocking resources**
```html
<!-- Move non-critical CSS to async -->
<link rel="stylesheet" href="non-critical.css" media="print" onload="this.media='all'">

<!-- Or use preload + onload -->
<link rel="preload" href="non-critical.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

### 2.5 Common LCP Mistakes
- LCP image has `loading="lazy"` — never lazy load above-the-fold images
- LCP image is not preloaded
- LCP image loaded via JS after page load
- LCP image is too large (not compressed, wrong format)
- Third-party script (ads, chat widgets) blocks the LCP image

---

## 3. CLS — Cumulative Layout Shift

### 3.1 Definition
CLS measures the sum of all unexpected layout shifts that occur during the page lifecycle. A layout shift occurs when a visible element changes its start position between frames.

### 3.2 CLS Thresholds
- **Good**: ≤0.1
- **Needs improvement**: ≤0.25
- **Poor**: >0.25

### 3.3 Layout Shift Score Formula
```
Layout Shift Score = impact fraction × distance fraction
```
- **Impact fraction**: the fraction of the viewport affected
- **Distance fraction**: the distance moved as a fraction of the viewport

### 3.4 What Causes CLS?

**#1: Images without dimensions**
```html
<!-- WRONG: causes layout shift when image loads -->
<img src="photo.jpg" alt="Photo">

<!-- RIGHT: reserve space with width/height attributes -->
<img src="photo.jpg" alt="Photo" width="800" height="600">
<!-- Browser calculates aspect ratio from w/h, reserving space before image downloads -->
```

**#2: Ads, embeds, and iframes without dimensions**
```html
<!-- Reserve space for ads -->
<div style="min-height: 250px;">
  <iframe src="ad.html" width="300" height="250"></iframe>
</div>

<!-- For dynamic content, use CSS aspect-ratio -->
<div style="aspect-ratio: 16 / 9;">
  <iframe src="video.html"></iframe>
</div>
```

**#3: Late-loading web fonts (FOIT/FOUT)**
```css
/* Prevent FOUT with font-display */
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/myfont.woff2') format('woff2');
  font-display: swap;
  ascent-override: 90%;
  descent-override: 25%;
  line-gap-override: 0%;
  size-adjust: 107%;
}

/* Using Google Fonts with preconnect */
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Font&display=swap">
```

**#4: Dynamically injected content**
- Don't insert content above existing content
- Don't push down existing content with notifications, banners, modals
- Reserve space for dynamically loaded components

**#5: Animations that use layout properties**
```css
/* WRONG: animating height causes layout shifts */
.panel.expanded {
  height: 500px; /* causes layout shift */
}

/* RIGHT: use transforms and opacity for animations */
.panel {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.panel.expanded {
  max-height: 500px;
}
```

**#6: CSS `transform` vs layout properties**
```css
/* Prefer (GPU-accelerated, no layout): */
transform: translateX(100px);
transform: scale(1.1);
opacity: 0.5;

/* Avoid (cause layout): */
width, height, margin, padding, top, left, right, bottom, border-width
```

---

## 4. INP — Interaction to Next Paint

### 4.1 Definition
INP measures the latency from when a user interacts (click, tap, keyboard) to when the next frame is painted. It is the 98th percentile interaction latency across all interactions on a page.

### 4.2 INP Thresholds
- **Good**: ≤200ms
- **Needs improvement**: ≤500ms
- **Poor**: >500ms

### 4.3 INP vs FID
| Aspect | FID | INP |
|--------|-----|-----|
| Measures | First interaction delay | All interactions |
| Metric type | Input delay only | Total blocking time |
| When updated | First interaction only | 98th percentile, all interactions |

### 4.4 INP Breakdown
INP = Input Delay + Processing Time + Presentation Delay

**Input Delay**: Time from user interaction to when event handler starts executing
- Causes: long tasks, main thread blocking
- Solutions: break up long tasks with `requestIdleCallback`, defer non-critical work

**Processing Time**: Time to execute event handlers
- Causes: heavy JS in event handlers
- Solutions: optimize event handlers, use Web Workers for heavy computation

**Presentation Delay**: Time to render the result
- Causes: large DOM updates, forced reflows
- Solutions: batch DOM updates, use CSS containment

### 4.5 How to Optimize INP

**Break up long tasks:**
```javascript
// WRONG: One long task blocking the main thread
function processItems(items) {
  items.forEach(item => heavyProcessing(item));
}

// RIGHT: Break into chunks using scheduler.yield
async function processItems(items) {
  for (const item of items) {
    heavyProcessing(item);
    if ('scheduler' in window) {
      await window.scheduler.yield();
    } else {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
  }
}
```

**Defer non-critical JS:**
```html
<script src="analytics.js" defer></script>
<script src="chat-widget.js" defer></script>
```

**Use Web Workers for heavy computation:**
```javascript
// worker.js
self.addEventListener('message', ({ data }) => {
  const result = heavyComputation(data);
  self.postMessage(result);
});

// main.js
const worker = new Worker('worker.js');
worker.postMessage(largeDataset);
worker.onmessage = ({ data }) => updateUI(data.result);
```

**Avoid forced reflows:**
```javascript
// WRONG: multiple forced reflows
element.style.height = '100px';
const height = element.offsetHeight; // forces reflow
element.style.width = '200px';
const width = element.offsetWidth; // forces reflow

// RIGHT: batch reads and writes
element.style.height = '100px';
element.style.width = '200px';
const computed = window.getComputedStyle(element); // single reflow
```

**Use CSS contain:**
```css
.widget {
  contain: layout style paint;
}
```

---

## 5. Bundle Analysis

### 5.1 Tools

| Tool | Type | What it does |
|------|------|-------------|
| [webpack-bundle-analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer) | Webpack | Visual treemap of bundle contents |
| [rollup-plugin-visualizer](https://github.com/btd/rollup-plugin-visualizer) | Rollup/Vite | Visual stats for rollup bundles |
| [source-map-explorer](https://github.com/danvk/source-map-explorer) | Any | Treemap from source maps |
| [esbuild --bundle=true --metafile](https://esbuild.github.io/api/) | esbuild | Built-in bundle analysis |
| [Bundlephobia](https://bundlephobia.com/) | Online | npm package size lookup |
| [Import Cost](https://marketplace.visualstudio.com/items?itemName=wkandfolder.import-cost) | VS Code | Inline bundle size in editor |

### 5.2 Bundle Budgets
```javascript
// Next.js: next.config.js
module.exports = {
  compiler: {
    bundleAnalyzerReport: { analyzerMode: 'static', reportFilename: 'bundle-report.html' }
  }
};
```

```json
// package.json budgets
{
  "budgets": [
    { "type": "initial", "maximumWarning": "500kb", "maximumError": "1mb" },
    { "type": "anyComponent", "maximumWarning": "100kb", "maximumError": "200kb" }
  ]
}
```

### 5.3 Reducing Bundle Size

**Tree shaking:**
- Use ES modules (import/export), not CommonJS (require)
- Use `sideEffects: false` in package.json
- Use named exports instead of barrel exports where possible
```javascript
// BAD: barrel export pulls in everything
export { Button } from './Button';
export { Card } from './Card';

// GOOD: direct import (or re-export only what you need)
import { Button } from './Button';
```

**Dynamic imports for route-based splitting:**
```javascript
// Lazy load route components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
```

**Analyze and replace heavy dependencies:**
- Replace `moment.js` (67kb gzipped) with `date-fns` (2.9kb) or `dayjs` (2kb)
- Replace `lodash` with `lodash-es` + specific imports
```javascript
// Instead of:
import _ from 'lodash'; // full lodash

// Do:
import sortBy from 'lodash-es/sortBy';
import debounce from 'lodash-es/debounce';
```

---

## 6. Image Optimization

### 6.1 Modern Image Formats

| Format | Compression | Transparency | Browser Support | Best for |
|--------|-------------|--------------|----------------|---------|
| AVIF | Best | Yes | Chrome 85+, Safari 16+ | Photos, complex graphics |
| WebP | 30% smaller than JPEG | Yes | Chrome 17+, Safari 14+ | General purpose |
| JPEG | Baseline | No | All | Photos |
| PNG | Lossless | Yes | All | Icons, screenshots, graphics with text |
| SVG | Vector | Yes | All | Icons, logos, illustrations |
| GIF | Limited | No | All | Simple animations |

### 6.2 Responsive Images
```html
<img src="image-800.jpg"
     srcset="image-400.jpg 400w,
             image-800.jpg 800w,
             image-1600.jpg 1600w"
     sizes="(max-width: 600px) 400px,
            (max-width: 1200px) 800px,
            1600px"
     alt="Description"
     width="800"
     height="600">
```

### 6.3 Art Direction (picture element)
```html
<picture>
  <source media="(min-width: 800px)"
          srcset="hero-wide.avif"
          type="image/avif">
  <source media="(min-width: 800px)"
          srcset="hero-wide.webp"
          type="image/webp">
  <img src="hero-narrow.jpg"
       alt="Hero image"
       width="800" height="600"
       loading="eager"
       fetchpriority="high">
</picture>
```

### 6.4 AVIF: The New Standard
AVIF typically achieves 50% smaller file sizes than JPEG at equivalent quality.
```html
<picture>
  <source srcset="photo.avif" type="image/avif">
  <source srcset="photo.webp" type="image/webp">
  <img src="photo.jpg" alt="Photo" width="800" height="600">
</picture>
```

### 6.5 Lazy Loading Images
```html
<!-- Native lazy loading -->
<img src="below-fold.jpg" loading="lazy" alt="Below fold image">

<!-- For above-the-fold LCP images: NEVER lazy load -->
<img src="hero.jpg" loading="eager" fetchpriority="high" alt="Hero">
```

### 6.6 Image CDNs
- Cloudflare Images: `images.cloudflare.com`
- Cloudinary: `res.cloudinary.com`
- imgix: `*.imgix.net`
- Bunny Optimizer: automatic format/quality optimization

### 6.7 Decoding Attribute
```html
<!-- Hint to browser to decode images off the main thread -->
<img src="photo.jpg" decoding="async" alt="Photo">

<!-- Use decoding="sync" only for the LCP image to prioritize it -->
```

---

## 7. Caching Strategies

### 7.1 HTTP Caching Headers

| Header | What it does | Typical use |
|--------|-------------|-------------|
| Cache-Control: max-age | Time in seconds before cached copy expires | Static assets |
| Cache-Control: no-cache | Must revalidate with server before use | Dynamic content |
| Cache-Control: no-store | Never cache | Sensitive data |
| Cache-Control: immutable | Content never changes | Hashed assets |
| ETag | Server-side validation token | Conditional requests |
| Last-Modified | Timestamp for conditional requests | Last-modified validation |

### 7.2 Cache Strategies

**Strategy 1: Cache-first (immutable)**
Best for: static assets, fonts, icons
```
Cache-Control: public, max-age=31536000, immutable
```
For hashed assets, the URL changes on each deploy, so aggressive caching is safe.

**Strategy 2: Stale-while-revalidate**
Best for: API responses that change occasionally
```
Cache-Control: public, max-age=60, stale-while-revalidate=600
```
Serve cached content for 60s, then serve stale while revalidating in background.

**Strategy 3: Network-first**
Best for: frequently changing content, user-specific data
```
Cache-Control: no-cache
```
Always try network first, fall back to cache if offline.

### 7.3 Service Worker Caching (Workbox)
```javascript
// sw.js
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate, CacheFirst } from 'workbox-strategies';

// Precache app shell
precacheAndRoute(self.__WB_MANIFEST);

// Cache-first for images
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'image-cache' })
);

// Stale-while-revalidate for API
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new StaleWhileRevalidate({ cacheName: 'api-cache' })
);
```

### 7.4 Cache-Busting with Content Hashing
Modern bundlers hash file content into the filename:
```
main.a3f2b1c4.js   → hashed, cacheable forever
vendor.d5e6f7g8.js → changed only when content changes
```
Deploys get new filenames automatically — no manual cache busting needed.

---

## 8. Code Splitting & Lazy Loading

### 8.1 Route-Based Splitting (React example)
```javascript
import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/dashboard', element: <Dashboard /> },
  { path: '/settings', element: <Settings /> },
]);

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
```

### 8.2 Preload vs Prefetch
```html
<!-- Preload: high priority, current navigation -->
<link rel="preload" as="script" href="critical.js">

<!-- Prefetch: lower priority, future navigation -->
<link rel="prefetch" href="next-page.js">
```

---

## 9. Critical Rendering Path

### 9.1 The Critical Rendering Path
1. Parse HTML → build DOM
2. Parse CSS → build CSSOM
3. Combine DOM + CSSOM → Render Tree
4. Layout (reflow) — calculate positions
5. Paint — pixels to layers
6. Composite — layer composition to screen

### 9.2 Critical CSS Inlining
```html
<head>
  <style>
    /* Critical CSS only — what's needed for above-the-fold */
    body { margin: 0; font-family: system-ui; }
    .hero { min-height: 100vh; display: flex; align-items: center; }
    .nav { position: sticky; top: 0; }
  </style>
  <!-- Non-critical CSS loaded async -->
  <link rel="stylesheet" href="non-critical.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="non-critical.css"></noscript>
</head>
```

---

## 10. Resource Hints

### 10.1 Preload
```html
<link rel="preload" as="script" href="critical.js">
<link rel="preload" as="style" href="critical.css">
<link rel="preload" as="image" href="hero.avif" fetchpriority="high">
<link rel="preload" as="font" href="font.woff2" type="font/woff2" crossorigin>
```

### 10.2 Prefetch
```html
<link rel="prefetch" href="/next-page.js" as="script">
<link rel="prefetch" href="/api/data.json" as="fetch">
```

### 10.3 Preconnect
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.example.com">
```
Note: `preconnect` is preferred when available; `dns-prefetch` is the fallback for browsers that don't support `preconnect`.

---

## 11. Performance Monitoring

### 11.1 Chrome DevTools

**Performance panel:**
- Record a page load or interaction
- Look for: long tasks (>50ms on main thread), forced reflows, excessive paint times
- Check flame chart for heavy JS

**Network panel:**
- Waterfall chart shows resource loading sequence
- Look for: render-blocking resources, large payloads, lack of compression
- Use "Coverage" tab to find unused CSS/JS

**Lighthouse:**
- Run from DevTools or `npx lighthouse https://example.com`
- Scores: Performance, Accessibility, Best Practices, SEO

### 11.2 WebPageTest
- [webpagetest.org](https://webpagetest.org) — free, detailed waterfall + filmstrip
- Waterfall view, request details, resource breakdown
- Filmstrip view for visual loading progression
- Compare across locations, browsers, connection speeds

### 11.3 Performance API
```javascript
// Measure LCP with PerformanceObserver
const observer = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.startTime);
});
observer.observe({ type: 'largest-contentful-paint', buffered: true });

// Measure CLS
let clsValue = 0;
const clsObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) clsValue += entry.value;
  }
});
clsObserver.observe({ type: 'layout-shift', buffered: true });

// Measure INP
let inpValue = 0;
const inpObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    inpValue = Math.max(inpValue || 0, entry.duration);
  }
});
inpObserver.observe({ type: 'event', buffered: true });
```

---

## 12. Real-User Monitoring (RUM)

### 12.1 CrUX (Chrome User Experience Report)
- Source: [PageSpeed Insights](https://pagespeed.web.dev/), [CrUX Dashboard](https://crux.tech/)
- Data: field performance from Chrome users
- Used for: Google ranking signals, benchmarking

### 12.2 web-vitals Library
```javascript
import { onLCP, onCLS, onINP } from 'web-vitals';

onLCP(metric => sendToAnalytics('LCP', metric));
onCLS(metric => sendToAnalytics('CLS', metric));
onINP(metric => sendToAnalytics('INP', metric));
```

**RUM Providers:**
- **Datadog RUM**: real-user monitoring with session replay
- **Sentry**: performance monitoring + error tracking
- **New Relic**: APM + RUM
- **SpeedCurve**: synthetic + RUM combined

---

## 13. Tools & Budgets

### 13.1 Toolchain Summary

| Category | Tools |
|----------|-------|
| Bundle analysis | webpack-bundle-analyzer, rollup-plugin-visualizer, source-map-explorer |
| Image optimization | Squoosh, Sharp, Cloudinary, imgix, cwebp |
| Code splitting | Webpack, Rollup, Vite, esbuild |
| Performance testing | Lighthouse CI, WebPageTest, PageSpeed Insights |
| RUM | web-vitals, Datadog, SpeedCurve |
| CI integration | Lighthouse CI (GitHub Actions), Calibre, DebugBear |

### 13.2 Lighthouse CI
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse
on: [push, pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx @lhci/cli autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

### 13.3 Performance Budget (package.json)
```json
{
  "lighthouse": {
    "budgets": [
      {
        "resourceType": "initial",
        "resourceSizes": [{ "type": "total", "budget": 300 }]
      },
      {
        "resourceType": "script",
        "resourceSizes": [{ "type": "total", "budget": 150 }]
      }
    ]
  }
}
```

---

## 14. Resources & References

### Core Web Vitals
- [web.dev Core Web Vitals](https://web.dev/articles/vitals)
- [web.dev LCP](https://web.dev/articles/optimize-lcp)
- [web.dev CLS](https://web.dev/articles/optimize-cls)
- [web.dev INP](https://web.dev/articles/inp)
- [Chrome Speed Metrics](https://developer.chrome.com/docs/pagespeed-web-vitals/)

### Tools
- [WebPageTest](https://webpagetest.org)
- [Squoosh](https://squoosh.app)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse/)
- [Bundlephobia](https://bundlephobia.com)
- [Workbox](https://developer.chrome.com/docs/workbox/)

### Image Formats
- [AVIF Browser Support (caniuse)](https://caniuse.com/avif)
- [Squoosh CLI](https://github.com/GoogleChrome/squoosh/tree/main/cli)
- [Sharp (Node.js image processing)](https://sharp.pixelenovely.com/)

---

*End of perf-v3.md*
