#!/bin/sh
# shellcheck disable=SC2269  # ${HIVE_DIR}/${INSTALL_DIR} self-assigns are
# template placeholders rendered by install.sh.
# Memory Hive SessionEnd hook (installed by install.sh, paths rendered).
# Ambient workstream capture: when a Claude Code session ends, append one
# timestamped event to hive/raw/sessions/ — memory forms even when the
# model never ran the ritual. Pieces-style passive capture, scoped to the
# harness instead of the whole OS.
#
# Contract: NEVER break session teardown. All failure paths exit 0.
# Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="${HIVE_DIR}"
INSTALL_DIR="${INSTALL_DIR}"
AGENT="${MEMORY_HIVE_AGENT_ID:-main}"

[ -d "$HIVE_DIR" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

_payload="$(cat 2>/dev/null || :)"

_event="$(MH_PAYLOAD="$_payload" python3 - <<'PY'
import json, os, sys

try:
    p = json.loads(os.environ.get("MH_PAYLOAD") or "{}")
except Exception:
    p = {}
cwd = str(p.get("cwd") or "").strip()
reason = str(p.get("reason") or "").strip()
bits = ["claude-code session ended"]
if reason:
    bits.append("reason: " + reason)
if cwd:
    bits.append("cwd: " + cwd)
sys.stdout.write(" | ".join(bits))
PY
)" || exit 0
[ -n "$_event" ] || _event="claude-code session ended"

sh "$INSTALL_DIR/memory-hive" capture --source sessions --agent "$AGENT" \
    "$_event" >/dev/null 2>&1 || :
exit 0
