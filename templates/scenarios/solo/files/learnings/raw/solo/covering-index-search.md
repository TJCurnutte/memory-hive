---
date: __DAYS_AGO_11__
agent: solo
context: search query latency was p95=380ms; covering index dropped it to 110ms
confidence: high
---

# Covering index for the search query path

## What happened

`/search` p95 was 380ms. EXPLAIN ANALYZE showed the planner was
hitting the table for two columns that weren't in the existing
single-column index. Added a covering index `(query, lang)` INCLUDE
`(title, snippet)`. p95 dropped to 110ms.

## Generalizable rule

When the SELECT columns + WHERE columns all fit in a single index,
the table read can be skipped entirely. Cost: bigger index pages
and slower writes; benefit: the read path is index-only.
