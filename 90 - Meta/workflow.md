---
type: runbook
project: spatial-spec
date: 2026-04-21
status: active
load_priority: high
---

# Workflow — Spatial Research

**Load this file first at the start of every session.** The current work follows [[01 - Python Research Plan]]. [[2026-04-21-spatial-spec-design]] holds the original source-documentation rationale.

## Current route — 30 September 2026

Research a **pure Python Spatial compiler** before implementation, under [[D-27]]. Start with [[00 - Python Rewrite Index]], [[02 - Python Open Questions]], and [[PY-R001 - Programming Model Study]]. The order is programming model, semantic contract, compiler design, HLS research, then implementation planning. Review the relevant design before implementing it.

Use **Codex-only** agents for bounded parallel source checks, alternative designs, and review. Give writers separate files; the integrating agent verifies the source claims that determine a conclusion. Read local files and use command-line checks by default; use browser UI only when requested or needed to inspect a visual defect.

New Python work belongs under `50 - Python Rewrite/`. Decisions continue in `20 - Research Notes/50 - Decision Records/`; do not create another decision register. Preserve the original Spatial specification, earlier Rust work, and frozen experiments as evidence. Neither a research conclusion nor an adopted direction establishes implementation completion.

For each topic, write evidence and alternatives first, then the decision, then the specification and validation cases. Follow [[conventions]] and [[00 - Python Validation Plan]]. Commit coherent documentation batches to the research repository, then rebuild the website from those same files. Record publication status in [[progress-log]].

## Original source-documentation workflow

The coverage phases below describe how the original Spatial specification was built and how to maintain it. They are not the current Python implementation queue. Reuse their citation and verification discipline; the Python research plan governs new design work.

## Source of truth

- Spatial code: `/Users/david/Documents/David_code/spatial`
- Research root (this vault folder): `/Users/david/Documents/Spatial Research/`
- Every algorithmic claim in `10 - Spec/` cites a file + line range from the code tree.

## Phases

| Phase | What | Who | Output |
|---|---|---|---|
| **0** | Scaffold folder structure, design docs | main session (me) | `00 - Index.md`, `90 - Meta/*` |
| **1** | Coverage pass — structural mapping of all subsystems | Independent agents assigned bounded source areas | `20 - Research Notes/00 - Coverage/*` |
| **2** | Deep dives — read source, write notes, distill to spec | main session directly from source | `20 - Research Notes/10 - Deep Dives/*` → `10 - Spec/*` |
| **3** | Earlier HLS mapping — categorize original constructs for the then-proposed Rust/HLS target | main session | `30 - HLS Mapping/*`; `hls_status` frontmatter on spec entries |
| **4** | Consolidation — cross-ref matrices, open-Q resolution | main session | `40 - Cross References/*` populated; `20 - Open Questions.md` emptied or tagged OOS |

## Phase 1 — Coverage dispatch (one-shot, ~30 min wall)

### The ten subagents

| # | Subagent | Paths | ~files |
|---|---|---|---|
| 1 | Argon framework | `argon/src/argon/` | 95 |
| 2 | Forge + shared runtime | `forge/`, `utils/`, `emul/` | ~50 |
| 3 | Spatial language surface | `src/spatial/lang/` + top-level `dsl.scala`, `Spatial.scala`, `SpatialApp.scala`, `SpatialConfig.scala` | ~63 |
| 4 | Spatial IR (nodes + metadata) | `src/spatial/node/`, `src/spatial/metadata/`, `src/spatial/tags/` | ~80 |
| 5 | Compiler passes | `src/spatial/transform/`, `rewrites/`, `traversal/`, `flows/` | ~80 |
| 6 | Codegen A (FPGA + host) | `codegen/chiselgen/`, `cppgen/`, `dotgen/`, `naming/`, `resourcegen/`, `treegen/` | ~37 |
| 7 | Codegen B (sim + alt targets) | `codegen/scalagen/`, `pirgen/`, `roguegen/`, `tsthgen/` | ~76 |
| 8 | Fringe | `fringe/src/` | 149 |
| 9 | Hardware targets | `src/spatial/targets/` | 29 |
| 10 | Polyhedral + Models + DSE + support | `poly/`, `models/`, `src/spatial/{dse,lib,executor,model,math,issues,report,util}/` | ~80 |

