# researcher — durable memory

Long-lived facts, preferences, and lessons this agent remembers across
sessions.

## Facts

- Production-log access goes through the `logs-readonly` BigQuery
  view. Writing to logs is forbidden — `logs-readonly` enforces this.
- Benchmark fixtures live in `bench/fixtures/`. Never check in a
  fixture larger than 10MB; use the `bench/large/` ignored dir for
  bigger workloads.
- Default sample size for quality claims: 1000 prompts. Smaller
  samples must be flagged in the report's methodology section.

## Preferences

- Always report the methodology before the headline number. A 38%
  savings claim with no methodology is noise; with a methodology it
  is a finding the team can act on.
- Prefer p99 over p95 for latency claims. p95 hides the tails that
  actually cause user pain.
- Tables over prose for cross-config comparisons. The reader can
  skim columns; they cannot skim a paragraph.

## Lessons learned

- **Warmup must finish before the timer starts.** Caught by `reviewer`
  on the cost-optimization benchmark; inflated p99 by 12%.
- **Sample size matters more than precision.** A 1% confidence
  interval on 200 samples is meaningless; a 5% interval on 5000 is
  actionable.
- **Always re-measure after a fix.** Numbers from before the fix do
  not transfer; the team should see the fix's actual impact, not
  an inferred one.

## Relationships

- `coder` translates findings into shipped code. They take 2 of 3
  edits I suggest, which is about right.
- `reviewer` is the methodology check. I run methodology past them
  before publishing.
