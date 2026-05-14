#!/usr/bin/env python3
"""Run 1000 proof loops against Memory Hive incremental recall updates.

This is a local verification harness, not a shipping/deploy step. It copies a
hive tree into a temporary sandbox, builds a recall index once, then proves that
1000 append/update/query cycles succeed without calling full rebuild.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def import_recall(repo_root: Path) -> Any:
    module_path = repo_root / "memory_hive_recall.py"
    spec = importlib.util.spec_from_file_location("memory_hive_recall_under_test", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_hive(src: Path, dst: Path) -> None:
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {n for n in names if n in {".git", ".hivecode", "node_modules", "__pycache__"}}

    shutil.copytree(src, dst, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-hive", default=str(Path.home() / ".memory-hive" / "hive"))
    parser.add_argument("--loops", type=int, default=1000)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    source_hive = Path(args.source_hive).expanduser().resolve()
    report = Path(args.report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    recall = import_recall(repo)

    with tempfile.TemporaryDirectory(prefix="memory-hive-1000-loop-") as td:
        hive = Path(td) / "hive"
        copy_hive(source_hive, hive)
        target = hive / "agents" / "hermes" / "memory.md"
        if not target.exists():
            raise RuntimeError(f"missing target memory file: {target}")

        t0 = time.perf_counter()
        recall.build_index(hive, force=True)
        build_ms = (time.perf_counter() - t0) * 1000

        full_build = recall.build_index

        def forbidden_full_rebuild(*_a, **_kw):
            raise AssertionError("incremental update called full build_index")

        recall.build_index = forbidden_full_rebuild
        update_times: list[float] = []
        query_times: list[float] = []
        doctor_checks = 0
        max_update_ms = 0.0
        max_query_ms = 0.0
        failures: list[str] = []

        try:
            for i in range(1, args.loops + 1):
                marker = f"mh1000-proof-marker-{i:04d}"
                with target.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n- {marker}: incremental update remembered this appended fact.\n")

                t0 = time.perf_counter()
                result = recall.update_index(hive)
                update_ms = (time.perf_counter() - t0) * 1000
                update_times.append(update_ms)
                max_update_ms = max(max_update_ms, update_ms)
                if result.get("changed_files") != 1 or result.get("deleted_files") != 0:
                    failures.append(f"loop {i}: unexpected update result {result}")
                    break

                t0 = time.perf_counter()
                hits = recall.query(hive, marker, for_agent="hermes", limit=1)
                query_ms = (time.perf_counter() - t0) * 1000
                query_times.append(query_ms)
                max_query_ms = max(max_query_ms, query_ms)
                if not hits or hits[0].citation.rel_path != "agents/hermes/memory.md" or marker not in hits[0].snippet:
                    failures.append(f"loop {i}: marker not recalled from hermes memory")
                    break

                if i % 100 == 0:
                    doctor_checks += 1
                    doctor = recall.doctor(hive)
                    if not doctor.get("ok"):
                        failures.append(f"loop {i}: doctor stale {doctor}")
                        break
        finally:
            recall.build_index = full_build

        loops_completed = len(update_times)
        summary = {
            "ok": not failures and loops_completed == args.loops,
            "loops_requested": args.loops,
            "loops_completed": loops_completed,
            "build_ms": round(build_ms, 3),
            "update_ms_min": round(min(update_times), 3) if update_times else None,
            "update_ms_avg": round(sum(update_times) / len(update_times), 3) if update_times else None,
            "update_ms_max": round(max_update_ms, 3),
            "query_ms_min": round(min(query_times), 3) if query_times else None,
            "query_ms_avg": round(sum(query_times) / len(query_times), 3) if query_times else None,
            "query_ms_max": round(max_query_ms, 3),
            "doctor_checks": doctor_checks,
            "source_hive": str(source_hive),
            "repo": str(repo),
            "failures": failures,
        }
        report.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, sort_keys=True))
        return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
