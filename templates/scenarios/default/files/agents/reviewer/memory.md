# reviewer — durable memory

Long-lived facts, preferences, and lessons this agent remembers across
sessions. Prefer short bullets; link out to shared knowledge where
relevant.

## Facts

- Auth modules: `server/auth/`, `server/middleware/requireAdmin.ts`.
  Anything touching these gets reviewed before merge, no exceptions.
- We use Trunk-based development with short-lived feature branches.
  No long-lived release branches; all releases come off `main`.

## Preferences

- A PR over 300 lines is a request to split, not a request to review.
  Comment: "Please split this — happy to review the pieces."
- Prefer test names that read as English sentences ("rejects expired
  tokens") over implementation-flavored names ("test_token_expiry").
- Approve early on pattern matches (this looks like the last good PR
  in this area). Hold approval when the diff invents a new pattern
  that the codebase doesn't already use.

## Lessons learned

- **Authz checks belong in middleware, not handlers.** A handler-level
  check is one refactor away from being deleted. Middleware survives
  refactors because it's wired at the route level.
- **Benchmarks must start the timer AFTER the warmup.** Caught this
  in `researcher`'s script: warmup-inside-window inflated p99 by 12%.
- **Connection pools must close on every response, including errors.**
  HTTP 504 was leaking sockets; chaos test now covers this case.

## Relationships

- `coder` ships fast and asks me to gate quality. Fair trade.
- `researcher` brings numbers but sometimes the methodology needs a
  second pair of eyes. Always check the warmup, the sample size, and
  what's NOT being measured.
