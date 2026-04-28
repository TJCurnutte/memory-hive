# Memory Adapter Contract (v1)

This document defines a stable, boring interface for runtime adapters that
read and write Memory Hive data from outside the local CLI.

## Goals

- Keep integration behavior predictable across runtimes.
- Keep ingestion deterministic and auditable.
- Avoid secret leaks by default.
- Make dry-run/import behavior explicit before any overwrite.

## Record model

Every durable memory exchange uses the same core record shape:

```json
{
  "id": "2026-04-28-open-source-notes",
  "agent": "coder",
  "kind": "pattern",
  "title": "Confidence gate for multi-agent claims",
  "summary": "Short, 1-3 sentence pattern summary.",
  "state": "active",
  "confidence": "high",
  "created_at": "2026-04-28T10:20:00Z",
  "updated_at": "2026-04-28T10:20:00Z",
  "source": "agent:coder",
  "tags": ["memory-hive", "curation"],
  "links": [
    {"path": "hive/learnings/raw/coder/2026-04-28-confidence-gates.md"}
  ],
  "body": "full markdown body retained in source file"
}
```

Required fields: `id`, `agent`, `kind`, `title`, `summary`, `state`,
`confidence`, `created_at`, `updated_at`, `source`.

State is one of:

- `active` — current and preferred.
- `superseded` — replaced by a newer aligned record.
- `deprecated` — intentionally kept for audit but no longer used.

`links` is optional; if present, paths must be relative to `hive/`.

### Conflict and overwrite rules

- New records are initially `active`.
- When a newer record is accepted as authoritative, older `active` records for
  the same `id` or same canonical topic should become `superseded`.
- A curator action can only set `deprecated` when the evidence indicates that
  record is obsolete or wrong.
- Conflict detection is deterministic:
  by default, newer timestamp wins, then confidence, then stable ID tie-break.

The full source file for a decision remains the source of truth.
Curated summaries should never drop context needed to reproduce the outcome.

## Adapter methods

Adapters are plain executables or modules that implement these methods. They
may be implemented as one HTTP endpoint, one CLI subcommand family, or one
in-process runtime hook.

### `query(criteria)`

Return matching records.

- Input: `{ kind?, agent?, state?, min_confidence?, q?, limit?, after? }`
- Output: array of records + `next_cursor` when paginating.
- Must support deterministic ordering by relevance.

### `ingest(records)`

Persist one or more records.

- Input: array of records (see model above).
- Must validate required fields and reject malformed input with structured errors.
- Must support `dry_run` (no persistence, returns would-be actions).

### `snapshot(agent_id, options?)`

Return an operational "working context slice" for a single agent.

- Input: `{ agent_id, max_tokens?, max_items?, include_private? }`
- Output:
  - `agent_id`
  - canonical order by trust/rank:
    `index.md`/`registry` → `knowledge` → `distilled` → `agent log`/`context`
  - selected entries only, bounded to requested token budget
- Intended consumer output: `memory-hive bundle --for <agent>`

### `export(options?)` and `import(blob)`

- `export`: produce machine-readable or markdown bundle for backup/interop.
- `import`: apply an external bundle with explicit overwrite policy:
  `error` (default), `skip`, or `overwrite`.
- Both methods must support `dry_run` to reveal adds/updates/conflicts.

### `health()`

Return status + adapter capabilities:

- `ok`: boolean
- `version`: semver
- `capabilities`: method names implemented
- `environment`: detected paths / write permission

## Required environment contract

Only these environment keys are required across adapters:

- `MEMORY_HIVE_DIR` — path to hive root (`~/.memory-hive` default)
- `MEMORY_HIVE_DIR_READ_ONLY` — optional flag (`1`) for read-only adapters
- `MEMORY_HIVE_ADAPTER_VERSION` — optional, for analytics only

Recommended optional keys:

- `MEMORY_HIVE_CONFIDENCE` (`low|medium|high`) — default confidence floor
  for unconfirmed imports
- `MEMORY_HIVE_DRY_RUN` (`1`) — enforce dry-run mode by default
- `MEMORY_HIVE_OVERWRITE` (`error|skip|overwrite`) — default overwrite behavior
- `MEMORY_HIVE_MAX_TOKENS` — cap for `snapshot`/bundle outputs

## Security and secret handling

- **No-secrets-by-default posture (required):** memory data should not
  include raw credentials, private API keys, or tokens.
- If an adapter must ingest secret-bearing content, it must require explicit
  opt-in:
  `MEMORY_HIVE_ALLOW_SECRETS=1`.
- If secrets are present, redact or remove them before writing into
  `knowledge/` or `learnings/distilled/`.

## Error envelope

Adapters must return structured errors so orchestrators can fail safely:

- `code`: machine-readable symbol (for routing)
- `message`: short human message
- `details`: optional structured context

Example:

```json
{
  "ok": false,
  "code": "OVERRIDE_REJECTED",
  "message": "id exists and overwrite policy is error",
  "details": {
    "id": "coder-confidence-gates",
    "path": "hive/learnings/distilled/patterns.md"
  }
}
```

Success responses should include `ok`, `applied`, `skipped`, and `conflicts`
counts where applicable.

## Adapter compatibility levels

- **Level 1**: `query`, `ingest`, `snapshot`, `health`
- **Level 2**: Level 1 + `export`, `import`
- **Level 3**: Level 2 + `health` telemetry + override hooks

Memory Hive ships with file-backed CLI adapters, and runtime integrations should
implement at least **Level 1**.
