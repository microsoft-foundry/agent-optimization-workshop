from __future__ import annotations
"""workshop-coach agent has valid frontmatter and every skill it lists exists."""
import json
import re
from pathlib import Path

from conftest import REPO_ROOT, SPECS_DIR

try:
    import yaml
    from jsonschema import validate
except ImportError:  # pragma: no cover
    yaml = None
    validate = None


COACH = REPO_ROOT / ".github" / "agents" / "workshop-coach.agent.md"
SKILLS_DIR = REPO_ROOT / ".github" / "agents" / "skills"

BEHAVIOR_PHRASES = [
    "Never do the task",
    "always guide",  # case-insensitive check below
    "progress-tracker",
    "bookmark",
]


def _frontmatter():
    text = COACH.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "workshop-coach.agent.md must start with YAML frontmatter"
    return yaml.safe_load(m.group(1)), text


def test_coach_frontmatter_valid():
    assert yaml is not None and validate is not None
    fm, _ = _frontmatter()
    with open(SPECS_DIR / "agent.schema.json") as f:
        schema = json.load(f)
    validate(fm, schema)


def test_every_listed_skill_exists():
    fm, _ = _frontmatter()
    for tool in fm.get("tools", []):
        assert (SKILLS_DIR / f"{tool}.md").is_file(), f"missing skill: {tool}"


def test_behavior_contract_present():
    _, text = _frontmatter()
    body = text.lower()
    for phrase in BEHAVIOR_PHRASES:
        assert phrase.lower() in body, f"workshop-coach missing key phrase: {phrase!r}"
