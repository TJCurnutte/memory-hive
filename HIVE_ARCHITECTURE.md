# Memory Hive Architecture

Conceptual model for the two-layer memory system. For installer
behavior and CLI usage see [INTEGRATION.md](INTEGRATION.md); for the
product overview see [README.md](README.md).

## Overview

Memory Hive is a shared, continuously learning memory system for
multi-agent AI architectures. Every agent has **two memory layers** —
a private silo for personal continuity and a shared hive for
collective intelligence. The system compounds over time: every task
makes the hive smarter, every agent keeps its own context, and a
curator maintains the shared knowledge base.

---

## The Two-Layer Architecture

### Layer 1 — Private Silos

Each agent has its own personal memory space in `agents/[agent-id]/`:

```
agents/[agent-id]/
├── log.md        ← Personal notes, working context, ongoing thoughts
├── context.md    ← Agent-specific state, preferences, relationships
└── memory.md     ← Private learnings only this agent needs
```

**Silo rules:**
- Only the owning agent reads and writes to their silo
- Curator never reads private silos (unless agent explicitly asks)
- Silos never auto-cleaned — the agent owns its own space
- Silos provide continuity — agent wakes up knowing what it was doing

### Layer 2 — Shared Hive

All agents read from and contribute to the collective brain in `hive/`:

```
hive/
├── index.md
├── registry/
├── knowledge/
├── learnings/
├── tasks/
└── curator/
```

**Hive rules:**
- All agents can read everything in the hive
- All agents write to `learnings/raw/[agent-id]/`
- Only the curator writes to `knowledge/` and `learnings/distilled/`
- Hive is the cross-pollination layer — what one agent learns benefits all

---

## Core Components

### The Hive Directory

```
~/.memory-hive/hive/          ← Shared brain (all agents read/write)
~/.memory-hive/hive/agents/   ← Private silos (one per agent)
```

---

### Sections — Shared Hive

#### 1. `index.md` — Entry Point

All agents read this first on every spawn. Contains:
- Current status of the hive
- What agents exist and their status
- Active projects and priorities
- Any urgent context
- Recent learnings worth knowing

#### 2. `registry/` — Agent Roster

**`AGENTS.md`** — Every agent in the system:
- Agent ID and name
- Role and specialty
- Current status (active/idle)
- Skills matrix reference

**`SKILLS_CATALOG.md`** — What each agent can do. Structured for routing decisions.

#### 3. `knowledge/` — Curated Truth

Written and maintained by curator only. Ships with three canonical files:
- `HUMAN_CONTEXT.md` — Human context (goals, preferences, tics, timezone)
- `SOUL.md` — System behavior guidelines
- `DOMAINS.md` — Area expertise definitions

**`knowledge/` is expandable.** The curator adds topical files as the hive
grows — any persistent truth the team needs to reference, in its own file:
- `PROJECTS.md` — active projects and their state
- `PREFERENCES.md` — detailed preferences and communication style
- `COMPANY.md`, `COMPLIANCE.md`, `<topic>.md` — whatever the team needs

There's no fixed set. The canonical three are the starting point; the
curator promotes topical files whenever repeated references warrant a
dedicated home.

**Rule:** Only the curator writes to `knowledge/`. No agent contributes directly to curated truth — the curator reviews and promotes.

#### 4. `learnings/` — The Learning Engine

The core of the hive's intelligence. Two-tier system:

**`raw/[agent-id]/`** — Agent contributions, no gatekeeping.
After every task, the agent writes what they learned:
- What worked
- What didn't
- Patterns noticed
- Mistakes made
- Anything worth remembering

Format: `learnings/raw/[agent-id]/[YYYY-MM-DD]-[task-summary].md`

Memory entries move through explicit states for continuity control:

- `active` — currently trusted and on the hot path
- `superseded` — replaced by a newer authoritative alternative
- `deprecated` — retained for audit, no longer recommended for active context

**`distilled/`** — Curated by curator.
The curator reviews `raw/` regularly and promotes valuable learnings. Four
canonical files, plus topical files as the hive grows:
- `patterns.md` — Cross-agent patterns noticed
- `mistakes.md` — Known failure modes
- `wins.md` — Confirmed successes
- `cross-agent-insights.md` — Insights from multiple agents working together
- `<topic>.md` — Any topic that accumulates enough distilled learnings to
  warrant its own file (e.g. `auth-patterns.md`, `deployment.md`,
  `customer-comms.md`). The canonical four are defaults, not a cap.

**`META.json`** — Stats: total contributions, last review date, health metrics.

#### 5. `tasks/` — Shared Work Context

**`queue.md`** — What's queued:
- Task description, assigned agent, priority, status, created date

**`active/`** — Currently running tasks:
- Brief, working notes, current state, blockers

#### 6. `curator/` — Curation Workspace

The curator's workspace for maintaining the hive.

**`CONFLICTS.md`** — When two agents contradict each other. Both
perspectives preserved until resolved. Populated by
[`memory-hive conflicts --write`](INTEGRATION.md).

