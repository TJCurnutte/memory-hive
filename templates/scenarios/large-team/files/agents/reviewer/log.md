# reviewer — activity log

## __DAYS_AGO_2__

- Reviewed the workflow-engine refactor. Approved with one comment
  about the lockfile cleanup path on crash.

## __DAYS_AGO_6__

- Found a TOCTOU between lockfile-acquire and write in `coder`'s
  first cut. Asked for an `O_EXCL` create instead.

## __DAYS_AGO_10__

- Audited every place we shell out to `mktemp` — three were not
  using `-p` for an explicit dir, which can break on systems where
  `$TMPDIR` is read-only. Fixed.
