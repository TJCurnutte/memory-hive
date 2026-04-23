#!/bin/sh
# Memory Hive: create a new agent silo.
#
# Usage:
#   sh create-agent.sh <agent-id>
#
# Override install location:
#   MEMORY_HIVE_DIR=/custom/path sh create-agent.sh <agent-id>
#
# Seed a role description into context.md's "## Role" section:
#   MH_AGENT_ROLE="Writes code and knows the codebase conventions." \
#     sh create-agent.sh <agent-id>
#
# Or point at a template file under templates/roles/:
#   MH_AGENT_ROLE_FILE=/path/to/role.md sh create-agent.sh <agent-id>

set -e

AGENT_ID="${1:-}"

# Self-locate: if this script lives next to a hive/ directory, use that as the
# install root. Lets `sh /custom/path/create-agent.sh` work without the user
# also exporting MEMORY_HIVE_DIR. The env var still wins if explicitly set.
SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -n "${MEMORY_HIVE_DIR:-}" ]; then
    INSTALL_DIR="$MEMORY_HIVE_DIR"
elif [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/hive" ]; then
    INSTALL_DIR="$SCRIPT_DIR"
else
    INSTALL_DIR="$HOME/.memory-hive"
fi
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

# Resolve the role text. Env var wins over file; both are optional.
ROLE_TEXT=""
if [ -n "${MH_AGENT_ROLE:-}" ]; then
    ROLE_TEXT="$MH_AGENT_ROLE"
elif [ -n "${MH_AGENT_ROLE_FILE:-}" ] && [ -f "$MH_AGENT_ROLE_FILE" ]; then
    ROLE_TEXT="$(cat "$MH_AGENT_ROLE_FILE")"
fi

cat > "$AGENT_DIR/log.md" <<EOF
# ${AGENT_ID} — activity log

Append-only journal of what this agent did, when, and why.
Newest entries at the top.

## ${TODAY}

- Silo initialized.
EOF

# context.md: seed the Role section with ROLE_TEXT if we have it,
# otherwise keep the placeholder prompt so the user fills it in later.
if [ -n "$ROLE_TEXT" ]; then
    {
        printf '# %s — working context\n\n' "$AGENT_ID"
        printf 'Short, current-task context for this agent. Replace freely as the task shifts.\n\n'
        printf '## Role\n\n'
        printf '%s\n\n' "$ROLE_TEXT"
        printf '## Current focus\n\n'
        printf '(What is the agent working on right now?)\n\n'
        printf '## Open questions\n\n'
        # Leading "- " via -- to prevent printf treating it as a flag.
        printf -- '-\n'
    } > "$AGENT_DIR/context.md"
else
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
fi

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
if [ -n "$ROLE_TEXT" ]; then
    printf "  role       — seeded into context.md\n"
fi
