---
date: __DAYS_AGO_10__
agent: reviewer
context: three places shelled out to mktemp without -p
confidence: medium
---

# `mktemp` without `-p` assumes `$TMPDIR` is writable

## What happened

Three call sites used bare `mktemp`. On a customer system where
`$TMPDIR` was a read-only NFS mount, all three failed silently.

## The fix

Pass `-p "$HIVE_DIR/.tmp"` (a directory we control). Falls back to
the default only if the user explicitly clears the override.

## Generalizable rule

Don't trust environment-controlled paths for state your code needs
to write. If you control a dir, prefer it.
