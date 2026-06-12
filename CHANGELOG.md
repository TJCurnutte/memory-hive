# Changelog

All notable changes to Memory Hive are recorded here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.7.0] — 2026-06-12 — `Clean exits`

### Added

- New `memory-hive uninstall [--apply]` verb: surgically unwires every
  integration the installer created — managed blocks out of all 17
  platform config files (user content preserved; wholly-installer-owned
  files removed), memory-hive entries out of `~/.claude/settings.json`
  and `~/.cursor/hooks.json` (user entries preserved), the Agent Skill,
  and PATH shims pointing at the install. Dry-run by default; hive data
  and the install dir are never touched (the receipt ends with the one
  manual `rm -rf` for a full purge). CI smoke covers user-content
  preservation, JSON cleanup, shim removal, and idempotency.

## [1.6.1] — 2026-06-12 — `Self-update no longer eats itself`

### Fixed

- `memory-hive update` could crash mid-run with phantom syntax errors
  ("syntax error near unexpected token") and leave a half-applied
  update. Cause: the installer copied `install.sh` and `memory-hive`
  over themselves in place while those very files were executing (the
  PATH shim is a symlink to the same inode), so the running interpreter
  read the new, longer file at old byte offsets. The recent releases
  grew both files enough to make this near-deterministic. Fixes:
  - all helper installs and hook renders now stage to a temp file and
    `mv` into place — rename keeps the old inode readable for running
    processes;
  - `update.sh` executes the installed installer from a temp copy,
    never from the path being refreshed;
  - new CI step installs, then self-updates from a deliberately
    offset-shifted upstream copy and asserts the run completes and the
    refreshed CLI works (both the direct and the `update.sh` wrapper
    paths).
  Affected machines recover with one
  `curl -fsSL .../install.sh | sh` (or a second `memory-hive update`,
  which is byte-identical and therefore safe); agent silos were never
  touched — the crash happened after the preserve/restore step.

## [1.6.0] — 2026-06-12 — `Cursor falls in line`

### Added

- Cursor harness hooks, wired into `~/.cursor/hooks.json` (version 1) at
  install time — enforcement parity with Claude Code: a `stop` hook
  replies once with a `followup_message` when a completed conversation
  has no fresh dated line in the agent's `log.md` (Cursor's `loop_count`
  is the loop guard; aborted/error runs and short transcripts exempt),
  and a `sessionEnd` hook feeds `hive/raw/sessions/` through
  `memory-hive capture` (model + workspace). Fail-open everywhere; the
  JSON merge touches only entries pointing at our `hooks/cursor-*.sh`
  scripts and refuses malformed files. Opt out with
  `MEMORY_HIVE_SKIP_CURSOR_HOOKS=1` (or `MEMORY_HIVE_SKIP_CURSOR=1` for
  all Cursor wiring); runtime kill switch `MEMORY_HIVE_HOOKS_DISABLE=1`.
  New doctor check (4f) and CI smoke for the merge (idempotency,
  user-entry preservation) and all stop/sessionEnd hook paths.

## [1.5.0] — 2026-06-12 — `The hive speaks MCP`

### Added

- MCP server: `memory-hive mcp` serves the hive over the Model Context
  Protocol (stdio, stdlib-python only — same dependency envelope as
  HyperRecall). Any MCP client (Claude Desktop/Code, Cursor, Goose,
  GitHub Copilot, ...) gets native tools — `ask_hive` (ranked, cited
  retrieval), `hive_log`, `hive_learn`, `hive_capture`, `hive_guide` —
  with no boot block at all. `memory-hive mcp --config` prints the
  ready-to-paste client config with the install's real paths. The helper
  ships to `~/.memory-hive/memory_hive_mcp.py`; doctor checks it (4e);
  CI smoke-tests initialize/list/call over stdio.
- Ambient workstream capture: `memory-hive capture "<event>" [--source
  <name>] [--agent <id>]` appends timestamped events to
  `hive/raw/<source>/YYYY-MM-DD.md` (Tier 1, append-only, searchable via
  query/recall, distilled later by the curator). A new Claude Code
  SessionEnd hook feeds the stream automatically — memory forms even
  when a session never ran the ritual. Same fail-open contract as the
  other hooks.

## [1.4.0] — 2026-06-11 — `Ritual as commands`

### Added

- The release workflow gained a `workflow_dispatch` path (version +
  optional sha): it creates the tag via the API and publishes the same
  changelog-backed release in one run — for environments that can push
  branches but not tag refs. Tag-push behavior is unchanged.
