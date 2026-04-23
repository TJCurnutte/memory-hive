# `hive/raw/` — External Context Capture

This folder holds **Tier 1** content in the Memory Hive three-tier model:
raw external context written by ingesters (not by agents).

Each ingester gets its own subfolder, scoped by source:

```
hive/raw/
├── discord/       ← messages captured by the Discord ingester
├── slack/         ← messages captured by a Slack ingester
├── email/         ← inbound email captured by a mail ingester
├── webhook/       ← events captured by the generic webhook ingester
└── <your-source>/ ← whatever you wire up
```

## Rules

- **Append-only.** Ingesters write new entries; they never edit or delete
  existing ones.
- **One file per channel / topic per source.** Don't write all of
  `hive/raw/discord/*.md` into a single file; split by channel so the
  file sizes stay manageable and agents can read just the channels they
  care about.
- **Format:** Every entry follows the "Raw capture" shape in
  [`../../templates/memory-entry.md`](../../templates/memory-entry.md).
- **Never touches agent silos.** Content here is strictly external.
  Agents synthesize from it into their own silos; the raw folder itself
  is never modified by agents.

## Example entry

```markdown
## [2026-04-23T14:32:11+00:00] #eng-team — @alice
**Message:** Reviewed the auth PR. LGTM modulo the rate-limit case.
**Attachments:** (none)
```

## This folder can be empty

If you don't run any ingester, `hive/raw/` stays empty. The rest of the
hive works identically — Tier 2 (agent synthesis) and Tier 3 (curator
distilled) don't depend on Tier 1.

## Setting up an ingester

Two reference implementations ship under
[`../../examples/ingesters/`](../../examples/ingesters/):

- `discord/` — polls Discord channels via the bot API
- `generic-webhook/` — accepts POST requests and writes them here

Copy one, adapt for your platform, run it alongside your hive.
