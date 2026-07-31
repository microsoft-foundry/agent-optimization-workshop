from __future__ import annotations
"""`scripts/reset.sh --dry-run` reports drift correctly."""
import subprocess
from pathlib import Path

from conftest import REPO_ROOT


RESET = REPO_ROOT / "scripts" / "reset.sh"


def test_reset_script_exists_and_executable():
    assert RESET.is_file(), "scripts/reset.sh missing"
    import os
    assert os.access(RESET, os.X_OK), "scripts/reset.sh must be executable (chmod +x)"


def test_reset_dry_run_reports_clean_when_no_drift():
    # Fresh checkout: src/ should be empty or mirror src.original/. Either way
    # --dry-run must exit 0 and NOT report drift when src/ and src.original/ are equal.
    result = subprocess.run(
        [str(RESET), "--dry-run"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"reset.sh --dry-run failed: {result.stderr}"
