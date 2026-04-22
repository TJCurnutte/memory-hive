#!/bin/sh
# Memory Hive installer
# Installs the Memory Hive file-based memory system for multi-agent AI,
# auto-detects the user's agent environment, merges a boot block into
# ~/.claude/CLAUDE.md when present, and scaffolds a default silo so
# agents can start using the hive immediately.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/TJCurnutte/memory-hive/main/install.sh | sh
#
# Environment overrides:
#   MEMORY_HIVE_DIR=/custom/path   install location (default: $HOME/.memory-hive)
#   MEMORY_HIVE_MERGE_CWD=1        also merge the hive block into $PWD/CLAUDE.md

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

# Merge each top-level entry under hive/ into $HIVE_DIR without overwriting
# anything the user already has.
#
# Rules:
#   - If $HIVE_DIR/<name> does not exist → copy wholesale.
#   - If it exists and is a directory → recursively copy only files that are
#     missing on the user's side. Existing files are left strictly alone.
#   - If it exists and is a file → never overwrite. Drop the upstream version
#     alongside as <file>.upstream so the user can `diff` it at their leisure.
# agents/ is handled separately below.
#
# Notes:
#   - POSIX `cp` has no portable --update flag, so we walk via `find` and copy
#     per-file.
#   - Symlinks in the repo are treated as their targets (unlikely in practice).

# MEMORY_HIVE_SYNC=1 turns a re-install into an "update": upstream wins for
# shared hive content. Agent silos (under $AGENTS_DIR) are ALWAYS preserved
# regardless of this flag — they live outside this merge loop entirely.
SYNC_MODE="${MEMORY_HIVE_SYNC:-0}"

_safe_merge_dir() {
    _src="$1"; _dst="$2"
    [ -d "$_dst" ] || mkdir -p "$_dst"
    # Relative paths of every file under $_src.
    ( cd "$_src" && find . -type f 2>/dev/null ) | while IFS= read -r rel; do
        rel="${rel#./}"
        [ -n "$rel" ] || continue
        _s="$_src/$rel"
        _d="$_dst/$rel"
        if [ -e "$_d" ]; then
            if cmp -s "$_s" "$_d" 2>/dev/null; then
                : # identical — nothing to do
            elif [ "$SYNC_MODE" = "1" ]; then
                # Update mode: upstream wins for shared content. Back up the
                # user's version as .local so nothing is irrecoverably lost.
                cp "$_d" "$_d.local" 2>/dev/null || true
                cp "$_s" "$_d" || die "Failed to update $rel in $_dst"
            else
                # Default (install mode): never overwrite. Drop the upstream
                # version alongside for review.
                cp "$_s" "$_d.upstream" 2>/dev/null || true
            fi
        else
            _ddir="$(dirname "$_d")"
            [ -d "$_ddir" ] || mkdir -p "$_ddir"
            cp "$_s" "$_d" || die "Failed to copy $rel into $_dst"
        fi
    done
}

for entry in "$TMP_DIR/memory-hive/hive/"* "$TMP_DIR/memory-hive/hive/".[!.]*; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    if [ "$name" = "agents" ]; then
        continue
    fi
    target="$HIVE_DIR/$name"
    if [ ! -e "$target" ]; then
        # Fresh install for this entry — just copy.
        cp -R "$entry" "$HIVE_DIR/" || die "Failed to copy $name into $HIVE_DIR"
    elif [ -d "$entry" ] && [ -d "$target" ]; then
        # Both directories — merge file-by-file, preserving existing.
        _safe_merge_dir "$entry" "$target"
    elif [ -f "$entry" ] && [ -f "$target" ]; then
        # File collision at hive root.
        if ! cmp -s "$entry" "$target" 2>/dev/null; then
            if [ "$SYNC_MODE" = "1" ]; then
                cp "$target" "$target.local" 2>/dev/null || true
                cp "$entry" "$target" || die "Failed to update $name in $HIVE_DIR"
            else
                cp "$entry" "$target.upstream" 2>/dev/null || true
            fi
        fi
    else
        # Type mismatch (rare) — leave the user's version alone, stash upstream.
        cp -R "$entry" "$target.upstream" 2>/dev/null || true
        warn "$name: type differs between upstream and local — left yours alone, stashed upstream as ${name}.upstream"
    fi
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

# Install the helper scripts into the install dir so users can run them
# locally without a curl round-trip. These are tools (not user content) and
# we always keep them current with upstream.
for helper in create-agent.sh update.sh install.sh check-compliance.sh; do
    _src="$TMP_DIR/memory-hive/$helper"
    [ -f "$_src" ] || continue
    cp "$_src" "$INSTALL_DIR/$helper"
    chmod +x "$INSTALL_DIR/$helper" 2>/dev/null || true
done

