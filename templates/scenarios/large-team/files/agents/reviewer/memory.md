# reviewer — durable memory

## Lessons learned

- **`O_EXCL` is the only race-free way to acquire a lockfile.** Any
  check-then-create has a TOCTOU window.
- **`mktemp` without `-p` assumes `$TMPDIR` is writable.** Always
  pass an explicit directory you control.
