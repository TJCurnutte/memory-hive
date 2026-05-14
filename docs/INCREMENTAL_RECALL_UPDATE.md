# Incremental recall update proof

Memory Hive v1.1 shipped `memory-hive recall update`, but the first implementation was only incremental at the detection layer: it counted changed, skipped, and deleted files, then rebuilt the full SQLite/FTS index when anything changed.

This page documents the corrected contract for recall writeback speed.

## Contract

`memory-hive recall update` should handle normal agent writeback without rebuilding the whole index.

When one markdown file changes, update should:

1. stat unchanged files and skip them without hashing/chunking;
2. hash only files whose size or mtime changed;
3. treat same-content mtime touches as metadata-only updates;
4. delete index rows only for changed or deleted files;
5. reinsert chunks only for changed or new files;
6. keep `files`, `chunks`, `codes`, `tokens`, `sketches`, and FTS tables coherent;
7. preserve unchanged file rows and citations;
8. make newly appended memory queryable immediately.

Markdown remains the source of truth. The SQLite/FTS index remains disposable and rebuildable.

## Regression gate

The regression tests in `tests/test_hivecode_incremental_update.py` monkeypatch `build_index()` to fail while `update_index()` runs. That catches accidental regressions where update silently falls back to full rebuild.

The tests verify:

- a single-file append updates only that file and preserves an unchanged file row;
- the appended phrase can be recalled immediately through `query(..., for_agent="hermes")`;
- deleting a file removes its indexed rows without leaving doctor-stale state;
- deleted files are no longer retrievable through `get_file_record()`.

## 1000-loop proof harness

`scripts/validate_incremental_update_1000.py` runs a sandbox proof loop:

1. copies a source hive into a temporary directory;
2. builds the recall index once;
3. monkeypatches `build_index()` so full rebuild attempts raise;
4. repeats append → update → query 1000 times;
5. runs `doctor()` every 100 loops;
6. writes a JSON receipt.

Example:

```bash
python3 scripts/validate_incremental_update_1000.py \
  --source-hive ~/.memory-hive/hive \
  --loops 1000 \
  --report /tmp/memory-hive-incremental-1000.json
```

## Local proof snapshot

A local Travis-machine proof on 2026-05-13 copied `/Users/curnutte/.memory-hive/hive` into temporary sandboxes and measured one appended Hermes memory line.

- Baseline median update: `3261.901 ms`
- Patched median update: `219.541 ms`
- Median update speedup: `14.86x`
- 1000-loop result: `1000/1000` append → update → query loops passed
- Failures: `0`
- Doctor checks: `10`

These are local reproducible measurements, not a provider billing or universal latency claim.
