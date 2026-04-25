---
date: __DAYS_AGO_7__
agent: planner
context: rollout plan for workflow-engine v2
confidence: high
---

# Three-phase rollouts (demo, opt-in, default-on) catch problems early

## What happened

v2 rollout was scoped as three phases: internal demo (~5 users,
1 week), opt-in flag (~50 users, 2 weeks), default-on. Phase 1 caught
the lockfile race. Phase 2 caught the mktemp issue. Default-on shipped
clean.

## Generalizable rule

A change big enough to need a plan is big enough to need at least
three rollout phases. The phases catch different classes of bug.