- New write-back verbs that make the task-end ritual executable on every
  platform instead of described in prose: `memory-hive log "<what you
  did>"` appends the dated line to the agent's silo log, and `memory-hive
  learn "<imperative rule>" --context "<one line>" [--kind ...]
  [--confidence ...] [--body <file>|-]` writes a raw learning to the
  canonical `learnings/raw/<id>/YYYY-MM-DD-<slug>.md` path with
  frontmatter that passes `memory-hive lint` by construction (and runs
  lint on the new file as a receipt). Both honor `--agent` /
  `MEMORY_HIVE_AGENT_ID`. This removes the biggest cross-model failure
  mode — hand-formatted paths, dates, and frontmatter — for Codex,
  Hermes, Cursor, Gemini CLI, and every other wired tool equally.

### Changed

- The managed boot block's task-end ritual now instructs agents to run
  `memory-hive log` / `memory-hive learn` instead of hand-writing files;
  the guide's Workflow 3 leads with the verbs (file format remains
  documented as the underlying contract); the Claude Code Stop hook's
  nudge now cites the exact `memory-hive log` command to run.

## [1.3.0] — 2026-06-09 — `Memory everywhere, enforced`

### Added

- Claude Code harness hooks, wired into `~/.claude/settings.json` at
  install time: a `SessionStart` hook injects a token-budgeted hive bundle
  (plus a `memory-hive guide` pointer) into every new session, and a `Stop`
  hook blocks a finishing session at most once when the task-end ritual has
  not run (no fresh dated line in the agent's `log.md`). The boot contract
  becomes mechanical instead of prompt-compliance. Scripts ship rendered to
  `~/.memory-hive/hooks/`; the JSON merge is python3-based, idempotent
  (entries carry a `# memory-hive` marker), and never touches user-authored
  hooks or malformed settings files. Loop-guarded via `stop_hook_active`,
  trivial sessions exempt, every failure path fails open. Opt out at
  install with `MEMORY_HIVE_SKIP_CLAUDE_HOOKS=1`, mute at runtime with
  `MEMORY_HIVE_HOOKS_DISABLE=1`, retarget the silo with
  `MEMORY_HIVE_AGENT_ID`. `memory-hive doctor` checks the wiring (4d) and
  CI smoke-tests merge idempotency, user-hook preservation, and all three
  Stop-hook paths.
- New `memory-hive guide [topic]` verb: prints the platform-neutral
  operating guide (path map, hydrate/retrieve/write-back workflows, lane
  rules, curator loop, troubleshooting) rendered with the install's real
  paths. Topics narrow output to one section:
  `paths|id|hydrate|retrieve|write|lanes|curate|health`. This is the
  progressive-disclosure path for every platform — any agent that can run
  a shell pulls full memory guidance on demand instead of carrying it in
  every session.
- New canonical guide source at `templates/guide.md`, shipped unrendered to
  `~/.memory-hive/templates/guide.md`. The Claude Code Agent Skill body is
  assembled from this same file at install time (frontmatter head +
  guide body), so the skill and the cross-platform guide cannot drift.
- The managed boot block now ends with a `### Going deeper` pointer to
  `memory-hive guide`, so all auto-injected platforms (Cursor, Codex,
  Gemini CLI, Goose, Warp, Amp, OpenCode, ...) advertise the on-demand
  guide, not just Claude Code.
- `memory-hive doctor` warns when the shipped guide template is missing
  (it is load-bearing for `memory-hive guide` on every platform).
- Shipped a native Claude Code Agent Skill template at
  `templates/skills/memory-hive/SKILL.md`. The installer renders
  `${HIVE_DIR}` / `${INSTALL_DIR}` placeholders to real paths and writes the
  result to `~/.claude/skills/memory-hive/SKILL.md` whenever `~/.claude/`
  exists. The unrendered template is also copied to
  `~/.memory-hive/templates/skills/memory-hive/SKILL.md` for inspection.
  Re-installs overwrite the skill file in place (whole-file managed; YAML
  frontmatter is the contract, no start/end markers needed).
- Added `MEMORY_HIVE_SKIP_CLAUDE_SKILL=1` env var to opt out of the Agent
  Skill installation only, leaving the managed `CLAUDE.md` block intact.
  `MEMORY_HIVE_SKIP_CLAUDE_CODE=1` (and its legacy alias
  `MEMORY_HIVE_SKIP_CLAUDE_MD=1`) now skips both the block and the skill.
- Extended `memory-hive doctor` to check that
  `~/.claude/skills/memory-hive/SKILL.md` exists and references the current
  install directory, with a re-install hint when the check fails.
