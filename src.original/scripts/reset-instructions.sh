#!/usr/bin/env bash
# Reset the active concierge prompt back to the immutable baseline seed.
#
# Copies instructions/versions/instructions-0.md over instructions/concierge.md
# so every fresh run of the optimize loop starts from the same intentionally
# under-optimized prompt — regardless of edits left over from a previous run in
# the same checkout.
#
# Usage:
#   ./scripts/reset-instructions.sh

set -euo pipefail

# Resolve the agent root (parent of this script's scripts/ folder).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

BASELINE="${AGENT_DIR}/instructions/versions/instructions-0.md"
ACTIVE="${AGENT_DIR}/instructions/concierge.md"

if [[ ! -f "${BASELINE}" ]]; then
  echo "error: baseline seed not found at ${BASELINE}" >&2
  exit 1
fi

if cmp -s "${BASELINE}" "${ACTIVE}"; then
  echo "instructions/concierge.md already matches the baseline (instructions-0) — nothing to reset."
  exit 0
fi

cp "${BASELINE}" "${ACTIVE}"
echo "Reset instructions/concierge.md to the baseline (instructions/versions/instructions-0.md)."
