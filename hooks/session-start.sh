#!/bin/sh
# shellcheck disable=SC2269,SC2016  # /Users/curnutte/.memory-hive/hive//Users/curnutte/.memory-hive self-assigns are
# template placeholders rendered by install.sh; backticks in printf are
# literal markdown.
# Memory Hive SessionStart hook (installed by install.sh, paths rendered).
# Injects hive hydration into new Claude Code sessions as additionalContext,
# so booting from memory is mechanical instead of prompt-compliance.
#
# Contract: NEVER break a session. Any failure path exits 0 with no output.
# Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="/Users/curnutte/.memory-hive/hive"
INSTALL_DIR="/Users/curnutte/.memory-hive"
AGENT="${MEMORY_HIVE_AGENT_ID:-main}"

[ -d "$HIVE_DIR" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

_payload="$(cat 2>/dev/null || :)"

CTX_FILE="$(mktemp 2>/dev/null)" || exit 0
trap 'rm -f "$CTX_FILE"' EXIT INT TERM

{
    if ! sh "$INSTALL_DIR/memory-hive" recall bundle "session hydrate for $AGENT" --for-agent "$AGENT" --max-tokens 1200 --cache 2>/dev/null; then
        if ! sh "$INSTALL_DIR/memory-hive" bundle --for "$AGENT" --max-tokens 1200 2>/dev/null; then
            sed -n '1,40p' "$HIVE_DIR/index.md" 2>/dev/null
        fi
    fi
    printf '\n'
    printf 'Orchestration: run memory-hive orchestrate before substantive work unless prompt opts out of optimize.\n'
    printf 'Full operating contract on demand: `memory-hive guide [paths|id|hydrate|retrieve|write|lanes|curate|health]`.\n'
    printf 'Task-end ritual is mandatory before finishing non-trivial work: `memory-hive guide write`.\n'
} > "$CTX_FILE" 2>/dev/null

MH_AGENT="$AGENT" MH_HIVE="$HIVE_DIR" MH_PAYLOAD="$_payload" \
    python3 - "$CTX_FILE" <<'PY'
import json, os, sys

try:
    body = open(sys.argv[1], encoding="utf-8", errors="replace").read()
except Exception:
    sys.exit(0)
if not body.strip():
    sys.exit(0)

model = ""
try:
    payload = json.loads(os.environ.get("MH_PAYLOAD") or "{}")
    model = str(payload.get("model") or "").strip()
except Exception:
    pass

header = "Memory Hive hydration (agent: %s, hive: %s%s)\n\n" % (
    os.environ.get("MH_AGENT", "main"),
    os.environ.get("MH_HIVE", ""),
    (", model: " + model) if model else "",
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": header + body,
    }
}))
PY
exit 0
