---
type: moc
project: spatial-spec
date_started: 2026-04-21
---

# Spatial Research — Top-Level Index

Source-grounded research and an implementation-level specification of the Spatial hardware DSL, targeting HLS. The current architecture recommendation is a restricted Python source frontend over one Rust semantic core, pending professor approval. The specification, historical experiments and research trail remain available below.

## Current architecture review

- [[D-26-professor-brief|Professor approval brief]] — concise research result and approval request.
- [[D-26-final-architecture|Selected architecture plan]] — one semantic authority, source contract and delivery gates.
- [[2026-09-28-d26-research-extension|Follow-up method and debate]] — competing case, new evidence and limitations.
- [[D-26|Original D-26 record]] — frozen protocol and historical meeting cut.

## Start here (for any session)

1. [[workflow]] — **load this first.** Describes phases, per-session rhythm, verification discipline, stopping conditions.
2. [[2026-04-21-spatial-spec-design]] — original brainstormed design doc (decisions + rationale).
3. [[conventions]] — frontmatter schemas, citation format, wikilink style.
4. [[progress-log]] — running log of what's been done, open questions count.

## Folder map

| Folder | Purpose |
|---|---|
| `10 - Spec/` | **The deliverable.** Authoritative, cross-linked spec. Populated progressively during Phase 2. |
| `20 - Research Notes/` | Raw artifacts. `00 - Coverage/` holds Phase 1 subagent outputs; `10 - Deep Dives/` holds per-topic reading notes; `20 - Open Questions.md` tracks unresolved issues. |
| `30 - HLS Mapping/` | Parallel notes categorizing each construct as clean-map / needs-rework / chisel-specific for the future HLS target. |
| `35 - Python Surface Mapping/` | Per-construct evidence for D-26 (Python embedding styles vs the external DSL); build spec if a Python surface is chosen. |
| `40 - Cross References/` | Navigation matrices (source-tree map, pass pipeline order, node↔codegen matrix). |
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
