# Mistakes

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## Naive datetime.now() flakes across timezones

- **Date promoted:** __DAYS_AGO_3__
- **Source:** [learnings/raw/coder/timezone-test-bug.md](../raw/coder/timezone-test-bug.md)
- **Contributing agent:** coder
- **Original date:** __DAYS_AGO_4__
- **Context:** a timezone bug in a test asserting datetime.now() flaked CI for 90 minutes

`datetime.now()` returns a naive datetime in the runner's local
timezone. Always anchor to UTC and convert at the display edge. Lint
rule that bans the naive form was the right fix.

## HTTP 504 responses leak connections if the pool doesn't close on error

- **Date promoted:** __DAYS_AGO_9__
- **Source:** [learnings/raw/coder/connection-pool-504.md](../raw/coder/connection-pool-504.md)
- **Contributing agent:** coder
- **Original date:** __DAYS_AGO_10__
- **Context:** long-tail memory leak in the polling service

Resource cleanup belongs in `finally`, not in the success path. Every
early-return on an error path is a potential leak.
