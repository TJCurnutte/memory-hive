---
date: __DAYS_AGO_3__
agent: solo
context: lru_cache returned stale auth state after a session change
confidence: high
---

# `lru_cache` is a foot-gun on mutable underlying state

## What happened

Auth check returned the pre-logout permission set after a user
explicitly logged out. Repro: log in, log out, hit a protected
endpoint within 30 seconds → still authorized.

## Root cause

Endpoint used `@lru_cache` on a `get_permissions(user_id)` helper.
LRU has no TTL and no invalidation on the auth event. The cache
happily served the stale permission set until process restart.

## The fix

Replaced with a TTL cache (30s) and an explicit invalidation on
auth events. Considered no caching at all — measured first; the
hit rate justified keeping the cache.

## Generalizable rule

`lru_cache` is for pure functions. Anything whose answer can change
without the input changing must use a TTL cache or explicit
invalidation. Treat `lru_cache` on stateful queries as a bug.
