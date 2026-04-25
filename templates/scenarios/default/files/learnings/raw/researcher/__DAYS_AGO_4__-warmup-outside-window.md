---
date: __DAYS_AGO_4__
agent: researcher
context: cost-optimization benchmark had warmup inside the timed window
confidence: high
---

# Benchmark warmup must complete before the timer starts

## What happened

First-cut of the cost-optimization benchmark reported p99 latency of
840ms. `reviewer` flagged the warmup loop was inside the timed window
— first ~50 calls were JIT-cold. Re-ran with warmup-then-time and
p99 dropped to 720ms.

## Root cause

The benchmark harness was written iteratively. Warmup was added
later, in the same loop as the timed calls, because that was the
fastest place to insert it.

## The fix

Two-loop structure: explicit warmup loop (untimed), then a timed
loop. Asserts that warmup ran before timing begins.

## Generalizable rule

Any latency measurement that includes cold-start data is reporting
something other than steady-state latency. State which one you're
measuring; if it's steady-state, the warmup must be outside the
timer.
