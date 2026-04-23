# Contributing to Memory Hive

Memory Hive is POSIX shell + Markdown — no runtime, no package manager,
no build step. Contributing is correspondingly simple: clone, change,
test, PR.

## Repo layout

```
.
├── README.md                    product overview + Day One walkthrough
├── INTEGRATION.md               installer + CLI behavior
├── MIGRATION.md                 upgrade paths from OpenClaw / pre-0.1
├── HIVE_ARCHITECTURE.md         conceptual model (two layers, curation)
├── CHANGELOG.md                 release history
├── install.sh                   one-shot installer (curl | sh target)
├── memory-hive                  CLI wrapper (add/list/archive/role/rename)
├── create-agent.sh              low-level silo scaffold (called by CLI + wizard)
├── update.sh                    refresh shared content from GitHub
├── check-compliance.sh          drift detector for an installed hive
├── templates/
│   ├── claude-boot-block.md     managed block for ~/.claude/CLAUDE.md
│   └── roles/                   starter role descriptions
│       ├── coder.md
│       ├── reviewer.md
│       ├── researcher.md
│       ├── writer.md
│       ├── planner.md
│       └── curator.md
└── hive/                        seed content copied into ~/.memory-hive/
    ├── index.md
    ├── registry/                AGENTS.md, SKILLS_CATALOG.md
    ├── knowledge/               curated truth (curator writes)
    ├── learnings/               raw → distilled
    ├── tasks/                   shared work queue
    ├── curator/                 curation workspace
    └── agents/
        ├── SILO_README.md       template documentation
        └── main/                curator silo (always ships)
```

## Testing installer changes locally

**Do not run the installer against your real `~/.memory-hive`.** It
will rewrite shared hive files and the managed `CLAUDE.md` block
against the version in your working copy, which might not be what you
want to ship.

Use throwaway paths and the skip-CLAUDE env var every time:

```bash
MEMORY_HIVE_REPO="$(pwd)" \
MEMORY_HIVE_DIR="$(mktemp -d)" \
MEMORY_HIVE_SKIP_CLAUDE_MD=1 \
  sh install.sh
```

What each variable does:

- `MEMORY_HIVE_REPO="$(pwd)"` — install from your working copy instead
  of `git clone`ing GitHub. Required, or you're testing the last
  published commit.
- `MEMORY_HIVE_DIR="$(mktemp -d)"` — put the install somewhere
  disposable. `rm -rf` after to clean up.
- `MEMORY_HIVE_SKIP_CLAUDE_MD=1` — don't touch `~/.claude/CLAUDE.md`.
  Forgetting this once will silently rewrite the file to point at your
  temp dir.

## Ways to contribute

### Report a bug

Open an issue with a clear description, reproduction steps, and your
setup (OS, shell, whether Claude Code / OpenClaw are present).

### Improve documentation

If something confused you, others will also get confused. Docs PRs
don't need an issue first.

### Code contributions

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes.
4. Test against a throwaway install (see above).
5. Run `sh check-compliance.sh` against the throwaway install to catch
   layout drift.
6. Open a pull request against `main`.

## Areas that welcome help

- **Framework adapters** — integrations for LangChain, AutoGen, CrewAI,
  OpenAI Agents SDK.
- **Role templates** — additions to `templates/roles/`, one paragraph
  each, matching the tone of the existing six.
- **Curation automation** — tooling that helps `main` process
  `learnings/raw/` faster.
- **Memory hygiene tools** — deduplication, size management, age-based
  escalation.
- **Visualization** — hive state dashboards, learning-graph views.

## Style conventions

### Shell

- POSIX `sh`, not bash. Target `/bin/sh` on macOS and Linux.
- No `local` (not POSIX). Prefix helper variables with `_` and
  namespace them by function.
- No `[[ ]]`, use `[ ]`.
- Avoid `awk -v` for multiline values (see the lessons in the
  installer) — write to a temp file and `getline` instead.
- Every user-facing error goes through a `die` helper that prints to
  stderr.

### Markdown

- No trailing whitespace. No tabs where spaces are expected.
- Heading levels monotonic (don't jump `#` → `###`).
- Links relative where possible so they resolve on GitHub.
- Don't introduce emoji unless the surrounding section already uses
  them; the docs aim for tight, product-first prose.

### Tests

- Installer/CLI changes should work in both the interactive wizard path
  and the non-interactive `< /dev/null` path. The test harness covers
  both.
- Check the output of `memory-hive list` and `check-compliance.sh`
  after any flow that touches silos.

## Questions

Open a GitHub Discussion if you're unsure about scope or approach.

## License

MIT. By contributing you agree that your work will ship under the same
license.
