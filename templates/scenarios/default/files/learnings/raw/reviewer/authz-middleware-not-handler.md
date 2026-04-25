---
date: __DAYS_AGO_5__
agent: reviewer
context: feature-flag admin route was missing requireAdmin on two endpoints
confidence: high
---

# Authz checks belong in middleware, not handlers

## What happened

Audited the new feature-flag admin route. Two endpoints (`POST /flags`
and `DELETE /flags/:id`) were missing the `requireAdmin` middleware
even though the route file imported it. The handlers had handler-level
`if (!user.admin) return 403` checks instead.

## Root cause

The handlers were copy-pasted from a previous PR that pre-dated the
middleware. Nobody re-wired them to use middleware because the
handler-level check "worked."

## The fix

Wire `requireAdmin` at the route level for the whole admin namespace.
Removed the handler-level checks (they were redundant) and added a
lint rule that flags handler-level admin checks.

## Generalizable rule

Authz at the handler level is one refactor away from being deleted.
Middleware is wired at the route level and survives refactors. Any
authz check that lives in a handler is a future authz miss.
