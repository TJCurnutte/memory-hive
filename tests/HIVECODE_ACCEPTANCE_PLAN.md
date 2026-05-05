# HiveCode Acceptance Test Plan

Status: loop-02 executable-test blueprint for loop 03.

Loop 03 should convert this plan into RED tests before production implementation. Suggested location: `tests/test_hivecode_*.py` using only Python stdlib (`unittest`, `tempfile`, `subprocess`, `sqlite3`, `json`, `pathlib`).

## Fixture shape

Create a temp Memory Hive root with:

```text
hive/
├── index.md
├── agents/hermes/log.md
├── agents/hermes/context.md
├── agents/hermes/memory.md
├── learnings/raw/hermes/2026-05-05-visible-pulls.md
├── learnings/distilled/patterns.md
├── knowledge/HUMAN_CONTEXT.md
├── registry/AGENTS.md
└── tasks/queue.md
```

Fixture content should include:

- YAML frontmatter in one raw learning.
- At least two dated log lines.
- A heading hierarchy.
- A paragraph wrapped across lines.
- A bullet list with continuation line.
- A Markdown table.
- A fenced code block containing token-like text.
- One fake secret-like value that must be redacted in output assertions, not committed as a real credential.

Use clearly fake placeholders such as `sk-test_FAKE_DO_NOT_USE_000000000000`.

## Test cases to add in loop 03

### Chunking and citations

1. `test_chunker_emits_frontmatter_with_exact_span`
   - Build fixture file with YAML frontmatter.
   - Assert first chunk type is `frontmatter`.
   - Assert line span covers only the frontmatter block.
   - Assert byte slice from original file equals chunk text bytes.

2. `test_chunker_tracks_heading_path_for_nested_content`
   - File has `# Root`, `## Child`, then paragraph.
   - Assert paragraph `heading_path == "Root > Child"`.

3. `test_chunker_groups_wrapped_paragraph_without_bullets`
   - Wrapped prose lines become one `paragraph` chunk.
   - Adjacent bullet lines become `bullet`, not paragraph.

4. `test_chunker_keeps_fenced_code_block_lossless`
   - Code block chunk starts at opening fence and ends at closing fence.
   - Byte span round-trips exactly.

5. `test_log_lines_emit_as_single_line_chunks`
   - Each `YYYY-MM-DD — ...` line in `agents/hermes/log.md` is a separate `log_line` chunk.

### Manifest and stable codes

6. `test_manifest_records_kind_agent_hash_size_mtime`
   - Build index over temp hive.
   - Assert `agents/hermes/log.md` has `kind='agent'`, `agent='hermes'`, `sha256`, `size`, `mtime_ns`.

7. `test_rebuild_unchanged_hive_preserves_codes`
   - Run build twice.
   - Assert sorted visible codes and chunk checksums are identical.

8. `test_editing_one_chunk_changes_only_affected_checksum`
   - Modify one log line.
   - Rebuild incrementally or force rebuild.
   - Assert unaffected chunks keep the same codes; edited chunk changes `chk`.

9. `test_code_grammar_matches_v1_segments`
   - Assert codes match `^hc:v1:[a-z0-9]{2}:[a-z0-9-]+|-:[0-9]{6}:[a-z0-9-]+:[a-z0-9]+:[a-z0-9]+(?:~[0-9]+)?$`.

### Query relevance and degraded fallback

10. `test_query_unique_phrase_returns_matching_chunk_first`
    - Query a unique phrase from `knowledge/HUMAN_CONTEXT.md`.
    - Assert first result citation path/line span points to that phrase.

11. `test_query_filters_agent_and_kind`
    - Query with `--for hermes`.
    - Assert returned agent-scoped chunks are boosted and non-agent chunks are lower or absent when limit is tight.

12. `test_query_by_hivecode_resolves_exact_chunk`
    - Build index, take one result code, query that code.
    - Assert exact chunk id/path/span returned.

13. `test_query_marks_stale_code_after_source_edit_without_rebuild`
    - Build index, edit source chunk without rebuild, query old code.
    - Assert stale/drift status rather than silent success.

14. `test_query_fallback_without_fts5_keeps_output_shape`
    - Force no-FTS mode via env or internal flag.
    - Assert JSON result schema matches FTS path and returns expected lexical match.

### Bundle budget and security

15. `test_bundle_respects_max_token_budget_with_citations`
    - Request `--max-tokens 400`.
    - Assert estimated token count <= 400.
    - Assert result headers include code + citation even if snippets are truncated.

16. `test_bundle_redacts_secret_like_snippets_but_keeps_citation`
    - Query phrase near fake secret.
    - Assert output contains `[REDACTED]` or equivalent.
    - Assert raw fake secret string is absent.
    - Assert citation path/span is still present.

17. `test_json_output_is_valid_and_stable_keys`
    - Run `recall query --json`.
    - Parse JSON.
    - Assert keys: `query`, `results`, `index`, and per-result `code`, `score`, `reason`, `citation`, `snippet`.

### CLI and doctor/stats

18. `test_recall_build_creates_sqlite_index_under_hivecode_dir`
    - Run `memory-hive recall build --hive <temp-hive>`.
    - Assert `hive/.hivecode/index.sqlite` exists and has schema version metadata.

19. `test_recall_doctor_reports_index_freshness_and_fts_status`
    - Run `memory-hive recall doctor --json`.
    - Assert `ok`, `schema_version`, `fts5`, `files_indexed`, and `stale_files` keys.

20. `test_recall_stats_reports_counts_without_scanning_full_output`
    - Run `memory-hive recall stats --json`.
    - Assert file/chunk/token/code counts and DB size are present.

## RED verification command for loop 03

After adding tests but before implementation, run:

```bash
python3 -m unittest discover -s tests -p 'test_hivecode*.py' -v
```

Expected loop-03 RED result: tests fail because `memory_hive_recall`/`hivecode` implementation and CLI subcommands do not exist yet. Failures should be assertion/import/usage failures tied to missing feature, not syntax errors in tests.

## GREEN target command for loops 04-06

```bash
python3 -m unittest discover -s tests -p 'test_hivecode*.py' -v
./check-compliance.sh
MEMORY_HIVE_DIR="$PWD" ./memory-hive recall doctor --json
```

## No-secret scan command before commit/PR

```bash
python3 - <<'PY'
from pathlib import Path
import re
patterns = [
    re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[A-Za-z0-9_./+=-]{12,}'),
    re.compile(r'sk-[A-Za-z0-9_-]{20,}'),
]
for p in Path('.').rglob('*'):
    if '.git' in p.parts or not p.is_file():
        continue
    try:
        text = p.read_text(errors='ignore')
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if 'FAKE_DO_NOT_USE' in line:
            continue
        if any(rx.search(line) for rx in patterns):
            print(f'{p}:{i}: possible secret')
PY
```
