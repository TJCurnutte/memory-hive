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
# Default behavior: silent, zero user-input. Creates the `main` silo,
# wires the managed block into ~/.claude/CLAUDE.md if found, and exits.
# Add agents any time with `memory-hive add <name>`.
#
# Environment overrides:
#   MEMORY_HIVE_DIR=/custom/path   install location (default: $HOME/.memory-hive)
#   MEMORY_HIVE_WIZARD=1           run the interactive setup wizard (prompts
#                                  for agent count, names, roles; offers to
#                                  import agents from ~/.claude/agents/ and
#                                  ~/.openclaw/hive/agents/ if present)
#   MEMORY_HIVE_MERGE_CWD=1        also merge the hive block into $PWD/CLAUDE.md
#   MEMORY_HIVE_REPO=/local/path   install from a local working copy instead of
#                                  cloning (useful for development and tests)
#   MEMORY_HIVE_SKIP_CLAUDE_MD=1   don't modify ~/.claude/CLAUDE.md even if it
#                                  exists (useful for tests that shouldn't
#                                  touch the developer's real config)
#   MEMORY_HIVE_ONLY=hermes,cursor comma- or space-separated platform IDs;
#                                  wire ONLY these and filter every other
#                                  detected platform out (useful when you
#                                  have many agent platforms installed but
#                                  only want memory-hive wired into a subset)

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

if [ -n "${MEMORY_HIVE_REPO:-}" ] && [ -d "$MEMORY_HIVE_REPO/hive" ]; then
    info "Using local repo at $MEMORY_HIVE_REPO (MEMORY_HIVE_REPO override)"
    cp -R "$MEMORY_HIVE_REPO" "$TMP_DIR/memory-hive" \
        || die "Failed to copy local repo from $MEMORY_HIVE_REPO"
else
    info "Fetching latest from $REPO_URL"
    if ! git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR/memory-hive" 2>/tmp/memory-hive-clone.err; then
        cat /tmp/memory-hive-clone.err >&2 || true
        die "Failed to clone $REPO_URL. Check your network connection."
    fi
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
for helper in create-agent.sh update.sh install.sh check-compliance.sh memory-hive memory_hive_recall.py; do
    _src="$TMP_DIR/memory-hive/$helper"
    [ -f "$_src" ] || continue
    cp "$_src" "$INSTALL_DIR/$helper"
    chmod +x "$INSTALL_DIR/$helper" 2>/dev/null || true
done

