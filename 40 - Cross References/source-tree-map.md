---
type: moc
project: spatial-spec
date_started: 2026-04-21
---

# Source Tree → Subsystem → Spec Map

Navigational index mapping the Spatial source tree to the Phase 1 coverage notes and the (future) spec subtree each subsystem feeds. Draft; refined during Phase 2 as deep-dive content lands.

## Top-level Spatial repo layout

| Source path | ~files | Coverage note | Primary spec target |
|---|---|---|---|
| `argon/src/argon/` | 95 | [[argon-coverage]] | `10 - Spec/30 - IR/00 - Argon Framework/`, `10 - Spec/20 - Semantics/`, `10 - Spec/40 - Compiler Passes/` (transformer+scheduler framework) |
| `forge/src/forge/` | 22 | [[forge-runtime-coverage]] | `10 - Spec/30 - IR/00 - Argon Framework/`, foundations (macro annotations, virtualization) |
| `utils/src/` | ~27 | [[forge-runtime-coverage]] | foundation utilities (Instrument, Tree, math helpers, IO) |
| `emul/src/` | 21 | [[forge-runtime-coverage]] | `10 - Spec/50 - Code Generation/20 - Scalagen/` runtime (numeric formats, memory simulators) |
| `src/spatial/lang/` + top-level `*.scala` | 62 | [[spatial-lang-coverage]] | `10 - Spec/10 - Language Surface/` (controllers, memories, primitives, host, IO, counters) |
| `src/spatial/node/` + `metadata/` + `tags/` | 79 | [[spatial-ir-coverage]] | `10 - Spec/30 - IR/10 - Spatial Nodes/`, `10 - Spec/30 - IR/20 - Metadata/` |
| `src/spatial/transform/` + `rewrites/` + `traversal/` + `flows/` | 78 | [[spatial-passes-coverage]] | `10 - Spec/40 - Compiler Passes/` (densest section — ~25 transformations + ~10 analyses) |
| `src/spatial/codegen/chiselgen/` | 17 | [[codegen-fpga-host-coverage]] | `10 - Spec/50 - Code Generation/10 - Chiselgen/` |
| `src/spatial/codegen/cppgen/` | 10 | [[codegen-fpga-host-coverage]] | `10 - Spec/50 - Code Generation/30 - Cppgen/` |
| `src/spatial/codegen/{dotgen,naming,resourcegen,treegen}/` | ~11 | [[codegen-fpga-host-coverage]] | `10 - Spec/50 - Code Generation/50 - Other Codegens.md`, debugging / reporting |
| `src/spatial/codegen/scalagen/` | 29 | [[codegen-sim-alt-coverage]] | `10 - Spec/50 - Code Generation/20 - Scalagen/` — **reference semantics anchor** |
| `src/spatial/codegen/pirgen/` | 32 | [[codegen-sim-alt-coverage]] | `10 - Spec/50 - Code Generation/40 - Pirgen/` |
| `src/spatial/codegen/{roguegen,tsthgen}/` | 15 | [[codegen-sim-alt-coverage]] | alternate host / simulator emitters |
| `fringe/src/` | 149 | [[fringe-coverage]] | `10 - Spec/80 - Runtime and Fringe/` — largest single subsystem |
| `src/spatial/targets/` | 27 | [[hardware-targets-coverage]] | `10 - Spec/70 - Models and DSE/30 - Target Hardware Specs.md` |
| `poly/src/` | 8 | [[poly-models-dse-coverage]] | `10 - Spec/60 - Polyhedral Model/` |
| `models/src/` | 13 | [[poly-models-dse-coverage]] | `10 - Spec/70 - Models and DSE/` (shared cost models) |
| `src/spatial/dse/` | 18 | [[poly-models-dse-coverage]] | `10 - Spec/70 - Models and DSE/40 - Design Space Exploration.md` |
| `src/spatial/{lib,math,executor,model,issues,report,util}/` | ~54 | [[poly-models-dse-coverage]] | various — standard library, executor, reports, utilities |

**Total Scala file count mapped in Phase 1:** ~765 files across 10 coverage notes.

## Quick facts (cross-cutting)

- **Reference semantics**: `src/spatial/codegen/scalagen/*` + `emul/src/*` — when two backends disagree, scalagen+emul is the ground truth.
- **Canonical pass order**: `src/spatial/Spatial.scala:60-257` (`runPasses`). See `spatial-passes-coverage` §8 for the 24-step enumeration.
- **Most complex single pass**: `MemoryConfigurer.scala` (818 lines) inside `traversal/banking/`.
- **Largest single subsystem by file count**: `fringe/src/` (149 Scala files, mostly Chisel hardware templates).
- **Pipeline entry**: `Spatial` trait (`src/spatial/Spatial.scala`), user apps extend `SpatialApp` which is `Spatial with argon.DSLApp`.

## Phase 2 priority order (from workflow.md)

1. Argon framework — Round 1 dispatched 2026-04-23 → `10 - Spec/30 - IR/00 - Argon Framework/`
2. Spatial IR nodes + metadata — Round 1 dispatched 2026-04-23 → `10 - Spec/30 - IR/10 - Spatial Nodes/`
3. Pass pipeline (canonical order first, then passes in dependency order) — Round 1 dispatched 2026-04-23 → `10 - Spec/40 - Compiler Passes/`
4. Language surface — Round 1 dispatched 2026-04-23 → `10 - Spec/10 - Language Surface/`
5. Semantics (synthesized from 1–4) — scheduled after Round 1 returns
6. Scalagen (reference semantics) → Chiselgen — Round 2 dispatched 2026-04-23 → `10 - Spec/50 - Code Generation/20 - Scalagen/`, `/10 - Chiselgen/`
7. Cppgen, pirgen, other codegens — Round 2 dispatched 2026-04-23 → `10 - Spec/50 - Code Generation/30 - Cppgen/`, `/40 - Pirgen/`, `50 - Other Codegens.md`
8. Polyhedral, Models, DSE, Fringe, Targets — Round 2 dispatched 2026-04-23 → `10 - Spec/60 - Polyhedral Model/`, `/70 - Models and DSE/`, `/80 - Runtime and Fringe/`
9. Testing, Debugging, Build — pending (Phase 2 tail)

## Deep-dive notes (Phase 2, in progress)

- `20 - Research Notes/10 - Deep Dives/argon-framework.md` (Round 1)
- `20 - Research Notes/10 - Deep Dives/spatial-ir-nodes.md` (Round 1)
- `20 - Research Notes/10 - Deep Dives/pass-pipeline.md` (Round 1)
- `20 - Research Notes/10 - Deep Dives/language-surface.md` (Round 1)
- `20 - Research Notes/10 - Deep Dives/scalagen-reference-semantics.md` (Round 2)
- `20 - Research Notes/10 - Deep Dives/chiselgen.md` (Round 2)
- `20 - Research Notes/10 - Deep Dives/other-codegens.md` (Round 2)
- `20 - Research Notes/10 - Deep Dives/poly-models-dse.md` (Round 2)
- `20 - Research Notes/10 - Deep Dives/fringe-and-targets.md` (Round 2)
