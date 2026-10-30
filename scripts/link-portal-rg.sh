#!/usr/bin/env bash
# link-portal-rg.sh — bind an azd env to a portal-created Foundry resource group.
#
# Use this ONCE before Lab 05 if your Foundry project was provisioned via the
# portal (Lab 02) instead of azd (Lab 01). It teaches azd about the existing
# resource group + Foundry account + project so `azd provision` (Step 2 of
# Lab 05) reuses them instead of creating a second copy in a new RG.
#
# Usage:
#   ./scripts/link-portal-rg.sh [resource-group] [azd-env-name]
#
# Defaults: rg-contoso-travel  contoso-travel
#
# Idempotent — safe to re-run. Requires `az` logged in and `jq` on PATH
# (both are already present in the workshop devcontainer).

set -euo pipefail

RG="${1:-rg-contoso-travel}"
ENV="${2:-contoso-travel}"

# --- sanity checks ---------------------------------------------------------
command -v az >/dev/null 2>&1 || { echo "❌ 'az' not found on PATH."; exit 127; }
command -v azd >/dev/null 2>&1 || { echo "❌ 'azd' not found on PATH."; exit 127; }
command -v jq >/dev/null 2>&1 || { echo "❌ 'jq' not found on PATH."; exit 127; }

az account show >/dev/null 2>&1 || {
  echo "❌ 'az' is not logged in. Run: az login --use-device-code"; exit 1; }

# --- discover the RG + Foundry resources -----------------------------------
RG_LOC=$(az group show -n "$RG" --query location -o tsv 2>/dev/null) || {
  echo "❌ Resource group '$RG' not found in the current subscription."
  echo "   Pass a different name: ./scripts/link-portal-rg.sh <rg-name>"
  exit 1
}
SUB=$(az account show --query id -o tsv)

# Foundry account = an AIServices account inside the RG (Lab 02 creates exactly one).
ACCT=$(az cognitiveservices account list -g "$RG" \
  --query "[?kind=='AIServices'] | [0].name" -o tsv 2>/dev/null || true)
if [[ -z "$ACCT" || "$ACCT" == "null" ]]; then
  echo "❌ No Foundry (AIServices) account found in resource group '$RG'."
  echo "   Did Lab 02 complete? Check the portal → Resource groups → $RG."
  exit 1
fi

# Project metadata — best-effort. Azure returns the name as 'account/project',
# while Bicep expects only the child project name.
PROJ_JSON=$(az cognitiveservices account project list \
  -g "$RG" --name "$ACCT" --query "[0]" -o json 2>/dev/null || true)
[[ -n "$PROJ_JSON" ]] || PROJ_JSON='{}'
PROJ_QUALIFIED=$(jq -r '.name // empty' <<<"$PROJ_JSON")
PROJ="${PROJ_QUALIFIED##*/}"
PROJ_ID=$(jq -r '.id // empty' <<<"$PROJ_JSON")
PROJ_ENDPOINT=$(jq -r '.properties.endpoints["AI Foundry API"] // empty' <<<"$PROJ_JSON")
PROJ_LOC=$(jq -r '.location // empty' <<<"$PROJ_JSON")
LOC="${PROJ_LOC:-$RG_LOC}"

# --- bind the azd env ------------------------------------------------------
if azd env list -o json 2>/dev/null | jq -e ".[] | select(.Name==\"$ENV\")" >/dev/null; then
  azd env select "$ENV" >/dev/null
else
  azd env new "$ENV" --no-prompt
fi

azd env set AZURE_SUBSCRIPTION_ID     "$SUB"
azd env set AZURE_RESOURCE_GROUP      "$RG"
azd env set AZURE_LOCATION            "$LOC"
azd env set AZURE_AI_ACCOUNT_NAME     "$ACCT"
[[ -n "$PROJ" && "$PROJ" != "null" ]] && azd env set AZURE_AI_PROJECT_NAME "$PROJ"
if [[ -n "$PROJ_ID" && "$PROJ_ID" != "null" ]]; then
  azd env set AZURE_AI_PROJECT_ID         "$PROJ_ID"
  azd env set AZURE_AI_FOUNDRY_PROJECT_ID "$PROJ_ID"
fi
if [[ -n "$PROJ_ENDPOINT" && "$PROJ_ENDPOINT" != "null" ]]; then
  azd env set AZURE_AI_PROJECT_ENDPOINT "$PROJ_ENDPOINT"
  azd env set FOUNDRY_PROJECT_ENDPOINT  "$PROJ_ENDPOINT"
fi
azd env set USE_EXISTING_AI_PROJECT   true
azd env set AI_PROJECT_DEPLOYMENTS    "[]"   # sidestep the JSON-escape gotcha in Lab 05

# --- report ----------------------------------------------------------------
echo ""
echo "✅ azd env '$ENV' linked to existing resource group '$RG' in $LOC."
echo "   Foundry account: $ACCT"
[[ -n "$PROJ" && "$PROJ" != "null" ]] && echo "   Foundry project: $PROJ"
echo ""
echo "Values now set (subscription id truncated for readability):"
azd env get-values | grep -E "^(AZURE_(SUBSCRIPTION_ID|RESOURCE_GROUP|LOCATION|AI_ACCOUNT_NAME|AI_PROJECT_NAME|AI_PROJECT_ID|AI_FOUNDRY_PROJECT_ID|AI_PROJECT_ENDPOINT)|FOUNDRY_PROJECT_ENDPOINT)|^USE_EXISTING_AI_PROJECT|^AI_PROJECT_DEPLOYMENTS" \
  | sed -E 's|(AZURE_SUBSCRIPTION_ID=")([^"]{4})[^"]*(")|\1\2…\3|'
echo ""
echo "Next: run Lab 05 Step 2 (azd provision) — it will reuse '$RG' instead of"
echo "creating a new one."
