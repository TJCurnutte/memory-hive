# Memory Hive wiring — Aider

**Detected marker:** `~/.aider.conf.yml` exists, or `aider` on PATH
**Integration:** manual (two-step — safer than splicing YAML)

Aider reads read-only convention files configured via `.aider.conf.yml`.
The installer can't safely merge into YAML (no managed-block convention
in structured config), so setup is a one-time manual step.

## Step 1 — point Aider at the hive block

Add this to your `~/.aider.conf.yml` (create it if missing):

```yaml
read:
  - ~/.memory-hive/templates/platforms/aider-conventions.md
```

If you already have `read:` entries, just add the path to the list.

## Step 2 — drop in the hive conventions file

The installer writes a ready-to-read conventions file at
`~/.memory-hive/templates/platforms/aider-conventions.md` — it contains
the same boot instructions as every other platform, framed as read-only
project conventions Aider always honors.

Re-running the installer refreshes the conventions file. Your
`~/.aider.conf.yml` is never touched.

Opt out with `MEMORY_HIVE_SKIP_AIDER=1`.
