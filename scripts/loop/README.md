# Memory Hive self-iteration loop

A scheduled loop where **each iteration makes a concrete, safe improvement to
the overall use of the hive** and records what changed.

## What one iteration does

`scripts/loop/loop_iteration.sh`:

1. Ensures a hive exists (installs a throwaway one from this repo if none).
2. Runs the built-in maintenance pass (`memory-hive maintain`): registry and
   citation refresh, recall-index maintenance, and the curator Optimizer.
3. Regenerates a usage-analytics snapshot (`scripts/loop/hive_usage_report.py`):
   corpus size, per-platform/agent memory footprint, recall-index health,
   raw→distilled learning pipeline, and stale signal.

Snapshots land in `reports/memory-hive-loop/` (`latest.md`, `latest.json`, plus
timestamped history). The script is deterministic, idempotent, and **never
commits, pushes, or merges.**

## Run it once

```sh
# Against your real hive (default ~/.memory-hive):
sh scripts/loop/loop_iteration.sh

# Against a specific hive:
MEMORY_HIVE_DIR=/path/to/.memory-hive sh scripts/loop/loop_iteration.sh

# Analytics only, printed to stdout:
python3 scripts/loop/hive_usage_report.py --hive ~/.memory-hive
```

## Run it hourly

Two supported cadences:

### A. Deterministic maintenance loop (no credentials) — included

`.github/workflows/memory-hive-loop.yml` runs one iteration every hour
(`cron: "0 * * * *"`) and uploads the snapshot as a build artifact. It is
**opt-in**: it only starts once merged to the branch GitHub schedules from
(the default branch). Delete the file or comment out the `schedule:` block to
turn it off.

For a non-GitHub host, use cron directly:

```cron
0 * * * * cd /path/to/memory-hive && sh scripts/loop/loop_iteration.sh >> /tmp/mh-loop.log 2>&1
```

### B. Agent-driven improvement loop (needs an agent runtime)

The deterministic loop keeps the hive healthy and visible, but it cannot invent
*new* features or code changes — that requires an LLM agent in the loop. To get
creative hourly improvements, schedule an agent (e.g. a Cursor scheduled cloud
agent, or a CI job that calls an LLM) with this repo and a prompt like
"make one improvement to overall use of Memory Hive, open a PR." That path
needs an API key / agent credential and should always open a **reviewed PR**
(never auto-merge).

## Guardrails

- No auto-commit, no auto-push, no auto-merge.
- Stdlib + POSIX shell only (same as the rest of the project).
- Idempotent: safe to run repeatedly; re-running only refreshes the snapshot.
