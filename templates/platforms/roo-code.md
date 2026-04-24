# Memory Hive wiring — Roo Code (VS Code)

**Detected dir:** `~/.roo/`
**Target file:** `~/.roo/rules/memory-hive.md`
**Integration:** auto-inject (managed block)

Roo Code reads global rules from `~/.roo/rules/*.md` (recursive,
alphabetical). The installer writes `memory-hive.md` with the managed
block between `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`
markers. Re-runs are idempotent.

When project-level rules (`<project>/.roo/rules/`) conflict with the
global hive rule, workspace rules take precedence — which is the correct
behavior, so Memory Hive doesn't fight your project-specific
conventions.

Opt out with `MEMORY_HIVE_SKIP_ROO_CODE=1`.

### Heads up

Roo Code's vendor has announced a shutdown for May 15, 2026. If you're
migrating, both **Cline** and **Kilo Code** are close successors — both
are supported by Memory Hive.
