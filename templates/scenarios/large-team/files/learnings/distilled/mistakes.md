# Mistakes

Curated learnings promoted from `learnings/raw/`.

## `mktemp` without `-p` assumes `$TMPDIR` is writable

- **Date promoted:** __DAYS_AGO_9__
- **Source:** [learnings/raw/reviewer/mktemp-explicit-dir.md](../raw/reviewer/mktemp-explicit-dir.md)
- **Contributing agent:** reviewer
- **Original date:** __DAYS_AGO_10__
- **Context:** three places shelled out to mktemp without -p

Don't trust environment-controlled paths for state your code needs to
write. If you control a dir, prefer it.
