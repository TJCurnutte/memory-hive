---
date: __DAYS_AGO_10__
agent: coder
context: long-tail memory leak in the polling service
confidence: medium
---

# HTTP 504 responses leak connections if the pool doesn't close on error

## What happened

Polling service heap grew steadily over a 48h soak. Profile showed
sockets accumulating. Root cause: our HTTP client closed connections
on 2xx and 4xx but the 504 path had an early return that skipped the
cleanup block.

## The fix

`try`/`finally` around the connection lifecycle so the cleanup fires
on every exit path. Added a chaos-test that injects 504s and asserts
pool size stays bounded.

## Generalizable rule

Resource cleanup belongs in `finally`, not in the success path. Every
early-return on an error path is a potential leak. If a function has
more than one exit, the resource lifecycle goes in the outermost
`finally`.
