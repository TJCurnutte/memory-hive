"""Shared RED-test helpers for the HiveCode Recall Engine.

These helpers intentionally exercise the public API that Loop 04+ must add.
Loop 03 should leave the tests failing because production recall code does not
exist yet.
"""

from __future__ import annotations

import importlib
import json
import math
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MEMORY_HIVE_CLI = REPO_ROOT / "memory-hive"


def recall_module():
    """Load the wished-for production module.

    Loop 03 RED expectation: this import fails until the implementation exists.
    """

    return importlib.import_module("memory_hive_recall")


def write_fixture_hive(base: Path) -> Path:
    """Create a small Memory Hive tree with citation-sensitive content."""

    hive = base / "hive"
    files = {
        "index.md": """# Memory Hive — Entry Point\n\nVisible pulls keep agents grounded.\n""",
        "agents/hermes/log.md": """# Hermes — Log\n2026-05-05 — Completed visible pull baseline for recall.\n2026-05-05 — Froze HiveCode recall specification.\n""",
        "agents/hermes/context.md": """# Hermes Context\n\n## Preferences\nHermes should retrieve compact cited snippets before long tasks.\n""",
        "agents/hermes/memory.md": """# Hermes Memory\n\n## Durable Facts\n- Recall bundles must cite source spans.\n  Continuation lines stay attached to their bullet.\n- Agent-specific memory should outrank broad unrelated notes.\n""",
        "learnings/raw/hermes/2026-05-05-visible-pulls.md": """---\ndate: 2026-05-05\nagent: hermes\ncontext: visible pull loop\n---\n# Visible Pulls\n\n## Nested Topic\nThis wrapped paragraph mentions orchid-anchor recall evidence\nacross two source lines for span validation.\n\n- First bullet for operational memory.\n  Continuation for the first bullet.\n- Second bullet.\n\n| item | value |\n|---|---|\n| recall | cited |\n\n```bash\nprintf '%s\\n' FAKE_DO_NOT_USE_PLACEHOLDER\n```\n""",
        "learnings/distilled/patterns.md": """# Distilled Patterns\n\nCitation-first recall prevents context drift.\n""",
        "knowledge/HUMAN_CONTEXT.md": """# Human Context\n\nTravis prefers direct operational output. The phrase zephyr-honeycomb only appears here.\n""",
        "registry/AGENTS.md": """# Agents\n\n| Agent | Role |\n|---|---|\n| hermes | operator |\n""",
        "tasks/queue.md": """# Queue\n\n- Build recall engine with RED tests first.\n""",
    }
    marker = "FAKE_DO_NOT_USE_" + "sk-" + "test" + ("0" * 24)
    files["knowledge/credential_fixture.md"] = (
        "# Credential Fixture\n\n"
        "This file contains a deliberately fake credential-like marker for "
        "redaction tests: " + marker + "\n"
    )

    for rel, text in files.items():
        path = hive / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return hive


def byte_slice(path: Path, start_byte: int, end_byte: int) -> bytes:
    return path.read_bytes()[start_byte:end_byte]


def estimated_tokens(text: str) -> int:
    return int(math.ceil(len(text) / 4))


def run_cli(args, *, hive: Path, check: bool = False):
    env = os.environ.copy()
    env["MEMORY_HIVE_DIR"] = str(hive)
    proc = subprocess.run(
        [str(MEMORY_HIVE_CLI)] + list(args),
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"CLI failed with {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def load_json_output(proc):
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"stdout was not JSON: {proc.stdout!r}") from exc


def sqlite_tables(db_path: Path):
    with sqlite3.connect(str(db_path)) as con:
        return {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
