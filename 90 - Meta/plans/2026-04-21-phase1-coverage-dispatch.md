# Phase 1 — Coverage Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce 10 verified coverage notes — one per Spatial subsystem — as a structural map of the `~/Documents/David_code/spatial` codebase, feeding Phase 2 deep dives.

**Architecture:** A single Claude Code session dispatches 10 `Agent` calls in parallel (each `subagent_type: Explore`, `model: opus`, thoroughness `"very thorough"`). Every subagent receives the same prompt skeleton with subsystem-specific substitutions. On return, the main session runs a structural validator over each note, performs 5-point random spot-checks against the cited source, and re-dispatches any subagent whose note fails. Output: verified, schema-compliant coverage notes in `20 - Research Notes/00 - Coverage/`.

**Tech Stack:**
- Claude Code harness (Agent tool, Write/Read/Edit, Bash, Grep, TaskCreate)
- Python 3 + PyYAML for frontmatter validation
- Obsidian-flavored markdown for outputs
- Source-of-truth: `/Users/david/Documents/David_code/spatial` (Scala, Argon-based)

**Context files (load before starting):**
- `Spatial Research/90 - Meta/workflow.md` — operational runbook (Phase 1 section)
- `Spatial Research/90 - Meta/conventions.md` — frontmatter + citation style
- `Spatial Research/90 - Meta/2026-04-21-spatial-spec-design.md` — full rationale

