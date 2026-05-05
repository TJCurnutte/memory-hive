<p align="center">
  <img alt="Memory Hive logo" src="assets/hive-mark.png" width="148">
</p>

<h1 align="center">Memory Hive</h1>

<p align="center">
  <em>Local-first shared memory for AI agents: private silos, a curated hive, and one POSIX shell CLI.</em>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-F59E0B.svg"></a>
  <a href="https://github.com/TJCurnutte/memory-hive/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/TJCurnutte/memory-hive/ci.yml?branch=main&label=CI&color=F59E0B"></a>
  <a href="https://github.com/TJCurnutte/memory-hive/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/TJCurnutte/memory-hive?color=14B8A6&label=release"></a>
  <a href="INTEGRATION.md"><img alt="Platforms: 23" src="https://img.shields.io/badge/platforms-23-F59E0B"></a>
  <img alt="Shell: POSIX" src="https://img.shields.io/badge/shell-POSIX-lightgrey">
  <a href="https://hive.neural-forge.io"><img alt="Site: hive.neural--forge.io" src="https://img.shields.io/badge/site-hive.neural--forge.io-14B8A6"></a>
</p>

<p align="center">
  <strong>Memory Hive is the public home for the Hive memory layer.</strong><br>
  It gives every agent a private workspace, one shared source of truth, and a curation loop so each task makes the next one smarter.
</p>

---

## What Memory Hive is

Memory Hive is a file-backed memory layer for AI agents. It is not an agent runtime, vector database, hosted service, or replacement for your editor/CLI.

It gives the tools you already use a durable place to remember:

- project truth that should survive the next session
- agent-specific context that should not be overwritten by other agents
- reusable lessons that should compound across the whole team
- curator decisions about what is trusted, stale, duplicated, or in conflict

Everything is local Markdown under `~/.memory-hive`. No account. No daemon. No database. No hidden cloud state.

## What you get

| Capability | What it does |
|---|---|
| **Private agent silos** | Each agent gets `log.md`, `context.md`, and `memory.md` under `hive/agents/<agent>/`. |
| **Shared hive knowledge** | Agents contribute raw learnings; `main` curates durable truth into shared knowledge. |
| **Drop-in tool wiring** | Installer detects Claude Code, Cursor, Codex, Hermes, Aider, Gemini CLI, Goose, and more. |
| **Operator CLI** | `tail`, `digest`, `query`, `stats`, `doctor`, `curate`, `optimize`, and `bundle`. |
| **Semver release history** | Versioned GitHub Releases stay readable: `v0.4.0`, `v0.3.2`, and so on. |

## Start in 2 minutes

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | sh
memory-hive add coder --role coder
memory-hive list
```

The default install is **zero-input**: no prompts, no account, no daemon. It creates `~/.memory-hive`, the reserved `main` curator silo, and managed config blocks for detected agent tools.

Want a guided setup instead?

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | MEMORY_HIVE_WIZARD=1 sh
# or later:
memory-hive setup
```

Want to see value before wiring your real agents?

```bash
memory-hive seed --scenario default
memory-hive digest --week
memory-hive confidence
memory-hive bundle --for coder --max-tokens 4000
```

## The Memory Hive loop

1. **Hydrate** — an agent reads `hive/index.md`, shared knowledge, current tasks, and its own private silo on boot and again before substantive work.
2. **Work** — it uses current project context, curated knowledge, and prior lessons.
3. **Write back** — it logs task notes and drops reusable observations into `hive/learnings/raw/`.
4. **Curate** — `main` promotes verified patterns into `hive/learnings/distilled/` and shared knowledge.
5. **Compound** — the next prompt, task, or agent starts smarter than the last one.

That is the product: **pull memory, work, write back, curate.**

Critical habit: Memory Hive is not a one-time boot note. For non-trivial,
cross-session, or operational prompts, agents should visibly re-pull the
smallest relevant hive slice before acting so operators can audit that the
shared memory actually informed the answer.

## The shape of a hive

```text
~/.memory-hive/
└── hive/
    ├── index.md                  # boot entrypoint: read this first
    ├── registry/                 # roster, citations, skill catalog
    ├── knowledge/                # curator-owned shared truth
    ├── learnings/
    │   ├── raw/                  # agent-submitted observations
    │   └── distilled/            # curator-promoted patterns
    ├── tasks/                    # shared queue / coordination
    ├── curator/                  # conflicts, decisions, drafts
    └── agents/
        ├── main/                 # reserved curator silo
        │   ├── log.md
        │   ├── context.md
        │   └── memory.md
        └── coder/                # any agents you define
            ├── log.md
            ├── context.md
            └── memory.md
```

Every hive has exactly one reserved `main` agent. `main` is the curator: it owns shared truth, reviews raw learnings, promotes durable patterns, and resolves conflicts. Working agents keep their own private silos.

## Why the two layers matter

| Layer | Owner | Purpose |
|---|---|---|
| **Private silo** | One agent | Continuity for that agent's habits, role, and working notes. |
| **Shared hive** | Curator-governed | Durable project truth, cross-agent patterns, conflicts, decisions, and team memory. |

