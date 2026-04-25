# Decisions

Audit trail of every curation decision made by the curator.

---

### __DAYS_AGO_13__ -- Promoted `learnings/raw/coder/parallel-test-isolation.md` -> `learnings/distilled/patterns.md`
- **Decision:** Append summary + backlink to patterns.md.
- **Reasoning:** Promoted via `memory-hive promote`; raw entry retained as source of truth.
- **Agents involved:** coder
- **Outcome:** Distilled section "Test isolation across parallel workers" written; raw file left in place.

### __DAYS_AGO_9__ -- Promoted `learnings/raw/coder/connection-pool-504.md` -> `learnings/distilled/mistakes.md`
- **Decision:** Append summary + backlink to mistakes.md.
- **Reasoning:** Pattern recurrence — this is the second connection-leak class bug we've shipped this quarter.
- **Agents involved:** coder, reviewer
- **Outcome:** Distilled section "HTTP 504 responses leak connections..." written; chaos-test added to prevent regression.

### __DAYS_AGO_8__ -- Promoted `learnings/raw/reviewer/split-large-prs.md` -> `learnings/distilled/wins.md`
- **Decision:** Append summary + backlink to wins.md.
- **Reasoning:** Reviewer-side win with clear before/after numbers.
- **Agents involved:** reviewer
- **Outcome:** Distilled section "Large PRs cost more total reviewer time..." written.

### __DAYS_AGO_5__ -- Promoted `learnings/raw/coder/retry-backoff-cap.md` -> `learnings/distilled/wins.md`
- **Decision:** Append summary + backlink to wins.md.
- **Reasoning:** Direct, measurable shipping win. Pattern applies broadly to any retry policy.
- **Agents involved:** coder
- **Outcome:** Distilled section "Retry-with-backoff needs both a delay cap..." written.

### __DAYS_AGO_5__ -- Promoted `learnings/raw/researcher/sample-size-1000.md` -> `learnings/distilled/wins.md`
- **Decision:** Append summary + backlink to wins.md.
- **Reasoning:** Methodology bar that should bind future research work.
- **Agents involved:** researcher
- **Outcome:** Distilled section "Quality-parity claims need at least 1000 samples" written.

### __DAYS_AGO_4__ -- Promoted `learnings/raw/reviewer/authz-middleware-not-handler.md` -> `learnings/distilled/patterns.md`
- **Decision:** Append summary + backlink to patterns.md.
- **Reasoning:** Security pattern with a concrete near-miss; high signal.
- **Agents involved:** reviewer
- **Outcome:** Distilled section "Authz checks belong in middleware, not handlers" written.

### __DAYS_AGO_3__ -- Promoted `learnings/raw/coder/timezone-test-bug.md` -> `learnings/distilled/mistakes.md`
- **Decision:** Append summary + backlink to mistakes.md.
- **Reasoning:** Common foot-gun, worth surfacing for future agents.
- **Agents involved:** coder
- **Outcome:** Distilled section "Naive datetime.now() flakes across timezones" written; lint rule shipped.

### __DAYS_AGO_3__ -- Promoted `learnings/raw/researcher/warmup-outside-window.md` -> `learnings/distilled/patterns.md`
- **Decision:** Append summary + backlink to patterns.md.
- **Reasoning:** Methodology pattern that applies to every benchmark we run.
- **Agents involved:** researcher, reviewer
- **Outcome:** Distilled section "Benchmark warmup must complete before the timer starts" written.
