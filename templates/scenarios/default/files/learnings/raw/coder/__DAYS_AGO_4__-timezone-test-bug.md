---
date: __DAYS_AGO_4__
agent: coder
context: a timezone bug in a test asserting datetime.now() flaked CI for 90 minutes
confidence: high
---

# Tests that assert against `datetime.now()` will flake across timezones

## What happened

CI flaked on `test_session_expiry`. Locally green every time. The CI
runner was UTC; my dev box was Pacific. The test asserted that a
session created at "now" expired at "now + 24h" using `datetime.now()`
with no timezone awareness — so the comparison was zone-relative and
crossed a day boundary half the time.

## Root cause

`datetime.now()` returns a naive datetime in the runner's local
timezone. Comparisons across two `now()` calls in different scopes
(one in test, one in production code) silently compared zones-as-equal.

## The fix

Switch to `datetime.now(tz=UTC)` everywhere; lint rule that bans the
naive form in our codebase.

## Generalizable rule

Naive datetimes are a foot-gun in any system with cross-timezone
deployment. Always anchor to UTC and convert at the display edge.