> Note: subagent #10 bundles several heterogeneous paths. The planning step should decide whether one coverage note is the right granularity, or whether #10's output needs internal sub-structure (e.g., one section per path).

### Dispatch mechanics

- Dispatch independent source areas to Codex agents within available concurrency. The ten-area table is a coverage map, not a requirement to launch ten agents at once.
- Prompt to each subagent must include: (a) the exact paths to cover, (b) the coverage-note schema in full, (c) the instruction that every claim about code content cites a file + line range, (d) the output file path: `Spatial Research/20 - Research Notes/00 - Coverage/<subsystem-slug>-coverage.md`.

### Coverage-note schema (every note has this structure)

```yaml
---
type: coverage
subsystem: <name>
paths: [<list>]
file_count: N
date: <YYYY-MM-DD>
verified: []
---

## 1. Purpose
## 2. File inventory
## 3. Key types / traits / objects
## 4. Entry points
## 5. Dependencies
## 6. Key algorithms
## 7. Invariants / IR state read or written
## 8. Notable complexities or surprises
## 9. Open questions
## 10. Suggested spec sections
```

### Post-dispatch verification

For each returned coverage note:
- Pick **5 specific claims** at random (mix of file inventory entries, key-types claims, and algorithm-name claims).
- Open the cited files, verify the claim.
- If OK, record in the note's `verified:` frontmatter list with today's date.
- If wrong, log to `20 - Open Questions.md` as a Q-NNN entry.

**Mechanical re-dispatch threshold:** if **2 or more of the 5 spot-checks fail**, re-dispatch that subagent with a prompt that cites the failed claims and asks for correction. If 1 fails, fix it in the note manually and proceed. If 0 fail, the note is accepted.

## Phase 2 — Deep dives (the bulk of the work)

### Priority ordering

1. Argon framework
2. Spatial IR nodes + metadata
3. Pass pipeline (order first, then passes in dependency order)
4. Language surface
5. Semantics (synthesized after 1–4)
6. Code Generation — scalagen before chiselgen (emulation = language ground truth)
7. Cppgen, pirgen, other codegens
8. Polyhedral, Models, DSE, Fringe, Targets
9. Testing, Debugging, Build

### Per-session rhythm

Every session, repeat the loop:

1. **Orient** — open [[progress-log]], pick a topic from the priority queue or from `20 - Open Questions.md`.
2. **Read source directly** — use bounded Codex tasks for independent reading and alternative analyses. The integrating agent verifies decisive claims in the source and resolves disagreements before adopting a conclusion.
3. **Write a deep-dive note** at `20 - Research Notes/10 - Deep Dives/<topic-slug>.md`. Raw findings, direct quotes from source, file:line citations, unresolved questions.
4. **Distill to a spec entry** at `10 - Spec/…/<concept>.md`. Authoritative prose. Frontmatter points back to the deep-dive note and the source files. Status starts at `draft`.
5. **HLS-tag** — add a `hls_status` field (`clean` / `rework` / `chisel-specific` / `unknown`) for spec entries. In Rust rewrite planning notes, also distinguish `surface-clean`, `semantic-portable`, `backend-pending`, and `reference-only` when the older vocabulary is too coarse. If non-trivial, add an entry to the appropriate `30 - HLS Mapping/` file.
6. **Log** — append one line to `progress-log.md`: topic, spec file created, open Qs added/resolved.

### The "notes-first" rule

Always write the deep-dive note *before* the spec entry. The note is where you show your work — quotes, confusions, half-formed hypotheses. The spec entry is the distilled artifact. Skipping the note means you'll lose audit trail for anything you got wrong.

### Verification discipline

- **Every algorithmic claim cites `spatial/<path>:<lines>`** or carries an explicit `(inferred, unverified)` tag.
- **Never paraphrase code behavior without a citation.** If you can't find one, flag the claim and drop it.
- **Re-reads earn a `verified: <date>` tag.** A spec entry with a `verified:` date has been cross-checked after initial writing.
- **Subagent summaries are maps, not sources.** Never quote a subagent in a spec entry.

