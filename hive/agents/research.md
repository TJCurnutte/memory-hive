# Code Quality Research — Coder Agent
> Compiled: 2026-04-22 | Session: coder

---

## 1. Code Architecture

### Clean Architecture (Bob Martin)
Layers from outer to inner:
- **Frameworks/Drivers** — DB, web, UI
- **Interface Adapters** — Controllers, Gateways, Presenters
- **Use Cases / Application** — Business rules for this app
- **Entities** — Enterprise business rules (pure)

Rule: **Dependencies point inward. The inner circle knows nothing about the outer.**

### SOLID Principles

| Principle | What it means | Why it matters |
|---|---|---|
| **S**ingle Responsibility | One class, one reason to change | Reduces coupling, easier to test |
| **O**pen/Closed | Open for extension, closed for modification | New features without touching existing code |
| **L**iskov Substitution | Subtypes must be substitutable for base types | Prevents hidden type-errors |
| **I**nterface Segregation | Many small interfaces > one big one | Clients only depend on what they use |
| **D**ependency Inversion | Depend on abstractions, not concretions | Enables swapping implementations (DB, mocks, etc.) |

### Dependency Injection
- Pass dependencies in via constructor (or factory)
- Never `new` up concrete dependencies inside a class
- Enables mocking in tests, looser coupling
- In Python: pass objects or use a DI container (e.g., `punq`, `dependency-injector`)
- In TypeScript/JS: pass via constructor or factory functions

