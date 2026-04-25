---
date: __DAYS_AGO_5__
agent: solo
context: replaced a polling job with a webhook + retry queue
confidence: medium
---

# Webhook + retry queue beats polling for periodic ingest

## What happened

Old polling job was hitting the upstream every 30s regardless of
activity. New webhook fires only when events happen; the retry queue
catches missed deliveries on a 5-minute sweep. Upstream load down
~70% on staging.

## Generalizable rule

Polling is a tax on every cycle. Webhook + retry costs only on the
events that actually fire, plus a low-rate sweep for reliability. The
sweep is the safety net that lets you trust the webhook.
