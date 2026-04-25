#!/bin/sh
# cut-release.sh — bump version, tag, push. The Release workflow does the rest.
#
# Usage:
#   scripts/cut-release.sh 0.3.0
#
# What it does:
#   1. Verifies you're on main with a clean tree.
#   2. Verifies CHANGELOG.md has a `## [<version>]` entry (you write that
#      yourself before running this — that's the part that needs human
#      judgment).
#   3. Creates an annotated tag `v<version>`.
#   4. Pushes main + tag to origin.
#
# The .github/workflows/release.yml workflow then fires on the tag push,
# extracts the CHANGELOG block, appends the commit log since the previous
# tag, and publishes the GitHub Release. Result: a stable URL at
# github.com/TJCurnutte/memory-hive/releases/tag/v<version>.

set -eu

VERSION="${1:-}"
if [ -z "$VERSION" ]; then
    printf 'usage: %s <version>   (e.g. 0.3.0)\n' "$0" >&2
    exit 2
fi

# Refuse to tag from a dirty tree or a branch other than main.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH" != "main" ]; then
    printf 'ERROR: not on main (currently on %s)\n' "$BRANCH" >&2
    exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
    printf 'ERROR: working tree not clean. Commit or stash first.\n' >&2
    exit 1
fi

# Verify the changelog entry exists. Without it, the release will have
# auto-commit-log only and no human-written narrative.
if ! grep -q "^## \[${VERSION}\]" CHANGELOG.md; then
    printf 'ERROR: CHANGELOG.md has no "## [%s]" section.\n' "$VERSION" >&2
    printf 'Promote the [Unreleased] block to [%s] first, then re-run.\n' "$VERSION" >&2
    exit 1
fi

TAG="v${VERSION}"
# `git tag --list <pattern>` matches exact tag names safely (no pipe to grep,
# no risk of partial-match false positives).
if [ -n "$(git tag --list "$TAG")" ]; then
    printf 'ERROR: tag %s already exists locally.\n' "$TAG" >&2
    exit 1
fi

git fetch origin --tags --quiet
if [ -n "$(git ls-remote --tags origin "refs/tags/${TAG}")" ]; then
    printf 'ERROR: tag %s already exists on origin.\n' "$TAG" >&2
    exit 1
fi

git tag -a "$TAG" -m "${TAG}"
git push origin main "$TAG"

printf '\nTagged %s and pushed.\n' "$TAG"
printf 'Release workflow will publish at:\n'
printf '  https://github.com/TJCurnutte/memory-hive/releases/tag/%s\n' "$TAG"
