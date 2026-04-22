# Agent Registry

All agents in the system. Each agent reads this on boot.

This file is a **user-maintained** roster. The installer seeds it with the
reserved `main` (curator) row. Add your own agents below as you create
silos — keep the table in sync with what actually exists in
`hive/agents/`.

## Format

Each agent entry has:

- `id` — lowercase, filesystem-safe (matches the silo directory name)
- **Role** — one-line description of responsibility
- **Specialty** — what this agent is best at
- **Status** — `Active`, `Idle`, or `Archived`
- **Private silo** — path to the agent's silo under `agents/`
- **Notes** — anything else worth knowing

## Roster

### main — Chief of Staff (reserved: curator)
- **Role:** Primary coordinator, first point of contact, hive curator
- **Specialty:** Triage, delegation, curation, conflict resolution
- **Status:** Active
- **Private silo:** `agents/main/`
- **Notes:** The `main` silo is the only one that ships with the installer.
  It is the curator — the single agent that writes to `knowledge/` and
  `learnings/distilled/`. Every other agent in this registry was added by
  you.

---

## Agent → Silo Mapping

| Agent ID | Private Silo Location | Role |
|---|---|---|
| main | `agents/main/` | Curator |

_Append a row for every silo you create so the registry stays accurate._

---

## Adding Agents

Three ways to add an agent:

1. **Installer wizard** — run `sh ~/.memory-hive/install.sh` on a tty. It
   walks you through naming and role selection.
2. **CLI** — `sh ~/.memory-hive/memory-hive add <name> --role <template>`
   where `<template>` is one of `coder`, `reviewer`, `researcher`,
   `writer`, `planner`, or a path to a custom role file.
3. **Manual** — `sh ~/.memory-hive/create-agent.sh <name>` creates the
   silo skeleton (`log.md`, `context.md`, `memory.md`); edit
   `context.md` to fill in the role.

After any of those, append the new agent to the roster above.

---

**Remember:** this file is a human-maintained index. If it drifts from
`hive/agents/`, the agents still exist — they just aren't documented.
Keeping it current is the curator's job.
