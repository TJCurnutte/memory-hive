<p align="center">
  <img alt="Memory Hive logo" src="assets/hive-mark.svg" width="148">
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
  <strong>Install once. Let agents read and write. Update periodically.</strong><br>
  Memory Hive keeps agent memory as local files with private silos, a shared curated hive, and receipts you can inspect.
</p>

---

## What Memory Hive is

Memory Hive is a file-backed memory layer for AI agents. It is not an agent runtime, hosted service, vector database, or replacement for your editor/CLI.

It gives the tools you already use a durable place to remember:

- project truth that should survive the next session
- agent-specific context that should not be overwritten by other agents
- reusable lessons that should compound across the whole team
- curator decisions about what is trusted, stale, duplicated, or in conflict

Everything starts as local Markdown under `~/.memory-hive`. The optional HyperRecall speed layer is a rebuildable SQLite index beside those files. Markdown stays the source of truth.

## Start in one command

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | sh
```

That first run does the work users previously had to stitch together by hand:

- creates `~/.memory-hive`
- creates the reserved `main` curator silo
- installs the `memory-hive` command or a PATH shim when possible
- wires managed Memory Hive blocks into detected agent tools
- refreshes the roster/registry
- builds or updates the HyperRecall index quietly
- runs the maintenance wrapper quietly
- prints one receipt with the install path, wired platforms, roster, and next commands

After install, the normal check is just:

```bash
memory-hive
# same as:
memory-hive status
```

Optional: add an agent silo when you want one.

```bash
memory-hive add coder --role coder
```

Periodic refresh is one command:

```bash
memory-hive update
```

`update` pulls the latest Memory Hive tool files, preserves local agent silos, refreshes shared managed content, rebuilds/updates the recall index, and runs maintenance. You should not need to run `doctor`, `recall build`, `lint`, `digest`, or `stale` during normal use.

## The daily command surface

| Command | Use it when you want to... |
|---|---|
| `memory-hive` | see the one-screen status receipt |
| `memory-hive status` | same receipt, explicit form |
| `memory-hive update` | refresh Memory Hive and run periodic maintenance |
| `memory-hive add <agent> --role coder` | add another private agent silo |
| `memory-hive search "term"` | search local hive Markdown |
| `memory-hive recall "task context"` | retrieve cited context; the index is built/updated automatically |
| `memory-hive help --advanced` | inspect curator/debug/internal commands |

That is the intended public UX. The rest of the verbs still exist for scripts, CI, power users, and the curator lane, but they are no longer part of day-one onboarding.

## What runs automatically now

Memory Hive keeps the plumbing available without making it the user journey.

| Internal operation | When it runs |
|---|---|
| Install health checks | during install and `memory-hive status` |
| Roster/registry refresh | during install, add/archive/rename, and maintenance |
| Citation registry refresh | during maintenance |
| HyperRecall build/update | during install, maintenance, and first recall query if missing; normal updates reindex changed/deleted files only |
| Curation health pass | during maintenance through the built-in Optimizer wrapper |
| Stale/raw-learning signal | included in status and maintenance summaries |

The commands are still there when you need receipts:

```bash
memory-hive help --advanced
```

## The Memory Hive loop

1. **Hydrate** — an agent reads shared hive context and its own private silo before substantive work.
2. **Work** — it uses current project context, curated knowledge, and prior lessons.
3. **Write back** — it logs task notes and drops reusable observations into `hive/learnings/raw/`.
4. **Curate** — `main` promotes verified patterns into `hive/learnings/distilled/` and shared knowledge.
5. **Compound** — the next prompt, task, or agent starts smarter than the last one.

The product is the habit: **pull memory, work, write back, curate.**

Critical habit for agent operators: Memory Hive is not a one-time boot note. For non-trivial, cross-session, or operational prompts, agents should visibly re-pull the smallest relevant hive slice before acting so operators can audit that memory informed the work.

## The shape of a hive

```text
~/.memory-hive/
├── memory-hive                 # CLI entry point
├── memory_hive_recall.py       # helper-backed recall engine
├── update.sh                   # safe periodic updater
└── hive/
    ├── index.md                # boot entrypoint: read this first
    ├── registry/               # roster, citations, skill catalog
    ├── knowledge/              # curator-owned shared truth
    ├── learnings/
    │   ├── raw/                # agent-submitted observations
    │   └── distilled/          # curator-promoted patterns
    ├── tasks/                  # shared queue / coordination
    ├── curator/                # conflicts, decisions, drafts
    ├── .hivecode/              # rebuildable HyperRecall SQLite index
    └── agents/
        ├── main/               # reserved curator silo
        │   ├── log.md
        │   ├── context.md
        │   └── memory.md
        └── coder/              # any agents you define
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

