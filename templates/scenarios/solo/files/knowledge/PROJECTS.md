# Projects

Active and recently-completed work the hive cares about.

## Active

### Auth rewrite

- **Status:** soaking on staging
- **Why it matters:** Fixes the rate-limit edge cases and removes a
  decade of accidental complexity in the auth path.
- **Next milestone:** 7-day soak window ends; cut over to prod.

## Recently completed

- Polling -> webhook + retry queue (~70% upstream load drop).
- Search covering index (p95 380ms -> 110ms).
- Handler middleware unification.
