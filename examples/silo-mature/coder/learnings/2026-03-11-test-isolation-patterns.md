---
date: 2026-03-11
agent: coder
context: our test suite leaks DB state across workers in parallel mode
confidence: medium
---

# Test isolation across parallel workers

## What happened

In parallel test mode (`pytest -n auto`), intermittent failures in
`test_user_creation` and `test_org_lookup`. Failures didn't reproduce
when running either test alone, only under load with 4+ workers.

## Root cause

A session-scoped fixture (`db_session`) was being reused across tests
in the same worker. One test was committing a row that a later test
then read under a different assumption. Parallelism made the ordering
unpredictable so the failure only surfaced intermittently.

## The fix

Move `db_session` to function scope. Cost: ~15% longer test suite.
Benefit: zero flakes over 50 consecutive runs.

## Generalizable rule

Shared test fixtures must not mutate state. Anything that writes to a
DB, filesystem, or mutable global should be function-scoped.

## For curator

This pattern applies beyond our test suite — any parallel execution
with shared mutable state has the same class of bug. Worth promoting
to `learnings/distilled/patterns.md` if other agents see it elsewhere.
