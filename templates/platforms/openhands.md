# Memory Hive wiring — OpenHands

**Detected dir:** `~/.openhands/`
**Target file:** `~/.openhands/microagents/memory-hive.md`
**Integration:** auto-inject (managed block)

OpenHands stores "microagents" as markdown files under
`~/.openhands/microagents/`. Each microagent enhances the system prompt
with domain-specific knowledge. The installer drops one microagent —
`memory-hive.md` — that tells every OpenHands session how to boot from
the hive.

Markers: `<!-- memory-hive:start -->` / `<!-- memory-hive:end -->`.
Re-runs are idempotent.

Opt out with `MEMORY_HIVE_SKIP_OPENHANDS=1`.

### Check it loaded

In an OpenHands session, microagents show up in the initial context. If
the file is present but not being applied, verify prompt extensions are
enabled in your `config.toml` and that `memory-hive` isn't in the
disabled list.