# Install a bare `memory-hive` command into the user's existing PATH when
# possible. This is deliberately done in addition to installing
# $INSTALL_DIR/memory-hive: a piped installer (`curl ... | sh`) cannot mutate the
# parent shell's PATH for the very next pasted command, so the only way
# `memory-hive doctor` works immediately is to place a shim in a directory that
# is already on PATH.
COMMAND_SHIM_PATH=""
COMMAND_SHIM_STATUS="not-installed"
COMMAND_SHIM_NOTE=""
_install_memory_hive_command_shim() {
    _target="$INSTALL_DIR/memory-hive"
    [ -x "$_target" ] || return 0

    # Already available? Leave it alone, but record the path for the banner.
    _existing="$(command -v memory-hive 2>/dev/null || true)"
    if [ -n "$_existing" ]; then
        COMMAND_SHIM_PATH="$_existing"
        COMMAND_SHIM_STATUS="already-on-path"
        return 0
    fi

    # First pass: use an existing writable directory that is already on PATH.
    _old_ifs="$IFS"
    IFS=:
    for _dir in $PATH; do
        IFS="$_old_ifs"
        [ -n "$_dir" ] || _dir="."
        [ -d "$_dir" ] || { IFS=:; continue; }
        [ -w "$_dir" ] || { IFS=:; continue; }
        case "$_dir" in
            /bin|/sbin|/usr/bin|/usr/sbin|/System/*|/Library/Apple/*) IFS=:; continue ;;
        esac
        _shim="$_dir/memory-hive"
        if [ -e "$_shim" ]; then
            IFS=:
            continue
        fi
        _target_q="'$(printf '%s' "$_target" | sed "s/'/'\\\\''/g")'"
        if ln -s "$_target" "$_shim" 2>/dev/null || { printf '#!/bin/sh\nexec %s "$@"\n' "$_target_q" > "$_shim" 2>/dev/null && chmod +x "$_shim" 2>/dev/null; }; then
            COMMAND_SHIM_PATH="$_shim"
            COMMAND_SHIM_STATUS="installed-on-path"
            IFS="$_old_ifs"
            return 0
        fi
        IFS=:
    done
    IFS="$_old_ifs"

    # Fallback: create ~/.local/bin/memory-hive and persist PATH for future
    # shells. This cannot affect the already-running parent shell, but it keeps
    # the next terminal session zero-troubleshoot.
    _local_bin="$HOME/.local/bin"
    if mkdir -p "$_local_bin" 2>/dev/null; then
        _shim="$_local_bin/memory-hive"
        _target_q="'$(printf '%s' "$_target" | sed "s/'/'\\\\''/g")'"
        if [ ! -e "$_shim" ] && (ln -s "$_target" "$_shim" 2>/dev/null || { printf '#!/bin/sh\nexec %s "$@"\n' "$_target_q" > "$_shim" 2>/dev/null && chmod +x "$_shim" 2>/dev/null; }); then
            COMMAND_SHIM_PATH="$_shim"
            COMMAND_SHIM_STATUS="installed-profile-path"
            COMMAND_SHIM_NOTE="Restart your terminal, then run: memory-hive doctor"
            for _profile in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile"; do
                [ -f "$_profile" ] || continue
                if ! grep -q 'HOME/.local/bin' "$_profile" 2>/dev/null && ! grep -q '\.local/bin' "$_profile" 2>/dev/null; then
                    printf '\n# Memory Hive CLI\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$_profile" 2>/dev/null || true
                    break
                fi
            done
        fi
    fi
}
_install_memory_hive_command_shim

# Install role templates so the wizard and CLI can seed context.md from them.
if [ -d "$TMP_DIR/memory-hive/templates/roles" ]; then
    mkdir -p "$INSTALL_DIR/templates/roles"
    for _role in "$TMP_DIR/memory-hive/templates/roles/"*.md; do
        [ -f "$_role" ] || continue
        _role_name="$(basename "$_role")"
        # Always refresh templates from upstream (these are reference content,
        # not user data — the CLI reads them verbatim).
        cp "$_role" "$INSTALL_DIR/templates/roles/$_role_name"
    done
fi

# Install seed scenarios so `memory-hive seed` can populate a fresh hive.
# Each scenario is a directory tree under templates/scenarios/<name>/files/
# plus an agents.txt manifest. We copy the whole tree (POSIX `cp -R`) since
# nested dirs and date-marker files need to land verbatim.
if [ -d "$TMP_DIR/memory-hive/templates/scenarios" ]; then
    mkdir -p "$INSTALL_DIR/templates/scenarios"
    for _scn_src in "$TMP_DIR/memory-hive/templates/scenarios/"*; do
        [ -d "$_scn_src" ] || continue
        _scn_name="$(basename "$_scn_src")"
        _scn_dst="$INSTALL_DIR/templates/scenarios/$_scn_name"
        # Refresh: remove the existing copy first so renamed/deleted files
        # in upstream don't linger after an update.
        rm -rf "$_scn_dst"
        # `cp -R` is POSIX. The trailing /. on the source copies contents,
        # not the dir itself, so the destination structure stays correct.
        mkdir -p "$_scn_dst"
        cp -R "$_scn_src/." "$_scn_dst/"
    done
fi

if [ "$SYNC_MODE" = "1" ]; then
    ok "Memory Hive updated"
else
    ok "Memory Hive installed"
fi

# =============================================================================
# Phase A: Platform registry + detection
# =============================================================================
# One source of truth for which agent platforms we integrate with. Each row
# has: id, human-readable name, shell predicate that detects whether it's
# installed on this machine, target config file path, injection strategy,
# and the skip env var. Add a new platform by extending `_mh_platform_ids`
# and adding a case arm for each field getter.
#
# Injection strategies:
#   auto-inject   — write the managed block directly (Claude Code style)
#   manual        — detected only, print instructions pointing at
#                   templates/platforms/<id>.md so the user wires it themselves
#
# An `append` strategy is reserved for future cases where we want to
# append-without-markers; today every auto-inject target is markdown-safe
# for the markers so we use the same codepath as Claude Code.

# Space-separated list of platform ids, in the order we want to report.
# Order is deliberate: Claude Code first (existing behavior), then CLAUDE.md
# cousins, then the rest grouped loosely by ecosystem.
_mh_platform_ids="claude-code openclaw nanoclaw hermes cursor continue aider gemini-cli goose open-interpreter amazon-q openhands cline roo-code kilo-code windsurf zed warp amp codex opencode crush github-copilot"

# _mh_platform_field <id> <field>
# Prints the field value to stdout. Fields:
#   name       human-readable label
#   marker     shell expression; returns 0 if detected
#   target     absolute path the installer writes to (if auto-inject)
#   strategy   one of: auto-inject, manual
#   skip_env   name of the env var that opts this platform out
_mh_platform_field() {
    _id="$1"; _field="$2"
    case "$_id:$_field" in
        # ------- Claude Code (the original) -------
        claude-code:name)      printf 'Claude Code' ;;
        claude-code:marker)    [ -d "$HOME/.claude" ] ;;
        claude-code:target)    printf '%s/.claude/CLAUDE.md' "$HOME" ;;
        claude-code:strategy)  printf 'auto-inject' ;;
        claude-code:skip_env)  printf 'MEMORY_HIVE_SKIP_CLAUDE_CODE' ;;

        # ------- OpenClaw -------
        openclaw:name)         printf 'OpenClaw' ;;
        openclaw:marker)       [ -d "$HOME/.openclaw" ] ;;
        openclaw:target)       printf '%s/.openclaw/CLAUDE.md' "$HOME" ;;
        openclaw:strategy)     printf 'auto-inject' ;;
        openclaw:skip_env)     printf 'MEMORY_HIVE_SKIP_OPENCLAW' ;;

        # ------- NanoClaw -------
        nanoclaw:name)         printf 'NanoClaw' ;;
        nanoclaw:marker)       [ -d "$HOME/.config/nanoclaw" ] || [ -d "$HOME/.nanoclaw" ] ;;
        nanoclaw:target)       printf '%s/.config/nanoclaw/AGENTS.md' "$HOME" ;;
        nanoclaw:strategy)     printf 'auto-inject' ;;
        nanoclaw:skip_env)     printf 'MEMORY_HIVE_SKIP_NANOCLAW' ;;

        # ------- Hermes Agent -------
        hermes:name)           printf 'Hermes Agent' ;;
        hermes:marker)         [ -d "$HOME/.hermes" ] ;;
        hermes:target)         printf '%s/.hermes/memories/MEMORY.md' "$HOME" ;;
        hermes:strategy)       printf 'auto-inject' ;;
        hermes:skip_env)       printf 'MEMORY_HIVE_SKIP_HERMES' ;;

        # ------- Cursor -------
        cursor:name)           printf 'Cursor' ;;
        cursor:marker)         [ -d "$HOME/.cursor" ] ;;
        cursor:target)         printf '%s/.cursor/rules/memory-hive.mdc' "$HOME" ;;
        cursor:strategy)       printf 'auto-inject' ;;
        cursor:skip_env)       printf 'MEMORY_HIVE_SKIP_CURSOR' ;;

        # ------- Continue.dev -------
        continue:name)         printf 'Continue.dev' ;;
        continue:marker)       [ -d "$HOME/.continue" ] ;;
        continue:target)       printf '%s/.continue/rules/memory-hive.md' "$HOME" ;;
        continue:strategy)     printf 'auto-inject' ;;
        continue:skip_env)     printf 'MEMORY_HIVE_SKIP_CONTINUE' ;;

        # ------- Aider (manual — YAML config is structured) -------
        aider:name)            printf 'Aider' ;;
        aider:marker)          [ -f "$HOME/.aider.conf.yml" ] || command -v aider >/dev/null 2>&1 ;;
        aider:target)          printf '%s/templates/platforms/aider-conventions.md' "$INSTALL_DIR" ;;
        aider:strategy)        printf 'manual' ;;
        aider:skip_env)        printf 'MEMORY_HIVE_SKIP_AIDER' ;;

        # ------- Gemini CLI -------
        gemini-cli:name)       printf 'Gemini CLI' ;;
        gemini-cli:marker)     [ -d "$HOME/.gemini" ] ;;
        gemini-cli:target)     printf '%s/.gemini/GEMINI.md' "$HOME" ;;
        gemini-cli:strategy)   printf 'auto-inject' ;;
        gemini-cli:skip_env)   printf 'MEMORY_HIVE_SKIP_GEMINI_CLI' ;;

        # ------- Goose (Block) -------
        goose:name)            printf 'Goose (Block)' ;;
        goose:marker)          [ -d "$HOME/.config/goose" ] || [ -d "$HOME/.goose" ] ;;
        goose:target)          printf '%s/.goosehints' "$HOME" ;;
        goose:strategy)        printf 'auto-inject' ;;
        goose:skip_env)        printf 'MEMORY_HIVE_SKIP_GOOSE' ;;

        # ------- Open Interpreter (manual — profile YAML) -------
        open-interpreter:name)     printf 'Open Interpreter' ;;
        open-interpreter:marker)   [ -d "$HOME/.config/open-interpreter" ] || command -v interpreter >/dev/null 2>&1 ;;
        open-interpreter:target)   printf 'manual' ;;
        open-interpreter:strategy) printf 'manual' ;;
        open-interpreter:skip_env) printf 'MEMORY_HIVE_SKIP_OPEN_INTERPRETER' ;;

        # ------- Amazon Q Developer CLI -------
        amazon-q:name)         printf 'Amazon Q Developer CLI' ;;
        amazon-q:marker)       [ -d "$HOME/.aws/amazonq" ] ;;
        amazon-q:target)       printf '%s/.aws/amazonq/rules/memory-hive.md' "$HOME" ;;
        amazon-q:strategy)     printf 'auto-inject' ;;
        amazon-q:skip_env)     printf 'MEMORY_HIVE_SKIP_AMAZON_Q' ;;

        # ------- OpenHands -------
        openhands:name)        printf 'OpenHands' ;;
        openhands:marker)      [ -d "$HOME/.openhands" ] ;;
        openhands:target)      printf '%s/.openhands/microagents/memory-hive.md' "$HOME" ;;
        openhands:strategy)    printf 'auto-inject' ;;
        openhands:skip_env)    printf 'MEMORY_HIVE_SKIP_OPENHANDS' ;;

        # ------- Cline (manual — VS Code state DB) -------
        cline:name)            printf 'Cline (VS Code)' ;;
        cline:marker)          [ -d "$HOME/.cline" ] ;;
        cline:target)          printf 'manual' ;;
        cline:strategy)        printf 'manual' ;;
        cline:skip_env)        printf 'MEMORY_HIVE_SKIP_CLINE' ;;

        # ------- Roo Code -------
        roo-code:name)         printf 'Roo Code' ;;
        roo-code:marker)       [ -d "$HOME/.roo" ] ;;
        roo-code:target)       printf '%s/.roo/rules/memory-hive.md' "$HOME" ;;
        roo-code:strategy)     printf 'auto-inject' ;;
        roo-code:skip_env)     printf 'MEMORY_HIVE_SKIP_ROO_CODE' ;;

        # ------- Kilo Code -------
        kilo-code:name)        printf 'Kilo Code' ;;
        kilo-code:marker)      [ -d "$HOME/.kilocode" ] ;;
        kilo-code:target)      printf '%s/.kilocode/rules/memory-hive.md' "$HOME" ;;
        kilo-code:strategy)    printf 'auto-inject' ;;
        kilo-code:skip_env)    printf 'MEMORY_HIVE_SKIP_KILO_CODE' ;;

        # ------- Windsurf (Codeium) -------
        windsurf:name)         printf 'Windsurf (Codeium)' ;;
        windsurf:marker)       [ -d "$HOME/.codeium/windsurf" ] ;;
        windsurf:target)       printf '%s/.codeium/windsurf/memories/global_rules.md' "$HOME" ;;
        windsurf:strategy)     printf 'auto-inject' ;;
        windsurf:skip_env)     printf 'MEMORY_HIVE_SKIP_WINDSURF' ;;

        # ------- Zed (manual — settings.json is structured) -------
        zed:name)              printf 'Zed' ;;
        zed:marker)            [ -d "$HOME/.config/zed" ] ;;
        zed:target)            printf 'manual' ;;
        zed:strategy)          printf 'manual' ;;
        zed:skip_env)          printf 'MEMORY_HIVE_SKIP_ZED' ;;

        # ------- Warp -------
        warp:name)             printf 'Warp' ;;
        warp:marker)           [ -d "$HOME/.warp" ] ;;
        warp:target)           printf '%s/.agents/AGENTS.md' "$HOME" ;;
        warp:strategy)         printf 'auto-inject' ;;
        warp:skip_env)         printf 'MEMORY_HIVE_SKIP_WARP' ;;

        # ------- Sourcegraph Amp -------
        amp:name)              printf 'Sourcegraph Amp' ;;
        amp:marker)            [ -d "$HOME/.config/amp" ] || command -v amp >/dev/null 2>&1 ;;
        amp:target)            printf '%s/.config/amp/AGENTS.md' "$HOME" ;;
        amp:strategy)          printf 'auto-inject' ;;
        amp:skip_env)          printf 'MEMORY_HIVE_SKIP_AMP' ;;

        # ------- OpenAI Codex CLI -------
        codex:name)            printf 'OpenAI Codex CLI' ;;
        codex:marker)          [ -d "$HOME/.codex" ] ;;
        codex:target)          printf '%s/.codex/AGENTS.md' "$HOME" ;;
        codex:strategy)        printf 'auto-inject' ;;
        codex:skip_env)        printf 'MEMORY_HIVE_SKIP_CODEX' ;;

        # ------- OpenCode -------
        opencode:name)         printf 'OpenCode' ;;
        opencode:marker)       [ -d "$HOME/.config/opencode" ] ;;
        opencode:target)       printf '%s/.config/opencode/AGENTS.md' "$HOME" ;;
        opencode:strategy)     printf 'auto-inject' ;;
        opencode:skip_env)     printf 'MEMORY_HIVE_SKIP_OPENCODE' ;;

        # ------- Crush (Charm) -------
        crush:name)            printf 'Crush (Charm)' ;;
        crush:marker)          [ -d "$HOME/.local/share/crush" ] ;;
        crush:target)          printf 'manual' ;;
        crush:strategy)        printf 'manual' ;;
        crush:skip_env)        printf 'MEMORY_HIVE_SKIP_CRUSH' ;;

        # ------- GitHub Copilot (repo-level, opt-in) -------
        github-copilot:name)   printf 'GitHub Copilot (repo)' ;;
        github-copilot:marker) [ "${MEMORY_HIVE_COPILOT_REPO:-0}" = "1" ] && [ -d "$PWD/.git" ] ;;
        github-copilot:target) printf '%s/.github/copilot-instructions.md' "$PWD" ;;
        github-copilot:strategy) printf 'auto-inject' ;;
        github-copilot:skip_env) printf 'MEMORY_HIVE_SKIP_GITHUB_COPILOT' ;;

        *) return 1 ;;
    esac
    # Propagate the exit status of the matched arm. Critical for `marker`
    # predicates: they're `[ -d ... ]` tests whose truthiness is the answer.
    # printf-only arms exit 0 naturally, which is what we want too.
    return $?
}

# _mh_platform_is_skipped <id>
# Returns 0 if the platform's skip env var is set to 1, 1 otherwise.
_mh_platform_is_skipped() {
    _id="$1"
    _env_name="$(_mh_platform_field "$_id" skip_env 2>/dev/null || printf '')"
    [ -n "$_env_name" ] || return 1
    _val=0
    eval "_val=\${$_env_name:-0}"
    [ "$_val" = "1" ]
}

# _mh_platform_detected <id>
# Calls the marker predicate, honoring the skip env var. Returns 0 if
# detected AND not skipped.
_mh_platform_detected() {
    _id="$1"
    if _mh_platform_is_skipped "$_id"; then
        return 1
    fi
    _mh_platform_field "$_id" marker
}

# Detection state used outside the platform-table loop. The platform
# table handles per-platform config-file wiring; these vars support
# orthogonal flows: sub-agent auto-silo creation and the optional
# MEMORY_HIVE_MERGE_CWD behavior.
DETECTED_CLAUDE_AGENTS=""  # space-separated list of ~/.claude/agents/* subdir names
DETECTED_CWD_CLAUDE_MD=0

CLAUDE_AGENTS_DIR="$HOME/.claude/agents"
CWD_CLAUDE_MD="$PWD/CLAUDE.md"

info "Detecting agent environment"

# Claude Code sub-agent enumeration — only used for auto-silo creation,
# not for config-file wiring (that's handled by the platform table).
if [ -d "$CLAUDE_AGENTS_DIR" ]; then
    for _agent_path in "$CLAUDE_AGENTS_DIR"/*; do
        [ -d "$_agent_path" ] || continue
        _agent_name="$(basename "$_agent_path")"
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
if [ -f "$CWD_CLAUDE_MD" ]; then
    DETECTED_CWD_CLAUDE_MD=1
fi

# =============================================================================
# Phase B: Render boot block + wire detected platforms
# =============================================================================

HIVE_BLOCK_START="<!-- memory-hive:start -->"
HIVE_BLOCK_END="<!-- memory-hive:end -->"

# Build the block body in a temp file so we can splice it cleanly.
# Source of truth is templates/claude-boot-block.md in the cloned repo;
# substitute the ${HIVE_DIR} placeholder with the real install path. This
# block is platform-agnostic — every auto-inject target gets the same text.
HIVE_BLOCK_FILE="$TMP_DIR/hive-block.md"
HIVE_BLOCK_TEMPLATE="$TMP_DIR/memory-hive/templates/claude-boot-block.md"
if [ ! -f "$HIVE_BLOCK_TEMPLATE" ]; then
    die "Boot block template missing at $HIVE_BLOCK_TEMPLATE"
fi
_hive_dir_escaped="$(printf '%s' "$HIVE_DIR" | sed 's/[&|]/\\&/g')"
_install_dir_escaped="$(printf '%s' "$INSTALL_DIR" | sed 's/[&|]/\\&/g')"
sed -e "s|\${HIVE_DIR}|$_hive_dir_escaped|g" \
    -e "s|\${INSTALL_DIR}|$_install_dir_escaped|g" \
    "$HIVE_BLOCK_TEMPLATE" > "$HIVE_BLOCK_FILE" \
    || die "Failed to render boot block from $HIVE_BLOCK_TEMPLATE"

# Also render the aider-conventions.md template with the same
# substitutions, since it ships with unresolved ${HIVE_DIR} placeholders
# (so the source file in the repo stays portable). This is a tools-level
# file — keep it fresh on every install.
_aider_src="$TMP_DIR/memory-hive/templates/platforms/aider-conventions.md"
_aider_dst="$INSTALL_DIR/templates/platforms/aider-conventions.md"
if [ -f "$_aider_src" ]; then
    mkdir -p "$(dirname "$_aider_dst")" 2>/dev/null || true
    sed -e "s|\${HIVE_DIR}|$_hive_dir_escaped|g" \
        -e "s|\${INSTALL_DIR}|$_install_dir_escaped|g" \
        "$_aider_src" > "$_aider_dst" 2>/dev/null || true
fi

# Also ship all platform docs to the install dir so users can read them
# post-install without going back to the repo. Copy verbatim — no
# substitutions needed (the docs describe the setup, they aren't loaded
# by any agent).
_plat_src_dir="$TMP_DIR/memory-hive/templates/platforms"
_plat_dst_dir="$INSTALL_DIR/templates/platforms"
if [ -d "$_plat_src_dir" ]; then
    mkdir -p "$_plat_dst_dir" 2>/dev/null || true
    for _pf in "$_plat_src_dir"/*.md; do
        [ -f "$_pf" ] || continue
        _pname="$(basename "$_pf")"
        # Skip aider-conventions.md — already rendered above.
        [ "$_pname" = "aider-conventions.md" ] && continue
        cp "$_pf" "$_plat_dst_dir/$_pname" 2>/dev/null || true
    done
fi

# merge_hive_block <target-markdown-path>
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
        _tmp="$_target.memhive.$$"
        cp "$HIVE_BLOCK_FILE" "$_tmp" || return 1
        mv "$_tmp" "$_target" || { rm -f "$_tmp"; return 1; }
        return 0
    fi

    _tmp="$_target.memhive.$$"
    if grep -q -F "$HIVE_BLOCK_START" "$_target" 2>/dev/null \
        && grep -q -F "$HIVE_BLOCK_END" "$_target" 2>/dev/null; then
        awk -v start="$HIVE_BLOCK_START" -v end="$HIVE_BLOCK_END" -v blockfile="$HIVE_BLOCK_FILE" '
            BEGIN { inblock = 0; emitted = 0 }
            {
                if (inblock == 0 && index($0, start) > 0) {
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
    else
        {
            cat "$_target"
            _last_char="$(tail -c 1 "$_target" 2>/dev/null || printf '')"
            if [ "$_last_char" != "" ] && [ "$_last_char" != "
" ]; then
                printf '\n'
            fi
            printf '\n'
            cat "$HIVE_BLOCK_FILE"
        } > "$_tmp" || { rm -f "$_tmp"; return 1; }
        mv "$_tmp" "$_target" || { rm -f "$_tmp"; return 1; }
    fi
    return 0
}

# Track per-platform outcomes for the end-of-install banner.
#   PLATFORM_WIRED    — auto-inject succeeded
#   PLATFORM_MANUAL   — detected but user must copy a snippet
#   PLATFORM_SKIPPED  — detected but the skip env var was set
#
# Each is a newline-separated list of "<id>\t<message>".
PLATFORM_WIRED=""
PLATFORM_MANUAL=""
PLATFORM_SKIPPED=""
# shellcheck disable=SC2034
PLATFORM_GONE=""
WIRED_TARGETS=""  # legacy — kept for banner compatibility below

# Previous-run state. If $HIVE_DIR/.wired-platforms exists, every ID in it
# was wired on the last install. After this run we'll diff against the
# current wired set to spot platforms that were uninstalled between runs
# (banner prints them under "[gone ]" so users see the system noticed).
_prev_wired_file="$HIVE_DIR/.wired-platforms"
_prev_wired=""
if [ -f "$_prev_wired_file" ]; then
    _prev_wired=" $(tr '\n' ' ' < "$_prev_wired_file" 2>/dev/null) "
fi

# MEMORY_HIVE_ONLY: comma- or space-separated list of platform IDs. When
# set, any platform outside the list is filtered — even if detected and
# not skipped by its own skip env var. Empty/unset means "all detected".
_only_list=""
if [ -n "${MEMORY_HIVE_ONLY:-}" ]; then
    _only_list=" $(printf '%s' "$MEMORY_HIVE_ONLY" | tr ',' ' ') "
fi

_mh_record() {
    # _mh_record <list-var> <id> <message>
    _lv="$1"; _lid="$2"; _lmsg="$3"
    eval "_cur=\$$_lv"
    if [ -z "$_cur" ]; then
        eval "$_lv=\"\$_lid	\$_lmsg\""
    else
        eval "$_lv=\"\$_cur
\$_lid	\$_lmsg\""
    fi
}

# Handle the Claude Code legacy env var: if MEMORY_HIVE_SKIP_CLAUDE_MD=1
# is set, also treat MEMORY_HIVE_SKIP_CLAUDE_CODE as 1 for backward
# compatibility with pre-multi-platform installers.
if [ "${MEMORY_HIVE_SKIP_CLAUDE_MD:-0}" = "1" ]; then
    export MEMORY_HIVE_SKIP_CLAUDE_CODE=1
fi

for _pid in $_mh_platform_ids; do
    _pname="$(_mh_platform_field "$_pid" name)"
    # MEMORY_HIVE_ONLY filter: if the user set an explicit allow-list,
    # silently skip everything outside it. No SKIPPED record — the
    # user asked for only these, they don't want noise about the rest.
    if [ -n "$_only_list" ]; then
        case "$_only_list" in
            *" $_pid "*) : ;;  # in the allow-list, proceed
            *)
                # Only surface a skip-note if it would have been wired.
                if _mh_platform_field "$_pid" marker 2>/dev/null; then
                    _mh_record PLATFORM_SKIPPED "$_pid" "$_pname filtered by MEMORY_HIVE_ONLY"
                fi
                continue
                ;;
        esac
    fi
    # Detect (honoring per-platform skip env var).
    if _mh_platform_is_skipped "$_pid"; then
        # Only note skip if the platform would otherwise have been detected.
        if _mh_platform_field "$_pid" marker 2>/dev/null; then
            _mh_record PLATFORM_SKIPPED "$_pid" "$_pname skipped by env var"
        fi
        continue
    fi
    if ! _mh_platform_field "$_pid" marker 2>/dev/null; then
        continue
    fi

    _pstrat="$(_mh_platform_field "$_pid" strategy)"
    _ptarget="$(_mh_platform_field "$_pid" target)"

    case "$_pstrat" in
        auto-inject)
            if merge_hive_block "$_ptarget"; then
                _mh_record PLATFORM_WIRED "$_pid" "$_pname: wired $_ptarget"
                if [ -z "$WIRED_TARGETS" ]; then
                    WIRED_TARGETS="$_ptarget"
                else
                    WIRED_TARGETS="$WIRED_TARGETS $_ptarget"
                fi
                ok "$_pname: managed block written to $(printf '%s' "$_ptarget" | sed -e "s|^$HOME|~|")"
            else
                warn "$_pname: could not update $_ptarget -- continuing"
            fi
            ;;
        manual)
            _docs_display="$INSTALL_DIR/templates/platforms/$_pid.md"
            _mh_record PLATFORM_MANUAL "$_pid" "$_pname: manual setup, see $(printf '%s' "$_docs_display" | sed -e "s|^$HOME|~|")"
            ok "$_pname: detected — manual setup instructions at $(printf '%s' "$_docs_display" | sed -e "s|^$HOME|~|")"
            ;;
        *)
            warn "$_pname: unknown strategy '$_pstrat' — skipping"
            ;;
    esac
done

if [ -z "$PLATFORM_WIRED" ] && [ -z "$PLATFORM_MANUAL" ] && [ -z "$PLATFORM_SKIPPED" ]; then
    info "No known agent platform detected -- continuing with generic install"
fi

# Optional: merge into $PWD/CLAUDE.md when the user explicitly opts in.
# Kept as a separate knob (MEMORY_HIVE_MERGE_CWD=1) rather than a platform
# entry because project-level CLAUDE.md is per-repo, not per-machine.
if [ "$DETECTED_CWD_CLAUDE_MD" -eq 1 ] && [ "${MEMORY_HIVE_MERGE_CWD:-0}" = "1" ]; then
    if merge_hive_block "$CWD_CLAUDE_MD"; then
        ok "Project CLAUDE.md: managed block written to $CWD_CLAUDE_MD"
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
# Phase D.5: Interactive wizard (tty only, best-effort)
# =============================================================================
# Adds two flows:
#   - Fresh install (no non-main silos present): ask how many agents to create
#     and for each one: name + role template.
#   - Re-install (non-main silos already present): ask keep/add/fresh/select.
#
# Default behavior: first-run setup wizard when the installer has a real tty.
# `curl ... | sh` gets a guided setup automatically on a clean hive, while
# reinstalls with existing agents stay non-interactive unless the user asks for
# `MEMORY_HIVE_WIZARD=1` or runs `memory-hive setup`.
#
# Set MEMORY_HIVE_WIZARD=0 to force silent install.

WIZARD_MODE="${MEMORY_HIVE_WIZARD:-auto}"

# Decide where the wizard reads from (only relevant when WIZARD is enabled):
#   - stdin is a tty                          → read from stdin directly
#   - stdin NOT tty, stdout IS tty, /dev/tty  → treat as `curl | sh` running
#     interactively; open /dev/tty on FD 3 and read from there
#   - otherwise                               → read from stdin and let EOF
#     naturally end the wizard (covers `sh install.sh < /dev/null` for CI,
#     heredoc-driven tests, and any other piped input)
#
# $WIZARD_TTY ends up: "stdin", "fd3", or "" (no wizard).
WIZARD_TTY=""
case "$WIZARD_MODE" in
    0|false|FALSE|no|NO|off|OFF)
        :
        ;;
    *)
        if [ -t 0 ]; then
            WIZARD_TTY="stdin"
        elif [ -t 1 ] && [ -r /dev/tty ] && { exec 3</dev/tty; } 2>/dev/null; then
            WIZARD_TTY="fd3"
        elif [ "$WIZARD_MODE" != "auto" ] && { [ -p /dev/stdin ] 2>/dev/null || [ -f /dev/stdin ] 2>/dev/null; }; then
            # Explicit wizard with piped/redirected stdin — e.g. heredoc tests.
            # Reads return EOF cleanly if the stream is empty.
            WIZARD_TTY="stdin"
        fi
        ;;
esac

# _wizard_read <varname> [default]
# Read a line from the wizard tty into the named variable. Honors $default if
# the user just hits enter. Returns 1 if we hit EOF (user cancelled or lost
# the tty mid-flow).
_wizard_read() {
    _mh_var="$1"
    _mh_default="${2:-}"
    _mh_line=""
    if [ "$WIZARD_TTY" = "fd3" ]; then
        IFS= read -r _mh_line <&3 || return 1
    else
        IFS= read -r _mh_line || return 1
    fi
    if [ -z "$_mh_line" ] && [ -n "$_mh_default" ]; then
        _mh_line="$_mh_default"
    fi
    # Portable indirect assignment.
    eval "$_mh_var=\$_mh_line"
    return 0
}

# _sanitize_name <raw> -> prints sanitized name to stdout.
# Rules: lowercase, letters/digits/dashes only, spaces->dashes, strip leading/
# trailing dashes, collapse multiple dashes, cap at 32 chars. Prints empty
# if the sanitized result is empty or just dashes.
_sanitize_name() {
    _raw="$1"
    # Replace spaces with dashes first, then lowercase, then strip anything
    # that isn't [a-z0-9-], then collapse/trim dashes.
    _name="$(printf '%s' "$_raw" \
        | tr ' ' '-' \
        | tr '[:upper:]' '[:lower:]' \
        | tr -cd 'a-z0-9-' \
        | sed -e 's/-\{2,\}/-/g' -e 's/^-//' -e 's/-$//')"
    # Cap at 32 chars.
    _name="$(printf '%s' "$_name" | cut -c1-32)"
    # Re-strip trailing dash if the cut produced one.
    _name="$(printf '%s' "$_name" | sed -e 's/-$//')"
    case "$_name" in
        ""|*[!a-z0-9-]*)
            printf ''
            return
            ;;
    esac
    printf '%s' "$_name"
}

# _role_text_for_template <template-name> -> prints role paragraph to stdout.
# Returns empty (and prints nothing) if the template isn't known / file missing.
# Callers should check for empty output, not exit status — command
# substitution eats exit codes anyway.
_role_text_for_template() {
    _tpl="$1"
    _tpl_file="$TMP_DIR/memory-hive/templates/roles/$_tpl.md"
    if [ -f "$_tpl_file" ]; then
        cat "$_tpl_file"
    fi
}

# _print_role_menu: print the numbered role template menu to stderr so it
# never mixes with captured stdout.
_print_role_menu() {
    printf '\n' >&2
    printf '  Role — pick a template or type your own:\n' >&2
    printf '    [1] coder       Writes and edits code; runs tests before shipping.\n' >&2
    printf '    [2] reviewer    Reviews code and designs for correctness and security.\n' >&2
    printf '    [3] researcher  Deep-dives on open questions with sources cited.\n' >&2
    printf '    [4] writer      Drafts and edits prose; tightens verbose writing.\n' >&2
    printf '    [5] planner     Breaks big tasks into concrete steps.\n' >&2
    printf '    [6] custom      Type your own description.\n' >&2
    printf '    [0] skip        Leave role blank for now.\n' >&2
}

# _resolve_role_choice <choice> -> writes role text to $WIZARD_ROLE_OUT or
# leaves it empty for skip. Returns 1 if the choice was invalid.
WIZARD_ROLE_OUT=""
_resolve_role_choice() {
    _choice="$1"
    WIZARD_ROLE_OUT=""
    case "$_choice" in
        0|"") return 0 ;;
        1) WIZARD_ROLE_OUT="$(_role_text_for_template coder)" ;;
        2) WIZARD_ROLE_OUT="$(_role_text_for_template reviewer)" ;;
        3) WIZARD_ROLE_OUT="$(_role_text_for_template researcher)" ;;
        4) WIZARD_ROLE_OUT="$(_role_text_for_template writer)" ;;
        5) WIZARD_ROLE_OUT="$(_role_text_for_template planner)" ;;
        6)
            printf '  Role description (one paragraph, end with a blank line):\n' >&2
            _custom=""
            while :; do
                _line=""
                if ! _wizard_read _line; then break; fi
                [ -z "$_line" ] && break
                if [ -z "$_custom" ]; then
                    _custom="$_line"
                else
                    _custom="$_custom
$_line"
                fi
            done
            WIZARD_ROLE_OUT="$_custom"
            ;;
        *) return 1 ;;
    esac
    return 0
}

# _wizard_create_one <name> <role-text>
# Creates the silo directly via create_silo then, if role is non-empty,
# rewrites the Role section in context.md. Re-uses create_silo to keep the
# file layout in sync with the rest of the installer.
_wizard_create_one() {
    _wname="$1"
    _wrole="$2"
    _rc=0
    create_silo "$_wname" || _rc=$?
    if [ "$_rc" = "2" ]; then
        warn "Skipped '$_wname' (could not create silo)"
        return 1
    fi
    track_silo "$_wname" "$_rc"
    if [ -n "$_wrole" ]; then
        _wfile="$AGENTS_DIR/$_wname/context.md"
        if [ -f "$_wfile" ]; then
            # Write role to a file so awk can read it — awk -v with multi-line
            # strings fails on several awks (macOS BWK awk, mawk).
            _wrolefile="$TMP_DIR/wizard-role-$$.md"
            printf '%s\n' "$_wrole" > "$_wrolefile"
            _wtmp="$_wfile.wizard.$$"
            if awk -v rolefile="$_wrolefile" '
                BEGIN { inrole = 0 }
                /^## Role$/ {
                    print
                    print ""
                    while ((getline line < rolefile) > 0) print line
                    close(rolefile)
                    inrole = 1
                    next
                }
                {
                    if (inrole == 1) {
                        if ($0 ~ /^## /) {
                            print ""
                            print
                            inrole = 0
                            next
                        }
                        next
                    }
                    print
                }
            ' "$_wfile" > "$_wtmp"; then
                mv "$_wtmp" "$_wfile" || { rm -f "$_wtmp"; return 1; }
            else
                rm -f "$_wtmp"
                return 1
            fi
            rm -f "$_wrolefile"
        fi
    fi
    return 0
}

# _wizard_archive_agent <name> <date>
# Move a silo to hive/agents/_archived/<date>/<name>/. Never deletes.
_wizard_archive_agent() {
    _aname="$1"
    _adate="$2"
    _src="$AGENTS_DIR/$_aname"
    [ -d "$_src" ] || return 1
    _arch_root="$AGENTS_DIR/_archived/$_adate"
    mkdir -p "$_arch_root" || return 1
    _dst="$_arch_root/$_aname"
    if [ -e "$_dst" ]; then
        # Append a suffix to avoid clobbering a previous archive of same name.
        _i=1
        while [ -e "${_dst}.${_i}" ]; do _i=$((_i + 1)); done
        _dst="${_dst}.${_i}"
    fi
    mv "$_src" "$_dst" || return 1
    return 0
}

# _list_non_main_agents: prints space-separated list of non-main, non-archived
# agent names present in AGENTS_DIR.
_list_non_main_agents() {
    _out=""
    if [ -d "$AGENTS_DIR" ]; then
        for _p in "$AGENTS_DIR"/*; do
            [ -d "$_p" ] || continue
            _n="$(basename "$_p")"
            case "$_n" in
                main|_archived|.*) continue ;;
            esac
            if [ -z "$_out" ]; then _out="$_n"; else _out="$_out $_n"; fi
        done
    fi
    printf '%s' "$_out"
}

# Where to look for pre-existing agent rosters we can import from.
# Users often have agents defined by Claude Code (~/.claude/agents/) or in a
# prior OpenClaw hive (~/.openclaw/hive/agents/). On a fresh memory-hive
# install, detecting those means the wizard can offer to seed silos instead
# of asking the user to retype the roster.
CLAUDE_AGENTS_DIR_DEFAULT="$HOME/.claude/agents"
OPENCLAW_AGENTS_DIR_DEFAULT="$HOME/.openclaw/hive/agents"

# _list_importable_agents: dedupes names found under the Claude Code agents
# dir and an existing OpenClaw hive agents dir. Skips 'main', '_archived',
# dotfiles, and anything whose sanitized name is empty. Prints
# space-separated names to stdout.
_list_importable_agents() {
    _out=""
    _seen=" "
    for _src in "$CLAUDE_AGENTS_DIR_DEFAULT" "$OPENCLAW_AGENTS_DIR_DEFAULT"; do
        [ -d "$_src" ] || continue
        for _p in "$_src"/*; do
            [ -e "$_p" ] || continue
            _bn="$(basename "$_p")"
            # strip common definition-file suffixes
            _bn="${_bn%.md}"
            _bn="${_bn%.yaml}"
            _bn="${_bn%.yml}"
            _bn="${_bn%.json}"
            case "$_bn" in
                main|_archived|.*|'*'|CONTRIBUTION_TEMPLATE|SILO_README) continue ;;
            esac
            _n="$(_sanitize_name "$_bn")"
            [ -n "$_n" ] || continue
            case "$_seen" in
                *" $_n "*) continue ;;
            esac
            _seen="$_seen$_n "
            if [ -z "$_out" ]; then _out="$_n"; else _out="$_out $_n"; fi
        done
    done
    printf '%s' "$_out"
}

# _guess_role_template_for_name <name>
# Heuristic: if the agent's name matches or contains a role-like word,
# return the matching template name. Falls back to empty for unknown names
# so the caller can leave the role blank.
_guess_role_template_for_name() {
    _gname="$1"
    case "$_gname" in
        coder|*-coder|coder-*|*-code|code-*|*developer*|*-dev|dev-*|*-eng|eng-*|*-engineer|engineer-*)
            printf 'coder' ;;
        reviewer|*-reviewer|reviewer-*|*-auditor|auditor-*|*-review|review-*|*-audit|audit-*)
            printf 'reviewer' ;;
        researcher|*-researcher|researcher-*|*-research|research-*|*-analyst|analyst-*|*-analysis|analysis-*)
            printf 'researcher' ;;
        writer|*-writer|writer-*|*-strategist|strategist-*|*-copy|copy-*|*-editor|editor-*)
            printf 'writer' ;;
        planner|*-planner|planner-*|*-specialist|specialist-*|coordinator|*-coordinator|coordinator-*|*-pm|pm-*)
            printf 'planner' ;;
        *)
            printf '' ;;
    esac
}

# _wizard_import_one <name>
# Create a silo for <name>, seed a role from (1) OpenClaw's existing
# context.md if it has real content, else (2) a template whose name matches
# the agent name, else leave blank. For log.md and memory.md: copy from
# OpenClaw only if the destination is empty.
_wizard_import_one() {
    _iname="$1"
    _rc=0
    create_silo "$_iname" || _rc=$?
    if [ "$_rc" = "2" ]; then
        warn "Skipped '$_iname' (could not create silo)"
        return 1
    fi
    track_silo "$_iname" "$_rc"

    _src_dir="$OPENCLAW_AGENTS_DIR_DEFAULT/$_iname"

    # Copy log.md and memory.md from OpenClaw if dest is still empty.
    if [ -d "$_src_dir" ]; then
        for _f in log.md memory.md; do
            _src_f="$_src_dir/$_f"
            _dst_f="$AGENTS_DIR/$_iname/$_f"
            if [ -f "$_src_f" ] && [ ! -s "$_dst_f" ]; then
                cp "$_src_f" "$_dst_f" 2>/dev/null || true
            fi
        done
    fi

    # Seed a role: prefer existing OpenClaw context.md content (if it has
    # something other than the placeholder), then a matching template.
    _role_text=""
    _src_ctx="$_src_dir/context.md"
    if [ -f "$_src_ctx" ] && grep -q "^## Role$" "$_src_ctx" 2>/dev/null; then
        # Extract the block between "## Role" and the next "## " heading.
        _extracted="$(awk '
            /^## Role$/ { capture=1; next }
            capture==1 && /^## / { exit }
            capture==1 { print }
        ' "$_src_ctx" | sed -e 's/^[[:space:]]*//' -e '/^$/d' | head -c 2000)"
        case "$_extracted" in
            ""|"(What is this agent"*) : ;;  # placeholder — skip
            *) _role_text="$_extracted" ;;
        esac
    fi
    if [ -z "$_role_text" ]; then
        _tpl="$(_guess_role_template_for_name "$_iname")"
        if [ -n "$_tpl" ]; then
            _role_text="$(_role_text_for_template "$_tpl")"
        fi
    fi

    if [ -n "$_role_text" ]; then
        _wfile="$AGENTS_DIR/$_iname/context.md"
        if [ -f "$_wfile" ]; then
            _wrolefile="$TMP_DIR/wizard-import-role-$$.md"
            printf '%s\n' "$_role_text" > "$_wrolefile"
            _wtmp="$_wfile.import.$$"
            if awk -v rolefile="$_wrolefile" '
                BEGIN { inrole = 0 }
                /^## Role$/ {
                    print
                    print ""
                    while ((getline line < rolefile) > 0) print line
                    close(rolefile)
                    inrole = 1
                    next
                }
                {
                    if (inrole == 1) {
                        if ($0 ~ /^## /) {
                            print ""
                            print
                            inrole = 0
                            next
                        }
                        next
                    }
                    print
                }
            ' "$_wfile" > "$_wtmp"; then
                mv "$_wtmp" "$_wfile" || { rm -f "$_wtmp"; return 1; }
            else
                rm -f "$_wtmp"
                return 1
            fi
            rm -f "$_wrolefile"
        fi
    fi
    return 0
}

