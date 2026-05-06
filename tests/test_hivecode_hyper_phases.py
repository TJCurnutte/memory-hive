"""RED tests for HyperRecall phases 3-6: FTS5, incremental update, skill index, cache, and bench."""

from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from hivecode_test_utils import load_json_output, recall_module, run_cli, write_fixture_hive


class HiveCodeHyperPhasesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.hive = write_fixture_hive(self.base)
        self.recall = recall_module()
        self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_query_uses_real_fts5_and_lexical_fallback_reports_truthfully(self):
        fts_payload = self.recall.query_json(self.hive, "zephyr-honeycomb", limit=1)
        self.assertEqual(fts_payload["backend"], "fts5")
        self.assertEqual(fts_payload["fallback"], "none")
        self.assertEqual(fts_payload["results"][0]["reason"], "fts5-term-match")

        lexical_payload = self.recall.query_json(self.hive, "zephyr-honeycomb", limit=1, use_fts=False)
        self.assertEqual(lexical_payload["backend"], "lexical")
        self.assertEqual(lexical_payload["fallback"], "forced")
        self.assertEqual(lexical_payload["results"][0]["reason"], "lexical-term-match")

    def test_incremental_update_skips_unchanged_files_and_indexes_changed_file(self):
        initial = self.recall.stats(self.hive)
        target = self.hive / "agents" / "hermes" / "memory.md"
        target.write_text(target.read_text(encoding="utf-8") + "\n- New incremental token: velocity-raven.\n", encoding="utf-8")
        updated = self.recall.update_index(self.hive)
        self.assertGreaterEqual(updated["skipped_files"], initial["files"] - 1)
        self.assertEqual(updated["changed_files"], 1)
        self.assertEqual(updated["deleted_files"], 0)
        results = self.recall.query(self.hive, "velocity-raven", for_agent="hermes", limit=1)
        self.assertEqual(len(results), 1)
        self.assertIn("velocity-raven", results[0].snippet)

    def test_doctor_reports_stale_and_gc_removes_deleted_files(self):
        deleted = self.hive / "knowledge" / "HUMAN_CONTEXT.md"
        deleted.unlink()
        report = self.recall.doctor(self.hive)
        self.assertFalse(report["ok"])
        self.assertIn("knowledge/HUMAN_CONTEXT.md", report["stale_files"])
        gc = self.recall.gc_index(self.hive)
        self.assertGreaterEqual(gc["removed_files"], 1)
        report_after = self.recall.doctor(self.hive)
        self.assertNotIn("knowledge/HUMAN_CONTEXT.md", report_after["stale_files"])

    def test_bundle_cache_reuses_source_fingerprint_and_invalidates_on_update(self):
        first = self.recall.bundle_json(self.hive, "zephyr-honeycomb", max_tokens=200, cache=True)
        second = self.recall.bundle_json(self.hive, "zephyr-honeycomb", max_tokens=200, cache=True)
        self.assertFalse(first["cache_hit"])
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["source_fingerprint"], second["source_fingerprint"])

        target = self.hive / "knowledge" / "HUMAN_CONTEXT.md"
        target.write_text(target.read_text(encoding="utf-8") + "\ncache invalidation marker\n", encoding="utf-8")
        self.recall.update_index(self.hive)
        third = self.recall.bundle_json(self.hive, "cache invalidation marker", max_tokens=200, cache=True)
        self.assertFalse(third["cache_hit"])
        self.assertNotEqual(second["source_fingerprint"], third["source_fingerprint"])

    def test_skill_index_ranks_memory_hive_and_design_skills(self):
        skills = self.base / "skills"
        (skills / "note-taking" / "memory-hive").mkdir(parents=True)
        (skills / "creative" / "claude-design").mkdir(parents=True)
        (skills / "note-taking" / "memory-hive" / "SKILL.md").write_text(
            "---\nname: memory-hive\ndescription: Memory Hive recall, HyperRecall, TokenFS.\n---\n# Memory Hive\nHyperRecall citation-preserving recall.\n",
            encoding="utf-8",
        )
        (skills / "creative" / "claude-design" / "SKILL.md").write_text(
            "---\nname: claude-design\ndescription: Design HTML artifacts and styled PDF documents.\n---\n# Claude Design\nPDF visual design.\n",
            encoding="utf-8",
        )
        self.recall.build_skill_index(self.hive, skills_root=skills)
        recall_hits = self.recall.query_skills(self.hive, "speed up Memory Hive HyperRecall TokenFS", limit=2)
        self.assertEqual(recall_hits[0]["name"], "memory-hive")
        design_hits = self.recall.query_skills(self.hive, "style a PDF like Neural Forge", limit=2)
        self.assertEqual(design_hits[0]["name"], "claude-design")

    def test_cli_hyper_alias_bench_and_gc(self):
        proc = run_cli(["hyper", "bench", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        payload = load_json_output(proc)
        self.assertEqual(payload["ok"], True)
        self.assertIn("query_ms", payload)
        self.assertIn("bundle_ms", payload)

        (self.hive / "knowledge" / "HUMAN_CONTEXT.md").unlink()
        proc = run_cli(["hyper", "doctor", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        self.assertFalse(load_json_output(proc)["ok"])
        proc = run_cli(["hyper", "gc", "--hive", str(self.hive), "--json"], hive=self.hive, check=True)
        self.assertGreaterEqual(load_json_output(proc)["removed_files"], 1)


if __name__ == "__main__":
    unittest.main()
