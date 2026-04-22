#!/bin/sh
# Memory Hive: compliance / drift detector.
#
# Runs a set of one-shot checks against agent silos and the shared hive to
# surface agents that are going off-guideline. Intended to be cheap, safe,
# and read-only — it never writes to the hive.
#
# Usage:
#   sh check-compliance.sh                    # all agents, last 24h
#   sh check-compliance.sh coder              # just coder, last 24h
#   sh check-compliance.sh coder --since 7d   # last 7 days
#   sh check-compliance.sh --since 48h        # all agents, last 48h
#
# Environment overrides:
#   MEMORY_HIVE_DIR=/custom/path   hive install location (default: $HOME/.memory-hive)
#
# Exit codes:
#   0 — no violations (warnings allowed)
#   1 — one or more violations found
#   2 — usage error

# Note: no `set -e` — individual checks are allowed to fail silently and
# we want to visit every agent even if one has broken files.

SCRIPT_NAME="$(basename "$0")"

# ---------------------------------------------------------------------------
# Argument parsing.
# ---------------------------------------------------------------------------

AGENT_ARG=""
SINCE_ARG="24h"

usage() {
    cat >&2 <<EOF
Usage: sh ${SCRIPT_NAME} [agent-id] [--since <duration>]

Arguments:
  agent-id       Optional. If omitted, every agent silo is checked.
  --since VAL    Lookback window. Supported suffixes: s,m,h,d,w.
                 Defaults to 24h.

Examples:
  sh ${SCRIPT_NAME}
  sh ${SCRIPT_NAME} coder
  sh ${SCRIPT_NAME} coder --since 7d
  sh ${SCRIPT_NAME} --since 48h

Environment:
  MEMORY_HIVE_DIR   Override install location (default: \$HOME/.memory-hive)
EOF
    exit 2
}

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        --since)
            shift
            [ $# -gt 0 ] || usage
            SINCE_ARG="$1"
            shift
            ;;
        --since=*)
            SINCE_ARG="${1#--since=}"
            shift
            ;;
        --*)
            printf "Unknown flag: %s\n" "$1" >&2
            usage
            ;;
        *)
            if [ -z "$AGENT_ARG" ]; then
                AGENT_ARG="$1"
            else
                printf "Too many positional arguments: %s\n" "$1" >&2
                usage
            fi
            shift
            ;;
    esac
done

# Parse --since <N><unit> into seconds.
parse_since_seconds() {
    _raw="$1"
    # Accept bare integers (seconds), or <N>(s|m|h|d|w).
    _num="$(printf '%s' "$_raw" | sed -n 's/^\([0-9][0-9]*\)[smhdw]\{0,1\}$/\1/p')"
    _unit="$(printf '%s' "$_raw" | sed -n 's/^[0-9][0-9]*\([smhdw]\{0,1\}\)$/\1/p')"
    if [ -z "$_num" ]; then
        printf "Invalid --since value: %s (expected e.g. 24h, 7d, 3600)\n" "$_raw" >&2
        exit 2
    fi
    case "$_unit" in
        ""|s) printf '%s' "$_num" ;;
        m)    printf '%s' "$(( _num * 60 ))" ;;
        h)    printf '%s' "$(( _num * 3600 ))" ;;
        d)    printf '%s' "$(( _num * 86400 ))" ;;
        w)    printf '%s' "$(( _num * 604800 ))" ;;
    esac
}

SINCE_SECONDS="$(parse_since_seconds "$SINCE_ARG")" || exit 2

# ---------------------------------------------------------------------------
# Locate install dir.
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -n "${MEMORY_HIVE_DIR:-}" ]; then
    INSTALL_DIR="$MEMORY_HIVE_DIR"