### Cross-reference maintenance

Maintain as-you-go, not at the end:
- `40 - Cross References/source-tree-map.md` — directory → concept mapping
- `40 - Cross References/pass-pipeline-order.md` — canonical execution order
- `40 - Cross References/node-to-codegen-matrix.md` — per-node, per-backend emission notes

## Frontmatter templates

> **YAML safety.** All list-valued fields use **block-style** YAML (one item per line with `- `) and **quoted string values**. Two hazards if you don't:
> - A bare colon inside a flow sequence (e.g. `[path:10-20]`) parses as a map entry rather than a scalar. Strict YAML parsers error; lenient ones misinterpret.
> - Unquoted `[[wikilink]]` inside a YAML list parses as a **nested list**, not the string `"[[wikilink]]"`. Obsidian does not auto-resolve wikilinks in that position.
>
> Always quote path-with-line citations and wikilinks when they appear in list values. Validate copied templates with a real YAML parser if in doubt.

**Coverage note:**
```yaml
---
type: coverage
subsystem: argon
paths:
  - "argon/src/argon/"
file_count: 95
date: 2026-04-21
verified: []
---
```

**Deep-dive note:**
```yaml
---
type: deep-dive
topic: unrolling-transformer
source_files:
  - "spatial/src/spatial/transform/UnrollingTransformer.scala"
session: <date>
status: draft
feeds_spec:
  - "[[40 - Unrolling]]"
---
```

**Spec entry:**
```yaml
---
type: spec
concept: unrolling
source_files:
  - "spatial/src/spatial/transform/UnrollingTransformer.scala:40-210"
source_notes:
  - "[[unrolling-transformer-deep-dive]]"
hls_status: rework
depends_on:
  - "[[10 - Counters and CounterChain]]"
status: draft
---
```

**HLS mapping note:**
```yaml
---
type: hls-mapping
construct: unrolling
spec_entry: "[[40 - Unrolling]]"
category: rework
---
```

For `hls-mapping`, `spec_entry` is a single wikilink (not a list), so it's a simple quoted scalar.

## Status vocabulary

- **Spec entries:** `draft` → `reviewed` → `stable`. `needs-rework` is a regression flag.
- **Deep-dive notes:** see [[conventions]] for draft, exploratory, conclusion, and superseded states. Research completion does not imply adoption.
- **HLS status:** `clean` (translates directly), `rework` (needs HLS-specific design), `chisel-specific` (tied to RTL; not portable), `unknown` (pending analysis).

## Stopping conditions (Phase 2 complete)

- Every top-level section in `10 - Spec/` has an index file.
- Every language construct in `lang/` has a spec entry.
- Every IR node in `node/` has a spec entry (or an explicit "trivial, no entry needed" note).
- Every pass in `transform/` + `rewrites/` + `traversal/` has a spec entry.
- Every target backend has at least an overview + one deep-dive file.
- `20 - Open Questions.md` is empty OR each remaining item has an explicit `out-of-scope-for-v1` tag.

## What NOT to do

- Don't write a spec entry without a deep-dive note first.
- Don't cite subagent output as a source in a spec entry.
- Don't populate `10 - Spec/` subfolders before reading the related source.
- Don't hand-wave "this is similar to X" — cite the files.
- Don't mix HLS-rewrite speculation into spec entries. HLS thoughts live in `30 - HLS Mapping/`.
- Don't silently delete open questions. Resolve them or tag them OOS.
- Don't skip the progress log. Future sessions rely on it.

## Kickoff checklist (at the start of any session)

1. Read `00 - Index.md` and this file.
2. Check `progress-log.md` for the most recent state.
3. Check [[02 - Python Open Questions]] for current choices; use the original open-question tracker for source-spec maintenance.
4. Pick a bounded topic from [[01 - Python Research Plan]].
5. Record its question, evidence needed, and deliverable; divide independent Codex tasks where useful.
6. Follow the notes-first loop in the current plan. Do not resume historical Rust implementation tasks without a current request.
