#!/bin/sh
# Memory Hive installer
# Installs the Memory Hive file-based memory system for multi-agent AI.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/TJCurnutte/memory-hive/main/install.sh | sh
#
# Override install location:
#   MEMORY_HIVE_DIR=/custom/path sh install.sh

set -e

REPO_URL="https://github.com/TJCurnutte/memory-hive.git"
INSTALL_DIR="${MEMORY_HIVE_DIR:-$HOME/.memory-hive}"
HIVE_DIR="$INSTALL_DIR/hive"
AGENTS_DIR="$HIVE_DIR/agents"

# Colors (fall back to plain text if no tty)
if [ -t 1 ]; then
    BOLD="$(printf '\033[1m')"
    GREEN="$(printf '\033[32m')"
    CYAN="$(printf '\033[36m')"
    YELLOW="$(printf '\033[33m')"
    RED="$(printf '\033[31m')"
    RESET="$(printf '\033[0m')"
else
    BOLD=""; GREEN=""; CYAN=""; YELLOW=""; RED=""; RESET=""
fi

info()  { printf "%s==>%s %s\n" "$CYAN"  "$RESET" "$1"; }
ok()    { printf "%sOK%s  %s\n"  "$GREEN" "$RESET" "$1"; }
warn()  { printf "%s!!%s  %s\n"  "$YELLOW" "$RESET" "$1"; }
die()   { printf "%sERROR%s %s\n" "$RED" "$RESET" "$1" >&2; exit 1; }

# --- preflight ---------------------------------------------------------------

command -v git >/dev/null 2>&1 || die "git is required but not installed. Install git and re-run. (macOS: xcode-select --install)"
command -v mkdir >/dev/null 2>&1 || die "mkdir not found in PATH."
command -v cp >/dev/null 2>&1 || die "cp not found in PATH."

info "Installing Memory Hive to ${BOLD}${INSTALL_DIR}${RESET}"

# --- fetch repo --------------------------------------------------------------

TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t memory-hive)"
trap 'rm -rf "$TMP_DIR"' EXIT INT TERM

info "Fetching latest from $REPO_URL"
if ! git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR/memory-hive" 2>/tmp/memory-hive-clone.err; then
    cat /tmp/memory-hive-clone.err >&2 || true
    die "Failed to clone $REPO_URL. Check your network connection."
fi

if [ ! -d "$TMP_DIR/memory-hive/hive" ]; then
    die "Cloned repo is missing the hive/ directory. Aborting."
fi

# --- install -----------------------------------------------------------------

mkdir -p "$INSTALL_DIR" || die "Could not create $INSTALL_DIR"
mkdir -p "$HIVE_DIR"    || die "Could not create $HIVE_DIR"

# Preserve existing agent silos: stash them, copy hive/, then restore.
AGENTS_BACKUP=""
if [ -d "$AGENTS_DIR" ]; then
    AGENTS_BACKUP="$TMP_DIR/agents-backup"
    info "Preserving existing agent silos in $AGENTS_DIR"
    mv "$AGENTS_DIR" "$AGENTS_BACKUP"
fi

# Copy each top-level entry under hive/ except agents/ (which we'll handle
# specifically so we don't clobber user data).
for entry in "$TMP_DIR/memory-hive/hive/"* "$TMP_DIR/memory-hive/hive/".[!.]*; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    if [ "$name" = "agents" ]; then
        continue
    fi
    cp -R "$entry" "$HIVE_DIR/" || die "Failed to copy $name into $HIVE_DIR"
done

# Restore (or create) the agents directory.
if [ -n "$AGENTS_BACKUP" ] && [ -d "$AGENTS_BACKUP" ]; then
    mv "$AGENTS_BACKUP" "$AGENTS_DIR"
    ok "Restored existing agent silos"
else
    mkdir -p "$AGENTS_DIR"
    # If the repo ships example agents (e.g. curator/), merge them in without
    # overwriting any that were just restored.
    if [ -d "$TMP_DIR/memory-hive/hive/agents" ]; then
        for agent in "$TMP_DIR/memory-hive/hive/agents/"*; do
            [ -e "$agent" ] || continue
            agent_name="$(basename "$agent")"
            if [ ! -e "$AGENTS_DIR/$agent_name" ]; then
                cp -R "$agent" "$AGENTS_DIR/"
            fi
        done
    fi
fi

# Also install the create-agent.sh helper into the install dir for convenience.
if [ -f "$TMP_DIR/memory-hive/create-agent.sh" ]; then
    cp "$TMP_DIR/memory-hive/create-agent.sh" "$INSTALL_DIR/create-agent.sh"
    chmod +x "$INSTALL_DIR/create-agent.sh" 2>/dev/null || true
fi

ok "Memory Hive installed"

# --- success banner ----------------------------------------------------------

cat <<EOF

${BOLD}${GREEN}Memory Hive is ready.${RESET}

  Install location: ${BOLD}${INSTALL_DIR}${RESET}
  Hive root:        ${BOLD}${HIVE_DIR}${RESET}
  Agent silos:      ${BOLD}${AGENTS_DIR}${RESET}

${BOLD}Next steps${RESET}

  1. Create your first agent silo:
       sh ${INSTALL_DIR}/create-agent.sh my-agent
     (or set MEMORY_HIVE_DIR to the same path you installed to)

  2. Point your agents at ${BOLD}${HIVE_DIR}${RESET}. Each agent reads/writes its
     own silo under ${BOLD}${AGENTS_DIR}/<agent-id>/${RESET} and shares knowledge
     through ${BOLD}${HIVE_DIR}/knowledge/${RESET} and ${BOLD}${HIVE_DIR}/registry/${RESET}.

  3. Read the docs:
       ${CYAN}https://github.com/TJCurnutte/memory-hive${RESET}

To upgrade later, just re-run this installer. Existing agent silos are preserved.
EOF
