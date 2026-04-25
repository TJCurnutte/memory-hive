---
date: __DAYS_AGO_3__
agent: researcher
context: workflow-engine v2 vs v1 cycle-time study
confidence: medium
---

# Workflow-engine v2 cuts cycle time from 14 to 8 calls

## What happened

Ran the same task suite (50 multi-step tasks) under v1 and v2.
v1 median: 14 calls. v2 median: 8 calls. p95: 22 vs 12. Methodology
in the raw notes.

## Generalizable rule

Cycle-time numbers compound. A 40% per-task cut at this layer flows
to every consumer of the workflow engine.
