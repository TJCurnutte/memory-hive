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

---

## Hive Swarm — multi-device compute mesh

If you're running multiple devices in a personal compute mesh via
[Hive Swarm](https://github.com/TJCurnutte/hive-swarm) (hardware-aware
swarm controller, GPU routing, carbon-aware scheduling — works with
Hermes Agent, OpenClaw, NanoClaw, or any agent runtime), Memory Hive
interoperates cleanly:

- **Mount the same `~/.memory-hive/hive/` on every node in the mesh**
  — via NFS, Syncthing, or a shared volume. Peer-spawned agents read
  the same shared brain regardless of which machine ran them.
- **Each node keeps its own local silo namespace.** A common
  convention is `agents/<hostname>-<role>/` so the laptop-coder and
  desktop-coder don't collide. Use `memory-hive add laptop-coder
  --role coder` etc.
- **`memory-hive bundle --for <agent>`** assembles a
  prompt-injection-ready context blob the swarm controller can ship
  to a remote worker, so a GPU node spawned by the swarm sees the
  same canonical truth as your local planner.

Memory Hive is the memory layer (what agents remember). Hive Swarm
is the compute layer (how/where agents run). They're orthogonal —
either works without the other, and they compose cleanly. Both ship
as part of the [neural-forge.io](https://neural-forge.io) family —
[memoryhive.neural-forge.io](https://memoryhive.neural-forge.io) and
[hiveswarm.neural-forge.io](https://hiveswarm.neural-forge.io).
