#!/usr/bin/env python3
"""Structural validator for Phase 1 coverage notes.

Usage: python3 validate_coverage_note.py <path-to-note>

Exits 0 if valid. Exits 1 with a list of issues if invalid.
Issues checked:
- Frontmatter present and parses as YAML
- Required frontmatter fields present: type, subsystem, paths, file_count, date, verified
- `type` equals "coverage"
- All 10 required body sections present in order:
    "## 1. Purpose" ... "## 10. Suggested spec sections"
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)

REQUIRED_FRONTMATTER = {
    "type", "subsystem", "paths", "file_count", "date", "verified",
}

REQUIRED_SECTIONS = [
    "1. Purpose",
    "2. File inventory",
    "3. Key types / traits / objects",
    "4. Entry points",
    "5. Dependencies",
    "6. Key algorithms",
    "7. Invariants / IR state read or written",
    "8. Notable complexities or surprises",
    "9. Open questions",
    "10. Suggested spec sections",
]

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def validate(path: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text()

    m = FRONTMATTER_RE.match(text)
    if not m:
        issues.append("missing or malformed frontmatter block")
        return issues

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        issues.append(f"frontmatter is not valid YAML: {e}")
        return issues

    if not isinstance(fm, dict):
        issues.append("frontmatter is not a mapping")
        return issues

    missing = REQUIRED_FRONTMATTER - set(fm)
    if missing:
        issues.append(f"frontmatter missing required fields: {sorted(missing)}")

    if fm.get("type") != "coverage":
        issues.append(f"frontmatter `type` must be 'coverage', got {fm.get('type')!r}")

    body = text[m.end():]
    last_pos = -1
    for section in REQUIRED_SECTIONS:
        header = f"## {section}"
        pos = body.find(header)
        if pos == -1:
            issues.append(f"missing body section: '{header}'")
        elif pos <= last_pos:
            issues.append(f"body section out of order: '{header}'")
        else:
            last_pos = pos

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-note>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 2

    issues = validate(path)
    if not issues:
        print(f"[OK] {path}")
        return 0

    print(f"[FAIL] {path}")
    for issue in issues:
        print(f"  - {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
