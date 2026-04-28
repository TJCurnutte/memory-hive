# Examples

Runnable reference implementations and reference content for Memory Hive
users. Nothing here is installed by default — `curl | sh` leaves
`examples/` alone. Copy what you want, adapt, run.

## What's here

### `ingesters/`

Reference implementations of the **Tier 1 raw-capture layer** (see
[HIVE_ARCHITECTURE.md](../HIVE_ARCHITECTURE.md#the-three-tier-memory-flow)).
Each ingester appends external context to `hive/raw/<source>/` using the
format in [`templates/memory-entry.md`](../templates/memory-entry.md).

- `discord/` — Poll Discord channels via the bot API. Append-only,
  resumable, zero deps.
- `generic-webhook/` — Minimal HTTP endpoint that accepts POST and
  writes the body to `hive/raw/<source>/<topic>.md`. Wire any system
  that can send HTTP (Zapier, Linear, GitHub webhooks, cron jobs) to
  it.

### `silo-mature/`

A reference populated silo showing what an agent's private memory looks
like after ~30 days of real use. Use it to understand the shape and
density of a mature silo — template files from a fresh install look
very different. Content is synthetic and generic; nothing personal.

### `hermes-crash-recovery/`

A local crash-recovery companion layout for Hermes-style daily-driver
agents. Use it as a machine-local safety net for interrupted sessions,
missing silos, and process recovery, then write durable lessons back to
Memory Hive at task end.

## Contributing more examples

Follow the existing shape:
1. One subdirectory per example, with its own README.
2. Document env vars up front, not buried.
3. Declare dependencies (or "stdlib only") at the top of the README.
4. Show both the command to run it and the file path it writes to.
