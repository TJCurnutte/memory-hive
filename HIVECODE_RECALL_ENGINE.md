# HiveCode Recall Engine

Status: design index for the `feat/recall-engine-codes` implementation loops.

The canonical loop-02 specification now lives at:

- [`docs/HIVECODE_ENGINE.md`](docs/HIVECODE_ENGINE.md)
- [`tests/HIVECODE_ACCEPTANCE_PLAN.md`](tests/HIVECODE_ACCEPTANCE_PLAN.md)

HiveCode is an optional, local-first recall index for Memory Hive. It makes per-turn Hive pulls fast, bounded, and citation-preserving as the hive grows. It never replaces Markdown source files; `hive/.hivecode/index.sqlite` is derived state that can be deleted and rebuilt.
