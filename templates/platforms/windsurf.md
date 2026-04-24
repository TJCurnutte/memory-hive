# Memory Hive wiring — Windsurf (Codeium)

**Detected dir:** `~/.codeium/windsurf/`
**Target file:** `~/.codeium/windsurf/memories/global_rules.md`
**Integration:** auto-inject (managed block)

Windsurf reads `global_rules.md` before any project-level rules. The
installer writes the managed block to
`~/.codeium/windsurf/memories/global_rules.md` between the
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers.
Re-runs are idempotent and preserve anything you've added outside the
markers.

Opt out with `MEMORY_HIVE_SKIP_WINDSURF=1`.

### If Cascade seems to ignore rules

There's a known issue where Cascade occasionally fails to apply
`global_rules.md` until you restart Windsurf. If the agent doesn't
acknowledge the hive, restart the editor once.
