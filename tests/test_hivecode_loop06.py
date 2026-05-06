"""Loop 06 RED tests for HiveCode UX hardening and retrieval metadata."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import load_json_output, recall_module, run_cli, write_fixture_hive


class HiveCodeLoop06UxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))
        self.recall = recall_module()
        self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_query_json_reports_backend_and_fallback_flag(self):
        payload = self.recall.query_json(self.hive, "zephyr-honeycomb", limit=1, use_fts=False)
        self.assertEqual(payload["backend"], "lexical")
        self.assertEqual(payload["fallback"], "forced")
        self.assertEqual(payload["results"][0]["reason"], "lexical-term-match")

    def test_recall_query_json_cli_is_machine_parseable(self):
        proc = run_cli(["recall", "query", "zephyr-honeycomb", "--hive", str(self.hive), "--json", "--limit", "1"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertEqual(payload["query"], "zephyr-honeycomb")
        self.assertIn("backend", payload)
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["citation"]["rel_path"], "knowledge/HUMAN_CONTEXT.md")

    def test_recall_bundle_json_cli_reports_budget_and_citations(self):
        proc = run_cli(["recall", "bundle", "recall evidence", "--hive", str(self.hive), "--for-agent", "hermes", "--max-tokens", "120", "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertEqual(set(payload.keys()), {"query", "estimated_tokens", "max_tokens", "source_fingerprint", "cache_hit", "text", "results"})
        self.assertLessEqual(payload["estimated_tokens"], 120)
        self.assertIn("hc:v1:", payload["text"])
        self.assertIn("citation", payload["results"][0])

    def test_top_level_help_documents_recall_commands(self):
        proc = run_cli(["help"], hive=self.hive, check=True)
        help_text = proc.stdout
        self.assertIn("memory-hive recall build", help_text)
        self.assertIn("memory-hive recall query", help_text)
        self.assertIn("memory-hive recall bundle", help_text)
        self.assertIn("hive/.hivecode/index.sqlite", help_text)


if __name__ == "__main__":
    unittest.main()