# _wizard_fresh_flow: prompt for N, then for each agent name + role.
_wizard_fresh_flow() {
    printf '\n' >&2
    printf '%sLet'\''s set up your agents.%s (besides '\''main'\'', who is always here)\n' \
        "$BOLD" "$RESET" >&2
    printf '\n' >&2
    printf 'How many agents do you want under Chief of Staff? [0-10, default 3]: ' >&2
    _count_raw=""
    if ! _wizard_read _count_raw "3"; then
        warn "Lost tty mid-wizard; skipping remaining prompts"
        return 0
    fi
    case "$_count_raw" in
        ""|*[!0-9]*) _count=3 ;;
        *) _count="$_count_raw" ;;
    esac
    if [ "$_count" -gt 10 ]; then _count=10; fi
    if [ "$_count" -lt 0 ]; then _count=0; fi
    if [ "$_count" -eq 0 ]; then
        printf '  No extra agents — just main. (Add later with '\''memory-hive add <name>'\'').\n' >&2
        return 0
    fi

    _i=1
    _blank_retries=0
    while [ "$_i" -le "$_count" ]; do
        printf '\n' >&2
        printf '  Agent %s of %s\n' "$_i" "$_count" >&2
        _name=""
        _sanitized=""
        while :; do
            printf '    Name (lowercase, letters/digits/dashes): ' >&2
            _raw=""
            if ! _wizard_read _raw; then return 0; fi
            # If the stream is empty (CI / lost tty), bail out after a couple
            # of retries so we don't loop forever on EOF echo.
            if [ -z "$_raw" ]; then
                _blank_retries=$((_blank_retries + 1))
                if [ "$_blank_retries" -ge 3 ]; then
                    warn "No name provided after 3 tries — skipping remaining agents"
                    return 0
                fi
                printf '    Name must contain letters or digits. Try again.\n' >&2
                continue
            fi
            _blank_retries=0
            _sanitized="$(_sanitize_name "$_raw")"
            if [ -z "$_sanitized" ]; then
                printf '    Name must contain letters or digits. Try again.\n' >&2
                continue
            fi
            if [ "$_sanitized" = "main" ] || [ "$_sanitized" = "_archived" ]; then
                printf '    "%s" is reserved. Pick a different name.\n' "$_sanitized" >&2
                continue
            fi
            if [ -d "$AGENTS_DIR/$_sanitized" ]; then
                printf '    A silo named "%s" already exists. Pick a different name.\n' "$_sanitized" >&2
                continue
            fi
            # Always confirm — lets the user abort a sanitization surprise and
            # aligns the wizard's input stream with the documented test flow.
            printf '    Create '\''%s'\''? [Y/n]: ' "$_sanitized" >&2
            _ok=""
            if ! _wizard_read _ok "y"; then return 0; fi
            case "$_ok" in
                n|N|no|NO|No) continue ;;
            esac
            break
        done
        _name="$_sanitized"

        _print_role_menu
        printf '  Choice [1-6, 0 to skip]: ' >&2
        _choice=""
        if ! _wizard_read _choice "0"; then return 0; fi
        if ! _resolve_role_choice "$_choice"; then
            warn "Unknown role choice '$_choice' — leaving role blank"
            WIZARD_ROLE_OUT=""
        fi

        _wizard_create_one "$_name" "$WIZARD_ROLE_OUT" || true
        _i=$((_i + 1))
    done
}

