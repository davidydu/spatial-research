---
type: moc
project: spatial-spec
date_started: 2026-04-21
---

# Spatial Research — Top-Level Index

Research effort to produce a comprehensive, implementation-level specification of the Spatial hardware DSL (`~/Documents/David_code/spatial`). The long-term goal is to support a Rust rewrite that targets HLS instead of Chisel; this spec is the blueprint.

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
| `40 - Cross References/` | Navigation matrices (source-tree map, pass pipeline order, node↔codegen matrix). |
| `90 - Meta/` | Workflow docs, design doc, progress log, conventions. |

## Phase status

- [x] **Phase 0** — Scaffold and design (2026-04-21)
- [x] **Phase 1** — Coverage pass, 10/10 verified (2026-04-21) — see `20 - Research Notes/00 - Coverage/`
- [x] **Phase 2** — Deep dives, spec population substantially complete (2026-04-25), 108 markdown files in `10 - Spec/` including 96 `type: spec` entries, see [[Spec Index]]
- [x] **Phase 3** — HLS mapping kicked off (2026-04-25), 96 entries classified across clean / rework / Chisel-specific indexes
- [ ] **Phase 4** — Consolidation (cross-refs, open-Q resolution)

## Source of truth

- Code: `/Users/david/Documents/David_code/spatial`
- Every algorithmic claim in the spec cites a file + line range from this tree
