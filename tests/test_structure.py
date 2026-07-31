"""Structure invariants — course.yaml is the source of truth."""
from conftest import LABS_DIR, REPO_ROOT, lab_path, load_course_spec


REQUIRED_DIRS = [
    ".github/agents",
    ".github/agents/skills",
    "data",
    "src",
    "src.original",
    "artifacts/datasets/reference",
    "artifacts/evaluators/reference",
    "artifacts/prompts/reference",
    "labs/_template",
    "labs/fundamentals",
    "labs/core",
    "labs/more",
    "specs",
    "specs/schemas",
    "tests",
    "scripts",
    "infra",
]


def test_required_directories_exist():
    for d in REQUIRED_DIRS:
        assert (REPO_ROOT / d).is_dir(), f"missing dir: {d}"


def test_every_lab_in_spec_has_a_file():
    spec = load_course_spec()
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            p = lab_path(phase["id"], lab["id"])
            assert p.is_file(), f"lab file missing for {phase['id']}/{lab['id']}: {p}"


def test_no_orphan_lab_files():
    spec = load_course_spec()
    declared = {
        (phase["id"], lab["id"])
        for phase in spec["phases"]
        for lab in phase["labs"]
    }
    for phase_dir in ("fundamentals", "core", "more"):
        for f in (LABS_DIR / phase_dir).glob("*.md"):
            if f.name == "README.md":
                continue
            lab_id = f.stem
            assert (phase_dir, lab_id) in declared, (
                f"orphan lab file not in course.yaml: {phase_dir}/{lab_id}"
            )


def test_prereqs_reference_existing_labs():
    spec = load_course_spec()
    declared = {
        f"{phase['id']}/{lab['id']}"
        for phase in spec["phases"]
        for lab in phase["labs"]
    }
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            for pr in lab.get("prereqs", []):
                assert pr in declared, (
                    f"{phase['id']}/{lab['id']} prereq points at unknown lab: {pr}"
                )
