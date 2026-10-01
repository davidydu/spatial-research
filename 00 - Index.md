---
type: moc
project: spatial-spec
date_started: 2026-04-21
---

# Spatial Research — Top-Level Index

Source-grounded research and an implementation-level specification of the Spatial hardware DSL. Following professor feedback reported on 30 September 2026, the current direction is a pure Python rewrite: understand the Python programming model first, then investigate HLS lowering. The earlier Rust-core proposal and experiments remain historical evidence.

## Current direction

- [[00 - Python Rewrite Index|Python Spatial research]] — current entry point for examples, research, decisions, and validation.
- [[01 - Python Research Plan|Research plan]] — programming model, semantics, compiler design, then HLS research and implementation planning.
- [[D-27|Pure Python direction]] — accepted direction and its limits; [[D-28|detailed architecture proposed for review]].

## Earlier architecture review — superseded

- [[D-26-professor-brief|Earlier professor brief]] — the recommendation presented before the new direction.
- [[D-26-final-architecture|Earlier architecture plan]] — historical Rust-core proposal.
- [[2026-09-28-d26-research-extension|Follow-up method and debate]] — competing case, new evidence and limitations.
- [[D-26|Original D-26 record]] — frozen protocol and historical meeting cut.

## Start here (for any session)

1. [[workflow]] — **load this first.** Describes phases, per-session rhythm, verification discipline, stopping conditions.
2. [[00 - Python Rewrite Index]] and [[01 - Python Research Plan]] — current work. [[2026-04-21-spatial-spec-design]] records the original source-documentation plan.
3. [[conventions]] — frontmatter schemas, citation format, wikilink style.
4. [[progress-log]] — running log of what's been done, open questions count.

## Folder map

| Folder | Purpose |
|---|---|
| `10 - Spec/` | Source-grounded specification of original Spatial. Evidence for the Python rewrite; not automatically its language contract. |
| `20 - Research Notes/` | Raw artifacts. `00 - Coverage/` holds Phase 1 subagent outputs; `10 - Deep Dives/` holds per-topic reading notes; `20 - Open Questions.md` tracks unresolved issues. |
| `30 - HLS Mapping/` | Parallel notes categorizing each construct as clean-map / needs-rework / chisel-specific for the future HLS target. |
| `35 - Python Surface Mapping/` | Earlier construct mappings and Python embedding comparisons; reusable design evidence for the pure Python rewrite. |
| `40 - Cross References/` | Navigation matrices (source-tree map, pass pipeline order, node↔codegen matrix). |
| `50 - Python Rewrite/` | Current Python studies, examples, proposed contracts, HLS mappings, review evidence, and professor brief. Decisions remain in the shared D-number register. |
| `90 - Meta/` | Workflow docs, design doc, progress log, conventions. |

## Specification coverage history

- [x] **Phase 0** — Scaffold and design (2026-04-21)
- [x] **Phase 1** — Coverage pass, 10/10 verified (2026-04-21) — see `20 - Research Notes/00 - Coverage/`
- [x] **Phase 2** — Deep dives, spec population substantially complete (2026-04-25), 108 markdown files in `10 - Spec/` including 96 `type: spec` entries, see [[10 - Spec/00 - Spec Index|Spec Index]]
- [x] **Phase 3** — HLS mapping kicked off (2026-04-25), 96 entries classified across clean / rework / Chisel-specific indexes
- [ ] **Phase 4** — Consolidation (cross-refs, open-Q resolution)

## Source of truth

- Source versions and upstreams: [[reference-clones]].
- Algorithmic claims cite source files and line ranges. Historical coverage counts above describe the dated specification pass, not current compiler completion.
