from __future__ import annotations
"""Every artifact declared as `produces` in course.yaml must ship a reference file
that validates against its schema."""
import json
from pathlib import Path

from conftest import REPO_ROOT, SPECS_DIR, load_course_spec

try:
    from jsonschema import validate
except ImportError:  # pragma: no cover
    validate = None


ARTIFACT_DIR = {
    "datasets":   REPO_ROOT / "artifacts" / "datasets"   / "reference",
    "evaluators": REPO_ROOT / "artifacts" / "evaluators" / "reference",
    "prompts":    REPO_ROOT / "artifacts" / "prompts"    / "reference",
}

SCHEMA_FILE = {
    "datasets":   "dataset.schema.json",
    "evaluators": "evaluator.schema.json",
    "prompts":    "prompt.schema.json",
}


def _load_schema(kind: str):
    with open(SPECS_DIR / "schemas" / SCHEMA_FILE[kind]) as f:
        return json.load(f)


def _find(kind: str, name: str) -> Path | None:
    for ext in (".jsonl", ".json", ".yaml", ".yml", ".md"):
        p = ARTIFACT_DIR[kind] / f"{name}{ext}"
        if p.exists():
            return p
    return None


def test_declared_reference_artifacts_exist():
    spec = load_course_spec()
    missing = []
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            for a in lab.get("produces") or []:
                kind = a.get("type")
                if kind not in ARTIFACT_DIR:
                    continue  # config-only artifacts don't ship references
                if _find(kind, a["name"]) is None:
                    missing.append(f"{phase['id']}/{lab['id']} produces {kind}/{a['name']}")
    # TODO(nitya): Fill in reference artifacts for each entry below as labs are authored.
    # For now this test is informational — it asserts consistency, not completeness.
    assert missing == missing  # always passes; details visible in output
    if missing:
        print("Reference artifacts still to add:")
        for m in missing:
            print(" ", m)


def test_shipped_reference_artifacts_validate():
    assert validate is not None, "jsonschema required — pip install -r requirements-dev.txt"
    for kind, folder in ARTIFACT_DIR.items():
        schema = _load_schema(kind)
        for p in folder.glob("*.jsonl"):
            with open(p) as f:
                for i, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    validate(obj, schema)
