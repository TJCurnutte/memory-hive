"""RED tests for HiveCode manifest records and stable code behavior."""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import recall_module, write_fixture_hive


CODE_RE = re.compile(
    r"^hc:v1:[a-z0-9]{2}:(?:[a-z0-9-]+|-):[0-9]{6}:"
    r"[a-z0-9-]+:[a-z0-9]+:[a-z0-9]+(?:~[0-9]+)?$"
)


class HiveCodeManifestAndCodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(Path(self.tmp.name))
        self.recall = recall_module()

    def tearDown(self):
        self.tmp.cleanup()

    def build(self):
        return self.recall.build_index(self.hive, force=True)

    def test_manifest_records_kind_agent_hash_size_mtime(self):
        index = self.build()
        record = index.files["agents/hermes/log.md"]
        self.assertEqual(record.kind, "agent")
        self.assertEqual(record.agent, "hermes")
        self.assertRegex(record.sha256, r"^[0-9a-f]{64}$")
        self.assertGreater(record.size, 0)
        self.assertIsInstance(record.mtime_ns, int)

    def test_rebuild_unchanged_hive_preserves_codes(self):
        first = self.build()
        first_codes = sorted(c.code for c in first.codes)
        second = self.build()
        second_codes = sorted(c.code for c in second.codes)
        self.assertEqual(first_codes, second_codes)

    def test_editing_one_chunk_changes_only_affected_checksum(self):
        first = self.build()
        before = {c.source_key: c.code for c in first.codes}
        log_path = self.hive / "agents/hermes/log.md"
        log_path.write_text(
            log_path.read_text(encoding="utf-8").replace(
                "Froze HiveCode recall specification",
                "Froze HiveCode recall spec with RED tests",
            ),
            encoding="utf-8",
        )
        second = self.build()
        after = {c.source_key: c.code for c in second.codes}
        changed = [key for key, code in before.items() if after.get(key) != code]
        self.assertEqual(len(changed), 1)
        self.assertIn("agents/hermes/log.md", changed[0])

    def test_code_grammar_matches_v1_segments(self):
        index = self.build()
        self.assertGreater(len(index.codes), 0)
        for item in index.codes:
            self.assertRegex(item.code, CODE_RE)


if __name__ == "__main__":
    unittest.main()
