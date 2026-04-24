# Memory Hive wiring — Claude Code

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

Opt out with `MEMORY_HIVE_SKIP_CLAUDE_CODE=1` (or the legacy
`MEMORY_HIVE_SKIP_CLAUDE_MD=1`, still honored) if you manage that file by
hand.

The canonical block content lives in
[`templates/claude-boot-block.md`](../claude-boot-block.md); the
installer substitutes `${HIVE_DIR}` and `${INSTALL_DIR}` at install time.
