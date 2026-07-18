#!/usr/bin/env python3
"""Benchmark: recall-bundle token efficiency, recall held constant.

Goal under test: cut the tokens Memory Hive serves per recall by >=20% while
keeping recall the same or better.

Method (honest A/B on identical retrieval):
  * Build a Memory Hive index over a corpus.
  * For each query, compare the CURRENT renderer (compact=False, dedupe=False)
    against the OPTIMIZED renderer (compact=True, dedupe=True).
  * Efficiency is measured at a generous budget so neither bundle truncates —
    the retrieved candidate set is identical, so any token delta is pure
    rendering efficiency, not dropped evidence.
  * Recall is verified two ways:
      - every topic "needle" present in the baseline bundle is still present in
        the optimized bundle (no fact lost), and
      - at a tight budget, the optimized renderer fits >= as many distinct
        topic needles (same-or-better recall under pressure).

The synthetic corpus models how real hives accrue tokens: wrapped Markdown
prose, padded tables, bullet continuations, and the write-back ritual echoing
the same fact across several silos (logs/memory/learnings). The optimization
removes that overhead and the redundant copies, never the underlying fact.
"""

from __future__ import annotations

import argparse
import importlib.util
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# (topic words used as the query, unique needle ref shared by every copy)
TOPICS = [
    ("rate limiting strategy", "kbref-ratelimit-7f3a"),
    ("database migration rollback", "kbref-migration-9c21"),
    ("authentication token refresh", "kbref-authtoken-4d8e"),
    ("cache invalidation policy", "kbref-cacheinval-b16f"),
    ("error retry backoff", "kbref-retrybackoff-2a7c"),
    ("pagination cursor ordering", "kbref-pagination-e5d9"),
]

AGENTS = ["claude", "codex", "cursor", "hermes", "aider", "goose"]