## Capabilities

| Capability | What it does |
|---|---|
| **Private agent silos** | Each agent gets `log.md`, `context.md`, and `memory.md` under `hive/agents/<agent>/`. |
| **Shared hive knowledge** | Agents contribute raw learnings; `main` curates durable truth into shared knowledge. |
| **Drop-in tool wiring** | Installer detects Claude Code, Cursor, Codex, Hermes, Aider, Gemini CLI, Goose, and more. |
| **Install-once CLI** | Day-one UX is `install`, `status`, optional `add`, `search`, `recall`, and periodic `update`. |
| **Maintenance wrapper** | `memory-hive maintain` runs registry/citation refresh, recall index maintenance, and the Optimizer pass. |
| **HyperRecall / TokenFS** | Local SQLite/FTS5 recall index, stable HiveCodes, cited bundles, cache, stale detection, changed-file-only updates, and skill routing. |
| **Prompt Optimizer addon** | Planned Memory Hive addon that compiles rough operator prompts into Hive-backed internal work orders before execution. |
| **Semver release history** | Versioned GitHub Releases stay readable: `v1.1.0`, `v0.4.1`, and so on. |

## Supported tools

Memory Hive works with Claude Code, OpenClaw, NanoClaw, Hermes, Cursor, Continue, Aider, Gemini CLI, Goose, Open Interpreter, Amazon Q, OpenHands, Cline, Roo Code, Kilo Code, Windsurf, Zed, Warp, Sourcegraph Amp, OpenAI Codex, OpenCode, Crush, and GitHub Copilot.

See [INTEGRATION.md](INTEGRATION.md) for the full platform table, managed-block format, and opt-out flags.

## Advanced commands

Normal users should not need these during onboarding. They remain available for operators, CI, and curator workflows.

<details>
<summary>Show advanced command families</summary>

**Lifecycle** — `list`, `setup`, `role`, `rename`, `archive`, `register`, `apply`.

**Health and maintenance** — `doctor`, `maintain`, `optimize`, `checkpoint`, `diff`.

**Inspection** — `tail`, `watch`, `stats`, `digest`, `query`, `bundle`.

**HyperRecall** — `recall query`, `recall bundle`, `recall build`, `recall update`, `recall doctor`, `recall stats`, `hyper`.

**Curator workflow** — `curate`, `promote`, `confidence`, `dedup`, `conflicts`, `stale`, `lint`, `tag`, `tags`, `citations`, `reflect`, `seed`.

Run:

```bash
memory-hive help --advanced
```

</details>

## Built-in maintenance, not another product

`memory-hive maintain` is the local maintenance wrapper. It refreshes registry/citation surfaces, builds or updates the recall index, runs the Optimizer pass, and records the last maintenance timestamp.

`memory-hive update` is the normal public entry point for periodic care. It refreshes tool files from upstream, preserves private agent silos, and then runs maintenance. Use `maintain` directly only when you want an offline/local pass without pulling new files.

`memory-hive optimize` still exists as the advanced maintenance brain: `doctor` → `curate` → `digest --week` → `stats` → `stale --count`, with optional report output for swarm controllers.

