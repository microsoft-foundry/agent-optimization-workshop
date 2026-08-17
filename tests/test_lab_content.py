"""Every lab file must have the required pedagogy sections."""
from __future__ import annotations

import re

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


# Header shape from AGENTS.md § "Callout conventions — Gotchas":
#   Inline:        > ⚠️ **Gotcha:** ...
#   Cross-cutting: > ⚠️ **Gotcha — <error phrase>.** ...  (must link to TROUBLESHOOTING.md#anchor)
_GOTCHA_INLINE = re.compile(r"^\s*>\s*⚠️\s*\*\*Gotcha:\*\*")
_GOTCHA_CROSSCUT = re.compile(r"^\s*>\s*⚠️\s*\*\*Gotcha\s+—")
_TROUBLESHOOTING_LINK = re.compile(r"TROUBLESHOOTING\.md#")


def _iter_blockquotes(text: str):
    """Yield (start_line, [line, ...]) for each contiguous `>`-prefixed block."""
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        if re.match(r"^\s*>", lines[i]):
            start = i
            block = []
            while i < n and re.match(r"^\s*>", lines[i]):
                block.append(lines[i])
                i += 1
            yield start, block
        else:
            i += 1


def test_gotcha_callouts_follow_convention():
    """Enforce the two-variant Gotcha rule from AGENTS.md.

    - Inline (`> ⚠️ **Gotcha:**`): must be ≤ 4 lines of blockquote.
    - Cross-cutting (`> ⚠️ **Gotcha — ...**`): must link to
      `../TROUBLESHOOTING.md#<anchor>` inside the same blockquote.
    """
    spec = load_course_spec()
    violations: list[str] = []
    for phase in spec["phases"]:
        for lab in phase["labs"]:
            p = lab_path(phase["id"], lab["id"])
            text = p.read_text(encoding="utf-8")
            rel = f"{phase['id']}/{lab['id']}.md"
            for start, block in _iter_blockquotes(text):
                header = block[0]
                if _GOTCHA_CROSSCUT.search(header):
                    body = "\n".join(block)
                    if not _TROUBLESHOOTING_LINK.search(body):
                        violations.append(
                            f"{rel}:{start + 1} cross-cutting Gotcha missing "
                            f"TROUBLESHOOTING.md link"
                        )
                elif _GOTCHA_INLINE.search(header) and len(block) > 4:
                    violations.append(
                        f"{rel}:{start + 1} inline Gotcha exceeds 4 lines "
                        f"({len(block)} lines) — split it out to "
                        f"labs/TROUBLESHOOTING.md and link instead"
                    )
    assert not violations, "gotcha convention violations:\n  " + "\n  ".join(violations)
