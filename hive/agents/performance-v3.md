# Web Performance Engineering — Deep Research
## Coder Agent — Performance Engineering (v3)

> Research date: 2026-04-22 | Focus: Frontend performance, Core Web Vitals, bundle optimization

---

## Table of Contents
1. [Web Performance Landscape 2026](#1-web-performance-landscape-2026)
2. [Core Web Vitals Deep Dive](#2-core-web-vitals-deep-dive)
3. [React Performance](#3-react-performance)
4. [Bundle Size Optimization](#4-bundle-size-optimization)
5. [Lighthouse CI & Monitoring](#5-lighthouse-ci--monitoring)
6. [Advanced Performance Patterns](#6-advanced-performance-patterns)
7. [Performance Budgets & Culture](#7-performance-budgets--culture)
8. [References](#8-references)

---


<a name="1-web-performance-landscape-2026"></a>
## 1. Web Performance Landscape 2026

### 1.1 Why Performance Still Matters (More Than Ever)

Performance is a feature, a competitive advantage, and a user right. Key statistics that drive this home:

- **Every 100ms of latency costs 1% of revenue** (Amazon, Walmart studies)
- **53% of mobile users abandon sites taking over 3 seconds to load** (Google)
- **A 1-second improvement in mobile page load time increases conversions by up to 27%** (Google)
- **Core Web Vitals are ranking signals** — poor performance directly impacts SEO

### 1.2 The 2026 Performance Stack

**Frontend Bundlers**:
- **Vite** has become the default for new projects — native ESM, fast HMR, Rollup-based production builds
- **esbuild** / **swc** as fast JS transformers (5-20x faster than Babel)
- **Rollup** / **Webpack 5** still used for complex applications
- **Turbopack** (Vercel) gaining traction for Next.js projects
- **Parcel 2** for zero-config performance

**Runtime Performance**:
- React 18+ with automatic batching, concurrent rendering
- Solid.js and Svelte for reactive frameworks with no virtual DOM overhead
- View Transitions API for smooth page transitions
- Speculation Rules API for prefetching next pages

**Performance Monitoring**:
- Chrome User Experience Report (CrUX) — real user data
- Lighthouse CI — automated performance audits
- WebPageTest — detailed waterfall analysis
- Core Web Vitals from various vendors

### 1.3 The Performance Budget

A performance budget is a set of constraints imposed on metrics that affect site performance. It includes:

1. **Quantity budgets**: Limit total resources
   - JavaScript: max 200KB gzipped (or tighter for mobile)
   - CSS: max 50KB gzipped
   - Images: lazy-load above-the-fold
   - Total page weight: max 1.5MB initial load

2. **Timing budgets**: Limit critical path performance
   - FCP: < 1.8s (Good)
   - LCP: < 2.5s (Good)
   - INP: < 200ms (Good)
   - CLS: < 0.1 (Good)
   - TTFB: < 800ms

3. **Score budgets**: Lighthouse score must remain above 90/100

---

<a name="2-core-web-vitals-deep-dive"></a>
## 2. Core Web Vitals Deep Dive

Google's Core Web Vitals are a set of specific factors that measure real-world user experience. They became Google ranking signals in 2021 and remain critical in 2026.

### 2.1 LCP — Largest Contentful Paint

**What it measures**: Time from page start to the largest content element visible in the viewport becoming rendered.

**Target**: < 2.5 seconds (Good), 2.5-4.0s (Needs Improvement), > 4.0s (Poor)

**What's measured**: `<img>`, `<image>` inside `<svg>`, `<video>`, elements with `background-image`, block-level text elements

**How to optimize LCP**:

```html
<!-- Preload your LCP image -->
<link rel="preload" href="/hero-image.webp" as="image">
<!-- Or with fetchpriority -->
<img src="/hero-image.webp" fetchpriority="high" alt="Hero">

<!-- CSS to prevent render blocking -->
<style>
  /* Critical CSS inline, rest async */
  .hero { /* critical styles */ }
</style>
<link rel="preload" href="/full-styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

```javascript
// Measure LCP with PerformanceObserver
const observer = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.startTime);
  
  // Report to analytics
  sendToAnalytics('lcp', lastEntry.startTime);
});

observer.observe({ type: 'largest-contentful-paint', buffered: true });
```

**Common LCP causes and fixes**:
1. **Slow server response (TTFB)**: Optimize TTFB first — use CDN, caching, edge workers
2. **Render-blocking resources**: Inline critical CSS, defer non-critical JS
3. **Slow image load**: Preload LCP image, use WebP/AVIF, use proper sizing
4. **Client-side rendering delays**: Use SSR/SSG for content-heavy pages

### 2.2 INP — Interaction to Next Paint (replaced FID in 2024)

**What it measures**: Time from user interaction (click, tap, keypress) to the next frame being painted. Measures responsiveness throughout the page lifetime.

**Target**: < 200ms (Good), 200-500ms (Needs Improvement), > 500ms (Poor)

**Important**: INP measures all interactions, not just the first. A slow button click 30 seconds into the session counts.

**How to measure**:

```javascript
// Use web-vitals library
import { onINP } from 'web-vitals';

onINP(({ value, entries }) => {
  const inp = value; // in ms
  const event = entries[entries.length - 1];
  console.log('INP:', inp, 'Interaction:', event.name);
});
```

**How to optimize INP**:

1. **Break up long tasks** (Long Tasks > 50ms)
```javascript
// BAD: One big task
function processData(data) {
  data.forEach(item => {
    heavyComputation(item);
  });
}

// GOOD: Yield to main thread periodically
async function processData(data) {
  const CHUNK_SIZE = 50;
  
  for (let i = 0; i < data.length; i += CHUNK_SIZE) {
    const chunk = data.slice(i, i + CHUNK_SIZE);
    chunk.forEach(item => heavyComputation(item));
    
    // Yield to allow browser to process other tasks
    await scheduler.yield();
  }
}

// Or use requestIdleCallback
function processInBackground(data) {
  const chunks = chunkArray(data, 50);
  
  function processNextChunk(index) {
    if (index >= chunks.length) return;
    
    chunks[index].forEach(item => heavyComputation(item));
    
    requestIdleCallback(() => processNextChunk(index + 1));
  }
  
  processNextChunk(0);
}
```

2. **Reduce main thread work**
```javascript
// Defer expensive operations
function onClick() {
  // Show immediate feedback
  button.classList.add('loading');
  
  // Defer heavy work to next frame
  requestAnimationFrame(() => {
    heavyComputation();
    button.classList.remove('loading');
  });
}
```

3. **Use web workers for non-UI work**
```javascript
// worker.js
self.onmessage = ({ data }) => {
  const result = expensiveDataProcessing(data);
  self.postMessage(result);
};

// main.js
const worker = new Worker('worker.js');
worker.postMessage(data);
worker.onmessage = ({ data }) => {
  updateUI(data);
};
```

### 2.3 CLS — Cumulative Layout Shift

**What it measures**: Cumulative score of all unexpected layout shifts that occur during the page's lifespan.

**Target**: < 0.1 (Good), 0.1-0.25 (Needs Improvement), > 0.25 (Poor)

**What causes CLS**:
1. Images without dimensions
2. Ads and embeds without reserved space
3. Dynamic content injected above existing content
4. Web fonts causing FOUT (Flash of Unstyled Text) / FOIT (Flash of Invisible Text)

**How to prevent CLS**:

```html
<!-- Always include width and height on images -->
<img src="photo.jpg" width="800" height="600" alt="...">
<!-- Modern browsers automatically compute aspect ratio -->

<!-- Reserve space for dynamic content -->
<div style="min-height: 200px;" id="dynamic-banner">
  <!-- Placeholder with exact dimensions -->
</div>
```

```css
/* Reserve space for dynamically loaded content */
.ad-container {
  min-height: 250px; /* or aspect-ratio */
  contain: layout;
}

/* Font loading to minimize FOUT */
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/myfont.woff2') format('woff2');
  font-display: optional; /* or swap for better UX */
}

/* Use font-display: swap for faster text appearance */
/* Use font-display: optional for zero CLS risk */
```

```javascript
// For dynamic content, animate height changes
function showBanner() {
  const banner = document.getElementById('banner');
  banner.style.transition = 'height 0.3s ease-out';
  banner.style.height = '200px'; // Animate to prevent jarring shift
}

// Better: pre-calculate and reserve space
async function loadDynamicContent() {
  const size = await predictContentSize();
  document.getElementById('placeholder').style.height = size + 'px';
}
```

### 2.4 TTFB — Time to First Byte

**Target**: < 800ms (Good), 800-1800ms (Needs Improvement), > 1800ms (Poor)

**How to improve TTFB**:
1. Use a CDN with edge servers close to users
2. Enable caching (Cache-Control, ETag, Last-Modified)
3. Optimize database queries
4. Use server-side rendering for faster initial response
5. Consider edge computing for dynamic content

```javascript
// Example: Edge-side caching with service worker
const CACHE_NAME = 'v1';
const STATIC_ASSETS = [
  '/',
  '/styles.css',
  '/app.js'
];

self.addEventListener('fetch', (event) => {
  // Serve from cache if available
  if (event.request.method === 'GET') {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) {
          // Return cached, but also update cache in background
          fetch(event.request).then(response => {
            if (response.ok) {
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, response);
              });
            }
          });
          return cached;
        }
        
        // Not in cache, fetch and cache
        return fetch(event.request).then(response => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        });
      })
    );
  }
});
```

---

<a name="3-react-performance"></a>
## 3. React Performance

### 3.1 When to Use memo, useMemo, and useCallback

These are the most commonly misunderstood React optimizations. The key insight: they add overhead that is only worth it when the component/prop/value is genuinely expensive to recreate.

**React.memo**:

```jsx
// Without memo - rerenders on every parent render
const Button = ({ onClick, label }) => {
  console.log('Button rendered');
  return <button onClick={onClick}>{label}</button>;
};

