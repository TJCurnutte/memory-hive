# Changelog

All notable changes to Memory Hive are recorded here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — `feat/dynamic-agents`

### Added

- **Import flow for Claude Code + OpenClaw agents.** Before running the
  fresh-install wizard, `install.sh` scans `~/.claude/agents/` and
  `~/.openclaw/hive/agents/` for pre-existing agents. If any are found it
  offers `[i] import all`, `[s] select`, or `[n] skip and run wizard`.
  Imports auto-seed Role from (1) the source's existing `context.md`
  `## Role` if non-placeholder, else (2) a role template matched to the
  agent's name (coder→coder, security-auditor→reviewer,
  research-analyst→researcher, content-strategist→writer,
  cxaas-specialist→planner), else blank. `log.md` and `memory.md` are
  also copied from the source when the destination is empty — never
  overwriting.
- **Interactive installer wizard.** On first install with a tty, `install.sh`
  asks how many agents you want, collects a name and optional role for each,
  and scaffolds one silo per agent. Non-interactive installs (`curl | sh` in
  CI, `< /dev/null`) skip the wizard and create only the reserved `main/`
  curator silo — behavior is backward compatible.
- **Re-install reconciliation flow.** When existing non-`main` silos are
  detected, the installer offers four choices:
  - `[k]` keep — default; just refresh the shared hive
  - `[a]` add — run the wizard alongside existing agents
  - `[f]` fresh — archive all existing non-`main` silos, then wizard
  - `[s]` select — walk each existing agent, keep or archive
- **Non-destructive archive.** "Fresh" and "select" flows move silos to
  `hive/agents/_archived/YYYY-MM-DD/<name>/`. Agent memory is never deleted.
- **Role templates** at `templates/roles/`: `coder`, `reviewer`,
  `researcher`, `writer`, `planner`, `curator`. One-paragraph role
  descriptions, used by the wizard to seed `context.md`'s `## Role` section.
- **`memory-hive` CLI wrapper.** Single entry point installed alongside the
  other helpers. Verbs: `add <name> [--role <template|path>]`, `list`,
  `archive <name>`, `role <name>` (opens `$EDITOR` on `context.md`),
  `rename <old> <new>`, `help`.
- **`MEMORY_HIVE_REPO` env var.** When set to a local path with a `hive/`
  subdir, `install.sh` copies from there instead of `git clone`ing. Useful
  for development, offline installs, and the test harness.
- **`MEMORY_HIVE_SKIP_CLAUDE_MD` env var.** Lets callers opt out of editing
  `~/.claude/CLAUDE.md`. Used by the test harness; also handy if the user
  manages that file by hand.

### Changed

- **Repo is now generic, product-first.** `README.md`, `HIVE_ARCHITECTURE.md`,
  `hive/index.md`, `hive/registry/AGENTS.md`, `hive/registry/SKILLS_CATALOG.md`,
  `hive/agents/SILO_README.md`, `hive/curator/DECISIONS.md`, and
  `hive/agents/main/log.md` were rewritten to remove the original author's
  personal 13-agent roster (Coder, Vibe Coder, SDR Alpha/Beta, CXaaS
  Specialist, Content Strategist, Security Auditor, etc.). New installs now
  look like their own system, not someone else's dotfiles.
- **`create-agent.sh`** accepts `MH_AGENT_ROLE` (inline text) and
  `MH_AGENT_ROLE_FILE` (path to a role file, typically a `templates/roles/*`
  entry). Existing CLI (`sh create-agent.sh <agent-id>`) is unchanged.

### Removed

- Empty author-specific silo directories (`coder`, `vibe-coder`, `sdr-1`,
  `sdr-2`, `security-auditor`, `cxaas-specialist`, `data-analyst`,
  `research-analyst`, `api-expert`, `web-dev`, `social-media-mgr`,
  `content-strategist`). Only `main/` (Chief of Staff / curator) ships now.
- 83 stray `.md` playbook/skill files that had accumulated under
  `hive/agents/` alongside the silo dirs. They're cross-agent knowledge
  and belong under `hive/knowledge/` or `hive/learnings/`, not as
  siblings of silos. Every fresh install had been copying them into the
  new user's `hive/agents/`.

### Fixed

- Installer re-opens `/dev/tty` when stdin is piped (the `curl | sh` case)
  so interactive prompts work. Falls through cleanly when no tty is
  reachable.

## Why this matters

- **Lower adoption bar.** First-time installers see their own system, not
  someone else's workflow.
- **Faster onboarding.** The wizard guides a new user to a working
  multi-agent setup in under two minutes with no documentation.
- **No surprise data loss.** Re-installing never nukes your memory. Archives
  are preserved under `hive/agents/_archived/`.
- **Add-an-agent is one command.** `memory-hive add <name>` replaces a
  re-run of the installer. `list`, `archive`, and `rename` round out the
  basics.
