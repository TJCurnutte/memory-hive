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
                "memory-hive list\n",
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
            self.assertIn("main", proc.stdout)
            install_out = output.read_text(encoding="utf-8")
            self.assertIn("Command ready: memory-hive", install_out)
            self.assertNotIn("Tip: add", install_out)


if __name__ == "__main__":
    unittest.main()
