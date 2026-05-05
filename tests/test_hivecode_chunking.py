"""RED tests for HiveCode chunking and citation spans."""

from __future__ import annotations

import tempfile
import unittest

from hivecode_test_utils import byte_slice, recall_module, write_fixture_hive


class HiveCodeChunkingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.hive = write_fixture_hive(__import__("pathlib").Path(self.tmp.name))
        self.recall = recall_module()

    def tearDown(self):
        self.tmp.cleanup()

    def chunks_for(self, rel_path: str):
        return list(self.recall.chunk_file(self.hive / rel_path, hive_root=self.hive))

    def test_chunker_emits_frontmatter_with_exact_span(self):
        chunks = self.chunks_for("learnings/raw/hermes/2026-05-05-visible-pulls.md")
        first = chunks[0]
        self.assertEqual(first.kind, "frontmatter")
        self.assertEqual((first.start_line, first.end_line), (1, 5))
        source = self.hive / "learnings/raw/hermes/2026-05-05-visible-pulls.md"
        self.assertEqual(byte_slice(source, first.start_byte, first.end_byte), first.text.encode("utf-8"))
        self.assertIn("agent: hermes", first.text)

    def test_chunker_tracks_heading_path_for_nested_content(self):
        chunks = self.chunks_for("learnings/raw/hermes/2026-05-05-visible-pulls.md")
        paragraph = next(c for c in chunks if c.kind == "paragraph" and "orchid-anchor" in c.text)
        self.assertEqual(paragraph.heading_path, "Visible Pulls > Nested Topic")

    def test_chunker_groups_wrapped_paragraph_without_bullets(self):
        chunks = self.chunks_for("learnings/raw/hermes/2026-05-05-visible-pulls.md")
        paragraph = next(c for c in chunks if c.kind == "paragraph" and "orchid-anchor" in c.text)
        self.assertIn("across two source lines", paragraph.text)
        bullets = [c for c in chunks if c.kind == "bullet"]
        self.assertTrue(any("Continuation for the first bullet" in c.text for c in bullets))
        self.assertFalse(any("orchid-anchor" in c.text for c in bullets))

    def test_chunker_keeps_fenced_code_block_lossless(self):
        source = self.hive / "learnings/raw/hermes/2026-05-05-visible-pulls.md"
        chunks = self.chunks_for("learnings/raw/hermes/2026-05-05-visible-pulls.md")
        code = next(c for c in chunks if c.kind == "code_block")
        self.assertTrue(code.text.startswith("```bash"))
        self.assertTrue(code.text.rstrip().endswith("```"))
        self.assertEqual(byte_slice(source, code.start_byte, code.end_byte), code.text.encode("utf-8"))

    def test_log_lines_emit_as_single_line_chunks(self):
        chunks = self.chunks_for("agents/hermes/log.md")
        log_lines = [c for c in chunks if c.kind == "log_line"]
        self.assertEqual(len(log_lines), 2)
        self.assertTrue(all(c.start_line == c.end_line for c in log_lines))
        self.assertIn("visible pull baseline", log_lines[0].text)


if __name__ == "__main__":
    unittest.main()
