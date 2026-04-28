<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img alt="Memory Hive" src="assets/logo-light.svg" width="420">
  </picture>
</p>

<p align="center">
  <em>A shared, continuously learning memory system for multi-agent AI.</em>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-F59E0B.svg"></a>
  <a href="https://github.com/TJCurnutte/memory-hive/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/TJCurnutte/memory-hive/ci.yml?branch=main&label=CI&color=F59E0B"></a>
  <a href="https://github.com/TJCurnutte/memory-hive/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/TJCurnutte/memory-hive?color=14B8A6&label=release"></a>
  <a href="INTEGRATION.md"><img alt="Platforms: 23" src="https://img.shields.io/badge/platforms-23-F59E0B"></a>
  <img alt="Shell: POSIX" src="https://img.shields.io/badge/shell-POSIX-lightgrey">
  <a href="https://memoryhive.neural-forge.io"><img alt="Site: memoryhive.neural-forge.io" src="https://img.shields.io/badge/site-memoryhive.neural--forge.io-14B8A6"></a>
</p>

<p align="center">
  Multi-agent AI has an amnesia problem. Memory Hive gives every agent a
  private silo and a shared hive so every task compounds instead of
  starting from scratch.
</p>

---

## Quick Start

```bash
curl -fsSL memoryhive.neural-forge.io/install.sh | sh
```

Works with **Claude Code, OpenClaw, NanoClaw, Hermes, Cursor, Continue,
Aider, Gemini CLI, Goose, Open Interpreter, Amazon Q, OpenHands, Cline,
Roo Code, Kilo Code, Windsurf, Zed, Warp, Sourcegraph Amp, OpenAI Codex,
OpenCode, Crush, and GitHub Copilot** — auto-detected and wired in one
step. See [INTEGRATION.md](INTEGRATION.md) for the full platform table
and opt-out env vars.

**Default is zero-input.** The installer scaffolds the reserved `main`
curator silo, writes a managed block into every detected agent
platform's config file (`~/.claude/CLAUDE.md`, `~/.cursor/rules/`,
`~/.gemini/GEMINI.md`, etc.), and exits. No prompts, no questions.

Want the guided setup? Opt in:

```bash
# Either set the env var at install time:
curl -fsSL memoryhive.neural-forge.io/install.sh | MEMORY_HIVE_WIZARD=1 sh

# Or install first, then run the wizard any time:
sh ~/.memory-hive/memory-hive setup
```

The wizard asks how many agents you want, their names, and role
templates. If it finds agents in `~/.claude/agents/` or
`~/.openclaw/hive/agents/`, it offers to import them.

Add, rename, archive, and edit agents at any time with the `memory-hive`
CLI:

```bash
sh ~/.memory-hive/memory-hive add backend-eng --role coder
sh ~/.memory-hive/memory-hive list
sh ~/.memory-hive/memory-hive rename backend-eng api-eng
sh ~/.memory-hive/memory-hive archive api-eng
sh ~/.memory-hive/memory-hive role api-eng   # opens $EDITOR
```

Add `~/.memory-hive` to your `PATH` if you want to drop the prefix.

---

## Day One

A narrative walkthrough of what a fresh install actually feels like:

1. **Run the installer.** One command, no prompts. You get the `main`
   curator silo and a wired-up `~/.claude/CLAUDE.md` managed block.
2. **Add the agents you want.** `memory-hive add coder --role coder`
   and `memory-hive add researcher --role researcher`. Each call
   scaffolds `log.md`, `context.md` (role seeded from the template),
   and `memory.md`, and updates the registry automatically.
3. **Your Claude Code agents load the hive on boot.** The managed
   block tells every agent to read `~/.memory-hive/hive/index.md` and
   its own silo before responding.
4. **List your roster.** `memory-hive list` shows the silos and the
   one-line role description each was seeded with.
5. **Tighten a role description.** `memory-hive role coder` opens
   `hive/agents/coder/context.md` in `$EDITOR`. Rewrite the role to
   match how you actually work. Save.
