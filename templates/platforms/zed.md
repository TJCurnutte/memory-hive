# Memory Hive wiring — Zed

**Detected dir:** `~/.config/zed/`
**Integration:** manual (user-level system prompts live in Zed's agent
settings UI, not a stable plain-text file)

Zed's AI agent reads project-level custom system prompts from
`<project>/.zed/prompts/*.md`. There's no equally stable global path in
2026 that the installer can write to without touching `settings.json`
directly.

## How to wire it

### Option A — per-project (recommended)

Create `.zed/prompts/memory-hive.md` in each project where you want the
hive active and paste the managed block from
`~/.memory-hive/templates/claude-boot-block.md`.

### Option B — global, via Zed settings

Open `~/.config/zed/settings.json` and add the Memory Hive boot
instructions to your agent's `system_prompt` field. You'll want to keep
the rest of the agent settings intact, so copy-paste the **contents of
the managed block** (not the markers) into your existing system prompt.

Opt out with `MEMORY_HIVE_SKIP_ZED=1`.
