# Memory Hive

**A shared, continuously learning memory system for multi-agent AI.**

- Live: https://memoryhive.neural-forge.io
- Source: https://github.com/TJCurnutte/memory-hive

Memory Hive gives every agent two memory layers:

- **Private silo** — personal continuity for each agent
- **Shared hive** — collective intelligence that compounds

Every agent reads from the hive on boot. Every agent writes learnings
after tasks. A curator synthesizes contributions. The system gets smarter
with every task.

---

## Quick Start

```bash
curl -fsSL memoryhive.neural-forge.io/install.sh | sh
```

On a real terminal, the installer runs an interactive wizard: you pick
how many agents you want, name them, and assign a role template (or
write your own). In a non-interactive context (CI, `| sh` with no tty),
it installs just the `main` curator silo and prints the one-liner for
adding more later.

You can add, rename, archive, and edit agents at any time with the
`memory-hive` CLI:

```bash
sh ~/.memory-hive/memory-hive add backend-eng --role coder
sh ~/.memory-hive/memory-hive list
sh ~/.memory-hive/memory-hive rename backend-eng api-eng
sh ~/.memory-hive/memory-hive archive api-eng
sh ~/.memory-hive/memory-hive role api-eng   # opens $EDITOR
```

Add `~/.memory-hive` to your `PATH` if you want to drop the prefix.

---

## The Shape of a Hive

```
                    ┌─────────────────────────────────────────┐
                    │          THE SHARED HIVE                │
                    │                                         │
                    │   registry/     knowledge/              │
                    │   ├── AGENTS.md  ├── SOUL.md            │
                    │   └── SKILLS     └── HUMAN_CONTEXT.md   │
                    │                                         │
                    │   learnings/    tasks/                  │
                    │   ├── raw/      ├── queue.md            │
                    │   └── distilled └── active/             │
                    │                                         │
                    │           curator reviews               │
                    │     writes ▲        ▲ reads             │
                    └────────────┼────────┼───────────────────┘
                                 │        │
                 ┌───────────────┴────────┴──────────────────┐
                 │                                           │
        ┌────────▼──────────┐     ┌────────▼──────────┐
        │  main (curator)   │     │  your agent #1    │  ...
        │  private silo     │     │  private silo     │
        │  └── log.md       │     │  └── log.md       │
        │  └── context.md   │     │  └── context.md   │
        │  └── memory.md    │     │  └── memory.md    │
        └───────────────────┘     └───────────────────┘
```

`main` is a reserved role — it's the Chief of Staff / curator, always
present. Every other agent in the diagram is one you chose.

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
│ 3. Submit summary to curator/DRAFT.md          │
│ 4. Curator reviews → promotes to distilled/    │
│ 5. Next agent boots → reads updated hive       │
└────────────────────────────────────────────────┘
    │
    ▼
Hive is smarter than before
```

---

## Core Architecture

```
~/.memory-hive/hive/                 ~/.memory-hive/hive/agents/[id]/
├── index.md                         ├── log.md        ← private
├── registry/                        ├── context.md    ← private
│   ├── AGENTS.md                    └── memory.md     ← private
│   └── SKILLS_CATALOG.md
├── knowledge/
│   ├── HUMAN_CONTEXT.md
│   ├── SOUL.md
│   └── DOMAINS.md
├── learnings/
│   ├── raw/[agent-id]/
│   ├── distilled/
│   │   ├── patterns.md
│   │   ├── mistakes.md
│   │   ├── wins.md
│   │   └── cross-agent-insights.md
│   └── META.json
├── tasks/
│   ├── queue.md
│   └── active/
└── curator/
    ├── DRAFT.md
    ├── CONFLICTS.md
    └── DECISIONS.md
```

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

## For Developers

### Install

```bash
curl -fsSL memoryhive.neural-forge.io/install.sh | sh
```

The installer auto-detects Claude Code and OpenClaw. See
[INTEGRATION.md](INTEGRATION.md) for what gets wired up and how to opt
into project-level `CLAUDE.md` merging.

### Re-install / Reconcile

Re-running the installer on an existing hive offers four choices:

- **keep** — just update the managed block and shared hive files
- **add** — add more agents alongside what's there
- **fresh** — archive every non-curator agent and start over
- **select** — review each agent, keep or archive one by one

No agents are ever deleted; archiving moves them to
`hive/agents/_archived/<date>/`.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Key areas:
- Framework adapters (LangChain, AutoGen, CrewAI, etc.)
- Additional role templates
- Curation automation
- Memory hygiene tools
- Visualization

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

## Who Built This

[Travis Curnutte](https://github.com/TJCurnutte) open-sourced this after
running it inside his own multi-agent setup. The repo is meant to work
for anyone's roster, not any one person's — pick the agents that match
how you work.

## License

MIT — use it, build on it, make it better.

---

**The hive learns. Every task. Every agent. Every time.**
