"""RED/GREEN tests for HiveCode SQLite index build and status."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from hivecode_test_utils import recall_module, sqlite_tables, write_fixture_hive


class HiveCodeIndexBuildStatusTests(unittest.TestCase):
    def test_build_creates_core_sqlite_tables_and_status(self):
        with tempfile.TemporaryDirectory() as td:
            hive = write_fixture_hive(Path(td))
            mod = recall_module()
            built = mod.build_index(hive, force=True)
            db_path = hive / ".hivecode" / "index.sqlite"
            self.assertEqual(Path(built.db_path).resolve(), db_path.resolve())
            self.assertTrue(db_path.exists())
            self.assertTrue({"files", "chunks", "codes", "tokens", "sketches", "meta"}.issubset(sqlite_tables(built.db_path)))

            status = mod.index_status(hive)
            self.assertEqual(status.schema_version, "1")
            self.assertEqual(status.file_count, len(built.files))
            self.assertEqual(status.chunk_count, len(built.chunks))
            self.assertGreaterEqual(status.code_count, status.chunk_count)
            self.assertIn(status.fts5, {"available", "unavailable"})


if __name__ == "__main__":
    unittest.main()