# _wizard_reconcile_flow: prompt keep/add/fresh/select for an existing install.
_wizard_reconcile_flow() {
    _existing="$1"
    _date="$(date -u +%Y-%m-%d 2>/dev/null || echo "today")"
    printf '\n' >&2
    printf '%sMemory Hive is already installed.%s\n' "$BOLD" "$RESET" >&2
    printf 'Existing agents: main %s\n' "$_existing" >&2
    printf '\n' >&2
    printf '  [k] Keep existing (default) — just update the managed block and shared hive\n' >&2
    printf '  [a] Add more alongside existing\n' >&2
    printf '  [f] Fresh start — archive existing agents to hive/agents/_archived/%s/\n' "$_date" >&2
    printf '  [s] Select — review each and keep or archive\n' >&2
    printf '\nChoice [k]: ' >&2
    _pick=""
    if ! _wizard_read _pick "k"; then return 0; fi
    case "$_pick" in
        k|K|keep) return 0 ;;
        a|A|add)
            _wizard_fresh_flow
            return 0
            ;;
        f|F|fresh)
            for _ag in $_existing; do
                if _wizard_archive_agent "$_ag" "$_date"; then
                    ok "Archived $_ag to hive/agents/_archived/$_date/$_ag"
                else
                    warn "Could not archive $_ag"
                fi
            done
            _wizard_fresh_flow
            return 0
            ;;
        s|S|select)
            for _ag in $_existing; do
                printf '  Keep '\''%s'\''? [Y/n]: ' "$_ag" >&2
                _ans=""
                if ! _wizard_read _ans "y"; then return 0; fi
                case "$_ans" in
                    n|N|no|NO|No)
                        if _wizard_archive_agent "$_ag" "$_date"; then
                            ok "Archived $_ag to hive/agents/_archived/$_date/$_ag"
                        else
                            warn "Could not archive $_ag"
                        fi
                        ;;
                esac
            done
            printf '\nAdd new agents now? [y/N]: ' >&2
            _more=""
            if ! _wizard_read _more "n"; then return 0; fi
            case "$_more" in
                y|Y|yes|YES|Yes) _wizard_fresh_flow ;;
            esac
            return 0
            ;;
        *)
            warn "Unrecognized choice '$_pick' — keeping existing (default)"
            return 0
            ;;
    esac
}

