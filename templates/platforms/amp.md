# Memory Hive wiring — Sourcegraph Amp

**Detected marker:** `~/.config/amp/` exists, or `amp` on PATH
**Target file:** `~/.config/amp/AGENTS.md`
**Integration:** auto-inject (managed block)

Amp looks for `AGENTS.md` in the current working directory, parent
directories up to `$HOME`, and two well-known global locations:
`~/.config/amp/AGENTS.md` and `~/.config/AGENTS.md`.

The installer writes the managed block to `~/.config/amp/AGENTS.md` so
the instructions are scoped to Amp specifically. Markers:
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.

Re-runs are idempotent.

Opt out with `MEMORY_HIVE_SKIP_AMP=1`.
