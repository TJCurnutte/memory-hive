"""Tests for recall-bundle token efficiency: compaction + near-dup suppression.

Invariant under test: fewer tokens, never fewer query terms or lost facts.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from hivecode_test_utils import recall_module

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


def words(text: str) -> set[str]:
    return {w.lower() for w in WORD_RE.findall(text)}


class CompactSnippetTests(unittest.TestCase):
    def setUp(self):
        self.recall = recall_module()

    def test_preserves_all_query_terms_and_cuts_chars(self):
        raw = (
            "## Heading\n\n"
            "This paragraph is wrapped across\n"
            "several source lines which cost\n"
            "newline tokens in a bundle.\n\n"
            "| aspect   | value    |\n"
            "|----------|----------|\n"
            "| policy   |  applied |\n"
        )
        compact = self.recall.compact_snippet(raw)
        # No query-relevant word is lost.
        self.assertEqual(words(raw), words(compact))
        # And it is strictly smaller (formatting overhead removed).
        self.assertLess(len(compact), len(raw))
        # Table separator row of dashes is gone.
        self.assertNotIn("|----------|", compact)

    def test_preserves_fenced_code_verbatim(self):
        raw = "Intro line.\n\n```python\ndef f(x):\n    return  x +  1\n```\n"
        compact = self.recall.compact_snippet(raw)
        self.assertIn("def f(x):", compact)
        self.assertIn("    return  x +  1", compact)  # indentation/spacing inside code kept

    def test_reflows_wrapped_prose_into_one_line(self):
        raw = "alpha beta\ngamma delta\nepsilon zeta\n"
        compact = self.recall.compact_snippet(raw)
        self.assertEqual(compact, "alpha beta gamma delta epsilon zeta")

    def test_compaction_never_increases_length(self):
        # A token-efficiency pass must not inflate any snippet, including
        # already-tight tables with no cell padding.
        samples = [
            "|a|b|\n|c|d|",
            "| padded | row |\n|--------|-----|\n| x | y |",
            "## H\n\nwrapped\nprose\nlines\n\n- bullet\n  continuation\n",
            "```\n| not a table |\n--- not sep ---\n```",
            "",
        ]
        for s in samples:
            self.assertLessEqual(len(self.recall.compact_snippet(s)), len(s), msg=repr(s))


class BundleDedupeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.recall = recall_module()
        self.hive = Path(self.tmp.name) / "hive"
        ref = "kbref-bucket-9988"
        fact = (
            "When handling rate limiting the agreed approach (ref {r}) is a token\n"
            "bucket per client key with the documented refill policy applied first.\n"
        )
        # Same fact echoed across three silos (write-back ritual / cross-agent).
        for agent in ("claude", "codex", "cursor"):
            p = self.hive / "agents" / agent / "memory.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# {agent} memory\n\n## Facts\n\n" + fact.format(r=ref), encoding="utf-8")
        # A distinct, unrelated fact that must never be dropped.
        distinct = self.hive / "agents" / "hermes" / "memory.md"
        distinct.parent.mkdir(parents=True, exist_ok=True)
        distinct.write_text(
            "# hermes memory\n\n## Facts\n\n"
            "Rate limiting alerts (ref kbref-alert-1212) page oncall when the "
            "bucket drains so capacity issues surface quickly.\n",
            encoding="utf-8",
        )
        self.recall.build_index(self.hive, force=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dedupe_drops_near_duplicates_but_keeps_the_fact(self):
        base = self.recall.bundle(self.hive, "rate limiting token bucket refill", max_tokens=20000, compact=False, dedupe=False)
        opt = self.recall.bundle(self.hive, "rate limiting token bucket refill", max_tokens=20000, compact=True, dedupe=True)

        self.assertLess(len(opt.results), len(base.results))  # redundant copies suppressed
        self.assertLess(opt.estimated_tokens, base.estimated_tokens)  # fewer tokens
        self.assertIn("kbref-bucket-9988", opt.text)  # the fact survives (recall kept)

    def test_distinct_fact_is_not_dropped(self):
        opt = self.recall.bundle(self.hive, "rate limiting bucket", max_tokens=20000, compact=True, dedupe=True)
        # Both the policy fact and the distinct alert fact remain present.
        self.assertIn("kbref-bucket-9988", opt.text)
        self.assertIn("kbref-alert-1212", opt.text)

    def test_default_bundle_is_optimized(self):
        default = self.recall.bundle(self.hive, "rate limiting token bucket refill", max_tokens=20000)
        raw = self.recall.bundle(self.hive, "rate limiting token bucket refill", max_tokens=20000, compact=False, dedupe=False)
        self.assertLessEqual(default.estimated_tokens, raw.estimated_tokens)


if __name__ == "__main__":
    unittest.main()
