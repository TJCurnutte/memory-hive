# researcher — activity log

Append-only journal. Newest entries at the top.

## __DAYS_AGO_2__

- Cost-optimization report v2 submitted to curator. Two of three
  edits from `coder` integrated. Headline: switching the hot-path
  prompts to the smaller model saves 38% with <1% quality drop.

## __DAYS_AGO_4__

- Re-ran the benchmark with the warmup fix `reviewer` flagged. p99
  dropped from 840ms to 720ms — was ~12% inflated by warmup-in-window.
  Filed the methodology fix as a raw learning.

## __DAYS_AGO_6__

- First draft of the cost-optimization report. Hit a sample-size
  problem: 200 prompts isn't enough to claim quality parity. Pulled
  another 800 from production logs and re-ran.

## __DAYS_AGO_8__

- Spike: does our covering-index rule from `coder` apply to SQLite
  fixtures? Result: yes, but the speedup is only ~8% (vs ~40% on
  Postgres) because SQLite's page cache already covers most reads
  on a small dataset.

## __DAYS_AGO_10__

- Investigated the polling-service memory pattern. Heap profile
  pointed at unclosed connections — handed off to `coder` to fix.
- Wrote up the parallel-test-isolation pattern as a cross-cutting
  observation; suggested promoting to `learnings/distilled/patterns.md`.

## __DAYS_AGO_13__

- Pulled three weeks of chaos-mode logs to characterize our retry
  pathology. Found that retries cluster around the 5-second mark —
  consistent with our backoff curve, but means a single slow
  downstream amplifies into 6x our normal load.
