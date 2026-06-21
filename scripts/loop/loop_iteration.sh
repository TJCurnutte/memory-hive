#!/bin/sh
# Memory Hive self-iteration loop — ONE iteration.
#
# Each run makes a concrete, safe improvement to "overall use" of the hive:
#   1. ensures a hive exists (installs a throwaway one from this repo if none),
#   2. runs the built-in maintenance pass (registry/citation refresh, recall
#      index maintenance, curator Optimizer) — best effort, non-interactive,
#   3. regenerates a usage-analytics snapshot so trends are visible over time.
#
# It is deterministic and idempotent. It never commits, pushes, or merges.
# To run it on a cadence, schedule it (cron / GitHub Actions) — see README.md.
#
# Env:
#   MEMORY_HIVE_DIR   target hive (default: ~/.memory-hive; auto-created if absent)
#   LOOP_REPORT_DIR   where snapshots are written (default: <repo>/reports/memory-hive-loop)
set -eu

unset CDPATH 2>/dev/null || true
_script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$_script_dir/../.." && pwd)"
HIVE_DIR="${MEMORY_HIVE_DIR:-$HOME/.memory-hive}"
REPORT_DIR="${LOOP_REPORT_DIR:-$REPO/reports/memory-hive-loop}"

log() { printf '[loop] %s\n' "$*"; }

# 1. Ensure a hive exists. If none, install a throwaway one from this working
#    copy so the loop is self-contained (used by CI / first run).
if [ ! -d "$HIVE_DIR/hive" ]; then
    log "no hive at $HIVE_DIR — installing a throwaway one from $REPO"
    mkdir -p "$HIVE_DIR"
    MEMORY_HIVE_REPO="$REPO" \
    MEMORY_HIVE_DIR="$HIVE_DIR" \
    MEMORY_HIVE_SKIP_CLAUDE_CODE=1 \
    MEMORY_HIVE_SKIP_CURSOR=1 \
    MEMORY_HIVE_SKIP_OPENCLAW=1 \
    MEMORY_HIVE_SKIP_GEMINI_CLI=1 \
    MEMORY_HIVE_SKIP_GOOSE=1 \
        sh "$REPO/install.sh" </dev/null >/dev/null 2>&1 || {
            log "install failed"; exit 1; }
fi
export MEMORY_HIVE_DIR="$HIVE_DIR"

# 2. Run the maintenance pass. Non-interactive, best-effort: a failure here must
#    not break the iteration (the analytics step still records current state).
log "running maintenance pass"
sh "$REPO/memory-hive" maintain </dev/null >/dev/null 2>&1 || log "maintain skipped/failed (non-fatal)"

# 3. Regenerate the usage-analytics snapshot.
ts="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REPORT_DIR"
log "writing usage snapshot for $ts"
python3 "$REPO/scripts/loop/hive_usage_report.py" \
    --repo "$REPO" \
    --hive "$HIVE_DIR" \
    --json "$REPORT_DIR/usage-$ts.json" \
    --markdown "$REPORT_DIR/usage-$ts.md"

cp "$REPORT_DIR/usage-$ts.json" "$REPORT_DIR/latest.json"
cp "$REPORT_DIR/usage-$ts.md" "$REPORT_DIR/latest.md"
log "done — snapshot at $REPORT_DIR/latest.md"
