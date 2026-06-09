#!/bin/sh
# shellcheck disable=SC2269,SC2016  # ${HIVE_DIR}/${INSTALL_DIR} self-assigns
# are template placeholders rendered by install.sh; backticks in printf are
# literal markdown.
# Memory Hive SessionStart hook (installed by install.sh, paths rendered).
# Injects hive hydration into new Claude Code sessions as additionalContext,
# so booting from memory is mechanical instead of prompt-compliance.
#
# Contract: NEVER break a session. Any failure path exits 0 with no output.
# Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="${HIVE_DIR}"
INSTALL_DIR="${INSTALL_DIR}"
AGENT="${MEMORY_HIVE_AGENT_ID:-main}"

[ -d "$HIVE_DIR" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Drain the hook payload from stdin BEFORE any heredoc python runs —
# `python3 - <<EOF` takes its program from stdin, so the payload must be
# captured here or it is lost to the heredoc.
_payload="$(cat 2>/dev/null || :)"

CTX_FILE="$(mktemp 2>/dev/null)" || exit 0
trap 'rm -f "$CTX_FILE"' EXIT INT TERM

{
    # Token-budgeted cited bundle when the CLI cooperates; index head as a
    # fallback so a broken bundle never means an empty boot.
    if ! sh "$INSTALL_DIR/memory-hive" bundle --for "$AGENT" --max-tokens 1200 2>/dev/null; then
        sed -n '1,40p' "$HIVE_DIR/index.md" 2>/dev/null
    fi
    printf '\n'
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

# Best-effort: surface which model/session this hydration belongs to when
# the harness tells us (hook payload JSON); silence on any parse trouble.
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
