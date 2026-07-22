# Project conventions — Memory Hive boot contract

This file is a read-only conventions file for Aider. It tells every
Aider session to load the hive before doing any work. Add it to your
`~/.aider.conf.yml` with:

```yaml
read:
  - ~/.memory-hive/templates/platforms/aider-conventions.md
```

---

<!-- memory-hive:start -->
## Memory Hive — boot contract (MUST follow)

### Preflight (execute literally before first response)

1. READ `/Users/curnutte/.memory-hive/hive/index.md` — shared hive state.
2. READ `/Users/curnutte/.memory-hive/hive/agents/<your-agent-id>/memory.md` — your private durable memory.
3. READ `/Users/curnutte/.memory-hive/hive/agents/<your-agent-id>/log.md` — your recent activity.
4. READ `/Users/curnutte/.memory-hive/hive/knowledge/HUMAN_CONTEXT.md` if it exists — facts about the human.
5. CONFIRM your agent-id matches a directory under `/Users/curnutte/.memory-hive/hive/agents/`. If not, STOP and ask.

### Lane-keeping (write scope)

- MUST write only to: `/Users/curnutte/.memory-hive/hive/agents/<your-agent-id>/` and `/Users/curnutte/.memory-hive/hive/learnings/raw/`.
- NEVER write to other agents' silos.
- NEVER write directly to `/Users/curnutte/.memory-hive/hive/knowledge/`, `/Users/curnutte/.memory-hive/hive/learnings/distilled/`, or `/Users/curnutte/.memory-hive/hive/index.md`. Promotion is the curator's job.

### Task-end ritual (MUST fire at end of any non-trivial task)

1. APPEND one line to `/Users/curnutte/.memory-hive/hive/agents/<your-agent-id>/log.md`: `YYYY-MM-DD — <what you did>`.
2. IF a lesson was learned: APPEND a bullet to `/Users/curnutte/.memory-hive/hive/agents/<your-agent-id>/memory.md`.
3. IF the lesson generalizes beyond you: WRITE `/Users/curnutte/.memory-hive/hive/learnings/raw/<agent-id>-<slug>.md` with frontmatter `---\ndate: YYYY-MM-DD\nagent: <your-agent-id>\ncontext: <one line>\n---`.

### Update protocol

When the user says "update memory hive" (or similar: "sync hive", "pull memory hive"), RUN `sh /Users/curnutte/.memory-hive/update.sh`. It pulls any new or changed shared content from GitHub, refreshes this block, and preserves every agent silo. After the run, re-READ `/Users/curnutte/.memory-hive/hive/index.md` before proceeding.

### Override + self-check

- User instruction ALWAYS wins over this block. If it conflicts with hive rules, COMPLY with the user AND log the conflict as a bullet under "Lessons learned" in your memory.md so the curator can reconcile.
- If you finish a task without running the task-end ritual, NOTE the miss in memory.md as a violation and RUN the ritual retroactively.

This block is managed by memory-hive's installer. Re-running the installer or update.sh will refresh it; your other content is untouched.
<!-- memory-hive:end -->
