#!/usr/bin/env python3
"""Memory Hive usage analytics for the self-iteration loop.

Reads a Memory Hive tree (and its rebuildable HyperRecall index) and emits a
usage snapshot: corpus size, per-agent/per-platform memory footprint, recall
index health, learning-pipeline state (raw vs distilled), and stale signal.

Stdlib only — matches the rest of the project. The loop runs this every
iteration so "overall use" of the hive is visible and trends over time.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_recall(repo_root: Path) -> Any:
    module_path = repo_root / "memory_hive_recall.py"
    spec = importlib.util.spec_from_file_location("memory_hive_recall_loop", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _refresh_index(recall: Any, hive: Path) -> dict[str, Any]:
    """Bring the recall index up to date; this is itself a hive improvement."""
    db = hive / ".hivecode" / "index.sqlite"
    t0 = time.perf_counter()
    if db.exists():
        try:
            result = recall.update_index(hive)
            mode = "incremental"
        except Exception:
            recall.build_index(hive, force=True)
            result = {"rebuilt": True}
            mode = "rebuild"
    else:
        recall.build_index(hive, force=True)
        result = {"rebuilt": True}
        mode = "initial-build"
    return {"mode": mode, "ms": round((time.perf_counter() - t0) * 1000, 2), "detail": result}


def _db(hive: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(hive / ".hivecode" / "index.sqlite"))
    con.row_factory = sqlite3.Row
    return con


def resolve_hive_root(path: Path) -> Path:
    """Return the dir that directly holds agents/, learnings/, etc.

    Accepts either an install dir (``<dir>/hive`` holds the content) or a hive
    content root passed directly.
    """
    for candidate in (path, path / "hive"):
        if (candidate / "agents").is_dir() or (candidate / "learnings").is_dir() or (candidate / "index.md").exists():
            return candidate
    return path


def collect_usage(repo_root: Path, hive: Path) -> dict[str, Any]:
    hive = resolve_hive_root(Path(hive).expanduser().resolve())
    recall = _load_recall(repo_root)
    refresh = _refresh_index(recall, hive)

    status = recall.index_status(hive)
    doctor = recall.doctor(hive)

    with _db(hive) as con:
        corpus_chars = int(con.execute("SELECT COALESCE(SUM(LENGTH(text)), 0) FROM chunks").fetchone()[0])
        token_rows = int(con.execute("SELECT COUNT(*) FROM tokens").fetchone()[0])
        distinct_terms = int(con.execute("SELECT COUNT(DISTINCT token) FROM tokens").fetchone()[0])
        per_agent_rows = con.execute(
            """
            SELECT f.agent AS agent,
                   COUNT(DISTINCT f.id) AS files,
                   COUNT(c.id) AS chunks,
                   COALESCE(SUM(LENGTH(c.text)), 0) AS chars
            FROM files f
            LEFT JOIN chunks c ON c.file_id = f.id
            GROUP BY f.agent
            ORDER BY chunks DESC, agent ASC
            """
        ).fetchall()
        per_kind_rows = con.execute(
            """
            SELECT f.kind AS kind,
                   COUNT(DISTINCT f.id) AS files,
                   COUNT(c.id) AS chunks
            FROM files f
            LEFT JOIN chunks c ON c.file_id = f.id
            GROUP BY f.kind
            ORDER BY chunks DESC, kind ASC
            """
        ).fetchall()

    per_agent = [
        {
            "agent": r["agent"],
            "files": r["files"],
            "chunks": r["chunks"],
            "est_tokens": (int(r["chars"]) + 3) // 4,
        }
        for r in per_agent_rows
    ]
    per_kind = [{"kind": r["kind"], "files": r["files"], "chunks": r["chunks"]} for r in per_kind_rows]

    raw_learnings = sum(k["files"] for k in per_kind if k["kind"] == "learning")
    distilled = sum(k["files"] for k in per_kind if k["kind"] == "distilled")
    # Knowledge-promotion ratio: how much raw signal has been curated into truth.
    promotion = round(distilled / raw_learnings, 3) if raw_learnings else None

    stale = list(doctor.get("stale_files", []))
    silos = [a for a in per_agent if a["agent"] not in ("-", "")]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hive": str(hive),
        "index_refresh": refresh,
        "corpus": {
            "files": status.file_count,
            "chunks": status.chunk_count,
            "codes": status.code_count,
            "est_tokens": (corpus_chars + 3) // 4,
            "token_postings": token_rows,
            "distinct_terms": distinct_terms,
            "db_bytes": status.db_bytes,
            "fts5": status.fts5,
            "schema_version": status.schema_version,
        },
        "platforms": {
            "silo_count": len(silos),
            "per_agent": per_agent,
        },
        "content_types": per_kind,
        "learning_pipeline": {
            "raw": raw_learnings,
            "distilled": distilled,
            "promotion_ratio": promotion,
        },
        "health": {
            "ok": bool(doctor.get("ok")),
            "fts5_available": bool(doctor.get("fts5")),
            "stale_count": len(stale),
            "stale_files": stale[:25],
        },
    }


def compute_trend(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    """Deltas between this iteration and the previous one.

    Lets the hourly loop show whether overall use of the hive is improving
    (more memory captured, more learnings distilled, fewer stale files).
    """
    cc, bc = current["corpus"], baseline.get("corpus", {})
    cl, bl = current["learning_pipeline"], baseline.get("learning_pipeline", {})
    ch, bh = current["health"], baseline.get("health", {})

    def d(a: Any, b: Any) -> int:
        return int(a or 0) - int(b or 0)

    cur_agents = {a["agent"] for a in current["platforms"]["per_agent"]}
    base_agents = {a["agent"] for a in baseline.get("platforms", {}).get("per_agent", [])}
    new_silos = sorted(a for a in (cur_agents - base_agents) if a not in ("-", ""))

    return {
        "baseline_generated_at": baseline.get("generated_at"),
        "files": d(cc.get("files"), bc.get("files")),
        "chunks": d(cc.get("chunks"), bc.get("chunks")),
        "est_tokens": d(cc.get("est_tokens"), bc.get("est_tokens")),
        "raw_learnings": d(cl.get("raw"), bl.get("raw")),
        "distilled": d(cl.get("distilled"), bl.get("distilled")),
        "stale_count": d(ch.get("stale_count"), bh.get("stale_count")),
        "new_silos": new_silos,
    }


def _signed(n: int) -> str:
    return f"+{n:,}" if n > 0 else f"{n:,}"


def _bar(value: int, peak: int, width: int = 24) -> str:
    if peak <= 0:
        return ""
    filled = int(round(width * value / peak))
    return "#" * filled + "." * (width - filled)


def render_markdown(data: dict[str, Any]) -> str:
    c = data["corpus"]
    lp = data["learning_pipeline"]
    h = data["health"]
    lines: list[str] = []
    lines.append("# Memory Hive — Usage Snapshot")
    lines.append("")
    lines.append(f"- Generated: `{data['generated_at']}`")
    lines.append(f"- Hive: `{data['hive']}`")
    lines.append(
        f"- Index refresh: `{data['index_refresh']['mode']}` "
        f"in `{data['index_refresh']['ms']} ms`"
    )
    lines.append("")
    trend = data.get("trend")
    if trend:
        lines.append("## Trend since last run")
        lines.append("")
        lines.append(f"- Baseline: `{trend.get('baseline_generated_at')}`")
        lines.append("")
        lines.append("| Metric | Δ |")
        lines.append("|---|---:|")
        lines.append(f"| Files indexed | {_signed(trend['files'])} |")
        lines.append(f"| Chunks | {_signed(trend['chunks'])} |")
        lines.append(f"| Estimated tokens | {_signed(trend['est_tokens'])} |")
        lines.append(f"| Raw learnings | {_signed(trend['raw_learnings'])} |")
        lines.append(f"| Distilled patterns | {_signed(trend['distilled'])} |")
        lines.append(f"| Stale files | {_signed(trend['stale_count'])} |")
        lines.append("")
        if trend["new_silos"]:
            lines.append("- New silos: " + ", ".join(f"`{s}`" for s in trend["new_silos"]))
            lines.append("")
    lines.append("## Corpus")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Files indexed | {c['files']} |")
    lines.append(f"| Chunks (citable spans) | {c['chunks']} |")
    lines.append(f"| Stable HiveCodes | {c['codes']} |")
    lines.append(f"| Estimated tokens | {c['est_tokens']:,} |")
    lines.append(f"| Distinct terms | {c['distinct_terms']:,} |")
    lines.append(f"| Index size (bytes) | {c['db_bytes']:,} |")
    lines.append(f"| FTS5 backend | {c['fts5']} |")
    lines.append("")
    lines.append("## Memory footprint per platform / agent")
    lines.append("")
    lines.append("| Agent | Files | Chunks | Est. tokens | Share |")
    lines.append("|---|---:|---:|---:|---|")
    peak = max((a["chunks"] for a in data["platforms"]["per_agent"]), default=0)
    total_chunks = sum(a["chunks"] for a in data["platforms"]["per_agent"]) or 1
    for a in data["platforms"]["per_agent"]:
        share = 100.0 * a["chunks"] / total_chunks
        label = "(shared/curated)" if a["agent"] == "-" else f"`{a['agent']}`"
        lines.append(
            f"| {label} | {a['files']} | {a['chunks']} | "
            f"{a['est_tokens']:,} | `{_bar(a['chunks'], peak)}` {share:4.1f}% |"
        )
    lines.append("")
    lines.append("## Learning pipeline")
    lines.append("")
    lines.append(f"- Raw learnings captured: **{lp['raw']}**")
    lines.append(f"- Distilled patterns promoted: **{lp['distilled']}**")
    lines.append(f"- Promotion ratio (distilled / raw): **{lp['promotion_ratio']}**")
    lines.append("")
    lines.append("## Health")
    lines.append("")
    lines.append(f"- Index OK: **{h['ok']}**")
    lines.append(f"- FTS5 available: **{h['fts5_available']}**")
    lines.append(f"- Stale files: **{h['stale_count']}**")
    if h["stale_files"]:
        for s in h["stale_files"]:
            lines.append(f"  - `{s}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Memory Hive usage analytics")
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument(
        "--hive",
        default=os.environ.get("MEMORY_HIVE_DIR", str(Path.home() / ".memory-hive")),
    )
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--markdown", dest="md_path")
    parser.add_argument(
        "--baseline",
        dest="baseline_path",
        help="prior snapshot JSON to diff against for a trend section",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo).resolve()
    hive = resolve_hive_root(Path(args.hive).expanduser().resolve())
    if not (hive / ".hivecode").exists() and not any(hive.rglob("*.md")):
        print(f"error: no hive content found under {hive}", file=sys.stderr)
        return 2

    data = collect_usage(repo_root, hive)

    if args.baseline_path:
        baseline_file = Path(args.baseline_path)
        if baseline_file.is_file():
            try:
                baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
                data["trend"] = compute_trend(data, baseline)
            except (json.JSONDecodeError, KeyError, OSError):
                pass

    md = render_markdown(data)

    if args.json_path:
        p = Path(args.json_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_path:
        p = Path(args.md_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md + "\n", encoding="utf-8")

    if not args.json_path and not args.md_path:
        print(md)
    else:
        print(
            f"usage snapshot: {data['corpus']['files']} files, "
            f"{data['corpus']['chunks']} chunks, "
            f"{data['platforms']['silo_count']} silos, "
            f"health_ok={data['health']['ok']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