6. **Your agents start logging.** After each non-trivial task, the agent
   appends to its own `log.md` and, if it learned something generalizable,
   drops a note in `hive/learnings/raw/`.
7. **The curator takes over from there.** `main` reviews `learnings/raw/`
   on whatever cadence you want, promotes the useful bits to
   `learnings/distilled/`, and keeps the shared hive coherent.

That's the whole loop. The hive learns because every agent writes back
to it, and the curator keeps the signal strong.

Coming from an existing setup (OpenClaw, Claude Code sub-agents, a
pre-0.1 hive)? See [MIGRATION.md](MIGRATION.md) — the installer can
import your existing agents in one step.

---

## What Loads Into Context

Memory Hive is designed to keep long-running agent memory inspectable
without turning every prompt into a full archive replay.

On boot, each agent reads a small, fixed set of surfaces: `index.md`,
the registry, human context, distilled patterns, the task queue, and
its own silo. It does **not** automatically inject every raw learning,
every external capture, or another agent's private notes.

Use the tiers as trust boundaries:

- `hive/raw/` and `learnings/raw/[agent-id]/` are queues and evidence,
  not canonical truth.
- `learnings/distilled/` and `knowledge/` are the promoted surfaces
  agents should trust by default.
- `curator/DECISIONS.md` records why something was promoted, deferred,
  or resolved after a conflict.

When an agent needs more history, reach for `memory-hive query`,
`digest`, `tail`, or `bundle --max-tokens N` instead of loading the
whole hive. The goal is durable memory with a bounded working set:
fresh enough to be useful, small enough to stay reliable.

---

## The Shape of a Hive

```
             ┌─────────────────────────────────────────┐
             │             SHARED HIVE                 │
             │                                         │
             │  registry/     knowledge/               │
             │  learnings/    tasks/                   │
             │                                         │
             │       curator promotes raw → distilled  │
             └───────▲─────────────────────▲───────────┘
             reads   │                     │  reads
             writes  │                     │  writes raw/
                     │                     │
         ┌───────────┴──────┐      ┌───────┴─────────┐
         │     main         │      │     agent       │   ...N
         │  (curator, one)  │      │  (you defined)  │
         ├──────────────────┤      ├─────────────────┤
         │ log.md           │      │ log.md          │
         │ context.md       │      │ context.md      │
         │ memory.md        │      │ memory.md       │
         └──────────────────┘      └─────────────────┘
```

Every hive has exactly one `main` (the curator) plus any number of
user-defined agents. The diagram shows the shape, not a specific roster
— you name your own agents at install time.

---

## The Two-Layer Architecture

### Layer 1 — Private Silos

Each agent has a personal memory space that nobody else touches:

```
agents/[agent-id]/
├── log.md        ← personal notes, observations, working context
├── context.md    ← role, state, current focus
└── memory.md     ← private learnings only this agent needs
```

Silos give agents continuity across sessions.

### Layer 2 — Shared Hive

All agents read from, and contribute to, the collective brain:

```
hive/
├── index.md        ← entry point — always read first
├── registry/       ← who's who and what they do
├── knowledge/      ← curated truth (curator only writes)
├── learnings/      ← raw → distilled → patterns
├── tasks/          ← shared work queue
└── curator/        ← curation workspace
```

The hive is the cross-pollination layer. What one agent learns benefits
every other agent on the next boot.

---

## How It Works

