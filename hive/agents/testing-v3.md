# Web Testing — v3 (Web-Dev Agent)
> Last updated: 2026-04-22 | Maintainer: web-dev agent

---

## Table of Contents
1. [Testing Pyramid & Strategy](#1-testing-pyramid--strategy)
2. [Playwright — E2E Testing](#2-playwright--e2e-testing)
3. [Playwright — Configuration & Setup](#3-playwright--configuration--setup)
4. [Playwright — API Testing](#4-playwright--api-testing)
5. [Component Testing (React/Angular/Vue)](#5-component-testing-reactangularvue)
6. [Visual Regression Testing](#6-visual-regression-testing)
7. [Accessibility Testing in CI](#7-accessibility-testing-in-ci)
8. [Unit Testing](#8-unit-testing)
9. [CI/CD Pipelines](#9-cicd-pipelines)
10. [Test Data Management](#10-test-data-management)
11. [Debugging & Reporting](#11-debugging--reporting)
12. [Resources & References](#12-resources--references)

---

## 1. Testing Pyramid & Strategy

### 1.1 The Testing Pyramid
```
         /\
        /  \        ← E2E Tests (few, slow, high confidence)
       /----\
      /      \      ← Integration Tests (medium, medium confidence)
     /--------\
    /          \    ← Unit Tests (many, fast, low confidence per test)
   /____________\
```

### 1.2 Test Distribution

| Layer | Amount | Speed | Confidence | Tools |
|-------|--------|-------|-----------|-------|
| Unit | 60-70% | ms | Per unit | Jest, Vitest, Mocha |
| Integration | 20-30% | seconds | Module integration | Jest, Vitest, React Testing Library |
| E2E | 5-15% | minutes | Full flow | Playwright, Cypress |
| Visual | 5-10% | seconds-minutes | Visual regression | Playwright Visual, Percy, Chromatic |

### 1.3 What to Test at Each Level

**Unit tests:**
- Pure functions with complex logic
- Utility functions
- Data transformations
- Edge cases, error handling

**Integration tests:**
- Component behavior with hooks/context/state
- API calls (mocked)
- Database operations (in memory or test DB)
- Routing behavior

**E2E tests:**
- Critical user journeys (login, checkout, sign-up)
- Forms that submit data
- Navigation flows
- Features difficult to test at lower levels

**Do NOT test at E2E level:**
- Internal implementation details
- Edge cases with multiple variations (unit test instead)
- Performance benchmarks
- Styling details (visual regression instead)

### 1.4 Testing Trophy (Kent C. Dodds)
A more nuanced view: integration tests as the primary confidence source:
```
         /\
        /  \        ← E2E (few, for critical paths only)
       /----\
      /      \      ← Integration (most important — test like a user)
     /--------\
    /          \    ← Static (lint, type-check — catch typos early)
   /____________\
```

---

## 2. Playwright — E2E Testing

### 2.1 Why Playwright?
- Cross-browser: Chromium, Firefox, WebKit (Safari)
- Auto-waiting: automatically waits for elements to be actionable
- Parallel execution by default
- Powerful debugging: Playwright Inspector, trace viewer
- Built-in network interception (mocking)
- Strong TypeScript support
- Single API across all browsers

### 2.2 Installation
```bash
npm init playwright@latest
# Or add to existing project:
npm install -D @playwright/test
npx playwright install # install browsers
```

### 2.3 Basic Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should show login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
  });

  test('should display validation errors on empty submit', async ({ page }) => {
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('should navigate to dashboard on successful login', async ({ page }) => {
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
});
```

### 2.4 Selectors (Best Practices)
Prefer accessibility-first locators:
```typescript
// BEST: Accessible name (recommended)
await page.getByRole('button', { name: 'Submit' })
await page.getByLabel('Email address')
await page.getByPlaceholder('Search products...')
await page.getByText('Forgot password?')
await page.getByRole('heading', { name: 'Settings' })

// GOOD: Test IDs as fallback
await page.getByTestId('signup-button')

// ACCEPTABLE: CSS selectors (only for complex cases)
await page.locator('.modal__close-btn').first()

// AVOID: XPath selectors (fragile, not accessible)
await page.locator('xpath=//button[contains(text(), "Submit")]')
```

### 2.5 Auto-Waiting
Playwright waits automatically for:
- Elements to be visible/hidden
- Elements to be attached to DOM
- Elements to be enabled/disabled
- Elements to have text/content
- Elements to be stable (no animation)
- Network idle after navigation

```typescript
// No manual waits needed — Playwright handles this:
await page.click('button'); // waits for button to be visible + enabled
await page.fill('input', 'text'); // waits for input to be enabled
```

### 2.6 Network Interception (Mocking)
```typescript
test('should display data from API', async ({ page }) => {
  await page.route('/api/users/123', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: '123',
        name: 'Jane Doe',
        email: 'jane@example.com',
        avatar: 'https://example.com/avatar.jpg'
      })
    });
  });

  await page.goto('/profile');
  await expect(page.getByText('Jane Doe')).toBeVisible();
  await expect(page.getByText('jane@example.com')).toBeVisible();
});

test('should handle API errors gracefully', async ({ page }) => {
  await page.route('/api/users/123', (route) => {
    route.fulfill({ status: 500, body: 'Server error' });
  });

  await page.goto('/profile');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
```

### 2.7 File Uploads
```typescript
test('should upload a file', async ({ page }) => {
  const fileInput = page.getByTestId('file-upload');
  await fileInput.setInputFiles({
    name: 'document.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('PDF content here')
  });
  await expect(page.getByText('document.pdf')).toBeVisible();
});
```

### 2.8 Authentication in Tests
```typescript
// Reuse authenticated state across tests
test.use({
  storageState: './tests/.auth/user.json',
});

test.describe('Authenticated User', () => {
  test('should access dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });
});
```

Or use API login:
```typescript
async function loginAsUser(page: Page, email: string, password: string) {
  const token = await getAuthToken(email, password);
  await page.context().addInitScript((token) => {
    localStorage.setItem('authToken', token);
  }, token);
  await page.goto('/');
}
```

---

## 3. Playwright — Configuration & Setup

### 3.1 playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,  // fail if only() is left in tests
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html'],
    ['list'],
  ],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',       // capture trace on first retry
    screenshot: 'only-on-failure',  // screenshot on failure
    video: 'retain-on-failure',     // keep video on failure
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### 3.2 Test Organization
```
tests/
├── e2e/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── signup.spec.ts
│   │   └── logout.spec.ts
│   ├── dashboard/
│   │   ├── overview.spec.ts
│   │   └── settings.spec.ts
│   └── checkout/
│       └── checkout.spec.ts
├── fixtures/
│   ├── users.ts
│   └── mock-data.ts
└── page-objects/
    ├── LoginPage.ts
    ├── DashboardPage.ts
    └── CheckoutPage.ts
```

### 3.3 Page Object Pattern
```typescript
// page-objects/LoginPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign In' });
    this.errorMessage = page.getByRole('alert');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }
}
```

```typescript
// Usage in tests:
import { test, expect } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';

test('should login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

---

## 4. Playwright — API Testing

### 4.1 API Testing with Playwright
```typescript
import { test, expect, request } from '@playwright/test';

test.describe('Users API', () => {
  const apiContext = request.newContext({ baseURL: 'https://api.example.com' });

  test('GET /users returns user list', async ({}) => {
    const response = await apiContext.get('/users');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data.users)).toBeTruthy();
    expect(data.users.length).toBeGreaterThan(0);
  });

  test('POST /users creates a new user', async ({}) => {
    const response = await apiContext.post('/users', {
      data: {
        name: 'Test User',
        email: `test-${Date.now()}@example.com`,
        password: 'securePassword123'
      }
    });
    expect(response.status()).toBe(201);

    const user = await response.json();
    expect(user.id).toBeDefined();
    expect(user.name).toBe('Test User');
  });

  test('GET /users/:id returns 404 for non-existent user', async ({}) => {
    const response = await apiContext.get('/users/999999');
    expect(response.status()).toBe(404);
  });
});
```

### 4.2 Schema Validation
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  createdAt: z.string().datetime(),
});

test('GET /users/:id returns valid user object', async ({}) => {
  const response = await apiContext.get('/users/123');
  const data = await response.json();

  const result = UserSchema.safeParse(data);
  expect(result.success).toBeTruthy();
});
```

---

## 5. Component Testing (React/Angular/Vue)

### 5.1 React Testing Library
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('renders the form fields', () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('calls onSubmit with form data on submit', async () => {
    const mockSubmit = jest.fn();
    render(<LoginForm onSubmit={mockSubmit} />);

    await fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    await fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    await fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });

  it('displays validation error for invalid email', async () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    await fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid-email' }
    });
    await fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/please enter a valid email/i)).toBeInTheDocument();
  });
});
```

### 5.2 Testing Async Components
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('displays loading state then user data', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ name: 'Jane Doe', email: 'jane@example.com' })
      })
    ) as jest.Mock;

    render(<UserProfile userId="123" />);

    // Loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Data appears after fetch resolves
    await waitFor(() => {
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });
});
```

### 5.3 Testing Hooks
```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('should initialize with 0', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('should increment count', () => {
    const { result } = renderHook(() => useCounter());
    act(() => result.current.increment());
    expect(result.current.count).toBe(1);
  });

  it('should decrement count', () => {
    const { result } = renderHook(() => useCounter());
    act(() => result.current.decrement());
    expect(result.current.count).toBe(-1);
  });
});
```

---

## 6. Visual Regression Testing

### 6.1 Tools

| Tool | Type | Notes |
|------|------|-------|
| [Playwright Visual](https://playwright.dev/docs/api/class-page#page-assertions-screenshot) | Built-in | `page.screenshot()` + pixel match |
| [Percy](https://percy.io/) | Cloud service | Managed, CI integration, branch diffing |
| [Chromatic](https://www.chromatic.com/) | Cloud service | Storybook integration |
| [BackstopJS](https://github.com/garris/BackstopJS) | Self-hosted | Open source, docker-based |
| [Pixelmatch](https://github.com/mapbox/pixelmatch) | Library | Low-level pixel diff |

### 6.2 Playwright Visual Testing
```typescript
import { test, expect } from '@playwright/test';