**Out of scope for this plan:**
- Writing any spec entry under `10 - Spec/` (that's Phase 2)
- Producing HLS mapping notes (Phase 3)
- Deep algorithmic analysis (Phase 2)
- Re-running Phase 0 scaffold tasks (already done)

---

## Task 1: Pre-flight checks

**Files:**
- None created or modified. Read-only verification.

- [ ] **Step 1: Verify the vault scaffold is in place**

Run: `ls -la ""`

Expected: subfolders `20 - Research Notes`, `30 - HLS Mapping`, `90 - Meta`, file `00 - Index.md`.

- [ ] **Step 2: Verify the `00 - Coverage/` output subfolder is ready**

Run: `ls "20 - Research Notes/"`

Expected: folder listing includes `00 - Coverage/` and `10 - Deep Dives/`. If either is absent, create with `mkdir -p`.

- [ ] **Step 3: Verify the Spatial source tree exists at the expected location**

Run: `ls -la /Users/david/Documents/David_code/spatial | head -10`

Expected: directories `argon`, `forge`, `src`, `fringe`, `emul`, `poly`, `models`, `utils`, `apps`, and file `build.sbt`. If the path differs, stop and ask the user.

- [ ] **Step 4: Confirm file counts match the plan's `~files` expectations**

Run the per-subagent file-count probe. Each row reports the combined `.scala` file count for one subagent's assigned paths, making the comparison against Task 4 one-to-one:

```bash
cd /Users/david/Documents/David_code/spatial && \
python3 - <<'EOF'
import subprocess, pathlib
BUNDLES = [
    (1,  "argon",            ["argon/src"],                                                              95),
    (2,  "forge-runtime",    ["forge/src", "utils/src", "emul/src"],                                     50),
    (3,  "spatial-lang",     ["src/spatial/lang"],                                                       63),
    (4,  "spatial-ir",       ["src/spatial/node", "src/spatial/metadata", "src/spatial/tags"],           80),
    (5,  "spatial-passes",   ["src/spatial/transform", "src/spatial/rewrites",
                              "src/spatial/traversal", "src/spatial/flows"],                             80),
    (6,  "codegen-fpga-host",["src/spatial/codegen/chiselgen", "src/spatial/codegen/cppgen",
                              "src/spatial/codegen/dotgen", "src/spatial/codegen/naming",
                              "src/spatial/codegen/resourcegen", "src/spatial/codegen/treegen"],         37),
    (7,  "codegen-sim-alt",  ["src/spatial/codegen/scalagen", "src/spatial/codegen/pirgen",
                              "src/spatial/codegen/roguegen", "src/spatial/codegen/tsthgen"],            76),
    (8,  "fringe",           ["fringe/src"],                                                            149),
    (9,  "hardware-targets", ["src/spatial/targets"],                                                    29),
    (10, "poly-models-dse",  ["poly/src", "models/src", "src/spatial/dse", "src/spatial/lib",
                              "src/spatial/executor", "src/spatial/model", "src/spatial/math",
                              "src/spatial/issues", "src/spatial/report", "src/spatial/util"],           80),
]
print(f"{'#':>2}  {'slug':<20} {'files':>6}  {'expected':>8}  {'delta%':>7}")
for n, slug, paths, expected in BUNDLES:
    total = sum(len(list(pathlib.Path(p).rglob("*.scala"))) for p in paths if pathlib.Path(p).exists())
    delta = 100 * (total - expected) / max(expected, 1)
    print(f"{n:>2}  {slug:<20} {total:>6}  {expected:>8}  {delta:>6.1f}%")
EOF
```

Expected: each `delta%` within ±15% of 0. A larger deviation means the tree has changed since the design doc was written and the subagent bundling may need rebalancing — if so, stop and consult the user.

- [ ] **Step 5: Log the pre-flight result**

Append to `90 - Meta/progress-log.md` under a new heading `## 2026-MM-DD — Phase 1 pre-flight`:
- Vault scaffold OK
- `00 - Coverage/` ready
- Spatial source at expected path
- File counts match (or note any deviations)

---

## Task 2: Write the coverage-note structural validator

**Files:**
- Create: `Spatial Research/90 - Meta/scripts/validate_coverage_note.py`
- Create: `Spatial Research/90 - Meta/scripts/fixtures/valid_stub.md` (test fixture)
- Create: `Spatial Research/90 - Meta/scripts/fixtures/missing_sections_stub.md` (test fixture)

The validator enforces the coverage-note schema mechanically so Task 6's verification has a stable acceptance check. Written first (TDD-style) so we know what "valid" means before subagents run.

- [ ] **Step 1: Write a known-good fixture that represents a valid note**

Create `90 - Meta/scripts/fixtures/valid_stub.md` with exactly this content:

```markdown
---
type: coverage
subsystem: stub-subsystem
paths:
  - "stub/path/"
file_count: 1
date: 2026-04-21
verified: []
---

## 1. Purpose
Stub purpose.

## 2. File inventory
Stub inventory.

## 3. Key types / traits / objects
Stub types.

## 4. Entry points
Stub entries.

## 5. Dependencies
Stub deps.

## 6. Key algorithms
Stub algs.

## 7. Invariants / IR state read or written
Stub invariants.

## 8. Notable complexities or surprises
Stub surprises.

## 9. Open questions
Stub questions.

## 10. Suggested spec sections
Stub spec sections.
```

- [ ] **Step 2: Write a known-bad fixture missing required sections**

Create `90 - Meta/scripts/fixtures/missing_sections_stub.md` — same frontmatter as the valid stub, but body contains only sections 1, 2, 3 (missing 4–10).

- [ ] **Step 3: Write the validator**

Create `90 - Meta/scripts/validate_coverage_note.py`:

```python
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
```

- [ ] **Step 4: Run the validator against the known-good fixture**

Run:
```bash
cd "90 - Meta/scripts" && \
python3 validate_coverage_note.py fixtures/valid_stub.md
```

Expected output: `[OK] fixtures/valid_stub.md`, exit code 0.

- [ ] **Step 5: Run the validator against the known-bad fixture**

Run:
```bash
cd "90 - Meta/scripts" && \
python3 validate_coverage_note.py fixtures/missing_sections_stub.md ; echo "exit=$?"
```

Expected output: `[FAIL]` with issues listing missing sections 4 through 10, followed by `exit=1`.

- [ ] **Step 6: Log validator ready**

Append one line to `progress-log.md`: "Validator ready at `90 - Meta/scripts/validate_coverage_note.py`; passes good-stub, fails bad-stub as expected."

---

## Task 3: Compose the shared subagent prompt template

**Files:**
- Create: `Spatial Research/90 - Meta/scripts/coverage-subagent-prompt.md`

The template is written once and referenced by all 10 dispatch calls in Task 4. Substitutions are `{{SUBAGENT_NUM}}`, `{{SUBSYSTEM}}`, `{{OUTPUT_SLUG}}`, `{{PATHS_BULLETS}}`, `{{PATHS_FLAT}}`.

- [ ] **Step 1: Write the prompt template**

Create `90 - Meta/scripts/coverage-subagent-prompt.md`:

````markdown
# Coverage subagent prompt (template)

Use this as the `prompt` argument to each of the 10 `Agent` calls in the Phase 1 dispatch. The main session substitutes the `{{…}}` placeholders per subagent before dispatch.

---

You are one of ten parallel Explore subagents mapping the Stanford Spatial codebase. Your assigned subsystem is **{{SUBSYSTEM}}** (subagent #{{SUBAGENT_NUM}} of 10).

Source tree: `/Users/david/Documents/David_code/spatial`

## Paths to cover (everything under these, recursively)

{{PATHS_BULLETS}}

## Output

Write a single markdown file at exactly this path:

```
20 - Research Notes/00 - Coverage/{{OUTPUT_SLUG}}-coverage.md
```

Use this exact structure. Frontmatter keys and section headings must match the schema letter-for-letter (a downstream validator checks them).

```markdown
---
type: coverage
subsystem: {{SUBSYSTEM}}
paths:
{{PATHS_FLAT}}
file_count: <actual count of .scala files under your paths>
date: <today's date, YYYY-MM-DD>
verified: []
---

## 1. Purpose
One paragraph. What this subsystem does. Where it sits in the Spatial compilation pipeline.

## 2. File inventory
Table: `path | one-line purpose`. Group near-duplicates (e.g. "transform/unrolling/*.scala — 12 per-controller unrollers").

## 3. Key types / traits / objects
The API surface. For each significant type: what it is, 2-3 key methods, which callers depend on it.

## 4. Entry points
Functions/objects/traits called from outside this subsystem. The integration seam.

## 5. Dependencies
Upstream (what this subsystem uses from elsewhere) and downstream (what elsewhere uses from this subsystem).

## 6. Key algorithms
Named only, with 1-2 line hints. Cite `spatial/<path>.scala:<lines>` for each. The deep-dive phase fills in algorithmic detail.

## 7. Invariants / IR state read or written
Metadata fields consumed or produced; invariants assumed or established; effect annotations relied on.

## 8. Notable complexities or surprises
Anything that warrants deeper attention in Phase 2 — tricky invariants, non-obvious coupling, code comments flagging TODOs.

## 9. Open questions
What's unclear from surface reading. These feed the Phase 2 priority queue.

## 10. Suggested spec sections
Map your findings onto the spec tree under `10 - Spec/`. Which files under that tree will your subsystem's content feed?
```

## Ground rules

- **Every claim about code content must cite `spatial/<path>.scala:<lines>`.** No un-cited assertions about behavior.
- **Read, don't run.** Do not execute the build. Your job is to read source and summarize.
- **Frontmatter is YAML, with block-style lists and quoted strings** — see [[conventions]] §"YAML safety". Specifically: `paths:` must be a block list, one `- "path/"` per line.
- **Group file inventory intelligently.** Subsystems with many near-duplicate files (per-target codegens, per-controller unrollers) should use grouped rows rather than 50 one-line entries.
- **Target length: 1500–3000 words.** Shorter is fine if the subsystem is small. Longer than 3000 means you're writing the deep-dive, not the coverage note.
- **Do not speculate about HLS.** HLS implications are out of scope for Phase 1.

## What you should NOT do

- Don't write spec entries under `10 - Spec/` — that's Phase 2.
- **Don't write, create, or edit any file outside your one coverage-note output path.** Ten subagents run in parallel; any shared-file edits will race or clobber.
- Don't modify `progress-log.md`, `00 - Index.md`, or any file under `90 - Meta/`, `30 - HLS Mapping/`, or `40 - Cross References/`.
- Don't delegate to further subagents.
- Don't cite any file you didn't directly read. If you cite `File.scala:42-78`, you actually opened that range.

## Return value

Report back (in chat) a short summary: subsystem name, file count, path to the written coverage note, and any paths you could not cover (if any). The main session will validate the note structurally and spot-check 5 claims before accepting it.
````

- [ ] **Step 2: Log template ready**

Append one line to `progress-log.md`: "Subagent prompt template at `90 - Meta/scripts/coverage-subagent-prompt.md`."

---

## Task 4: Dispatch all 10 subagents in parallel

**Files:**
- No files created in this task. Each subagent writes its own coverage note.

The main session sends a single message with 10 `Agent` tool calls. The table below lists the 10 substitution bundles — use them to fill the template from Task 3.

### Substitution table

| # | SUBSYSTEM | OUTPUT_SLUG | Paths |
|---|---|---|---|
| 1 | Argon framework | `argon` | `argon/src/argon/` |
| 2 | Forge + shared runtime | `forge-runtime` | `forge/src/forge/`, `utils/src/`, `emul/src/` |
| 3 | Spatial language surface | `spatial-lang` | `src/spatial/lang/`, plus top-level files: `src/spatial/dsl.scala`, `src/spatial/Spatial.scala`, `src/spatial/SpatialApp.scala`, `src/spatial/SpatialConfig.scala` |
| 4 | Spatial IR (nodes + metadata) | `spatial-ir` | `src/spatial/node/`, `src/spatial/metadata/`, `src/spatial/tags/` |
| 5 | Compiler passes | `spatial-passes` | `src/spatial/transform/`, `src/spatial/rewrites/`, `src/spatial/traversal/`, `src/spatial/flows/` |
| 6 | Codegen A: FPGA + host | `codegen-fpga-host` | `src/spatial/codegen/chiselgen/`, `cppgen/`, `dotgen/`, `naming/`, `resourcegen/`, `treegen/` |
| 7 | Codegen B: sim + alt targets | `codegen-sim-alt` | `src/spatial/codegen/scalagen/`, `pirgen/`, `roguegen/`, `tsthgen/` |
| 8 | Fringe | `fringe` | `fringe/src/` |
| 9 | Hardware targets | `hardware-targets` | `src/spatial/targets/` |
| 10 | Polyhedral + Models + DSE + support | `poly-models-dse` | `poly/src/`, `models/src/`, `src/spatial/dse/`, `src/spatial/lib/`, `src/spatial/executor/`, `src/spatial/model/`, `src/spatial/math/`, `src/spatial/issues/`, `src/spatial/report/`, `src/spatial/util/` |

### Substitution rules

- `SUBAGENT_NUM`: the `#` column.
- `SUBSYSTEM`: the `SUBSYSTEM` column verbatim.
- `OUTPUT_SLUG`: the `OUTPUT_SLUG` column (used in the output file path).
- `PATHS_BULLETS`: each path as a markdown bullet, one per line — e.g.:
  ```
  - `src/spatial/codegen/chiselgen/`
  - `src/spatial/codegen/cppgen/`
  ```
- `PATHS_FLAT`: YAML block-list fragment, one `- "path/"` per line, indented two spaces (because it's nested under the `paths:` key):
  ```
    - "src/spatial/codegen/chiselgen/"
    - "src/spatial/codegen/cppgen/"
  ```

### Steps

- [ ] **Step 1: Define acceptance criteria for this task**

Acceptance for the dispatch itself (not the outputs):
- A single assistant message contains exactly 10 `Agent` tool calls.
- Each call has `subagent_type: "Explore"`, `model: "opus"`, a short `description`, and a `prompt` derived from Task 3's template.
- No two calls share an `OUTPUT_SLUG`.
- All 10 calls return (possibly with failures) before proceeding to Task 5.

- [ ] **Step 2: Assemble the 10 Agent call arguments in memory**

For each row of the substitution table, prepare an `Agent` call with:
- `subagent_type`: `"Explore"`
- `model`: `"opus"`
- `description`: `"Phase 1 coverage: " + SUBSYSTEM` (keep short)
- `prompt`: the template from Task 3 with placeholders substituted per rules above

Do this assembly silently; do not emit the prompts as chat text before dispatch (it would be pure noise).

- [ ] **Step 3: Dispatch all 10 in parallel**

Emit a single assistant message containing all 10 `Agent` tool calls. Do not include any other tool calls in this message (they would run before dispatch returns and waste context).

**Pre-dispatch invariant:** If while assembling the 10 calls in Step 2 you discover any malformed prompt, missing substitution, or invalid path, abort the whole batch and re-form. Do not dispatch 9 calls and patch the 10th afterward — single-shot parallelism is part of the plan's performance story and a partial dispatch invalidates the wall-clock estimate.

- [ ] **Step 4: Wait for all 10 to return**

Each subagent returns a chat-message summary. Record each `(subagent #, reported note path, file count)` in a small inline table in chat so the user can see progress.

- [ ] **Step 5: Log dispatch complete**

Append to `progress-log.md` under a new heading `## 2026-MM-DD — Phase 1 dispatch`:
- All 10 subagents dispatched and returned
- Coverage notes written at: (list paths)
- Any subagent that reported partial coverage (list with reason)

---

## Task 5: Structural validation of each returned note

**Files:**
- Modify: `20 - Research Notes/00 - Coverage/*-coverage.md` (add `verified:` entries on success)

For each of the 10 returned notes, run the Task 2 validator. This is a fast first-pass filter before content spot-checks.

- [ ] **Step 1: List the returned notes**

Run:
```bash
ls "20 - Research Notes/00 - Coverage/"
```

Expected: 10 files matching the `OUTPUT_SLUG` column, plus no extras.

- [ ] **Step 2: Run the validator over all 10**

Run:
```bash
cd "$HOME/Documents/Spatial Research" && \
for f in "20 - Research Notes/00 - Coverage/"*-coverage.md; do
  python3 "90 - Meta/scripts/validate_coverage_note.py" "$f"
done
```

Expected: 10 × `[OK] …`. If any `[FAIL]` appears, record the failing file and issue list.

- [ ] **Step 3: For any validator failure, re-dispatch that subagent**

Craft a follow-up prompt for the affected subagent pointing to the exact issues, and re-dispatch with an `Agent` call. When the corrected note returns, re-run the validator on only that file, **then continue to Task 6 (content spot-checks) for that note** — structural validation alone isn't acceptance.

Do **not** hand-edit a coverage note to make the validator pass — the structural gaps usually signal missing content the subagent should re-produce.

- [ ] **Step 4: Log validator results**

Append to `progress-log.md`: "Structural validator: 10/10 OK" (or list the failures and re-dispatches).

---

## Task 6: Content spot-checks per note

**Files:**
- Modify: each coverage note (add date to `verified:` list on success)
- Modify: `20 - Research Notes/20 - Open Questions.md` (file new Q-NNN entries for issues)

Acceptance check per [[workflow]] §"Post-dispatch verification": pick 5 specific claims at random per note, verify each against source, apply the mechanical re-dispatch threshold.

Repeat this section **once per coverage note (10 iterations)**. Below is the per-note loop.

- [ ] **Step 1: Read the coverage note**

Use the Read tool on the note. Identify 5 claims to spot-check using **stratified sampling** (this is intentionally biased toward falsifiable, file:line-cited claims — "random" as stated in workflow.md is approximate):
- §2 File inventory — 1 or 2 path→purpose claims
- §3 Key types — 1 claim about a type's methods or responsibilities
- §6 Key algorithms — 1 or 2 claims about where named algorithms live

Prefer claims with file:line citations — those are falsifiable. If fewer than 5 such claims exist, file a Q-NNN entry about thin citation and pick the strongest available 5.

- [ ] **Step 2: Verify each claim against source**

For each claim: open the cited file+line range (Read tool) and read the surrounding code. Mark the claim ✓ (supported), ✗ (contradicted), or ? (undecidable from surface reading).

- [ ] **Step 3: Apply the re-dispatch threshold**

- **0 ✗:** accept the note. Proceed to Step 4.
- **1 ✗:** fix the single claim in the note manually (Edit tool), file a Q-NNN entry noting the original error, accept.
- **2+ ✗:** re-dispatch that subagent with a prompt citing every failed claim and asking for a corrected note. Go back to Task 5 Step 1 for the re-issued note.

- [ ] **Step 4: Record verification in the note's frontmatter**

Edit the note's frontmatter to append today's date to the `verified:` list:

```yaml
verified:
  - 2026-MM-DD
```

(Always block-style; never `verified: [2026-MM-DD]` — Obsidian-safe.)

- [ ] **Step 5: File any open questions for this note**

Add entries to `20 - Research Notes/20 - Open Questions.md` for anything flagged `?` (undecidable) or surprising. Use the format from [[conventions]] §"Open questions format". IDs zero-padded, stable.

- [ ] **Step 6: Log progress for this note**

Append one line to `progress-log.md`: "Spot-check `<subsystem>`: 5/5 supported" (or `"4/5 supported, 1 fix; Q-NNN filed"`, or `"2+ failures → re-dispatched"`).

---

## Task 7: Phase 1 wrap-up

**Files:**
- Modify: `Spatial Research/00 - Index.md` (flip Phase 1 checkbox)
- Modify: `Spatial Research/90 - Meta/progress-log.md` (final Phase 1 entry)
- Create (optional): `Spatial Research/40 - Cross References/source-tree-map.md` (first draft)

- [ ] **Step 1: Verify all 10 notes accepted**

Run:
```bash
cd "$HOME/Documents/Spatial Research" && \
ls "20 - Research Notes/00 - Coverage/"*-coverage.md | wc -l
```

Expected: `10`.

Also confirm every note has a non-empty `verified:` list by running:
```bash
cd "$HOME/Documents/Spatial Research" && \
python3 - <<'EOF'
import re, yaml
from pathlib import Path
base = Path("20 - Research Notes/00 - Coverage")
for f in sorted(base.glob("*-coverage.md")):
    text = f.read_text()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    fm = yaml.safe_load(m.group(1)) if m else {}
    verified = fm.get("verified") or []
    print(f"{'OK ' if verified else 'MISSING'} {f.name:<45} verified={verified}")
EOF
```

Expected: every line starts `OK` and shows a non-empty `verified` list.

- [ ] **Step 2: Aggregate open questions**

Run:
```bash
grep -c "^## Q-" "20 - Research Notes/20 - Open Questions.md"
```

Record the count. This is the number of open items heading into Phase 2.

- [ ] **Step 3: Draft the source-tree map**

Using the 10 coverage notes' §5 (Dependencies) and §10 (Suggested spec sections), draft `40 - Cross References/source-tree-map.md` with a table mapping each top-level source directory to the spec subtree it feeds. Frontmatter type: `moc`.

This is a rough first pass — it'll be refined during Phase 2. Goal here: produce a navigable index now.

- [ ] **Step 4: Flip Phase 1 in the index**

Edit `00 - Index.md` — change:
```
- [ ] **Phase 1** — Coverage pass (10 parallel Opus subagents)
```
to:
```
- [x] **Phase 1** — Coverage pass (10 parallel Opus subagents)
```

- [ ] **Step 5: Phase-complete entry in the progress log**

Append to `progress-log.md`:

```markdown
## 2026-MM-DD — Phase 1 complete

- 10 coverage notes written and verified at `20 - Research Notes/00 - Coverage/`
- N open questions logged (see `20 - Open Questions.md`)
- Source-tree map drafted at `40 - Cross References/source-tree-map.md`
- Next: Phase 2 deep-dive priority is Argon framework per [[workflow]] §"Priority ordering"
```

- [ ] **Step 6: Surface priority-queue recommendation to the user**

Report to the user in chat:
- Phase 1 complete (10/10 notes verified)
- Count of open questions
- Recommended Phase 2 starting topic (Argon framework per workflow.md priority order)
- Anything surprising from the coverage notes that the user should know before Phase 2 begins (e.g., subsystem #10's bundle was too heterogeneous and should split; or a subsystem had to be re-dispatched)

---

## Stopping conditions

Phase 1 is complete when **all** of the following hold:
- `20 - Research Notes/00 - Coverage/` contains exactly 10 `*-coverage.md` files, one per `OUTPUT_SLUG` in Task 4.
- Each note passes the validator (Task 5).
- Each note has a non-empty `verified:` list in its frontmatter (Task 6).
- `00 - Index.md` shows Phase 1 checked off.
- `progress-log.md` has a "Phase 1 complete" entry.

If any of these are false, Phase 1 is not done — return to the appropriate task.
