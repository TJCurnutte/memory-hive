# Memory Hive wiring — Cursor

**Detected dir:** `~/.cursor/` or `.cursor/` in your current project
**Target file:** `~/.cursor/rules/memory-hive.mdc` (user-level rule)
**Integration:** auto-inject (managed block)

Cursor reads user-level rules from `~/.cursor/rules/*.mdc`. The installer
writes a single `memory-hive.mdc` file containing the managed block.

## v2 orchestration

Cursor agents must follow Workflow 0 from the shared guide before every
substantive prompt. Use agent-id `cursor`; when fanning out workers, prefer
Grok and Cursor/Composer family models when Cursor exposes them.

MDC rules are always-on unless you attach scoping metadata. The file the
installer writes has no glob scope, so the hive instructions apply to
every project you open in Cursor.

Re-runs refresh the managed block; nothing outside the
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers is
modified. If you want to disable Memory Hive on a per-project basis,
delete the rule from inside Cursor's rule picker — the file stays intact.

Opt out with `MEMORY_HIVE_SKIP_CURSOR=1`.

## Surface 2 — Harness hooks in `~/.cursor/hooks.json`

**Integration:** JSON merge via python3, version-1 hooks file

The rule asks the model to follow the memory contract; the hooks make
Cursor's agent harness enforce it mechanically:

| Hook event | Script | What it does |
|---|---|---|
| `stop` | `~/.memory-hive/hooks/cursor-stop.sh` | When an agent conversation completes without a fresh dated line in the agent's `log.md`, replies once with a `followup_message` telling the agent to run `memory-hive log` / `memory-hive learn`. Cursor's own `loop_count` is the loop guard (nudges only at 0); aborted/error runs and short transcripts are exempt. |
| `sessionEnd` | `~/.memory-hive/hooks/cursor-session-end.sh` | Ambient capture: appends a timestamped session-ended event (model, workspace) to `hive/raw/sessions/` via `memory-hive capture`. |

Both scripts fail open — missing hive, missing python3, unparseable
payload all exit 0 silently. The agent id defaults to `main`; set
`MEMORY_HIVE_AGENT_ID` to target another silo.

**Refresh semantics:** re-installing replaces only entries whose command
points at our `hooks/cursor-*.sh` scripts. Hooks you wrote yourself are
untouched; a malformed `hooks.json` is left alone (with a warning).

**Opt out:** `MEMORY_HIVE_SKIP_CURSOR_HOOKS=1` at install time, or export
`MEMORY_HIVE_HOOKS_DISABLE=1` at runtime to mute the installed hooks.
`MEMORY_HIVE_SKIP_CURSOR=1` skips both surfaces.

**Doctor coverage:** `memory-hive doctor` warns when the scripts are
missing or `hooks.json` no longer references them.

### Legacy `.cursorrules`

The older `.cursorrules` single-file format in project roots is still
supported by Cursor but deprecated. If you want the hive in a specific
project only, copy the managed block into `<project>/.cursorrules`
yourself.