// With memo - only rerenders when props change
const Button = React.memo(({ onClick, label }) => {
  console.log('Button rendered');
  return <button onClick={onClick}>{label}</button>;
});

// Custom comparison function (use rarely - the default is usually fine)
const ComplexButton = React.memo(({ onClick, label, icon }) => {
  return <button onClick={onClick}>
    {icon}{label}
  </button>;
}, (prevProps, nextProps) => {
  // Only re-render if label changed (ignore onClick reference changes)
  return prevProps.label === nextProps.label;
});
```

**When to use React.memo**:
- Component renders frequently with same props
- Component is expensive to render (complex calculations, deep DOM)
- Component is often wrapped with different prop values

**When NOT to use React.memo**:
- Component is cheap to render
- Component will almost always receive new props anyway (like functions from parent)
- You don't have a measurable performance problem

**useMemo**:

```jsx
// Expensive calculation - memoize it
const ExpensiveList = ({ items, filter }) => {
  // Only recomputes when items or filter changes
  const filteredItems = useMemo(() => {
    return items.filter(item => item.name.includes(filter));
  }, [items, filter]);
  
  return <List items={filteredItems} />;
};

// Stable object reference for prop comparison
const options = useMemo(() => ({
  enableSearch: true,
  maxResults: 100,
  sortOrder: 'desc'
}), []); // Empty deps = never changes

