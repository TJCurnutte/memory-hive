# HiveCode Recall Engine

Status: design index for the `feat/recall-engine-codes` implementation loops.

The canonical loop-02 specification now lives at:

- [`docs/HIVECODE_ENGINE.md`](docs/HIVECODE_ENGINE.md)
- [`tests/HIVECODE_ACCEPTANCE_PLAN.md`](tests/HIVECODE_ACCEPTANCE_PLAN.md)

HiveCode / HyperRecall is the built-in v1.1 local-first recall index for Memory Hive. Recall is an aspect of Memory Hive, not a separate product. It makes per-turn Hive pulls fast, bounded, and citation-preserving as the hive grows. It never replaces Markdown source files; `hive/.hivecode/index.sqlite` is derived state that can be deleted and rebuilt.