# _wizard_import_flow: offered when the user has a clean memory-hive install
# but has agents defined elsewhere on the machine (Claude Code sub-agents,
# existing OpenClaw hive). Lets them import the whole roster, pick a subset,
# or skip and run the fresh-flow wizard from scratch.
_wizard_import_flow() {
    _names="$1"
    printf '\n' >&2
    printf '%sFound existing agents on this machine:%s\n' "$BOLD" "$RESET" >&2
    if [ -d "$CLAUDE_AGENTS_DIR_DEFAULT" ]; then
        printf '  ~/.claude/agents/\n' >&2
    fi
    if [ -d "$OPENCLAW_AGENTS_DIR_DEFAULT" ]; then
        printf '  ~/.openclaw/hive/agents/\n' >&2
    fi
    printf '  Detected: %s\n' "$_names" >&2
    printf '\n' >&2
    printf '  [i] Import all (default) — scaffold a silo for each, seed from OpenClaw if present\n' >&2
    printf '  [s] Select — pick which ones to import\n' >&2
    printf '  [n] Skip — start fresh with the wizard instead\n' >&2
    printf '\nChoice [i]: ' >&2
    _pick=""
    if ! _wizard_read _pick "i"; then return 0; fi
    case "$_pick" in
        i|I|import|"")
            for _ag in $_names; do
                _wizard_import_one "$_ag" || true
            done
            printf '\nAdd more agents via the wizard now? [y/N]: ' >&2
            _more=""
            if ! _wizard_read _more "n"; then return 0; fi
            case "$_more" in
                y|Y|yes|YES|Yes) _wizard_fresh_flow ;;
            esac
            ;;
        s|S|select)
            for _ag in $_names; do
                printf '  Import '\''%s'\''? [Y/n]: ' "$_ag" >&2
                _ans=""
                if ! _wizard_read _ans "y"; then return 0; fi
                case "$_ans" in
                    n|N|no|NO|No) continue ;;
                esac
                _wizard_import_one "$_ag" || true
            done
            printf '\nAdd more agents via the wizard now? [y/N]: ' >&2
            _more=""
            if ! _wizard_read _more "n"; then return 0; fi
            case "$_more" in
                y|Y|yes|YES|Yes) _wizard_fresh_flow ;;
            esac
            ;;
        n|N|no|NO|No|skip)
            _wizard_fresh_flow
            ;;
        *)
            warn "Unrecognized choice '$_pick' — importing all (default)"
            for _ag in $_names; do
                _wizard_import_one "$_ag" || true
            done
            ;;
    esac
}

