"""Every lab file must have the required pedagogy sections."""
from conftest import SECTION_PATTERNS, lab_path, load_course_spec


def test_all_labs_use_template_sections():
    spec = load_course_spec()
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            p = lab_path(phase["id"], lab["id"])
            text = p.read_text(encoding="utf-8")
            for section, pattern in SECTION_PATTERNS.items():
                assert pattern.search(text), (
                    f"{phase['id']}/{lab['id']} missing section: {section}"
                )