<ListComponent options={options} />
```

**When to use useMemo**:
- Expensive calculations (sorting, filtering, complex math)
- Creating object/array references that are passed to memoized children
- Expensive derived state computations

**When NOT to use useMemo**:
- Trivial calculations (adding numbers, string concatenation)
- The memoized value is only used once
- You don't have a measurable performance problem

**useCallback**:

```jsx
// Without useCallback - new function every render
const Parent = () => {
  const handleClick = () => console.log('clicked');
  return <Button onClick={handleClick} />;
};

// With useCallback - stable function reference
const Parent = () => {
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []); // No dependencies = never changes
  
  return <Button onClick={handleClick} />;
};

// With dependencies
const Parent = ({ userId }) => {
  const handleClick = useCallback(() => {
    console.log('clicked by', userId);
  }, [userId]); // Changes when userId changes
  
  return <Button onClick={handleClick} />;
};
```

**When to use useCallback**:
- Function passed to a memoized component as a prop
- Function used in useEffect dependencies
- Function used in a dependency array of another useCallback

**When NOT to use useCallback**:
- Function only used inside the same component's JSX
- Function is cheap and you don't have a performance problem

### 3.2 Code Splitting and Lazy Loading

```jsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));
const SettingsPage = lazy(() => import('./SettingsPage'));
const AdminPanel = lazy(() => import('./AdminPanel'));

// Route-level code splitting
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      {/* These won't load until navigated to */}
      <Route path="/settings" element={
        <Suspense fallback={<LoadingSpinner />}>
          <SettingsPage />
        </Suspense>
      } />
    </Routes>
  );
}

