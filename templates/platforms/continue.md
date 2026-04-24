# Memory Hive wiring — Continue.dev

**Detected dir:** `~/.continue/`
**Target file:** `~/.continue/rules/memory-hive.md`
**Integration:** auto-inject (managed block)

Continue loads rule files from the `rules/` directory next to
`config.yaml`. The installer drops a single `memory-hive.md` rule that
contains the managed block, so every Continue model invocation (chat,
edit, apply) sees the hive instructions.

Markers: `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.
Re-runs are idempotent.

Opt out with `MEMORY_HIVE_SKIP_CONTINUE=1`.

### If you still use `config.json` (legacy)

Continue's new format is YAML (`~/.continue/config.yaml`). The rules
directory works for both old and new configs; nothing else needs to
change.
