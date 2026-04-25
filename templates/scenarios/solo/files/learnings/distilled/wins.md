# Wins

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## Search query p95 cut from 380ms to 110ms

- **Date promoted:** __DAYS_AGO_10__
- **Source:** [learnings/raw/solo/covering-index-search.md](../raw/solo/covering-index-search.md)
- **Contributing agent:** solo
- **Original date:** __DAYS_AGO_11__
- **Context:** covering index for /search

Single covering index (query, lang) INCLUDE (title, snippet) replaced
two narrower indexes and skipped the table read entirely on the hot
path. ~70% latency reduction at p95.
