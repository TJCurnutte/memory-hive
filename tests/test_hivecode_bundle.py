"""RED tests for HiveCode bundle budgets, redaction, and JSON contracts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import estimated_tokens, recall_module, write_fixture_hive


class HiveCodeBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))
        self.recall = recall_module()
        self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_bundle_respects_max_token_budget_with_citations(self):
        bundle = self.recall.bundle(self.hive, "recall evidence", max_tokens=120, for_agent="hermes")
        self.assertLessEqual(bundle.estimated_tokens, 120)
        self.assertLessEqual(estimated_tokens(bundle.text), 120)
        self.assertIn("hc:v1:", bundle.text)
        self.assertIn("agents/hermes", bundle.text)

    def test_bundle_redacts_secret_like_snippets_but_keeps_citation(self):
        bundle = self.recall.bundle(self.hive, "credential-like marker", max_tokens=200)
        self.assertIn("[REDACTED]", bundle.text)
        self.assertNotIn("sk-test", bundle.text)
        self.assertIn("knowledge/credential_fixture.md", bundle.text)

    def test_json_output_is_valid_and_stable_keys(self):
        payload = self.recall.query_json(self.hive, "zephyr-honeycomb", limit=1)
        self.assertEqual(set(payload.keys()), {"query", "results", "index"})
        result = payload["results"][0]
        self.assertEqual(
            set(result.keys()),
            {"code", "score", "reason", "citation", "snippet"},
        )
        self.assertEqual(
            set(result["citation"].keys()),
            {"rel_path", "start_line", "end_line", "start_byte", "end_byte", "agent", "kind"},
        )


if __name__ == "__main__":
    unittest.main()
