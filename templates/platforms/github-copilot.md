# Memory Hive wiring — GitHub Copilot (repo-level)

**Detected marker:** `$PWD/.git/` exists and you opted in with
`MEMORY_HIVE_COPILOT_REPO=1`
**Target file:** `$PWD/.github/copilot-instructions.md`
**Integration:** opt-in auto-inject (per-repo, never global)

GitHub Copilot reads `.github/copilot-instructions.md` at the repository
root. The installer will only wire this file if you explicitly opt in
(`MEMORY_HIVE_COPILOT_REPO=1`) — it's a per-repo decision, so auto-doing
it on every `curl | sh` would be surprising.

When opted in, the installer writes the managed block to
`.github/copilot-instructions.md` in your current working directory.
Markers: `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.
Re-runs are idempotent.

Opt out again with `MEMORY_HIVE_SKIP_GITHUB_COPILOT=1`.

### Why opt-in only

`copilot-instructions.md` is typically committed to your repo and
affects every collaborator's Copilot sessions. That's a team-level
change, not a personal one, so the installer doesn't assume consent.
