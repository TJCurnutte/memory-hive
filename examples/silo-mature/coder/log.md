# coder — activity log

Append-only journal. Newest entries at the top.

## 2026-04-08

- Landed the retry-queue refactor. Three tests flaked under load; root
  cause was a shared fixture. Moved fixture into function scope — green
  ten runs in a row.
- Reviewed PR #214 (auth rate-limit). Approved with one comment about
  the window-reset edge case.

## 2026-04-07

- Paired with `reviewer` on the migration plan. Ended with a smaller
  migration (just the `sessions` table) instead of the full schema pass
  we'd originally scoped.

## 2026-04-05

- Chased a flaky CI for 90 minutes. Was a timezone bug in a test
  asserting `datetime.now()` — added it to `learnings/raw/`.

## 2026-04-03

- Shipped `/api/v2/webhooks` retry-with-backoff. Tested against a
  chaos-mode simulator that drops 1-in-5 requests. Backoff formula
  capped at 30s after the sixth attempt.

## 2026-04-01

- Reviewed `research-analyst`'s cost-optimization report before they
  submitted to the curator. Suggested sharper framing for the
  "token-budget vs. quality" tradeoff. They took two of three edits.

## 2026-03-28

- Fixed a long-tail memory leak in the polling service (unclosed
  connections on 504). Added a soak-test harness so it doesn't regress.

## 2026-03-25

- Wired the new feature flags into the deploy preview. Built a small
  admin route to flip them without a redeploy.

## 2026-03-22

- Replied in `#eng-team` about the database index choice — pointed at
  the covering-index doc. Updated `memory.md` with the rule.

## 2026-03-18

- Landed the mock-boundary rule. Too many tests were mocking one layer
  down from where the bug actually lived. Wrote a learning: only mock
  at the system boundary, not inside it.

## 2026-03-14

- Onboarding touch-up: our internal "how to add a route" doc was four
  commits out of date. Fixed and opened a PR.

## 2026-03-11

- Discovered that our test suite leaks DB state across workers in
  parallel mode. Added the test-isolation-patterns learning.

## 2026-03-08

- Shipped the first cut of the background worker. Basic happy path
  works; need to come back for retry semantics.

## 2026-03-02

- First real task: fix the paginated-query N+1. Replaced with a single
  JOIN. Response time on `/search` dropped from 1.8s to 220ms.

## 2026-02-28

- Silo initialized. Getting oriented — reading the hive, the registry,
  and the main curator's `DECISIONS.md` to see recent calls.