WIZARD_RAN=0
WIZARD_AUTO_SKIPPED=0
if [ -n "$WIZARD_TTY" ]; then
    _existing_nonmain="$(_list_non_main_agents)"
    if [ -n "$_existing_nonmain" ]; then
        if [ "$WIZARD_MODE" = "auto" ]; then
            # Reinstall/update path: don't drop the user into reconciliation by
            # surprise. They can run `memory-hive setup` when they want it.
            WIZARD_AUTO_SKIPPED=1
        else
            _wizard_reconcile_flow "$_existing_nonmain"
            WIZARD_RAN=1
        fi
    else
        _importable="$(_list_importable_agents)"
        if [ -n "$_importable" ]; then
            _wizard_import_flow "$_importable"
        else
            _wizard_fresh_flow
        fi
        WIZARD_RAN=1
    fi
fi

# Close the tty fd if we opened one.
if [ "$WIZARD_TTY" = "fd3" ]; then
    exec 3<&- 2>/dev/null || true
fi

# Refresh hive/registry/AGENTS.md now that silos are (re)populated. Covers
# fresh/import/reconcile flows alike; if the CLI isn't available for some
# reason, silently skip — the registry is a convenience, not a correctness
# gate.
if [ -x "$INSTALL_DIR/memory-hive" ]; then
    MEMORY_HIVE_DIR="$INSTALL_DIR" sh "$INSTALL_DIR/memory-hive" register \
        >/dev/null 2>&1 || true
