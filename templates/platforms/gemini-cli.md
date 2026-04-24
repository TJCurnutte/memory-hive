# Memory Hive wiring — Gemini CLI

**Detected dir:** `~/.gemini/`
**Target file:** `~/.gemini/GEMINI.md`
**Integration:** auto-inject (managed block)

Gemini CLI reads `GEMINI.md` files for persistent project context. The
installer writes the managed block to `~/.gemini/GEMINI.md` (the
user-level context) so every `gemini` session loads the hive.

Markers: `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.
Re-runs are idempotent.

### Why not `system.md`?

Gemini CLI also supports a full system-prompt override via
`GEMINI_SYSTEM_MD` / `~/.gemini/system.md`, but using it replaces the
CLI's built-in core prompt entirely. That's a bigger swap than Memory
Hive needs — `GEMINI.md` gives the agents the hive instructions without
overriding safety defaults.

Opt out with `MEMORY_HIVE_SKIP_GEMINI_CLI=1`.
