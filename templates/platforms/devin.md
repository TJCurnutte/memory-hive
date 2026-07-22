# Memory Hive wiring — Devin

**Detected dir:** `~/.config/devin/` (Devin CLI / Devin Desktop terminal)
**Target file:** `~/.config/devin/AGENTS.md`
**Integration:** auto-inject (managed block)

Devin reads `AGENTS.md` from your user config directory (`~/.config/devin/AGENTS.md`)
and applies it as global, always-on guidance for every session. The installer writes
the managed Memory Hive boot block between
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers.

## Devin Desktop (Windsurf rebrand)

Devin Desktop is a rebrand of Windsurf and continues to read the Windsurf global
rules file at `~/.codeium/windsurf/memories/global_rules.md`. That file is already
managed by the Windsurf integration (`MEMORY_HIVE_SKIP_WINDSURF`), so Devin Desktop
will pick up Memory Hive from there.

The Devin CLI (and Devin Desktop's terminal agent) also reads `~/.config/devin/AGENTS.md`,
so this integration makes Memory Hive explicit for the Devin CLI as well.

## v2 orchestration

Devin agents must follow Workflow 0 from the shared guide before every substantive
prompt. Keep the platform's configured agent id; when fanning out workers from a host
that exposes them, prefer Grok and Cursor/Composer family models before Devin fallbacks.

Re-runs are idempotent and preserve any content outside the managed markers.

Opt out with `MEMORY_HIVE_SKIP_DEVIN=1`.
