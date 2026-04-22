# 🧠 Memory Hive Architecture

## Overview

Memory Hive is a shared, continuously learning memory system for multi-agent AI architectures. Every agent has **two memory layers** — a private silo for personal continuity and a shared hive for collective intelligence. The system compounds over time: every task makes the hive smarter, every agent keeps its own context, and a curator maintains the shared knowledge base.

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

Written and maintained by curator only. Contains:
- `HUMAN_CONTEXT.md` — Human context (goals, preferences, tics, timezone)
- `SOUL.md` — System behavior guidelines
- `DOMAINS.md` — Area expertise definitions
- `PROJECTS.md` — Active projects and their state
- `PREFERENCES.md` — Human preferences, communication style

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

**`distilled/`** — Curated by curator.
The curator reviews `raw/` regularly and promotes valuable learnings to:
- `patterns.md` — Cross-agent patterns noticed
- `mistakes.md` — Known failure modes
- `wins.md` — Confirmed successes
- `cross-agent-insights.md` — Insights from multiple agents working together

**`META.json`** — Stats: total contributions, last review date, health metrics.

#### 5. `tasks/` — Shared Work Context

**`queue.md`** — What's queued:
- Task description, assigned agent, priority, status, created date

**`active/`** — Currently running tasks:
- Brief, working notes, current state, blockers

#### 6. `curator/` — Curation Workspace

The curator's workspace for maintaining the hive.

**`DRAFT.md`** — Pending contributions from agents.

**`CONFLICTS.md`** — When two agents contradict each other. Both perspectives preserved until resolved.

**`DECISIONS.md`** — Audit trail of every curation decision.

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

The curator runs this loop after every task or on a schedule:

1. **Collect** — Check `curator/DRAFT.md` for new contributions
2. **Review** — Read raw learnings, identify what matters
3. **Promote** — Move valuable learnings to `learnings/distilled/`
4. **Resolve** — Handle any conflicts in `curator/CONFLICTS.md`
5. **Archive** — Raw learnings >7 days old → review and archive
6. **Log** — Every decision goes to `DECISIONS.md`

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
7. Read own private silo: agents/[id]/log.md
8. Read own context: agents/[id]/context.md
9. Check for active task in hive/tasks/active/
10. Begin work
```

This ensures every agent has full hive context plus its own personal context before starting.

---

## Task Completion Flow

When an agent completes a task:

```
1. Agent writes learnings to hive/learnings/raw/[agent-id]/
2. Agent updates own silo: agents/[agent-id]/log.md
3. Agent submits contribution summary to curator/DRAFT.md
4. Curator reviews within 24h
5. Curator promotes valuable learnings to learnings/distilled/
6. Curator logs decision to curator/DECISIONS.md
7. Next agent to spawn sees updated hive
8. System is now smarter than before the task
```

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

This prevents speculation from polluting core knowledge.

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
| Raw learnings | >7 days unreviewed → auto-escalate |
| Active tasks | >14 days → auto-escalate |
| Individual file size | Cap at 50KB |
| Daily raw writes | Cap at 20KB per file |
| Confidence gating | Low can't reach knowledge/ |
| Private silos | Never auto-cleaned (agent owns) |
| Review cadence | Curator reviews daily |

---

## Integrating With Your Agents

### OpenClaw

All agents can be configured to use the hive boot sequence. Each agent's workspace becomes:
- `~/.openclaw/workspace-[agent-id]/` — agent's own dir
- `~/.memory-hive/hive/` — shared hive
- `~/.memory-hive/hive/agents/[agent-id]/` — private silo

### Custom Frameworks

The hive is framework-agnostic. Any agent can:
- Read from and write to the hive via standard file operations
- Keep personal context in `agents/[id]/`
- Implement the boot sequence and task completion flow independently

Key integration points:
1. On agent spawn → run boot sequence
2. On task completion → write to `learnings/raw/[id]/` and `agents/[id]/log.md`
3. If curator → run curation loop
4. All agents → read `learnings/distilled/` before starting tasks

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