---
type: design
project: spatial-spec
date: 2026-04-21
status: approved
approved_by: user
supersedes: []
---

# Design — Spatial Language Specification Research Project

## 1. Purpose

Produce a comprehensive, implementation-level specification of the Spatial language as it exists in the Stanford `spatial` codebase (`~/Documents/David_code/spatial`, Scala, Argon-based). The long-term motivation is a Rust rewrite that compiles to HLS (High-Level Synthesis) instead of Chisel RTL. This spec is the blueprint such a rewrite would be checked against.

The spec must be:

- **Layered** — organized from the language surface (what users write) down through IR, passes, and codegen.
- **Algorithmic in depth** — describes the *logic* of each pass, not just its interface.
- **Multi-backend aware** — covers chiselgen, scalagen, cppgen, pirgen.
- **Full-stack** — includes adjacent layers (Argon, Forge, polyhedral, models, DSE, fringe) that any rewrite must reconstruct.

## 2. Decisions (aligned with user)

| Question | Decision |
|---|---|
| Overall shape | **Layered implementation spec.** Not a language reference; not a compiler-internals-only doc; not two separate docs. |
| Depth | **Algorithmic.** For each pass: inputs, outputs, invariants, and prose description of the algorithm. |
| Targets covered | All four: **chiselgen, scalagen, cppgen, pirgen.** |
| Adjacent layers | All four: **Argon + Forge, Polyhedral model, Models + DSE, Fringe.** |
| On-disk organization | **Many small files, Obsidian-native.** Wikilinks, numeric-prefix folder sort. |
| Sequencing | **Coverage pass first, then deep-dive.** Phase 1 is rapid structural mapping; Phase 2 is algorithmic detail. |
| Notes vs spec | **Parallel trees.** Research Notes/ is raw and dated; Spec/ is distilled and authoritative, with citations back to notes. |
| Execution model | **Approach B** — 10 parallel Opus 4.7 Explore subagents for Phase 1 coverage; main session drives Phase 2 deep dives directly from source to preserve algorithmic fidelity. |
| HLS awareness | Spec describes Spatial *as it is* (not pre-shaped for HLS). Parallel `30 - HLS Mapping/` folder tags each construct as clean / rework / chisel-specific. |
| Design doc location | Inside the Obsidian vault at `Spatial Research/90 - Meta/2026-04-21-spatial-spec-design.md`. |

## 3. Folder structure

```
Spatial Research/
├── 00 - Index.md
│
├── 10 - Spec/
│   ├── 00 - Overview and Philosophy.md
│   ├── 10 - Language Surface/
│   │   ├── 10 - Types/
│   │   ├── 20 - Controllers/
│   │   ├── 30 - Memories/
│   │   ├── 40 - Primitives/
│   │   ├── 50 - Host and IO/
│   │   ├── 60 - Counters and Iteration/
│   │   ├── 70 - Parallelization Annotations/
│   │   └── 80 - Application Structure/
│   ├── 20 - Semantics/
│   ├── 30 - IR/
│   │   ├── 00 - Argon Framework/
│   │   ├── 10 - Spatial Nodes/
│   │   └── 20 - Metadata/
│   ├── 40 - Compiler Passes/
│   │   ├── 00 - Pass Pipeline.md
│   │   ├── 10 - Analyses/
│   │   ├── 20 - Transformations/
│   │   └── 30 - Rewrites.md
│   ├── 50 - Code Generation/
│   │   ├── 00 - Codegen Framework.md
│   │   ├── 10 - Chiselgen/
│   │   ├── 20 - Scalagen/
│   │   ├── 30 - Cppgen/
│   │   ├── 40 - Pirgen/
│   │   └── 50 - Other Codegens.md
│   ├── 60 - Polyhedral Model/
│   ├── 70 - Models and DSE/
│   ├── 80 - Runtime and Fringe/
│   ├── 85 - Debugging, Reporting, and Diagnostics/
│   ├── 90 - Testing and Regression/
│   └── 95 - Build and Invocation/
│
├── 20 - Research Notes/
│   ├── 00 - Coverage/              # Phase 1 subagent outputs
│   ├── 10 - Deep Dives/            # Phase 2 per-topic reading notes
│   └── 20 - Open Questions.md
│
├── 30 - HLS Mapping/
│   ├── 00 - Overview.md
│   ├── 10 - Clean Mappings.md
│   ├── 20 - Needs Rework.md
│   └── 30 - Chisel-Specific.md
│
├── 40 - Cross References/
│   ├── source-tree-map.md
│   ├── pass-pipeline-order.md
│   └── node-to-codegen-matrix.md
│
└── 90 - Meta/
    ├── 2026-04-21-spatial-spec-design.md   # this file
    ├── workflow.md                          # standalone runbook
    ├── conventions.md                       # frontmatter + citation style
    └── progress-log.md
```

