# Memory Hive wiring — OpenAI Codex CLI

**Detected dir:** `~/.codex/`
**Target file:** `~/.codex/AGENTS.md`
**Integration:** auto-inject (managed block)

Codex CLI reads `AGENTS.md` from `$CODEX_HOME` (default `~/.codex/`) for
every session — it's the user-level "global guidance" layer in Codex's
instruction chain. The managed block instructs Codex to pull Memory Hive on
boot and re-pull relevant hive context before substantive prompts/tasks. The
installer writes the managed block between `<!-- memory-hive:start -->` /
`<!-- memory-hive:end -->` markers.

Re-runs are idempotent. Codex caps `AGENTS.md` at 32 KiB and truncates
silently past that, but the managed block is ~1.6 KB so you have plenty
of headroom.

If you prefer to shadow `AGENTS.md` on the fly without touching it,
Codex also reads `AGENTS.override.md` with higher priority — drop one
there and the installer's block won't be seen that session.

Opt out with `MEMORY_HIVE_SKIP_CODEX=1`.
