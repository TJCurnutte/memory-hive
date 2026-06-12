# Integration

How Memory Hive wires itself into your existing agent environment after
`curl -fsSL https://hive.neural-forge.io/install.sh | sh`.

## Supported platforms

The installer auto-detects every major agent platform that exposes a
stable plain-text config file, writes a managed block, and exits. Platforms
where the only configuration lives inside a structured YAML/JSON file
(where in-place splicing is unsafe) get printed manual instructions
instead. Every auto-inject wiring uses the same `<!-- memory-hive:start -->` /
`<!-- memory-hive:end -->` markers, so re-runs are idempotent and user
content outside the markers is never touched.

| Platform | Detection | Integration | Config target |
|---|---|---|---|
| Claude Code | `~/.claude/` | auto-inject | `~/.claude/CLAUDE.md` |
| OpenClaw | `~/.openclaw/` | auto-inject | `~/.openclaw/CLAUDE.md` |
| NanoClaw | `~/.config/nanoclaw/` | auto-inject | `~/.config/nanoclaw/AGENTS.md` |
| Hermes Agent | `~/.hermes/` | auto-inject | `~/.hermes/memories/MEMORY.md` |
| Cursor | `~/.cursor/` | auto-inject | `~/.cursor/rules/memory-hive.mdc` |
| Continue.dev | `~/.continue/` | auto-inject | `~/.continue/rules/memory-hive.md` |
| Aider | `~/.aider.conf.yml` or `aider` on PATH | manual | `~/.aider.conf.yml` (structured YAML) |
| Gemini CLI | `~/.gemini/` | auto-inject | `~/.gemini/GEMINI.md` |
| Goose (Block) | `~/.config/goose/` or `~/.goose/` | auto-inject | `~/.goosehints` |
| Open Interpreter | `~/.config/open-interpreter/` or `interpreter` on PATH | manual | profile YAML |
| Amazon Q Developer CLI | `~/.aws/amazonq/` | auto-inject | `~/.aws/amazonq/rules/memory-hive.md` |
| OpenHands | `~/.openhands/` | auto-inject | `~/.openhands/microagents/memory-hive.md` |
| Cline (VS Code) | `~/.cline/` | manual | VS Code settings UI |
| Roo Code | `~/.roo/` | auto-inject | `~/.roo/rules/memory-hive.md` |
| Kilo Code | `~/.kilocode/` | auto-inject | `~/.kilocode/rules/memory-hive.md` |
| Windsurf (Codeium) | `~/.codeium/windsurf/` | auto-inject | `~/.codeium/windsurf/memories/global_rules.md` |
| Zed | `~/.config/zed/` | manual | `~/.config/zed/settings.json` |
| Warp | `~/.warp/` | auto-inject | `~/.agents/AGENTS.md` |
| Sourcegraph Amp | `~/.config/amp/` or `amp` on PATH | auto-inject | `~/.config/amp/AGENTS.md` |
| OpenAI Codex CLI | `~/.codex/` | auto-inject | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/` | auto-inject | `~/.config/opencode/AGENTS.md` |
| Crush (Charm) | `~/.local/share/crush/` | manual | project-level `AGENTS.md` |
| GitHub Copilot (repo) | `MEMORY_HIVE_COPILOT_REPO=1` + `$PWD/.git/` | auto-inject (opt-in) | `$PWD/.github/copilot-instructions.md` |

Every platform has a dedicated doc under
[`templates/platforms/<id>.md`](templates/platforms/) with the exact
integration details, and the installer ships all of them into
`~/.memory-hive/templates/platforms/` so you can read them post-install.

## What the installer does

The installer drops the hive at `~/.memory-hive/` (override with
`MEMORY_HIVE_DIR=/custom/path`), detects your environment, and adapts.

### The wizard (opt-in interactive terminal)

The default installer path is zero-input so `curl | sh`, CI, and scripted
installs stay boring. To launch the interactive wizard, set
`MEMORY_HIVE_WIZARD=1` or run `memory-hive setup` after install.

When enabled, the wizard has three paths, depending on what's already on disk:

1. **Fresh hive, no pre-existing agents elsewhere.** The wizard asks how
   many agents you want beyond the curator, collects a name and optional
   role template for each, and scaffolds one silo per agent.
2. **Fresh hive, but agents exist elsewhere** (`~/.claude/agents/` or
   `~/.openclaw/hive/agents/`). The wizard offers an **import flow**:
   - `[i] Import all` (default) — create a silo in `~/.memory-hive/`
     for each detected agent. Role is seeded from the source's existing
     `context.md` if non-placeholder, else from a name-matched template
     (e.g. `security-auditor` → `reviewer`, `content-strategist` →
     `writer`). `log.md` and `memory.md` copy across when the
     destination is empty.
   - `[s] Select` — walk the list, pick which ones to import.
   - `[n] Skip` — start fresh with the wizard instead.
3. **Re-install over an existing hive.** The wizard offers four
   reconciliation choices:
   - `[k] Keep` (default) — refresh the managed block and shared hive
     files; leave agents alone.
   - `[a] Add` — run the wizard alongside existing agents.
   - `[f] Fresh` — archive every non-`main` agent to
     `hive/agents/_archived/<date>/`, then run the wizard.
   - `[s] Select` — walk each existing agent, keep or archive.

Nothing is ever deleted. Archiving is a `mv` into `_archived/`, and you
can restore an agent by moving it back.

### Non-interactive fallback (CI, `< /dev/null`, no tty reachable)

The installer creates just the `main` curator silo and prints a
one-liner for adding more agents later. Backward-compatible with any
CI pipeline or scripted install.

### The deep guide — every platform

The managed block each platform receives is deliberately tiny: it has to
ride along in every session. Deep operating knowledge — the retrieval verb
guide, the exact raw-learning frontmatter that passes lint, lane rules, the
curator loop — lives in one platform-neutral document instead:
[`templates/guide.md`](templates/guide.md).

Any agent on any platform pulls it on demand:

```bash
memory-hive guide            # full guide, rendered with this install's real paths
memory-hive guide write      # one section: paths|id|hydrate|retrieve|write|lanes|curate|health
```

The managed block points agents at this verb (`### Going deeper`), so
Cursor, Codex, Gemini CLI, Goose, Warp, Amp, OpenCode, and the rest get the
same progressive disclosure Claude Code gets — the boot surface stays
small, and depth is a shell call away. The installer ships the unrendered
guide to `~/.memory-hive/templates/guide.md`; `memory-hive guide`
substitutes `${HIVE_DIR}` / `${INSTALL_DIR}` at read time, and
`memory-hive doctor` warns if the shipped copy goes missing.

