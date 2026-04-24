# Memory Hive wiring — Kilo Code (VS Code / JetBrains / CLI)

**Detected dir:** `~/.kilocode/`
**Target file:** `~/.kilocode/rules/memory-hive.md`
**Integration:** auto-inject (managed block)

Kilo Code (https://kilo.ai) loads rules from `.kilocode/rules/*.md`
(project) and `~/.kilocode/rules/*.md` (global). The installer drops one
global rule — `memory-hive.md` — with the managed block between
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers.

Re-runs are idempotent. Project-level rules override globals, which is
the correct direction.

Opt out with `MEMORY_HIVE_SKIP_KILO_CODE=1`.
