#!/usr/bin/env bash
# Snapshot the active concierge prompt into the versioned history.
#
# Copies instructions/concierge.md to the next free
# instructions/versions/instructions-N.md so the prompt's evolution is
# traceable across workshop iterations.
#
# Usage:
#   ./scripts/snapshot-instructions.sh ["short note for the version log"]

set -euo pipefail

# Resolve the agent root (parent of this script's scripts/ folder).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ACTIVE="${AGENT_DIR}/instructions/concierge.md"
VERSIONS_DIR="${AGENT_DIR}/instructions/versions"

if [[ ! -f "${ACTIVE}" ]]; then
  echo "error: active prompt not found at ${ACTIVE}" >&2
  exit 1
fi

mkdir -p "${VERSIONS_DIR}"

# Find the next version index.
next=0
shopt -s nullglob
for f in "${VERSIONS_DIR}"/instructions-*.md; do
  base="$(basename "${f}" .md)"      # instructions-N
  n="${base#instructions-}"
  if [[ "${n}" =~ ^[0-9]+$ ]] && (( n >= next )); then
    next=$(( n + 1 ))
  fi
done
shopt -u nullglob

# Warn if the active prompt is identical to the most recent snapshot.
latest=$(( next - 1 ))
if (( latest >= 0 )); then
  prev="${VERSIONS_DIR}/instructions-${latest}.md"
  if [[ -f "${prev}" ]] && cmp -s "${ACTIVE}" "${prev}"; then
    echo "warning: concierge.md is identical to instructions-${latest}.md — nothing changed since the last snapshot." >&2
    echo "Edit instructions/concierge.md first, then re-run this script." >&2
    exit 1
  fi
fi

dest="${VERSIONS_DIR}/instructions-${next}.md"
cp "${ACTIVE}" "${dest}"
echo "Snapshotted instructions/concierge.md -> instructions/versions/instructions-${next}.md"

note="${1:-}"
if [[ -n "${note}" ]]; then
  echo "  note: ${note}"
  echo "Add a row to instructions/README.md version log:"
  echo "  | ${next} | ${note} |"
fi
