"""RED tests for HiveCode query ranking, code resolution, and fallback mode."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import recall_module, write_fixture_hive


class HiveCodeQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))
        self.recall = recall_module()
        self.index = self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_query_unique_phrase_returns_matching_chunk_first(self):
        results = self.recall.query(self.hive, "zephyr-honeycomb", limit=3)
        self.assertGreater(len(results), 0)
        first = results[0]
        self.assertEqual(first.citation.rel_path, "knowledge/HUMAN_CONTEXT.md")
        self.assertIn("zephyr-honeycomb", first.snippet)
        self.assertLessEqual(first.citation.start_line, first.citation.end_line)

    def test_query_filters_agent_and_kind(self):
        results = self.recall.query(self.hive, "agent-specific memory", for_agent="hermes", limit=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].citation.agent, "hermes")
        self.assertIn("agents/hermes/memory.md", results[0].citation.rel_path)

    def test_query_by_hivecode_resolves_exact_chunk(self):
        result = self.recall.query(self.hive, "orchid-anchor", limit=1)[0]
        resolved = self.recall.resolve_code(self.hive, result.code)
        self.assertEqual(resolved.chunk_id, result.chunk_id)
        self.assertEqual(resolved.citation.rel_path, result.citation.rel_path)
        self.assertEqual(resolved.citation.start_line, result.citation.start_line)

    def test_query_marks_stale_code_after_source_edit_without_rebuild(self):
        result = self.recall.query(self.hive, "orchid-anchor", limit=1)[0]
        source = self.hive / result.citation.rel_path
        source.write_text(
            source.read_text(encoding="utf-8").replace("orchid-anchor", "orchid-drift"),
            encoding="utf-8",
        )
        resolved = self.recall.resolve_code(self.hive, result.code)
        self.assertEqual(resolved.status, "STALE")
        self.assertIn("rebuild", resolved.guidance.lower())

    def test_query_fallback_without_fts5_keeps_output_shape(self):
        results = self.recall.query(self.hive, "zephyr-honeycomb", limit=1, use_fts=False)
        self.assertEqual(len(results), 1)
        item = results[0]
        self.assertTrue(item.code.startswith("hc:v1:"))
        self.assertGreater(item.score, 0)
        self.assertEqual(item.citation.rel_path, "knowledge/HUMAN_CONTEXT.md")


if __name__ == "__main__":
    unittest.main()
