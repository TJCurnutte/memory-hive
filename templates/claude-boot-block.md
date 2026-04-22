<!-- memory-hive:start -->
## Memory Hive — shared memory for this agent

On boot, always read these two files before responding:
- Shared context: ${HIVE_DIR}/index.md
- Your private silo: ${HIVE_DIR}/agents/<your-agent-id>/memory.md

After any significant task, append a learning to your silo's memory.md
and log what you did in log.md. Promote generalizable insights to
${HIVE_DIR}/knowledge/.

This block is managed by memory-hive's installer. Re-running the
installer will update it; your other content is untouched.
<!-- memory-hive:end -->
