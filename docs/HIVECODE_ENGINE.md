# HiveCode Engine Specification

Status: loop-02 design freeze for the `feat/recall-engine-codes` branch.

HiveCode / HyperRecall is the built-in v1.1 recall index for Memory Hive. It must make per-turn Hive pulls fast and bounded without replacing the Markdown hive as source of truth.

## Design goals

1. **Lossless source, lossy acceleration.** Markdown files remain canonical. SQLite rows, sketches, token tables, and generated codes are disposable accelerators.
2. **Citation-first recall.** Every result cites `rel_path`, `start_line`, `end_line`, `start_byte`, and `end_byte`. A result without a verifiable span is invalid.
3. **Small relevant slices.** Query and bundle commands return ranked chunks under explicit budgets instead of dumping whole files.
4. **Local-first baseline.** The baseline uses Python stdlib and SQLite. FTS5 is used when available and gracefully disabled when unavailable.
5. **Deterministic codes.** Stable content and path metadata produce stable `hc:` codes. Content drift changes the check segment so stale citations are detectable.
6. **Install-story compatible.** The shell CLI can call a Python helper, but a fresh install must still work without network services or heavyweight dependencies.

## Chunk taxonomy

The chunker walks Markdown files and emits stable records in file order. Each chunk stores both line and UTF-8 byte spans.

| Chunk type | Boundary rule | Notes |
|---|---|---|
| `frontmatter` | Leading YAML block from first `---` through closing `---` only. | One chunk per file when present. |
| `heading` | A Markdown heading line (`#` through `######`) plus no body. | Updates the active `heading_path`. |
| `paragraph` | Consecutive non-blank prose lines under the same heading, excluding bullets and code fences. | Wrapped lines remain one paragraph chunk. |
| `bullet` | Consecutive list lines sharing indentation and marker family. Continuation lines stay attached. | Keeps operational notes compact. |
| `log_line` | A single line matching common dated-log forms, e.g. `YYYY-MM-DD — ...` or `YYYY-MM-DD - ...`. | Used heavily by agent silos. |
| `code_block` | Fenced block from opening fence through closing fence. | Preserves language tag in metadata when present. |
| `table` | Consecutive Markdown table lines. | Keeps roster/registry rows together. |
| `blockquote` | Consecutive `>` lines. | Rare but deterministic. |

Chunking rules:

- Blank lines separate paragraph-like chunks but are not emitted as chunks.
- A heading line always emits its own `heading` chunk and becomes context for following chunks.
- `heading_path` is a ` > ` joined list of active headings, normalized without leading `#` markers.
- Chunk ordinals are zero-based per file and assigned after chunk boundaries are finalized.
- `start_byte` is inclusive and `end_byte` is exclusive over UTF-8 bytes read from the exact source file.
- `text_sha256` hashes the exact chunk bytes, not normalized text.

## HiveCode grammar

Canonical display form:

```text
hc:v1:<tier><kind>:<agent>:<date>:<topic>:<sig>:<chk>
```

Example:

```text
hc:v1:lr:hermes:260505:recall-hive:9k3p7x2b:q4m1z8
```

Segments:

| Segment | Meaning | Source | Stability |
|---|---|---|---|
| `hc` | Literal namespace. | Constant. | Stable. |
| `v1` | Grammar version. | Constant until breaking change. | Stable. |
| `<tier><kind>` | Two-character source class: tier (`h` hive, `a` agent/silo, `l` learning, `k` knowledge, `t` task, `c` curator, `r` registry) + chunk kind (`f`, `h`, `p`, `b`, `l`, `x`, `t`, `q`). | Reversible through chunk/file metadata. | Stable if file class and chunk type stay stable. |
| `<agent>` | Sanitized agent id or `-` for non-agent files. | Path metadata. | Stable across content edits. |
| `<date>` | `YYMMDD` from frontmatter `date`, dated log line, filename date, then file mtime fallback. | Metadata extractor. | Prefer semantic dates; mtime fallback may drift. |
| `<topic>` | One to three normalized salient tokens joined by `-`, max 18 chars. | Tokenizer over heading + text + path. | Lossy hint; may change on major edits. |
| `<sig>` | Base32/base36 compact SimHash-like 48-64 bit sketch. | Normalized token multiset. | Similar chunks tend to have nearby Hamming distance. |
| `<chk>` | Short checksum from `rel_path`, span, and `text_sha256`. | Exact source pointer. | Changes when citation or content drifts. |