fi

# =============================================================================
# Phase E: Context-aware success banner
# =============================================================================

# Use ~ for $HOME in display paths for readability.
display_path() {
    case "$1" in
        "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;;
        *) printf '%s' "$1" ;;
    esac
}

_install_display="$(display_path "$INSTALL_DIR")"
_hive_display="$(display_path "$HIVE_DIR")"

printf '\n'
printf '%s%s✓ Memory Hive installed at %s%s\n' "$BOLD" "$GREEN" "$_install_display" "$RESET"
printf '\n'

# Per-platform status lines. One row per detected platform so the user
# sees exactly what got wired, what needs manual setup, and what was
# skipped. Newline-separated lists with "<id>\t<message>" per entry.
_emit_platform_lines() {
    _lv="$1"; _label="$2"
    eval "_content=\$$_lv"
    [ -n "$_content" ] || return 0
    printf '%s\n' "$_content" | while IFS='	' read -r _pid _pmsg; do
        [ -n "$_pid" ] || continue
        printf '  [%s] %s\n' "$_label" "$_pmsg"
    done
}

# Set the telemetry baseline AFTER all installer + wizard writes are done
# but BEFORE the banner prints. Any file in the hive with mtime > this
# baseline is real agent activity, not installer scaffolding.
# `memory-hive stats` reads this file to filter out the initial template
# writes — otherwise new installs would show ~13 "writes" just from the
# scaffolding and the counter would lie.
touch "$HIVE_DIR/.baseline-installed" 2>/dev/null || true

# Diff previous-run wired state against this run's → anything missing
# was uninstalled between runs. Record under PLATFORM_GONE so the
# banner can surface it honestly.
_current_wired_ids=""
if [ -n "$PLATFORM_WIRED" ]; then
    _current_wired_ids=" $(printf '%s\n' "$PLATFORM_WIRED" | awk -F'	' '{print $1}' | tr '\n' ' ') "
fi
for _ppid in $_prev_wired; do
    [ -n "$_ppid" ] || continue
    case "$_current_wired_ids" in
        *" $_ppid "*) continue ;;   # still wired, no delta
        *)
            _pgone_name="$(_mh_platform_field "$_ppid" name 2>/dev/null)"
            [ -n "$_pgone_name" ] || _pgone_name="$_ppid"
            _mh_record PLATFORM_GONE "$_ppid" "$_pgone_name: no longer detected (cleaned up with the uninstall)"
            ;;
    esac