test('homepage hero matches design', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveScreenshot('hero-desktop.png', {
    maxDiffPixels: 100,         // allow small diffs (font rendering, anti-aliasing)
    fullPage: true,              // screenshot entire page
  });
});

test('homepage hero mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await expect(page).toHaveScreenshot('hero-mobile.png');
});
```

### 6.3 Percy CI Integration
```yaml
# .github/workflows/visual.yml
name: Visual Regression
on: [pull_request]

jobs:
  visual:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - name: Visual snapshot
        uses: percy/exec-action@x
        with:
          command: npx percy snapshot ./tests/e2e
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}
```

### 6.4 Visual Testing Best Practices
- Test at multiple viewport sizes (mobile, tablet, desktop)
- Use `fullPage: true` for pages you want to verify end-to-end
- Set a threshold (`maxDiffPixels`) for minor rendering variations
- Disable animations or use `prefers-reduced-motion` via `page.emulateMedia()`
- Update baselines when intentionally changing design

---

## 7. Accessibility Testing in CI

### 7.1 axe-playwright
```typescript
import AxeBuilder from '@axe-core/playwright';

test('no accessibility violations on homepage', async ({ page }) => {
  await page.goto('/');

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
    .analyze();

  expect(accessibilityScanResults.violations).toEqual([]);
});
```

### 7.2 GitHub Actions CI Integration
```yaml
# .github/workflows/a11y.yml
name: Accessibility
on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run dev &
      - name: Wait for server
        run: sleep 5
      - name: Run Playwright tests
        run: npx playwright test --project=chromium
