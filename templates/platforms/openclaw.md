# Memory Hive wiring — OpenClaw

**Detected dir:** `~/.openclaw/`
**Target file:** `~/.openclaw/CLAUDE.md`
**Integration:** auto-inject (managed block)

OpenClaw reads `~/.openclaw/CLAUDE.md` on session start. The installer
writes the same managed block it writes for Claude Code, so OpenClaw
agents load the hive on boot.

The block uses the `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`
markers. Re-running the installer refreshes the block in place; nothing
outside the markers is modified.

Opt out with `MEMORY_HIVE_SKIP_OPENCLAW=1`.

### Alternative setup

If you prefer a single hive shared between OpenClaw and Memory Hive,
symlink or copy after install:

```bash
ln -s ~/.memory-hive ~/.openclaw/hive
# or
cp -r ~/.memory-hive ~/.openclaw/hive
```
