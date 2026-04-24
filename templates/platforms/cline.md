# Memory Hive wiring — Cline (VS Code)

**Detected dir:** `~/.cline/`
**Integration:** manual (no standard user-level rules file)

Cline stores its global state at `~/.cline/globalState.json`, but custom
instructions are set inside the VS Code UI rather than a plain-text
config file. The installer doesn't edit VS Code state DBs.

## How to wire it

Open VS Code, hit the Cline extension settings, and paste the hive block
into the **Custom Instructions** field:

```
READ ~/.memory-hive/hive/index.md before responding.
READ ~/.memory-hive/hive/agents/<your-agent-id>/memory.md.
READ ~/.memory-hive/hive/agents/<your-agent-id>/log.md.
READ ~/.memory-hive/hive/knowledge/HUMAN_CONTEXT.md if it exists.

Write only to your own silo (hive/agents/<your-agent-id>/) and
hive/learnings/raw/. Never write to other agents' silos or to
hive/knowledge/ — that's the curator's job.

Full boot contract: ~/.memory-hive/templates/claude-boot-block.md
```

For project-level instead of global wiring, drop the same block into
`<project>/.clinerules/memory-hive.md` — Cline auto-loads everything
under `.clinerules/`.

Opt out with `MEMORY_HIVE_SKIP_CLINE=1` (suppresses the install-time
note).
