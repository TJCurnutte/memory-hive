# Skills Catalog

Matrix of what each agent in your hive can do. Used for routing decisions.

This catalog is **user-maintained**. The installer seeds it with just the
curator row. As you add agents, append their skills below so the curator
(and you) can route tasks to the right one.

## Format

Group skills by category. For each row, list the agent IDs that have the
skill. Routing is as simple as "task X needs skill Y → any agent listed
under Y can handle it."

## Categories (examples)

Adapt these to your roster. The categories below are examples, not
requirements — delete the ones you don't need and add your own.

### Coordination

| Skill | Agents |
|---|---|
| Task triage & delegation | main |
| Memory curation | main |
| Conflict resolution | main |
| Multi-agent orchestration | main |

### Development (example — populate as you add agents)

| Skill | Agents |
|---|---|
| Architecture & system design | _(add agent IDs)_ |
| Backend development | _(add agent IDs)_ |
| Frontend development | _(add agent IDs)_ |
| Debugging | _(add agent IDs)_ |
| Code review | _(add agent IDs)_ |
| Testing & QA | _(add agent IDs)_ |

### Research & Analysis (example)

| Skill | Agents |
|---|---|
| Deep research | _(add agent IDs)_ |
| Data analysis | _(add agent IDs)_ |
| Report synthesis | _(add agent IDs)_ |

### Writing & Content (example)

| Skill | Agents |
|---|---|
| Long-form writing | _(add agent IDs)_ |
| Editing & tightening | _(add agent IDs)_ |
| Tone matching | _(add agent IDs)_ |

### Planning (example)

| Skill | Agents |
|---|---|
| Breaking down tasks | _(add agent IDs)_ |
| Risk identification | _(add agent IDs)_ |
| Dependency mapping | _(add agent IDs)_ |

---

## Routing Guide

When a task comes in, route to an agent whose primary skill matches. If no
agent matches, the curator (`main`) picks it up by default.

- **Anything unclear or cross-cutting** → `main`
- **Every other bucket** → whichever agent you listed for that skill

Update this catalog every time you add or remove an agent.

---

**Keep this in sync with `AGENTS.md`. They should always agree on who
exists.**
