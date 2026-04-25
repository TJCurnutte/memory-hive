# Migration

Upgrade paths into Memory Hive from the setups people commonly arrive
from. All of them route through the interactive installer at
`~/.memory-hive/install.sh` (or `curl -fsSL
memoryhive.neural-forge.io/install.sh | sh`) — nothing here requires
manual file surgery.

For the full wizard behavior see [INTEGRATION.md](INTEGRATION.md).

---

## From an OpenClaw hive

Scenario: you already have a populated `~/.openclaw/hive/agents/` —
maybe thirteen silos, each with their own `log.md`, `memory.md`, and
domain history built up over months.

1. Run the installer:
   ```bash
   curl -fsSL memoryhive.neural-forge.io/install.sh | sh
   ```
2. The wizard detects `~/.openclaw/hive/agents/` and offers an **import
   flow**:
   ```
   [i] Import all (default) — scaffold a silo for each, seed from OpenClaw if present
   [s] Select — pick which ones to import
   [n] Skip — start fresh with the wizard instead
   ```
3. Pick `[i]`. The installer:
   - creates a silo in `~/.memory-hive/hive/agents/<name>/` for each
     detected agent
   - seeds the role from the source's existing `context.md` if it has
     non-placeholder content, else matches a role template by name
     (e.g. `security-auditor` → `reviewer`, `content-strategist` →
     `writer`, `coder` → `coder`)
   - copies `log.md` and `memory.md` from OpenClaw when the
     destination file is empty (never overwrites)
4. Your OpenClaw directory is untouched. The installer reads from it;
   it never writes.

If you want a single root going forward, either symlink or copy after
the import:

```bash
ln -s ~/.memory-hive ~/.openclaw/hive
# or
cp -r ~/.memory-hive ~/.openclaw/hive
```

---

## From a bare Claude Code setup

Scenario: you have `~/.claude/` and possibly `~/.claude/agents/` with
sub-agent definitions, but no hive yet.

1. Run the installer. It detects `~/.claude/` and will inject the
   managed block into `~/.claude/CLAUDE.md` (opt out with
   `MEMORY_HIVE_SKIP_CLAUDE_CODE=1`; the legacy
   `MEMORY_HIVE_SKIP_CLAUDE_MD=1` is still honored as an alias).
2. If `~/.claude/agents/` has sub-agents, the wizard offers the same
   import flow as the OpenClaw case — `[i] Import all` scaffolds a
   silo per sub-agent.
3. If `~/.claude/agents/` is empty or missing, the wizard goes to the
   fresh flow: you pick how many agents you want and name them.

From this point on, every Claude Code agent reads the hive on boot via
the managed `CLAUDE.md` block. No code changes needed on your side.

---

## From a pre-0.1 hardcoded-roster hive

Scenario: you installed Memory Hive before the `feat/dynamic-agents`
rewrite landed, so your `~/.memory-hive/hive/agents/` contains the old
author-specific roster that used to ship with the repo.

1. Re-run the installer against the same directory:
   ```bash
   sh ~/.memory-hive/install.sh
   ```
   (or the `curl` one-liner — same effect.)
2. The wizard sees non-`main` silos already on disk and offers
   **reconciliation**:
   ```
   [k] Keep existing (default) — just update the managed block and shared hive
   [a] Add more alongside existing
   [f] Fresh start — archive existing agents to hive/agents/_archived/<date>/
   [s] Select — review each and keep or archive
   ```
3. Pick the option that matches what you want:
   - `[k]` if the old roster still fits.
   - `[f]` to archive all of them and start clean — nothing is deleted;
     everything moves to `hive/agents/_archived/<date>/`.
   - `[s]` to walk each and decide individually.

After reconciliation, use `memory-hive add/archive/rename` to keep the
roster tidy.

---

## Rolling back

Every non-destructive flow archives instead of deletes. If you
change your mind:

```bash
# where did it go?
ls ~/.memory-hive/hive/agents/_archived/

# restore a specific silo
mv ~/.memory-hive/hive/agents/_archived/<date>/<agent-name> \
   ~/.memory-hive/hive/agents/<agent-name>
```

The `log.md`, `context.md`, and `memory.md` inside are byte-for-byte
what they were pre-archive.

If the installer's managed block in `~/.claude/CLAUDE.md` is pointing
at the wrong path (e.g. after a test run hijacked it to a temp dir),
just re-run the installer — the block is idempotent and fixes itself.

---

## Nothing fits my setup

If your existing agent roster lives somewhere the installer doesn't
scan, the path is the same two-step:

1. Run the installer. Pick the fresh flow to scaffold blank silos.
2. Manually populate each silo's `log.md` / `memory.md` from whatever
   source you're migrating. The silo files are plain Markdown — no
   schema to respect, just consistent headings.

Or, if you have many agents, point `MEMORY_HIVE_REPO` at a local copy
of the repo and run the installer from a script that pre-seeds the
silo dirs before the wizard runs.

---

**The hive is additive. Upgrading never loses memory.**
