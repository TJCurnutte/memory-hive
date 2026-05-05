"""Local-first HiveCode recall indexer for Memory Hive.

This module is intentionally dependency-light: Python stdlib + SQLite only.
Source Markdown remains authoritative; the SQLite database and HiveCodes are
citation-preserving derived state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from typing import Iterable


DATE_RE = re.compile(r"(20\d{2})[-/](\d{2})[-/](\d{2})")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


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
class IndexStatus:
    schema_version: str
    file_count: int
    chunk_count: int
    code_count: int
    fts5: str
    db_bytes: int


@dataclass(frozen=True)
class DriftResult:
    changed_chunks: int
    unchanged_chunks: int


@dataclass(frozen=True)
class ResolveResult:
    code: str
    rel_path: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    text: str
    stale: bool
    message: str = ""


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
    return path.relative_to(root).as_posix()


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
    return Chunk(
        rel_path=rel_path,
        kind=kind,
        text="".join(text_lines),
        start_line=start_line,
        end_line=end_line,
        start_byte=start_byte,
        end_byte=end_byte,
        heading_path=heading,
    )


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
            assert m is not None
            level = len(m.group(1))
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = m.group(2).strip()
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
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")) and lines[i].strip():
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
    if not m:
        return "000000"
    return f"{m.group(1)[2:]}{m.group(2)}{m.group(3)}"


def _topic_code(text: str, heading_path: str) -> str:
    words = [w.lower().strip("_-") for w in WORD_RE.findall((heading_path + " " + text).lower())]
    stop = {"the", "and", "for", "with", "this", "that", "must", "should", "source", "line", "lines"}
    words = [w for w in words if w not in stop]
    if words:
        return "-".join(words[:2])[:18].strip("-") or "ctx"
    return "ctx"


def _kind_code(kind: str) -> str:
    return {
        "frontmatter": "0f",
        "heading_section": "0h",
        "bullet": "0b",
        "log_line": "0l",
        "paragraph": "0p",
        "code_block": "0c",
        "table": "0t",
    }.get(kind, "0x")


def make_code(chunk: Chunk, agent: str) -> str:
    text_hash = _sha256(chunk.text.encode("utf-8"))
    sig = _base36_from_hex(_sha256((chunk.heading_path + "\n" + chunk.text.lower()).encode("utf-8")), 7)
    chk = text_hash[:8]
    return ":".join([
        "hc",
        "v1",
        _kind_code(chunk.kind),
        agent or "-",
        _date_code(chunk.rel_path, chunk.text),
        _topic_code(chunk.text, chunk.heading_path),
        sig,
        chk,
    ])


def iter_markdown_files(hive_root: Path) -> Iterable[Path]:
    skip_parts = {".git", ".hivecode", "node_modules", "__pycache__"}
    for path in sorted(hive_root.rglob("*.md")):
        if any(part in skip_parts for part in path.parts):
            continue
        yield path


def _db_path(hive_root: Path) -> Path:
    return hive_root / ".hivecode" / "index.sqlite"


def _init_db(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        DROP TABLE IF EXISTS chunks_fts;
        DROP TABLE IF EXISTS files;
        DROP TABLE IF EXISTS chunks;
        DROP TABLE IF EXISTS codes;
        DROP TABLE IF EXISTS tokens;
        DROP TABLE IF EXISTS sketches;
        DROP TABLE IF EXISTS meta;
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE files (
          id INTEGER PRIMARY KEY,
          rel_path TEXT UNIQUE NOT NULL,
          kind TEXT NOT NULL,
          agent TEXT NOT NULL,
          sha256 TEXT NOT NULL,
          size INTEGER NOT NULL,
          mtime_ns INTEGER NOT NULL,
          indexed_at INTEGER NOT NULL
        );
        CREATE TABLE chunks (
          id INTEGER PRIMARY KEY,
          file_id INTEGER NOT NULL,
          ordinal INTEGER NOT NULL,
          chunk_type TEXT NOT NULL,
          heading_path TEXT NOT NULL,
          start_line INTEGER NOT NULL,
          end_line INTEGER NOT NULL,
          start_byte INTEGER NOT NULL,
          end_byte INTEGER NOT NULL,
          text_sha256 TEXT NOT NULL,
          text TEXT NOT NULL,
          source_key TEXT NOT NULL,
          FOREIGN KEY(file_id) REFERENCES files(id)
        );
        CREATE TABLE codes (
          chunk_id INTEGER PRIMARY KEY,
          code TEXT UNIQUE NOT NULL,
          checksum TEXT NOT NULL,
          FOREIGN KEY(chunk_id) REFERENCES chunks(id)
        );
        CREATE TABLE tokens (chunk_id INTEGER NOT NULL, token TEXT NOT NULL, weight REAL NOT NULL);
        CREATE TABLE sketches (chunk_id INTEGER PRIMARY KEY, simhash64 TEXT NOT NULL);
        """
    )
    try:
        con.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(text, heading_path, rel_path)")
        con.execute("INSERT INTO meta(key, value) VALUES('fts5', 'available')")
    except sqlite3.OperationalError:
        con.execute("INSERT INTO meta(key, value) VALUES('fts5', 'unavailable')")


