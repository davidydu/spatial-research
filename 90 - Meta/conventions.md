---
type: conventions
project: spatial-spec
date: 2026-04-21
---

# Conventions

Minimal style/format rules so the vault stays consistent across sessions.

## Frontmatter

Every file has a frontmatter block. `type` is required; other fields depend on `type`.

> **YAML safety.** For list-valued fields, use **block style** (one item per line with `- `) and **quote strings** that contain a colon or wikilink syntax.
>
> - A bare colon inside a flow sequence (`[path:10-20]`) parses as a map entry rather than a scalar.
> - Unquoted `[[wikilink]]` inside a YAML list parses as a **nested list**, not the wikilink string. Obsidian does not auto-resolve wikilinks in that position.
>
> Always quote path-with-line citations and wikilinks when they appear inside lists. See the templates at the bottom of this file for the canonical safe shapes.

### Required types

| type | Used for | Required extra fields |
|---|---|---|
| `moc` | Top-level / folder-level indexes ([[00 - Index]]) | — |
| `design` | One-off design docs ([[2026-04-21-spatial-spec-design]]) | `status` |
| `plan` | Research, validation, and execution plans | `status`, `scope`, `date` |
| `runbook` | Operational session-start docs ([[workflow]]) | `load_priority` |
| `conventions` | This file — style / frontmatter / citation rules | `date` |
| `log` | Append-only logs ([[progress-log]]) | — |
| `open-questions` | The unresolved-questions tracker | `date_started` |
| `hls-mapping-index` | Index file for `30 - HLS Mapping/` | `date_started` |
| `coverage` | Phase 1 subagent outputs | `subsystem`, `paths`, `file_count`, `date`, `verified` |
| `deep-dive` | Source readings and comparative studies | `topic`, `source_files`, `session`, `status`, `feeds_spec` |
| `spec` | Original Spatial entries under `10 - Spec/`; proposed or adopted Python contracts under `50 - Python Rewrite/40 - Specification/` | `concept`, `source_files`, `source_notes`, `hls_status`, `depends_on`, `status`; Python additions below |
| `hls-mapping` | Non-index entries under `30 - HLS Mapping/` (per-construct) | `construct`, `spec_entry`, `category` |
| `cross-ref` | Navigation matrix: directory → concept mapping, pass orders, node↔codegen matrices | — |
| `decision-record` | Decision records under `20 - Research Notes/50 - Decision Records/` | `decision-id`, `related-questions`, `status`, `date` |
| `decision-queue` | The decision queue | `date` |
| `research` | Per-angle research notes under `D-NN-research/` | `decision`, `angle`; **from D-26 onward also** `discriminates`, `sources`, `verified`, `status` |
| `research-note` | Free-standing research notes (legacy; prefer `research` or `deep-dive`) | `topic`, `date`, `status` |
| `decision` / `handoff` | Legacy one-off notes; do not create new ones | — |
| `reference` | Source manifests and common example definitions | `date` |
| `python-mapping-index` | Index of `35 - Python Surface Mapping/` | `date_started` |
| `python-mapping` | Per-construct entries under `35 - Python Surface Mapping/` | `construct`, `spec_entry`, `grammar_rule`, `per_style`, `obligations_at_risk`, `raters`, `verified`, `status` |

If a new type is needed, add it to this table before using it — the schema is the authoritative list.

`approved_by` is optional on design notes. Use it when a design decision has an
explicit human approval record; omit it for manager-owned active research notes,
implementation contracts, and prompts.

## Source code citations

Two forms:

1. **Inline identifiers** — backticks: `` `argon.Op` ``, `` `state.scheduler` ``.
2. **Algorithmic / behavioral claims** — must include a path + line range: `spatial/src/spatial/transform/UnrollingTransformer.scala:42-78`.

If a citation isn't available, tag the claim `(inferred, unverified)` in-prose. Untagged behavioral claims without citations are a style error.

After a re-read confirms a claim, add `verified: <YYYY-MM-DD>` to the entry's frontmatter (list of dates for multiple re-reads).

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

## Wikilinks

- Between vault files: `[[file stem]]` — stem *includes* the numeric prefix (e.g., `[[40 - Unrolling]]`).
- When the prefix is ugly inline, use aliases: `[[40 - Unrolling|unrolling]]`.
- Source code paths are **not** wikilinks — keep them plain text so they're greppable with normal tools.
- Never use relative paths in wikilinks; Obsidian resolves by stem globally within the vault.

## File and folder naming

- **Folders**: numeric prefix with gap-10 pattern (`00 - Foo`, `10 - Bar`, `20 - Baz`). Gaps let you insert new entries without renumbering.
- **Spec files inside folders**: same pattern.
- **Coverage notes and deep-dive notes**: descriptive kebab-case, no prefix (order-independent): `argon-coverage.md`, `unrolling-transformer.md`.
- **Stems are unique vault-wide.** Two files with the same stem (even in different folders) break wikilinks.

## Status vocabulary

**Spec entries (`status` field):**
- `draft` — written, not re-checked
- `reviewed` — re-read against source, all claims confirmed
- `stable` — reviewed + cross-referenced from multiple places without issue
- `needs-rework` — a downstream reader flagged a problem; fix pending

**Deep-dive notes (`status` field):**
- `draft` — in progress
- `exploratory` — initial design possibilities; no adoption implied
- `research-conclusion` — a bounded research conclusion, with evidence and limits; no API adoption or implementation implied
- `ready-to-distill` — note is complete, ready to feed a spec entry
- `superseded` — spec entry supersedes this note; kept for audit trail

