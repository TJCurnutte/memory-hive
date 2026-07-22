#!/bin/sh
# shellcheck disable=SC2269  # /Users/curnutte/.memory-hive/hive//Users/curnutte/.memory-hive self-assigns are
# template placeholders rendered by install.sh.
# Memory Hive Cursor `sessionEnd` hook (installed by install.sh, paths
# rendered). Ambient workstream capture, parity with the Claude Code
# SessionEnd hook: append one timestamped event to hive/raw/sessions/ when
# a Cursor agent session ends — memory forms even when no ritual ran.
#
# Contract: NEVER break session teardown. All failure paths exit 0.
# Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="/Users/curnutte/.memory-hive/hive"
INSTALL_DIR="/Users/curnutte/.memory-hive"
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
bits = ["cursor session ended"]
model = str(p.get("model") or "").strip()
if model:
    bits.append("model: " + model)
roots = p.get("workspace_roots") or []
if isinstance(roots, list) and roots:
    bits.append("workspace: " + str(roots[0]))
sys.stdout.write(" | ".join(bits))
PY
)" || exit 0
[ -n "$_event" ] || _event="cursor session ended"

sh "$INSTALL_DIR/memory-hive" capture --source sessions --agent "$AGENT" \
    "$_event" >/dev/null 2>&1 || :
exit 0