// Component-level splitting
function Dashboard() {
  const [showChart, setShowChart] = useState(false);
  
  // Only load chart when needed
  const Chart = useMemo(() => 
    lazy(() => import('./Chart')), 
    []
  );
  
  return (
    <>
      <MainContent />
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <Chart />
        </Suspense>
      )}
    </>
  );
}
```

### 3.3 Concurrent Features in React 18+

React 18's concurrent features enable better UX, but require careful implementation to avoid performance issues.

**useTransition for non-urgent updates**:

```jsx
import { useState, useTransition } from 'react';

function SearchApp() {
  const [query, setQuery] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [isPending, startTransition] = useTransition();
  
  const handleChange = (e) => {
    const value = e.target.value;
    setInputValue(value); // Urgent - update input immediately
    
    // Mark this as non-urgent - can be interrupted
    startTransition(() => {
      setQuery(value); // Non-urgent - filtering can wait
    });
  };
  
  return (
    <div>
      <input value={inputValue} onChange={handleChange} />
      {isPending ? <Spinner /> : <Results query={query} />}
    </div>
  );
}
```

**useDeferredValue for deferred values**:

```jsx
import { useState, useDeferredValue } from 'react';

function SearchResults({ query }) {
  // Deferred version can lag behind for non-urgent updates
  const deferredQuery = useDeferredValue(query);
  
  const results = useMemo(() => {
    return searchItems(deferredQuery);
  }, [deferredQuery]);
  
  const isStale = query !== deferredQuery;
  
  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      {results.map(item => <ResultItem key={item.id} item={item} />)}
    </div>
  );
}
```

**Suspense for data fetching**:

```jsx
import { Suspense } from 'react';

// Component that suspends while loading
function UserProfile({ userId }) {
  const user = useUser(userId); // Suspends if not ready
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary fallback={<Error />}>
      <Suspense fallback={<ProfileSkeleton />}>
        <UserProfile userId={123} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### 3.4 Virtualization for Large Lists

```jsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualizedList({ items }) {
  const parentRef = useRef(null);
  
  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Estimated row height
    overscan: 5, // Render extra rows above/below viewport
  });
  
  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{
        height: `${rowVirtualizer.getTotalSize()}px`,
        width: '100%',
        position: 'relative',
      }}>
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: virtualRow.start,
              height: `${virtualRow.size}px`,
              width: '100%',
            }}
          >
            <ListItem item={items[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

<a name="4-bundle-size-optimization"></a>
## 4. Bundle Size Optimization

### 4.1 Analyzing Your Bundle

```bash
# Analyze with webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/stats.json

# Or use source-map-explorer
npx source-map-explorer dist/*.js

# With Vite
import { visualizer } from 'rollup-plugin-visualizer';
// Add to vite.config.js plugins

# Quick bundle check
npx bundlephobia-cli react
npx bundlephobia-cli lodash
```

### 4.2 Tree Shaking

Tree shaking removes unused code from your bundle. It works with ES modules (import/export) but not CommonJS.

```javascript
// webpack.config.js - Enable tree shaking
module.exports = {
  mode: 'production', // Tree shaking only works in production
  optimization: {
    usedExports: true,    // Mark unused exports
    sideEffects: true,    // Enable side effects analysis
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', { modules: false }] // Don't transform ESM
            ]
          }
        }
      }
    ]
  }
};
```

**package.json side effects**:

```json
{
  "sideEffects": [
    "*.css",
    "./side-effect-file.js"
  ]
}
```

If `sideEffects: false`, webpack assumes all exports are pure and can be tree-shaken. Only mark files as having side effects if they really do.

### 4.3 Import Strategies

**Don't import entire libraries when you only need a piece**:

```javascript
// BAD - imports entire lodash (70KB+)
import _ from 'lodash';
const sorted = _.sortBy(items, 'name');

// GOOD - imports only sortBy (2KB)
import sortBy from 'lodash/sortBy';
const sorted = sortBy(items, 'name');

// BETTER - imports only sortBy, tree-shakes more
import { sortBy } from 'lodash';
const sorted = sortBy(items, 'name');

// BEST (if available) - native alternatives
const sorted = [...items].sort((a, b) => a.name.localeCompare(b.name));

// For utility libraries, consider lighter alternatives:
// - date-fns (tree-shakeable) instead of moment (200KB) or date-fns-lite
// - lodash-es (ES modules) instead of lodash (CommonJS)
// - You-don't-need lodash - use native JS
```

### 4.4 Code Splitting Strategies

**Route-based splitting** (most common):

```javascript
// Vite / React Router example
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));
```

**Component-based splitting**:

```javascript
// Split heavy components
const RichTextEditor = lazy(() => import('./components/RichTextEditor'));
const DataTable = lazy(() => import('./components/DataTable'));

// Split based on user permission
const AdminPanel = lazy(() => import(/* webpackChunkName: "admin" */ './Admin'));
const ViewerPanel = lazy(() => import(/* webpackChunkName: "viewer" */ './Viewer'));
```

**Dynamic imports for features**:

```javascript
// Only load charting library when needed
async function loadChart(data) {
  const { Chart, ChartData } = await import('./libs/chart.js');
  return new Chart(data);
}

