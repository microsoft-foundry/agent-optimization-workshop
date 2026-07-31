#!/usr/bin/env bash
# use-reference.sh — drop a known-good reference artifact into `generated/`
# so learners can unblock the next lab even if their own generation was weak.
#
# Usage:
#   ./scripts/use-reference.sh datasets sample-prompts-v1
#   ./scripts/use-reference.sh evaluators quality-evaluator-v1
#   ./scripts/use-reference.sh prompts prompt-agent-baseline-v1

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <datasets|evaluators|prompts> <artifact-name>" >&2
  exit 2
fi

KIND="$1"
NAME="$2"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF_DIR="${REPO_ROOT}/artifacts/${KIND}/reference"
GEN_DIR="${REPO_ROOT}/artifacts/${KIND}/generated"

if [[ ! -d "$REF_DIR" ]]; then
  echo "error: unknown kind '${KIND}' (expected datasets|evaluators|prompts)" >&2
  exit 2
fi

# Find the reference file — try common extensions
for ext in .jsonl .json .yaml .yml .md; do
  candidate="${REF_DIR}/${NAME}${ext}"
  if [[ -f "$candidate" ]]; then
    mkdir -p "$GEN_DIR"
    cp "$candidate" "$GEN_DIR/"
    echo "✓ Copied ${candidate#$REPO_ROOT/} -> ${GEN_DIR#$REPO_ROOT/}/$(basename "$candidate")"
    exit 0
  fi
done

echo "error: reference artifact '${NAME}' not found in ${REF_DIR}" >&2
exit 1
