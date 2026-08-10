#!/usr/bin/env bash
# post-create.sh — one-time setup after the devcontainer builds.
#
# Add anything that needs to run once when the container starts for the first
# time. Keep it idempotent — this script may run again on rebuild.

set -euo pipefail

log() { printf "\n▸ %s\n" "$*"; }

# Install Dependencies
log "Installing workshop Python dependencies"
pip install --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi
if [[ -f requirements-dev.txt ]]; then
  pip install -r requirements-dev.txt
fi

# Update Tools
log "Ensuring azd + the hosted-agents extension are ready"
if command -v azd >/dev/null 2>&1; then
  azd version || true
  # Hosted-agent commands (`azd ai agent`, `azd deploy` for host: azure.ai.agent)
  # come from the azure.ai.agents extension used in Fundamentals lab 05.
  azd config set alpha.extensions on >/dev/null 2>&1 || true
  if azd extension list --installed --output json 2>/dev/null | grep -q "azure.ai.agents"; then
    echo "azure.ai.agents already installed — upgrading to the latest version"
    azd extension upgrade azure.ai.agents || true
  else
    echo "Installing azure.ai.agents extension"
    azd extension install azure.ai.agents || true
  fi
  azd extension list --installed || true
else
  echo "⚠️  azd not installed — skipping extension setup"
fi

# Prepare Environment
log "Making workshop scripts executable"
chmod +x scripts/*.sh 2>/dev/null || true

log "Preparing coach progress directory"
mkdir -p /home/vscode/.contoso-coach
touch /home/vscode/.contoso-coach/.keep

# Python Dependencies
# log "Running spec tests as a smoke check"
# if command -v pytest >/dev/null 2>&1; then
#  pytest -q || echo "⚠️  spec tests reported issues — see output above"
# fi

log "Devcontainer ready. Open README.md to get started."
