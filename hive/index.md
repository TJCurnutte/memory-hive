# 🧠 Memory Hive — Entry Point

**Last updated:** 2026-04-22
**Status:** Active — double-layer memory system online

## The Two-Layer System

```
LAYER 1 — PRIVATE SILOS (personal, agent-owned)
agents/[agent-id]/
├── log.md     ← working notes
├── context.md ← state and preferences
└── memory.md  ← private learnings

LAYER 2 — SHARED HIVE (collective intelligence)
hive/
├── index.md          ← you are here
├── registry/         ← who's who
├── knowledge/        ← curated truth
├── learnings/        ← raw → distilled
├── tasks/            ← shared work queue
└── curator/          ← curation workspace
```

Every agent has both layers. Silos for personal continuity. Hive for shared intelligence. Both matter.

---

## Quick Facts

- **Hive location:** `~/.openclaw/hive/`
- **Private silos:** `~/.openclaw/hive/agents/[agent-id]/`
- **Curator:** Chief of Staff (main agent)
- **Number of agents:** 13
- **Last full update:** 2026-04-22

---

## Who's Active

| Agent | Status | Private Silo | Current Task |
|---|---|---|---|
| main (Chief of Staff) | Active | `agents/main/` | Hive curation |
| coder | Idle | `agents/coder/` | — |
| vibe-coder | Idle | `agents/vibe-coder/` | — |
| security-auditor | Idle | `agents/security-auditor/` | — |
| social-media-mgr | Idle | `agents/social-media-mgr/` | — |
| sdr-1 | Idle | `agents/sdr-1/` | — |
| sdr-2 | Idle | `agents/sdr-2/` | — |
| web-dev | Idle | `agents/web-dev/` | — |
| api-expert | Idle | `agents/api-expert/` | — |
| research-analyst | Idle | `agents/research-analyst/` | — |
| data-analyst | Idle | `agents/data-analyst/` | — |
| content-strategist | Idle | `agents/content-strategist/` | — |
| cxaas-specialist | Idle | `agents/cxaas-specialist/` | — |

---

## Active Projects

- `memory-hive` — open-source two-layer memory system (GitHub: TJCurnutte/memory-hive)

## Current Priorities

1. First real task execution → first real learning contributions
2. Agents begin using both silo and hive on boot
3. Curator starts curation loop with genuine learnings

---

## Recent Learnings

_(empty — first real task hasn't completed yet)_

When the first task completes, agents write to `hive/learnings/raw/[agent-id]/` and the curator promotes to `hive/learnings/distilled/`. Check those files for canonical learnings.

---

## Boot Sequence (Two-Layer)

Every agent, on every spawn:

```
1. Read hive/index.md                    ← current hive state
2. Read hive/registry/AGENTS.md          ← who's who
3. Read hive/registry/SKILLS_CATALOG.md  ← what they can do
4. Read hive/knowledge/HUMAN_CONTEXT.md ← human context
5. Read hive/learnings/distilled/patterns.md  ← what works
6. Read hive/tasks/queue.md             ← what's queued

7. Read agents/[id]/log.md              ← SILO: own working notes
8. Read agents/[id]/context.md         ← SILO: own state
9. Check hive/tasks/active/            ← current task context

10. Begin work
```

---

## Documentation

- [HIVE_ARCHITECTURE.md](../HIVE_ARCHITECTURE.md) — Full system design
- [registry/AGENTS.md](./registry/AGENTS.md) — Agent roster + silo mapping
- [registry/SKILLS_CATALOG.md](./registry/SKILLS_CATALOG.md) — Skills matrix
- [knowledge/HUMAN_CONTEXT.md](./knowledge/HUMAN_CONTEXT.md) — Human context
- [learnings/distilled/](./learnings/distilled/) — Curated learnings

---

**Read this on every boot. Write to silos and hive after every task.**
**Double layer: silos remember, hive compounds.**