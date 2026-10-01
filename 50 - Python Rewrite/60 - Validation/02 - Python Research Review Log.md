---
type: log
title: "Python research review log"
project: spatial-python
date: 2026-09-30
---

## 30 September 2026 — Foundation source checks

The integrating agent checked the following claims directly in the pinned original source. These are source inspections, not fresh Scala, Python compiler, or hardware executions. The corresponding studies will carry the proposed Python rules and their reasoning.

| Claim checked | Pinned evidence | Consequence for the research |
|---|---|---|
| Scalar reduction stores an optional fold initializer; memory reduction stores a Boolean fold mode | `spatial@e7a8f2f:src/spatial/node/Control.scala:57-101` | Do not collapse both into a Boolean plus identity; preserve the distinction in the proposed representation |
| The two implicit `Fold` overloads supply different `isFold` values | `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:90-96` | Original API spelling alone does not establish an ordered left-fold contract |
| Full unrolling prepends the optional fold value to tree inputs; partial accumulation combines the tree result with the selected initial/prior value | `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-75`; `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:201-223` | A proposed strict fold must be identified as a semantic choice, not an automatic transcription of original `Fold` |
| The fixed-point FMA template explicitly calls multiply with truncation/wrapping, then adds; the floating template calls `ffma` | `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:844-867`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:671-677` | A blanket claim that the fixed-point template necessarily uses fused precision is unsupported; floating and fixed-point paths need separate analysis |
| Original control defaults and rewrites distinguish pipelined, sequenced, fork, and fork/join schedules | `spatial@e7a8f2f:src/spatial/flows/SpatialFlowRules.scala:331-368` | Bare `Foreach` is not evidence for a universally sequential original schedule |
| Generated Scala FIFO storage is a mutable queue; enabled enqueue has no capacity check, while empty dequeue yields an invalid value | `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:12-20`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFIFO.scala:30-44` | Bounded FIFO faults or blocking in Python are explicit policy choices; do not attribute them to this simulator |
| Generated loop code warns that `breakWhen` differs from synthesis, and `UnitPipe` matches but does not use its stop field | `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:74-93`; `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:180-184` | Define cancellation and commit boundaries explicitly; no single old simulator path settles all target behavior |
| Generated `Switch` uses conditional branches; generated `ParallelPipe` calls `gen(func)` rather than establishing a cycle-accurate parallel simulator | `spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenController.scala:187-219` | Branch laziness has direct evidence, while parallel timing/backpressure still requires a separate contract |

The review distinguishes ordered evaluation of effectful contribution bodies from legal reassociation of a pure combining operation. This is an integration requirement for the candidate design, not yet a professor-approved language rule. Independent numeric and control writers were asked to address it consistently.

## Completion audit status

The initial source checks have produced design-relevant evidence, but they do not close R01–R12 in [[03 - Managed Research Execution]]. The detailed studies, full-scope crosswalk, architecture, HLS work, and final independent review are still in progress.
