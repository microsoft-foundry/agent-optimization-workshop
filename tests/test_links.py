from __future__ import annotations
"""Internal markdown links in labs must resolve to real files."""
import re

from conftest import LABS_DIR, REPO_ROOT, lab_path, load_course_spec

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _internal(target: str) -> bool:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return False
    return True


def test_lab_links_resolve():
    spec = load_course_spec()
    broken = []
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            p = lab_path(phase["id"], lab["id"])
            text = p.read_text(encoding="utf-8")
            for match in LINK_RE.finditer(text):
                target = match.group(1).split("#", 1)[0].strip()
                if not target or not _internal(target):
                    continue
                resolved = (p.parent / target).resolve()
                if not resolved.exists():
                    broken.append(f"{phase['id']}/{lab['id']} -> {target}")
    assert not broken, "broken internal links:\n  " + "\n  ".join(broken)
