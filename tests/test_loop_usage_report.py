"""Tests for the self-iteration loop usage-analytics generator."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import write_fixture_hive

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_report_module():
    module_path = REPO_ROOT / "scripts" / "loop" / "hive_usage_report.py"
    spec = importlib.util.spec_from_file_location("hive_usage_report_under_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LoopUsageReportTests(unittest.TestCase):
    def setUp(self):
        self.report = _load_report_module()
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        write_fixture_hive(self.base)

    def tearDown(self):
        self._tmp.cleanup()

    def test_collect_usage_reports_corpus_and_per_agent(self):
        data = self.report.collect_usage(REPO_ROOT, self.base)

        self.assertGreater(data["corpus"]["files"], 0)
        self.assertGreater(data["corpus"]["chunks"], 0)
        self.assertGreater(data["corpus"]["est_tokens"], 0)

        agents = {row["agent"] for row in data["platforms"]["per_agent"]}
        self.assertIn("hermes", agents)

        # Fixture has one raw learning under learnings/raw/hermes/.
        self.assertGreaterEqual(data["learning_pipeline"]["raw"], 1)
        self.assertTrue(data["health"]["ok"])

    def test_index_refresh_runs_and_is_incremental_on_second_pass(self):
        first = self.report.collect_usage(REPO_ROOT, self.base)
        self.assertIn(first["index_refresh"]["mode"], {"initial-build", "rebuild"})

        second = self.report.collect_usage(REPO_ROOT, self.base)
        self.assertEqual(second["index_refresh"]["mode"], "incremental")

    def test_render_markdown_includes_key_sections(self):
        data = self.report.collect_usage(REPO_ROOT, self.base)
        md = self.report.render_markdown(data)
        self.assertIn("# Memory Hive — Usage Snapshot", md)
        self.assertIn("## Memory footprint per platform / agent", md)
        self.assertIn("## Learning pipeline", md)


if __name__ == "__main__":
    unittest.main()
