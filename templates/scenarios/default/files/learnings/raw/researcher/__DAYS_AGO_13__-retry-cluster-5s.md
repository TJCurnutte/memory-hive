---
date: __DAYS_AGO_13__
agent: researcher
context: characterizing our retry pathology from chaos-mode logs
confidence: medium
---

# Retries cluster at the 5-second mark and amplify slow downstreams

## What happened

Pulled three weeks of chaos-mode logs. Plotted retry timings: a sharp
spike at 5s, consistent with our backoff curve. The same plot showed
that when a downstream is slow but not failing, the spike at 5s
becomes a sustained 6x amplification of normal load.

## Generalizable rule

Backoff curves with a synchronous start time create thundering-herd
amplification when a downstream is slow-not-down. Mitigation: jitter
the first retry delay by ±20% so the herd disperses. (Open question
in `curator/CONFLICTS.md` — not yet implemented.)
