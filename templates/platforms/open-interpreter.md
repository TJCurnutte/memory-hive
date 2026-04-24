# Memory Hive wiring — Open Interpreter

**Detected marker:** `~/.config/open-interpreter/` exists, or
`interpreter` on PATH
**Integration:** manual (profile YAML is structured; unsafe to splice)

Open Interpreter uses profile YAML files (e.g. `default.yaml`) for
configuration, including `custom_instructions`. Since the `custom_instructions`
field is a single multi-line string inside a structured YAML file, the
installer won't auto-edit it — that's the kind of change that is
supposed to be deliberate.

## How to wire it

Edit your profile (default location:
`~/.config/open-interpreter/profiles/default.yaml`) and set:

```yaml
custom_instructions: |
  Before doing anything else, READ the Memory Hive files:
  1. ~/.memory-hive/hive/index.md
  2. ~/.memory-hive/hive/agents/<your-agent-id>/memory.md
  3. ~/.memory-hive/hive/agents/<your-agent-id>/log.md
  4. ~/.memory-hive/hive/knowledge/HUMAN_CONTEXT.md (if it exists)

  Write only to your own silo (hive/agents/<your-agent-id>/) and
  hive/learnings/raw/. Never write to other agents' silos or to
  hive/knowledge/.

  Full boot contract: ~/.memory-hive/templates/claude-boot-block.md
```

After editing, restart Open Interpreter.

Opt out with `MEMORY_HIVE_SKIP_OPEN_INTERPRETER=1` (suppresses the
detection note during install).
