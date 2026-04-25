# Patterns

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## Webhook + retry queue beats polling for periodic ingest

- **Date promoted:** __DAYS_AGO_4__
- **Source:** [learnings/raw/solo/webhook-vs-polling.md](../raw/solo/webhook-vs-polling.md)
- **Contributing agent:** solo
- **Original date:** __DAYS_AGO_5__
- **Context:** replaced a polling job with a webhook + retry queue

Polling is a tax on every cycle. Webhook + retry costs only on the
events that actually fire, plus a low-rate sweep for reliability. The
sweep is the safety net that lets you trust the webhook.

## Covering index when SELECT + WHERE columns all fit

- **Date promoted:** __DAYS_AGO_10__
- **Source:** [learnings/raw/solo/covering-index-search.md](../raw/solo/covering-index-search.md)
- **Contributing agent:** solo
- **Original date:** __DAYS_AGO_11__
- **Context:** search query latency was p95=380ms; covering index dropped it to 110ms

When the SELECT columns + WHERE columns all fit in a single index,
the table read can be skipped entirely. Cost: bigger index pages and
slower writes; benefit: the read path is index-only.
