---
type: runbook
project: spatial-spec
date: 2026-04-21
status: active
load_priority: high
---

# Workflow — Spatial Spec Project

**Load this file first at the start of every session.** It is the operational runbook; [[2026-04-21-spatial-spec-design]] holds the underlying rationale.

> **Execution harness.** This runbook assumes **Claude Code** as the agent harness. References to `Agent` (Task tool), `TaskCreate`, `subagent_type: Explore`, and `model: opus` are Claude-Code-specific primitives. On another harness (Codex CLI, Gemini CLI, etc.), map these to the harness's equivalents — or do not execute the runbook and use it as reference only.

## Source of truth

- Spatial code: `/Users/david/Documents/David_code/spatial`
- Research root (this vault folder): `Spring 2026/Spatial Research/`
- Every algorithmic claim in `10 - Spec/` cites a file + line range from the code tree.

## Phases

| Phase | What | Who | Output |
|---|---|---|---|
| **0** | Scaffold folder structure, design docs | main session (me) | `00 - Index.md`, `90 - Meta/*` |
| **1** | Coverage pass — structural mapping of all subsystems | 10 parallel Opus 4.7 Explore subagents | `20 - Research Notes/00 - Coverage/*` |
| **2** | Deep dives — read source, write notes, distill to spec | main session directly from source | `20 - Research Notes/10 - Deep Dives/*` → `10 - Spec/*` |
| **3** | HLS mapping — categorize each construct for the Rust/HLS target | main session | `30 - HLS Mapping/*`; `hls_status` frontmatter on spec entries |
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

- Single message with 10 `Agent` tool calls in parallel.
- `subagent_type: Explore`, `model: opus`, thoroughness "very thorough".
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
2. **Read source directly** — main session. Use subagents only for scoped lookups ("find all callers of X", "list every file that imports Y"). Do not delegate algorithmic understanding.
3. **Write a deep-dive note** at `20 - Research Notes/10 - Deep Dives/<topic-slug>.md`. Raw findings, direct quotes from source, file:line citations, unresolved questions.
4. **Distill to a spec entry** at `10 - Spec/…/<concept>.md`. Authoritative prose. Frontmatter points back to the deep-dive note and the source files. Status starts at `draft`.
5. **HLS-tag** — add a `hls_status` field (`clean` / `rework` / `chisel-specific` / `unknown`). If non-trivial, add an entry to the appropriate `30 - HLS Mapping/` file.
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
- **Deep-dive notes:** `draft` → `ready-to-distill` → `superseded`.
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
3. Check `20 - Open Questions.md` for unresolved items.
4. Pick a topic (priority queue or open Q).
5. Set `TaskCreate` entries for the session.
6. Begin the per-session rhythm loop.