- Added CI smoke coverage for skill template rendering, doctor skill check,
  and the new skip-var behavior.

### Fixed

- The managed boot block's task-end ritual now teaches the canonical raw
  learning layout (`learnings/raw/<agent-id>/YYYY-MM-DD-<slug>.md`) and a
  frontmatter example that includes the lint-required `confidence` field.
  The previous flat-path example (`learnings/raw/<agent-id>-<slug>.md`,
  no `confidence`) produced files that failed `memory-hive lint` on both
  the `agent:`-matches-parent-directory rule and the required-field rule.
- The boot block's lane-keeping rule now scopes shared-pool writes to the
  agent's own subdir (`learnings/raw/<your-agent-id>/`), matching how
  lint, `promote`, and `stale` actually resolve ownership.

### Changed

- Documented the block-vs-skill positioning in `INTEGRATION.md`,
  `templates/platforms/claude-code.md`, and `README.md`: the managed
  `CLAUDE.md` block is the always-on boot contract; the Agent Skill is the
  on-demand depth layer (progressive disclosure, invocable as `/memory-hive`).

## [1.2.1] — 2026-05-13 — `Incremental recall update proof`

### Fixed

- Reworked `memory-hive recall update` so normal single-file memory/log writeback updates only changed or deleted markdown files instead of falling back to a full SQLite/FTS rebuild.
- Preserved unchanged file rows and citations during update, while keeping `files`, `chunks`, `codes`, `tokens`, `sketches`, and FTS rows coherent for changed files.
- Added regression coverage that fails if `update_index()` calls full `build_index()` for single-file append/delete cases.

### Added

- Added `scripts/validate_incremental_update_1000.py`, a sandbox proof harness that runs append → update → query loops while monkeypatching full rebuilds to fail.
- Added `docs/INCREMENTAL_RECALL_UPDATE.md` with the proof contract, regression gate, and local 1000-loop benchmark snapshot.

## [1.2.0] — 2026-05-11 — `Install-once status/update UX`

### Added

- Added a simplified day-one command surface: bare `memory-hive` now opens the one-screen status receipt instead of dumping the full command catalog.
- Added `memory-hive status` as the explicit health receipt for install path, hive path, active silo count, recall helper/index state, stale raw-learning count, and last maintenance timestamp.
- Added `memory-hive maintain` as the local periodic maintenance wrapper. It refreshes registry/citations, builds or updates the HyperRecall index, runs the built-in Optimizer pass, and records `.last-maintained`.
- Added `memory-hive update` as the normal public refresh command. It delegates to the safe updater, preserves agent silos, refreshes shared/tool files, and lets install/update run quiet maintenance afterward.
- Added user-facing `memory-hive recall "query text"` so recall can be used directly without asking users to learn `recall query` or manually build the index first.
- Added draft release notes at `docs/RELEASE_NOTES_SIMPLIFIED_UX.md` covering headline, motivation, user-visible changes, compatibility, migration notes, issue #25, and verification targets.

### Changed

- The installer now runs `memory-hive maintain --quiet` best-effort after registering silos, so first install/update leaves registry/citations and the recall speed index ready without extra copy-paste commands.
- `memory-hive help` is now intentionally small and points normal users to `status`, `update`, optional `add`, `search`, and direct `recall`. The full command catalog moved behind `memory-hive help --advanced`.
- README onboarding now presents Memory Hive as install-once plus periodic update/maintenance, not a pile of separate health, recall, lint, digest, stale, and curator commands.
- README command tables now separate the daily public surface from advanced/debug/curator verbs, with a new "What runs automatically now" section explaining which plumbing is still available behind the wrapper.
- `update.sh` usage now names `memory-hive update` as the preferred public path while preserving the direct script and curl forms for automation.

### Fixed

- Fixed the PATH-shim HyperRecall helper bug reported in issue #25. Recall no longer resolves `memory_hive_recall.py` from `$(dirname "$0")`, because `$0` may point at `~/.local/bin` or another shim directory. It now resolves helpers from the detected install directory first, with repo-checkout fallback for tests/dev.
- Recall queries and bundles now build/update the HyperRecall index automatically when the index is missing or stale enough for the update path, reducing fresh-install failures and removing the need for `memory-hive recall build --json` during onboarding.

## [1.1.1] — 2026-05-07 — `Prompt Optimizer addon contract`

### Added

