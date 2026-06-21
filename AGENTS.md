# AGENTS.md

## Cursor Cloud specific instructions

Memory Hive is a single product: a POSIX-shell CLI (`memory-hive`) plus Python
stdlib helpers (`memory_hive_recall.py` recall engine, `memory_hive_mcp.py` MCP
server). There is **no package manager, no lockfile, and no build step** — see
`CONTRIBUTING.md`. Runtime needs are only POSIX `sh` + `python3` (3.9+, with
SQLite FTS5). The only external dev tool is `shellcheck`, used for lint.

### Lint
- `shellcheck --format=gcc install.sh create-agent.sh memory-hive update.sh check-compliance.sh`
- Matches CI (`.github/workflows/ci.yml`). It is **warn-level / non-failing**:
  there are pre-existing notes and a non-zero exit is expected and acceptable.

### Tests
- Run from the repo root with the repo root on `PYTHONPATH`:
  `PYTHONPATH=$(pwd) python3 -m unittest discover -s tests`
- Gotcha: the tests import `memory_hive_recall` (a repo-root module). Without
  `PYTHONPATH` pointing at the repo root the imports fail with
  `ModuleNotFoundError: No module named 'memory_hive_recall'`. The `tests/`
  directory has no `__init__.py`, so do not use `-t .` as the discover
  top-level dir.

### Run (dev mode)
- Never run the installer against a real `~/.memory-hive`. Install into a
  throwaway dir from the working copy (see `CONTRIBUTING.md`):
  `MEMORY_HIVE_REPO="$(pwd)" MEMORY_HIVE_DIR="$(mktemp -d)" MEMORY_HIVE_SKIP_CLAUDE_CODE=1 MEMORY_HIVE_SKIP_CURSOR=1 sh install.sh < /dev/null`
- The installer puts a `memory-hive` command on PATH and reads `MEMORY_HIVE_DIR`
  from the environment, so `export MEMORY_HIVE_DIR=<throwaway>` makes subsequent
  `memory-hive <verb>` calls operate on that hive.
- Core verbs: `memory-hive status`, `memory-hive add <name> --role coder`,
  `memory-hive search "term"`, `memory-hive recall "task context"`.
  `memory-hive learn <agent> "<text>" --context "<where it came up>"` — the
  `--context` flag is required.
- `check-compliance.sh` reads `MEMORY_HIVE_DIR` from the environment. Do **not**
  pass the install dir as a positional arg — it is interpreted as an agent name
  and errors with `no such agent silo`.
- Optional MCP server (stdio JSON-RPC): `memory-hive mcp` or
  `python3 memory_hive_mcp.py`. Tools: `ask_hive`, `hive_log`, `hive_learn`,
  `hive_capture`, `hive_guide`.