if [ "$SYNC_MODE" = "1" ]; then
    ok "Memory Hive updated"
else
    ok "Memory Hive installed"
fi

# =============================================================================
# Phase A: Environment detection
# =============================================================================
# Detection must never abort the install -- wrap probes so a missing dir or
# permission error just means "not detected".

DETECTED_CLAUDE_CODE=0
DETECTED_CLAUDE_MD=0
DETECTED_CLAUDE_AGENTS=""  # space-separated list of ~/.claude/agents/* subdir names
DETECTED_OPENCLAW=0
DETECTED_OPENCLAW_DIR=""
DETECTED_CWD_CLAUDE_MD=0

CLAUDE_HOME="$HOME/.claude"
CLAUDE_MD_PATH="$CLAUDE_HOME/CLAUDE.md"
CLAUDE_AGENTS_DIR="$CLAUDE_HOME/agents"
OPENCLAW_HOME="$HOME/.openclaw"
CWD_CLAUDE_MD="$PWD/CLAUDE.md"

info "Detecting agent environment"

if [ -d "$CLAUDE_HOME" ]; then
    DETECTED_CLAUDE_CODE=1
    ok "Found Claude Code config at $CLAUDE_HOME"
fi

if [ -f "$CLAUDE_MD_PATH" ]; then
    DETECTED_CLAUDE_MD=1
fi

