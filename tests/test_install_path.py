"""Installer PATH behavior tests.

These cover the public copy-paste install path: after `curl ... | sh`, the next
terminal command should be `memory-hive ...`, not `sh ~/.memory-hive/memory-hive`.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = REPO_ROOT / "install.sh"


class InstallPathTests(unittest.TestCase):
    def test_installer_places_memory_hive_command_on_existing_path_for_immediate_use(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            path_bin = root / "bin"
            home.mkdir()
            path_bin.mkdir()
            script = root / "run.sh"
            output = root / "install.out"
            env_path = f"{path_bin}:/usr/bin:/bin"
            script.write_text(
                "set -eu\n"
                f"export HOME={home}\n"
                f"export PATH={env_path}\n"
                f"export MEMORY_HIVE_DIR={home / '.memory-hive'}\n"
                f"export MEMORY_HIVE_REPO={REPO_ROOT}\n"
                "export MEMORY_HIVE_ONLY=none\n"
                f"sh {INSTALL_SH} > {output}\n"
                "command -v memory-hive\n"
                "memory-hive\n"
                "memory-hive list\n"
                "memory-hive recall query 'Memory Hive' --limit 1 --json\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                ["/bin/sh", str(script)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )

            if proc.returncode != 0:
                raise AssertionError(
                    f"installer smoke failed with {proc.returncode}\n"
                    f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}\n"
                    f"INSTALL OUT:\n{output.read_text(encoding='utf-8') if output.exists() else ''}"
                )

            self.assertIn(str(path_bin / "memory-hive"), proc.stdout)
            self.assertIn("Memory Hive status", proc.stdout)
            self.assertIn("main", proc.stdout)
            self.assertIn('"query": "Memory Hive"', proc.stdout)
            install_out = output.read_text(encoding="utf-8")
            self.assertIn("Command ready: memory-hive", install_out)
            self.assertNotIn("Tip: add", install_out)

    def test_installer_compacts_long_roster_in_success_banner(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            path_bin = root / "bin"
            install_dir = home / ".memory-hive"
            agents_dir = install_dir / "hive" / "agents"
            home.mkdir()
            path_bin.mkdir()
            for idx in range(1, 21):
                agent_dir = agents_dir / f"agent-{idx:02d}"
                agent_dir.mkdir(parents=True)
                (agent_dir / "log.md").write_text("# Log\n", encoding="utf-8")
                (agent_dir / "memory.md").write_text("# Memory\n", encoding="utf-8")
                (agent_dir / "context.md").write_text("# Context\n\n## Role\n\nWrites code.\n", encoding="utf-8")

            output = root / "install.out"
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "PATH": f"{path_bin}:/usr/bin:/bin",
                    "MEMORY_HIVE_DIR": str(install_dir),
                    "MEMORY_HIVE_REPO": str(REPO_ROOT),
                    "MEMORY_HIVE_ONLY": "none",
                    "MEMORY_HIVE_WIZARD": "0",
                }
            )
            proc = subprocess.run(
                ["/bin/sh", str(INSTALL_SH)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                timeout=60,
            )
            output.write_text(proc.stdout + proc.stderr, encoding="utf-8")
            if proc.returncode != 0:
                raise AssertionError(output.read_text(encoding="utf-8"))

            install_out = output.read_text(encoding="utf-8")
            self.assertIn("agents total", install_out)
            self.assertIn("Full roster: memory-hive list", install_out)
            self.assertIn("Preview:", install_out)
            self.assertNotIn("agent-20             Writes code", install_out)


if __name__ == "__main__":
    unittest.main()
