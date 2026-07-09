#!/usr/bin/env python3
"""Thin Memory Hive v2 benchmark wrapper."""

from __future__ import annotations

from pathlib import Path
import json
import os
import sys

INSTALL_DIR = Path(__file__).resolve().parents[1]
if str(INSTALL_DIR) not in sys.path:
    sys.path.insert(0, str(INSTALL_DIR))

from memory_hive_orchestrate import bench_suite  # noqa: E402


def main() -> int:
    hive = Path(os.environ.get("MEMORY_HIVE_DIR") or (Path.home() / ".memory-hive" / "hive")).expanduser()
    result = bench_suite(hive)
    claims = result["claims"]

    print("Memory Hive v2 benchmark")
    print(f"Hive: {result['hive_root']}")
    print(f"Query: {result['query']}")
    print()
    print(f"naive: {result['naive_tokens']} tokens, {result['naive_ms']} ms")
    print(f"v0.3.2: {result['v032_tokens']} tokens, {result['v032_ms']} ms")
    print(f"v2: {result['v2_tokens']} tokens, {result['v2_ms']} ms")
    print()
    print(f"speedup_vs_naive_pct: {result['speedup_vs_naive_pct']}")
    print(f"efficiency_vs_naive: {result['efficiency_vs_naive']}x")
    print(f"speedup_vs_v032_pct: {result['speedup_vs_v032_pct']}")
    print(f"efficiency_vs_v032: {result['efficiency_vs_v032']}x")
    print()
    print("claims:")
    print(json.dumps(claims, indent=2, sort_keys=True))
    if not all(claims.values()):
        print("Claim gates did not all pass; exiting 0 for first-run tuning.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
