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

## 30 September 2026 — Architecture and protocol review in progress

The manager independently inspected xDSL's pinned base/optional dependencies, operation verifier, effect traits, and clone behavior. The first functional probe in PY-R006 was extracted and rerun using its recorded isolated environment. Stdout matched exactly: two consuming operations survived CSE/DCE, cloned passes preserved the original count, generic text round-tripped, an operand type mismatch rejected, and same-block use-before-definition passed the framework verifier. This supports the need for Spatial-owned dominance/effect checking; it does not validate a Spatial dialect or compiler. Framework timing numbers have not been promoted to compiler performance evidence.

Review of PY-R008 found a progress bug in the proposed atomic merge-vector rule: one input way of capacity one could not supply two output elements before the proposed all-at-once consume committed. The writer replaced that rule with explicit per-token consumption into a bounded packer followed by atomic output publication, and added the capacity-one discriminator. Review also required semantic publication credits and stop-sensitive iteration admission to stay distinct from physical depth or a soft II preference. These are design repairs, not fixed implementation bugs.

Independent source checks confirmed caller-index round-robin priorities, PIR lock key handling, FSM action-before-next emission, per-field StreamStruct dequeue, and sparse-transfer padding at the cited original revision. The published source notes for data types and numeric reference behavior were also corrected locally from pinned evidence; these source-documentation edits preserve the frozen D-26 record.

## 30 September 2026 — Full scope and independent challenge

The manager independently expanded R005's source-family table and compared it with the pinned repository tree: exactly 124 paths, no duplicate or missing entries (58 Spatial language, 33 Spatial node, 24 Argon language, nine library files). The ledger contains all 106 original `type: spec` documents; each row names a substantive family, migration obligation, implementation stage, and gate. This verifies research accounting, not implemented language support. The manager accepts the R004 source/builder comparison and R005 crosswalk as research artifacts after source/probe and coverage checks; their author's review is not counted as independent certification.

The separate architecture review repaired three issues: trace safety without progress, a missing versioned foreign-model registry, and ambiguity between failed planning and eligible emitted artifacts. The protocol/HLS review repaired keyed-lock serialization that could introduce deadlock, stale-view behavior across free/reallocation, and packed-word updates that could lose a disjoint nibble write. Reviewers reread the actual repairs and retained their counterexamples. These are specification repairs before implementation, not claims of fixed compiler defects.

Numeric integration separates state-free combines from fault-free/speculatable operations, permits lawful identity-free reduction with a nonempty requirement, fixes contribution-versus-combine fault order, and makes stochastic draw/exhaustion and general rational division explicit. A seeded generator defines replay; ideal-uniform probability calculations are not a statistical theorem about every seed. Final independent numerical findings and verification are recorded in the numeric review.

The manager reran R011's saved Philox probe and matched all three outputs against the official Random123 v1.14.0 known-answer file. Its retrieved SHA256 was `aab5ebabf40003f63d6d87b24cbd2c8a02652e00cf8bad64226fd50586929183`. This verifies the bounded round/word examples, not an integrated RNG or RTL design. The earlier R002/R004 probes and R006 functional probe were also independently reproduced as recorded above.

Primary-source reinspection confirmed R010's original DSE analysis omissions, allocation-status request/response distinction, and narrow legacy HLS recognizer. AMD's 2025.2 manual-burst page gives different cross-process guidance in simulation and tool-limit sections, so the proposal keeps a single owner until a release-specific executable gate passes. Reinspection of PG060 v7.1 confirmed the cited subnormal, rounding, signaling-NaN and observed-FMA-status differences. These checks do not establish any installed vendor capability.

The four proposed contracts and D-28 distill these findings. Original numeric source notes received dated corrections; frozen D-26 and prior measured evidence were preserved. The completion audit tracks final document checks and publication separately from compiler, math-certificate, vendor, and device evidence that remains unrun.

## 2 October 2026 — Fable review and independent numerical countercheck

At David's explicit request, four text-only `claude2 -p` Fable sessions reviewed snapshot `8e5dd54`: three focused reviews followed by an all-document reconciliation. The requested account was verified locally; each successful result identified `claude-fable-5-1` with no tools or MCP servers. All 44 supplied documents were frozen and hash-checked. [[09 - Fable Design Review]] owns the integrating disposition, and [[10 - Fable Reconciled Feedback]] preserves the full final response.

The integrating agent reproduced an incorrect underflow status at the minimum-normal boundary using the frozen quantizer and two exact-arithmetic formulations of the tininess rule, checked against the official SoftFloat FAQ. Two cases return NX where UF+NX is required; a boundary control correctly remains NX. The old candidate and enumerating oracle share the bad predicate. No SoftFloat binary, Scala program, Python Spatial compiler or vendor tool ran in this check. The original design/probe is flagged pending repair, and its historical archive is unchanged.

The review retains the Python direction and shared checked-program architecture while identifying contract/API work and a measured xDSL/custom-IR comparison. Several criticisms were rejected or narrowed against existing rules. Syntax, initialization and protocol recommendations remain unadopted. The evidence archive includes all four final reports, frozen documents, provenance and the portable reproduction; raw model event streams and authentication metadata are excluded.
