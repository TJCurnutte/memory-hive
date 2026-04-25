# Patterns

Curated learnings promoted from `learnings/raw/`.

## Lockfile acquire must be `O_EXCL`, not check-then-create

- **Date promoted:** __DAYS_AGO_7__
- **Source:** [learnings/raw/coder/lockfile-toctou.md](../raw/coder/lockfile-toctou.md)
- **Contributing agent:** coder
- **Original date:** __DAYS_AGO_8__
- **Context:** orchestrator race when two sub-agents wrote to the same log

Any check-then-create has a race. Atomic create primitives exist for
a reason.

## Three-phase rollouts catch different classes of bug at each phase

- **Date promoted:** __DAYS_AGO_6__
- **Source:** [learnings/raw/planner/three-phase-rollout.md](../raw/planner/three-phase-rollout.md)
- **Contributing agent:** planner
- **Original date:** __DAYS_AGO_7__
- **Context:** rollout plan for workflow-engine v2

A change big enough to need a plan is big enough to need at least
three rollout phases (demo, opt-in, default-on). The phases catch
different classes of bug.