done

# Persist current state for the next run's diff.
if [ -n "$PLATFORM_WIRED" ]; then
    printf '%s\n' "$PLATFORM_WIRED" | awk -F'	' '{print $1}' > "$_prev_wired_file" 2>/dev/null || true
else
    : > "$_prev_wired_file" 2>/dev/null || true
fi

_emit_platform_lines PLATFORM_WIRED   "wired"
_emit_platform_lines PLATFORM_GONE    "gone "
_emit_platform_lines PLATFORM_MANUAL  "manual"
_emit_platform_lines PLATFORM_SKIPPED "skip "

if [ -n "$CREATED_SILOS" ] && [ -n "$EXISTING_SILOS" ]; then
    printf '  Silos created: %s\n' "$CREATED_SILOS"
    printf '  Silos preserved: %s\n' "$EXISTING_SILOS"
elif [ -n "$CREATED_SILOS" ]; then
    printf '  Silos created: %s\n' "$CREATED_SILOS"
elif [ -n "$EXISTING_SILOS" ]; then
    printf '  Silos preserved: %s\n' "$EXISTING_SILOS"
fi

printf '  Shared hive:  %s/\n' "$_hive_display"
case "$COMMAND_SHIM_STATUS" in
    installed-on-path)
        printf '  Command ready: memory-hive (%s)\n' "$(display_path "$COMMAND_SHIM_PATH")"
        ;;
    already-on-path)
        printf '  Command ready: memory-hive (%s)\n' "$(display_path "$COMMAND_SHIM_PATH")"
        ;;
    installed-profile-path)
        printf '  Command installed for new shells: memory-hive (%s)\n' "$(display_path "$COMMAND_SHIM_PATH")"
        [ -n "$COMMAND_SHIM_NOTE" ] && printf '  Note: %s\n' "$COMMAND_SHIM_NOTE"
        ;;
    *)
        printf '  Command fallback: sh %s/memory-hive\n' "$_install_display"
        ;;
esac

printf '\n'

if [ -n "$PLATFORM_WIRED" ]; then
    printf '%s→ Changes take effect on next agent boot.%s\n' "$BOLD" "$RESET"
    printf '  Restart your agent(s) to apply immediately, or run:\n'
    printf '    sh %s/memory-hive apply\n' "$_install_display"
    printf '\n'
    printf 'Read the docs: %shttps://github.com/TJCurnutte/memory-hive%s\n' "$CYAN" "$RESET"
    printf '  Check compliance: sh %s/check-compliance.sh\n' "$_install_display"
elif [ -n "$PLATFORM_MANUAL" ]; then
    printf 'Some detected platforms need manual setup — see the per-platform docs\n'
    printf 'under %s/templates/platforms/ for copy-paste snippets.\n' "$_install_display"
    printf 'Docs: %shttps://github.com/TJCurnutte/memory-hive%s\n' "$CYAN" "$RESET"
else
    printf "We didn't detect any supported agent platform on this machine. To wire\n"
    printf 'into your own setup, point your agent at %s/ for shared\n' "$_hive_display"
    printf 'context and %s/agents/main/ for the default silo.\n' "$_hive_display"
    printf 'Docs: %shttps://github.com/TJCurnutte/memory-hive%s\n' "$CYAN" "$RESET"
    printf '  Check compliance: sh %s/check-compliance.sh\n' "$_install_display"
fi

if [ "$COMMAND_SHIM_STATUS" = "installed-on-path" ] || [ "$COMMAND_SHIM_STATUS" = "already-on-path" ]; then
    _cli_prefix="memory-hive"
else
    _cli_prefix="sh $_install_display/memory-hive"
fi

# Compact roster summary. Long swarms should not flood the install banner;
# `memory-hive list` remains the full roster view.
printf '\n%sYour roster:%s\n' "$BOLD" "$RESET"
_mh_roster_tmp="$(mktemp -t mh-roster.XXXXXX)" || _mh_roster_tmp=""
_mh_roster_total=0
_mh_roster_with_role=0
_mh_roster_no_role=0
_mh_roster_incomplete=0
_mh_roster_preview=""
if [ -n "$_mh_roster_tmp" ]; then
    find "$AGENTS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort > "$_mh_roster_tmp"
    while IFS= read -r _rd; do
        [ -n "$_rd" ] || continue
        _rn="$(basename "$_rd")"
        case "$_rn" in
            _archived|.*) continue ;;
        esac
        _mh_roster_total=$((_mh_roster_total + 1))
        if [ "$_mh_roster_total" -le 8 ]; then
            if [ -z "$_mh_roster_preview" ]; then _mh_roster_preview="$_rn"; else _mh_roster_preview="$_mh_roster_preview, $_rn"; fi
        fi
        _rd="$AGENTS_DIR/$_rn"
        if [ ! -f "$_rd/log.md" ] || [ ! -f "$_rd/context.md" ] || [ ! -f "$_rd/memory.md" ]; then
            _mh_roster_incomplete=$((_mh_roster_incomplete + 1))
            continue
        fi
        _rrole="$(awk '/^## Role$/{flag=1;next} /^## /{flag=0} flag' "$_rd/context.md" \
            | sed -e 's/^[[:space:]]*//' -e '/^$/d' -e 's/\.[[:space:]]*$/./' \
            | head -1 | cut -c1-72)"
        case "$_rrole" in
            "(What is this agent"*|"") _mh_roster_no_role=$((_mh_roster_no_role + 1)) ;;
            *) _mh_roster_with_role=$((_mh_roster_with_role + 1)) ;;
        esac
    done < "$_mh_roster_tmp"
fi
if [ "$_mh_roster_total" -eq 0 ]; then
    printf '  (empty — the installer did not find or create any silos)\n'
elif [ "$_mh_roster_total" -le 12 ]; then
    while IFS= read -r _rd; do
        [ -n "$_rd" ] || continue
        _rn="$(basename "$_rd")"
        case "$_rn" in _archived|.*) continue ;; esac
        _rrole=""
        if [ -f "$_rd/context.md" ]; then
            _rrole="$(awk '/^## Role$/{flag=1;next} /^## /{flag=0} flag' "$_rd/context.md" \
                | sed -e 's/^[[:space:]]*//' -e '/^$/d' -e 's/\.[[:space:]]*$/./' \
                | head -1 | cut -c1-72)"
            case "$_rrole" in "(What is this agent"*|"") _rrole="(no role set)" ;; esac
        else
            _rrole="(incomplete silo)"
        fi
        if [ "$_rn" = "main" ]; then
            printf '  %s%-20s%s %s\n' "$CYAN" "$_rn" "$RESET" "$_rrole"
        else
            printf '  %-20s %s\n' "$_rn" "$_rrole"
        fi
    done < "$_mh_roster_tmp"
else
    _more=$((_mh_roster_total - 8))
    printf '  %s agents total: %s with roles, %s without roles, %s incomplete.\n' \
        "$_mh_roster_total" "$_mh_roster_with_role" "$_mh_roster_no_role" "$_mh_roster_incomplete"
    printf '  Preview: %s' "$_mh_roster_preview"
    [ "$_more" -gt 0 ] && printf ', +%s more' "$_more"
    printf '\n'
    printf '  Full roster: %s list\n' "$_cli_prefix"
fi
[ -n "$_mh_roster_tmp" ] && rm -f "$_mh_roster_tmp"

# Always show the CLI + "add more agents" hint. In the default zero-input
# install this is the only way the user learns how to populate their roster.
printf '\n'
if [ "$WIZARD_RAN" -eq 0 ]; then
    printf 'Next steps:\n'
    printf '  %s add <name> --role coder   # add an agent\n' "$_cli_prefix"
    printf '  %s list                       # see what you have\n' "$_cli_prefix"
    printf '  %s setup                      # guided setup (optional)\n' "$_cli_prefix"
else
    printf 'CLI: %s (add|list|role|rename|archive|setup|doctor|register)\n' "$_cli_prefix"
fi
if [ "$COMMAND_SHIM_STATUS" = "installed-profile-path" ]; then
    printf 'Tip: open a new terminal to use `memory-hive` directly.\n'
elif [ "$COMMAND_SHIM_STATUS" = "not-installed" ]; then
    printf 'Tip: add %s to your PATH to drop the "sh ...memory-hive" prefix.\n' "$_install_display"
fi
