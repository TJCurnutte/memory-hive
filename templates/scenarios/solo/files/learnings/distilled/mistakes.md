# Mistakes

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## `lru_cache` on stateful queries is a foot-gun

- **Date promoted:** __DAYS_AGO_2__
- **Source:** [learnings/raw/solo/lru-cache-staleness.md](../raw/solo/lru-cache-staleness.md)
- **Contributing agent:** solo
- **Original date:** __DAYS_AGO_3__
- **Context:** lru_cache returned stale auth state after a session change

`lru_cache` is for pure functions. Anything whose answer can change
without the input changing must use a TTL cache or explicit
invalidation. Treat `lru_cache` on stateful queries as a bug.
