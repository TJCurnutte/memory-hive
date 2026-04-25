# Patterns

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## Test isolation across parallel workers

- **Date promoted:** __DAYS_AGO_13__
- **Source:** [learnings/raw/coder/parallel-test-isolation.md](../raw/coder/parallel-test-isolation.md)
- **Contributing agent:** coder
- **Original date:** __DAYS_AGO_14__
- **Context:** our test suite leaks DB state across workers in parallel mode

Shared test fixtures must not mutate state. Anything that writes to a
DB, filesystem, or mutable global should be function-scoped. Pattern
applies beyond the test suite — any parallel execution with shared
mutable state has the same class of bug.

## Authz checks belong in middleware, not handlers

- **Date promoted:** __DAYS_AGO_4__
- **Source:** [learnings/raw/reviewer/authz-middleware-not-handler.md](../raw/reviewer/authz-middleware-not-handler.md)
- **Contributing agent:** reviewer
- **Original date:** __DAYS_AGO_5__
- **Context:** feature-flag admin route was missing requireAdmin on two endpoints

Authz at the handler level is one refactor away from being deleted.
Middleware is wired at the route level and survives refactors. Any
authz check that lives in a handler is a future authz miss.

## Benchmark warmup must complete before the timer starts

- **Date promoted:** __DAYS_AGO_3__
- **Source:** [learnings/raw/researcher/warmup-outside-window.md](../raw/researcher/warmup-outside-window.md)
- **Contributing agent:** researcher
- **Original date:** __DAYS_AGO_4__
- **Context:** cost-optimization benchmark had warmup inside the timed window

Any latency measurement that includes cold-start data is reporting
something other than steady-state latency. State which one you're
measuring; if it's steady-state, the warmup must be outside the timer.
