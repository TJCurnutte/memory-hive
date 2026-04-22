#!/bin/sh
# Memory Hive: create a new agent silo.
#
# Usage:
#   sh create-agent.sh <agent-id>
#
# Override install location:
#   MEMORY_HIVE_DIR=/custom/path sh create-agent.sh <agent-id>

set -e

AGENT_ID="${1:-}"
INSTALL_DIR="${MEMORY_HIVE_DIR:-$HOME/.memory-hive}"
AGENTS_DIR="$INSTALL_DIR/hive/agents"

if [ -z "$AGENT_ID" ]; then
    printf "Usage: sh create-agent.sh <agent-id>\n" >&2
    printf "  e.g. sh create-agent.sh researcher\n" >&2
    exit 2
fi

# Basic sanity: agent ids should be filesystem-safe.
case "$AGENT_ID" in
    */*|.*|*" "*)
        printf "ERROR: agent id must not contain slashes, spaces, or start with '.'\n" >&2
        exit 2
        ;;
esac

if [ ! -d "$INSTALL_DIR/hive" ]; then
    printf "ERROR: Memory Hive is not installed at %s\n" "$INSTALL_DIR" >&2
    printf "Run the installer first:\n" >&2
    printf "  curl -fsSL https://raw.githubusercontent.com/TJCurnutte/memory-hive/main/install.sh | sh\n" >&2
    exit 1
fi

mkdir -p "$AGENTS_DIR"
AGENT_DIR="$AGENTS_DIR/$AGENT_ID"

if [ -d "$AGENT_DIR" ]; then
    printf "Agent silo already exists: %s\n" "$AGENT_DIR"
    exit 0
fi

mkdir -p "$AGENT_DIR"

TODAY="$(date -u +%Y-%m-%d 2>/dev/null || echo "today")"

cat > "$AGENT_DIR/log.md" <<EOF
# ${AGENT_ID} — activity log

Append-only journal of what this agent did, when, and why.
Newest entries at the top.

## ${TODAY}

- Silo initialized.
EOF

cat > "$AGENT_DIR/context.md" <<EOF
# ${AGENT_ID} — working context

Short, current-task context for this agent. Replace freely as the task shifts.

## Role

(What is this agent's responsibility? One or two sentences.)

## Current focus

(What is the agent working on right now?)

## Open questions

-
EOF

cat > "$AGENT_DIR/memory.md" <<EOF
# ${AGENT_ID} — durable memory

Long-lived facts, preferences, and lessons this agent should remember across
sessions. Prefer short bullets; link out to shared knowledge where relevant.

## Facts

-

## Preferences

-

## Lessons learned

-
EOF

printf "Created agent silo: %s\n" "$AGENT_DIR"
printf "  log.md     — append-only activity log\n"
printf "  context.md — current working context\n"
printf "  memory.md  — durable memory\n"