```
Agent spawns
    │
    ▼
┌────────────────────────────────────────────────┐
│ 1. Read hive/index.md          (current state) │
│ 2. Read hive/registry/AGENTS.md                │
│ 3. Read hive/registry/SKILLS_CATALOG.md        │
│ 4. Read hive/knowledge/HUMAN_CONTEXT.md        │
│ 5. Read hive/learnings/distilled/patterns.md   │
│ 6. Read hive/tasks/queue.md                    │
│ 7. Read own private silo (agents/[id]/)        │
│ 8. Load active task context                    │
│ 9. Begin work                                  │
└────────────────────────────────────────────────┘
    │
    ▼
Task completes
    │
    ▼
┌────────────────────────────────────────────────┐
│ 1. Write learnings to hive/learnings/raw/      │
│ 2. Update private silo (agents/[id]/log.md)    │
│ 3. Curator scans raw/ (tail / digest / dedup)  │
│ 4. Curator promotes raw → distilled (promote)  │
│ 5. Next agent boots → reads updated hive       │
└────────────────────────────────────────────────┘
    │
    ▼
Hive is smarter than before
```

For the full directory layout, curation loop, confidence gates, and
conflict-resolution rules, see [HIVE_ARCHITECTURE.md](HIVE_ARCHITECTURE.md).

---

## CLI Verbs

`memory-hive <verb>` is the single entry point. Run `memory-hive help` for
the full reference. The verbs cluster into three categories:

**Lifecycle** — `add`, `list`, `archive`, `role`, `rename`, `register`,
`setup`, `apply`, `doctor`, `seed`. Manage silos and keep the install
healthy.

`seed [--scenario <name>] [--dry-run] [--force]` answers the most
common first-day question: "I installed it, now what?" One command
populates a fresh hive with synthetic-but-realistic content (silo
logs, raw + distilled learnings, a curator decision log, a projects
file) so the observability verbs below produce non-trivial output
on first use. Bundled scenarios: `default` (3-agent team, two weeks
of activity), `solo`, `large-team`. Refuses to overwrite a non-empty
hive without `--force`.

**Observability** — see what's happening in the hive without manual grep:

| Verb | What |
|---|---|
| `tail [-n N] [--silo <name>] [--since <date>]` | Most recent N writes with key content extracted |
| `watch` | Streaming live counter (Ctrl+C to exit) |
| `stats` | Honest counts: silos, raw learnings, distilled files, decisions |
| `digest [--today \| --yesterday \| --week \| --since <date>]` | Human-readable change summary for a window |
| `query <term> [--silo] [--kind] [--since]` | Grep every text surface of the hive |
| `diff [--since <checkpoint\|date>]` | What changed since a reference point |
| `checkpoint [--name <name>] \| --list` | Save a reference marker for later diffs |
| `bundle [--for <agent>] [--max-tokens N]` | Concatenate canonical hive surfaces into one prompt-injection-ready blob |

**Curator workflow** — close the loop from raw → distilled:

| Verb | What |
|---|---|
| `dedup [--per-agent] [--strict]` | Cluster near-duplicate raw learnings |
| `confidence` | Cluster aligned observations, suggest upgrades |
| `promote <raw-file>` | One-command: append summary + log decision |
| `stale [--days N]` | Surface raw learnings with no curator decision |
| `lint [--fix]` | Validate frontmatter schema |
| `tag <file> <tag>` / `tags` | Tag learnings, see emerging topics |
| `citations` | Build cross-agent citation graph |
| `conflicts [--agent <name>] [--strict] [--write]` | Surface raw learnings that contradict each other |
| `reflect <agent> [--days N] [--write]` | Agent self-reflection: distill recent log activity into memory.md themes |
| `curate [--dry-run \| --apply]` | Autonomous one-pass curator: chains dedup → confidence → promote → lint → stale |

Every verb is pure shell, ships a CI smoke test, and reads from the
existing two-layer architecture without changing it.

---

## Role Templates

The installer ships six starter role descriptions under
[`templates/roles/`](templates/roles/). Each is a short paragraph you can
drop straight into an agent's `context.md`:

- **coder** — writes and edits code, knows conventions, tests before shipping
- **reviewer** — reviews code and designs for correctness, security, maintainability
- **researcher** — deep-dives on open questions with sources cited
- **writer** — drafts and edits prose, matches tone, tightens verbose writing
- **planner** — breaks big tasks into concrete steps, surfaces risks early
- **curator** — reserved role for `main` — owns the shared hive

