# Hermes crash-recovery companion

Dependencies: none. This is a local file layout and operating pattern.

Memory Hive is the durable shared memory layer. A crash-recovery companion
is a small, machine-local scratchpad for the moments before an agent has
fully booted, when a process dies mid-task, or when the hive silo expected
by a runtime is missing and the agent needs enough context to recover safely.

This pattern came from running Hermes Agent as a daily driver. It is not a
replacement for `hive/agents/<agent-id>/log.md` or `hive/learnings/raw/`.
Use it as a local safety net, then write durable lessons back to Memory Hive
at task end.

## Layout

Create a local folder outside the shared hive:

```text
~/.hermes/crash-recovery/
|-- SESSION.md    # current machine/session state
|-- ACTIVITY.md   # timestamped local activity log
|-- PENDING.md    # prioritized restart queue
`-- DECISIONS.md  # local decisions and rationale
```

For other runtimes, keep the same filenames under that runtime's local
state directory, for example `~/.openclaw/crash-recovery/`.

## SESSION.md

Keep this short and current:

```markdown
# Crash Recovery - Current Session

Last updated: YYYY-MM-DD HH:MM
Status: active | blocked | recovering

## Machine state

- Runtime:
- Local services:
- Agent capacity:

## Rules

- Read Memory Hive first when available.
- Check process count before spawning extra agents.
- Keep external actions gated by explicit human confirmation.

## Active pending work

1. ...
```

## ACTIVITY.md

Append one line per significant local event:

```markdown
# Activity Log

Format: `YYYY-MM-DD HH:MM - description`

## YYYY-MM-DD

- HH:MM - Restarted runtime after crash and verified local service health.
```

## PENDING.md

Use this as the restart queue:

```markdown
# Pending Work

## High priority

1. Verify the interrupted task before spawning more workers.

## Medium priority

1. Move any general lessons into Memory Hive raw learnings.
```

## DECISIONS.md

Record why you chose a recovery path:

```markdown
# Key Decisions Log

| Time | Decision | Rationale |
|------|----------|-----------|
| HH:MM | Paused new delegation | Local process count was too high after crash. |
```

## Boot order

1. Read the normal Memory Hive boot surfaces.
2. Confirm the current agent has a matching silo under `hive/agents/`.
3. If the silo exists, proceed normally.
4. If the silo is missing, read crash-recovery files for minimal continuity,
   ask the human before writing outside allowed lanes, and create or repair
   the silo only when explicitly approved.
5. At task end, write durable facts back to the agent silo and generalized
   lessons to `hive/learnings/raw/`.

## What belongs here

- Local process counts, service health, and restart state.
- The interrupted task and what verification remains.
- Temporary operational decisions needed to recover safely.

## What does not belong here

- Secrets, tokens, webhook URLs, or private message contents.
- Canonical project truth that belongs in `hive/knowledge/`.
- Cross-agent lessons that belong in `hive/learnings/raw/`.