The write-back half of the contract is executable too — the boot block on
every platform instructs agents to run these instead of hand-writing files:

```bash
memory-hive log --agent <id> "<what you did, one line>"
memory-hive learn --agent <id> "<imperative rule>" --context "<where>" --kind pattern
```

`learn` writes the raw learning to the canonical
`learnings/raw/<id>/YYYY-MM-DD-<slug>.md` path with frontmatter that
passes `memory-hive lint` by construction, regardless of which model or
harness invoked it.

### The MCP server — any MCP client

Tools that speak the Model Context Protocol (Claude Desktop/Code, Cursor,
Goose, GitHub Copilot, ...) can skip files entirely and get the hive as
native tools:

```bash
memory-hive mcp --config   # print this install's client config snippet
```

```json
{
  "mcpServers": {
    "memory-hive": {
      "command": "python3",
      "args": ["~/.memory-hive/memory_hive_mcp.py"]
    }
  }
}
```

The server (stdio, stdlib-python only) exposes `ask_hive` (ranked, cited
retrieval over HyperRecall with a plain-search fallback), `hive_log`,
`hive_learn`, `hive_capture`, and `hive_guide`. Retrieval and write-back
stay lane-correct because every tool call goes through the same CLI verbs
documented above. `memory-hive doctor` warns if the helper goes missing.

### Ambient capture — memory without a ritual

