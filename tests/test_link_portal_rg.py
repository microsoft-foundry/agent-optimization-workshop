"""Portal-first linker writes canonical Foundry project metadata."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from conftest import REPO_ROOT


LINKER = REPO_ROOT / "scripts" / "link-portal-rg.sh"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


def test_linker_normalizes_project_name_and_sets_project_metadata(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    azd_log = tmp_path / "azd.log"

    _write_executable(
        bin_dir / "az",
        """#!/usr/bin/env bash
set -euo pipefail
case "$*" in
  "account show") echo '{}' ;;
  "account show --query id -o tsv") echo '00000000-0000-0000-0000-000000000000' ;;
  "group show -n rg-test --query location -o tsv") echo 'eastus' ;;
  "cognitiveservices account list -g rg-test --query "*) echo 'foundry-test' ;;
  "cognitiveservices account project list -g rg-test --name foundry-test --query [0] -o json")
    cat <<'JSON'
{"id":"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-test/providers/Microsoft.CognitiveServices/accounts/foundry-test/projects/travel-project","location":"eastus2","name":"foundry-test/travel-project","properties":{"endpoints":{"AI Foundry API":"https://foundry-test.services.ai.azure.com/api/projects/travel-project"}}}
JSON
    ;;
  *) echo "unexpected az command: $*" >&2; exit 1 ;;
esac
""",
    )
    _write_executable(
        bin_dir / "azd",
        """#!/usr/bin/env bash
set -euo pipefail
case "$*" in
  "env list -o json") echo '[]' ;;
  "env new test-env --no-prompt") ;;
  "env set "*) printf '%s\n' "$*" >> "$AZD_LOG" ;;
  "env get-values")
    cat <<'VALUES'
AZURE_SUBSCRIPTION_ID="00000000-0000-0000-0000-000000000000"
AZURE_RESOURCE_GROUP="rg-test"
AZURE_LOCATION="eastus2"
AZURE_AI_ACCOUNT_NAME="foundry-test"
AZURE_AI_PROJECT_NAME="travel-project"
AZURE_AI_PROJECT_ID="project-id"
AZURE_AI_FOUNDRY_PROJECT_ID="project-id"
AZURE_AI_PROJECT_ENDPOINT="project-endpoint"
FOUNDRY_PROJECT_ENDPOINT="project-endpoint"
USE_EXISTING_AI_PROJECT="true"
AI_PROJECT_DEPLOYMENTS="[]"
VALUES
    ;;
  *) echo "unexpected azd command: $*" >&2; exit 1 ;;
esac
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["AZD_LOG"] = str(azd_log)
    result = subprocess.run(
        [str(LINKER), "rg-test", "test-env"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    writes = azd_log.read_text().splitlines()
    assert "env set AZURE_LOCATION eastus2" in writes
    assert "env set AZURE_AI_PROJECT_NAME travel-project" in writes
    assert not any("foundry-test/travel-project" in write for write in writes)
    project_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-test/providers/Microsoft.CognitiveServices/accounts/foundry-test/projects/travel-project"
    assert f"env set AZURE_AI_PROJECT_ID {project_id}" in writes
    assert f"env set AZURE_AI_FOUNDRY_PROJECT_ID {project_id}" in writes
    endpoint = "https://foundry-test.services.ai.azure.com/api/projects/travel-project"
    assert f"env set AZURE_AI_PROJECT_ENDPOINT {endpoint}" in writes
    assert f"env set FOUNDRY_PROJECT_ENDPOINT {endpoint}" in writes