```

### 7.3 Storybook Accessibility Testing
```javascript
// .storybook/main.js
module.exports = {
  addons: ['@storybook/addon-a11y'],
};

// stories/Button.stories.tsx
import '@storybook/addon-a11y/preview';

const meta = {
  component: Button,
  parameters: {
    a11y: {
      config: {
        rules: [{ id: 'color-contrast', enabled: true }],
      },
    },
  },
};
```

---

## 8. Unit Testing

### 8.1 Vitest (Modern, Fast Alternative to Jest)
```typescript
import { describe, it, expect, vi } from 'vitest';

describe('formatCurrency', () => {
  it('should format positive numbers', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('should format negative numbers', () => {
    expect(formatCurrency(-1234.56)).toBe('-$1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });
});

describe('useDebounce', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('should debounce the value', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: 'initial' } }
    );

    rerender({ value: 'updated' });
    expect(result.current).toBe('initial');

    act(() => vi.advanceTimersByTime(500));
    expect(result.current).toBe('updated');
  });
});
```

### 8.2 Mocking
```typescript
// Mock external module
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ name: 'Jane Doe' }),
}));

// Mock fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ data: 'test' })
  })
) as vi.Mock;

// Spy on console.error
vi.spyOn(console, 'error').mockImplementation(() => {});
```

---

## 9. CI/CD Pipelines

### 9.1 GitHub Actions Full Stack
```yaml
name: Test & Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # ─── Lint & Type Check ───
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck

  # ─── Unit Tests ───
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: codecov/codecov-action@v4
        with: { token: ${{ secrets.CODECOV_TOKEN }} }

  # ─── E2E Tests (Chromium only in PR) ───
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --project=chromium
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/

  # ─── Lighthouse CI ───
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - name: Run Lighthouse CI
        run: npx @lhci/cli autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

  # ─── Deploy (on merge to main) ───
  deploy:
    needs: [quality, unit-tests, e2e]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: npm run deploy
