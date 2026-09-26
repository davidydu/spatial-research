---
type: plan
project: spatial-spec
status: ready
scope: D-26 Wave 0 vault scaffolding and the meeting-cut research waves (angles 1a, 1c, 2, 3, 5, mapping-A/B, citation audit, angle 13 for P-E)
date: 2026-09-25
design: "[[2026-09-25-python-rust-architecture-research-design]]"
---

# D-26 Research Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Research subagents are dispatched with the Agent tool as described in Task 9; audits per Task 12.

**Goal:** Produce the meeting cut of decision record D-26 — pre-registered, evidence-backed, cited, audited — plus the 13 discriminating Python-surface mapping entries, following the vault's own decision-record discipline.

**Architecture:** Wave 0 (main session) files the open question, extends conventions, pins the precedent clones, commits the mapping skeleton and the pre-registration *before* any research exists. Waves 1–2 dispatch framing-blind Claude general-purpose subagents (one note per agent) that write only their own output file; the main session validates each note mechanically (`validate_d26_note.py`, stem/leak/wikilink checks) and spot-checks five claims per note. Wave 3 runs a citation audit and a "case for P-E" inference audit with fresh agents; the main session writes the cost angle, the recommendation matrix, and the D-26 draft, then hands it to David.

**Tech Stack:** Claude Code Agent tool (`subagent_type: general-purpose`, `model: fable`); Codex reviewers via the `iterative-review-workflow` skill for audits (fallback: fresh Claude agents); Python 3 + PyYAML (present: 6.0.1); git; Quartz build only at publication.

**Context files (main session loads before starting):**
- `90 - Meta/2026-09-25-python-rust-architecture-research-design.md` — the approved design (never given to research subagents)
- `90 - Meta/workflow.md`, `90 - Meta/conventions.md`
- `90 - Meta/plans/2026-04-21-phase1-coverage-dispatch.md` — the dispatch pattern being reused

**Ordering with the other two plans:**
1. `private/plans/2026-09-25-vault-publication-gate.md` (gitignored; it holds the real values) — run first (history rewrite before new commits).
2. This plan, Tasks 1–8 (Wave 0).
3. `spatial-rs/docs/superpowers/plans/2026-09-25-check-cli.md` — in parallel with Wave 1; must be done before Wave 2's angle 3.
4. This plan, Tasks 9–13.

**Out of scope:** angles 1b, 4, 6, 7, 9, 11, 12, the second mapping rater, angle 13 for cells other than P-E, the reader study, the overlay callout and `index.md` reviewer block (all after the meeting, per the design §9).

---

## File structure

| Path (under the vault root) | Created by |
|---|---|
| `20 - Research Notes/20 - Open Questions.md` (Q-165 appended) | Task 1 |
| `90 - Meta/conventions.md` (types table + external citations + labels) | Task 2 |
| `20 - Research Notes/40 - Decision Queue.md` (D-26 entry) | Task 3 |
| `90 - Meta/reference-clones.md` | Task 4 |
| `90 - Meta/scripts/validate_d26_note.py`, `90 - Meta/scripts/d26_wave_check.sh`, fixtures | Task 5 |
| `35 - Python Surface Mapping/00 - Python Mapping Overview.md` + 13 entries | Task 6 |
| `20 - Research Notes/50 - Decision Records/D-26.md` (pre-registration) | Task 7 |
| `00 - Index.md`, `90 - Meta/2026-07-07-session-resume-guide.md`, `90 - Meta/progress-log.md` (pointers) | Task 8 |
| `20 - Research Notes/50 - Decision Records/D-26-research/D-26-01a-…`, `D-26-01c-…` | Wave 1 |
| `…/D-26-02-…`, `D-26-03-…`, `D-26-05-…`; mapping entry bodies | Wave 2 |
| `…/D-26-08-…`, `D-26-10-…`, `D-26-13-case-for-p-e.md`, `90 - Meta/2026-09-25-d26-citation-audit.md` | Wave 3 / main |

Outside the vault: `/Users/david/Documents/David_code/reference/<repo>/` clones (Task 4).

## Task 1: File the open question

**Files:** Modify `20 - Research Notes/20 - Open Questions.md` (append at end)

- [ ] **Step 1: Append Q-165**

```markdown
## Q-165 — [2026-09-25] Host-language architecture (Rust/Python core, external/embedded student surface) asserted, not researched

The vault records "Do not use Python as the compiler-core owner" as a non-goal
(`90 - Meta/2026-06-26-rust-first-spatial-dsl-overlay.md`, Non-Goals) and
"The external-DSL choice itself is right for teaching … diagnostics are fully
owned" (`90 - Meta/2026-07-07-fundamental-design-review.md`, Issue 2) without a
decision record or research notes. The course professor's stated position is
that Python is easier to teach and to pick up. Which language hosts the
compiler core, which surface students write, and how Python integrates need
the same treatment as D-01..D-25.

Source: `90 - Meta/2026-06-26-rust-first-spatial-dsl-overlay.md`; `90 - Meta/2026-07-07-fundamental-design-review.md`
Blocked by: —
Status: needs-architectural-decision
Decision criteria: D-26 pre-registration (hypotheses, weights, reversal conditions) → research angles → recommendation matrix → user decision among cells R-X, R-E, R-B, P-X, P-E, P-B.
Resolution: tracked by [[D-26]]
```

- [ ] **Step 2: Verify the ID is unique**

Run: `grep -c '^## Q-165' "20 - Research Notes/20 - Open Questions.md"`
Expected: `1`.

## Task 2: Conventions

**Files:** Modify `90 - Meta/conventions.md`

- [ ] **Step 1: Add the in-use and new types to the "Required types" table** (append rows after `cross-ref`)

```markdown
| `decision-record` | Decision records under `20 - Research Notes/50 - Decision Records/` | `decision-id`, `related-questions`, `status`, `date` |
| `decision-queue` | The decision queue | `date` |
| `research` | Per-angle research notes under `D-NN-research/` | `decision`, `angle`; **from D-26 onward also** `discriminates`, `sources`, `verified`, `status` |
| `research-note` | Free-standing research notes (legacy; prefer `research` or `deep-dive`) | `topic`, `date`, `status` |
| `decision` / `handoff` | Legacy one-off notes; do not create new ones | — |
| `reference` | Manifests of external material (e.g. [[reference-clones]]) | `date` |
| `python-mapping-index` | Index of `35 - Python Surface Mapping/` | `date_started` |
| `python-mapping` | Per-construct entries under `35 - Python Surface Mapping/` | `construct`, `spec_entry`, `grammar_rule`, `per_style`, `obligations_at_risk`, `raters`, `verified`, `status` |
```

- [ ] **Step 2: Add an "External citations" subsection after "Source code citations"**

