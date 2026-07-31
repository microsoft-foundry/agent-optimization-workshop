#!/usr/bin/env bash
# post-create.sh — one-time setup after the devcontainer builds.
#
# Add anything that needs to run once when the container starts for the first
# time. Keep it idempotent — this script may run again on rebuild.

set -euo pipefail

log() { printf "\n▸ %s\n" "$*"; }

log "Installing workshop Python dependencies"
pip install --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi
if [[ -f requirements-dev.txt ]]; then
  pip install -r requirements-dev.txt
fi

log "Ensuring azd extensions are up to date"
if command -v azd >/dev/null 2>&1; then
  azd version || true
  # Hosted-agents extension used in Fundamentals lab 05.
  # TODO(nitya): pin exact extension version once labs stabilize.
  azd ext install azure.ai.agents || true
  azd ext list || true
else
  echo "⚠️  azd not installed — skipping extension setup"
fi

log "Making workshop scripts executable"
chmod +x scripts/*.sh 2>/dev/null || true

log "Preparing coach progress directory"
mkdir -p /home/vscode/.contoso-coach
touch /home/vscode/.contoso-coach/.keep

log "Running spec tests as a smoke check"
if command -v pytest >/dev/null 2>&1; then
  pytest -q || echo "⚠️  spec tests reported issues — see output above"
fi

log "Devcontainer ready. Open .github/PLAN.md or README.md to get started."
