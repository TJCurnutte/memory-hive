#!/bin/sh
# shellcheck disable=SC2269  # ${HIVE_DIR} self-assign is a template
# placeholder rendered by install.sh.
# Memory Hive Stop hook (installed by install.sh, paths rendered).
# Enforces the task-end ritual mechanically: when a session ends without a
# fresh line in the agent's log.md, block ONCE with instructions to run the
# ritual. Claude complies, stops again with stop_hook_active=true, and we
# let it through — no loops, at most one nudge per session.
#
# Contract: NEVER trap a session. Trivial sessions (short transcripts),
# missing hive, missing python3, unparseable input — all exit 0 silently.
# Runtime kill switch: MEMORY_HIVE_HOOKS_DISABLE=1.

[ "${MEMORY_HIVE_HOOKS_DISABLE:-0}" = "1" ] && exit 0

HIVE_DIR="${HIVE_DIR}"
AGENT="${MEMORY_HIVE_AGENT_ID:-main}"
LOG="$HIVE_DIR/agents/$AGENT/log.md"

[ -f "$LOG" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Drain the hook payload from stdin BEFORE the heredoc python runs —
# `python3 - <<EOF` takes its program from stdin, so the payload must be
# captured here or it is lost to the heredoc.
_payload="$(cat 2>/dev/null || :)"

MH_PAYLOAD="$_payload" python3 - "$LOG" <<'PY'
import datetime, json, os, sys

try:
    payload = json.loads(os.environ.get("MH_PAYLOAD") or "")
except Exception:
    sys.exit(0)
if payload.get("stop_hook_active"):
    sys.exit(0)  # already nudged this session — let it finish

# Trivial-session guard: a quick Q&A doesn't owe the hive a log line.
transcript = payload.get("transcript_path") or ""
try:
    with open(transcript, encoding="utf-8", errors="replace") as f:
        lines = sum(1 for _ in f)
    if lines < 20:
        sys.exit(0)
except Exception:
    sys.exit(0)  # can't judge the session — never block blind

today = datetime.date.today().isoformat()
try:
    with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
        if today in f.read():
            sys.exit(0)  # ritual already ran today
except Exception:
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": (
        "Memory Hive task-end ritual has not run this session. Append one "
        "line to " + sys.argv[1] + " in the form `- " + today + " — <what "
        "you did>`. If a lesson generalizes beyond you, also write a raw "
        "learning (exact spec: `memory-hive guide write`). Then finish "
        "your response."
    ),
}))
PY
exit 0