Principles:
- `10 - Spec/` and `20 - Research Notes/` are **parallel trees**. Notes are raw/audit-trail; spec is distilled.
- Folders only where depth justifies them (Semantics is a folder; Rewrites is a single file).
- Subtree-per-codegen under `50 - Code Generation/`.
- Progressive population: only `00 - Index.md`, `90 - Meta/`, `20 - Research Notes/`, `30 - HLS Mapping/00 - Overview.md` created up front.

## 4. Phase 1 — Coverage plan

Ten parallel Opus 4.7 Explore subagents, dispatched in a single batch. Each scans an assigned subtree and writes a coverage note into `20 - Research Notes/00 - Coverage/`.

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

### Coverage-note schema (uniform across all 10)

```yaml
---
type: coverage
subsystem: <name>
paths: [<list of covered directories>]
file_count: N
date: 2026-04-21
verified: []
---

## 1. Purpose
One paragraph — what this subsystem does, where it sits in the compilation pipeline.

## 2. File inventory
Table: path | one-line purpose. Group near-duplicates.

## 3. Key types / traits / objects
The API surface. For each: purpose, key methods, who depends on it.

## 4. Entry points
Functions/objects called from outside this subsystem. The integration seam.

## 5. Dependencies
Upstream (what this uses) and downstream (what uses this).

## 6. Key algorithms
Named only, with 1-2 line hints. Deep dive fills in detail.

## 7. Invariants / IR state read or written
Metadata fields consumed/produced; invariants assumed or established.

## 8. Notable complexities or surprises
Things that warrant deeper attention.

## 9. Open questions
What's unclear from surface reading. Feeds Phase 2 priorities.

## 10. Suggested spec sections
Which files under `10 - Spec/` this content will feed into.
```

### Dispatch and verification

- Single message with 10 `Agent` tool calls, parallel. `subagent_type: Explore`, `model: opus`, thoroughness "very thorough".
- Each subagent prompt fixes: paths to cover, the schema above, the instruction that every claim about code content must cite a file + line range.
- After return, spot-check 3–5 claims per note against raw source. Log any mismatches to `20 - Open Questions.md`. Re-dispatch if error rate is high.

## 5. Spec Table of Contents (initial shape)

The structure of `10 - Spec/` is laid out in §3 above. The key decisions within the TOC:

- **Section 10 (Language Surface)** is heavily subdivided — one file per construct (per controller, per memory type, etc.). The user explicitly approved "as many folders as needed for clarity."
- **Section 20 (Semantics)** is its own folder (not folded into Overview). Subfiles: scheduling model, memory model, type system, effects, error semantics.
- **Section 30 (IR)** — Argon framework as its own subfolder; Spatial nodes categorized rather than file-per-node; Metadata promoted to a folder (45 metadata files justify breakdown).
- **Section 40 (Compiler Passes)** — densest section. One file per pass. Analyses separated from Transformations. Rewrites kept as a single file (only 5 files in source).
- **Section 50 (Code Generation)** — subfolder per backend; each grows to 3–7 files depending on complexity.
- **Sections 85, 90, 95** — debugging/reporting, testing/regression, build/invocation. Added at user's request to cover tooling layers.

## 6. Workflow (phases)

```
Phase 0 — Scaffold (this doc, Index, workflow, conventions)
Phase 1 — Coverage (10 parallel Opus subagents, spot-check, file open Qs)
Phase 2 — Deep dives (main session, source → note → spec, HLS-tag as you go)
Phase 3 — HLS mapping (populate 30 - HLS Mapping/, tag spec entries)
Phase 4 — Consolidation (cross-ref matrices, resolve open Qs, final pass)
```

