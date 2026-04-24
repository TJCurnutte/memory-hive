# Memory Hive wiring — Hermes Agent

**Detected dir:** `~/.hermes/`
**Target file:** `~/.hermes/memories/MEMORY.md`
**Integration:** auto-inject (managed block, append-safe)

Hermes Agent (Nous Research) layers its system prompt as
`SOUL.md` → `USER.md` → `AGENTS.md` → `MEMORY.md`. The installer writes
the managed block into `MEMORY.md` so every session loads the hive.

Markers: `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.
Hermes caps `MEMORY.md` at ~2,200 characters by default
(`memory_char_limit` in `~/.hermes/config.yaml`) — the block is about
1,600 chars, so you have headroom for your own curated facts.

The installer preserves anything outside the markers — your
agent-curated memory entries are untouched.

Opt out with `MEMORY_HIVE_SKIP_HERMES=1`.
