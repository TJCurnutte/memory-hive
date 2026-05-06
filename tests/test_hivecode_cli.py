"""RED tests for HiveCode CLI build/query/doctor/stats behavior."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import load_json_output, run_cli, sqlite_tables, write_fixture_hive


class HiveCodeCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_recall_build_creates_sqlite_index_under_hivecode_dir(self):
        proc = run_cli(["recall", "build", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        db_path = self.hive / ".hivecode" / "index.sqlite"
        self.assertTrue(db_path.exists())
        self.assertEqual(payload["index_path"], str(db_path))
        self.assertIn("chunks", sqlite_tables(db_path))
        self.assertIn("codes", sqlite_tables(db_path))

    def test_recall_doctor_reports_index_freshness_and_fts_status(self):
        run_cli(["recall", "build", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        proc = run_cli(["recall", "doctor", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertEqual(set(payload.keys()), {"ok", "schema_version", "fts5", "files_indexed", "stale_files", "missing_files", "source_fingerprint"})
        self.assertTrue(payload["ok"])
        self.assertIsInstance(payload["fts5"], bool)

    def test_recall_stats_reports_counts_without_scanning_full_output(self):
        run_cli(["recall", "build", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        proc = run_cli(["recall", "stats", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertGreaterEqual(payload["files"], 9)
        self.assertGreater(payload["chunks"], payload["files"])
        self.assertGreater(payload["codes"], 0)
        self.assertGreater(payload["db_bytes"], 0)

    def test_recall_build_without_hive_flag_uses_installed_hive_dir(self):
        proc = run_cli(["recall", "build", "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertEqual(payload["index_path"], str(self.hive / ".hivecode" / "index.sqlite"))
        self.assertTrue((self.hive / ".hivecode" / "index.sqlite").exists())

    def test_recall_query_missing_index_exits_nonzero_with_useful_error(self):
        proc = run_cli(["recall", "query", "zephyr-honeycomb", "--hive", str(self.hive)], hive=self.hive)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("recall build", (proc.stderr + proc.stdout).lower())
        self.assertFalse((self.hive / ".hivecode" / "index.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