Private silos prevent agents from trampling each other's context. The shared hive lets good lessons spread without letting every raw note become truth.

For the full governance model, see [HIVE_ARCHITECTURE.md](HIVE_ARCHITECTURE.md).

## Supported tools

Memory Hive works with Claude Code, OpenClaw, NanoClaw, Hermes, Cursor, Continue, Aider, Gemini CLI, Goose, Open Interpreter, Amazon Q, OpenHands, Cline, Roo Code, Kilo Code, Windsurf, Zed, Warp, Sourcegraph Amp, OpenAI Codex, OpenCode, Crush, and GitHub Copilot.

See [INTEGRATION.md](INTEGRATION.md) for the full 23-platform table, managed-block format, and opt-out flags.

## Commands you will actually use

| Command | Use it when you want to... |
|---|---|
| `memory-hive add coder --role coder` | create a new agent silo from a role template |
| `memory-hive list` | see the active roster |
| `memory-hive doctor` | verify the install and managed blocks |
| `memory-hive tail -n 20` | see the most recent hive writes |
| `memory-hive digest --week` | summarize recent activity |
| `memory-hive query <term>` | search every text surface in the hive |
| `memory-hive promote <raw-file>` | turn one raw learning into a curated pattern |
| `memory-hive confidence` | find repeated observations ready for promotion |
| `memory-hive curate --dry-run` | preview the curation queue |
| `memory-hive optimize --report report.md` | run the built-in maintenance pass |
| `memory-hive bundle --for coder` | produce a prompt-ready context bundle |
| `memory-hive seed --scenario default` | populate demo data in a fresh hive |

<details>
<summary>Full command families</summary>

**Lifecycle** — `add`, `list`, `archive`, `role`, `rename`, `register`, `setup`, `apply`, `doctor`, `seed`.

**Observability** — `tail`, `watch`, `stats`, `digest`, `query`, `diff`, `checkpoint`, `bundle`, `optimize`.

**Curator workflow** — `dedup`, `confidence`, `promote`, `stale`, `lint`, `tag`, `tags`, `citations`, `conflicts`, `reflect`, `curate`, `optimize`.

Run `memory-hive help` for exact flags and examples.

</details>

## Built-in maintenance, not another product

`memory-hive optimize` is the maintenance pass inside Memory Hive. It composes existing commands — `doctor`, `curate`, `digest`, `stats`, and `stale` — into one operator report.

For advanced multi-agent controllers, `--report <file>` emits a compact routing signal. There is no separate memory product to install or synchronize.

## Versioned releases

Memory Hive uses conventional GitHub Releases for public shipping notes.

- versioned tags like `v0.4.0` create changelog-backed releases
- release titles stay readable instead of generated commit-hash cards
- changelog entries remain the source of truth for what shipped

Latest changes: <https://github.com/TJCurnutte/memory-hive/releases>

## Installation details

The installer is intentionally boring shell:

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | sh
```

Re-running it is safe. Existing agent data is reconciled, not deleted. Removed agents are archived under `hive/agents/_archived/<date>/`.

Key environment flags:

- `MEMORY_HIVE_DIR=/path/to/hive` — install somewhere other than `~/.memory-hive`
- `MEMORY_HIVE_WIZARD=1` — opt into the interactive wizard
- `MEMORY_HIVE_SKIP_<PLATFORM>=1` — skip a platform integration during install

See [INTEGRATION.md](INTEGRATION.md) for platform-specific flags.

## Design principles

1. **Local first** — Markdown on disk beats invisible state.
2. **Private by default** — each agent owns its own silo.
3. **Curated shared truth** — raw observations are cheap; promotion is deliberate.
4. **Non-destructive reconciliation** — archive before delete, checkpoint before apply.
5. **Shell-native portability** — POSIX shell, no runtime server, no npm package required.
6. **Every task compounds** — useful lessons survive beyond the current chat window.

## Project docs

- [HIVE_ARCHITECTURE.md](HIVE_ARCHITECTURE.md) — directory layout, curation loop, confidence gates, conflict handling
- [INTEGRATION.md](INTEGRATION.md) — supported platforms, managed blocks, opt-out flags
- [MIGRATION.md](MIGRATION.md) — safe migration and import strategy
- [MEMORY_ADAPTER_CONTRACT.md](MEMORY_ADAPTER_CONTRACT.md) — adapter expectations for other memory backends
- [CONTRIBUTING.md](CONTRIBUTING.md) — local development and test workflow
- [CHANGELOG.md](CHANGELOG.md) — release history

## Contributing

Areas that welcome help:

- more platform adapters
- additional role templates
- curation automation
- memory hygiene tooling
- visualizations and reports
- real-world examples from agent teams

Start with [CONTRIBUTING.md](CONTRIBUTING.md), then open an issue or PR.

## Links

- Live site: <https://hive.neural-forge.io>
- Repo: <https://github.com/TJCurnutte/memory-hive>
- Releases: <https://github.com/TJCurnutte/memory-hive/releases>
- License: [MIT](LICENSE)

---

<p align="center">
  <strong>The hive learns. Every task. Every agent. Every time.</strong>
</p>
