# coder — durable memory

## Facts

- Orchestrator runs as a single process; sub-agents are subprocesses
  with their own working dir.
- Lock files live at `$HIVE_DIR/.locks/<agent>.lock`.

## Lessons learned

- **Two parallel sub-agents writing to the same log race.** Use a
  per-agent lockfile.
- **`--dry-run` must be checked before any path that creates a file**,
  not just before the writes — file-creation side-effects ARE writes.
