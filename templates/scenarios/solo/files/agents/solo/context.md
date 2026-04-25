# solo — working context

## Role

Solo developer agent. Owns the whole stack — handlers, data layer,
deploy pipeline, tests. No specialization handoff; responsibilities
are partitioned by feature, not by layer.

## Current focus

- Auth rewrite shipped to staging; soaking for a week before prod cut-over.
- Database migration cleanup — removing the four old indexes from prod
  once the covering-index change has soaked another 48h.

## Open questions

- Is the TTL for the cache aggressive enough? 30s feels right but
  haven't measured the hit rate.

## Collaborators

- **main (Chief of Staff)** — the only other agent. Used for curation
  and cross-session handoff, not for active pairing.
