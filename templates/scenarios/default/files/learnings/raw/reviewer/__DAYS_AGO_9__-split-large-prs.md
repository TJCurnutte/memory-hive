---
date: __DAYS_AGO_9__
agent: reviewer
context: spent an hour on a 540-line PR before asking for a split
confidence: medium
---

# Large PRs cost more total reviewer time than the splits they delay

## What happened

Picked up a 540-line PR. Spent an hour walking through it; found two
real issues but missed a third (caught in a later post-mortem). Asked
the author to split it. Came back as three smaller PRs the next day —
each took 15-25 minutes to review and all three landed before the
original would have.

## Root cause

Reviewer attention degrades non-linearly with diff size. Past ~300
lines I am pattern-matching, not reading. Pattern-matching catches
some bugs and silently misses others.

## Generalizable rule

A PR over 300 lines is a request to split, not a request to review.
The author's lost cycle time on the split is less than the reviewer's
lost attention plus the cost of the bug that gets missed.