You can also pass `--role /path/to/your/own.md` to the CLI, or pick
"custom" in the wizard and type your own paragraph.

---

## Key Principles

### 1. Double Layer — Both, Not Either
Private silos for personal continuity. Shared hive for collective
intelligence. Each serves a different purpose.

### 2. Curator System
One agent (`main`) acts as curator. Agents contribute freely to
`learnings/raw/`; the curator reviews and promotes valuable insights to
`learnings/distilled/`. Low friction to contribute, high bar to promote.

### 3. Two-Tier Learning
- **Raw learnings** — agents dump post-task observations without friction
- **Distilled learnings** — curator writes canonical patterns, mistakes, wins

### 4. Silo Privacy Respected
Each agent's private directory is theirs alone. The curator doesn't read
private silos unless explicitly asked.

### 5. Conflict Resolution
When two agents contradict each other, both perspectives go to
`curator/CONFLICTS.md`. The curator investigates and resolves — logged
in `DECISIONS.md`. No unilateral overwrites.

### 6. Non-Destructive Reconciliation
Re-running the installer against an existing hive never deletes your
data. Agents you remove are archived to
`hive/agents/_archived/YYYY-MM-DD/`, not deleted. You can always dig
them back out.

### 7. Memory Hygiene
- Raw learnings >7 days unreviewed → auto-escalate
- Active tasks >14 days old → auto-escalate
- Private silos never auto-cleaned (agent owns its own space)
- Confidence gates prevent low-confidence info from polluting core knowledge

---

## Installation details

The installer auto-detects 23 agent platforms (Claude Code, OpenClaw,
Cursor, Continue, Gemini CLI, Goose, Amazon Q, OpenHands, Roo, Kilo,
Windsurf, Warp, Sourcegraph Amp, OpenAI Codex, OpenCode, and more) and
wires a managed block into each platform's config file. See
[INTEGRATION.md](INTEGRATION.md) for the full platform table, the
managed-block format, and every opt-out env var
(`MEMORY_HIVE_SKIP_CURSOR`, `MEMORY_HIVE_SKIP_GOOSE`, etc.).

### Re-install / reconcile

Re-running the installer on an existing hive offers four choices:

- **keep** — just update the managed block and shared hive files
- **add** — add more agents alongside what's there
- **fresh** — archive every non-curator agent and start over
- **select** — review each agent, keep or archive one by one

No agents are ever deleted; archiving moves them to
`hive/agents/_archived/<date>/`.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup and the safe
local-test workflow. Areas that welcome help:

- Framework adapters (LangChain, AutoGen, CrewAI, etc.)
- Additional role templates
- Curation automation
- Memory hygiene tools
- Visualization

For release history, see [CHANGELOG.md](CHANGELOG.md).

---

## The Curator Role

The `main` agent acts as curator. This is the most important role in the
system — it maintains the shared hive so all other agents can focus on
their specialties.

**Curator responsibilities:**

- Maintain `knowledge/` as curated truth
- Review `learnings/raw/` on a regular cadence
- Promote valuable learnings to `learnings/distilled/`
- Resolve conflicts in `curator/CONFLICTS.md`
- Log every decision in `curator/DECISIONS.md`
- Synthesize cross-agent insights

---

## Links

- **Live site:** <https://memoryhive.neural-forge.io>
- **Repo:** <https://github.com/TJCurnutte/memory-hive>
- **Releases:** <https://github.com/TJCurnutte/memory-hive/releases> — version history with everything that shipped per release.
- **Changelog:** [CHANGELOG.md](CHANGELOG.md) — Keep-a-Changelog format, mirrored on the Releases page.
- **License:** [MIT](LICENSE) — use it, build on it, make it better.

---

<p align="center">
  <strong>The hive learns. Every task. Every agent. Every time.</strong>
</p>
