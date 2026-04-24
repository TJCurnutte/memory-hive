# Memory Hive wiring — Cursor

**Detected dir:** `~/.cursor/` or `.cursor/` in your current project
**Target file:** `~/.cursor/rules/memory-hive.mdc` (user-level rule)
**Integration:** auto-inject (managed block)

Cursor reads user-level rules from `~/.cursor/rules/*.mdc`. The installer
writes a single `memory-hive.mdc` file containing the managed block.

MDC rules are always-on unless you attach scoping metadata. The file the
installer writes has no glob scope, so the hive instructions apply to
every project you open in Cursor.

Re-runs refresh the managed block; nothing outside the
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers is
modified. If you want to disable Memory Hive on a per-project basis,
delete the rule from inside Cursor's rule picker — the file stays intact.

Opt out with `MEMORY_HIVE_SKIP_CURSOR=1`.

### Legacy `.cursorrules`

The older `.cursorrules` single-file format in project roots is still
supported by Cursor but deprecated. If you want the hive in a specific
project only, copy the managed block into `<project>/.cursorrules`
yourself.
