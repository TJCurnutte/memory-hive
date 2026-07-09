# Memory Hive Bench Suite

Run the reproducible v2 benchmark from the repository root:

```bash
MEMORY_HIVE_DIR="$PWD/hive" ./memory-hive bench suite --json
```

The JSON result records naive full-boot, v0.3.2-style HyperRecall, and v2
optimize+bundle baselines. Performance claims are gated by the definitions in
the JSON `methodology` field, especially token reduction for agent-turn speed
and `naive_tokens / v2_tokens` for efficiency.
