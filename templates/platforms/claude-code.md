# Memory Hive wiring — Claude Code

Claude Code gets two Memory Hive surfaces installed together.

---

## Surface 1 — Managed block in `~/.claude/CLAUDE.md`

**Detected file:** `~/.claude/CLAUDE.md`
**Integration:** auto-inject (managed block)

When Memory Hive detects Claude Code (`~/.claude/` exists), it writes a
managed block to `~/.claude/CLAUDE.md` between these markers:

```
<!-- memory-hive:start -->
...boot instructions...
<!-- memory-hive:end -->
```

Every Claude Code session reads `CLAUDE.md` on boot, so this tells all of
your Claude Code agents (main + sub-agents) to load the hive before
responding. The block is idempotent: re-running the installer replaces it
in place and never touches content outside the markers.

**Purpose:** always-on boot contract — hydrate before work, write back after.

**Source template:** [`templates/claude-boot-block.md`](../claude-boot-block.md)
The installer substitutes `${HIVE_DIR}` and `${INSTALL_DIR}` at install time.

**Opt out:** `MEMORY_HIVE_SKIP_CLAUDE_CODE=1` (or legacy
`MEMORY_HIVE_SKIP_CLAUDE_MD=1`) — skips both the block and the Agent Skill.

---

## Surface 2 — Agent Skill at `~/.claude/skills/memory-hive/SKILL.md`

**Integration:** rendered from template, written on install

The installer renders and writes a native Claude Code Agent Skill to
`~/.claude/skills/memory-hive/SKILL.md`.

**Purpose:** on-demand depth layer — Claude Code loads only the skill's
one-line description into every session and pulls the full body (retrieval
verb guide, exact raw-learning frontmatter that passes lint, lane rules,
curator loop, troubleshooting) only when memory work is actually happening.
Progressive disclosure instead of a permanent context tax. Also user-invocable
as `/memory-hive` inside any Claude Code session.

**Source templates:** the YAML frontmatter head at
[`templates/skills/memory-hive/SKILL.md`](../skills/memory-hive/SKILL.md)
plus the platform-neutral body at [`templates/guide.md`](../guide.md) —
the same guide every other platform prints with `memory-hive guide`, so
the Claude skill and the cross-platform guide cannot drift apart. The
installer concatenates them, renders `${HIVE_DIR}` and `${INSTALL_DIR}`
placeholders to real paths, and writes the result. The unrendered sources
are also shipped under `~/.memory-hive/templates/` for inspection.

**Refresh semantics:** re-installing overwrites the skill file in place. The
whole file is installer-managed; no markers are needed because the file must
start with YAML frontmatter.

**Opt out:** `MEMORY_HIVE_SKIP_CLAUDE_SKILL=1` — skips the skill only; the
managed block is still written.

**Doctor coverage:** `memory-hive doctor` checks that the skill file exists
and references the current install, and warns with a re-install hint if not.

---

## Uninstalling

```bash
rm -rf ~/.claude/skills/memory-hive
# then open ~/.claude/CLAUDE.md and delete the block between
# <!-- memory-hive:start --> and <!-- memory-hive:end -->
```