Collision behavior:

- `codes.code` is unique in the DB.
- If two chunks produce the same visible code, append a deterministic `~n` suffix in insertion order sorted by `(rel_path, ordinal)` and record `collision_group`.
- A `hc:` code lookup first resolves exact code; if `chk` mismatches current source, the result is returned as stale with rebuild guidance, not silently rewritten.

## SQLite schema

Default derived index path:

```text
hive/.hivecode/index.sqlite
```

Schema v1:

```sql
CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE files (
  id INTEGER PRIMARY KEY,
  rel_path TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,
  agent TEXT,
  size INTEGER NOT NULL,
  mtime_ns INTEGER NOT NULL,
  sha256 TEXT NOT NULL,
  indexed_at TEXT NOT NULL
);

CREATE TABLE chunks (
  id INTEGER PRIMARY KEY,
  file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
  ordinal INTEGER NOT NULL,
  chunk_type TEXT NOT NULL,
  heading_path TEXT NOT NULL DEFAULT '',
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL,
  start_byte INTEGER NOT NULL,
  end_byte INTEGER NOT NULL,
  text_sha256 TEXT NOT NULL,
  salience REAL NOT NULL DEFAULT 1.0,
  text TEXT NOT NULL,
  UNIQUE(file_id, ordinal)
);

CREATE TABLE codes (
  chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
  code TEXT NOT NULL UNIQUE,
  version TEXT NOT NULL,
  tier TEXT NOT NULL,
  kind_code TEXT NOT NULL,
  agent_code TEXT,
  date_code TEXT NOT NULL,
  topic_code TEXT NOT NULL,
  sig_code TEXT NOT NULL,
  chk_code TEXT NOT NULL,
  collision_group TEXT
);

CREATE TABLE tokens (
  chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  token TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 1.0,
  PRIMARY KEY(chunk_id, token)
);

CREATE TABLE sketches (
  chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
  simhash64 INTEGER NOT NULL,
  minhash_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE queries (
  id INTEGER PRIMARY KEY,
  prompt TEXT NOT NULL,
  created_at TEXT NOT NULL,
  parsed_json TEXT NOT NULL,
  max_results INTEGER,
  max_tokens INTEGER
);

CREATE TABLE access_log (
  id INTEGER PRIMARY KEY,
  query_id INTEGER REFERENCES queries(id) ON DELETE SET NULL,
  chunk_id INTEGER REFERENCES chunks(id) ON DELETE SET NULL,
  score REAL NOT NULL,
  reason TEXT NOT NULL,
  accessed_at TEXT NOT NULL
);
```

Indexes:

```sql
CREATE INDEX idx_files_kind_agent ON files(kind, agent);
CREATE INDEX idx_files_mtime ON files(mtime_ns);
CREATE INDEX idx_chunks_file_span ON chunks(file_id, start_line, end_line);
CREATE INDEX idx_tokens_token ON tokens(token);
CREATE INDEX idx_codes_code ON codes(code);
CREATE INDEX idx_sketches_simhash ON sketches(simhash64);
```

Optional FTS5 table when supported:

```sql
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  text,
  heading_path,
  rel_path,
  content='chunks',
  content_rowid='id'
);
```

Fallback when FTS5 is unavailable:

- Populate `tokens` and use SQLite `LIKE`/token joins for candidate generation.
- Report `fts5: unavailable` in `recall doctor` and `recall stats`.
- Keep output schema identical; only scores/reasons differ.

## Metadata classification

Path-derived `files.kind`:

| Path pattern | kind | agent |
|---|---|---|
| `index.md` | `index` | null |
| `agents/<id>/*.md` | `agent` | `<id>` |
| `learnings/raw/**.md` | `learning_raw` | from frontmatter `agent`, parent dir, or null |
| `learnings/distilled/**.md` | `learning_distilled` | null |
| `knowledge/**.md` | `knowledge` | null |
| `registry/**.md` | `registry` | null |
| `tasks/**.md` | `task` | null |
| `curator/**.md` | `curator` | null |
| other Markdown | `other` | null |

## Query planner

Input: prompt string plus optional filters.

Planner steps:

1. Parse explicit code hints with regex `hc:v[0-9]+:[A-Za-z0-9:_~.-]+`.
2. Extract date hints: ISO dates, `today`, `yesterday`, weekday names, and `last N days` where supplied by CLI flags.
3. Extract agent hints from `--for`, path-like mentions, and known `agents/<id>` roster names.
4. Extract kind hints from words such as `learning`, `distilled`, `task`, `registry`, `log`, `context`, `knowledge`.
5. Normalize lexical tokens: lowercase, ASCII fold where possible, split on non-alphanumerics, remove short/common stopwords, keep code-like tokens.
6. Candidate generation priority:
   - exact `hc:` code matches;
   - path/agent/date/kind filtered FTS5 BM25 candidates;
   - token-join fallback candidates;
   - recency/salience candidates when prompt is sparse.
7. Scoring combines:
   - lexical/BM25 score;
   - path/kind/agent/date match boosts;
   - SimHash relatedness to prompt tokens;
   - salience from chunk type and surface (`knowledge`/distilled > recent raw > logs > generic prose);
   - stale penalty when file hash/span checksum differs.
8. Deduplicate overlapping chunks by `(file_id, heading_path, text_sha256)` and near-duplicate sketch distance.
9. Return top chunks under `--limit` and/or `--max-tokens`.

Reason strings must be compact and auditable, e.g.:

```text
reason: bm25+agent:hermes+kind:agent+recent+sketch:0.78
```

## CLI UX

New command family:

```bash
memory-hive recall build [--hive DIR] [--db PATH] [--force] [--json]
memory-hive recall query --q TEXT [--for AGENT] [--kind KIND] [--since DATE|DURATION] [--limit N] [--json]
memory-hive recall bundle --for AGENT --q TEXT [--max-tokens N] [--json]
memory-hive recall doctor [--json]
memory-hive recall stats [--json]
```

Output defaults:

- Human output is Markdown with a compact header and one section per result.
- JSON output is line/stable-schema oriented for agents.
- `recall bundle` prints a prompt-ready Memory Hive pull with `HiveCode Recall Bundle`, query metadata, result headers, citations, and snippets.

Result shape:

```json
{
  "code": "hc:v1:...",
  "score": 0.91,
  "reason": "bm25+agent:hermes+recent",
  "citation": {
    "rel_path": "agents/hermes/log.md",
    "start_line": 76,
    "end_line": 76,
    "start_byte": 12001,
    "end_byte": 12144,
    "text_sha256": "..."
  },
  "heading_path": "Hermes — Log",
  "snippet": "2026-05-05 — Completed Memory Hive Recall Engine loop 01..."
}
```

Exit codes:

| Exit | Meaning |
|---:|---|
| 0 | Success, including zero-result query with valid JSON/human output. |
| 1 | Runtime/search failure. |
| 2 | Usage/configuration error. |
| 3 | Stale/corrupt index detected by `doctor`. |

## Bundle budget rules

- Default `--max-tokens` is 4000 for `recall bundle`.
- Token estimate uses `ceil(chars / 4)` unless a future tokenizer plug-in is configured.
- Header, query metadata, and citations are reserved first.
- Snippets are included in score order until budget is exhausted.
- If a result does not fit, include its compact header/code/citation and omit or truncate snippet with an explicit `truncated: true` marker.
- Summaries may be added later but must never be the only citation-bearing artifact.

## Security and no-secret handling

- Index build must not print raw file contents except as bounded snippets requested by query/bundle.
- Query/bundle should redact common secret shapes in snippets by default while preserving citations to the original source.
- The index may contain source text because it is stored under the local hive derived-artifact directory; docs and reports must not include live secrets.
- `recall doctor` should warn if index permissions are broader than the hive directory policy.

## Acceptance criteria for implementation loops

1. Chunker emits deterministic chunk order and exact line/byte spans for frontmatter, headings, bullets, paragraphs, log lines, tables, and fenced code.
2. Rebuilding an unchanged hive produces identical file hashes, chunk text hashes, and visible `hc:` codes.
3. Editing a chunk changes only affected file/chunk rows and the edited chunk's `chk` segment.
4. Querying by a unique phrase returns the matching chunk first with correct citation span.
5. Querying by `hc:` code resolves exact chunk or reports stale checksum status.
6. `recall bundle --max-tokens N` never exceeds budget by more than the documented estimator tolerance and preserves citation headers.
7. The system works with FTS5 enabled and with an induced no-FTS fallback path.
8. No-secret scan passes before push/PR/release.
