#!/usr/bin/env bash
# reset.sh — restore src/ from the pristine src.original/ snapshot.
#
# Usage:
#   ./scripts/reset.sh            # do the reset
#   ./scripts/reset.sh --dry-run  # report drift without changing anything
#
# TODO(nitya): once src.original/ contains the ported hosted-agent code,
# extend this to preserve learner-authored .env files if desired.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${REPO_ROOT}/src"
ORIG="${REPO_ROOT}/src.original"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

if [[ ! -d "$ORIG" ]]; then
  echo "error: ${ORIG} not found" >&2
  exit 2
fi

# Compare src/ against src.original/
if diff -r "$ORIG" "$SRC" > /dev/null 2>&1; then
  echo "✓ src/ matches src.original/ — no drift, nothing to reset."
  exit 0
fi

if $DRY_RUN; then
  echo "src/ differs from src.original/. Run without --dry-run to reset."
  diff -r "$ORIG" "$SRC" || true
  exit 0
fi

echo "Resetting src/ from src.original/ ..."
rm -rf "$SRC"
cp -R "$ORIG" "$SRC"
echo "✓ Reset complete."
