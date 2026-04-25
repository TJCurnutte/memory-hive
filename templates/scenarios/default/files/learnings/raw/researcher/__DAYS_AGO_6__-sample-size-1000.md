---
date: __DAYS_AGO_6__
agent: researcher
context: cost-optimization quality claim required more samples than 200
confidence: medium
---

# Quality-parity claims need at least 1000 samples

## What happened

First draft of the cost-optimization report claimed "<1% quality drop"
based on 200 prompts. Confidence interval was wide enough that the
real drop could have been 4%. Pulled 800 more from production logs;
re-ran; confirmed <1% with a tight interval.

## Generalizable rule

For quality-parity claims, 1000 prompts is the floor. Below that, the
confidence interval is wide enough that a real regression can hide
inside the noise. Larger is better when the data is cheap.

## For curator

Worth promoting to a methodology section in `learnings/distilled/`
or a `knowledge/RESEARCH_METHODOLOGY.md`. Other agents will hit this.
