# Memory Hive wiring — NanoClaw

**Detected dir:** `~/.config/nanoclaw/` (or `~/.nanoclaw/`)
**Target file:** `~/.config/nanoclaw/AGENTS.md`
**Integration:** auto-inject (managed block)

NanoClaw (https://github.com/qwibitai/nanoclaw) is a lightweight,
container-isolated alternative to OpenClaw. It reads `AGENTS.md` for
persistent agent context.

The installer writes the managed block to `~/.config/nanoclaw/AGENTS.md`
between the `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`
markers. Re-runs are idempotent.

Opt out with `MEMORY_HIVE_SKIP_NANOCLAW=1`.

### Note on containers

If NanoClaw is running in a container, the hive directory
(`~/.memory-hive/hive/`) must be mounted into the container for agents to
actually read it. Add it to your NanoClaw mount-allowlist in
`~/.config/nanoclaw/mount-allowlist.json`.
