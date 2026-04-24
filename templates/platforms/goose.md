# Memory Hive wiring — Goose (Block)

**Detected dir:** `~/.config/goose/` or `~/.goose/`
**Target file:** `~/.goosehints`
**Integration:** auto-inject (managed block)

Goose reads `.goosehints` files for persistent developer-extension
guidance. The priority order Goose checks is:

1. `.goosehints.local` (per-project override)
2. `~/.goosehints` (user-level) ← this is where the installer writes
3. `.goosehints` (per-project)

The installer writes the managed block to `~/.goosehints` between the
`<!-- memory-hive:start -->` / `<!-- memory-hive:end -->` markers.
Re-runs are idempotent, and any content you add outside the markers is
preserved.

Opt out with `MEMORY_HIVE_SKIP_GOOSE=1`.

### Requires the developer extension

`.goosehints` is only read when Goose's developer extension is enabled.
If you've disabled that extension, the hints are inert — enable it in
`~/.config/goose/config.yaml` or via `goose configure`.