**`DECISIONS.md`** — Audit trail of every curation decision. Appended
to by [`memory-hive promote`](INTEGRATION.md) and
[`memory-hive curate --apply`](INTEGRATION.md).

> Note: earlier versions of this architecture had a `DRAFT.md` queue
> for pending contributions. In practice agents write directly to
> `learnings/raw/[agent-id]/` and the curator scans that path — there
> is no separate draft step. The verbs `tail`, `digest`, `confidence`,
> and `dedup` give the curator everything they need to triage raw
> contributions without an intermediate queue.

---

### Sections — Private Silos

#### `agents/[agent-id]/` — Personal Memory

Each agent has its own private directory:

**`log.md`** — Personal working notes. The agent's running journal of what it's doing, what it's thought about, what's in progress. Nobody else reads this.

**`context.md`** — Agent-specific state. How this agent prefers to work, what it's currently focused on, relationships with other agents (e.g., "reviewer: pairs with coder on every PR").

**`memory.md`** — Private learnings. Things this agent learned that don't need to be in the shared hive but are worth remembering (personal notes, agent-specific patterns, private observations).

**Silo privacy is absolute.** The curator only accesses a private silo if the agent explicitly asks for help.

---

## The Curation Loop

The curator runs this loop after every task or on a schedule. The
shipped CLI verbs collapse most of it into one command:

1. **Collect** — `memory-hive tail` or `digest` shows new raw
   contributions; `dedup` clusters near-duplicates across agents
2. **Review** — `memory-hive confidence` flags clusters that have
   crossed an upgrade threshold; `lint` validates frontmatter
3. **Promote** — `memory-hive promote <raw-file>` appends a summary
   with backlink to `learnings/distilled/<topic>.md` (raw stays as
   source of truth)
4. **Resolve** — `memory-hive conflicts --write` populates
   `curator/CONFLICTS.md` when two agents disagree
5. **Triage stale** — `memory-hive stale` lists raw learnings >7 days
   old without a curator decision
6. **Log** — Every promotion + every conflict resolution lands in
   `DECISIONS.md` automatically
7. **Stage state** — stale or conflicting `active` records are moved to
   `superseded` or `deprecated` after curator confirmation.

`memory-hive curate` runs steps 1–5 in one pass and prints a single
summary line. Default is dry-run; `--apply` performs promotions for
clusters at the high-confidence threshold.

`memory-hive optimize` is the built-in Optimizer pass around this loop. It
runs `doctor`, `curate`, `digest --week`, `stats`, and `stale --count`, then
prints one operator report. Use `memory-hive optimize --report
hive/optimizer/SWARM_SIGNALS.md` when a swarm-routing lane needs a compact
health/routing signal without scraping full command output.

---

## Boot Sequence

Every agent, on every spawn:

```
1. Read hive/index.md
2. Read hive/registry/AGENTS.md
3. Read hive/registry/SKILLS_CATALOG.md
4. Read hive/knowledge/HUMAN_CONTEXT.md
5. Read hive/learnings/distilled/patterns.md
6. Read hive/tasks/queue.md
7. Build `hive-bundle` for this agent (`memory-hive bundle --for <agent> --max-tokens N`)
8. Read own private silo: agents/[id]/log.md
9. Read own context: agents/[id]/context.md
10. Check for active task in hive/tasks/active/
11. Begin work
```

This gives every agent the curated hive surfaces plus its own personal
context before starting. It is intentionally not a full replay of the
archive: raw captures, raw learnings, and other agents' private silos stay
out of the prompt unless the agent explicitly queries them.

Per-turn context is ranked and bounded so the active working set stays
small and current. Record state (`active`, `superseded`, `deprecated`) keeps
continuity auditable without flooding prompt windows.

---

## Task Completion Flow

When an agent completes a task:

```
1. Agent writes learnings to hive/learnings/raw/[agent-id]/
2. Agent updates own silo: agents/[agent-id]/log.md
3. Curator scans hive/learnings/raw/ (memory-hive tail / digest /
   confidence / dedup surface what's new and what aligns)
4. Curator promotes valuable learnings to learnings/distilled/ via
   memory-hive promote (or memory-hive curate --apply for the whole
   loop in one pass)
5. Curator logs decision to curator/DECISIONS.md (automatic on promote)
6. Next agent to spawn sees updated hive
7. System is now smarter than before the task
```

There is no separate `DRAFT.md` queue. `learnings/raw/[agent-id]/`
*is* the queue.

---

## The Three-Tier Memory Flow

Memory Hive distinguishes between three tiers of content, each with a
different writer, format, and permanence. Understanding the tiers is the
difference between "a place agents write notes" and "a system that gets
smarter over time":

| Tier | Source | Location | Writer | Purpose |
|---|---|---|---|---|
| **1. Raw external** | Machine ingestion from outside the hive | `hive/raw/<source>/` | Ingester scripts (Discord, Slack, webhooks, email, etc.) | Capture context that happened outside any agent's session, so agents can read it on boot |
| **2. Structured** | Agents observing + synthesizing | Silo `log.md`, `learnings/raw/[agent-id]/` | Agents, after each task | Agent-owned notes and raw contributions to the shared learning pool |
| **3. Distilled** | Curator promoting valuable structured content | `learnings/distilled/*.md`, `knowledge/` | Curator only | Canonical truth — patterns, wins, mistakes, cross-agent insights |

