---
date: __DAYS_AGO_8__
agent: coder
context: orchestrator race when two sub-agents wrote to the same log
confidence: high
---

# Lockfile acquire must be `O_EXCL`, not check-then-create

## What happened

Parallel sub-agents writing the same `agents/<id>/log.md` produced
interleaved bytes. First fix used `if ! -f .lock; then touch .lock`;
TOCTOU window was just wide enough to fire on ~3% of runs.

## The fix

`open(...O_EXCL|O_CREAT)` and check the return code. Race-free.

## Generalizable rule

Any check-then-create has a race. The kernel exposes atomic create
primitives — use them.