```markdown
### External citations (from D-26 onward)

- Code in a pinned external clone: `<repo>@<7-char sha>:<path>:<L1-L2>`, e.g.
  `calyx@1a2b3c4:calyx-py/calyx/builder.py:40-88`. The full SHA, upstream URL,
  and clone date live in [[reference-clones]]; a reader rebuilds
  `https://github.com/<org>/<repo>/blob/<sha>/<path>#L<L1>-L<L2>`.
- `spatial-rs` (not public) uses the same form, `spatial-rs@<sha>:<path>:<L1-L2>`.
- Documentation and papers: `<URL> (accessed YYYY-MM-DD)`.
- Absolute local paths (`/Users/...`) are not citations and must not appear in
  new notes.
- Every factual claim in a `research` or `python-mapping` note carries an
  evidence tag: `[measured]`, `[precedent-measured]`, `[designed]`, or
  `[judgment]`. Untagged claims fail the spot-check.
```

- [ ] **Step 3: Add the mapping vocabulary to "Status vocabulary"**

```markdown
**Python surface mapping labels (`python-mapping` entries):**
- `expressible`: `yes` / `awkward` (needs a construct outside the style's allowed-Python subset) / `no` (with the data-model citation)
- `info_preserved`: subset of `[spans, literal_types, size_vs_int, scope, order]` the style keeps
- `error_locus`: `python-time` / `ir-check` / `runtime` / `silent`
- `silently_divergent`: hazards where Python evaluates with its own semantics before the DSL sees the value
```

- [ ] **Step 4: Verify the file still parses as the vault expects**

Run: `python3 - <<'EOF'
import re,yaml,pathlib
t=pathlib.Path("90 - Meta/conventions.md").read_text()
print(yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n",t,re.S).group(1))["type"])
EOF`
Expected: `conventions`.

## Task 3: Decision Queue entry

**Files:** Modify `20 - Research Notes/40 - Decision Queue.md` (append after D-25)

- [ ] **Step 1: Append**

```markdown
## D-26 — [Q-165] Choose the host-language architecture: compiler core (Rust / Python) × student surface (external DSL / Python-embedded / both) × Python integration depth.
Source: 90 - Meta/2026-06-26-rust-first-spatial-dsl-overlay.md (Non-Goals); 90 - Meta/2026-07-07-fundamental-design-review.md (Issue 2)
Decision criteria: User decision among cells R-X, R-E, R-B, P-X, P-E, P-B after the pre-registered D-26 protocol; integration depth (I0/I1/I1′/I2/In) chosen for R-* cells.
```

- [ ] **Step 2: Update the count in the intro line** ("25 items" → "26 items").

## Task 4: Reference clones and manifest

**Files:** Create `/Users/david/Documents/David_code/reference/` (outside the vault); create `90 - Meta/reference-clones.md`

- [ ] **Step 1: Clone at depth 1 and record the SHAs**

```bash
mkdir -p /Users/david/Documents/David_code/reference && cd /Users/david/Documents/David_code/reference
for r in calyxir/calyx cucapra/dahlia cornell-zhang/allo exo-lang/exo pymtl/pymtl3 amaranth-lang/amaranth pola-rs/polars; do
  n=${r#*/}; git clone --depth 1 "https://github.com/$r.git" "$n" && printf '%s %s %s\n' "$n" "https://github.com/$r" "$(git -C "$n" rev-parse HEAD)"
done
```
Expected: seven lines `name url sha`. If a URL 404s, find the current upstream (`gh search repos <name>`) and record the corrected URL in the manifest; do not guess.

- [ ] **Step 2: Write the manifest** (`90 - Meta/reference-clones.md`)

```markdown
---
type: reference
project: spatial-spec
date: 2026-09-25
---

# Reference Clones (D-26 precedent material)

Shallow clones under `David_code/reference/` (outside the vault; never
published). Citations use `<name>@<7-char sha>:<path>:<L1-L2>`; the full SHA
below rebuilds a GitHub blob URL. Re-clone at the same SHA to reproduce.

| name | role in D-26 | upstream | full SHA | cloned | licence |
|---|---|---|---|---|---|
| calyx (+ calyx-py) | Python builder over a Rust compiler core; IR-level boundary | https://github.com/calyxir/calyx | <sha> | 2026-09-25 | <from LICENSE> |
| dahlia | external DSL whose type system is the legality checker; emits Calyx | https://github.com/cucapra/dahlia | <sha> | 2026-09-25 | <…> |
| allo | Python AST-transform DSL on MLIR, HLS backend; teaching use | https://github.com/cornell-zhang/allo | <sha> | 2026-09-25 | <…> |
| exo | Python AST-transform DSL; forbids host metaprogramming | https://github.com/exo-lang/exo | <sha> | 2026-09-25 | <…> |
| pymtl3 | all-Python HDL with AST-transformed blocks; course use | https://github.com/pymtl/pymtl3 | <sha> | 2026-09-25 | <…> |
| amaranth | all-Python HDL; `Value.__bool__` raises; frame-inspection naming | https://github.com/amaranth-lang/amaranth | <sha> | 2026-09-25 | <…> |
| polars | Rust core + PyO3 bindings exemplar (integration depth I2 only) | https://github.com/pola-rs/polars | <sha> | 2026-09-25 | <…> |
| spatial-rs | the Rust prototype (local only, not public) | local: David_code/spatial-rs | <sha> | 2026-09-25 | — |
| spatial | the original Scala Spatial (local clone of stanford-ppl/spatial + local EE109 lane commit) | https://github.com/stanford-ppl/spatial | <sha> | 2026-09-25 | <from LICENSE> |

By URL only (no clone): HeteroCL, JAX, Taichi, Triton, TVMScript, MLIR
`Location`, Ruff (`maturin bindings = "bin"`), IPython cell magics; Chisel
`SourceInfo` is cited from the local `spatial` clone.
```
Fill `<sha>` and licence from `LICENSE*` in each clone; for the two local repos
use `git -C /Users/david/Documents/David_code/<repo> rev-parse HEAD`. The
`spatial-rs` row's upstream column deliberately says `local:` so a reader knows
the link cannot be rebuilt.

## Task 5: Validation scripts

**Files:** Create `90 - Meta/scripts/validate_d26_note.py`, `90 - Meta/scripts/d26_wave_check.sh`, `90 - Meta/scripts/fixtures/d26_research_valid.md`, `90 - Meta/scripts/fixtures/d26_research_invalid.md`

- [ ] **Step 1: Write the fixtures first**

`fixtures/d26_research_valid.md`:
```markdown
---
type: "research"
decision: "D-26"
angle: "1a"
discriminates: surface-embedding
sources:
  - "allo@0000000:README.md:1-10"
verified: []
status: draft
---
## Scope
x
## Findings
Claim [precedent-measured] (allo@0000000:README.md:1-10).
## Implications
### R-X
### R-E
### R-B
### P-X
### P-E
### P-B
## Evidence against
y
## Open questions
## Confidence
low — fixture
```

`fixtures/d26_research_invalid.md`: the same file with `sources:` written as `sources: [[allo@0000000:README.md:1-10]]`, no `## Evidence against` section, and the Findings line lacking a tag.

- [ ] **Step 2: Write the validator**

`90 - Meta/scripts/validate_d26_note.py`:
```python
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
```

- [ ] **Step 3: Run it on the fixtures**

Run: `python3 "90 - Meta/scripts/validate_d26_note.py" "90 - Meta/scripts/fixtures/d26_research_valid.md" "90 - Meta/scripts/fixtures/d26_research_invalid.md"; echo "exit=$?"`
Expected: `[OK]` for the valid fixture; `[FAIL]` for the invalid one listing the list-of-strings issue, the missing `## Evidence against`, and one untagged Findings line; `exit=1`.

- [ ] **Step 4: Write the wave check script**

`90 - Meta/scripts/d26_wave_check.sh`:
```bash
#!/usr/bin/env bash
# Post-wave mechanical checks for D-26. Run from the vault root after every wave.
# Usage: d26_wave_check.sh [--skip-status]   (use --skip-status during Wave 0,
# when the main session legitimately has many uncommitted files; after the
# Wave 0 commit the status section is the audit of what subagents touched)
set -u
shopt -s nullglob
cd "$(dirname "$0")/../.."
fail=0
research=("20 - Research Notes/50 - Decision Records/D-26-research/"*.md)
mapping=("35 - Python Surface Mapping/"[1-9A-Z]*.md)
if [ "${1:-}" != "--skip-status" ]; then
  echo "== unexpected changes (expect none)"
  git status --porcelain | grep -vE '(D-26|d26|35 - Python Surface Mapping|progress-log|2026-09-25)' && fail=1
fi
echo "== schema (${#research[@]} research notes, ${#mapping[@]} mapping entries)"
if [ $(( ${#research[@]} + ${#mapping[@]} )) -gt 0 ]; then
  # ${arr[@]+"${arr[@]}"} is the bash-3.2-safe way to expand a possibly-empty array under set -u
  python3 "90 - Meta/scripts/validate_d26_note.py" ${research[@]+"${research[@]}"} ${mapping[@]+"${mapping[@]}"} || fail=1
fi
echo "== D-26.md frontmatter"
python3 - <<'EOF' || fail=1
import re,yaml,pathlib,sys
p=pathlib.Path("20 - Research Notes/50 - Decision Records/D-26.md")
if p.exists():
    fm=yaml.safe_load(re.match(r"\A---\n(.*?)\n---\n",p.read_text(),re.S).group(1))
    ok=fm.get("type")=="decision-record" and isinstance(fm.get("related-questions"),list) and all(isinstance(q,str) for q in fm["related-questions"])
    print("D-26.md frontmatter", "ok" if ok else "BAD (type or related-questions)"); sys.exit(0 if ok else 1)
EOF
echo "== duplicate stems (baseline 23)"
dups=$(find . -name '*.md' -not -path './.git/*' -exec basename {} .md \; | sort | uniq -d | wc -l | tr -d ' ')
echo "duplicates: $dups"; [ "$dups" -le 23 ] || fail=1
echo "== leak grep (expect nothing)"
grep -rnE 'accelerator-bandits|EE109-Spr-2026|/Users/david/|\.pem|ec2-[0-9]|us-west-2' "35 - Python Surface Mapping" "20 - Research Notes/50 - Decision Records/D-26"* 2>/dev/null && fail=1
echo "== citation density per research note (>= 8) and unverified count"
for f in ${research[@]+"${research[@]}"}; do
  c=$(grep -cE '@[0-9a-f]{7,}:|https?://' "$f"); u=$(grep -c 'inferred, unverified' "$f")
  printf '%3d cites %2d unverified  %s\n' "$c" "$u" "$f"; [ "$c" -ge 8 ] || fail=1
done
echo "== citation bounds"
python3 - <<'EOF' || fail=1
import re,subprocess,sys,pathlib
man=pathlib.Path("90 - Meta/reference-clones.md").read_text()
shas={r.split("|")[1].strip().split()[0]: r.split("|")[4].strip() for r in man.splitlines() if r.startswith("| ") and ("https://" in r or "local:" in r)}
LOCAL={"spatial-rs","spatial"}   # live under David_code/<name>, not reference/<name>
bad=0
for f in list(pathlib.Path("20 - Research Notes/50 - Decision Records").glob("D-26*/*.md"))+list(pathlib.Path("35 - Python Surface Mapping").glob("*.md")):
    for m in re.finditer(r"([a-z0-9-]+)@([0-9a-f]{7,}):([^\s:`]+):(\d+)-(\d+)", f.read_text()):
        name,sha,path,l1,l2=m.groups()
        root=pathlib.Path("/Users/david/Documents/David_code")/(name if name in LOCAL else f"reference/{name}")
        full=shas.get(name,""); target=root/path
        if not full.startswith(sha): print(f"{f}: {name}@{sha} not the manifest SHA"); bad+=1
        elif not target.is_file(): print(f"{f}: missing {target}"); bad+=1
        elif int(l2) > sum(1 for _ in open(target,errors="ignore")): print(f"{f}: {path}:{l1}-{l2} past EOF"); bad+=1
sys.exit(1 if bad else 0)
EOF
echo "== wikilinks in new notes resolve"
python3 - <<'EOF' || fail=1
import re,pathlib,sys
stems={p.stem for p in pathlib.Path(".").rglob("*.md") if ".git" not in p.parts}
paths={str(p.with_suffix("")) for p in pathlib.Path(".").rglob("*.md")}
bad=0
for f in list(pathlib.Path("20 - Research Notes/50 - Decision Records").glob("D-26*/*.md"))+list(pathlib.Path("35 - Python Surface Mapping").glob("*.md"))+[pathlib.Path("20 - Research Notes/50 - Decision Records/D-26.md")]:
    if not f.exists(): continue
    for m in re.finditer(r"\[\[([^\]|#]+)", f.read_text()):
        t=m.group(1).strip()
        if t not in stems and t not in paths: print(f"{f}: unresolved [[{t}]]"); bad+=1
sys.exit(1 if bad else 0)
EOF
echo "== RESULT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"; exit $fail
```
Run: `chmod +x "90 - Meta/scripts/d26_wave_check.sh" && "90 - Meta/scripts/d26_wave_check.sh" --skip-status`
Expected: `== schema (0 research notes, 0 mapping entries)`, `duplicates: 23`, empty leak/density/bounds/wikilink sections, `RESULT: PASS`. (Without `--skip-status` the status section lists the uncommitted Wave 0 files — expected until Task 8's commit; from Wave 1 on, run it without the flag.)

## Task 6: Mapping skeleton

**Files:** Create `35 - Python Surface Mapping/00 - Python Mapping Overview.md` and 13 entries.

- [ ] **Step 1: Write the overview**

```markdown
---
type: python-mapping-index
project: spatial-spec
date_started: 2026-09-25
---

# Python Surface Mapping — Overview

One entry per discriminating construct of the external DSL
(`spatial-rs@<sha>:docs/language-spec.md`, closed EBNF), rated under three
Python embedding styles — tracing, builder, AST transform — on the same rubric
as the external DSL itself. Labels are defined in [[conventions]] ("Python
surface mapping labels"). Two independent raters per entry; agreement and
adjudication are recorded here once both ratings exist.

Cells: R-X, R-E, R-B, P-X, P-E, P-B (core Rust/Python × surface external/
embedded/both). This folder is the evidence for D-26 angles 2–4 and becomes the
build spec only if an E or B cell is chosen.

## Embedding styles (summary)

Filled by the mapping agents from their entries: the allowed-Python subset per
style, the hazards common to all entries, the "silently divergent" class.

## Coverage

| Entry | Grammar rules | Status |
|---|---|---|
| [[10 - Python Controller Bodies]] | `foreach_ctrl`, `memreduce_ctrl`, `memfold_ctrl`, `reduce_expr`, `fold_expr`, `value_block` | skeleton |
| [[20 - Python If Expressions]] | `if_expr`, `if_stmt` | skeleton |
| [[30 - Python Assignment]] | `assign_stmt`, `lvalue` | skeleton |
| [[40 - Python FSM]] | `fsm_ctrl` | skeleton |
| [[50 - Python FixPt and Size]] | `fixed_type`, `const_decl`, `const_expr` | skeleton |
| [[60 - Python Bulk IO and Views]] | `load_stmt`, `store_stmt`, `memory_view`, `view_suffix`, `slice`, `transfer_par` | skeleton |
| [[70 - Python Par and Schedules]] | `schedule`, `foreach_ctrl` (`par`/`tail`) | skeleton |
| [[80 - Python Kernel Ports and Requires]] | `kernel_decl`, `port_decl`, `port_type`, `dram_shape`, `requires_block` | skeleton |
| [[90 - Python Naming and Scoping]] | cross-cutting: `ident`, Names/Scope/Lifetime section | skeleton |
| [[A0 - Python Size to Int Embedding]] | cross-cutting: `const_expr` vs `expr`, E0506 | skeleton |
| [[B0 - Python Literal Typing]] | cross-cutting: `value_decl` with `scalar_type`, `scalar_literal` | skeleton |
| [[C0 - Python Fifo Deq Timing]] | cross-cutting: `primary` (`.deq()`), `fifo_enq_stmt` | skeleton |
| [[D0 - Python Declaration Order]] | cross-cutting: declaration-ID order (obligation Rule 4) | skeleton |

Deferred until an E/B cell is chosen: `Lut`/`Reg`/`LineBuffer`/`RegFile`
constructors, `reset_stmt`, `shift_stmt`, `builtin_call`, `.value`, `Bool`,
comments/lexing.
```

- [ ] **Step 2: Write the 13 entries with frontmatter only** (one example; the others differ in `construct`, `spec_entry`, `grammar_rule`, and the stem)

`35 - Python Surface Mapping/10 - Python Controller Bodies.md`:
```markdown
---
type: "python-mapping"
construct: "controller bodies: foreach / memreduce / memfold / reduce / fold with yield"
spec_entry: "[[10 - Spec/10 - Language Surface/10 - Controllers|Controllers]]"
grammar_rule: "foreach_ctrl, memreduce_ctrl, memfold_ctrl, reduce_expr, fold_expr, value_block"
external_dsl:
  concepts_without_hardware_meaning: []
per_style:
  tracing: { expressible: null, info_preserved: [], error_locus: null, silently_divergent: [] }
  builder: { expressible: null, info_preserved: [], error_locus: null, silently_divergent: [] }
  ast: { expressible: null, info_preserved: [], error_locus: null, silently_divergent: [] }
obligations_at_risk: []
raters: []
verified: []
status: skeleton
---
## External DSL form
## Python forms
## Assessment
## Precedent
```

`spec_entry` values (use the full-path form where the stem is duplicated in the vault):

| Stem | `spec_entry` |
|---|---|
| 10 - Python Controller Bodies | `[[10 - Spec/10 - Language Surface/10 - Controllers\|Controllers]]` |
| 20 - Python If Expressions | `[[30 - Control Semantics]]` |
| 30 - Python Assignment | `[[10 - Effects and Aliasing]]` |
| 40 - Python FSM | `[[10 - Spec/10 - Language Surface/10 - Controllers\|Controllers]]` |
| 50 - Python FixPt and Size | `[[50 - Data Types]]` |
| 60 - Python Bulk IO and Views | `[[60 - Host and IO]]` |
| 70 - Python Par and Schedules | `[[20 - Scheduling Model]]` |
| 80 - Python Kernel Ports and Requires | `[[90 - Host-Accel Boundary]]` |
| 90 - Python Naming and Scoping | `[[90 - Aliases and Shadowing]]` |
| A0 - Python Size to Int Embedding | `[[50 - Data Types]]` |
| B0 - Python Literal Typing | `[[50 - Data Types]]` |
| C0 - Python Fifo Deq Timing | `[[80 - Streaming]]` |
| D0 - Python Declaration Order | `[[10 - Effects and Aliasing]]` |

- [ ] **Step 3: Verify stems are unique and links resolve**

Run: `"90 - Meta/scripts/d26_wave_check.sh" --skip-status`
Expected: `== schema (0 research notes, 13 mapping entries)` with each skeleton `[OK]` (empty sections are present as headings; `status: skeleton` and `null` ratings are accepted), duplicates still 23, `RESULT: PASS`.

## Task 7: D-26 pre-registration

**Files:** Create `20 - Research Notes/50 - Decision Records/D-26.md`

- [ ] **Step 1: Write the pre-registration** (the Findings/Recommendation/Decision sections are added in Wave 3; nothing below is edited after commit except filling the weights table)

```markdown
---
type: decision-record
decision-id: D-26
related-questions: ["Q-165"]
status: pre-registered
date: 2026-09-25
---

# D-26 — Host-Language Architecture (compiler core × student surface × Python integration)

## Question

Which language hosts the Spatial rewrite's compiler core, which surface do
students write, and how does Python integrate?

| | Surface: external DSL (X) | Surface: Python-embedded (E) | Surface: both (B) |
|---|---|---|---|
| **Core: Rust (R)** | R-X | R-E | R-B |
| **Core: Python (P)** | P-X | P-E | P-B |

Integration depth for R-* cells: I0 CLI only; I1 + Python testbenches over
JSON; I1′ CLI shipped as a wheel; I2 PyO3 bindings over `check`/`build`/`run`;
In notebook cell magic.

Embedding styles for E/B cells (evaluated, not pre-chosen): tracing/operator
overloading; builder/context-manager; AST transform; hybrids.

Source: `90 - Meta/2026-06-26-rust-first-spatial-dsl-overlay.md` (Non-Goals);
`90 - Meta/2026-07-07-fundamental-design-review.md` (Issue 2); Q-165 in
[[20 - Open Questions]].

## Pre-registration (committed before any research note exists)

### Hypotheses and measures

The professor's stated position is "Python is easy to teach and easy for
students to pick up" — a claim about the student surface (X vs E), not the
compiler core (R vs P). D-26 evaluates the surface axis on teachability and the
core axis on maintainability, cost, and simulator performance, and reports
them separately.

- **H1 — easy to pick up.** Measure: per Tier-0 lab, hardware concepts exposed
  vs. non-hardware host constructs a student must learn, tallied identically
  for Scala, the external DSL, and the Python hybrid (angle 2);
  install-to-first-`check` (angle 11, full plan).
- **H2 — easy to teach.** Measure: on the fixed mistake list, which surface
  catches each mistake earlier and which explains it better, from real tool
  output (angle 3); precedent teaching reports (angle 1); reader study (angle
  14) if run.
- **H3 — steelman (not the professor's words): Python is already the course's
  tooling language and TAs can fix a Python compiler.** Measure: scenario cost
  (angle 8) and what catches a maintainer's mistake (angle 7, full plan).
  Written to win in angle 13.

### Audience

Students, by the professor's framing. Maintainer findings are labelled as such
and never counted under H1/H2.

### Decision rule

Winner reported under (a) David's weights, (b) the Rust-leaning instructor's
weights, (c) equal weights, (d) a surface-only weighting (H1+H2 only). Weights
are recorded here before Wave 1:

| Angle | David | Rust-leaning instructor |
|---|---|---|
| 1 precedent | | |
| 2 surface comparison | | |
| 3 error paths | | |
| 5 boundary | | |
| 8 cost | | |
| 11 course ops (full plan) | | |
| 12 simulator speed (full plan) | | |

### Reversal conditions

- **R-* cells lose** if every entry in `35 - Python Surface Mapping/` is
  `expressible: yes` with `info_preserved` = all five under at least one style,
  Python error paths reach parity on the whole mistake list, and precedent or
  spike evidence shows a Python simulator within k× of a Rust one on Tier-0
  (k = 10 unless David sets another value before the Wave 0 commit; record the
  value here).
- **P-* cells lose** if any pre-registered obligation (spans, literal types,
  Size-vs-Int, scope, order) cannot be enforced before lowering under every
  style, or the simulator bound above is exceeded.
- **E/B cells are recommended only with these guarantees:** one IR, one
  diagnostic catalog, "same mistake, same message" golden test in both
  surfaces, every lab maintained in both surfaces, wheels with no Rust
  toolchain, CI releases, a message catalog a TA can edit without rebuilding
  the core.

### Fixed lists

- **Angle 2 programs (Tier-0):** Lab1Part2 (dense DRAM/SRAM tiling), Lab1Part6
  (scalar reduce), Lab2Part6 (tiled GEMM with `memfold`). Scala originals:
  `spatial@<sha>:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala`,
  `spatial-rs@<sha>:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala`,
  `spatial-rs@<sha>:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala`.
  External-DSL forms from the canonical fragments in `docs/language-spec.md`
  (the pre-canonical `accel!` corpus in `examples/ee109/src/lib.rs` is not a
  source for this angle).
- **Angle 3 mistakes (top 8; confirmed against private course material, not
  cited):** (1) tile bound not dividing the extent; (2) `par` not dividing the
  range; (3) `Int` used where `FixPt` is required; (4) SRAM read before `load`;
  (5) DRAM written directly inside a loop instead of `store`; (6) `reduce`
  without `init`; (7) a host/Python value used inside the accelerator body
  (staging leak); (8) LUT index without a `requires` bound.

### Stopping rule

Meeting cut: angles 1a, 1c, 2, 3, 5, 8, 10, 13 (P-E) audited. Full plan: every
angle audited or recorded "not decisive" with a reason.

## Research findings

(Wave 3.)

## Option matrices

(Wave 3: core-language sub-matrix; surface-embedding sub-matrix; combination
table with integration depth.)

## Recommendation

(Wave 3.)

## Rejected alternatives and answers to the "case for" notes

(Wave 3.)

## Spillover (host-language-neutral findings about the DSL itself)

(Wave 3 — routed to the syntax teachability review, not decided here.)

## Decision

(David.)
```

- [ ] **Step 2: Fill the weights table** with David's numbers now and the Rust-leaning instructor's when available (a blank column is allowed; the decision rule then reports (a), (c), (d) only).

## Task 8: Pointers, log, commit

**Files:** Modify `00 - Index.md`, `90 - Meta/2026-07-07-session-resume-guide.md`, `90 - Meta/progress-log.md`

- [ ] **Step 1: Index pointer** — under "Folder map" add a row: `| \`35 - Python Surface Mapping/\` | Per-construct evidence for D-26 (Python embedding styles vs the external DSL). |`

- [ ] **Step 2: Resume guide** — add at the top of "Where Things Stand" a bullet: `- **D-26 host-language research (2026-09-25):** design [[2026-09-25-python-rust-architecture-research-design]]; plan [[2026-09-25-d26-research-dispatch]]; record [[D-26]] (pre-registered). The deck waits for the meeting cut.`

- [ ] **Step 3: Progress log** — prepend a `## 2026-09-25 — D-26 Wave 0` block listing Q-165, the conventions additions, the manifest SHAs, the skeleton, the pre-registration, and the validator/wave-check scripts.

- [ ] **Step 4: Run the wave check, then commit Wave 0**

```bash
"90 - Meta/scripts/d26_wave_check.sh" --skip-status | tail -1
git add "20 - Research Notes/20 - Open Questions.md" "90 - Meta/conventions.md" "20 - Research Notes/40 - Decision Queue.md" "90 - Meta/reference-clones.md" "90 - Meta/scripts" "35 - Python Surface Mapping" "20 - Research Notes/50 - Decision Records/D-26.md" "00 - Index.md" "90 - Meta/2026-07-07-session-resume-guide.md" "90 - Meta/progress-log.md" "90 - Meta/plans/2026-09-25-d26-research-dispatch.md" "90 - Meta/2026-09-25-check-cli-slice-contract.md"
git commit -m "D-26 Wave 0: pre-registration, mapping skeleton, conventions, reference manifest"
```
Expected: `RESULT: PASS`; one commit. From here `git status` is the audit of what subagents touch.

## Task 9: Wave 1 — angles 1a and 1c

**Files:** Subagents create `20 - Research Notes/50 - Decision Records/D-26-research/D-26-01a-precedent-python-over-core.md` and `D-26-01c-precedent-external-dsl-over-core.md`.

- [ ] **Step 1: Assemble the shared prompt skeleton** (verbatim; substitute the `{…}` fields per angle; never include the design doc, the plan, or any preference)

```text
You are writing one research note for an architecture decision in an Obsidian research vault. Write ONLY the file at {OUTPUT_PATH}; do not create, edit, or delete anything else; do not delegate.

## The decision (labels only — you are not told which is preferred, and there is no default)
A hardware DSL compiler is being rewritten. Six candidate architectures are labelled by
compiler-core language × student-facing surface:
  R-X: Rust core, students write an external DSL (.spatial files)
  R-E: Rust core, students write a Python-embedded DSL
  R-B: Rust core, both surfaces over one IR
  P-X: Python core, external DSL
  P-E: Python core, Python-embedded DSL
  P-B: Python core, both surfaces
Python embedding styles are: tracing/operator overloading; builder/context-manager API; AST transform; hybrids. For R-* cells, "integration depth" may be I0 (CLI only), I1 (Python testbenches over JSON), I1′ (CLI shipped as a wheel), I2 (PyO3 bindings), In (notebook cell magic).

## Your angle: {ANGLE_ID} — {ANGLE_TITLE}
{QUESTION}

## Sources you may cite (open them; do not cite what you did not open)
{SOURCES}
Pinned clones live under /Users/david/Documents/David_code/reference/<name>/ at the SHAs in the manifest below; the two local repositories are /Users/david/Documents/David_code/spatial-rs (the Rust prototype, cite as spatial-rs@<sha>:…) and /Users/david/Documents/David_code/spatial (the original Scala Spatial, cite as spatial@<sha>:…). Cite code as <name>@<7-char sha>:<path>:<L1-L2>; cite docs/papers as <URL> (accessed 2026-09-25). Never write an absolute local path into the note. Never reference any course lab repository, student name, or GitHub Classroom organisation.
Manifest:
{MANIFEST_ROWS}

## Evidence rules
- Tag every factual claim in Findings with exactly one of [measured] [precedent-measured] [designed] [judgment]. [precedent-measured] means you read the code or ran the tool; [designed] means you constructed the example yourself; [judgment] is your inference.
- Untagged or uncited behavioural claims must be marked "(inferred, unverified)".
- Write "## Evidence against": the strongest evidence against your own leaning. It is mandatory and must not be empty.
- Under "## Implications", write one "### <cell>" subsection for each of R-X, R-E, R-B, P-X, P-E, P-B, even if it says "not affected by this angle".
- Set `discriminates:` to core-language, surface-embedding, integration-depth, both, or neither — what this angle actually distinguishes.
- Length: 900–1800 words of body. Prefer tables for comparisons.

## Required file shape (frontmatter exactly; body sections in this order)
---
type: "research"
decision: "D-26"
angle: "{ANGLE_ID}"
discriminates: <one of the five values>
sources:
  - "<citation>"        # one per line, quoted, at least 8
verified: []
status: draft
---
## Scope
## Findings
## Implications
### R-X
### R-E
### R-B
### P-X
### P-E
### P-B
## Evidence against
## Open questions
## Confidence
<high|medium|low> — <reason>

{DELIVERABLES}
```

- [ ] **Step 2: Angle 1a substitutions**

- `{ANGLE_ID}`: `1a`; `{ANGLE_TITLE}`: `Precedent — Python frontend over a compiled core`
- `{QUESTION}`: `For each precedent (allo, exo, calyx-py over Calyx, pymtl3's AST-transformed blocks): where exactly is the Python↔core boundary (which artifact crosses it — source text, an AST, a typed IR, a builder API); how does a user error reach the user (which layer reports it, whether the message names a Python line or an IR object; quote two real messages); whether it is used in a course and what the maintainers say about that; who maintains it and how errors in the Python layer are tested. Which embedding style each one actually uses (they are often hybrids — say so).`
- `{SOURCES}`: the four clones (allo, exo, calyx, pymtl3) plus the projects' papers/docs by URL.
- `{DELIVERABLES}`: `Include a table: precedent | boundary artifact | style | error locus | teaching use (cited) | maintenance notes. In Implications, state for R-B and R-E which precedent's boundary they would resemble and what that precedent's known pain points are.`

- [ ] **Step 3: Angle 1c substitutions**

- `{ANGLE_ID}`: `1c`; `{ANGLE_TITLE}`: `Precedent — external DSL over a compiled core`
- `{QUESTION}`: `For dahlia (external DSL emitting Calyx; what its type system enforces before emission and what messages it gives), Calyx as a compilation target (what position/source information its IR carries and how errors are reported back), Ruff's maturin "bin" packaging (how a Rust CLI ships as a pip wheel with no Rust toolchain for users; what the wheel matrix looks like), and IPython cell magics (how an external language is hosted in notebooks with zero frontend): what each shows about R-X and P-X at integration depths I1′ and In, and about what an external DSL must build for tooling.`
- `{SOURCES}`: dahlia and calyx clones; Ruff repository `pyproject.toml`/docs by URL; maturin docs by URL; IPython custom-magics docs by URL.
- `{DELIVERABLES}`: `Include: the exact Ruff/maturin configuration lines that make the CLI a wheel (cited); the list of Dahlia static checks with their error messages (cited); Calyx's source-position mechanism (cited). In Implications, state what R-X and P-X gain at I1′ and In and what, if anything, they still lack.`

- [ ] **Step 4: Dispatch both in one message**

Two `Agent` calls, `subagent_type: general-purpose`, `model: fable`, `description` "D-26 angle 1a" / "D-26 angle 1c", `prompt` = skeleton with substitutions and the manifest rows pasted from `reference-clones.md`.
Expected: two notes appear at the output paths; nothing else changes.

- [ ] **Step 5: Mechanical check**

Run: `"90 - Meta/scripts/d26_wave_check.sh"`
Expected: `RESULT: PASS`. On FAIL, fix mechanical issues (a missing tag, an unquoted list item) by hand if ≤ 3, otherwise re-dispatch that agent quoting the validator output.

- [ ] **Step 6: Five-claim spot-check per note** (workflow rule)

Pick five cited claims per note; open the cited clone file at the pinned SHA or fetch the URL; confirm. 0 failures → add `verified: ["2026-09-25"]`; 1 → correct it in the note, add the date, and file the correction as a Q-NNN in `20 - Open Questions.md` (workflow rule); ≥ 2 → re-dispatch with the failed claims quoted. Record the outcome in the progress log.

- [ ] **Step 7: Commit Wave 1**

```bash
git add "20 - Research Notes/50 - Decision Records/D-26-research" "90 - Meta/progress-log.md"
git commit -m "D-26 Wave 1: precedent angles 1a and 1c"
```

## Task 10: Wave 2 — angles 2, 3, 5 and the mapping entries

**Preconditions:** Task 9 committed; `spatial-rs check` landed (check-cli plan, Task 5 green); the `spatial-rs` HEAD SHA recorded as `<sha>` for citations.

- [ ] **Step 1: Angle 2 substitutions** (output `D-26-02-student-surface-comparison.md`)

- `{ANGLE_TITLE}`: `Student-surface comparison on three Tier-0 programs`
- `{QUESTION}`: `For each of Lab1Part2 (dense DRAM/SRAM tiling), Lab1Part6 (scalar reduce), Lab2Part6 (tiled GEMM with memfold): present the Scala original (from the cited files), the external-DSL form (from the canonical fragments in the language spec — construct it faithfully where the spec gives only a fragment, tag it [designed]), and one Python form per embedding style (tracing, builder, AST; tag [designed]; use real precedent syntax from the clones where a precedent has the construct, tag [precedent-measured]). Then build a concept-introduction table with one row per concept a student must understand to write the program (e.g. tile, load, par, reduce identity, fixed-point width, context manager, lambda, decorator, implicit return), columns: concept | hardware meaning? (yes/no) | Scala | external DSL | Python-tracing | Python-builder | Python-AST — marking in which surfaces the concept appears. Do not use line counts as a measure. Apply the "no hardware meaning" test to every surface, including the external DSL's let/yield/using/:=.`
- `{SOURCES}`: `spatial@<sha>:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala`, `spatial-rs@<sha>:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala`, `spatial-rs@<sha>:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala`, `spatial-rs@<sha>:docs/language-spec.md` (Canonical Style and Canonical Construct Examples), the allo/exo/pymtl3/calyx clones. Not a source: `examples/ee109/src/lib.rs` (pre-canonical spelling).
- `{DELIVERABLES}`: `The three side-by-side listings in full (fenced, one fence per surface), the concept table, and a count per surface of concepts with no hardware meaning. Implications: which cells this discriminates (surface-embedding), and what a P-E form would need to add to reach the external DSL's concept count or vice versa.`

- [ ] **Step 2: Angle 3 substitutions** (output `D-26-03-error-paths.md`)

- `{ANGLE_TITLE}`: `Error-path study on the pre-registered mistake list`
- `{QUESTION}`: `For each of the eight mistakes in the list below, produce: (a) a minimal external-DSL program containing the mistake and the exact stderr and exit code of \`cargo run -q -p spatial-rs-cli -- check <file>\` run from /Users/david/Documents/David_code/spatial-rs (tag [measured]; if the compiler accepts the program or reports a legacy E0xxx/E01xx/E02xx/E04xx code instead of a canonical one, say so — that is a finding, not a failure); (b) the same mistake written in one precedent Python DSL where the construct exists (allo, exo, calyx-py, or pymtl3) and the real message obtained by running it if the tool runs locally in a venv under /tmp, otherwise the message text located in the precedent's source or tests (tag [precedent-measured] either way and say which); (c) the Scala Spatial message where you can locate it in the local Spatial clone's tests or source (tag [precedent-measured]) — do not attempt to run sbt. For each mistake: which surface catches it earliest (parse / check / trace / run / silent) and which message a first-year student could act on without help, with your reasoning tagged [judgment]. Mistakes: (1) tile bound not dividing the extent; (2) par not dividing the range; (3) Int used where FixPt is required; (4) SRAM read before load; (5) DRAM written directly inside a loop instead of store; (6) reduce without init; (7) a host/Python value used inside the accelerator body; (8) LUT index without a requires bound.`
- `{SOURCES}`: `spatial-rs@<sha>:docs/language-spec.md` (Diagnostics And Target Legality), `spatial-rs@<sha>:crates/spatial-rs-cli/`, the clones, `spatial@<sha>:test/spatial/tests/` for Scala messages (the local `/Users/david/Documents/David_code/spatial` clone; cite as `spatial@<sha>:path:lines`).
- `{DELIVERABLES}`: `A table: mistake | external-DSL code + exit | Python precedent + message | Scala message | earliest catch | actionable? Then the full transcripts in an appendix section "## Transcripts" (allowed after Confidence). Note which canonical codes (E0311–E0315) are specified but not emitted.`

- [ ] **Step 3: Angle 5 substitutions** (output `D-26-05-boundary-design.md`)

- `{ANGLE_TITLE}`: `Where the Python↔Rust boundary can sit, and what each choice costs in diagnostics`
- `{QUESTION}`: `Three candidate boundaries for R-E/R-B: (i) .spatial text plus a Python→line source map; (ii) an unchecked surface AST serialized from the closed EBNF, every node carrying a source span; (iii) the checked controller-tree IR after name/const/type resolution. For each: which diagnostics phases (parse, name, const-eval, type, typed-use, legality) still run in Rust on Python-originated programs; what a Python frontend must re-implement; how a message points back to the student's Python line; and what calyx-py/Calyx (IR-level boundary), Allo (AST→MLIR with locations), and MLIR Location do — cited. Also: for I1/I2, what exactly crosses the boundary today per ADR 0002 (the JSON envelopes) and what a PyO3 binding over check/build/run would expose.`
- `{SOURCES}`: `spatial-rs@<sha>:docs/adr/0002-file-cli-host-runtime.md`, `spatial-rs@<sha>:docs/language-spec.md` (Diagnostics And Target Legality; Closed EBNF), `spatial-rs@<sha>:crates/spatial-rs-core/src/frontend/source.rs`, `spatial-rs@<sha>:crates/spatial-rs-core/src/compiler.rs`, calyx and allo clones, MLIR docs by URL.
- `{DELIVERABLES}`: `A table boundary | Rust phases retained | Python re-implements | span provenance | precedent. A concrete recommendation of which boundary preserves every diagnostic, and the list of requirements it imposes on a future IR definition (span on every node; source registry admitting non-.spatial origins), tagged [judgment].`

- [ ] **Step 4: Mapping agents A and B** (prompt: the skeleton's decision block, evidence rules, and manifest, then the following; each agent replaces the **bodies** of its entries and fills `per_style`, `external_dsl`, `obligations_at_risk`, `raters: ["agent-A"]` / `["agent-B"]` — all other frontmatter keys stay as committed)

Agent A entries: `10 - Python Controller Bodies`, `20 - Python If Expressions`, `30 - Python Assignment`, `40 - Python FSM`, `90 - Python Naming and Scoping`, `D0 - Python Declaration Order`.
Agent B entries: `50 - Python FixPt and Size`, `60 - Python Bulk IO and Views`, `70 - Python Par and Schedules`, `80 - Python Kernel Ports and Requires`, `A0 - Python Size to Int Embedding`, `B0 - Python Literal Typing`, `C0 - Python Fifo Deq Timing`.

Task text for both: `For each entry: (1) "## External DSL form": quote the grammar rules named in the frontmatter from the closed EBNF and one canonical fragment, cited to spatial-rs@<sha>:docs/language-spec.md:L1-L2, and list the external DSL's own concepts without hardware meaning in external_dsl.concepts_without_hardware_meaning. (2) "## Python forms": the most faithful form under tracing, builder, and AST styles, each as a fenced Python snippet; where a precedent has the construct, use its real syntax and cite it [precedent-measured]; otherwise design it and tag [designed]; where a style cannot express it, write "not expressible" with a citation to the Python language reference (data model / expressions) explaining why. (3) Fill per_style.<style>: expressible (yes/awkward/no — awkward means a construct outside this allowed subset is needed: tracing = expressions, indexing, augmented assignment, method calls; builder = the above plus with-blocks and explicit builder calls; AST = ordinary Python statements re-interpreted by a transform), info_preserved (which of spans, literal_types, size_vs_int, scope, order the style keeps), error_locus (python-time / ir-check / runtime / silent — where the FIRST report of a misuse would come from), silently_divergent (cases where Python evaluates with its own semantics before the DSL sees the value, e.g. literal folding, chained comparisons, truthiness). (4) "## Assessment": the obligations from the language spec's Normative Static Obligation Calculus that this construct carries, and for R-B versus P-E who enforces each and when — fill obligations_at_risk as strings "<obligation> — under <cell>: <who, when>". (5) "## Precedent": which precedent does the equivalent, cited. Set status: draft (it is currently skeleton). Do not touch entries not assigned to you and do not edit the overview file.`

- [ ] **Step 5: Dispatch all five in one message** (angles 2, 3, 5, mapping A, mapping B), then run `d26_wave_check.sh`, five-claim spot-checks, `verified` dates.

- [ ] **Step 6: Main session fills the overview** (`00 - Python Mapping Overview.md`): the "Embedding styles (summary)" section from the 13 entries (allowed-Python subset per style as the agents applied it; hazards common to all entries; the silently-divergent list), the coverage table's status column (`skeleton` → `draft`), and a "Raters" line noting one rating per entry so far (the second rater is full-plan work). Then commit `D-26 Wave 2: surface, error paths, boundary, mapping entries`.

## Task 11: Main session — angle 8, angle 10, D-26 draft

**Files:** Create `D-26-research/D-26-08-cost.md`, `D-26-research/D-26-10-recommendation-matrix.md`; edit `D-26.md` sections marked "(Wave 3.)".

- [ ] **Step 1: Angle 8** using the design's §4 row 8: per cell, new work to reach Phase-1 parity on the 39 programs under the same architecture; shared assets credited to all; proxies (`validate.rs` 5,363 lines for the calculus; Exo `pyparser` and Allo builder sizes from the clones, cited); the three scenarios (wrong message in week 3; new construct for a lab; Vitis bump) as who/what language/how shipped. Kept-lines only as a footnote. Same schema and tags.

- [ ] **Step 2: Angle 10** — a `research` note in the required file shape (the wave check enforces it): `## Findings` holds the two sub-matrices (core language; surface embedding), each Option | Strength | Problem | Disposition, then a combination table cells × integration depth (table rows need no tags; any prose line does), plus the pre-registered reversal conditions re-evaluated line by line with the evidence that bears on each; `## Implications` gives the per-cell disposition; `## Evidence against` states what most undermines the recommendation; the Recommendation and Rejected alternatives paragraphs live in `D-26.md` itself. Cite the other angle notes by wikilink and the underlying sources by `repo@sha` (≥ 8 citations, as for every note).

- [ ] **Step 3: D-26 body**: Research findings (one paragraph per angle with wikilinks to the notes), the matrices, the recommendation, the spillover list. Keep `status: pre-registered` until Wave 3 completes, then set `status: awaiting-user-confirmation`.

## Task 12: Wave 3 — audits

- [ ] **Step 1: Citation audit** (fresh agent with no session context; Codex reviewer via the `iterative-review-workflow` skill, or `general-purpose`/`fable` as fallback). Prompt: the April method (`20 - Research Notes/30 - Adversarial Review.md`) applied to every D-26 note and mapping entry: every `repo@sha:path:L1-L2` resolves in the manifest, the file exists in the clone, `L2 ≤` file length, and the cited lines support the claim; every URL fetched; leak grep empty; five load-bearing behavioural claims per note re-derived. Output: `90 - Meta/2026-09-25-d26-citation-audit.md` with counts (checked / correct / incorrect) and a per-issue list. No silent corrections.

- [ ] **Step 2: Angle 13 — the case for P-E** (fresh agent, framing-blind; output `D-26-research/D-26-13-case-for-p-e.md`). Prompt: the full skeleton from Task 9 Step 1 **including the "Required file shape" block** (angle `13`, the wave check enforces the schema), with `{QUESTION}` = `Write the strongest honest case that P-E (Python core, Python-embedded student surface) should be chosen for an undergraduate FPGA lab course whose staff already drive their vendor tools with Python scripts, whose students know Python, and whose TAs would patch the compiler between offerings. Use the precedent clones and the other D-26 research notes at <paths> as evidence; you may disagree with their conclusions.` and `{DELIVERABLES}` = `Findings carries the argument and its evidence (tagged); Implications gives, per cell, why P-E beats it; Evidence against holds the best answers to the three strongest objections you find in the notes and states what would have to be true for P-E to be the wrong choice.`

- [ ] **Step 3: Answer the case** in `D-26.md` ("Rejected alternatives and answers") point by point, citing the notes; fix every incorrect citation the audit found (or mark the claim "(inferred, unverified)" and downgrade the note's Confidence); rerun `d26_wave_check.sh`.

## Task 13: Hand-off

- [ ] **Step 1:** `D-26.md` → `status: awaiting-user-confirmation`; progress-log entry with the audit counts; commit `D-26 meeting cut: findings, matrices, recommendation, audits`.
- [ ] **Step 2:** Give David the D-26 path, the recommendation in three sentences, the reversal-condition evaluation, and the spillover list. The deck is revised only after his decision.
- [ ] **Step 3 (after the decision, not before):** the 2026-06-26 overlay callout, the `index.md` "For reviewers" block, push per the publication-gate plan's Task 7.