**How the tiers compose:**

```
Tier 1 (raw external)
       │
       │  agent reads on boot
       ▼
Tier 2 (agent synthesis)  ◄──  agents observe in session
       │
       │  curator promotes
       ▼
Tier 3 (distilled truth)
```

- **Tier 1 is optional.** If you don't run an ingester, `hive/raw/` stays empty
  and the hive still works — it's just limited to what agents see in their own
  sessions.
- **Tier 1 writes a simple format** agents can skim efficiently. See
  [`templates/memory-entry.md`](templates/memory-entry.md) for the format spec
  and [`examples/ingesters/`](examples/ingesters/) for working ingester
  implementations.
- **Tier 2 and Tier 3 are the core system** — they work identically with or
  without Tier 1.

### Ingesters: how external context gets in

An **ingester** is anything that writes to `hive/raw/<source>/`. Ingesters
are:

- **External:** they don't need to be running inside an agent session
- **Append-only:** they write, they never edit existing entries
- **Scoped:** one `<source>` subfolder per ingester (e.g.
  `hive/raw/discord/`, `hive/raw/slack/`, `hive/raw/email/`)
- **Simple:** they follow the format in `templates/memory-entry.md` so every
  agent can parse them uniformly

The repo ships two reference ingesters under `examples/ingesters/`:
- `discord/` — polls Discord channels via the bot API every N seconds
- `generic-webhook/` — a minimal HTTP endpoint that accepts POSTs and writes
  them to `hive/raw/<source>/<topic>.md`

Both are optional. Copy and adapt for your own platform (Linear, GitHub,
email, Slack, etc.).

---

## Confidence System

Not all learning is equal. The hive uses confidence gates:

| Level | Description | Can reach knowledge/ |
|---|---|---|
| Low | Single observation, unconfirmed | No |
| Medium | Confirmed by 2+ agents or repeated | No (can propose) |
| High | Confirmed across time + agents | Yes |

**Upgrade rules:**
- 3 aligned low-confidence observations → medium
- 3 aligned medium → high
- 3+ aligned high → ready for promotion to `distilled/`

This prevents speculation from polluting core knowledge.

Run `memory-hive confidence` to scan `learnings/raw/<agent>/*.md`,
cluster aligned observations by normalized title, and surface the
upgrades a curator should consider. The verb suggests only — the
curator still decides what to actually promote.

---

## Conflict Resolution

**Step 1:** Both perspectives written to `curator/CONFLICTS.md`

**Step 2:** Curator investigates:
- Context-dependent? (both right in different situations)
- Which is newer?
- Requires testing?
- Can one be retracted?

**Step 3:** Resolution written to `DECISIONS.md`

**Step 4:** Both perspectives remain in `CONFLICTS.md` as historical record

---

## Memory Hygiene

| Rule | Policy |
|---|---|
| Raw learnings | >7 days unreviewed → surfaced by `memory-hive doctor` and `memory-hive stale`; escalates to a doctor warning when count exceeds `MEMORY_HIVE_STALE_THRESHOLD` (default 20). "Unreviewed" = basename absent from `curator/DECISIONS.md`. |
| Active tasks | >14 days → auto-escalate |
| Individual file size | Cap at 50KB |
| Daily raw writes | Cap at 20KB per file |
| Confidence gating | Low can't reach knowledge/ |
| Private silos | Never auto-cleaned (agent owns) |
| Review cadence | Curator reviews daily |
| Built-in optimizer | `memory-hive optimize` chains health + curation + digest + stats; optional reports feed built-in swarm-routing signals. |

---

## Integrating With Your Agents

The hive is framework-agnostic — nothing here depends on Claude Code,
OpenClaw, or any specific runtime. Any agent, in any framework, can:

- Read from and write to the hive via standard file operations
- Keep personal context in `agents/[id]/`
- Implement the boot sequence and task completion flow independently

Key integration points:

1. On agent spawn → run the boot sequence
2. On task completion → write to `learnings/raw/[id]/` and `agents/[id]/log.md`
3. If curator → run the curation loop
4. All agents → read `learnings/distilled/` before starting tasks

For Claude Code and OpenClaw users, the installer wires this up
automatically. See [INTEGRATION.md](INTEGRATION.md) for what it does
and [MIGRATION.md](MIGRATION.md) if you're moving from an older setup.

---

## Who Runs This

The **Chief of Staff** (main agent) acts as curator. In any architecture, this is the primary orchestrator — the agent that receives all human input and dispatches work. The curator maintains the hive so all other agents can focus on their specialties.

The curator is the only agent that:
- Writes to `knowledge/`
- Modifies `learnings/distilled/`
- Resolves conflicts in `CONFLICTS.md`
- Updates `DECISIONS.md`

All other agents contribute to `learnings/raw/` and maintain their private silos.

---

**The hive learns. Every task. Every agent. Every time.**
**Private silos remember. Shared hive compounds.**
