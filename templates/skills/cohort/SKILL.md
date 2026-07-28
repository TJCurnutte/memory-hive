---
name: cohort
description: "Run a 25-agent swarm for large tasks. Use when the user asks for a cohort, swarm, team of agents, ultimate implementation team, /cohort, 'spin up a team', 'orchestrate N agents', or any request that clearly needs parallel specialist agents. The skill works in any IDE or harness by emitting a plan that the host agent fans out using its own subagent primitives."
trigger: ["/cohort", "cohort", "swarm", "25 agents", "implementation team", "agent team"]
---

# /cohort — 25-agent universal swarm

When the user invokes `/cohort <task>` (or any trigger above), run Memory Hive's cohort command and fan out the resulting plan using your IDE's native subagent mechanism.

## One-line contract

1. Call `memory-hive cohort "<task>" [--agent <id>] [--json]` to get a 25-role plan.
2. Spawn one subagent per role from the returned `roles` array.
3. Pass each subagent its `prompt` plus the Memory Hive recall bundle for context.
4. Collect outputs; have the `Integrator` and `Swarm Lead` merge them.
5. Stop when SUCCESS CRITERIA are met.

## Why this is IDE-agnostic

- Devin: use `run_subagent` for each role.
- Claude Code / Claude Desktop: use Tasks/Projects or parallel `@` mentions.
- Cursor / Composer: use Composer agents or inline agent calls.
- Codex / Windsurf / aider / any harness: split the manifest into parallel tool calls, threads, or sessions.

The Memory Hive CLI owns the plan; your harness owns the fan-out. No vendor lock-in.

## Example

```
/cohort refactor the CLI to three commands and ship v3
```

Run:

```bash
memory-hive cohort "refactor the CLI to three commands and ship v3" --agent devin
```

Then spawn subagents for Planner, Code Agents 1-5, Review Agents 1-4, Research Agents 1-3, Writer, Docs, QA, Security, Integration, Quality Director, Release, Ops, Product, Design, Integrator, and Swarm Lead. Feed each the role prompt and the recall bundle.

## Rules

- Always hydrate from Memory Hive first (`memory-hive do` or `memory-hive recall bundle`) so every agent sees shared context.
- Let the host IDE pick the model per role; Memory Hive only recommends lanes, not models.
- After the swarm finishes, run `memory-hive done --agent <id> --log "..." --learn "..."`.
