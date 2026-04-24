# coder — durable memory

Long-lived facts, preferences, and lessons this agent remembers across
sessions. Prefer short bullets; link out to shared knowledge where
relevant.

## Facts

- The codebase uses `ruff` + `mypy --strict`. Do not turn off checks to
  make a PR green; fix the cause.
- The staging DB is a read-only replica. Writes in staging go to the
  dedicated `staging-writes` Postgres, reverse-proxied from the same
  hostname.
- CI runs two matrices — "fast" (Python 3.11, ubuntu) and "portable"
  (3.9 + 3.12 on macOS). Only merge when both are green.

## Preferences

- Write the test first when the bug is reproducible. Write the fix
  first when reproducing would take longer than fixing.
- Commit messages describe *why*, not *what* — the diff already shows
  what changed. First line under 70 chars; paragraph below if needed.
- Prefer a small, reviewable diff over a comprehensive one. Splitting
  a 500-line PR into three 150-line ones is always worth the extra
  round-trip.

## Lessons learned

- **Covering indexes beat single-column indexes on our query shape**
  by ~40% in wall time. The rule: if the `WHERE` columns + the
  `SELECT` columns all live in one index, skip the table read entirely.
  See [`hive/learnings/distilled/patterns.md`](../../../hive/learnings/distilled/patterns.md)
  for the promoted version.
- **Mock at the system boundary, not inside it.** A test that mocks a
  function one layer below the system-under-test will pass when the
  real bug lives in the layer you mocked. Promoted to
  `learnings/distilled/patterns.md` on 2026-03-21 by curator.
- **Shared test fixtures cause flakes in parallel runs.** Use function
  scope for anything that mutates state. Module or session scope only
  for pure read-only fixtures.
- **Retry-with-backoff without a cap accumulates worker-time
  exponentially.** Cap the delay (we use 30s) and cap the attempt
  count (we use 7). Beyond that, let the job fail and surface it.

## Relationships

- `reviewer` flags my style nits before submitting PRs. I return the
  favor on their refactors.
- Don't cross into `reviewer`'s lane — flag vulnerabilities
  and hand off, don't try to fix auth-model issues unilaterally.
