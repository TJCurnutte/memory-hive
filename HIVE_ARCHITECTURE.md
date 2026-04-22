# 🧠 Memory Hive Architecture

## Overview

Memory Hive is a shared, continuously learning memory system for multi-agent AI architectures. All agents share one central knowledge base that they read from on boot and contribute to after completing tasks. The system compounds intelligence over time — every task makes the hive smarter.

---

## Core Components

### The Hive Directory

```
~/.openclaw/hive/
```

One shared directory. Not per-agent. Not siloed. Everything lives here.

---

### Sections

#### 1. `index.md` — Entry Point

All agents read this first on every spawn. Contains:
- Current status of the hive
- What agents exist
- What's being worked on
- Any urgent context

#### 2. `registry/` — Agent Roster

**`AGENTS.md`** — Every agent in the system. Each entry:
- Agent ID and name
- Role and specialty
- Current status (active/idle)
- Skills matrix reference

**`SKILLS_CATALOG.md`** — What each agent can do. Structured so any agent can look up who handles what.

#### 3. `knowledge/` — Curated Truth

Written and maintained by curator (Chief of Staff) only. Contains:
- `TRAVIS.md` — Human context (goals, preferences, tics, timezone)
- `SOUL.md` — System behavior guidelines
- `DOMAINS.md` — Area expertise definitions
- `PROJECTS.md` — Active projects and their state
- `PREFERENCES.md` — Human preferences, communication style

**Rule:** Only the curator writes to `knowledge/`. No agent contributes directly — the curator reviews and promotes.

#### 4. `learnings/` — The Learning Engine

This is where the hive gets smart.

**`raw/`** — Agent contributions, no gatekeeping.
After every task, the agent writes what they learned:
- What worked
- What didn't
- Patterns noticed
- Mistakes made
- Anything worth remembering

**Format:** `learnings/raw/[agent-id]/[YYYY-MM-DD]-[task-summary].md`

**`distilled/`** — Curated by curator.
The curator reviews `raw/` regularly and promotes valuable learnings to:
- `patterns.md` — Cross-agent patterns noticed
- `mistakes.md` — Known failure modes
- `wins.md` — Confirmed successes
- `cross-agent-insights.md` — Insights that emerged from multiple agents

**`META.json`** — Stats: total contributions, last review date, health metrics.

#### 5. `tasks/` — Shared Work Context

**`queue.md`** — What's queued up:
- Task description
- Assigned agent
- Priority
- Status
- Created date

**`active/`** — Currently running tasks:
- Brief
- Working notes
- Current state
- Blockers

#### 6. `agents/` — Personal Logs

Each agent has its own log: `agents/[agent-id]/log.md`

Not shared — personal memory for that agent. The curator doesn't read this unless asked. It stays private to each agent.

#### 7. `curator/` — Curation Workspace

The Chief of Staff's workspace for maintaining the hive.

**`DRAFT.md`** — Agent contributions pending review.

**`CONFLICTS.md`** — When two agents contradict each other. Both perspectives are preserved. Curator investigates and resolves.

**`DECISIONS.md`** — Audit trail of every curation decision. Why something was promoted, why something was rejected, why a conflict was resolved a certain way.

---

## The Curation Loop

The curator (Chief of Staff) runs this loop after every task or on a schedule:

1. **Collect** — Check `curator/DRAFT.md` for new contributions
2. **Review** — Read raw learnings, identify what matters
3. **Promote** — Move valuable learnings to `distilled/`
4. **Resolve** — Handle any conflicts in `CONFLICTS.md`
5. **Archive** — Raw learnings >7 days old → review and archive
6. **Log** — Every decision goes to `DECISIONS.md`

---

## Boot Sequence

Every agent, on every spawn:

```
1. Read index.md
2. Read registry/AGENTS.md
3. Read registry/SKILLS_CATALOG.md
4. Read knowledge/TRAVIS.md
5. Read learnings/distilled/patterns.md
6. Read tasks/queue.md
7. Read own log in agents/[id]/
8. Load active task context
9. Begin work
```

This ensures every agent has the full hive context before starting — not just their own narrow slice.

---

## Confidence System

Not all learning is equal. The system uses confidence gates:

| Level | Description | Can reach knowledge/ |
|---|---|---|
| Low | Single observation, unconfirmed | No |
| Medium | Confirmed by 2+ agents or repeated | No (but can propose) |
| High | Confirmed across time + agents | Yes |

**Upgrade rules:**
- 3 aligned low-confidence → medium
- 3 aligned medium → high

This prevents speculation from polluting core knowledge.

---

## Conflict Resolution

**Step 1:** Both perspectives written to `CONFLICTS.md`

**Step 2:** Curator investigates:
- Context-dependent? (both right in different situations)
- Which is newer?
- Requires testing?
- Can one be retracted?

**Step 3:** Resolution written to `DECISIONS.md`

**Step 4:** Loser not deleted — both remain in `CONFLICTS.md` as resolved

---

## Memory Hygiene

| Rule | Policy |
|---|---|
| Raw learnings | >7 days unreviewed → auto-escalate |
| Active tasks | >14 days → auto-escalate |
| Individual file size | Cap at 50KB |
| Daily raw writes | Cap at 20KB per file |
| Confidence gating | Low can't reach knowledge/ |
| Review cadence | Curator reviews daily |

---

## Integrating With Your Agents

### OpenClaw

All OpenClaw agents can be configured to use the hive boot sequence. Update agent system prompts to include the boot sequence, then point agents to `~/.openclaw/hive/index.md`.

### Custom Frameworks

The hive is framework-agnostic. Any agent can read from and write to the hive directory via standard file operations. Just implement:
1. Boot: read index.md first
2. Contribute: write learnings after tasks
3. Curation: if you're the curator, run the curation loop

---

## Who Runs This

The **Chief of Staff** (main agent) acts as curator. In Travis's architecture, that's the primary orchestrator that receives all human input and dispatches work. The curator role is dedicated — it maintains the hive so all other agents can focus on their specialties.

---

**The hive learns. Every task. Every agent. Every time.**