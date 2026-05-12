---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Spec — Top-Level Index

Authoritative, cross-linked specification of the Spatial hardware DSL. Every algorithmic claim cites a file + line range from the code tree at `/Users/david/Documents/David_code/spatial`. Populated during Phase 2 of the research workflow ([[workflow]]).

## Structure

| Section | Scope |
|---|---|
| `10 - Language Surface/` | User-facing DSL: controllers, memories, primitives, IO, host, counters. Spec for what an application writer types. |
| `20 - Semantics/` | Cross-cutting formal semantics: effects, scheduling, binding, bit-exactness, timing. Synthesized from the other sections. |
| `30 - IR/` | `00 - Argon Framework/` (staged-IR substrate), `10 - Spatial Nodes/` (per-node entries), `20 - Metadata/` (metadata categories). |
| `40 - Compiler Passes/` | Pipeline order; per-pass entry (transformer or analysis); invariants established/consumed. |
| `50 - Code Generation/` | Per-backend: `10 - Chiselgen/`, `20 - Scalagen/` (reference semantics), `30 - Cppgen/`, `40 - Pirgen/`, `50 - Other Codegens.md`. |
| `60 - Polyhedral Model/` | `poly/` (ISL binding) + access-pattern math. |
| `70 - Models and DSE/` | Area/latency models, `targets/` descriptions, DSE engine. |
| `80 - Runtime and Fringe/` | `fringe/` runtime + host drivers. |
| `95 - Compiler Infrastructure/` | Shared compiler utilities, Scala executor infrastructure, reports, and deferred issue diagnostics. |

## Status vocabulary (per spec entry)

- `draft` — written, not re-checked
- `reviewed` — re-read against source, all claims confirmed
- `stable` — reviewed + cross-referenced from multiple places without issue
- `needs-rework` — a downstream reader flagged a problem; fix pending

HLS status: `clean` (translates directly) / `rework` (needs HLS-specific design) / `chisel-specific` (tied to RTL; not portable) / `unknown`.

## Reading order

1. `30 - IR/00 - Argon Framework/` — substrate (staging, symbols, transformers)
2. `30 - IR/10 - Spatial Nodes/` — what Spatial adds to Argon
3. `40 - Compiler Passes/` — the sequence from staged block to codegen-ready IR
4. `10 - Language Surface/` — surface API that stages the nodes
5. `20 - Semantics/` — formalization synthesized from 1-4
6. `50 - Code Generation/20 - Scalagen/` — reference emulation = ground truth
7. `50 - Code Generation/10 - Chiselgen/` — RTL backend
8. Backends 30/40/50 — cppgen, pirgen, others
9. `60 - Polyhedral Model/`, `70 - Models and DSE/`, `80 - Runtime and Fringe/`

## Cross-references

- [[source-tree-map]] — directory → coverage-note → spec-target mapping
- [[pass-pipeline-order]] — canonical pass sequence
- [[node-to-codegen-matrix]] — per-node × per-backend emission summary