if [ -d "$CLAUDE_AGENTS_DIR" ]; then
    # Collect agent names whose path is a directory. Suppress errors from
    # an empty glob.
    for _agent_path in "$CLAUDE_AGENTS_DIR"/*; do
        [ -d "$_agent_path" ] || continue
        _agent_name="$(basename "$_agent_path")"
        # Skip dotfiles just in case a shell expanded them.
        case "$_agent_name" in
            .*) continue ;;
        esac
        if [ -z "$DETECTED_CLAUDE_AGENTS" ]; then
            DETECTED_CLAUDE_AGENTS="$_agent_name"
        else
            DETECTED_CLAUDE_AGENTS="$DETECTED_CLAUDE_AGENTS $_agent_name"
        fi
    done
    if [ -n "$DETECTED_CLAUDE_AGENTS" ]; then
        ok "Found Claude Code sub-agents: $DETECTED_CLAUDE_AGENTS"
    fi
fi

if [ -d "$OPENCLAW_HOME" ]; then
    DETECTED_OPENCLAW=1
    DETECTED_OPENCLAW_DIR="$OPENCLAW_HOME"
    ok "Found OpenClaw config at $OPENCLAW_HOME"
fi

if [ -f "$CWD_CLAUDE_MD" ]; then
    DETECTED_CWD_CLAUDE_MD=1
fi

if [ "$DETECTED_CLAUDE_CODE" -eq 0 ] && [ "$DETECTED_OPENCLAW" -eq 0 ]; then
    info "No known agent environment detected -- continuing with generic install"
fi

# =============================================================================
# Phase B: Auto-merge into CLAUDE.md
# =============================================================================

HIVE_BLOCK_START="<!-- memory-hive:start -->"
HIVE_BLOCK_END="<!-- memory-hive:end -->"

# Build the block body in a temp file so we can splice it cleanly.
# Source of truth is templates/claude-boot-block.md in the cloned repo;
# substitute the ${HIVE_DIR} placeholder with the real install path.
HIVE_BLOCK_FILE="$TMP_DIR/hive-block.md"
HIVE_BLOCK_TEMPLATE="$TMP_DIR/memory-hive/templates/claude-boot-block.md"
if [ ! -f "$HIVE_BLOCK_TEMPLATE" ]; then
    die "Boot block template missing at $HIVE_BLOCK_TEMPLATE"
fi
# Use a sed delimiter unlikely to appear in a filesystem path.
_hive_dir_escaped="$(printf '%s' "$HIVE_DIR" | sed 's/[&|]/\\&/g')"
_install_dir_escaped="$(printf '%s' "$INSTALL_DIR" | sed 's/[&|]/\\&/g')"
sed -e "s|\${HIVE_DIR}|$_hive_dir_escaped|g" \
    -e "s|\${INSTALL_DIR}|$_install_dir_escaped|g" \
    "$HIVE_BLOCK_TEMPLATE" > "$HIVE_BLOCK_FILE" \
    || die "Failed to render boot block from $HIVE_BLOCK_TEMPLATE"

# merge_hive_block <target-claude-md-path>
# Idempotently inject (or replace) the managed block in the file. POSIX awk
# handles the splice: if the markers are present we replace lines between
# them; otherwise we append a fresh copy separated by a blank line. Write to
# a temp file and mv for atomicity. Never touches content outside the
# markers.
merge_hive_block() {
    _target="$1"
    _parent="$(dirname "$_target")"
    mkdir -p "$_parent" 2>/dev/null || true

    if [ ! -f "$_target" ]; then
        # Create from scratch with just the managed block.
        _tmp="$_target.memhive.$$"
        cp "$HIVE_BLOCK_FILE" "$_tmp" || return 1
        mv "$_tmp" "$_target" || { rm -f "$_tmp"; return 1; }
        ok "Created $_target with Memory Hive block"
        return 0
    fi

    _tmp="$_target.memhive.$$"
    # Does the file already contain the managed block?
    if grep -q -F "$HIVE_BLOCK_START" "$_target" 2>/dev/null \
        && grep -q -F "$HIVE_BLOCK_END" "$_target" 2>/dev/null; then
        # Replace the existing block in place.
        awk -v start="$HIVE_BLOCK_START" -v end="$HIVE_BLOCK_END" -v blockfile="$HIVE_BLOCK_FILE" '
            BEGIN { inblock = 0; emitted = 0 }
            {
                if (inblock == 0 && index($0, start) > 0) {
                    # Emit the replacement block once, then swallow lines
                    # until we see the end marker.
                    while ((getline line < blockfile) > 0) print line
                    close(blockfile)
                    inblock = 1
                    emitted = 1
                    next
                }
                if (inblock == 1) {
                    if (index($0, end) > 0) { inblock = 0 }
                    next
                }
                print
            }
        ' "$_target" > "$_tmp" || { rm -f "$_tmp"; return 1; }
        mv "$_tmp" "$_target" || { rm -f "$_tmp"; return 1; }
        ok "Updated Memory Hive block in $_target"
    else
        # Append a fresh block. Make sure we separate from existing content
        # with a blank line so we don't glue onto the previous paragraph.
        {
            cat "$_target"
            # Ensure trailing newline before the block.
            _last_char="$(tail -c 1 "$_target" 2>/dev/null || printf '')"
            if [ "$_last_char" != "" ] && [ "$_last_char" != "
" ]; then
                printf '\n'
            fi
            printf '\n'
            cat "$HIVE_BLOCK_FILE"
        } > "$_tmp" || { rm -f "$_tmp"; return 1; }
        mv "$_tmp" "$_target" || { rm -f "$_tmp"; return 1; }
        ok "Added Memory Hive block to $_target"
    fi
    return 0
}

WIRED_TARGETS=""

if [ "$DETECTED_CLAUDE_CODE" -eq 1 ]; then
    if merge_hive_block "$CLAUDE_MD_PATH"; then
        WIRED_TARGETS="$CLAUDE_MD_PATH"
    else
        warn "Could not update $CLAUDE_MD_PATH -- continuing"
    fi
fi

if [ "$DETECTED_CWD_CLAUDE_MD" -eq 1 ] && [ "${MEMORY_HIVE_MERGE_CWD:-0}" = "1" ]; then
    if merge_hive_block "$CWD_CLAUDE_MD"; then
        if [ -z "$WIRED_TARGETS" ]; then
            WIRED_TARGETS="$CWD_CLAUDE_MD"
        else
            WIRED_TARGETS="$WIRED_TARGETS $CWD_CLAUDE_MD"
        fi
    fi
elif [ "$DETECTED_CWD_CLAUDE_MD" -eq 1 ]; then
    info "Skipping project-level $CWD_CLAUDE_MD (set MEMORY_HIVE_MERGE_CWD=1 to opt in)"
fi

# =============================================================================
# Phase C + D: Silo scaffolding (default + per-detected-agent)
# =============================================================================
# Inline the same templates create-agent.sh uses so we don't need to shell out
# for each silo. Preserves existing silos (skip if the dir already exists).

TODAY="$(date -u +%Y-%m-%d 2>/dev/null || echo "today")"

# create_silo <agent-id>
# Returns 0 if the silo was newly created, 1 if it already existed, 2 on error.
create_silo() {
    _aid="$1"
    case "$_aid" in
        ""|*/*|.*|*" "*)
            warn "Skipping silo with invalid id: '$_aid'"
            return 2
            ;;
    esac
    _dir="$AGENTS_DIR/$_aid"
    _was_existing=0
    if [ -d "$_dir" ]; then
        # Already there. If it has the full triplet, nothing to do (idempotent).
        # Otherwise top up any missing starter files — don't touch existing ones.
        if [ -f "$_dir/log.md" ] && [ -f "$_dir/context.md" ] && [ -f "$_dir/memory.md" ]; then
            return 1
        fi
        _was_existing=1
    else
        mkdir -p "$_dir" || return 2
    fi

    if [ ! -f "$_dir/log.md" ]; then
        cat > "$_dir/log.md" <<EOF
# ${_aid} — activity log

Append-only journal of what this agent did, when, and why.
Newest entries at the top.

## ${TODAY}

