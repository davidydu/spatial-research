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

## 30 September 2026 — Foundation integration review

The manager reviewed PY-R002–004 and requested repairs before accepting their recommendations. Ordinary assignment now follows Python RHS-before-target order, rather than silently importing the earlier Rust order. Augmented assignment retains its separate target-once/read-before-RHS rule. State lifetimes distinguish iteration scratch, outer loop-carried state, task activation, invocation state, and explicit persistence. Effectful contribution bodies remain distinct from pure reduction combiners.

Additional source spot-checks confirmed the normal float packing formula lacks retained-bit parity at a tie (`spatial@e7a8f2f:emul/src/emul/FloatPoint.scala:358-376`); runtime saturating casts pass raw values directly while ordinary casts rescale (`spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:107-114`; `spatial@e7a8f2f:emul/src/emul/FixedPoint.scala:90-93`); Exo's function capture uses introspected source and its host quotation executes constructed code (`exo@defe172:src/exo/frontend/pyparser.py:73-90`, `exo@defe172:src/exo/frontend/pyparser.py:432-445`, `exo@defe172:src/exo/frontend/pyparser.py:570-587`); Allo directly accepts source strings (`allo@094ab41:allo/ir/utils.py:144-161`). These checks support the distinctions in the studies; they do not run those compilers.

The manager independently extracted and reran the complete recorded Python probes from PY-R002 and PY-R004. Both reproduced their recorded stdout exactly, including 2,054,352 small-format fixed-FMA triples and the token/AST/source-span observations. The arithmetic probe is a bounded arithmetic experiment; the capture probe uses Python's parser only. Neither implements or validates a Python Spatial frontend.

Source-only capture is now the manager's research recommendation in [[PY-R001 - Programming Model Study]], with a builder for generators/tooling. Its strongest objection and reversal conditions remain visible. Full scope, advanced protocols, architecture/framework choice, host workflow, and HLS still require the later waves. The foundation authors do not count as the final independent reviewers of their own work.
