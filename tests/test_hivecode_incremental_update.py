"""Regression tests for real incremental recall-index updates.

The public contract is that Memory Hive can absorb common append/edit churn
without rebuilding every unchanged chunk, while newly written memory remains
queryable immediately after `recall update`.
"""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hivecode_test_utils import recall_module, write_fixture_hive


class HiveCodeIncrementalUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))
        self.recall = recall_module()
        self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _row(self, rel_path: str):
        db_path = self.hive / ".hivecode" / "index.sqlite"
        with sqlite3.connect(str(db_path)) as con:
            con.row_factory = sqlite3.Row
            return con.execute(
                "SELECT id, rel_path, sha256, size, mtime_ns FROM files WHERE rel_path=?",
                (rel_path,),
            ).fetchone()

    def test_update_index_does_not_full_rebuild_for_single_file_append(self):
        unchanged_before = self._row("knowledge/HUMAN_CONTEXT.md")
        target = self.hive / "agents" / "hermes" / "memory.md"
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\n- Fresh append remembers the needle phrase: incremental-orchid-speed.\n",
            encoding="utf-8",
        )

        with mock.patch.object(self.recall, "build_index", side_effect=AssertionError("full rebuild should not run")):
            result = self.recall.update_index(self.hive)

        self.assertEqual(result["changed_files"], 1)
        self.assertGreaterEqual(result["skipped_files"], 1)
        self.assertEqual(result["deleted_files"], 0)
        unchanged_after = self._row("knowledge/HUMAN_CONTEXT.md")
        self.assertEqual(dict(unchanged_before), dict(unchanged_after))

        hits = self.recall.query(self.hive, "incremental-orchid-speed", for_agent="hermes", limit=1)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].citation.rel_path, "agents/hermes/memory.md")
        self.assertIn("incremental-orchid-speed", hits[0].snippet)

    def test_update_index_removes_deleted_file_without_full_rebuild(self):
        deleted = self.hive / "knowledge" / "credential_fixture.md"
        deleted.unlink()

        with mock.patch.object(self.recall, "build_index", side_effect=AssertionError("full rebuild should not run")):
            result = self.recall.update_index(self.hive)

        self.assertEqual(result["deleted_files"], 1)
        report = self.recall.doctor(self.hive)
        self.assertNotIn("knowledge/credential_fixture.md", report["stale_files"])
        with self.assertRaises(KeyError):
            self.recall.get_file_record(self.hive, "knowledge/credential_fixture.md")


if __name__ == "__main__":
    unittest.main()