def load_recall() -> Any:
    module_path = REPO_ROOT / "memory_hive_recall.py"
    spec = importlib.util.spec_from_file_location("memory_hive_recall_bench", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fact_paragraph(topic: str, ref: str, agent: str) -> str:
    # A wrapped Markdown paragraph (multiple source lines) stating the fact.
    # Every copy carries `ref` and the topic words; agent filler makes copies
    # near-duplicates rather than exact ones (matches real write-back echoes).
    return (
        f"When handling {topic}, the agreed approach (ref {ref}) is to apply the\n"
        f"documented policy before retrying so behavior stays predictable across\n"
        f"services. Agent {agent} confirmed this during review and noted it should\n"
        f"hold for the {topic} path under load.\n"
    )


def _fact_bullets(topic: str, ref: str) -> str:
    return (
        f"- Key rule for {topic} (ref {ref}): prefer the explicit policy and keep\n"
        f"  the continuation of this bullet on the same logical point so it reads\n"
        f"  cleanly even when wrapped onto several indented lines.\n"
        f"- Secondary note: measure before and after changing {topic}.\n"
    )


def _fact_table(topic: str, ref: str) -> str:
    return (
        f"| aspect            | guidance for {topic}                |\n"
        f"|-------------------|--------------------------------------|\n"
        f"| ref               | {ref}                                |\n"
        f"| default           | apply documented policy first        |\n"
    )


def write_corpus(base: Path, *, echoes: bool = True) -> Path:
    hive = base / "hive"
    files: dict[str, str] = {}
    files["index.md"] = "# Memory Hive\n\nEntry point for the shared hive.\n"

    # Curated knowledge: one authoritative answer file per topic.
    for topic, ref in TOPICS:
        slug = ref.split("-")[1]
        files[f"knowledge/{slug}.md"] = (
            f"# {topic.title()}\n\n"
            + _fact_paragraph(topic, ref, "main")
            + "\n"
            + _fact_bullets(topic, ref)
            + "\n"
            + _fact_table(topic, ref)
        )

    # Each agent silo echoes a subset of the facts (write-back ritual): the same
    # fact lands in the agent's memory.md, log.md, and a raw learning.
    for idx, agent in enumerate(AGENTS if echoes else []):
        owned = [TOPICS[(idx + k) % len(TOPICS)] for k in range(3)]
        ctx = [f"# {agent} context\n\n## Role\n\nWorking agent {agent}.\n"]
        mem = [f"# {agent} memory\n\n## Durable facts\n"]
        logs = [f"# {agent} log\n"]
        for topic, ref in owned:
            mem.append(_fact_bullets(topic, ref))
            mem.append("")
            logs.append(f"2026-06-29 — {agent} reaffirmed {topic} (ref {ref}) after review.\n")
            slug = ref.split("-")[1]
            files[f"learnings/raw/{agent}/2026-06-29-{slug}.md"] = (
                f"---\ndate: 2026-06-29\nagent: {agent}\ncontext: {topic} review\n---\n"
                f"# {topic.title()}\n\n"
                + _fact_paragraph(topic, ref, agent)
                + "\n"
                + _fact_table(topic, ref)
            )
        files[f"agents/{agent}/context.md"] = "\n".join(ctx)
        files[f"agents/{agent}/memory.md"] = "\n".join(mem)
        files[f"agents/{agent}/log.md"] = "\n".join(logs)

    for rel, text in files.items():
        path = hive / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return hive


def _needles_in(text: str) -> set[str]:
    return {ref for _, ref in TOPICS if ref in text}


def run(hive: Path, recall_budget: int, big_budget: int) -> int:
    recall = load_recall()
    recall.build_index(hive, force=True)

    rows: list[dict[str, Any]] = []
    lost_needles = 0
    base_recall_total = 0
    opt_recall_total = 0

    comp_total = dedup_total = 0
    for topic, ref in TOPICS:
        base = recall.bundle(hive, topic, max_tokens=big_budget, compact=False, dedupe=False)
        comp = recall.bundle(hive, topic, max_tokens=big_budget, compact=True, dedupe=False)
        ded = recall.bundle(hive, topic, max_tokens=big_budget, compact=False, dedupe=True)
        opt = recall.bundle(hive, topic, max_tokens=big_budget, compact=True, dedupe=True)
        comp_total += comp.estimated_tokens
        dedup_total += ded.estimated_tokens

        base_needle = ref in base.text
        opt_needle = ref in opt.text
        if base_needle and not opt_needle:
            lost_needles += 1

        # Same-or-better recall under a tight budget.
        base_tight = recall.bundle(hive, topic, max_tokens=recall_budget, compact=False, dedupe=False)
        opt_tight = recall.bundle(hive, topic, max_tokens=recall_budget, compact=True, dedupe=True)
        base_recall_total += len(_needles_in(base_tight.text))
        opt_recall_total += len(_needles_in(opt_tight.text))

        reduction = 100.0 * (base.estimated_tokens - opt.estimated_tokens) / base.estimated_tokens
        rows.append(
            {
                "topic": topic,
                "base_tokens": base.estimated_tokens,
                "opt_tokens": opt.estimated_tokens,
                "reduction": reduction,
                "base_entries": len(base.results),
                "opt_entries": len(opt.results),
                "needle_kept": opt_needle,
            }
        )

    print(f"Corpus hive: {hive}")
    print(f"Efficiency budget (no truncation): {big_budget} tok | recall budget: {recall_budget} tok\n")
    print(f"{'topic':<32} {'base':>6} {'opt':>6} {'cut%':>7} {'entries(b/o)':>13} {'needle':>7}")
    print("-" * 80)
    for r in rows:
        entries = f"{r['base_entries']}/{r['opt_entries']}"
        needle = "yes" if r["needle_kept"] else "NO"
        print(
            f"{r['topic']:<32} {r['base_tokens']:>6} {r['opt_tokens']:>6} "
            f"{r['reduction']:>6.1f}% {entries:>13} {needle:>7}"
        )

    mean_reduction = statistics.mean(r["reduction"] for r in rows)
    total_base = sum(r["base_tokens"] for r in rows)
    total_opt = sum(r["opt_tokens"] for r in rows)
    overall = 100.0 * (total_base - total_opt) / total_base

    comp_cut = 100.0 * (total_base - comp_total) / total_base
    dedup_cut = 100.0 * (total_base - dedup_total) / total_base

    print("-" * 80)
    print(f"mean per-query token cut : {mean_reduction:5.1f}%")
    print(f"overall token cut        : {overall:5.1f}%  ({total_base} -> {total_opt} tokens)")
    print(f"  - compaction only      : {comp_cut:5.1f}%  (formatting overhead removed)")
    print(f"  - dedupe only          : {dedup_cut:5.1f}%  (redundant cross-silo copies)")
    print(f"needles lost (recall)    : {lost_needles}")
    print(f"tight-budget recall      : baseline={base_recall_total}  optimized={opt_recall_total} (distinct needles)")

    recall_ok = lost_needles == 0 and opt_recall_total >= base_recall_total
    goal_ok = overall >= 20.0 and mean_reduction >= 20.0 and recall_ok
    print(f"\nGOAL >=20% token cut with recall maintained-or-better: {'PASS' if goal_ok else 'FAIL'}")
    return 0 if goal_ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hive", help="existing hive content root; default: synthetic corpus")
    parser.add_argument("--recall-budget", type=int, default=500)
    parser.add_argument("--big-budget", type=int, default=20000)
    parser.add_argument(
        "--low-redundancy",
        action="store_true",
        help="synthetic corpus with no cross-silo echoes (isolates compaction)",
    )
    args = parser.parse_args(argv)

    if args.hive:
        return run(Path(args.hive).expanduser().resolve(), args.recall_budget, args.big_budget)
    with tempfile.TemporaryDirectory(prefix="mh-token-bench-") as td:
        hive = write_corpus(Path(td), echoes=not args.low_redundancy)
        return run(hive, args.recall_budget, args.big_budget)


if __name__ == "__main__":
    raise SystemExit(main())
