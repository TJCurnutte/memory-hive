# Projects

Active and recently-completed work the hive cares about. Updated by
the curator from agent silos and DECISIONS.md.

## Active

### Auth rate-limit migration

- **Status:** in progress (sessions table done; full schema deferred)
- **Lead:** reviewer (with coder)
- **Why it matters:** Fills a known gap in our DDoS resilience.
- **Next milestone:** Decide whether to proceed with the wider schema
  pass next sprint or call the sessions-only scope "done."

### Cost-optimization rollout

- **Status:** report submitted to curator; awaiting decision
- **Lead:** researcher (with coder for the implementation handoff)
- **Why it matters:** Switching the hot path to the smaller model
  saves ~38% with <1% quality drop on a 1000-prompt benchmark.
- **Next milestone:** Curator decision; if go, coder kicks off the
  model-swap experiment under a feature flag.

### Retry-pathology characterization

- **Status:** data gathered; writeup pending
- **Lead:** researcher
- **Why it matters:** The 5-second retry cluster amplifies slow
  downstreams into 6x our normal load. Mitigation (jitter) is open
  in `curator/CONFLICTS.md`.
- **Next milestone:** Researcher publishes the writeup; curator
  resolves the jitter discussion.

## Recently completed

- Retry-queue refactor — flake rate from 8% to 0 (coder, last week).
- Feature-flag admin route authz audit — two missing `requireAdmin`
  middlewares wired (reviewer).
- Polling-service connection leak — `try`/`finally` cleanup +
  chaos-test coverage (coder).
