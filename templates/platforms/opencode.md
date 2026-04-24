# Memory Hive wiring — OpenCode

**Detected dir:** `~/.config/opencode/`
**Target file:** `~/.config/opencode/AGENTS.md`
**Integration:** auto-inject (managed block)

OpenCode reads `AGENTS.md` files as default instructions and also lets
you point at any markdown via the `instructions` array in
`~/.config/opencode/opencode.json`. The installer writes the managed
block to `~/.config/opencode/AGENTS.md` between
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers so
the hive loads without any JSON edits.

Re-runs are idempotent.

Opt out with `MEMORY_HIVE_SKIP_OPENCODE=1`.
