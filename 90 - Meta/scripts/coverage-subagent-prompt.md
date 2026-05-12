# Coverage subagent prompt (template)

Use this as the `prompt` argument to each of the 10 `Agent` calls in the Phase 1 dispatch. The main session substitutes the `{{…}}` placeholders per subagent before dispatch.

Placeholders:
- `{{SUBAGENT_NUM}}` — integer 1–10
- `{{SUBSYSTEM}}` — e.g. "Argon framework"
- `{{OUTPUT_SLUG}}` — e.g. "argon" (used in output path)
- `{{PATHS_BULLETS}}` — each assigned path as a markdown bullet
- `{{PATHS_FLAT}}` — YAML block-list fragment for the frontmatter `paths:` field

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

````markdown
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
````

## Ground rules

- **Every claim about code content must cite `spatial/<path>.scala:<lines>`.** No un-cited assertions about behavior.
- **Read, don't run.** Do not execute the build. Your job is to read source and summarize.
- **Frontmatter is YAML, with block-style lists and quoted strings.** Specifically: `paths:` must be a block list, one `- "path/"` per line. Never use flow style like `paths: [foo/]` because colons and brackets get ambiguous.
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
