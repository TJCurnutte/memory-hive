# coder — activity log

## __DAYS_AGO_1__

- Shipped the workflow-engine refactor. Cycle time on a typical
  multi-step task: 14 calls before, 8 calls after.

## __DAYS_AGO_4__

- Pair-coded with `planner` on the new task-decomposition path. Got it
  passing the integration suite on the first end-to-end run.

## __DAYS_AGO_8__

- Fixed the orchestrator's race when two parallel sub-agents both wrote
  to the same `agents/<id>/log.md` — now uses a per-agent lockfile.

## __DAYS_AGO_12__

- Added the `--dry-run` flag everywhere it was missing. Caught one bug
  (the "promote" path was writing on `--dry-run` if the target didn't
  exist yet).
