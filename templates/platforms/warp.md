# Memory Hive wiring — Warp

**Detected dir:** `~/.warp/`
**Target file:** `~/.agents/AGENTS.md`
**Integration:** auto-inject (managed block)

Warp reads global `AGENTS.md` files from `~/.agents/` (the standard
cross-tool location Warp now honors). The installer writes the managed
block to `~/.agents/AGENTS.md` between the `<!-- memory-hive:start -->`
/ `<!-- memory-hive:end -->` markers.

Re-runs are idempotent. Nothing outside the markers is touched, so any
other guidance you've put in the global `AGENTS.md` is preserved.

Opt out with `MEMORY_HIVE_SKIP_WARP=1`.

### Warp-specific filename rule

Warp requires `AGENTS.md` to be in ALL CAPS exactly — `agents.md` or
`Agents.md` won't be picked up. The installer writes the correct case.
