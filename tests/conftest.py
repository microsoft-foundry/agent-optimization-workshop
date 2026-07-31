from __future__ import annotations
"""Test helpers — repo root, spec loader, lab file discovery."""
from pathlib import Path
import re

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "specs"
LABS_DIR = REPO_ROOT / "labs"


def load_course_spec():
    assert yaml is not None, "PyYAML required — pip install -r requirements-dev.txt"
    with open(SPECS_DIR / "course.yaml") as f:
        return yaml.safe_load(f)


def lab_path(phase: str, lab_id: str) -> Path:
    return LABS_DIR / phase / f"{lab_id}.md"


SECTION_PATTERNS = {
    "goal":            re.compile(r"^##\s+🎯\s+Goal", re.M),
    "where_this_fits": re.compile(r"^##\s+🧭\s+Where this fits", re.M),
    "steps":           re.compile(r"^##\s+📋\s+Steps", re.M),
    "verify":          re.compile(r"^##\s+✅\s+Verify", re.M),
    "recap":           re.compile(r"^##\s+🧠\s+Recap", re.M),
    "next":            re.compile(r"^##\s+➡️\s+Next", re.M),
}
