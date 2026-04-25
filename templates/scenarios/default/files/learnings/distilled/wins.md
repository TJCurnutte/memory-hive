# Wins

Curated learnings promoted from `learnings/raw/`. Each section cites
its source raw file; raw is the source of truth, distilled is the
reference index. Append-only -- entries are never edited in place.

## Retry-with-backoff needs both a delay cap and an attempt cap

- **Date promoted:** __DAYS_AGO_5__
- **Source:** [learnings/raw/coder/retry-backoff-cap.md](../raw/coder/retry-backoff-cap.md)
- **Contributing agent:** coder
- **Original date:** __DAYS_AGO_6__
- **Context:** shipped retry-with-backoff for /api/v2/webhooks

Capped at 30s per attempt and 7 total attempts. Cut chaos-test pool
amplification from 6x to 1.4x. Pattern: every retry policy needs both
a per-attempt cap and a total-attempt cap.

## Quality-parity claims need at least 1000 samples

- **Date promoted:** __DAYS_AGO_5__
- **Source:** [learnings/raw/researcher/sample-size-1000.md](../raw/researcher/sample-size-1000.md)
- **Contributing agent:** researcher
- **Original date:** __DAYS_AGO_6__
- **Context:** cost-optimization quality claim required more samples than 200

For quality-parity claims, 1000 prompts is the floor. Below that, the
confidence interval is wide enough that a real regression can hide
inside the noise.

## Large PRs cost more total reviewer time than the splits they delay

- **Date promoted:** __DAYS_AGO_8__
- **Source:** [learnings/raw/reviewer/split-large-prs.md](../raw/reviewer/split-large-prs.md)
- **Contributing agent:** reviewer
- **Original date:** __DAYS_AGO_9__
- **Context:** spent an hour on a 540-line PR before asking for a split

A PR over 300 lines is a request to split, not a request to review.
The author's lost cycle time is less than the reviewer's lost
attention plus the cost of bugs that get missed.
