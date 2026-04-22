#!/bin/sh
# Memory Hive updater.
#
# Pulls the latest shared hive content from GitHub and merges it into the
# user's install:
#   - NEW files/dirs from upstream → added
#   - CHANGED shared files (knowledge/, index.md, registry/, learnings/distilled/,
#     tasks/, curator/, templates/) → refreshed from upstream
#   - Agent silos under $HIVE_DIR/agents/ → strictly preserved, never touched
#   - CLAUDE.md managed block → refreshed to latest boot contract
#
# This is what "update memory hive" should feel like: idempotent, safe for
# agent private memory, and pulls in whatever the maintainer has changed.
#
# Usage:
#   sh ~/.memory-hive/update.sh
#   curl -fsSL memoryhive.neural-forge.io/update.sh | sh
#
# Honors MEMORY_HIVE_DIR like install.sh. Delegates to install.sh with
# MEMORY_HIVE_SYNC=1 so upstream wins for shared content.

set -e

INSTALL_DIR="${MEMORY_HIVE_DIR:-$HOME/.memory-hive}"
REMOTE_INSTALLER="https://raw.githubusercontent.com/TJCurnutte/memory-hive/main/install.sh"

# Prefer the locally-installed install.sh so offline/private forks still work;
# fall back to curl from GitHub. In both cases, set MEMORY_HIVE_SYNC=1 so
# install.sh knows this is an update and should refresh shared content.
if [ -f "$INSTALL_DIR/install.sh" ]; then
    MEMORY_HIVE_SYNC=1 MEMORY_HIVE_DIR="$INSTALL_DIR" sh "$INSTALL_DIR/install.sh"
elif command -v curl >/dev/null 2>&1; then
    MEMORY_HIVE_SYNC=1 MEMORY_HIVE_DIR="$INSTALL_DIR" \
        sh -c "$(curl -fsSL "$REMOTE_INSTALLER")"
else
    printf 'ERROR: neither %s nor curl is available\n' "$INSTALL_DIR/install.sh" >&2
    exit 1
fi
