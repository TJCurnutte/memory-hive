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

Opt out with `MEMORY_HIVE_SKIP_CLAUDE_MD=1` if you manage that file by
hand.

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
| `MEMORY_HIVE_SKIP_CLAUDE_CODE` | Opt out of the Claude Code wiring. Legacy `MEMORY_HIVE_SKIP_CLAUDE_MD=1` is still honored as an alias. |
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
rm -rf ~/.memory-hive
# then open ~/.claude/CLAUDE.md and delete the block between
# <!-- memory-hive:start --> and <!-- memory-hive:end -->
```

That's it. No other files are modified.