## Prompt Optimizer addon

Prompt Optimizer is a planned Memory Hive addon, not a separate product. It uses the hive, private silos, distilled learnings, session artifacts, and HyperRecall bundles to compile rough operator prompts into compact internal work orders before an agent starts work.

The addon contract remains advanced/planned:

```bash
memory-hive prompt classify "<raw prompt>" --json
memory-hive prompt optimize "<raw prompt>" --json
memory-hive prompt questions "<raw prompt>" --count 3 --json
memory-hive prompt bundle "<raw prompt>" --for-agent <agent>
```

The workflow stays simple: classify the prompt, pull the smallest useful hive slice, produce an executable work order, verify the result, and write back useful lessons. If the prompt is still genuinely ambiguous after context inspection, the addon returns exactly three clarification questions.

See [docs/PROMPT_OPTIMIZER.md](docs/PROMPT_OPTIMIZER.md) for the command contract, JSON shape, and implementation checklist.

## Versioned releases

Memory Hive uses conventional GitHub Releases for public shipping notes.

- versioned tags like `v1.1.0` create changelog-backed releases
- release titles stay readable instead of generated commit-hash cards
- changelog entries remain the source of truth for what shipped

Latest changes: <https://github.com/TJCurnutte/memory-hive/releases>

## Installation details

The installer is intentionally boring shell:

```bash
curl -fsSL https://hive.neural-forge.io/install.sh | sh
```

Re-running it is safe. Existing agent data is preserved. Shared files are refreshed only through the update/sync path. Agent silos under `hive/agents/` are never overwritten by upstream content.

Key environment flags:

- `MEMORY_HIVE_DIR=/path/to/install` — install somewhere other than `~/.memory-hive`
- `MEMORY_HIVE_WIZARD=1` — opt into the interactive wizard
- `MEMORY_HIVE_ONLY=hermes,cursor` — wire only selected detected platforms
- `MEMORY_HIVE_SKIP_<PLATFORM>=1` — skip a platform integration during install

See [INTEGRATION.md](INTEGRATION.md) for platform-specific flags.

## Design principles

1. **Local first** — Markdown on disk beats invisible state.
2. **Private by default** — each agent owns its own silo.
3. **Curated shared truth** — raw observations are cheap; promotion is deliberate.
4. **Non-destructive reconciliation** — preserve silos, archive before delete, checkpoint before apply.
5. **Small public surface** — normal use should be install, status, optional add, search/recall, update.
6. **Shell-native portability** — POSIX shell, no runtime server, no npm package required.
7. **Every task compounds** — useful lessons survive beyond the current chat window.

## Project docs

- [HIVE_ARCHITECTURE.md](HIVE_ARCHITECTURE.md) — directory layout, curation loop, confidence gates, conflict handling
- [INTEGRATION.md](INTEGRATION.md) — supported platforms, managed blocks, opt-out flags
- [docs/HIVECODE_ENGINE.md](docs/HIVECODE_ENGINE.md) — HyperRecall / HiveCode engine details
- [docs/PROMPT_OPTIMIZER.md](docs/PROMPT_OPTIMIZER.md) — Prompt Optimizer addon contract for compiling raw prompts into Hive-backed work orders
- [MIGRATION.md](MIGRATION.md) — safe migration and import strategy
- [MEMORY_ADAPTER_CONTRACT.md](MEMORY_ADAPTER_CONTRACT.md) — adapter expectations for other memory backends
- [CONTRIBUTING.md](CONTRIBUTING.md) — local development and test workflow
- [CHANGELOG.md](CHANGELOG.md) — release history
- [docs/RELEASE_NOTES_SIMPLIFIED_UX.md](docs/RELEASE_NOTES_SIMPLIFIED_UX.md) — v1.2.0 release notes for the install-once/status/update UX simplification

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
  <strong>Silos remember. Hive compounds. One install, periodic care.</strong>
</p>
