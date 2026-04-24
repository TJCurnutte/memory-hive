# Memory Hive wiring — Crush (Charm)

**Detected dir:** `~/.local/share/crush/`
**Integration:** manual (Crush config is structured JSON; no markdown
rules file)

Crush stores config at `~/.local/share/crush/crush.json` (Unix) with
LSP, MCP, and permission settings. There's no standard user-level
markdown rules file the installer can write to safely.

## How to wire it

Crush reads `AGENTS.md` in your project root when present, same as the
emerging cross-tool standard. The cleanest option is to symlink the
hive's shared `AGENTS.md` into each project where you use Crush:

```bash
ln -s ~/.memory-hive/templates/claude-boot-block.md \
      <project>/AGENTS.md
```

Or paste the contents of the managed block into your project's existing
`AGENTS.md`.

Opt out with `MEMORY_HIVE_SKIP_CRUSH=1` (suppresses the install-time
note).