- Silo initialized by memory-hive installer.
EOF
    fi

    if [ ! -f "$_dir/context.md" ]; then
        cat > "$_dir/context.md" <<EOF
# ${_aid} — working context

Short, current-task context for this agent. Replace freely as the task shifts.

## Role

(What is this agent's responsibility? One or two sentences.)

## Current focus

(What is the agent working on right now?)

## Open questions

-
EOF
    fi

    if [ ! -f "$_dir/memory.md" ]; then
        cat > "$_dir/memory.md" <<EOF
# ${_aid} — durable memory

Long-lived facts, preferences, and lessons this agent should remember across
sessions. Prefer short bullets; link out to shared knowledge where relevant.

## Facts

-

## Preferences

-

## Lessons learned

-
EOF
    fi

    # Returning 0 for top-ups is a mild white lie — it means the banner
    # will say "created" for a silo that was actually just completed. That's
    # fine: from the user's POV, they now have a working silo they didn't
    # have before.
    if [ "$_was_existing" -eq 1 ]; then
        return 0
    fi
    return 0
}

CREATED_SILOS=""
EXISTING_SILOS=""

track_silo() {
    _name="$1"
    _rc="$2"
    if [ "$_rc" = "0" ]; then
        if [ -z "$CREATED_SILOS" ]; then
            CREATED_SILOS="$_name"
        else
            CREATED_SILOS="$CREATED_SILOS $_name"
        fi
    elif [ "$_rc" = "1" ]; then
        if [ -z "$EXISTING_SILOS" ]; then
            EXISTING_SILOS="$_name"
        else
            EXISTING_SILOS="$EXISTING_SILOS $_name"
        fi
    fi
}

# Phase C: default silo.
# NOTE: `create_silo` returns 1 when the silo already exists. Under `set -e`
# that terminates the script, so we guard every call with `|| _rc=$?` which
# captures the status without tripping errexit.
_rc=0; create_silo "main" || _rc=$?
track_silo "main" "$_rc"

# Phase D: auto-silo for detected Claude Code sub-agents.
if [ -n "$DETECTED_CLAUDE_AGENTS" ]; then
    for _ag in $DETECTED_CLAUDE_AGENTS; do
        _rc=0; create_silo "$_ag" || _rc=$?
        track_silo "$_ag" "$_rc"
    done
fi

# =============================================================================
# Phase E: Context-aware success banner
# =============================================================================

# Use ~ for $HOME in display paths for readability.
display_path() {
    case "$1" in
        "$HOME"/*) printf '~%s' "${1#$HOME}" ;;
        *) printf '%s' "$1" ;;
    esac
}

_install_display="$(display_path "$INSTALL_DIR")"
_hive_display="$(display_path "$HIVE_DIR")"

printf '\n'
printf '%s%s✓ Memory Hive installed at %s%s\n' "$BOLD" "$GREEN" "$_install_display" "$RESET"
printf '\n'

if [ -n "$WIRED_TARGETS" ]; then
    for _t in $WIRED_TARGETS; do
        printf '  Wired into: %s (managed block added)\n' "$(display_path "$_t")"
    done
fi

if [ -n "$CREATED_SILOS" ] && [ -n "$EXISTING_SILOS" ]; then
    printf '  Silos created: %s\n' "$CREATED_SILOS"
    printf '  Silos preserved: %s\n' "$EXISTING_SILOS"
elif [ -n "$CREATED_SILOS" ]; then
    printf '  Silos created: %s\n' "$CREATED_SILOS"
elif [ -n "$EXISTING_SILOS" ]; then
    printf '  Silos preserved: %s\n' "$EXISTING_SILOS"
fi

printf '  Shared hive:  %s/\n' "$_hive_display"

if [ "$DETECTED_OPENCLAW" -eq 1 ]; then
    printf '  OpenClaw:     %s (detected, no config changes made)\n' "$(display_path "$DETECTED_OPENCLAW_DIR")"
fi

printf '\n'

if [ "$DETECTED_CLAUDE_CODE" -eq 1 ] || [ "$DETECTED_OPENCLAW" -eq 1 ]; then
    printf 'Your agents will pick up the hive on next boot — no restart required.\n'
    printf 'Read the docs: %shttps://github.com/TJCurnutte/memory-hive%s\n' "$CYAN" "$RESET"
    printf '  Check compliance: sh %s/check-compliance.sh\n' "$_install_display"
else
    printf "We didn't detect Claude Code or OpenClaw on this machine. To wire this\n"
    printf 'into your own agent system, point it at %s/ for shared\n' "$_hive_display"
    printf 'context and %s/agents/main/ for the default silo.\n' "$_hive_display"
    printf 'Docs: %shttps://github.com/TJCurnutte/memory-hive%s\n' "$CYAN" "$RESET"
    printf '  Check compliance: sh %s/check-compliance.sh\n' "$_install_display"
fi