def build_index(hive_root: str | os.PathLike[str], *, force: bool = False, incremental: bool = False) -> BuildResult:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    files: dict[str, FileRecord] = {}
    chunks: list[Chunk] = []
    codes: list[CodeRecord] = []

    with sqlite3.connect(str(db_path)) as con:
        _init_db(con)
        con.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', '1')")
        for path in iter_markdown_files(root):
            rel_path = _rel(path, root)
            data = path.read_bytes()
            stat = path.stat()
            kind, agent = classify_file(rel_path)
            record = FileRecord(rel_path, kind, agent, _sha256(data), len(data), int(stat.st_mtime_ns))
            files[rel_path] = record
            cur = con.execute(
                "INSERT INTO files(rel_path, kind, agent, sha256, size, mtime_ns, indexed_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (record.rel_path, record.kind, record.agent, record.sha256, record.size, record.mtime_ns, int(time.time())),
            )
            file_id = int(cur.lastrowid)
            for ordinal, chunk in enumerate(chunk_file(path, hive_root=root), start=1):
                code = make_code(chunk, agent)
                chunk_with_code = Chunk(**{**chunk.__dict__, "code": code})
                chunks.append(chunk_with_code)
                checksum = _sha256(chunk.text.encode("utf-8"))
                ccur = con.execute(
                    """INSERT INTO chunks(file_id, ordinal, chunk_type, heading_path, start_line, end_line,
                       start_byte, end_byte, text_sha256, text, source_key) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (file_id, ordinal, chunk.kind, chunk.heading_path, chunk.start_line, chunk.end_line, chunk.start_byte, chunk.end_byte, checksum, chunk.text, chunk.source_key),
                )
                chunk_id = int(ccur.lastrowid)
                con.execute("INSERT INTO codes(chunk_id, code, checksum) VALUES(?, ?, ?)", (chunk_id, code, checksum))
                try:
                    con.execute("INSERT INTO chunks_fts(rowid, text, heading_path, rel_path) VALUES(?, ?, ?, ?)", (chunk_id, chunk.text, chunk.heading_path, rel_path))
                except sqlite3.OperationalError:
                    pass
                for token in sorted(set(w.lower() for w in WORD_RE.findall(chunk.text))):
                    con.execute("INSERT INTO tokens(chunk_id, token, weight) VALUES(?, ?, ?)", (chunk_id, token, 1.0))
                con.execute("INSERT INTO sketches(chunk_id, simhash64) VALUES(?, ?)", (chunk_id, _sha256(chunk.text.lower().encode("utf-8"))[:16]))
                codes.append(CodeRecord(code, chunk.source_key, rel_path, chunk.start_line, chunk.end_line, checksum))
        con.commit()
    return BuildResult(root, db_path, files, chunks, codes)


def compare_code_sets(before: list[str], after: list[str]) -> DriftResult:
    before_set = set(before)
    after_set = set(after)
    return DriftResult(changed_chunks=len(before_set.symmetric_difference(after_set)), unchanged_chunks=len(before_set & after_set))


def _connect_existing(hive_root: str | os.PathLike[str]) -> sqlite3.Connection:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    if not db_path.exists():
        raise FileNotFoundError(f"HiveCode index missing at {db_path}; run recall build first")
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    return con


def get_file_record(hive_root: str | os.PathLike[str], rel_path: str) -> FileRecord:
    with _connect_existing(hive_root) as con:
        row = con.execute(
            "SELECT rel_path, kind, agent, sha256, size, mtime_ns FROM files WHERE rel_path = ?",
            (rel_path,),
        ).fetchone()
    if row is None:
        raise KeyError(rel_path)
    return FileRecord(row["rel_path"], row["kind"], row["agent"], row["sha256"], int(row["size"]), int(row["mtime_ns"]))


def index_status(hive_root: str | os.PathLike[str]) -> IndexStatus:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    with _connect_existing(root) as con:
        def scalar(sql: str, default=0):
            row = con.execute(sql).fetchone()
            return row[0] if row and row[0] is not None else default
        schema = scalar("SELECT value FROM meta WHERE key='schema_version'", "")
        fts5 = scalar("SELECT value FROM meta WHERE key='fts5'", "unavailable")
        return IndexStatus(
            schema_version=str(schema),
            file_count=int(scalar("SELECT count(*) FROM files")),
            chunk_count=int(scalar("SELECT count(*) FROM chunks")),
            code_count=int(scalar("SELECT count(*) FROM codes")),
            fts5=str(fts5),
            db_bytes=db_path.stat().st_size,
        )


def stats(hive_root: str | os.PathLike[str]) -> dict[str, int]:
    status = index_status(hive_root)
    with _connect_existing(hive_root) as con:
        token_count = int(con.execute("SELECT count(*) FROM tokens").fetchone()[0])
    return {
        "files": status.file_count,
        "chunks": status.chunk_count,
        "tokens": token_count,
        "codes": status.code_count,
        "db_bytes": status.db_bytes,
    }


def doctor(hive_root: str | os.PathLike[str]) -> dict[str, object]:
    status = index_status(hive_root)
    return {
        "ok": True,
        "schema_version": status.schema_version,
        "fts5": status.fts5 == "available",
        "files_indexed": status.file_count,
        "stale_files": [],
    }


def resolve_code(hive_root: str | os.PathLike[str], code: str) -> ResolveResult:
    root = Path(hive_root).resolve()
    db_path = _db_path(root)
    if not db_path.exists():
        raise FileNotFoundError(f"HiveCode index missing at {db_path}; run recall build first")
    with sqlite3.connect(str(db_path)) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            """SELECT f.rel_path, c.start_line, c.end_line, c.start_byte, c.end_byte, c.text, co.checksum
               FROM codes co JOIN chunks c ON c.id = co.chunk_id JOIN files f ON f.id = c.file_id
               WHERE co.code = ?""",
            (code,),
        ).fetchone()
    if row is None:
        raise KeyError(code)
    path = root / row["rel_path"]
    raw = path.read_bytes()
    current = raw[int(row["start_byte"]):int(row["end_byte"])]
    current_hash = _sha256(current)
    stale = current_hash != row["checksum"]
    text = current.decode("utf-8", errors="replace")
    return ResolveResult(
        code=code,
        rel_path=row["rel_path"],
        start_line=int(row["start_line"]),
        end_line=int(row["end_line"]),
        start_byte=int(row["start_byte"]),
        end_byte=int(row["end_byte"]),
        text=text,
        stale=stale,
        message=("Source drift detected; rebuild the HiveCode index before using this citation." if stale else "OK"),
    )
