# Memory Entry Format

This is the canonical format for entries written to `hive/raw/<source>/`
by ingesters (Discord bot, Slack app, email poller, webhook receivers,
etc.). Agents read these files on boot to pick up context that happened
outside any agent's own session.

There are two shapes — one for machine-written raw capture, one for
agent-written structured synthesis. Ingesters use the raw shape.
Agents, when summarizing a conversation into their silo, use the
structured shape.

---

## Shape 1 — Raw capture (ingester-written)

Simple, mechanical, append-only. One entry per message / event. Machines
write these; humans rarely read them directly (agents summarize from
them).

```markdown
## [2026-04-23T14:32:11+00:00] #<source-channel> — @<author>
**Message:** <verbatim content, trimmed to 600 chars>
**Attachments:** <list of file names / URLs, or "(none)">
```

**Rules:**
- ISO-8601 timestamp in the header so entries sort chronologically
- `<source-channel>` identifies where it came from (`#general`,
  `#eng-team`, `inbox`, etc.)
- `@<author>` is the human / bot / system that created the message
- Content is trimmed at ~600 chars — ingesters must never truncate mid-
  sentence without an ellipsis
- Every entry ends with a blank line before the next heading

## Shape 2 — Structured synthesis (agent-written)

What an agent writes when it *summarizes* a conversation or external
event into its own silo or into `learnings/raw/<agent-id>/`. Higher
signal-to-noise than raw capture.

```markdown
## [2026-04-23 14:32] #<channel> — @<author>
**Topic:** <one-line summary of what the exchange was about>
**Key Points:**
- <bullet>
- <bullet>
**Decisions:** <what was concluded, or "none">
**For Follow-up:** <open questions or next steps, or "none">
```

**Rules:**
- Date-only timestamp is fine (no seconds needed; this is synthesis,
  not raw capture)
- Every section header must be present; use "none" when empty
- Key Points are bullets, not prose — agents scan them
- Decisions and Follow-ups are the actionable outputs
- Synthesis is signed by the agent that wrote it via the silo path
  (no signature line needed)

---

## Which shape goes where

| Location | Shape | Example |
|---|---|---|
| `hive/raw/<source>/` | Raw capture | `hive/raw/discord/eng-team.md` |
| `hive/agents/<id>/log.md` | Structured (agent's own log) | Agent summarizes a Discord thread it read on boot |
| `hive/learnings/raw/<id>/` | Structured (contribution) | Agent submits a generalizable pattern it saw |
| `hive/learnings/distilled/*.md` | Curator prose | Canonical distilled form, free shape |

---

## Why two shapes, not one

Raw capture is high-volume (hundreds to thousands of entries). A
minimal shape makes ingesters fast, cheap, and easy to write — any
platform can produce it in a few lines of code. Agents then pay the
cost of synthesis once, turning raw capture into structured entries
that the rest of the hive (and the curator) actually consumes.

If you only have one shape, you either (a) force agents to write raw
capture (wasteful) or (b) force ingesters to synthesize (slow, and they
don't have the context to do it well).
