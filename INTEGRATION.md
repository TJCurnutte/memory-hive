# Integration

How Memory Hive wires itself into your existing agent environment after
`curl -fsSL memoryhive.neural-forge.io/install.sh | sh`.

## What the installer does

The installer auto-detects your environment and drops the hive at
`~/.memory-hive/`. It then adapts based on what it finds.

### Claude Code users

If `~/.claude/` exists, the installer injects a managed fenced block into
`~/.claude/CLAUDE.md`:

```
<!-- memory-hive:start -->
...boot instructions...
<!-- memory-hive:end -->
```

Every Claude Code agent reads `CLAUDE.md` on boot, so this tells them all
to load the hive before responding. The block is **idempotent**: re-running
the installer finds the markers and replaces the block in place. Anything
outside the markers — your own notes, other tools' blocks — is never
touched. The canonical content lives in
[`templates/claude-boot-block.md`](templates/claude-boot-block.md); the
installer substitutes `${HIVE_DIR}` at install time.

### OpenClaw users

If `~/.openclaw/` exists, the installer still writes to `~/.memory-hive/`
(to keep the upgrade path clean), then prints a note:

```
openclaw detected — to use the hive under your openclaw root, run:
  ln -s ~/.memory-hive ~/.openclaw/hive
  # or: cp -r ~/.memory-hive ~/.openclaw/hive
```

### Generic users

If neither is found, the installer prints where the files live
(`~/.memory-hive/`) and a short snippet showing how to point any agent
framework at `index.md` and a per-agent silo.

## Per-agent silos

The installer scans `~/.claude/agents/` and creates a matching silo under
`~/.memory-hive/hive/agents/<name>/` for every agent it finds. A `main`
silo is always created for ad-hoc use even if no agents are detected.

### What's in a silo

- `log.md` — running journal of what the agent did, session by session
- `context.md` — agent-specific state, preferences, and working config
- `memory.md` — private learnings this agent wants to remember

## Re-installing

Safe. The installer refreshes the shared hive (`index.md`, `knowledge/`,
`registry/`, etc.) and the managed CLAUDE.md block. Agent silos'
`log.md`, `context.md`, and `memory.md` are left alone — your agents
keep their memory across upgrades.

## Uninstalling

```bash
rm -rf ~/.memory-hive
# then open ~/.claude/CLAUDE.md and delete the block between
# <!-- memory-hive:start --> and <!-- memory-hive:end -->
```

That's it. No other files are modified.
