# reviewer — activity log

Append-only journal. Newest entries at the top.

## __DAYS_AGO_1__

- Reviewed PR #218 (background worker retry semantics from `coder`).
  Approved with two comments on the test-naming and one on the timeout
  bound. `coder` accepted all three.

## __DAYS_AGO_2__

- Auth-rate-limit migration plan reviewed. Pushed back on the
  full-schema pass — too much surface for one PR. Settled on the
  `sessions` table only.

## __DAYS_AGO_3__

- Caught a logic bug in `researcher`'s benchmarking script: the
  warmup loop was inside the timed window, inflating tail latency
  by ~12%. Filed as a learning under `learnings/raw/`.

## __DAYS_AGO_5__

- Audited the new feature-flag admin route for authz holes. Two
  endpoints missing the `requireAdmin` middleware. Filed PR #221.

## __DAYS_AGO_7__

- Pair-reviewed the retry-with-backoff PR with `coder`. Confirmed the
  jitter discussion is still pending in `curator/CONFLICTS.md`;
  shipped without jitter for now.

## __DAYS_AGO_9__

- Spent an hour on a PR that was 540 lines. Asked `coder` to split it.
  Came back as three smaller PRs the next day — all merged faster.

## __DAYS_AGO_11__

- Found the long-tail memory leak in the polling service before it
  shipped. Connection pool wasn't closing on HTTP 504. Added the case
  to our chaos-test list.

## __DAYS_AGO_13__

- Reviewed the test-isolation patch from `coder`. Suggested moving
  the assertion helper to a shared module so other suites can adopt
  the same pattern.