- Added the Prompt Optimizer addon spec at `docs/PROMPT_OPTIMIZER.md`, defining the Memory Hive-owned route from raw operator prompt → context pull → internal work order → verification → write-back.
- Added the planned `memory-hive prompt classify|optimize|questions|bundle` command contract, including the JSON work-order shape and the exact three-question clarification rule.
- Added README positioning for Prompt Optimizer as a Memory Hive addon layered on top of silos, shared hive context, distilled learnings, and HyperRecall bundles.

### Changed

- README now lists Prompt Optimizer in the capability table and project docs without presenting it as a separate product surface.

## [1.1.0] — 2026-05-06 — `HyperRecall TokenFS speed layer`

### Added

- Added the v1.1 HyperRecall / TokenFS recall engine as a built-in Memory Hive capability through `memory-hive recall`, with `hyper` as an alias.
- Added a local-first SQLite/FTS5 HiveCode index with stable citation codes, source line spans, stale-file detection, incremental update, GC, bundle cache, benchmark output, and skill-index routing.
- Added `memory_hive_recall.py` to the installed helper set so the speed layer works from the normal `memory-hive` terminal command after install/update.
- Added the deep plan PDF at `docs/Memory-Hive-HyperRecall-TokenFS-Plan.pdf`.

### Changed

- README onboarding now includes visible verification steps: `memory-hive doctor`, `memory-hive recall build --json`, and `memory-hive recall doctor --json`.
- README and help text now describe detected agent-platform verification on screen and clarify that installs preserve local hive data unless update/sync mode is explicitly used.

## [0.4.1] — 2026-05-05 — `critical per-turn hive pulls`

### Fixed

- Clarified the managed Memory Hive boot block so agents re-pull the smallest
  relevant hive slice before every non-trivial, cross-session, or operational
  prompt/task — not only once at process startup.
- Documented visible/auditable hive pulls as the default for human-in-the-loop
  sessions, preventing agents from silently answering from stale prompt context.
- Updated README, architecture, integration, Hermes, and Codex wiring docs to
  describe the same pull-memory → work → write-back loop.

## [0.4.0] — 2026-05-05 — `public README + semver release cleanup`

### Changed

- Replaced the GitHub README header with the canonical transparent Hive mark from `assets/hive-mark.png`.
- Restored public releases to readable semver tags such as `v0.4.0` instead of generated commit-hash release cards.
- Repositioned Memory Hive as the public home for the Hive memory layer: local-first Markdown memory, private agent silos, shared curated knowledge, and one POSIX CLI.
- Reworked the README around product clarity, quick start, demo data, the memory loop, supported tools, and practical command paths.
- Absorbed the old HiveOptimizer safety workflow into Memory Hive: checkpoint before apply-mode optimization, inventory before pruning, archive before delete, and routing/model-spend audits as inputs to the optimizer loop.
- Folded Optimizer into Memory Hive as `memory-hive optimize` / `optimizer`, a built-in health + curation + digest + stats loop with optional built-in routing report output.
- Documented Optimizer as an internal maintenance workflow rather than a separate product surface.

## [0.3.2] — 2026-04-28 — `memory lifecycle governance`

### Added

- **Per-turn memory hydration pattern** documented in the architecture and
  onboarding docs.
  Agents now read a compact, ranked `hive-bundle` slice on boot instead of
  replaying every historical file. This improves continuity while keeping
  context windows small.

- **Lifecycle state model for memory records** with explicit statuses:
  `active`, `superseded`, and `deprecated`.
  Conflict/overwrite handling is now documented with timestamp, confidence,
  and supersession rules to reduce stale-memory resurfacing.

- **Memory adapter contract** published at
  [`MEMORY_ADAPTER_CONTRACT.md`](MEMORY_ADAPTER_CONTRACT.md), including:
  required methods (`query`, `ingest`, `snapshot`, `export/import`, `health`),
  schema expectations, required env, and capability matrix.

- **Migration safety contract** added to `MIGRATION.md` with dry-run flows,
  import conflict strategies, and secret-by-default safety checks.

- **Hermes crash-recovery companion example**
  ([`examples/hermes-crash-recovery/`](examples/hermes-crash-recovery/)).
  Documents a machine-local `SESSION.md` / `ACTIVITY.md` / `PENDING.md` /
  `DECISIONS.md` safety net for Hermes-style daily-driver agents, plus a
  pointer from the Hermes platform integration doc.

### Changed

- `INTEGRATION.md`, `MIGRATION.md`, `HIVE_ARCHITECTURE.md`, and `README.md`
  now cross-link the new governance model so onboarding and integration teams
  use the same model.

