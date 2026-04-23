# Integration

How Memory Hive wires itself into your existing agent environment after
`curl -fsSL memoryhive.neural-forge.io/install.sh | sh`.

## What the installer does

The installer drops the hive at `~/.memory-hive/` (override with
`MEMORY_HIVE_DIR=/custom/path`), detects your environment, and adapts.

### The wizard (interactive terminal)

If the installer has a real tty — a normal shell, or a `curl | sh`
pipeline that can still reach `/dev/tty` — it launches an interactive
wizard. Three paths, depending on what's already on disk:

1. **Fresh hive, no pre-existing agents elsewhere.** The wizard asks how
   many agents you want beyond the curator, collects a name and optional
   role template for each, and scaffolds one silo per agent.
2. **Fresh hive, but agents exist elsewhere** (`~/.claude/agents/` or
   `~/.openclaw/hive/agents/`). The wizard offers an **import flow**:
   - `[i] Import all` (default) — create a silo in `~/.memory-hive/`
     for each detected agent. Role is seeded from the source's existing
     `context.md` if non-placeholder, else from a name-matched template
     (e.g. `security-auditor` → `reviewer`, `content-strategist` →
     `writer`). `log.md` and `memory.md` copy across when the
     destination is empty.
   - `[s] Select` — walk the list, pick which ones to import.
   - `[n] Skip` — start fresh with the wizard instead.
3. **Re-install over an existing hive.** The wizard offers four
   reconciliation choices:
   - `[k] Keep` (default) — refresh the managed block and shared hive
     files; leave agents alone.
   - `[a] Add` — run the wizard alongside existing agents.
   - `[f] Fresh` — archive every non-`main` agent to
     `hive/agents/_archived/<date>/`, then run the wizard.
   - `[s] Select` — walk each existing agent, keep or archive.

Nothing is ever deleted. Archiving is a `mv` into `_archived/`, and you
can restore an agent by moving it back.

### Non-interactive fallback (CI, `< /dev/null`, no tty reachable)

The installer creates just the `main` curator silo and prints a
one-liner for adding more agents later. Backward-compatible with any
CI pipeline or scripted install.

### Claude Code users

If `~/.claude/` exists, the installer injects a managed fenced block
into `~/.claude/CLAUDE.md`:

```
<!-- memory-hive:start -->
...boot instructions...
<!-- memory-hive:end -->
```

Every Claude Code agent reads `CLAUDE.md` on boot, so this tells them
all to load the hive before responding. The block is **idempotent**:
re-running the installer finds the markers and replaces the block in
place. Anything outside the markers — your own notes, other tools'
blocks — is never touched. The canonical content lives in
[`templates/claude-boot-block.md`](templates/claude-boot-block.md);
the installer substitutes `${HIVE_DIR}` and `${INSTALL_DIR}` at install
time.

Opt out with `MEMORY_HIVE_SKIP_CLAUDE_MD=1` if you manage that file by
hand.

### OpenClaw users

If `~/.openclaw/` exists, the installer still writes to
`~/.memory-hive/` (to keep the upgrade path clean), and — if you have
agents under `~/.openclaw/hive/agents/` — offers to import them via
the wizard (see above). If you prefer to keep a single root, either
symlink or copy after install:

```bash
ln -s ~/.memory-hive ~/.openclaw/hive
# or
cp -r ~/.memory-hive ~/.openclaw/hive
```

### Generic users

If neither is found, the installer prints where the files live
(`~/.memory-hive/`) and a short snippet showing how to point any agent
framework at `hive/index.md` and a per-agent silo.

## Managing agents after install

Once the hive is in place, the `memory-hive` CLI is the everyday entry
point:

```bash
sh ~/.memory-hive/memory-hive add backend-eng --role coder
sh ~/.memory-hive/memory-hive list
sh ~/.memory-hive/memory-hive rename backend-eng api-eng
sh ~/.memory-hive/memory-hive archive api-eng
sh ~/.memory-hive/memory-hive role api-eng   # opens $EDITOR on context.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev workflow and
[MIGRATION.md](MIGRATION.md) for upgrade paths from older setups.

## What's in a silo

Each agent's private directory under `hive/agents/<id>/` contains:

- `log.md` — running journal of what the agent did, session by session
- `context.md` — agent-specific state, role, preferences, working config
- `memory.md` — private learnings this agent wants to remember

The wizard and CLI seed these from the selected role template. The
agent edits them freely over time.

## Re-installing

Safe. The installer refreshes the shared hive (`index.md`, `knowledge/`,
`registry/`, etc.) and the managed `CLAUDE.md` block. Existing silo
files (`log.md`, `context.md`, `memory.md`) are **never** overwritten
— your agents keep their memory across upgrades.

If you want a different roster than last time, the re-install
reconciliation flow (above) lets you add or archive without losing the
silos you keep.

## Environment variables

| Variable | Purpose |
|---|---|
| `MEMORY_HIVE_DIR` | Install location (default: `$HOME/.memory-hive`) |
| `MEMORY_HIVE_REPO` | Install from a local working copy instead of cloning GitHub. Points at a directory with a `hive/` subdir. |
| `MEMORY_HIVE_SKIP_CLAUDE_MD` | Set to `1` to skip the managed block in `~/.claude/CLAUDE.md`. |

## Uninstalling

```bash
rm -rf ~/.memory-hive
# then open ~/.claude/CLAUDE.md and delete the block between
# <!-- memory-hive:start --> and <!-- memory-hive:end -->
```

That's it. No other files are modified.