`memory-hive capture "<event>" [--source <name>] [--agent <id>]` appends a
timestamped line to `hive/raw/<source>/YYYY-MM-DD.md` — the Tier-1
append-only stream from `hive/raw/`'s convention. It is searchable via
`query`/`recall` immediately and distilled by the curator later. The
Claude Code SessionEnd hook feeds `hive/raw/sessions/` automatically, so a
trace of every session exists even when the model never wrote back; other
harnesses can do the same from cron or their own hook systems by calling
the verb.

### Claude Code users

If `~/.claude/` exists, the installer injects a managed fenced block
into `~/.claude/CLAUDE.md`:

```
<!-- memory-hive:start -->
...boot instructions...
<!-- memory-hive:end -->
```

Every Claude Code agent reads `CLAUDE.md` on boot, so this tells them
to load the hive before responding and to re-pull relevant hive context before
substantive prompts/tasks. The block is **idempotent**:
re-running the installer finds the markers and replaces the block in
place. Anything outside the markers — your own notes, other tools'
blocks — is never touched. The canonical content lives in
[`templates/claude-boot-block.md`](templates/claude-boot-block.md);
the installer substitutes `${HIVE_DIR}` and `${INSTALL_DIR}` at install
time.

Opt out with `MEMORY_HIVE_SKIP_CLAUDE_CODE=1` (legacy alias
`MEMORY_HIVE_SKIP_CLAUDE_MD=1` still honored) if you manage that file by
hand. Setting this var skips both the managed block and the Agent Skill
described below.

#### Agent Skill

In addition to the managed block, the installer renders and writes a
native Claude Code Agent Skill to `~/.claude/skills/memory-hive/SKILL.md`.

The **managed block** is the always-on boot contract: every session hydrates
from the hive before responding and writes back after non-trivial work. The
**Agent Skill** is the on-demand depth layer: Claude Code loads only the
skill's one-line description into every session and pulls the full body
— retrieval verb guide, exact raw-learning frontmatter that passes lint,
lane rules, curator loop, troubleshooting — only when memory work is
actually happening. This is progressive disclosure instead of a permanent
context tax.

The skill is also user-invocable as `/memory-hive` inside any Claude Code
session.

The skill is assembled at install time from two sources: the YAML
frontmatter head at
[`templates/skills/memory-hive/SKILL.md`](templates/skills/memory-hive/SKILL.md)
plus the platform-neutral body at [`templates/guide.md`](templates/guide.md)
— the same body `memory-hive guide` prints on every other platform, so the
two surfaces cannot drift apart. The installer renders `${HIVE_DIR}` and
`${INSTALL_DIR}` placeholders to real paths and writes the result to
`~/.claude/skills/memory-hive/SKILL.md`. The unrendered sources are also
shipped under `~/.memory-hive/templates/` for inspection. Re-installing
overwrites the skill file in place (the whole file is installer-managed; no
markers are needed because the file must start with YAML frontmatter).

`memory-hive doctor` checks that the skill file exists and references the
current install, and warns with a re-install hint if it does not.

Opt out of the skill alone with `MEMORY_HIVE_SKIP_CLAUDE_SKILL=1`.

#### Harness hooks (mechanical hydrate + ritual)

The block and the skill are prompt-level: they *ask* the model to hydrate
and write back. The installer also wires two hooks into
`~/.claude/settings.json` so the harness does it mechanically:

- **SessionStart** — runs `~/.memory-hive/hooks/session-start.sh`, which
  injects a token-budgeted hive bundle (plus a pointer to
  `memory-hive guide`) into every new session as additional context. New
  sessions boot hydrated even if the model never reads `CLAUDE.md`.