// Only load PDF library when user clicks export
document.getElementById('export-pdf').addEventListener('click', async () => {
  const { exportToPdf } = await import('./utils/pdf-export.js');
  await exportToPdf(reportData);
});
```

### 4.5 Preloading and Prefetching

```html
<!-- Prefetch for future navigation -->
<link rel="prefetch" href="/settings.js" as="script">
<!-- Preload for current navigation -->
<link rel="preload" href="/critical.js" as="script">

<!-- Preload critical font -->
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin="type">

<!-- Or use magic comments in webpack/Vite -->
import(/* webpackPrefetch: true */ './SettingsPage');
import(/* webpackPreload: true */ './Dashboard');
```

### 4.6 Compression

**Brotli vs Gzip**:
- Brotli (br) is 15-20% better than Gzip
- Most CDNs support Brotli
- Server should serve both (Brotli preferred, Gzip fallback)

```nginx
# nginx.conf - Enable Brotli
brotli on;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml;
brotli_comp_level 6;
brotli_min_length 1024;

# Cache static assets
location ~* \.(js|css|woff2)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

```javascript
// Server-side Brotli (Node.js example)
import compress from 'compression';
import shrinkRay from 'shrink-ray';

app.use(shrinkRay({
  brotli: true,
  gzip: true,
  threshold: 1024
}));
```

### 4.7 Image Optimization

```html
<!-- Modern formats -->
<img src="photo.avif" alt="...">
<img src="photo.webp" alt="...">

<!-- Responsive images -->
<img 
  src="photo-800.jpg" 
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1600.jpg 1600w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1600px"
  alt="..."
>

<!-- Lazy loading (all images except above-the-fold LCP) -->
<img src="photo.jpg" loading="lazy" alt="...">

<!-- Explicit dimensions to prevent CLS -->
<img src="photo.jpg" width="800" height="600" alt="...">
```

```javascript
// Generate responsive images in build pipeline
// Use sharp for Node.js image processing
import sharp from 'sharp';

async function generateResponsiveImages(inputPath) {
  const sizes = [400, 800, 1200, 1600];
  
  await Promise.all(sizes.map(size => 
    sharp(inputPath)
      .resize(size)
      .webp({ quality: 80 })
      .toFile(`image-${size}.webp`)
  ));
}
```

---

<a name="5-lighthouse-ci--monitoring"></a>
## 5. Lighthouse CI & Monitoring

### 5.1 Lighthouse CI Setup

Lighthouse CI is a tool for running Lighthouse in continuous integration to catch performance regressions.

```bash
# Install Lighthouse CI
npm install -D @lhci/cli

# Create lighthouserc.json
# (or lighthouserc.js, lighthouse.config.js)
```

```json
{
  "ci": {
    "collect": {
      "settings": {
        "staticDistDir": "./dist",
        "url": [
          "http://localhost:3000/",
          "http://localhost:3000/about",
          "http://localhost:3000/dashboard"
        ],
        "numberOfRuns": 3
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["warn", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "total-blocking-time": ["error", { "maxNumericValue": 200 }],
        "cumulative-layout-shift": ["error", { "maxMetricValue": 0.1 }],
        "network-requests": ["warn", { "maxLength": 50 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        
      - name: Run CI
        uses: actions/setup-node@v4
        with:
          node-version: 20
          
      - run: npm ci
      - run: npm run build
      - run: npx lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

### 5.2 Custom Lighthouse Checks

```javascript
// lighthouserc.json - Custom audit
{
  "ci": {
    "collect": {
      "settings": {
        "extraHeaders": {
          "x-custom-header": "lhci-test"
        },
        "preset": "desktop",
        "throttling": {
          "rttMs": 40,
          "throughputKbps": 10240,
          "cpuSlowdownMultiplier": 1
        }
      }
    },
    "assert": {
      "preset": "no-pwa",
      "assertions": {
        "uses-long-parallel-imports": "off",
        "uses-rel-preconnect": ["warn", { "minScore": 0.5 }]
      }
    }
  }
}
```

### 5.3 Real User Monitoring (RUM)

Lighthouse is synthetic testing. Real User Monitoring captures actual user data.

```javascript
// web-vitals library for RUM
import { onCLS, onFID, onFCP, onLCP, onTTFB, onINP } from 'web-vitals';

