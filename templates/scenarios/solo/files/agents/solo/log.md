# solo — activity log

Append-only journal. Newest entries at the top.

## __DAYS_AGO_1__

- Shipped the auth rewrite. Caught two off-by-one bugs in the rate-limit
  windowing during local smoke. Tests green; deployed to staging.

## __DAYS_AGO_3__

- Migrated from a naive lru_cache to an explicit TTL cache. The lru
  was returning stale data on session changes. Wrote up the gotcha
  under learnings/raw/.

## __DAYS_AGO_5__

- Replaced the polling job with a webhook + retry queue. ~70% drop in
  upstream load on the staging dashboard.

## __DAYS_AGO_8__

- Refactored the request-handling layer — handlers now share a
  middleware chain instead of each one re-implementing auth.

## __DAYS_AGO_11__

- Database migration: dropped four unused indexes, added one covering
  index for the search query. Search latency p95: 380ms -> 110ms.

## __DAYS_AGO_14__

- First task in this hive. Imported existing project notes and
  bootstrapped the silo.
