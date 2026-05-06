# Generic webhook ingester

A minimal HTTP endpoint that accepts `POST`s and appends each body to
`hive/raw/<source>/<topic>.md`. Use it to capture context from anything
that can send an HTTP request — Zapier, Linear, GitHub webhooks, cron
jobs, internal tools, a `curl` from your editor.

## Run it

```bash
export MEMORY_HIVE_DIR=~/.memory-hive       # optional
export WEBHOOK_PORT=8787                     # optional, default 8787
export WEBHOOK_TOKEN=FAKE_DO_NOT_USE_WEBHOOK_TOKEN  # optional — required as ?token=... if set

python3 webhook_ingester.py
# [webhook] listening on http://127.0.0.1:8787  writing to ~/.memory-hive/hive/raw
```

## Send it something

```bash
curl -X POST http://127.0.0.1:8787/ -d '{
  "source":   "linear",
  "topic":    "team-alpha",
  "author":   "alice",
  "message":  "Closed LIN-273, rolled into next sprint",
  "attachments": ["https://linear.app/..."]
}'
```

Result:

```
~/.memory-hive/hive/raw/linear/team-alpha.md

## [2026-04-23T14:32:11+00:00] #team-alpha — @alice
**Message:** Closed LIN-273, rolled into next sprint
**Attachments:** https://linear.app/...
```

## Fields

| Field | Required | Default |
|---|---|---|
| `source` | yes | — |
| `topic` | yes | — |
| `message` | yes | — |
| `author` | no | `webhook` |
| `timestamp` | no | `now()` in UTC ISO-8601 |
| `attachments` | no | `[]` |

## Why this is tiny

Intentionally. Complex plumbing (auth, rate limiting, retries, signing)
belongs behind whatever proxy you put in front of this — nginx,
Cloudflare, a reverse tunnel with auth. This script's one job is:
accept a well-formed POST, write it to the right file, append-only.

## Security

- **Default bind is 127.0.0.1** — not reachable from outside the host.
- **`WEBHOOK_TOKEN` is optional** but strongly recommended if you front
  this with any public tunnel. Senders must include `?token=...`.
- The script never executes or evaluates request content. It's a
  file-appender.

## Adapting

Change `do_POST` for your platform's exact payload shape, or add more
routes (e.g. `/github`, `/linear`) that parse source-specific payloads
into the internal fields. The `append_entry` function is the only
Memory-Hive-aware line.