function sendToAnalytics({ name, value, id, rating }) {
  // Send to your analytics endpoint
  fetch('/analytics', {
    method: 'POST',
    body: JSON.stringify({
      metric: name,
      value: Math.round(name === 'CLS' ? value * 1000 : value),
      rating,
      id,
      path: window.location.pathname,
      connection: navigator.connection?.effectiveType,
      deviceMemory: navigator.deviceMemory,
      timestamp: Date.now()
    }),
    keepalive: true,
    headers: { 'Content-Type': 'application/json' }
  });
}

onCLS(sendToAnalytics);
onINP(sendToAnalytics);  // INP instead of FID as of 2024
onLCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

### 5.4 Performance Budget Enforcement

```json
// budgets.json (from Lighthouse)
{
  "budgets": [
    {
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 100
        },
        {
          "resourceType": "total",
          "budget": 500
        }
      ],
      "resourceCounts": [
        {
          "resourceType": "third-party",
          "budget": 10
        }
      ]
    }
  ]
}
```

---

<a name="6-advanced-performance-patterns"></a>
## 6. Advanced Performance Patterns

### 6.1 Partial Hydration / Islands Architecture

The concept of hydrating only the interactive parts of a page. Popularized by frameworks like Astro, Qwik, and islands in Next.js.

```astro
---
// Astro example - server-render most, hydrate interactive islands
import Counter from './Counter.jsx';
import StaticContent from './StaticContent.jsx';
---

<!-- Static HTML - no JS sent -->
<StaticContent />

<!-- Interactive island - JS only for this component -->
<Counter client:visible />  <!-- Hydrate when visible -->
<HeavyChart client:idle />  <!-- Hydrate when idle -->
<Modal client:load />       <!-- Hydrate immediately -->
```

```tsx
// Next.js with partial hydration
import dynamic from 'next/dynamic';

// Only load heavy components when needed
const HeavyMap = dynamic(() => import('./components/Map'), {
  ssr: true,
  loading: () => <MapSkeleton />
});

// Load only on client side
const ClientOnlyChart = dynamic(() => import('./components/Chart'), {
  ssr: false,
  loading: () => <ChartSkeleton />
});
```

### 6.2 Streaming SSR with Suspense

```tsx
import { Suspense } from 'react';
import { renderToPipeableStream } from 'react-dom/server';

function App() {
  return (
    <html>
      <body>
        {/* Stream header immediately */}
        <header>
          <h1>My App</h1>
        </header>
        
        {/* Stream content as it becomes ready */}
        <Suspense fallback={<ContentSkeleton />}>
          <HeavyContent /> {/* This streams when ready */}
        </Suspense>
        
        <Footer />
      </body>
    </html>
  );
}

// Server streaming with backpressure handling
app.get('/', (req, res) => {
  const { pipe } = renderToPipeableStream(<App />, {
    bootstrapScripts: ['/main.js'],
    onShellReady() {
      res.statusCode = 200;
      pipe(res);
    },
    onError(error) {
      console.error(error);
      res.statusCode = 500;
    }
  });
});
```

### 6.3 Resource Hints

```html
<!-- Preconnect to critical origins -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<!-- Prefetch for likely navigations -->
<link rel="prefetch" href="/dashboard">
<link rel="dns-prefetch" href="https://analytics.example.com">

<!-- Module preload -->
<link rel="modulepreload" href="/app.js">

<!-- Speculation Rules API (Chrome 121+) -->
<script type="speculationrules">
{
  "prerender": [{
    "where": { "href_matches": "/products/*" },
    "eagerness": "moderate"
  }],
  "prefetch": [{
    "where": { "selector_matches": ".product-link" },
    "eagerness": "conservative"
  }]
}
</script>
```

