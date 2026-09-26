#!/usr/bin/env python3
"""Structural validator for D-26 notes (`research` and `python-mapping`).

Usage: python3 validate_d26_note.py <note.md> [...]
Exit 0 if every note is valid, 1 otherwise. Checks frontmatter fields per
type, required sections in order, that list fields contain only strings
(the unquoted-wikilink hazard), that every Findings claim line carries an
evidence tag, and that no forbidden path appears anywhere.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
TAG_RE = re.compile(r"\[(measured|precedent-measured|designed|judgment)\]")
FORBIDDEN_RE = re.compile(r"/Users/|accelerator-bandits|EE109-Spr-2026|\.pem|ec2-[0-9]|us-west-2")

SCHEMAS = {
    "research": {
        "fields": {"type", "decision", "angle", "discriminates", "sources", "verified", "status"},
        "lists": ["sources", "verified"],
        "sections": ["Scope", "Findings", "Implications", "Evidence against", "Open questions", "Confidence"],
        "subsections": {"Implications": ["R-X", "R-E", "R-B", "P-X", "P-E", "P-B"]},
    },
    "python-mapping": {
        "fields": {"type", "construct", "spec_entry", "grammar_rule", "external_dsl", "per_style",
                   "obligations_at_risk", "raters", "verified", "status"},
        "lists": ["obligations_at_risk", "raters", "verified"],
        "sections": ["External DSL form", "Python forms", "Assessment", "Precedent"],
        "subsections": {},
    },
}


def validate(path: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return ["missing or malformed frontmatter block"]
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"frontmatter is not valid YAML: {e}"]
    if not isinstance(fm, dict):
        return ["frontmatter is not a mapping"]
    schema = SCHEMAS.get(fm.get("type"))
    if schema is None:
        return [f"unknown type {fm.get('type')!r}; expected one of {sorted(SCHEMAS)}"]
    missing = schema["fields"] - set(fm)
    if missing:
        issues.append(f"frontmatter missing required fields: {sorted(missing)}")
    for key in schema["lists"]:
        value = fm.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            issues.append(f"`{key}` must be a list of strings (quote wikilinks and path:line citations)")
    if fm.get("type") == "python-mapping" and not str(fm.get("spec_entry", "")).startswith("[["):
        issues.append("`spec_entry` must be a quoted wikilink string starting with [[")

    body = text[m.end():]
    last = -1
    for section in schema["sections"]:
        pos = body.find(f"## {section}")
        if pos == -1:
            issues.append(f"missing body section: '## {section}'")
        elif pos <= last:
            issues.append(f"body section out of order: '## {section}'")
        else:
            last = pos
    for section, subs in schema["subsections"].items():
        for sub in subs:
            if f"### {sub}" not in body:
                issues.append(f"missing subsection '### {sub}' under '## {section}'")

    if fm.get("type") == "research":
        findings = body.split("## Findings", 1)[-1].split("## Implications", 1)[0]
        # Table rows are exempt (tags go in a column or the spot-check covers them);
        # every prose or bullet line in Findings must carry a tag.
        claims = [l for l in findings.splitlines()
                  if l.strip() and not l.startswith("#") and not l.lstrip().startswith("|")]
        untagged = [l for l in claims if not TAG_RE.search(l)]
        if untagged:
            issues.append(f"{len(untagged)} Findings line(s) without an evidence tag, e.g. {untagged[0][:60]!r}")

    for n, line in enumerate(text.splitlines(), 1):
        if FORBIDDEN_RE.search(line):
            issues.append(f"line {n}: forbidden path or identifier")
    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    rc = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        issues = validate(path) if path.is_file() else [f"not a file: {path}"]
        print(f"[{'OK' if not issues else 'FAIL'}] {path}")
        for issue in issues:
            print(f"  - {issue}")
        rc |= bool(issues)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