- **Stop** — runs `~/.memory-hive/hooks/stop-ritual.sh`, which blocks a
  finishing session **at most once** when the task-end ritual hasn't run
  (no fresh dated line in the agent's `log.md`), with instructions to run
  it. `stop_hook_active` prevents loops; short transcripts (trivial
  sessions) are exempt; any unexpected condition exits silently. The agent
  id defaults to `main` — set `MEMORY_HIVE_AGENT_ID` in the environment to
  point the hooks at another silo.

The merge is done with `python3` (already required for HyperRecall) and is
surgical: re-runs replace only entries carrying the `# memory-hive` marker
in their command; hooks you wrote yourself are never touched. If
`settings.json` is malformed JSON the installer refuses to modify it and
warns instead.

Opt out with `MEMORY_HIVE_SKIP_CLAUDE_HOOKS=1` at install time, or disable
at runtime without uninstalling by exporting `MEMORY_HIVE_HOOKS_DISABLE=1`.

**Cursor gets the same enforcement layer** via `~/.cursor/hooks.json`
(version 1): a `stop` hook that replies once with a `followup_message`
when the ritual didn't run — Cursor's own `loop_count` is the loop guard —
and a `sessionEnd` hook that feeds `hive/raw/sessions/` through
`memory-hive capture`. The merge only ever touches entries whose command
points at our `hooks/cursor-*.sh` scripts; malformed files are left alone.
Opt out with `MEMORY_HIVE_SKIP_CURSOR_HOOKS=1`; the same runtime
`MEMORY_HIVE_HOOKS_DISABLE=1` kill switch applies.

### OpenClaw users

If `~/.openclaw/` exists, the installer still writes to
`~/.memory-hive/` (to keep the upgrade path clean), and — if you have
agents under `~/.openclaw/hive/agents/` — offers to import them via
the wizard (see above). If you prefer to keep a single root, either
symlink or copy after install:

```bash
ln -s ~/.memory-hive ~/.openclaw/hive
# or
cp -r ~/.memory-hive ~/.openclaw/hive
```

### Generic users

If neither is found, the installer prints where the files live
(`~/.memory-hive/`) and a short snippet showing how to point any agent
framework at `hive/index.md` and a per-agent silo.

## Managing agents after install

Once the hive is in place, the `memory-hive` CLI is the everyday entry
point:

```bash
sh ~/.memory-hive/memory-hive add backend-eng --role coder
sh ~/.memory-hive/memory-hive list
sh ~/.memory-hive/memory-hive rename backend-eng api-eng
sh ~/.memory-hive/memory-hive archive api-eng
sh ~/.memory-hive/memory-hive role api-eng   # opens $EDITOR on context.md
sh ~/.memory-hive/memory-hive optimize      # built-in hygiene + curation report
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev workflow and
[MIGRATION.md](MIGRATION.md) for upgrade paths from older setups.

## Built-in Optimizer loop

Optimizer is folded into Memory Hive as a command, not installed as another
product. Run:

```bash
sh ~/.memory-hive/memory-hive optimize
sh ~/.memory-hive/memory-hive optimize --report ~/.memory-hive/hive/optimizer/SWARM_SIGNALS.md
```

The command composes existing file-backed checks: `doctor`, `curate`,
`digest --week`, `stats`, and `stale --count`. In `--apply` mode it creates a
checkpoint before curation changes. The optional report is compact markdown for
built-in swarm-routing decisions.

## What's in a silo

Each agent's private directory under `hive/agents/<id>/` contains:

- `log.md` — running journal of what the agent did, session by session
- `context.md` — agent-specific state, role, preferences, working config
- `memory.md` — private learnings this agent wants to remember

The wizard and CLI seed these from the selected role template. The
agent edits them freely over time.

## Re-installing

Safe. The installer refreshes the shared hive (`index.md`, `knowledge/`,
`registry/`, etc.) and the managed `CLAUDE.md` block. Existing silo
files (`log.md`, `context.md`, `memory.md`) are **never** overwritten
— your agents keep their memory across upgrades.

If you want a different roster than last time, the re-install
reconciliation flow (above) lets you add or archive without losing the
silos you keep.

## Environment variables

| Variable | Purpose |
|---|---|
| `MEMORY_HIVE_DIR` | Install location (default: `$HOME/.memory-hive`). |
| `MEMORY_HIVE_REPO` | Install from a local working copy instead of cloning GitHub. Points at a directory with a `hive/` subdir. |
| `MEMORY_HIVE_MERGE_CWD` | Set to `1` to also merge the managed block into `$PWD/CLAUDE.md`. |
| `MEMORY_HIVE_COPILOT_REPO` | Set to `1` to opt into writing `.github/copilot-instructions.md` in the current repo. |
| `MEMORY_HIVE_SKIP_CLAUDE_CODE` | Opt out of all Claude Code wiring (managed block, Agent Skill, and harness hooks). Legacy `MEMORY_HIVE_SKIP_CLAUDE_MD=1` is still honored as an alias. |
| `MEMORY_HIVE_SKIP_CLAUDE_SKILL` | Opt out of installing the Agent Skill only; the managed `CLAUDE.md` block is still written. |
| `MEMORY_HIVE_SKIP_CLAUDE_HOOKS` | Opt out of wiring the SessionStart/Stop/SessionEnd harness hooks into `~/.claude/settings.json`. Runtime equivalent without re-installing: `MEMORY_HIVE_HOOKS_DISABLE=1`. |
| `MEMORY_HIVE_SKIP_CURSOR_HOOKS` | Opt out of wiring the stop/sessionEnd harness hooks into `~/.cursor/hooks.json`. Same `MEMORY_HIVE_HOOKS_DISABLE=1` runtime kill switch. |
| `MEMORY_HIVE_AGENT_ID` | Runtime (not install): which silo the harness hooks hydrate from and check the ritual against. Defaults to `main`. |
| `MEMORY_HIVE_SKIP_OPENCLAW` | Opt out of OpenClaw wiring. |
| `MEMORY_HIVE_SKIP_NANOCLAW` | Opt out of NanoClaw wiring. |
| `MEMORY_HIVE_SKIP_HERMES` | Opt out of Hermes Agent wiring. |
| `MEMORY_HIVE_SKIP_CURSOR` | Opt out of Cursor wiring. |
| `MEMORY_HIVE_SKIP_CONTINUE` | Opt out of Continue.dev wiring. |
| `MEMORY_HIVE_SKIP_AIDER` | Suppress the Aider manual-setup note. |
| `MEMORY_HIVE_SKIP_GEMINI_CLI` | Opt out of Gemini CLI wiring. |
| `MEMORY_HIVE_SKIP_GOOSE` | Opt out of Goose (Block) wiring. |
| `MEMORY_HIVE_SKIP_OPEN_INTERPRETER` | Suppress the Open Interpreter manual-setup note. |
| `MEMORY_HIVE_SKIP_AMAZON_Q` | Opt out of Amazon Q Developer CLI wiring. |
| `MEMORY_HIVE_SKIP_OPENHANDS` | Opt out of OpenHands wiring. |
| `MEMORY_HIVE_SKIP_CLINE` | Suppress the Cline manual-setup note. |
| `MEMORY_HIVE_SKIP_ROO_CODE` | Opt out of Roo Code wiring. |
| `MEMORY_HIVE_SKIP_KILO_CODE` | Opt out of Kilo Code wiring. |
| `MEMORY_HIVE_SKIP_WINDSURF` | Opt out of Windsurf (Codeium) wiring. |
| `MEMORY_HIVE_SKIP_ZED` | Suppress the Zed manual-setup note. |
| `MEMORY_HIVE_SKIP_WARP` | Opt out of Warp wiring. |
| `MEMORY_HIVE_SKIP_AMP` | Opt out of Sourcegraph Amp wiring. |
| `MEMORY_HIVE_SKIP_CODEX` | Opt out of OpenAI Codex CLI wiring. |
| `MEMORY_HIVE_SKIP_OPENCODE` | Opt out of OpenCode wiring. |
| `MEMORY_HIVE_SKIP_CRUSH` | Suppress the Crush manual-setup note. |
| `MEMORY_HIVE_SKIP_GITHUB_COPILOT` | Suppress GitHub Copilot even if `MEMORY_HIVE_COPILOT_REPO=1`. |

## Uninstalling

```bash
memory-hive uninstall          # dry-run: list every unwire action
memory-hive uninstall --apply  # strip managed blocks from all platform
                               # files, remove our hook entries from
                               # ~/.claude/settings.json and
                               # ~/.cursor/hooks.json (yours stay), remove
                               # the Agent Skill and PATH shims
rm -rf ~/.memory-hive          # optional final purge — hive data lives here
```

`uninstall` never touches hive data or user-authored content: managed
blocks are removed between their markers, wholly-installer-owned files are
deleted, everything else is preserved.