### 6.4 HTTP/2 and HTTP/3

Modern protocols dramatically improve performance:
- **Multiplexing**: Multiple requests over single connection
- **Header compression**: HPACK (H2), QPACK (H3)
- **Server push**: Push resources before requested (H2; deprecated in H3)
- **0-RTT**: Faster subsequent connections (H3)

```nginx
# nginx.conf - Enable HTTP/2 and HTTP/3
server {
    listen 443 ssl http2;
    listen 443 ssl http3;
    http3 on;
    
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

### 6.5 Edge Caching

```javascript
// Cloudflare Workers example
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const cacheKey = new Request(request.url, {
    method: 'GET',
    headers: request.headers
  });
  
  const cached = await caches.default.match(cacheKey);
  if (cached) {
    // Return cached, update in background
    event.waitUntil(
      fetch(request).then(response => {
        if (response.ok) {
          caches.default.put(cacheKey, response);
        }
      })
    );
    return cached;
  }
  
  const response = await fetch(request);
  
  if (response.ok && request.method === 'GET') {
    const responseClone = response.clone();
    caches.default.put(cacheKey, responseClone);
  }
  
  return response;
}
```

---

<a name="7-performance-budgets--culture"></a>
## 7. Performance Budgets & Culture

### 7.1 Setting Performance Budgets

**Start with the user's connection speed as a baseline**:
- Approximate 3G: 400Kbps download, 150ms RTT
- Approximate 4G: 4Mbps download, 50ms RTT
- Approximate WiFi: 20Mbps, 5ms RTT

**Target for a good experience**:
- Time to Interactive < 5 seconds on 3G
- LCP < 2.5 seconds on 4G
- INP < 200ms
- CLS < 0.1

**Performance budget tiers**:

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| FCP | < 1.8s | 1.8-3.0s | > 3.0s |
| LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| INP | < 200ms | 200-500ms | > 500ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
| TTFB | < 800ms | 800-1800ms | > 1800s |

### 7.2 Making Performance Part of Development Culture

1. **Add performance to Definition of Done**
   - PRs must not decrease Lighthouse score
   - New features must include performance tests

2. **Automate performance checks in CI**
   - Lighthouse CI on every PR
   - Regression threshold at 5 points

3. **Performance reviews in code review**
   - Ask: "What will this cost in bundle size?"
   - Ask: "How will this affect Core Web Vitals?"

4. **Make performance visible**
   - Dashboard of Core Web Vitals
   - Weekly performance review in standups
   - Performance as a first-class metric (like revenue)

5. **Performance budget ownership**
   - Each team owns their performance budget
   - Cross-team coordination for shared resources

### 7.3 Common Performance Anti-Patterns

1. **Over-fetching data**: Fetching entire datasets when you only need summaries
2. **Synchronous operations on the main thread**: Heavy computation blocks rendering
3. **N+1 queries**: One query per item, not batch fetching
4. **Unoptimized images**: No lazy loading, wrong formats, too large
5. **Unused CSS/JS**: Code in production that no one uses
6. **Blocking third-party scripts**: Analytics, chat, ads blocking page load
7. **No caching**: Repeated fetches for the same data

---

<a name="8-references"></a>
## 8. References

### Core Web Vitals
- [web.dev/vitals](https://web.dev/vitals/) - Google's official documentation
- [Core Web Vitals Guide](https://web.dev/vitals-measurement-getting-started/)
- [INP documentation](https://web.dev/inp/)

### React Performance
- [React docs: Performance](https://react.dev/learn/performance)
- [useMemo and useCallback](https://react.dev/reference/react/useMemo)
- [React.memo](https://react.dev/reference/react/memo)
- [Code splitting](https://react.dev/reference/react/lazy)

### Bundle Optimization
- [Webpack: Tree Shaking](https://webpack.js.org/guides/tree-shaking/)
- [Bundlephobia](https://bundlephobia.com/)
- [Vite: Optimizing Dependencies](https://vitejs.dev/guide//features.html#lazy-loading)

### Lighthouse CI
- [Lighthouse CI documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [web-vitals library](https://github.com/GoogleChrome/web-vitals)

### General Performance
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Qwik](https://qwik.builder.io/) - Islands architecture example
- [Astro](https://astro.build/) - Islands architecture example

---

*Document generated by Coder Agent — Performance Engineering subagent*
*Research completed: 2026-04-22*