```

### 9.2 Flaky Test Handling
```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,
  // For known-flaky tests, add to test name: test('test @flaky', ...)
});
```

### 9.3 Matrix Testing
```yaml
# Test across multiple configurations
strategy:
  matrix:
    node-version: [18, 20, 22]
    browser: [chromium, firefox, webkit]

steps:
  - uses: actions/setup-node@v4
    with: { node-version: ${{ matrix.node-version }} }
  - run: npx playwright test --project=${{ matrix.browser }}
```

---

## 10. Test Data Management

### 10.1 Fixtures
```typescript
// fixtures/users.ts
export const testUsers = {
  admin: {
    id: 'user-admin-1',
    email: 'admin@example.com',
    password: 'AdminPassword123!',
    role: 'admin',
    name: 'Alice Admin'
  },
  user: {
    id: 'user-standard-1',
    email: 'user@example.com',
    password: 'UserPassword123!',
    role: 'user',
    name: 'Bob User'
  },
  guest: {
    id: 'user-guest-1',
    email: 'guest@example.com',
    password: 'GuestPassword123!',
    role: 'guest',
    name: 'Carol Guest'
  }
};
```

### 10.2 Playwright Fixtures
```typescript
// fixtures/api-fixtures.ts
import { test as base } from '@playwright/test';
import { testUsers, testOrganizations } from './fixtures/users';

type ApiFixtures = {
  createTestUser: typeof testUsers.user;
  createTestOrg: typeof testOrganizations.acme;
};

export const test = base.extend<ApiFixtures>({
  createTestUser: async ({ request }, use) => {
    const user = await request.post('/api/test/users', { data: testUsers.user });
    const createdUser = await user.json();
    await use(createdUser);
    // Cleanup
    await request.delete(`/api/test/users/${createdUser.id}`);
  }
});
```

### 10.3 Test Data Factories
```typescript
// utils/test-data-factory.ts
import { faker } from '@faker-js/faker';

export function createUser(overrides = {}) {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    avatar: faker.image.avatar(),
    createdAt: faker.date.past().toISOString(),
    ...overrides
  };
}

export function createProduct(overrides = {}) {
  return {
    id: faker.string.uuid(),
    name: faker.commerce.productName(),
    price: parseFloat(faker.commerce.price()),
    description: faker.commerce.productDescription(),
    image: faker.image.urlPicsumPhotos(),
    category: faker.commerce.department(),
    inStock: faker.datatype.boolean(),
    ...overrides
  };
}
```

---

## 11. Debugging & Reporting

### 11.1 Playwright Inspector
```bash
npx playwright test --ui          # UI mode with interactive debugging
npx playwright show-report        # View HTML report
PWDEBUG=1 npx playwright test     # Debug mode
```

### 11.2 Trace Viewer
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    trace: 'on-first-retry',
  }
});
```
```bash
npx playwright show-trace trace.zip
```
Trace viewer shows: timeline, screenshots, clicks, network requests, console logs.

### 11.3 CI Artifacts
```yaml
# Upload test artifacts on failure
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: playwright-report
    path: |
      playwright-report/
      test-results/
      trace.zip
    retention-days: 14
```

---

## 12. Resources & References

### Playwright
- [Playwright Docs](https://playwright.dev/docs/intro)
- [Playwright API](https://playwright.dev/docs/api/class-page)
- [Playwright Test](https://playwright.dev/docs/api/class-test)
- [Playwright Examples](https://playwright.dev/docs/examples)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

### Component Testing
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Library Queries](https://testing-library.com/docs/queries/about/)
- [Vitest](https://vitest.dev/)

### Visual Regression
- [Percy Docs](https://docs.percy.io/)
- [Chromatic Docs](https://www.chromatic.com/docs/)
- [BackstopJS](https://github.com/garris/BackstopJS)

### CI/CD
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Playwright CI docs](https://playwright.dev/docs/ci-intro)

### Accessibility Testing
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [axe-core-playwright](https://github.com/dequelabs/axe-core-npm/tree/develop/packages/playwright)
- [Storybook A11y addon](https://storybook.js.org/addons/@storybook/addon-a11y)

---

*End of testing-v3.md*
