#!/usr/bin/env bash
set -euo pipefail

# scrub_history.sh
#
# Build a replacements file from secrets provided via the environment and run
# `git filter-repo --replace-text` to remove those secrets from all commits.
#
# USAGE (recommended):
#
#   # Export secrets as a newline-separated string in SECRETS_FILE or as env var
#   export SECRETS_FILE=/path/to/secrets.txt
#   # OR export SECRETS as a single-line, tokens separated by '::'
#   export SECRETS="token1::token2::token3"
#
#   # Dry-run: build replacements file and show planned replacements
#   ./.github/scripts/scrub_history.sh --dry-run
#
#   # Run (will rewrite history and force-push):
#   ./.github/scripts/scrub_history.sh --run --remote origin --branches main,develop,week5-milestones
#
# WARNING: Rewriting history is destructive. All collaborators must re-clone.

WORKDIR=$(pwd)
TMPDIR=$(mktemp -d)
REPL_FILE="$TMPDIR/replacements.txt"

cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

show_help() {
  sed -n '1,120p' "$0"
}

DRY_RUN=1
RUN=0
REMOTE=origin
BRANCHES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) DRY_RUN=0; RUN=1; shift ;;
    --dry-run) DRY_RUN=1; RUN=0; shift ;;
    --remote) REMOTE="$2"; shift 2 ;;
    --branches) BRANCHES="$2"; shift 2 ;;
    --help) show_help; exit 0 ;;
    *) echo "Unknown arg: $1"; show_help; exit 1 ;;
  esac
done

# Gather secrets from SECRETS_FILE or SECRETS env var
if [[ -n "${SECRETS_FILE-}" && -f "$SECRETS_FILE" ]]; then
  mapfile -t SECRETS_ARR < "$SECRETS_FILE"
elif [[ -n "${SECRETS-}" ]]; then
  IFS='::' read -r -a SECRETS_ARR <<< "$SECRETS"
else
  echo "No secrets provided. Set SECRETS_FILE or SECRETS env var." >&2
  exit 1
fi

if [[ ${#SECRETS_ARR[@]} -eq 0 ]]; then
  echo "No secrets found in provided input." >&2
  exit 1
fi

echo "Preparing replacements file at $REPL_FILE"
> "$REPL_FILE"
for s in "${SECRETS_ARR[@]}"; do
  # skip empty
  if [[ -z "$s" ]]; then
    continue
  fi
  # Each replacement line: exact literal to replace ==> replacement text
  # We intentionally write a non-secret replacement value.
  printf '%s==>REDACTED_SECRET\n' "$s" >> "$REPL_FILE"
done

echo "Planned replacements:"
nl -ba "$REPL_FILE" | sed -n '1,200p'

if [[ $DRY_RUN -eq 1 ]]; then
  COUNT=$(wc -l < "$REPL_FILE" | tr -d '[:space:]')
  NOW=$(date --iso-8601=seconds 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S%z")
  echo ""
  echo "DRY-RUN ACK: $COUNT replacement(s) planned. Replacements file: $REPL_FILE"
  echo "DRY-RUN TIMESTAMP: $NOW"
  echo "Dry run complete. To execute the rewrite, re-run with --run." 
  exit 0
fi

echo "Ensuring git-filter-repo is available..."
if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo not found; attempting to install via pip (requires Python and pip)."
  if command -v python >/dev/null 2>&1; then
    python -m pip install --user git-filter-repo
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "Please install git-filter-repo manually: https://github.com/newren/git-filter-repo" >&2
    exit 1
  fi
fi

echo "Running git filter-repo (this will rewrite history)..."
git filter-repo --force --replace-text "$REPL_FILE"

echo "Filter-repo finished. Pushing rewritten refs to remote $REMOTE"
if [[ -n "$BRANCHES" ]]; then
  IFS=',' read -r -a BR_ARRAY <<< "$BRANCHES"
  for b in "${BR_ARRAY[@]}"; do
    git push --force $REMOTE refs/heads/$b:refs/heads/$b
  done
else
  git push --force --all $REMOTE
fi
git push --force --tags $REMOTE

echo "History rewrite complete. ALL collaborators must re-clone the repository." 
