# Memory Hive wiring — Amazon Q Developer CLI

**Detected dir:** `~/.aws/amazonq/`
**Target file:** `~/.aws/amazonq/rules/memory-hive.md`
**Integration:** auto-inject (managed block)

Amazon Q Developer CLI loads markdown rules from `.amazonq/rules/` at
project level and (via `/context add --global`) at user level. The
installer drops a single `memory-hive.md` rule into
`~/.aws/amazonq/rules/` and assumes you add it to global context once:

```bash
q chat
/context add --global ~/.aws/amazonq/rules/memory-hive.md
/context show   # verify
```

After that, every Amazon Q chat session across every project will pick
up the hive instructions.

The rule file itself is managed by the `<!-- memory-hive:start -->` /
`<!-- memory-hive:end -->` markers. Re-runs refresh it in place.

Opt out with `MEMORY_HIVE_SKIP_AMAZON_Q=1`.