**HLS status (`hls_status` field on spec entries):**
- `clean` — translates directly to HLS
- `rework` — needs HLS-specific design
- `chisel-specific` — tied to RTL semantics; not portable
- `unknown` — not yet analyzed

**Rust rewrite HLS planning labels (use in new planning notes when the coarse `hls_status` vocabulary is not precise enough):**
- `surface-clean` — the hardware idea maps cleanly to the Rust DSL surface
- `semantic-portable` — the Spatial behavior can be preserved in Rust IR
- `backend-pending` — HLS lowering still needs design or vendor evidence
- `reference-only` — useful for legacy understanding, not something to port directly

**Rust support evidence labels:**
- `accepted fixture adapter` — exact lab-shaped program accepted and host-C++ checked
- `supported feature` — reusable semantic lowering with non-lab tests and fail-closed negatives
- `host_cpp_structural_gate` — generated C++ compiled and ran with the local system compiler
- `vitis_csim_validated` — generated Vitis/Vivado project ran `csim_design`
- `vitis_csynth_validated` — generated Vitis/Vivado project ran `csynth_design`, with report metadata recorded
- `vitis_evidence_validated` — captured evidence directory passed the repo-local Vitis evidence validator
- `ec2_rust_1_75_compatible` — local manifests and lockfile remain readable by the EC2 Rust/Cargo 1.75 toolchain

**Python surface mapping labels (`python-mapping` entries):**
- `expressible`: `yes` / `awkward` (needs a construct outside the style's allowed-Python subset) / `no` (with the data-model citation)
- `info_preserved`: subset of `[spans, literal_types, size_vs_int, scope, order]` the style keeps
- `error_locus`: `python-time` / `ir-check` / `runtime` / `silent`
- `silently_divergent`: hazards where Python evaluates with its own semantics before the DSL sees the value

## Python rewrite documentation

[[00 - Python Rewrite Index]] is the current entry point. Use the existing document types rather than creating a parallel schema.

- Studies use `PY-R001`, example collections use `PY-E001`, and questions use `PY-Q001`. Include the study or collection ID in its filename. Keep identifiers and stems unique; never reuse them.
- Decisions continue the shared `D-NN` sequence, with `scope: python-rewrite`. Record who adopted the choice and what remains open. [[D-27]] records the direction; it does not approve a detailed architecture.
- A future Python specification must also include `scope: python-rewrite`, `decision_records` (quoted wikilinks in a block list), `adoption_status`, and `implementation_status`. Use `adoption_status: proposed` for a review contract and `adopted` only with explicit adoption evidence. The existing `status` describes document review, not adoption or implemented support. Begin `implementation_status` at `not-implemented`; use `partial` or `validated` only with linked, scoped execution evidence.
- Keep original Spatial behavior, earlier Rust design choices, proposed Python behavior, and measured results distinct. Cite pinned source revisions for source facts. An expected output calculated from a listing is not an observed result.
- Keep candidate code in its study and shared case definitions in the example corpus; link between them. Label illustrative APIs as unimplemented. Create specification and HLS topic folders with substantive content, not empty index placeholders.

## Progress log format

Append-only, newest-first within day blocks:

```markdown
## 2026-04-21 — Phase 0-1
- Design doc + workflow committed: [[2026-04-21-spatial-spec-design]]
- Phase 1 dispatched: 10 subagents
- Spot-checks: argon (3/3 OK), forge (2/3 OK — 1 correction filed as Q-003)
- Open Qs logged: Q-001 … Q-007

## 2026-04-22 — Deep dive
- Topic: Argon Symbol/Ref → [[10 - Symbol and Reference System]]
- Opened: Q-008, Q-009 (unclear effect propagation in nested blocks)
```

## Open questions format

```markdown
## Q-014 — [2026-04-22] Threading model of argon.State
Coverage says "implicit singleton per compilation" but scalagen references
a worker-per-thread pattern. Need to verify against State.scala directly.

Source: argon/src/argon/State.scala
Blocked by: —
Status: open | resolved-<date> | out-of-scope
Resolution: (empty until resolved)
```

IDs are zero-padded (Q-001, Q-014, Q-101) for stable sort. Never reuse an ID; resolved entries stay in the file with their resolution noted.

## Note templates

### Spec entry skeleton

```markdown
---
type: spec
concept: <concept>
source_files:
  - "spatial/src/.../<File>.scala:<line-range>"    # always quote; colons break flow syntax
source_notes:
  - "[[<deep-dive-note-stem>]]"                    # always quote wikilinks inside lists
hls_status: unknown
depends_on:
  - "[[<related-concept>]]"
status: draft
---

# <Concept>

## Summary

One paragraph. What this thing is in Spatial, why it exists, where it lives in the compilation pipeline.

## Syntax / API (if applicable)

## Semantics

What this does, precisely enough that a reimplementation could match the stated behavior.

## Implementation

How the current Spatial code realizes it. Algorithmic depth. Cite file:line for every claim.

## Interactions

What other parts of the compiler this touches — passes that read/write it, codegens that emit for it.

## HLS notes

Short. If detailed, defer to `30 - HLS Mapping/...`.

## Open questions

Link to `20 - Open Questions.md` entries, if any.
```

### Deep-dive skeleton

```markdown
---
type: deep-dive
topic: <slug>
source_files:
  - "spatial/src/.../<File>.scala"
session: <date>
status: draft
feeds_spec:
  - "[[<spec-entry-stem>]]"
---

# <Topic>

## Reading log
(Files read, in order. Notes as you go.)

## Observations
(Raw findings, quotes, file:line citations.)

## Open questions
(Filed into `20 - Open Questions.md` when the session ends.)

## Distillation plan
(What parts of this note feed which spec entries.)
```