elif [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/hive" ]; then
    INSTALL_DIR="$SCRIPT_DIR"
else
    INSTALL_DIR="$HOME/.memory-hive"
fi

HIVE_DIR="$INSTALL_DIR/hive"
AGENTS_DIR="$HIVE_DIR/agents"
KNOWLEDGE_DIR="$HIVE_DIR/knowledge"
LEARNINGS_RAW_DIR="$HIVE_DIR/learnings/raw"

if [ ! -d "$HIVE_DIR" ]; then
    printf "ERROR: Memory Hive is not installed at %s\n" "$INSTALL_DIR" >&2
    printf "Set MEMORY_HIVE_DIR or run install.sh first.\n" >&2
    exit 2
fi

# ---------------------------------------------------------------------------
# Colors + symbols.
# ---------------------------------------------------------------------------

if [ -t 1 ]; then
    BOLD="$(printf '\033[1m')"
    DIM="$(printf '\033[2m')"
    GREEN="$(printf '\033[32m')"
    YELLOW="$(printf '\033[33m')"
    RED="$(printf '\033[31m')"
    CYAN="$(printf '\033[36m')"
    RESET="$(printf '\033[0m')"
else
    BOLD=""; DIM=""; GREEN=""; YELLOW=""; RED=""; CYAN=""; RESET=""
fi

PASS_MARK="${GREEN}✓${RESET}"
FAIL_MARK="${RED}✗${RESET}"
WARN_MARK="${YELLOW}⚠${RESET}"

# ---------------------------------------------------------------------------
# Portable helpers.
# ---------------------------------------------------------------------------

NOW_EPOCH="$(date +%s)"
WINDOW_START="$(( NOW_EPOCH - SINCE_SECONDS ))"

# file_mtime <path> — print epoch seconds, or empty string on missing file.
# Prefers GNU/BusyBox `stat -c`, falls back to BSD `stat -f`.
file_mtime() {
    _p="$1"
    [ -e "$_p" ] || { printf ''; return; }
    _v="$(stat -c %Y "$_p" 2>/dev/null)"
    if [ -z "$_v" ]; then
        _v="$(stat -f %m "$_p" 2>/dev/null)"
    fi
    printf '%s' "$_v"
}

# humanize_age <seconds> — turn a positive delta into "3h ago" / "2d ago".
humanize_age() {
    _s="$1"
    if [ "$_s" -lt 60 ]; then
        printf '%ss ago' "$_s"
    elif [ "$_s" -lt 3600 ]; then
        printf '%sm ago' "$(( _s / 60 ))"
    elif [ "$_s" -lt 86400 ]; then
        printf '%sh ago' "$(( _s / 3600 ))"
    elif [ "$_s" -lt 604800 ]; then
        printf '%sd ago' "$(( _s / 86400 ))"
    else
        printf '%sw ago' "$(( _s / 604800 ))"
    fi
}

# rel_path <path> — strip the install dir prefix for terser output.
rel_path() {
    _p="$1"
    case "$_p" in
        "$HIVE_DIR"/*) printf 'hive/%s' "${_p#$HIVE_DIR/}" ;;
        *) printf '%s' "$_p" ;;
    esac
}

# ---------------------------------------------------------------------------
# Resolve agent list.
# ---------------------------------------------------------------------------

AGENTS=""
if [ -n "$AGENT_ARG" ]; then
    if [ ! -d "$AGENTS_DIR/$AGENT_ARG" ]; then
        printf "ERROR: no such agent silo: %s\n" "$AGENTS_DIR/$AGENT_ARG" >&2
        exit 2
    fi
    AGENTS="$AGENT_ARG"
else
    if [ -d "$AGENTS_DIR" ]; then
        for _p in "$AGENTS_DIR"/*; do
            [ -d "$_p" ] || continue
            _n="$(basename "$_p")"
            case "$_n" in .*) continue ;; esac
            if [ -z "$AGENTS" ]; then
                AGENTS="$_n"
            else
                AGENTS="$AGENTS $_n"
            fi
        done
    fi
fi

# ---------------------------------------------------------------------------
# Header.
# ---------------------------------------------------------------------------

printf '%sMemory Hive compliance report%s\n' "$BOLD" "$RESET"
printf 'Install dir: %s\n' "$INSTALL_DIR"
printf 'Lookback:    %s\n' "$SINCE_ARG"
printf '─────────────────────────────\n'

TOTAL_AGENTS=0
TOTAL_VIOLATIONS=0
TOTAL_WARNINGS=0

# ---------------------------------------------------------------------------
# Per-agent checks.
# ---------------------------------------------------------------------------

check_agent() {
    _aid="$1"
    _silo="$AGENTS_DIR/$_aid"
    _log="$_silo/log.md"
    _mem="$_silo/memory.md"

    printf '\n%s%s%s\n' "$BOLD" "$_aid" "$RESET"

    # --- C1: log recency ---------------------------------------------------
    _log_mtime="$(file_mtime "$_log")"
    if [ -z "$_log_mtime" ]; then
        printf '  C1 log recency       %b no log.md found\n' "$FAIL_MARK"
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    else
        _age=$(( NOW_EPOCH - _log_mtime ))
        [ "$_age" -lt 0 ] && _age=0
        if [ "$_log_mtime" -ge "$WINDOW_START" ]; then
            printf '  C1 log recency       %b last modified %s\n' "$PASS_MARK" "$(humanize_age "$_age")"
        else
            printf '  C1 log recency       %b last modified %s (outside %s window)\n' "$WARN_MARK" "$(humanize_age "$_age")" "$SINCE_ARG"
            TOTAL_WARNINGS=$(( TOTAL_WARNINGS + 1 ))
        fi
    fi

    # --- C2: stay in lane --------------------------------------------------
    # Files under OTHER agents' silos modified in the window — flag them
    # on the *current* agent's report only as a generic cross-silo warning,
    # because we can't tell who actually wrote. The more actionable check
    # is: walk each foreign silo and list files touched recently; that's
    # done at the hive-wide scan below. Here we just note whether any
    # foreign silos appear to have been touched and we couldn't rule the
    # current agent out.
    #
    # Best we can do portably: we DON'T currently track authorship per
    # file. So C2 surfaces recent writes in OTHER agents' silos as
    # "possible cross-silo write (by someone)" — review required.
    _lane_hits=""
    _lane_count=0
    for _other in "$AGENTS_DIR"/*; do
        [ -d "$_other" ] || continue
        _other_name="$(basename "$_other")"
        [ "$_other_name" = "$_aid" ] && continue
        case "$_other_name" in .*) continue ;; esac
        # Walk files in this foreign silo and check mtime.
        ( cd "$_other" && find . -type f 2>/dev/null ) | while IFS= read -r _rel; do
            _rel="${_rel#./}"
            [ -n "$_rel" ] || continue
            _full="$_other/$_rel"
            _m="$(file_mtime "$_full")"
            [ -n "$_m" ] || continue
            if [ "$_m" -ge "$WINDOW_START" ]; then
                printf '%s|%s\n' "$_other_name" "$_rel"
            fi
        done
    done > /tmp/.mh-lane.$$ 2>/dev/null

    if [ -s /tmp/.mh-lane.$$ ]; then
        _lane_count="$(wc -l < /tmp/.mh-lane.$$ | tr -d ' ')"
    fi

    if [ "$_lane_count" = "0" ] || [ -z "$_lane_count" ]; then
        printf '  C2 stay in lane      %b\n' "$PASS_MARK"
    else
        # Not a hard violation on THIS agent — we don't know who wrote.
        # Surface as a warning with details so humans can investigate.
        printf '  C2 stay in lane      %b %s recent write(s) in other silos (authorship unknown)\n' "$WARN_MARK" "$_lane_count"
        # Show up to 5 entries.
        _shown=0
        while IFS='|' read -r _owner _rel; do
            [ "$_shown" -ge 5 ] && break
            _mt="$(file_mtime "$AGENTS_DIR/$_owner/$_rel")"
            _ag=$(( NOW_EPOCH - _mt ))
            [ "$_ag" -lt 0 ] && _ag=0
            printf '    - agents/%s/%s (%s)\n' "$_owner" "$_rel" "$(humanize_age "$_ag")"
            _shown=$(( _shown + 1 ))
        done < /tmp/.mh-lane.$$
        if [ "$_lane_count" -gt 5 ]; then
            printf '    %s… and %s more%s\n' "$DIM" "$(( _lane_count - 5 ))" "$RESET"
        fi
        TOTAL_WARNINGS=$(( TOTAL_WARNINGS + 1 ))
    fi
    rm -f /tmp/.mh-lane.$$

    # --- C3: knowledge direct-writes --------------------------------------
    _knowledge_hits=""
    _knowledge_count=0
    if [ -d "$KNOWLEDGE_DIR" ]; then
        ( cd "$KNOWLEDGE_DIR" && find . -type f 2>/dev/null ) | while IFS= read -r _rel; do
            _rel="${_rel#./}"
            [ -n "$_rel" ] || continue
            _full="$KNOWLEDGE_DIR/$_rel"
            _m="$(file_mtime "$_full")"
            [ -n "$_m" ] || continue
            if [ "$_m" -ge "$WINDOW_START" ]; then
                printf '%s\n' "$_rel"
            fi
        done > /tmp/.mh-knowledge.$$ 2>/dev/null
        if [ -s /tmp/.mh-knowledge.$$ ]; then
            _knowledge_count="$(wc -l < /tmp/.mh-knowledge.$$ | tr -d ' ')"
        fi
    fi

    if [ "$_knowledge_count" = "0" ] || [ -z "$_knowledge_count" ]; then
        printf '  C3 knowledge writes  %b\n' "$PASS_MARK"
    else
        printf '  C3 knowledge writes  %b %s file(s) modified in last %s\n' "$FAIL_MARK" "$_knowledge_count" "$SINCE_ARG"
        _shown=0
        while IFS= read -r _rel; do
            [ "$_shown" -ge 5 ] && break
            _mt="$(file_mtime "$KNOWLEDGE_DIR/$_rel")"
            _ag=$(( NOW_EPOCH - _mt ))
            [ "$_ag" -lt 0 ] && _ag=0
            printf '    - knowledge/%s (modified %s)\n' "$_rel" "$(humanize_age "$_ag")"
            _shown=$(( _shown + 1 ))
        done < /tmp/.mh-knowledge.$$
        if [ "$_knowledge_count" -gt 5 ]; then
            printf '    %s… and %s more%s\n' "$DIM" "$(( _knowledge_count - 5 ))" "$RESET"
        fi
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    fi
    rm -f /tmp/.mh-knowledge.$$

    # --- C4: log.md shape -------------------------------------------------
    if [ ! -f "$_log" ]; then
        printf '  C4 log.md shape      %b log.md missing\n' "$FAIL_MARK"
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    elif [ ! -s "$_log" ]; then
        printf '  C4 log.md shape      %b log.md is empty\n' "$FAIL_MARK"
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    else
        # Need at least one line that starts with an ISO date or "## 20..".
        if grep -E -q '^(## 20[0-9]{2}-[0-1][0-9]-[0-3][0-9]|20[0-9]{2}-[0-1][0-9]-[0-3][0-9])' "$_log" 2>/dev/null; then
            printf '  C4 log.md shape      %b\n' "$PASS_MARK"
        else
            printf '  C4 log.md shape      %b no dated entry found\n' "$FAIL_MARK"
            TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
        fi
    fi

    # --- C5: memory.md shape ----------------------------------------------
    if [ ! -f "$_mem" ]; then
        printf '  C5 memory.md         %b memory.md missing\n' "$FAIL_MARK"
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    elif [ ! -s "$_mem" ]; then
        printf '  C5 memory.md         %b memory.md is empty\n' "$FAIL_MARK"
        TOTAL_VIOLATIONS=$(( TOTAL_VIOLATIONS + 1 ))
    else
        # Template-only heuristic: every non-blank, non-heading, non-prose
        # line is literally a lone "-" (the starter bullets). If so the
        # agent never wrote a durable lesson.
        _real_bullets="$(grep -E '^- .+' "$_mem" 2>/dev/null | wc -l | tr -d ' ')"
        if [ "${_real_bullets:-0}" = "0" ]; then
            printf '  C5 memory.md         %b only starter template\n' "$WARN_MARK"
            TOTAL_WARNINGS=$(( TOTAL_WARNINGS + 1 ))
        else
            printf '  C5 memory.md         %b %s bullet(s)\n' "$PASS_MARK" "$_real_bullets"
        fi
    fi

    # --- C6: orphaned learnings -------------------------------------------
    # A learning is considered well-formed if it has frontmatter (--- ... ---)
    # containing both `agent:` and `date:` fields. We only report this per
    # agent once; it's hive-wide and cheap. Scope: flag learnings whose
    # `agent:` field matches *this* agent but are malformed, PLUS show the
    # global orphan count (agent: missing entirely).
    _orphans_for_agent=0
    _orphans_total=0
    if [ -d "$LEARNINGS_RAW_DIR" ]; then
        for _lf in "$LEARNINGS_RAW_DIR"/*; do
            [ -f "$_lf" ] || continue
            # Extract the first frontmatter block (lines between leading ---).
            _fm="$(awk 'BEGIN{in_fm=0; started=0}
                /^---[[:space:]]*$/ {
                    if (started==0) { started=1; in_fm=1; next }
                    else if (in_fm==1) { exit }
                }
                in_fm==1 { print }
            ' "$_lf" 2>/dev/null)"
            _has_agent=0
            _has_date=0
            _agent_val=""
            if [ -n "$_fm" ]; then
                if printf '%s\n' "$_fm" | grep -E -q '^agent:[[:space:]]*[^[:space:]]'; then
                    _has_agent=1
                    _agent_val="$(printf '%s\n' "$_fm" | sed -n 's/^agent:[[:space:]]*//p' | head -n1 | sed 's/["'\'' ]//g')"
                fi
                if printf '%s\n' "$_fm" | grep -E -q '^date:[[:space:]]*[^[:space:]]'; then
                    _has_date=1
                fi
            fi
            if [ "$_has_agent" -eq 0 ] || [ "$_has_date" -eq 0 ]; then
                _orphans_total=$(( _orphans_total + 1 ))
                if [ "$_has_agent" -eq 1 ] && [ "$_agent_val" = "$_aid" ]; then
                    _orphans_for_agent=$(( _orphans_for_agent + 1 ))
                fi
            fi
        done
    fi

    if [ "$_orphans_for_agent" -eq 0 ] && [ "$_orphans_total" -eq 0 ]; then
        printf '  C6 learnings         %b\n' "$PASS_MARK"
    elif [ "$_orphans_for_agent" -gt 0 ]; then
        printf '  C6 learnings         %b %s orphan(s) attributed to %s\n' "$WARN_MARK" "$_orphans_for_agent" "$_aid"
        TOTAL_WARNINGS=$(( TOTAL_WARNINGS + 1 ))
    else
        printf '  C6 learnings         %b %s global orphan(s) in learnings/raw/ (agent unknown)\n' "$WARN_MARK" "$_orphans_total"
        TOTAL_WARNINGS=$(( TOTAL_WARNINGS + 1 ))
    fi

    TOTAL_AGENTS=$(( TOTAL_AGENTS + 1 ))
}

if [ -z "$AGENTS" ]; then
    printf '\n%sNo agent silos found under %s%s\n' "$YELLOW" "$AGENTS_DIR" "$RESET"
    printf '\nSummary: 0 agents checked\n'
    exit 0
fi

for _a in $AGENTS; do
    check_agent "$_a"
done

# ---------------------------------------------------------------------------
# Summary.
# ---------------------------------------------------------------------------

printf '\n'
if [ "$TOTAL_VIOLATIONS" -eq 0 ] && [ "$TOTAL_WARNINGS" -eq 0 ]; then
    printf '%sSummary:%s %s agent(s) checked · clean\n' "$BOLD" "$RESET" "$TOTAL_AGENTS"
else
    printf '%sSummary:%s %s agent(s) checked · %s violation(s) · %s warning(s)\n' \
        "$BOLD" "$RESET" "$TOTAL_AGENTS" "$TOTAL_VIOLATIONS" "$TOTAL_WARNINGS"
fi

if [ "$TOTAL_VIOLATIONS" -gt 0 ]; then
    exit 1
fi
exit 0
