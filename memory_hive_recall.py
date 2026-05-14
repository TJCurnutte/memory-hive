"""Local-first HiveCode recall indexer for Memory Hive.

Python stdlib + SQLite only. Markdown files remain source of truth; the SQLite
index and visible HiveCodes are derived, rebuildable citation accelerators.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import time
from typing import Iterable

DATE_RE = re.compile(r"(20\d{2})[-/](\d{2})[-/](\d{2})")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
SECRET_RE = re.compile(r"sk-[A-Za-z0-9]{12,}|FAKE_DO_NOT_USE_[A-Za-z0-9_-]+|[A-Za-z0-9_-]{24,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{20,}")


@dataclass(frozen=True)
class Chunk:
    rel_path: str
    kind: str
    text: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    heading_path: str = ""
    code: str = ""
    chunk_id: int = 0

    @property
    def source_key(self) -> str:
        return f"{self.rel_path}:{self.kind}:{self.start_line}-{self.end_line}"


@dataclass(frozen=True)
class FileRecord:
    rel_path: str
    kind: str
    agent: str
    sha256: str
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class CodeRecord:
    code: str
    source_key: str
    rel_path: str
    start_line: int
    end_line: int
    checksum: str


@dataclass(frozen=True)
class BuildResult:
    hive_root: Path
    db_path: Path
    files: dict[str, FileRecord]
    chunks: list[Chunk]
    codes: list[CodeRecord]

    @property
    def visible_codes(self) -> list[str]:
        return [record.code for record in self.codes]

    @property
    def chunk_hashes(self) -> dict[str, str]:
        return {record.source_key: record.checksum for record in self.codes}


@dataclass(frozen=True)
class DriftResult:
    changed_chunks: int
    unchanged_chunks: int


@dataclass(frozen=True)
class IndexStatus:
    schema_version: str
    file_count: int
    chunk_count: int
    code_count: int
    fts5: str
    db_bytes: int


@dataclass(frozen=True)
class Citation:
    rel_path: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    agent: str
    kind: str


@dataclass(frozen=True)
class QueryResult:
    chunk_id: int
    code: str
    score: float
    reason: str
    citation: Citation
    snippet: str


@dataclass(frozen=True)
class ResolveResult:
    chunk_id: int
    code: str
    citation: Citation
    text: str
    status: str
    guidance: str
    stale: bool


@dataclass(frozen=True)
class BundleResult:
    text: str
    estimated_tokens: int
    results: list[QueryResult]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _base36_from_hex(hex_text: str, length: int = 6) -> str:
    n = int(hex_text[:16], 16)
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while n:
        n, rem = divmod(n, 36)
        out = alphabet[rem] + out
    return (out or "0")[-length:].rjust(length, "0")


def _line_offsets(raw: bytes) -> list[int]:
    offsets = [0]
    for i, b in enumerate(raw):
        if b == 10:
            offsets.append(i + 1)
    return offsets


def _span(offsets: list[int], raw_len: int, start_line: int, end_line: int) -> tuple[int, int]:
    start = offsets[start_line - 1]
    end = offsets[end_line] if end_line < len(offsets) else raw_len
    return start, end


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def classify_file(rel_path: str) -> tuple[str, str]:
    parts = rel_path.split("/")
    if parts[:1] == ["agents"] and len(parts) >= 3:
        return "agent", parts[1]
    if parts[:2] == ["learnings", "raw"] and len(parts) >= 4:
        return "learning", parts[2]
    if parts[:2] == ["learnings", "distilled"]:
        return "distilled", "-"
    if parts[:1] == ["knowledge"]:
        return "knowledge", "-"
    if parts[:1] == ["registry"]:
        return "registry", "-"
    if parts[:1] == ["tasks"]:
        return "task", "-"
    if rel_path == "index.md":
        return "index", "-"
    return "other", "-"


def _heading_path(levels: dict[int, str]) -> str:
    return " > ".join(levels[i] for i in sorted(levels) if levels[i])


def _is_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}\s+", line))


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^\s*([-*+] |\d+\. )", line))


def _is_log_line(line: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}\s+[—-]\s+", line))


def _emit(rel_path: str, kind: str, text_lines: list[str], start_line: int, end_line: int, offsets: list[int], raw_len: int, heading: str) -> Chunk:
    start_byte, end_byte = _span(offsets, raw_len, start_line, end_line)
    return Chunk(rel_path, kind, "".join(text_lines), start_line, end_line, start_byte, end_byte, heading)


def chunk_file(path: Path, *, hive_root: Path | None = None) -> list[Chunk]:
    hive_root = hive_root or path.parent
    rel_path = _rel(path, hive_root)
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    offsets = _line_offsets(raw)
    chunks: list[Chunk] = []
    headings: dict[int, str] = {}
    i = 0

    if lines and lines[0].strip() == "---":
        j = 1
        while j < len(lines) and lines[j].strip() != "---":
            j += 1
        if j < len(lines):
            end = j + 1
            chunks.append(_emit(rel_path, "frontmatter", lines[0:end], 1, end, offsets, len(raw), ""))
            i = end

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        line_no = i + 1
        if not stripped:
            i += 1
            continue
        if _is_heading(line):
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line.rstrip("\n"))
            level = len(m.group(1)) if m else 1
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = (m.group(2).strip() if m else stripped.lstrip("# "))
            chunks.append(_emit(rel_path, "heading_section", [line], line_no, line_no, offsets, len(raw), _heading_path(headings)))
            i += 1
            continue
        if line.startswith("```"):
            start = i
            i += 1
            while i < len(lines):
                if lines[i].startswith("```"):
                    i += 1
                    break
                i += 1
            chunks.append(_emit(rel_path, "code_block", lines[start:i], start + 1, i, offsets, len(raw), _heading_path(headings)))
            continue
        if _is_log_line(line):
            chunks.append(_emit(rel_path, "log_line", [line], line_no, line_no, offsets, len(raw), _heading_path(headings)))
            i += 1
            continue
        if _is_bullet(line):
            start = i
            i += 1
            while i < len(lines) and lines[i].strip() and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                i += 1
            chunks.append(_emit(rel_path, "bullet", lines[start:i], start + 1, i, offsets, len(raw), _heading_path(headings)))
            continue
        if line.lstrip().startswith("|"):
            start = i
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                i += 1
            chunks.append(_emit(rel_path, "table", lines[start:i], start + 1, i, offsets, len(raw), _heading_path(headings)))
            continue
        start = i
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if not nxt.strip() or _is_heading(nxt) or nxt.startswith("```") or _is_bullet(nxt) or _is_log_line(nxt) or nxt.lstrip().startswith("|"):
                break
            i += 1
        chunks.append(_emit(rel_path, "paragraph", lines[start:i], start + 1, i, offsets, len(raw), _heading_path(headings)))
    return chunks


def _date_code(rel_path: str, text: str) -> str:
    m = DATE_RE.search(rel_path) or DATE_RE.search(text)
    return f"{m.group(1)[2:]}{m.group(2)}{m.group(3)}" if m else "000000"


def _topic_code(text: str, heading_path: str) -> str:
    words = [w.lower().strip("_-") for w in WORD_RE.findall((heading_path + " " + text).lower())]
    stop = {"the", "and", "for", "with", "this", "that", "must", "should", "source", "line", "lines"}
    words = [w for w in words if w not in stop]
    return ("-".join(words[:2])[:18].strip("-") or "ctx") if words else "ctx"


def _kind_code(kind: str) -> str:
    return {
        "frontmatter": "0f", "heading_section": "0h", "bullet": "0b",
        "log_line": "0l", "paragraph": "0p", "code_block": "0c", "table": "0t",
    }.get(kind, "0x")


def make_code(chunk: Chunk, agent: str, used: dict[str, int] | None = None) -> str:
    text_hash = _sha256(chunk.text.encode("utf-8"))
    sig = _base36_from_hex(_sha256((chunk.rel_path + "\n" + chunk.heading_path + "\n" + chunk.text.lower()).encode("utf-8")), 7)
    base = ":".join(["hc", "v1", _kind_code(chunk.kind), agent or "-", _date_code(chunk.rel_path, chunk.text), _topic_code(chunk.text, chunk.heading_path), sig, text_hash[:8]])
    if used is None:
        return base
    n = used.get(base, 0)
    used[base] = n + 1
    return base if n == 0 else f"{base}~{n+1}"


def iter_markdown_files(hive_root: Path) -> Iterable[Path]:
    skip = {".git", ".hivecode", "node_modules", "__pycache__"}
    for path in sorted(hive_root.rglob("*.md")):
        if not any(part in skip for part in path.parts):
            yield path


def _db_path(hive_root: Path) -> Path:
    return hive_root / ".hivecode" / "index.sqlite"


def _init_db(con: sqlite3.Connection) -> str:
    con.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
    PRAGMA temp_store=MEMORY;
    PRAGMA mmap_size=268435456;
    DROP TABLE IF EXISTS chunks_fts;
    DROP TABLE IF EXISTS skill_fts;
    DROP TABLE IF EXISTS files;
    DROP TABLE IF EXISTS chunks;
    DROP TABLE IF EXISTS codes;
    DROP TABLE IF EXISTS tokens;
    DROP TABLE IF EXISTS sketches;
    DROP TABLE IF EXISTS skills;
    DROP TABLE IF EXISTS bundle_cache;
    DROP TABLE IF EXISTS access_log;
    DROP TABLE IF EXISTS meta;
    CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE files (id INTEGER PRIMARY KEY, rel_path TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, agent TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL, indexed_at INTEGER NOT NULL);
    CREATE TABLE chunks (id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL, ordinal INTEGER NOT NULL, chunk_type TEXT NOT NULL, heading_path TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, start_byte INTEGER NOT NULL, end_byte INTEGER NOT NULL, text_sha256 TEXT NOT NULL, text TEXT NOT NULL, source_key TEXT NOT NULL, FOREIGN KEY(file_id) REFERENCES files(id));
    CREATE TABLE codes (chunk_id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, checksum TEXT NOT NULL, FOREIGN KEY(chunk_id) REFERENCES chunks(id));
    CREATE TABLE tokens (chunk_id INTEGER NOT NULL, token TEXT NOT NULL, weight REAL NOT NULL);
    CREATE TABLE sketches (chunk_id INTEGER PRIMARY KEY, simhash64 TEXT NOT NULL);
    CREATE TABLE skills (id INTEGER PRIMARY KEY, name TEXT NOT NULL, rel_path TEXT NOT NULL, description TEXT NOT NULL, tags TEXT NOT NULL, text TEXT NOT NULL, sha256 TEXT NOT NULL);
    CREATE TABLE bundle_cache (cache_key TEXT PRIMARY KEY, created_at TEXT NOT NULL, source_fingerprint TEXT NOT NULL, query TEXT NOT NULL, agent TEXT, max_tokens INTEGER NOT NULL, payload_json TEXT NOT NULL);
    CREATE TABLE access_log (ts TEXT NOT NULL, query_hash TEXT NOT NULL, chunk_id INTEGER NOT NULL, action TEXT NOT NULL, agent TEXT, task_kind TEXT);
    CREATE INDEX idx_files_rel_path ON files(rel_path);
    CREATE INDEX idx_files_hash ON files(sha256);
    CREATE INDEX idx_chunks_file ON chunks(file_id);
    CREATE INDEX idx_codes_code ON codes(code);
    CREATE INDEX idx_tokens_token ON tokens(token);
    CREATE INDEX idx_tokens_chunk ON tokens(chunk_id);
    """)
    try:
        con.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(text, heading_path, rel_path)")
        con.execute("CREATE VIRTUAL TABLE skill_fts USING fts5(name, description, tags, text, rel_path)")
        return "available"
    except sqlite3.OperationalError:
        return "unavailable"