### Phase 2 priority ordering

1. Argon framework
2. Spatial IR nodes + metadata
3. Pass pipeline (order first, then passes in dependency order)
4. Language surface
5. Semantics
6. Code Generation (scalagen first, then chiselgen — scalagen is emulation ground truth)
7. Cppgen, pirgen, other codegens
8. Polyhedral, Models, DSE, Fringe, Targets
9. Testing, Debugging, Build

Rationale: bottom-up for infrastructure, then language layer, then backends. Scalagen before chiselgen because emulation semantics anchor the language.

### Per-session rhythm (Phase 2 onward)

1. Pick topic from priority queue or `20 - Open Questions.md`.
2. Read source directly (main session). Use targeted subagents only for scoped lookups.
3. Write to `20 - Research Notes/10 - Deep Dives/<topic>.md` first — raw findings, quotes, file:line citations, questions.
4. Distill to `10 - Spec/…/<concept>.md` — authoritative prose, cross-linked, cites the deep-dive note.
5. Update `30 - HLS Mapping/` if there's a clear HLS implication.
6. Append to progress log.

### Verification discipline

- Every algorithmic claim in a spec entry cites `spatial/<path>:<lines>` or carries an explicit `(inferred, unverified)` tag.
- Claims verified on re-read get a `verified: <date>` frontmatter tag.
- Subagent summaries are treated as maps, not sources; spec claims are always backed by direct source reads.

### Stopping conditions

The spec is done-enough when:
- Every top-level section in `10 - Spec/` has an index file.
- Every language construct in `lang/` has a spec entry.
- Every IR node in `node/` has a spec entry (or an explicit "trivial, no entry needed" note).
- Every pass in `transform/` + `rewrites/` + `traversal/` has a spec entry.
- Every target backend has at least an overview + one deep-dive file.
- `20 - Open Questions.md` is empty OR each remaining entry has an "out-of-scope-for-v1" tag.

## 7. Conventions (summary)

Full details in [[conventions]]. Key points:

- **Frontmatter** required on every file (types: `coverage`, `deep-dive`, `spec`, `hls-mapping`, plus `moc` for indexes and `design` for this doc).
- **Source citations**: `spatial/src/<path>.scala:<lines>` — always for algorithmic claims.
- **Wikilinks**: `[[file stem]]` or `[[file stem|display alias]]`. Source paths are not wikilinks.
- **Folders**: numeric prefix with gap-10 (`00 -`, `10 -`, `20 -`).
- **Status vocabulary**: `draft`, `reviewed`, `stable`, `needs-rework` (for spec entries); `draft`, `ready-to-distill`, `superseded` (for deep-dive notes).
- **HLS status**: `clean`, `rework`, `chisel-specific`, `unknown`.

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Subagent summaries lose algorithmic detail | Use Opus 4.7 (not Haiku); spot-check each coverage note; deep-dive always reads source directly. |
| Main session context pressure on a 700-file codebase | Notes-first pattern keeps heavy-read sessions focused on one subsystem; spec entries distill; raw reads live in deep-dive notes, not in working context. |
| Scope creep into unrelated Stanford lineage (Delite, OptiML) | Explicit out-of-scope. Mention only in glossary. |
| Spec goes stale vs. upstream spatial repo | Project is reverse-engineering a frozen snapshot (April 2026). Future upstream changes out-of-scope. |
| HLS assumptions leak into "pure" spec | HLS implications live in `30 - HLS Mapping/`, not in spec entries. Spec describes Spatial as-is. |
| Algorithm-level claims wrong after refactor | Every claim cites file:line. Rewrites re-verify. `verified:` tag marks post-rewrite confirmations. |

## 9. What's deliberately excluded from v1

- **Apps walkthroughs** — `apps/` is not spec material.
- **Tutorials** — this is a spec, not a user guide.
- **Historical / lineage discussion** beyond glossary.
- **Upstream change tracking** — project is reverse-engineering a snapshot.
- **HLS-flow implementation** — spec informs a future rewrite; the rewrite is not in scope here.

## 10. Next step

Phase 1 coverage dispatch. See [[workflow]] for the operational runbook.
