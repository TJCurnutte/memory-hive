#!/bin/sh
# shellcheck disable=SC2269  # /Users/curnutte/.memory-hive/hive//Users/curnutte/.memory-hive self-assigns are
# template placeholders rendered by install.sh.
# Memory Hive Cursor `stop` hook (installed by install.sh, paths rendered).
# Parity with the Claude Code Stop hook: when an agent conversation ends
# without a fresh dated line in the agent's log.md, reply once with a
# followup_message instructing the ritual. Cursor's own loop_count is the
# loop guard (we only nudge on loop_count 0); aborted/error runs and short
# transcripts are exempt.
#
# Contract: NEVER trap a session. All failure paths exit 0 with no output
# (fail-open). Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="/Users/curnutte/.memory-hive/hive"
INSTALL_DIR="/Users/curnutte/.memory-hive"
AGENT="${MEMORY_HIVE_AGENT_ID:-main}"
LOG="$HIVE_DIR/agents/$AGENT/log.md"

[ -f "$LOG" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

_payload="$(cat 2>/dev/null || :)"

MH_PAYLOAD="$_payload" MH_INSTALL="$INSTALL_DIR" MH_AGENT="$AGENT" \
    python3 - "$LOG" <<'PY'
import datetime, json, os, sys

try:
    payload = json.loads(os.environ.get("MH_PAYLOAD") or "")
except Exception:
    sys.exit(0)

# Cursor increments loop_count each time a stop hook loops the agent —
# nudging only at 0 means at most one nudge per conversation.
if payload.get("loop_count"):
    sys.exit(0)
if payload.get("status") not in (None, "completed"):
    sys.exit(0)  # aborted/error runs owe nothing

transcript = payload.get("transcript_path") or ""
try:
    with open(transcript, encoding="utf-8", errors="replace") as f:
        lines = sum(1 for _ in f)
    if lines < 20:
        sys.exit(0)  # trivial conversation — don't nag
except Exception:
    sys.exit(0)  # can't judge the session — never block blind

today = datetime.date.today().isoformat()
try:
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        if today in f.read():
            sys.exit(0)  # ritual already ran today
except Exception:
    sys.exit(0)

install = os.environ.get("MH_INSTALL", "")
agent = os.environ.get("MH_AGENT", "main")
print(json.dumps({
    "followup_message": (
        "Memory Hive task-end ritual has not run this session. Run: `sh "
        + install + "/memory-hive log --agent " + agent + " \"<what you "
        "did, one line>\"`. If a lesson generalizes beyond you, also run "
        "`memory-hive learn \"<imperative rule>\" --context \"<where>\"` "
        "(spec: `memory-hive guide write`). Then finish your response."
    ),
}))
PY
exit 0
