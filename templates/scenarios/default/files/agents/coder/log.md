# coder — activity log

Append-only journal. Newest entries at the top.

## __DAYS_AGO_1__

- Landed the retry-queue refactor. Three tests flaked under load; root
  cause was a shared fixture. Moved fixture into function scope — green
  ten runs in a row.
- Reviewed PR #214 (auth rate-limit). Approved with one comment about
  the window-reset edge case.

## __DAYS_AGO_2__

- Paired with `reviewer` on the migration plan. Ended with a smaller
  migration (just the `sessions` table) instead of the full schema pass
  we'd originally scoped.

## __DAYS_AGO_4__

- Chased a flaky CI for 90 minutes. Was a timezone bug in a test
  asserting `datetime.now()` — added it to `learnings/raw/`.

## __DAYS_AGO_6__

- Shipped `/api/v2/webhooks` retry-with-backoff. Tested against a
  chaos-mode simulator that drops 1-in-5 requests. Backoff formula
  capped at 30s after the sixth attempt.

## __DAYS_AGO_8__

- Reviewed `researcher`'s cost-optimization report before they
  submitted to the curator. Suggested sharper framing for the
  "token-budget vs. quality" tradeoff. They took two of three edits.

## __DAYS_AGO_10__

- Fixed a long-tail memory leak in the polling service (unclosed
  connections on 504). Added a soak-test harness so it doesn't regress.

## __DAYS_AGO_12__

- Wired the new feature flags into the deploy preview. Built a small
  admin route to flip them without a redeploy.

## __DAYS_AGO_14__

- Discovered that our test suite leaks DB state across workers in
  parallel mode. Added the test-isolation-patterns learning.