def _index_markdown_file(
    con: sqlite3.Connection,
    root: Path,
    path: Path,
    *,
    used_codes: dict[str, int],
    fts5: str,
    indexed_at: int,
    data: bytes | None = None,
) -> tuple[FileRecord, list[Chunk], list[CodeRecord]]:
    rel_path = _rel(path, root)
    data = path.read_bytes() if data is None else data
    stat = path.stat()
    kind, agent = classify_file(rel_path)
    record = FileRecord(rel_path, kind, agent, _sha256(data), len(data), int(stat.st_mtime_ns))
    cur = con.execute(
        "INSERT INTO files(rel_path, kind, agent, sha256, size, mtime_ns, indexed_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
        (record.rel_path, record.kind, record.agent, record.sha256, record.size, record.mtime_ns, indexed_at),
    )
    file_id_raw = cur.lastrowid
    if file_id_raw is None:
        raise RuntimeError(f"failed to index file: {rel_path}")
    file_id = int(file_id_raw)
    chunks: list[Chunk] = []
    codes: list[CodeRecord] = []
    for ordinal, chunk in enumerate(chunk_file(path, hive_root=root), start=1):
        code = make_code(chunk, agent, used_codes)
        checksum = _sha256(chunk.text.encode("utf-8"))
        ccur = con.execute(
            """INSERT INTO chunks(file_id, ordinal, chunk_type, heading_path, start_line, end_line, start_byte, end_byte, text_sha256, text, source_key) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (file_id, ordinal, chunk.kind, chunk.heading_path, chunk.start_line, chunk.end_line, chunk.start_byte, chunk.end_byte, checksum, chunk.text, chunk.source_key),
        )
        chunk_id_raw = ccur.lastrowid
        if chunk_id_raw is None:
            raise RuntimeError(f"failed to index chunk in {rel_path}:{chunk.start_line}-{chunk.end_line}")
        chunk_id = int(chunk_id_raw)
        chunk_with_code = Chunk(**{**asdict(chunk), "code": code, "chunk_id": chunk_id})
        chunks.append(chunk_with_code)
        con.execute("INSERT INTO codes(chunk_id, code, checksum) VALUES(?, ?, ?)", (chunk_id, code, checksum))
        if fts5 == "available":
            con.execute("INSERT INTO chunks_fts(rowid, text, heading_path, rel_path) VALUES(?, ?, ?, ?)", (chunk_id, chunk.text, chunk.heading_path, rel_path))
        for token in sorted(set(w.lower() for w in WORD_RE.findall(chunk.text))):
            con.execute("INSERT INTO tokens(chunk_id, token, weight) VALUES(?, ?, ?)", (chunk_id, token, 1.0))
        con.execute("INSERT INTO sketches(chunk_id, simhash64) VALUES(?, ?)", (chunk_id, _sha256(chunk.text.lower().encode("utf-8"))[:16]))
        codes.append(CodeRecord(code, chunk.source_key, rel_path, chunk.start_line, chunk.end_line, checksum))
    return record, chunks, codes


def _code_base_and_count(code: str) -> tuple[str, int]:
    base, sep, suffix = code.rpartition("~")
    if sep and suffix.isdigit():
        return base, int(suffix)
    return code, 1


def _load_used_codes(con: sqlite3.Connection) -> dict[str, int]:
    used: dict[str, int] = {}
    for row in con.execute("SELECT code FROM codes"):
        base, count = _code_base_and_count(row[0])
        used[base] = max(used.get(base, 0), count)
    return used


def _delete_indexed_file(con: sqlite3.Connection, rel_path: str) -> int:
    row = con.execute("SELECT id FROM files WHERE rel_path=?", (rel_path,)).fetchone()
    if row is None:
        return 0
    file_id = int(row[0])
    chunk_ids = [int(r[0]) for r in con.execute("SELECT id FROM chunks WHERE file_id=?", (file_id,))]
    for chunk_id in chunk_ids:
        try:
            con.execute("DELETE FROM chunks_fts WHERE rowid=?", (chunk_id,))
        except sqlite3.OperationalError:
            pass
        con.execute("DELETE FROM tokens WHERE chunk_id=?", (chunk_id,))
        con.execute("DELETE FROM sketches WHERE chunk_id=?", (chunk_id,))
        con.execute("DELETE FROM codes WHERE chunk_id=?", (chunk_id,))
    con.execute("DELETE FROM chunks WHERE file_id=?", (file_id,))
    con.execute("DELETE FROM files WHERE id=?", (file_id,))
    return len(chunk_ids)


def build_index(hive_root: str | os.PathLike[str], *, force: bool = False, incremental: bool = False) -> BuildResult:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    files: dict[str, FileRecord] = {}
    chunks: list[Chunk] = []
    codes: list[CodeRecord] = []
    used_codes: dict[str, int] = {}
    with sqlite3.connect(str(db_path)) as con:
        fts5 = _init_db(con)
        con.execute("INSERT INTO meta(key, value) VALUES('schema_version', '1')")
        con.execute("INSERT INTO meta(key, value) VALUES('fts5', ?)", (fts5,))
        now = int(time.time())
        for path in iter_markdown_files(root):
            record, file_chunks, file_codes = _index_markdown_file(con, root, path, used_codes=used_codes, fts5=fts5, indexed_at=now)
            files[record.rel_path] = record
            chunks.extend(file_chunks)
            codes.extend(file_codes)
        con.commit()
    return BuildResult(root, db_path, files, chunks, codes)


def compare_code_sets(before: list[str], after: list[str]) -> DriftResult:
    before_set, after_set = set(before), set(after)
    return DriftResult(len(before_set.symmetric_difference(after_set)), len(before_set & after_set))


def _connect_existing(hive_root: str | os.PathLike[str]) -> sqlite3.Connection:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    if not db_path.exists():
        raise FileNotFoundError(f"HiveCode index missing at {db_path}; run recall build first")
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def index_status(hive_root: str | os.PathLike[str]) -> IndexStatus:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    with _connect_existing(root) as con:
        def scalar(sql: str, default=0):
            row = con.execute(sql).fetchone()
            return row[0] if row and row[0] is not None else default
        return IndexStatus(
            schema_version=str(scalar("SELECT value FROM meta WHERE key='schema_version'", "")),
            file_count=int(scalar("SELECT count(*) FROM files")),
            chunk_count=int(scalar("SELECT count(*) FROM chunks")),
            code_count=int(scalar("SELECT count(*) FROM codes")),
            fts5=str(scalar("SELECT value FROM meta WHERE key='fts5'", "unavailable")),
            db_bytes=db_path.stat().st_size,
        )


def get_file_record(hive_root: str | os.PathLike[str], rel_path: str) -> FileRecord:
    with _connect_existing(hive_root) as con:
        row = con.execute("SELECT rel_path, kind, agent, sha256, size, mtime_ns FROM files WHERE rel_path = ?", (rel_path,)).fetchone()
    if row is None:
        raise KeyError(rel_path)
    return FileRecord(row["rel_path"], row["kind"], row["agent"], row["sha256"], int(row["size"]), int(row["mtime_ns"]))


def stats(hive_root: str | os.PathLike[str]) -> dict[str, int]:
    status = index_status(hive_root)
    with _connect_existing(hive_root) as con:
        token_count = int(con.execute("SELECT count(*) FROM tokens").fetchone()[0])
    return {"files": status.file_count, "chunks": status.chunk_count, "tokens": token_count, "codes": status.code_count, "db_bytes": status.db_bytes}


def _indexed_file_rows(hive_root: str | os.PathLike[str]) -> list[sqlite3.Row]:
    with _connect_existing(hive_root) as con:
        return con.execute("SELECT rel_path, sha256, size, mtime_ns FROM files ORDER BY rel_path").fetchall()


def source_fingerprint(hive_root: str | os.PathLike[str]) -> str:
    parts = []
    for row in _indexed_file_rows(hive_root):
        parts.append(f"{row['rel_path']}:{row['sha256']}:{row['size']}:{row['mtime_ns']}")
    return _sha256("\n".join(parts).encode("utf-8"))


def doctor(hive_root: str | os.PathLike[str]) -> dict[str, object]:
    root = Path(hive_root).resolve()
    status = index_status(root)
    stale: list[str] = []
    missing: list[str] = []
    for row in _indexed_file_rows(root):
        path = root / row["rel_path"]
        if not path.exists():
            stale.append(row["rel_path"])
            missing.append(row["rel_path"])
            continue
        data = path.read_bytes()
        if _sha256(data) != row["sha256"] or path.stat().st_mtime_ns != int(row["mtime_ns"]):
            stale.append(row["rel_path"])
    return {"ok": len(stale) == 0, "schema_version": status.schema_version, "fts5": status.fts5 == "available", "files_indexed": status.file_count, "stale_files": stale, "missing_files": missing, "source_fingerprint": source_fingerprint(root)}


def update_index(hive_root: str | os.PathLike[str]) -> dict[str, int | str]:
    root = Path(hive_root).resolve()
    existing = {row["rel_path"]: row for row in _indexed_file_rows(root)}
    current_paths: set[str] = set()
    changed_files: list[tuple[Path, bytes]] = []
    skipped = 0
    touched_same_content = 0

    for path in iter_markdown_files(root):
        rel_path = _rel(path, root)
        current_paths.add(rel_path)
        st = path.stat()
        row = existing.get(rel_path)
        size = int(st.st_size)
        mtime_ns = int(st.st_mtime_ns)
        if row and int(row["size"]) == size and int(row["mtime_ns"]) == mtime_ns:
            skipped += 1
            continue
        data = path.read_bytes()
        sha = _sha256(data)
        if row and row["sha256"] == sha and int(row["size"]) == size:
            touched_same_content += 1
            skipped += 1
            with _connect_existing(root) as con:
                con.execute("UPDATE files SET mtime_ns=?, indexed_at=? WHERE rel_path=?", (mtime_ns, int(time.time()), rel_path))
                con.commit()
            continue
        changed_files.append((path, data))

    deleted_paths = sorted(set(existing) - current_paths)
    if changed_files or deleted_paths:
        with _connect_existing(root) as con:
            fts_row = con.execute("SELECT value FROM meta WHERE key='fts5'").fetchone()
            fts5 = str(fts_row[0]) if fts_row else "unavailable"
            for rel_path in sorted([_rel(path, root) for path, _ in changed_files] + deleted_paths):
                _delete_indexed_file(con, rel_path)
            used_codes = _load_used_codes(con)
            now = int(time.time())
            for path, data in sorted(changed_files, key=lambda item: _rel(item[0], root)):
                _index_markdown_file(con, root, path, used_codes=used_codes, fts5=fts5, indexed_at=now, data=data)
            con.commit()

    return {
        "ok": 1,
        "changed_files": len(changed_files),
        "skipped_files": skipped,
        "deleted_files": len(deleted_paths),
        "touched_same_content": touched_same_content,
        "source_fingerprint": source_fingerprint(root),
    }


def gc_index(hive_root: str | os.PathLike[str]) -> dict[str, int]:
    root = Path(hive_root).resolve()
    stale = doctor(root)["stale_files"]
    removed = 0
    if stale:
        removed = len(stale)
        build_index(root, force=True)
    return {"removed_files": removed}


def _citation(row: sqlite3.Row) -> Citation:
    return Citation(row["rel_path"], int(row["start_line"]), int(row["end_line"]), int(row["start_byte"]), int(row["end_byte"]), row["agent"], row["kind"])


def _score(text: str, heading: str, rel_path: str, q_terms: list[str]) -> float:
    hay = (text + " " + heading + " " + rel_path).lower()
    if not q_terms:
        return 0.0
    exact = " ".join(q_terms)
    score = 10.0 if exact and exact in hay else 0.0
    for term in q_terms:
        score += hay.count(term) * 3.0
    return score


def _fts_query_text(text: str) -> str:
    terms = [w.lower() for w in WORD_RE.findall(text)]
    # Quote tokens so hyphenated user phrases split into safe FTS terms instead
    # of being parsed as column/filter syntax.
    return " OR ".join(f'"{t}"' for t in terms) if terms else text.replace('"', ' ')


def _query_rows(hive_root: str | os.PathLike[str], text: str, *, limit: int, for_agent: str | None = None, use_fts: bool = True) -> list[sqlite3.Row]:
    terms = [w.lower() for w in WORD_RE.findall(text)]
    with _connect_existing(hive_root) as con:
        status = str(con.execute("SELECT value FROM meta WHERE key='fts5'").fetchone()[0])
        if use_fts and status == "available" and terms:
            sql = """SELECT ch.id AS chunk_id, co.code, ch.text, ch.heading_path, ch.start_line, ch.end_line, ch.start_byte, ch.end_byte, f.rel_path, f.kind, f.agent, bm25(chunks_fts) AS bm25_score
                     FROM chunks_fts
                     JOIN chunks ch ON ch.id = chunks_fts.rowid
                     JOIN files f ON f.id=ch.file_id
                     JOIN codes co ON co.chunk_id=ch.id
                     WHERE chunks_fts MATCH ?"""
            params: list[object] = [_fts_query_text(text)]
            if for_agent:
                sql += " AND f.agent = ?"
                params.append(for_agent)
            sql += " ORDER BY bm25_score ASC, f.rel_path ASC, ch.start_line ASC LIMIT ?"
            params.append(limit)
            rows = con.execute(sql, params).fetchall()
            if rows:
                return rows
        sql = """SELECT ch.id AS chunk_id, co.code, ch.text, ch.heading_path, ch.start_line, ch.end_line, ch.start_byte, ch.end_byte, f.rel_path, f.kind, f.agent
                 FROM chunks ch JOIN files f ON f.id=ch.file_id JOIN codes co ON co.chunk_id=ch.id"""
        params = []
        if for_agent:
            sql += " WHERE f.agent = ?"
            params.append(for_agent)
        rows = con.execute(sql, params).fetchall()
    ranked = []
    for row in rows:
        score = _score(row["text"], row["heading_path"], row["rel_path"], terms)
        if score > 0:
            ranked.append((score, row))
    ranked.sort(key=lambda x: (-x[0], x[1]["rel_path"], x[1]["start_line"]))
    return [r for _, r in ranked[:limit]]


def _redact(text: str) -> str:
    return SECRET_RE.sub("[REDACTED]", text)


def _backend_status(hive_root: str | os.PathLike[str], use_fts: bool = True) -> tuple[str, str]:
    status = index_status(hive_root)
    if not use_fts:
        return "lexical", "forced"
    if status.fts5 == "available":
        return "fts5", "none"
    return "lexical", "fts5-unavailable"


def query(hive_root: str | os.PathLike[str], text: str, *, limit: int = 5, for_agent: str | None = None, use_fts: bool = True) -> list[QueryResult]:
    rows = _query_rows(hive_root, text, limit=limit, for_agent=for_agent, use_fts=use_fts)
    terms = [w.lower() for w in WORD_RE.findall(text)]
    backend, _ = _backend_status(hive_root, use_fts=use_fts)
    reason = "fts5-term-match" if backend == "fts5" else "lexical-term-match"
    out: list[QueryResult] = []
    for row in rows:
        score = _score(row["text"], row["heading_path"], row["rel_path"], terms)
        out.append(QueryResult(int(row["chunk_id"]), row["code"], score, reason, _citation(row), _redact(row["text"])))
    return out


def resolve_code(hive_root: str | os.PathLike[str], code: str) -> ResolveResult:
    with _connect_existing(hive_root) as con:
        row = con.execute("""SELECT ch.id AS chunk_id, co.code, co.checksum, ch.text, ch.start_line, ch.end_line, ch.start_byte, ch.end_byte, f.rel_path, f.kind, f.agent
                             FROM codes co JOIN chunks ch ON ch.id=co.chunk_id JOIN files f ON f.id=ch.file_id WHERE co.code=?""", (code,)).fetchone()
    if row is None:
        raise KeyError(code)
    path = Path(hive_root).resolve() / row["rel_path"]
    current = path.read_bytes()[int(row["start_byte"]):int(row["end_byte"])]
    stale = _sha256(current) != row["checksum"]
    return ResolveResult(int(row["chunk_id"]), code, _citation(row), _redact(current.decode("utf-8", errors="replace")), "STALE" if stale else "OK", "Rebuild the HiveCode index before using this citation." if stale else "Citation is current.", stale)


def query_json(hive_root: str | os.PathLike[str], text: str, *, limit: int = 5, for_agent: str | None = None, use_fts: bool = True) -> dict[str, object]:
    backend, fallback = _backend_status(hive_root, use_fts=use_fts)
    return {
        "query": text,
        "backend": backend,
        "fallback": fallback,
        "index": asdict(index_status(hive_root)),
        "results": [
            {"code": r.code, "score": r.score, "reason": r.reason, "citation": asdict(r.citation), "snippet": r.snippet}
            for r in query(hive_root, text, limit=limit, for_agent=for_agent, use_fts=use_fts)
        ],
    }


def _estimated_tokens(text: str) -> int:
    return int(math.ceil(len(text) / 4))


def bundle(hive_root: str | os.PathLike[str], text: str, *, max_tokens: int = 1200, for_agent: str | None = None) -> BundleResult:
    results = query(hive_root, text, limit=20, for_agent=for_agent)
    lines = [f"HiveCode Recall Bundle: {text}"]
    kept: list[QueryResult] = []
    for r in results:
        entry = f"\n[{r.code}] {r.citation.rel_path}:{r.citation.start_line}-{r.citation.end_line}\n{r.snippet.strip()}\n"
        candidate = "\n".join(lines) + entry
        if _estimated_tokens(candidate) <= max_tokens:
            lines.append(entry.strip())
            kept.append(r)
        elif not kept:
            budget_chars = max(0, max_tokens * 4 - len("\n".join(lines)) - 120)
            clipped = entry[:budget_chars].rstrip()
            lines.append(clipped)
            kept.append(r)
            break
    out = "\n".join(lines)
    return BundleResult(out, _estimated_tokens(out), kept)


def bundle_json(hive_root: str | os.PathLike[str], text: str, *, max_tokens: int = 1200, for_agent: str | None = None, cache: bool = False) -> dict[str, object]:
    root = Path(hive_root).resolve()
    fp = source_fingerprint(root)
    cache_key = _sha256(f"{text}\0{for_agent or ''}\0{max_tokens}\0{fp}".encode("utf-8"))
    if cache:
        with _connect_existing(root) as con:
            row = con.execute("SELECT payload_json FROM bundle_cache WHERE cache_key=? AND source_fingerprint=?", (cache_key, fp)).fetchone()
            if row:
                payload = json.loads(row["payload_json"])
                payload["cache_hit"] = True
                return payload
    built = bundle(root, text, max_tokens=max_tokens, for_agent=for_agent)
    payload = {
        "query": text,
        "estimated_tokens": built.estimated_tokens,
        "max_tokens": max_tokens,
        "source_fingerprint": fp,
        "cache_hit": False,
        "text": built.text,
        "results": [
            {"code": r.code, "score": r.score, "reason": r.reason, "citation": asdict(r.citation), "snippet": r.snippet}
            for r in built.results
        ],
    }
    if cache:
        with _connect_existing(root) as con:
            con.execute("INSERT OR REPLACE INTO bundle_cache(cache_key, created_at, source_fingerprint, query, agent, max_tokens, payload_json) VALUES(?, ?, ?, ?, ?, ?, ?)", (cache_key, datetime.now(timezone.utc).isoformat(), fp, text, for_agent, max_tokens, json.dumps(payload, sort_keys=True)))
            con.commit()
    return payload




def _parse_skill_frontmatter(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
    return meta


def build_skill_index(hive_root: str | os.PathLike[str], *, skills_root: str | os.PathLike[str] | None = None) -> dict[str, int]:
    root = Path(hive_root).resolve()
    skills = Path(skills_root or os.environ.get("HERMES_SKILLS_DIR") or (Path.home() / ".hermes" / "skills")).resolve()
    with _connect_existing(root) as con:
        con.execute("DELETE FROM skills")
        try:
            con.execute("DELETE FROM skill_fts")
        except sqlite3.OperationalError:
            pass
        count = 0
        if skills.exists():
            for path in sorted(skills.rglob("SKILL.md")):
                text = path.read_text(encoding="utf-8")
                meta = _parse_skill_frontmatter(text)
                name = meta.get("name") or path.parent.name
                desc = meta.get("description", "")
                tags = meta.get("tags", "")
                rel = path.relative_to(skills).as_posix()
                sha = _sha256(text.encode("utf-8"))
                cur = con.execute("INSERT INTO skills(name, rel_path, description, tags, text, sha256) VALUES(?, ?, ?, ?, ?, ?)", (name, rel, desc, tags, text, sha))
                try:
                    con.execute("INSERT INTO skill_fts(rowid, name, description, tags, text, rel_path) VALUES(?, ?, ?, ?, ?, ?)", (int(cur.lastrowid), name, desc, tags, text, rel))
                except sqlite3.OperationalError:
                    pass
                count += 1
        con.commit()
    return {"skills": count}


def query_skills(hive_root: str | os.PathLike[str], text: str, *, limit: int = 5) -> list[dict[str, object]]:
    terms = [w.lower() for w in WORD_RE.findall(text)]
    with _connect_existing(hive_root) as con:
        rows = []
        try:
            rows = con.execute("""SELECT s.name, s.rel_path, s.description, s.tags, s.text, bm25(skill_fts) AS bm25_score
                                  FROM skill_fts JOIN skills s ON s.id=skill_fts.rowid
                                  WHERE skill_fts MATCH ? ORDER BY bm25_score ASC LIMIT ?""", (_fts_query_text(text), limit)).fetchall()
        except sqlite3.OperationalError:
            pass
        if not rows:
            rows = con.execute("SELECT name, rel_path, description, tags, text FROM skills").fetchall()
    ranked = []
    for row in rows:
        hay = " ".join(str(row[k]) for k in row.keys() if k in {"name", "rel_path", "description", "tags", "text"}).lower()
        score = sum(hay.count(t) * 3 for t in terms)
        if row["name"].lower() in hay:
            score += 1
        if score > 0 or "bm25_score" in row.keys():
            ranked.append((score, row))
    ranked.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [{"name": r["name"], "rel_path": r["rel_path"], "description": r["description"], "score": float(score)} for score, r in ranked[:limit]]


def bench(hive_root: str | os.PathLike[str]) -> dict[str, object]:
    root = Path(hive_root).resolve()
    if not _db_path(root).exists():
        build_index(root, force=True)
    t0 = time.perf_counter(); q = query(root, "memory recall", limit=5); query_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter(); b = bundle(root, "memory recall", max_tokens=400); bundle_ms = (time.perf_counter() - t0) * 1000
    return {"ok": True, "query_ms": round(query_ms, 3), "bundle_ms": round(bundle_ms, 3), "results": len(q), "bundle_tokens": b.estimated_tokens, **stats(root)}

def _hive_from_args(ns: argparse.Namespace) -> Path:
    return Path(ns.hive or os.environ.get("MEMORY_HIVE_DIR") or ".")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="memory_hive_recall")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("build", "update", "doctor", "stats", "gc", "bench"):
        p = sub.add_parser(name)
        p.add_argument("--hive")
        p.add_argument("--json", action="store_true")
    q = sub.add_parser("query")
    q.add_argument("query")
    q.add_argument("--hive")
    q.add_argument("--json", action="store_true")
    q.add_argument("--limit", type=int, default=5)
    q.add_argument("--for-agent")
    b = sub.add_parser("bundle")
    b.add_argument("query")
    b.add_argument("--hive")
    b.add_argument("--max-tokens", type=int, default=1200)
    b.add_argument("--for-agent")
    b.add_argument("--json", action="store_true")
    b.add_argument("--cache", action="store_true")
    sk = sub.add_parser("skills")
    sk.add_argument("action", choices=["build", "query"])
    sk.add_argument("query", nargs="?")
    sk.add_argument("--hive")
    sk.add_argument("--skills-root")
    sk.add_argument("--limit", type=int, default=5)
    sk.add_argument("--json", action="store_true")
    ns = parser.parse_args(argv)
    hive = _hive_from_args(ns)
    try:
        if ns.cmd == "build":
            built = build_index(hive, force=True)
            payload = {"ok": True, "index_path": str(hive / ".hivecode" / "index.sqlite"), "files": len(built.files), "chunks": len(built.chunks), "codes": len(built.codes)}
        elif ns.cmd == "update":
            payload = update_index(hive)
        elif ns.cmd == "doctor":
            payload = doctor(hive)
        elif ns.cmd == "stats":
            payload = stats(hive)
        elif ns.cmd == "gc":
            payload = gc_index(hive)
        elif ns.cmd == "bench":
            payload = bench(hive)
        elif ns.cmd == "query":
            payload = query_json(hive, ns.query, limit=ns.limit, for_agent=ns.for_agent)
        elif ns.cmd == "bundle":
            if ns.json:
                print(json.dumps(bundle_json(hive, ns.query, max_tokens=ns.max_tokens, for_agent=ns.for_agent, cache=ns.cache), sort_keys=True))
            else:
                print(bundle(hive, ns.query, max_tokens=ns.max_tokens, for_agent=ns.for_agent).text)
            return 0
        elif ns.cmd == "skills":
            if ns.action == "build":
                payload = build_skill_index(hive, skills_root=ns.skills_root)
            else:
                if not ns.query:
                    parser.error("skills query requires query text")
                payload = {"query": ns.query, "results": query_skills(hive, ns.query, limit=ns.limit)}
        else:
            parser.error("unknown command")
        print(json.dumps(payload, sort_keys=True) if getattr(ns, "json", False) else payload)
        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
