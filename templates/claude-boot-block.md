<!-- memory-hive:start -->
## Memory Hive — boot contract (MUST follow)

### Preflight (execute literally before first response)

1. READ `${HIVE_DIR}/index.md` — shared hive state.
2. READ `${HIVE_DIR}/agents/<your-agent-id>/memory.md` — your private durable memory.
3. READ `${HIVE_DIR}/agents/<your-agent-id>/log.md` — your recent activity.
4. READ `${HIVE_DIR}/knowledge/HUMAN_CONTEXT.md` if it exists — facts about the human.
5. CONFIRM your agent-id matches a directory under `${HIVE_DIR}/agents/`. If not, STOP and ask.

### Lane-keeping (write scope)

- MUST write only to: `${HIVE_DIR}/agents/<your-agent-id>/` and `${HIVE_DIR}/learnings/raw/`.
- NEVER write to other agents' silos.
- NEVER write directly to `${HIVE_DIR}/knowledge/`, `${HIVE_DIR}/learnings/distilled/`, or `${HIVE_DIR}/index.md`. Promotion is the curator's job.

### Task-end ritual (MUST fire at end of any non-trivial task)

1. APPEND one line to `${HIVE_DIR}/agents/<your-agent-id>/log.md`: `YYYY-MM-DD — <what you did>`.
2. IF a lesson was learned: APPEND a bullet to `${HIVE_DIR}/agents/<your-agent-id>/memory.md`.
3. IF the lesson generalizes beyond you: WRITE `${HIVE_DIR}/learnings/raw/<agent-id>-<slug>.md` with frontmatter `---\ndate: YYYY-MM-DD\nagent: <your-agent-id>\ncontext: <one line>\n---`.

### Override + self-check

- User instruction ALWAYS wins over this block. If it conflicts with hive rules, COMPLY with the user AND log the conflict as a bullet under "Lessons learned" in your memory.md so the curator can reconcile.
- If you finish a task without running the task-end ritual, NOTE the miss in memory.md as a violation and RUN the ritual retroactively.

This block is managed by memory-hive's installer. Re-running the installer will update it; your other content is untouched.
<!-- memory-hive:end -->
