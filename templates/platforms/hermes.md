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

## Crash-recovery companion

For long-running local Hermes setups, pair Memory Hive with a small
machine-local recovery folder such as `~/.hermes/crash-recovery/`.
Memory Hive remains the durable memory layer; the recovery folder is only
for bootstrapping after a crash, recording local process/service state, and
keeping the restart queue visible before the agent has fully reloaded its
hive silo.

Recommended files:

```text
SESSION.md    current session and machine state
ACTIVITY.md   timestamped recovery activity
PENDING.md    prioritized restart queue
DECISIONS.md  recovery decisions and rationale
```

See [`examples/hermes-crash-recovery/`](../../examples/hermes-crash-recovery/)
for a copyable layout.

For runtime integrations that use Memory Hive as a programmatic memory backend
(instead of plain file reads), follow the standard adapter surface in
[`MEMORY_ADAPTER_CONTRACT.md`](../../MEMORY_ADAPTER_CONTRACT.md).

---

## Swarm routing — built into Memory Hive

Do not treat Hive Swarm as a separate required product or repository. The
canonical GitHub home for Hive work is
[Memory Hive](https://github.com/TJCurnutte/memory-hive); swarm routing is a
Memory Hive capability that helps decide how/where agents run.

When running multiple devices in a personal compute mesh:

- **Mount the same `~/.memory-hive/hive/` on every node in the mesh**
  — via NFS, Syncthing, or a shared volume. Peer-spawned agents read
  the same shared brain regardless of which machine ran them.
- **Each node keeps its own local silo namespace.** A common convention is
  `agents/<hostname>-<role>/` so laptop-coder and desktop-coder do not collide.
  Use `memory-hive add laptop-coder --role coder` etc.
- **`memory-hive bundle --for <agent>`** assembles a prompt-injection-ready
  context blob a controller can ship to a remote worker, so a GPU node sees the
  same canonical truth as the local planner.
- **`memory-hive optimize --report <file>`** emits compact health/routing
  signals that help decide whether to fan out, pause for repair, or route first
  to a curator/reviewer lane.

Memory Hive is the memory, optimizer, and swarm-signal layer. Separate
Hive-branded repos should fold back into Memory Hive instead of becoming new
product surfaces.
