# solo — durable memory

## Facts

- Stack: Node 20 + Postgres 15 + Redis. Single-region deploy.
- CI: GitHub Actions, ubuntu-latest. ~4 minute green build.

## Preferences

- Small commits. Each commit either passes tests or is the start of
  a stash that will be squashed before push.
- Always write the migration's down-script before the up-script so
  rollback is real, not aspirational.

## Lessons learned

- **lru_cache returns stale data when the underlying state mutates.**
  Use explicit TTL or invalidate-on-write.
- **Covering indexes can replace ~3 single-column indexes** when the
  query shape is stable. Run `EXPLAIN ANALYZE` before and after.
- **Webhook + retry queue beats polling** for almost any periodic
  ingest. Polling is a tax on every cycle; webhook costs only on
  the events that actually fire.