### Modular Design
- Modules should be **high cohesion** (related things together) + **low coupling** (minimal dependencies)
- Use **pure functions** where possible — same input → same output, no side effects
- **Package by feature**, not by layer (don't group all `controllers/` together — group by domain: `auth/`, `orders/`)

---

## 2. Common Bugs & Prevention

### Null / Undefined Reference Errors
**Problem:** Accessing `.property` on `null` or `undefined`
**Prevention:**
- Use optional chaining: `obj?.foo?.bar` (TS/JS), `obj?.prop` (Python 3.10+)
- Use nullish coalescing: `value ?? 'default'`
- Return empty collections `[]` instead of `null`
- Return zero/empty string instead of `null` for primitives where sensible
- TypeScript: strict null checks enabled, never use `any`
- Python: type hints with `Optional[T]` for nullable values

### Race Conditions
**Problem:** Shared mutable state accessed simultaneously by multiple threads/async operations
**Prevention:**
- Immutable data structures — don't mutate shared state
- Use mutexes/locks for shared mutable state (or prefer thread-safe message passing)
- Async: avoid shared state across `await` points
- Idempotent operations — safe to call multiple times

### Memory Leaks
**Problem:** Objects retained in memory after they're no longer needed
**Prevention:**
- Python: watch for circular references (use `weakref` where applicable)
- JS: always remove event listeners when done; clear intervals/timeouts
- Monitor long-lived objects accumulating references
- Use profiling tools: Chrome DevTools Memory tab, Python `tracemalloc`
- Close DB connections, file handles, streams explicitly

### Off-by-One Errors
**Problem:** Loop boundary mistakes, index confusion
**Prevention:**
- Name variables clearly: `start`, `end`, `count` — not `i`, `j`
- Prefer `range(start, end)` semantics over manual index math
- Use built-in iteration methods instead of manual loops when possible
- Test boundary conditions explicitly

### SQL Injection
**Problem:** User input concatenated into SQL queries
**Prevention:**
- Always use parameterized queries / prepared statements
- Never concatenate user input into SQL strings
- Use an ORM's query builder (SQLAlchemy, Prisma, etc.) for complex queries
- Validate/sanitize input at the boundary, not deep in logic

### Silent Failures
**Problem:** Functions return `None`/`null`/`false` without raising an error, caller doesn't check
**Prevention:**
- Use exceptions for truly exceptional conditions
- Return Result/Either types in languages that support it (or simulate with tuples)
- Log warnings for recoverable errors — don't silently swallow

---

## 3. Testing Strategies

### The Testing Pyramid

```
        /\
       /  \     E2E / UI Tests (few, slow, expensive)
      /----\
     /      \   Integration Tests (medium)
    /--------\
   /          \ Unit Tests (many, fast, cheap)
  /------------\
```

### Unit Tests
- Test **one unit** (function, class, method) in isolation
- Mock all external dependencies (DB, API, file system)
- **Arrange-Act-Assert** pattern: set up → execute → verify
- Fast (< 100ms each) — run hundreds in seconds
- Target: **70-80% code coverage** for critical paths, not 100% (diminishing returns)

### Integration Tests
- Test how units work **together** — real DB, real cache, etc.
- Use test containers (Docker) for databases
- Keep them slower than unit tests; have fewer of them
- Good for verifying: DB queries, auth flows, API contracts

### TDD (Test-Driven Development)
1. **Red:** Write a failing test
2. **Green:** Write minimal code to make it pass
3. **Refactor:** Improve code while tests stay green
- Forces simpler, more testable design
- Creates living documentation
- Slow to start; pays off over time on complex systems

### Mocking Best Practices
- Mock **at the boundary** (external services, DB), not internal collaborators
- Don't over-mock — prefer real objects where the test can
- Use spies/stubs sparingly — they create fragile tests
- `unittest.mock` (Python), `jest.mock` (JS/TS)

### Code Coverage
- **Line coverage ≠ correctness**
- A 100% covered but poorly written test suite is worse than 70% well-asserted tests
- Use coverage to find untested branches, not as a metric to hit
- Flag: tests that only pass because they're tightly coupled to implementation

### Property-Based Testing
- Generate random inputs to test function behavior across many values
- Tools: `hypothesis` (Python), `fast-check` (JS/TS)
- Catches edge cases human-written tests miss

---

## 4. Modern Language Patterns

### Async/Await
- **Always** `await` in try/catch or use `.catch()` — unhandled promise rejections crash processes
- Don't mix `.then()` chains with `await` unnecessarily — pick one style
- In Python: `asyncio.run()` for top-level; don't mix threading with asyncio
- In Node.js: `await` inside loops — use `Promise.all()` for parallel operations
- Pattern: `await asyncio.gather(*tasks)` for concurrency

### Functional Patterns (in any language)
- **Pure functions** — no side effects, same input → same output
- **Immutability** — prefer `Object.freeze()`, immutable data structures
- **Higher-order functions** — `map`, `filter`, `reduce`, `compose`
- **Pipes/chains** — `data |> transform1 |> transform2` (or method chaining)
- **Pattern matching** — exhaustive conditional logic (Python `match`, Rust `match`, TS `satisfies`)

### Design Patterns (use judiciously)

| Pattern | When to use | When to avoid |
|---|---|---|
| **Factory** | Object creation involves complex logic | Simple `new` works fine |
| **Observer** | One-to-many events, pub/sub | When a simple callback works |
| **Strategy** | Interchangeable algorithms | When one algorithm is always used |
| **Decorator** | Add behavior without changing class | Over-engineering; inheritance works |
| **Repository** | Abstract DB/data access | Simple apps with direct queries |
| **Builder** | Complex object construction | Simple object with few params |

### Error Handling Patterns
- **Result/Either monad** (Rust, Haskell) — explicit error paths
- **Go-style**: return `(value, error)` tuple
- **C# Try pattern**: `bool TryParse(out result)`
- **Never swallow exceptions silently** — log or re-raise with context

---

## 5. Performance & Security

### Caching
- Cache expensive computations (DB queries, API calls, computed values)
- Tools: Redis, Memcached, in-memory LRU caches
- **Cache invalidation** is the hard part — use time-based TTL + explicit invalidation
- Don't cache user-specific data in shared caches without proper isolation

### Database Optimization
- Index columns used in `WHERE`, `JOIN`, `ORDER BY`
- Use EXPLAIN ANALYZE (PostgreSQL) / EXPLAIN (MySQL) to find slow queries
- Batch inserts instead of row-by-row
- Use connection pooling (pgBouncer, built-in poolers)
- Prefer bulk reads over N+1 query patterns

### Input Validation
- Validate at **boundaries** (API entry, form submission) — not deep in business logic
- Use schema validation libraries: Pydantic, Zod, Joi, JSON Schema
- **Never trust user input** — sanitize, validate, escape
- Type-safe validation catches bugs at the edge

### Secure Coding
- **Principle of least privilege** — request only permissions you need
- Secrets in env vars or a secrets manager (AWS Secrets Manager, Vault) — never in code or git
- HTTPS everywhere; validate TLS certificates
- **OWASP Top 10** — review for your stack (injection, broken auth, sensitive data exposure)
- Rate limiting on public APIs to prevent abuse
- CSRF tokens for state-changing operations in web apps
- Content Security Policy headers to prevent XSS