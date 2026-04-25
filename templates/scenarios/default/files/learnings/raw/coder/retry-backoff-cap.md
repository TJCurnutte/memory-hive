---
date: __DAYS_AGO_6__
agent: coder
context: shipped retry-with-backoff for /api/v2/webhooks
confidence: high
---

# Retry-with-backoff needs both a delay cap and an attempt cap

## What happened

First cut of the webhook retry path used uncapped exponential backoff
with no attempt limit. In a chaos test that dropped 1-in-5 requests,
a single slow downstream caused worker time to grow exponentially —
within 3 minutes our retry pool was at 6x normal load.

## The fix

Cap delay at 30s; cap attempt count at 7. Beyond that, surface the
failure and let the caller decide.

## Generalizable rule

Retry without a cap is not retry — it is unbounded queue growth.
Every retry policy needs both a per-attempt cap and a total-attempt
cap. The caller can always decide to retry the whole sequence; the
retry layer cannot decide to stop on its own.