## [0.3.1] — 2026-04-25 — `audit pass + Hive Swarm interop`

### Fixed (audit pass — PRs #21 + #22 + follow-ups)

- **`mh_seed` shipped lint-failing templates.** Bundled scenario raw
  learnings used bare slug filenames; running `memory-hive lint --strict`
  (or `memory-hive curate`) on a freshly-seeded hive surfaced 9 warnings
  per scenario. Renamed 16 templates across all three scenarios to use
  the `__DAYS_AGO_N__` substitution convention so dates match
  frontmatter and `lint --strict` passes clean.
- **`mh_watch` was bash-only on Linux.** The fswatch branch used
  `read -r -d ''` which dash (Ubuntu's `/bin/sh`) does not support.
  Switched to newline-delimited reads — works under both bash and dash.
- **`check-compliance.sh` TOCTOU.** Used predictable `/tmp/.mh-lane.$$`
  temp paths — symlink-attack vector and PID-recycle bug. Switched to
  `mktemp`.
- **Architecture documentation drift.** `HIVE_ARCHITECTURE.md` and
  README ASCII diagram described a `DRAFT.md` queue between agents and
  the curator — but the shipped 0.2.0/0.3.0 verbs (`promote`, `dedup`,
  `confidence`, `curate`) bypass it. Rewrote the Curation Loop and Task
  Completion Flow sections so each step names the verb that performs
  it. The legacy file classifier still recognizes `DRAFT.md` if present
  — no behavior change for anyone who already had one.
- **Six docs-audit fixes** across README, CHANGELOG, CONTRIBUTING,
  MIGRATION reconciling verb counts (28), platform counts (23),
  category counts (3 not 4), legacy env-var references
  (`MEMORY_HIVE_SKIP_CLAUDE_MD` → `MEMORY_HIVE_SKIP_CLAUDE_CODE` plus
  per-platform vars), and the repo-layout tree (added `assets/`,
  `scripts/`, `examples/`, `templates/platforms/`,
  `templates/scenarios/`).
- **Site SEO**: production HTML now emits a full OG/Twitter meta-tag
  set with the v0.2.0 OG card image, canonical URL, and
  `metadataBase`. Anything sharing the URL on Slack/X/LinkedIn now
  renders properly.
- **8 assorted shell-portability nits** caught by ruff/shellcheck:
  cleanup of dead code, robust temp-file handling, consistent quoting.

### Added

- **Hive Swarm interop note** in `templates/platforms/hermes.md`. The
  hardware-aware swarm controller is treated as a compute layer adjacent to
  Memory Hive's memory layer. The docs explain how to mount the hive across
  a multi-machine mesh, namespace silos by hostname, and use
  `memory-hive bundle --for <agent>` to ship context to remote workers.

## [0.3.0] — 2026-04-25 — `autonomous curator + onboarding`

### Added — 5 new verbs that close the agent self-loop

A second wave of parallel feature work shipped five more CLI verbs.
They turn the curator loop from "agents write, human reviews" into
"agents write, agents reflect, system suggests, human ratifies."

- **`memory-hive curate [--dry-run | --apply]`** — Autonomous one-pass
  curator. Chains `dedup` → `confidence` → `promote` → `lint --strict`
  → `stale` and prints a single summary line: `X clusters need
  attention, Y promotions ready, Z lint violations, N stale items`.
  Default is dry-run (suggest only). `--apply` runs `mh_promote` for
  every promotion-ready cluster (3+ aligned high-confidence raw
  learnings). Pure orchestration over existing verbs — no
  reimplementation, so cluster keys and kind-aliasing stay aligned
  across `dedup`, `confidence`, and `promote`.

- **`memory-hive conflicts [--agent <name>] [--strict] [--write]`** —
  Surfaces raw learnings that contradict each other. Three
  deterministic signals (no LLM in the loop): lexical antonym pairs
  in body text (always/never, fix/broken, works/fails, etc.),
  frontmatter `kind:` mismatch (one says `kind: win`, another `kind:
  mistake` on the same topic), confidence high-vs-low split.
  `--write` stages a stub block in `curator/CONFLICTS.md` for the
  curator to resolve per `HIVE_ARCHITECTURE.md`.

- **`memory-hive reflect <agent> [--days N] [--write] [--raw]`** —
  Agent self-reflection. Distills an agent's recent log activity into
  a memory.md addendum. Pure-shell theme detection: tokenize log
  bodies, credit each token once per entry (DF-style — three different
  entries each mentioning a word once is a pattern, one ranty entry
  using it twelve times is not), surface words hitting 3+ distinct
  entries as themes with citations. Lets agents close their own loop
  without waiting for the curator.

- **`memory-hive bundle [--for <agent>] [--max-tokens N] [--out <file>]`** —
  Concatenates the canonical hive surfaces into a single
  prompt-injection-ready markdown blob. Section ordering is
  canon-first (`index.md` → `registry/AGENTS.md` → knowledge →
  distilled → agent silo last) so prompt overflow drops the
  least-portable content. `.baseline-installed` honored at file
  granularity — unedited installer scaffolding doesn't pollute the
  bundle. Footer (chars/files/tokens) goes to stderr so
  `bundle | consumer` works cleanly.

- **`memory-hive seed [--scenario <name>] [--dry-run] [--force]`** —
  Populate a fresh hive with synthetic but realistic content so the
  observability verbs (`tail`, `digest`, `confidence`, `stats`,
  `query`) produce non-trivial output the moment a new user finishes
  installing. Bundled scenarios: `default` (3-agent team — coder,
  reviewer, researcher — with two weeks of activity, 9 raw learnings,
  3 distilled files, populated `DECISIONS.md` and `PROJECTS.md`),
  `solo` (1 agent), `large-team` (5 agents). Refuses to run against
  a non-empty hive unless `--force`; `--dry-run` lists what would be
  written. Date markers (`__DAYS_AGO_N__`) substituted at seed time
  so activity always looks recent. Templates live under
  `templates/scenarios/<name>/`.

### Changed

- **`install.sh`** now copies `templates/scenarios/` alongside
  `templates/roles/` and `templates/platforms/`, so the seed verb
  works post-install without cloning the repo.

## [0.2.0] — 2026-04-24 — `multi-platform + curator loop`

### Added — Curator + observability verbs (13 new commands)

A wave of parallel feature work added thirteen new CLI verbs that close the
loop between agent contributions and curator promotion. All are pure shell,
all ship a CI smoke test, all read from the existing two-layer architecture
without changing it.

- **`memory-hive tail [-n N] [--silo <name>] [--since <YYYY-MM-DD>]`** —
  Like `tail -f` for the hive (non-streaming). Prints the N most recent
  hive writes with key content extracted per kind: log/DECISIONS/CONFLICTS
  show the newest dated heading + first paragraph; memory/context show the
  tail; learnings show H1 + frontmatter. Use `watch` for the streaming view.

- **`memory-hive promote <raw-file> [--into <name>] [--title <text>] [--dry-run]`** —
  One-command curator workflow. Reads a raw learning, appends a summary
  with backlink to a distilled file, and logs the decision in
  `curator/DECISIONS.md`. Raw file stays untouched as source of truth.
  `--into` defaults to inferring from frontmatter `kind:`.

- **`memory-hive confidence`** — Clusters raw learnings by normalized title
  and suggests upgrades when a cluster crosses an architecture threshold
  (3 aligned low → medium, 3 aligned medium → high). Suggest-only; curator
  decides what to promote.

- **`memory-hive tag <file> <tag1> [tag2 ...]`** + **`memory-hive tags [--agent <name>] [--tag <name>]`** —
  Lightweight topical tagging for learning files. `tag` adds to YAML
  frontmatter (lowercase, dashes, 2-24 chars, sorted alphabetically,
  deduplicated). `tags` lists every tag in the hive with file count;
  `--tag <name>` lists files using a tag; `--agent <name>` limits the scan
  to one silo. Lets topical clusters emerge so the curator can spin up new
  `learnings/distilled/<topic>.md` files when a tag passes a threshold.

- **`memory-hive stale [--days N] [--agent <name>] [--count]`** + doctor
  integration — Surfaces raw learnings >N days old (default 7) with no
  curator decision. `doctor` lists top 5 inline; auto-escalates to a
  warning when count exceeds `MEMORY_HIVE_STALE_THRESHOLD` (default 20).
  Files already referenced in `DECISIONS.md` are excluded.

- **`memory-hive checkpoint [--name <name>] | --list`** + **`memory-hive diff [--since <checkpoint|YYYY-MM-DD>] [--verbose]`** —
  Save a named reference marker, then show every hive write since that
  point. Default `--since` is the most recent checkpoint, or the install
  baseline if none exists. Lists New vs Modified files, classified by
  agent. Honors `.baseline-installed` so installer scaffolding never
  appears in diffs.

- **`memory-hive dedup [--per-agent] [--strict] [--threshold N]`** —
  Cluster near-duplicate raw learnings by normalized title. Default mode
  is cross-agent (catches when two agents independently document the same
  finding); `--per-agent` restricts within a single silo.

- **`memory-hive query <term> [--silo <name>] [--kind <k>] [--since <date>]`** —
  Searchable hive. Greps every text surface (silo log/memory/context,
  learnings raw + distilled, knowledge, registry, curator) with
  line-number context. Filter by silo, kind, or date.

- **`memory-hive citations`** — Cross-agent citation graph. Walks every
  file for `[..](path)` links and builds a who-cites-whom map. Surfaces
  team topology without manual tracking.

- **`memory-hive lint [--fix] [--strict] [<path>]`** — Frontmatter schema
  validation for learning files. Checks required keys, date format, valid
  agent, valid confidence. `--fix` rewrites where safe; `--strict` exits
  non-zero on warnings.

- **`memory-hive digest [--today | --yesterday | --week | --since YYYY-MM-DD]`** —
  Human-readable change summary for a time window (default rolling 24h).
  Per-agent newest writes with extracted content, ordered newest-first.
  "What's been happening?" without manual grep.

- **Multi-platform integration.** The installer now auto-detects and wires up
  every major agent platform that has a stable plain-text config file on
  local disk. 17 auto-inject targets, 5 manual-instructions platforms, plus
  an opt-in GitHub Copilot repo wiring:

  | Platform | Integration | Config file |
  |---|---|---|
  | Claude Code | auto-inject | `~/.claude/CLAUDE.md` |
  | OpenClaw | auto-inject | `~/.openclaw/CLAUDE.md` |
  | NanoClaw | auto-inject | `~/.config/nanoclaw/AGENTS.md` |
  | Hermes Agent | auto-inject | `~/.hermes/memories/MEMORY.md` |
  | Cursor | auto-inject | `~/.cursor/rules/memory-hive.mdc` |
  | Continue.dev | auto-inject | `~/.continue/rules/memory-hive.md` |
  | Gemini CLI | auto-inject | `~/.gemini/GEMINI.md` |
  | Goose (Block) | auto-inject | `~/.goosehints` |
  | Amazon Q Developer CLI | auto-inject | `~/.aws/amazonq/rules/memory-hive.md` |
  | OpenHands | auto-inject | `~/.openhands/microagents/memory-hive.md` |
  | Roo Code | auto-inject | `~/.roo/rules/memory-hive.md` |
  | Kilo Code | auto-inject | `~/.kilocode/rules/memory-hive.md` |
  | Windsurf (Codeium) | auto-inject | `~/.codeium/windsurf/memories/global_rules.md` |
  | Warp | auto-inject | `~/.agents/AGENTS.md` |
  | Sourcegraph Amp | auto-inject | `~/.config/amp/AGENTS.md` |
  | OpenAI Codex CLI | auto-inject | `~/.codex/AGENTS.md` |
  | OpenCode | auto-inject | `~/.config/opencode/AGENTS.md` |
  | Aider | manual snippet | `~/.aider.conf.yml` (structured YAML) |
  | Open Interpreter | manual snippet | profile YAML |
  | Cline (VS Code) | manual snippet | VS Code settings UI |
  | Zed | manual snippet | `~/.config/zed/settings.json` |
  | Crush (Charm) | manual snippet | `~/.local/share/crush/crush.json` |
  | GitHub Copilot (repo) | opt-in (`MEMORY_HIVE_COPILOT_REPO=1`) | `$PWD/.github/copilot-instructions.md` |

  Every auto-inject target uses the same `<!-- memory-hive:start -->` /
  `<!-- memory-hive:end -->` markers, so re-installs are idempotent and
  user content outside the markers is always preserved.
- **Per-platform opt-out env vars.** Every platform has a matching
  `MEMORY_HIVE_SKIP_<PLATFORM>=1` env var (e.g. `MEMORY_HIVE_SKIP_CURSOR=1`,
  `MEMORY_HIVE_SKIP_GOOSE=1`). The legacy `MEMORY_HIVE_SKIP_CLAUDE_MD=1`
  still works as an alias for `MEMORY_HIVE_SKIP_CLAUDE_CODE=1`.
- **Platform docs** under [`templates/platforms/`](templates/platforms/).
  One markdown file per supported platform explaining what gets wired,
  where, and how to opt out. Shipped into `~/.memory-hive/templates/platforms/`
  on install so users can read them without cloning the repo.
- **`memory-hive doctor` is now multi-platform.** Instead of only checking
  `~/.claude/CLAUDE.md`, `doctor` iterates every auto-inject platform whose
  config file exists on disk and reports per-platform whether the managed
  block is present and points at the right install directory.
- **New CI smoke tests** for the platform loop: detection, auto-inject,
  manual, opt-out, idempotency, and the multi-platform doctor. Runs on
  both `ubuntu-latest` and `macos-latest`.

### Added (prior Unreleased work)

- **Three-tier memory flow documented** in `HIVE_ARCHITECTURE.md`:
  raw external capture (Tier 1) → agent synthesis (Tier 2) → curator
  distilled truth (Tier 3). Clarifies how external context enters the
  hive without changing any existing flow.
- **`hive/raw/` folder convention** for Tier 1 raw external capture.
  One subfolder per source (`hive/raw/discord/`, `hive/raw/slack/`,
  etc.). Append-only; never modified by agents. Includes a `README.md`
  explaining the convention.
- **`templates/memory-entry.md`** — canonical format spec for Tier 1
  raw capture and Tier 2 structured synthesis. Two shapes, one spec.
- **`examples/ingesters/discord/`** — reference Discord ingester.
  Polls channels via the bot API and appends to `hive/raw/discord/`.
  Pure stdlib, env-var configured, resumable via state file,
  append-only. Includes a README with setup, launchd/cron recipes,
  and adaptation notes.
- **`examples/ingesters/generic-webhook/`** — minimal HTTP endpoint
  that accepts POSTs and appends to `hive/raw/<source>/<topic>.md`.
  Use it to capture context from anything that can send HTTP (Linear,
  GitHub webhooks, Zapier, cron, internal tools).
- **`examples/silo-mature/coder/`** — synthetic populated silo showing
  what a mature agent memory looks like after weeks of use. Log,
  context, memory, and learnings files with realistic density.
  Reference content only; not installed.
- **`examples/README.md`** — index explaining what's under
  `examples/` and when to use each piece.

### Documented (existing behavior, previously implicit)

- **`hive/knowledge/` is expandable.** Ships with three canonical files
  (HUMAN_CONTEXT, SOUL, DOMAINS); curator adds topical files as the
  hive grows (PROJECTS, COMPLIANCE, per-topic, etc.). Previously
  implicit; now called out in `HIVE_ARCHITECTURE.md`.
- **`hive/learnings/distilled/` is expandable.** Ships with four
  canonical files (patterns, mistakes, wins, cross-agent-insights);
  curator adds topical files (e.g. `auth-patterns.md`) as the hive
  accumulates enough distilled content per topic to warrant its own
  file. Previously implicit; now documented.

### Changed

- **Default install is now zero-input.** `curl | sh` scaffolds the
  reserved `main` silo, wires the managed `CLAUDE.md` block, and exits.
  No wizard, no prompts. Users opt into the interactive setup with
  `MEMORY_HIVE_WIZARD=1 curl | sh` or `memory-hive setup` after install.
- **Heuristic role matching** in the installer now uses only generic
  patterns (`*-coder`, `*-dev`, `*-engineer`, `*-auditor`, `*-analyst`,
  `*-strategist`, `*-specialist`, `*-pm`, etc.). Specific agent names
  from any individual user's roster have been removed.
- **`hive/knowledge/HUMAN_CONTEXT.md`** is now a blank template. Each
  user fills in their own facts locally; nothing personal ships in the
  public repo.

### Added

- **`memory-hive setup`** — CLI verb that re-invokes the installer with
  `MEMORY_HIVE_WIZARD=1` on demand. Useful after a silent install when
  you decide you want the guided flow.

## [0.1.0] — `feat/dynamic-agents`

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
- **Docs second pass.** README gets a "Day One" walkthrough and a
  representative (not enumerated) hive diagram; INTEGRATION.md and
  CONTRIBUTING.md rewritten to match the wizard + import flow + CLI;
  new `MIGRATION.md` covers upgrade paths from OpenClaw, bare Claude
  Code, and pre-0.1 hives. Cross-links added across README ↔
  INTEGRATION ↔ HIVE_ARCHITECTURE ↔ MIGRATION ↔ CHANGELOG.
- **`create-agent.sh`** accepts `MH_AGENT_ROLE` (inline text) and
  `MH_AGENT_ROLE_FILE` (path to a role file, typically a `templates/roles/*`
  entry). Existing CLI (`sh create-agent.sh <agent-id>`) is unchanged.

### Removed

- Empty silo directories from the original author's personal roster.
  Only `main/` (Chief of Staff / curator) ships now; everything else is
  user-created.
- Stray playbook / skill markdown files that had accumulated under
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
