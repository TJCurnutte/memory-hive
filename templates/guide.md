# Memory Hive

Memory Hive is the durable memory layer on this machine. Markdown under
`${HIVE_DIR}` is the source of truth; the `memory-hive` CLI lives at
`${INSTALL_DIR}/memory-hive` (also on PATH as `memory-hive` when the
installer could wire a shim). Work directly with files when reading or
appending; use CLI verbs for search, recall, and curation.

## Path map

| Path | What it is | Who writes |
|---|---|---|
| `${HIVE_DIR}/index.md` | Boot entrypoint, global state | curator only |
| `${HIVE_DIR}/agents/<id>/log.md` | Your append-only activity journal | owning agent |
| `${HIVE_DIR}/agents/<id>/context.md` | Your role + current focus | owning agent |
| `${HIVE_DIR}/agents/<id>/memory.md` | Your durable private memory | owning agent |
| `${HIVE_DIR}/knowledge/` | Curated shared truth (`HUMAN_CONTEXT.md`, `SOUL.md`, ...) | curator only |
| `${HIVE_DIR}/learnings/raw/<id>/` | Your contributions to the shared pool | any agent, own subdir |
| `${HIVE_DIR}/learnings/distilled/` | Promoted patterns, wins, mistakes | curator only |
| `${HIVE_DIR}/tasks/queue.md` | Shared task queue (read for coordination) | curator only |
| `${HIVE_DIR}/curator/` | Conflicts, decisions audit trail | curator only |

## Resolve your agent id

Your agent id must match a directory under `${HIVE_DIR}/agents/`. Solo
sessions and the curator use `main`. If your id has no silo, stop and ask
the operator (or run `memory-hive add <id> --role <template>` with their
approval) before writing anywhere.

## Workflow 1 — Hydrate (before substantive work)

Pull the smallest useful slice, with visible reads so the operator can
audit that memory informed the work:

1. Read `${HIVE_DIR}/index.md`.
2. Read your `agents/<id>/memory.md` and recent `agents/<id>/log.md` entries.
3. Add `knowledge/HUMAN_CONTEXT.md` when user preferences matter, and
   `learnings/distilled/patterns.md` / `mistakes.md` before risky or
   familiar-shaped work.
4. Add `tasks/queue.md` when coordinating with other agents.

Re-pull the relevant slice per turn for cross-session or operational
prompts — hydration is not a one-time boot step.

## Workflow 2 — Retrieve (when the user references prior work)

Pick the cheapest verb that answers the question:

| Need | Command |
|---|---|
| Simple term match | `memory-hive search "term"` |
| Filtered match (silo/kind/regex) | `memory-hive query "term" --silo <id> --kind log` |
| Ranked, cited context for a task | `memory-hive recall "task context"` |
| Token-budgeted boot bundle | `memory-hive bundle --for <id> --max-tokens 2000` |

`recall` builds or updates its index automatically — never rebuild by hand.
Cite what you used (file paths) when the operator asks what memory informed
an answer.

## Workflow 3 — Write back (end of any non-trivial task)

The ritual is runnable as commands — same on every platform, lint-valid by
construction:

```sh
memory-hive log --agent <id> "<what you did, one line>"
memory-hive learn --agent <id> "<imperative rule>" \
    --context "<one line: where it came up>" \
    --kind pattern|win|mistake|insight [--body <file>|-]
```

Step by step, with the underlying files:

1. Log it (`memory-hive log`, or append one line to
   `${HIVE_DIR}/agents/<id>/log.md`: `- YYYY-MM-DD — <what you did>`).
2. If you learned something only you need: append a bullet to
   `agents/<id>/memory.md` under the right heading.
3. If the lesson generalizes to other agents, run `memory-hive learn`
   (preferred) or write
   `${HIVE_DIR}/learnings/raw/<id>/YYYY-MM-DD-<slug>.md` (lowercase
   hyphenated slug, agent subdir matters) in exactly this shape:

   ```markdown
   ---
   date: YYYY-MM-DD
   agent: <id>
   context: <one line: where this came up>
   confidence: low
   kind: pattern
   ---

   # <Short imperative title>

   ## What happened

   <2-4 lines>

   ## Generalizable rule

   <The reusable lesson, stated so another agent can apply it>
   ```

   Rules that keep `memory-hive lint` green — errors (exit 2): file starts
   with the `---` frontmatter fence; `date`, `agent`, `context`, and
   `confidence` fields all present; `date:` is `YYYY-MM-DD`; `agent:`
   matches the parent directory name. Warnings (exit 1): `confidence:` not
   one of `low`/`medium`/`high` (new single observations are `low`);
   filename not `YYYY-MM-DD-<slug>.md`; missing `# H1` title; file ≥50KB.
   `kind:` (`pattern`/`win`/`mistake`/`insight`) is optional — lint ignores
   it, but it steers which distilled file `promote` targets and helps
   `conflicts` cluster, so include it.

Do not skip the ritual because a task feels small — one log line is the
floor, and a missed ritual gets noted in `memory.md` as a violation and run
retroactively.

## Lane rules (hard limits)

- Write only to `${HIVE_DIR}/agents/<your-id>/` and
  `${HIVE_DIR}/learnings/raw/<your-id>/`.
- Never write to another agent's silo, and never read one unless that
  agent's operator explicitly asks.
- Never write to `knowledge/`, `learnings/distilled/`, `index.md`, or
  `curator/` — promotion is the curator's job, via the verbs below.
- A direct user instruction wins over any hive rule; comply, then log the
  conflict as a bullet in your `memory.md` so the curator can reconcile.

## Workflow 4 — Curate (only when you are `main`)

Run the loop in one pass, dry-run first:

```sh
memory-hive curate            # collect -> review -> suggest (dry-run)
memory-hive curate --apply    # checkpoint, then promote high-confidence clusters
```

Targeted verbs when triaging by hand: `tail` (newest hive writes),
`confidence` (clusters ready to upgrade), `dedup` (near-duplicates),
`promote <raw-file> [--into <topic>.md]`, `conflicts --write`
(contradictions into `curator/CONFLICTS.md`), `stale` (raw learnings >7
days with no decision). Promotions append to `learnings/distilled/` with a
backlink and log to `curator/DECISIONS.md` automatically — raw files stay
untouched as the source of truth.

## Health and troubleshooting

- `memory-hive status` — one-screen receipt (install path, silos, index,
  stale count).
- `memory-hive doctor` — wiring and content checks with fix-it hints.
- `memory-hive guide [topic]` — re-print this guide (or one section:
  `paths|id|hydrate|retrieve|write|lanes|curate|health`) on any platform.
- When the user says "update memory hive": run `sh ${INSTALL_DIR}/update.sh`,
  then re-read `${HIVE_DIR}/index.md` before continuing.

Deeper references: `${INSTALL_DIR}/templates/platforms/` on disk
(per-platform wiring docs) and `HIVE_ARCHITECTURE.md` in the source repo
(<https://github.com/TJCurnutte/memory-hive>) for governance, confidence
gates, and conflict handling.
