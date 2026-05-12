---
type: spec
status: draft
concept: scheduling-model
source_files:
  - "argon/src/argon/State.scala:9-53"
  - "argon/src/argon/State.scala:124-146"
  - "argon/src/argon/static/Scoping.scala:16-119"
  - "argon/src/argon/schedule/Scheduler.scala:6-38"
  - "argon/src/argon/schedule/SimpleScheduler.scala:6-34"
  - "argon/src/argon/schedule/Schedule.scala:9-13"
  - "argon/src/argon/BlockOptions.scala:5-12"
  - "src/spatial/transform/PipeInserter.scala:15-323"
  - "src/spatial/transform/unrolling/UnrollingBase.scala:126-187"
  - "src/spatial/transform/unrolling/ForeachUnrolling.scala:21-86"
source_notes:
  - "[[60 - Scopes and Scheduling]]"
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
  - "[[50 - Staging Pipeline]]"
  - "[[50 - Pipe Insertion]]"
  - "[[80 - Unrolling]]"
hls_status: rework
depends_on:
  - "[[60 - Scopes and Scheduling]]"
  - "[[30 - Effects and Aliasing]]"
  - "[[20 - Ops and Blocks]]"
  - "[[50 - Staging Pipeline]]"
  - "[[50 - Pipe Insertion]]"
  - "[[80 - Unrolling]]"
---

# Scheduling Model

## Summary

The Spatial scheduling model is a stack of three related mechanisms. Argon first schedules a lexical staging scope into a `Block` using `SimpleScheduler`; Spatial then inserts explicit `Pipe` structure so outer controls do not mix primitive compute and child controllers; finally unrolling duplicates controllers, memories, and accesses according to counter parallelism and banking metadata. [[60 - Scopes and Scheduling]] defines the base block scheduler, [[30 - Effects and Aliasing]] explains why effect dependencies constrain statement order, [[50 - Pipe Insertion]] makes hardware-stage boundaries explicit, and [[80 - Unrolling]] explains how parallel lanes become real duplicated IR. The semantics are intentionally conservative: Spatial does not infer a full partial-order schedule from scratch. It stages in source order, records effect anti-dependencies, DCEs only idempotent dead symbols, and later structural passes reshape the graph.

## Formal Semantics

A staging scope is a `ScopeBundle`: `(scope, impure, cache, handle)` where `scope` is the ordered vector of all staged syms, `impure` is the ordered vector of `Impure` scheduling facts, and `cache` maps CSE-eligible ops to symbols (`argon/src/argon/State.scala:14-21`). The active bundle is installed by `withScope`; `withNewScope(motion)` creates a fresh bundle and inherits the outer cache exactly when `motion` is true (`argon/src/argon/State.scala:124-146`). Therefore cache inheritance is the only default cross-scope code motion mechanism before a scheduler returns explicit `motioned` symbols.

`stageScope_Start` creates a bundle, stages the user block, and returns raw `(result, scope, impure, scheduler, motion)`; `stageScope_Schedule` invokes the scheduler and appends returned `motioned` syms to the outer scope when motion is enabled (`argon/src/argon/static/Scoping.scala:16-78`). `BlockOptions` supplies a frequency hint and optional scheduler; `Normal` is `Freq.Normal` with no override, and `Sealed` is `Freq.Cold` with no override (`argon/src/argon/BlockOptions.scala:5-12`). [[20 - Ops and Blocks]] defines `Block` itself as `(inputs, stms, result, effects, options)`.

The default scheduler is `SimpleScheduler`. Its semantic output is `Schedule(block, Nil)`: it never moves code out, even when `allowMotion` is true (`argon/src/argon/schedule/SimpleScheduler.scala:10-31`, `argon/src/argon/schedule/Schedule.scala:9-13`). Its only optimization is reverse-order dead-code elimination. A symbol is dropped iff four conditions hold: it is not the block result, it has no live consumers after already-dropped consumers are subtracted, its effects are idempotent, and DCE is enabled (`argon/src/argon/schedule/SimpleScheduler.scala:21-27`). The `s != result` guard is semantic: a block result must stay present even when no outer consumer exists, because the result is the block's value.

The resulting block preserves the relative order of kept statements from the original `scope.filter`, so DCE never reorders survivors (`argon/src/argon/schedule/SimpleScheduler.scala:27-30`). This matters for effectful-but-idempotent reads: they can be kept or removed by liveness, but they are not floated across siblings by this scheduler.

Effects are the real scheduling constraints. During staging, `computeEffects` creates anti-dependencies from global effects, write-after-read hazards, access-after-write hazards, allocation-before-access dependencies, simple-effect ordering, and prior global ordering (`argon/src/argon/static/Staging.scala:202-234`). `Scheduler.summarizeScope` then folds `andThen` over the scope's impure vector and attaches the full impure list as the parent-visible anti-dependency list (`argon/src/argon/schedule/Scheduler.scala:14-26`). Thus schedules emerge from a source-ordered statement vector plus anti-dependency summaries; no later pass may treat a block as freely reorderable unless it preserves those dependencies.

Spatial's `PipeInserter` adds the next layer. For each outer-control block, it classifies statements as `Transient`, `Alloc`, `Primitive`, `Control`, or `FringeNode`; primitives are placed in inner stages, allocations/controls/fringe nodes in outer stages, and transient nodes are attached to the last stage whose nodes or effect writes feed them (`src/spatial/transform/PipeInserter.scala:117-134`). It wraps inner stages in `Pipe { ... }`, routes escaping bit values through `Reg` or `FIFOReg` holders, and routes non-bit values through `Var` holders (`src/spatial/transform/PipeInserter.scala:170-209`, `src/spatial/transform/PipeInserter.scala:256-305`). For parallel or stream parents, an inner stage that produces a value consumed by the next outer stage can be bound with that following stage (`src/spatial/transform/PipeInserter.scala:135-168`). The postcondition is recorded globally by setting `allowPrimitivesInOuterControl = false` (`src/spatial/transform/PipeInserter.scala:317-321`).

Unrolling preserves this staged structure while materializing parallelism. `UnrollingBase.unroll` decides whether a symbol is a control and then calls `duplicateController` or lane duplication; if multiple duplicate controllers are produced in MoP mode, they are wrapped in a `ParallelPipe` (`src/spatial/transform/unrolling/UnrollingBase.scala:126-178`). `ForeachUnrolling` turns loops into `UnitPipe`, `UnrolledForeach`, or `ParallelPipe` compositions depending on full-vs-partial unroll and MoP-vs-PoM (`src/spatial/transform/unrolling/ForeachUnrolling.scala:21-86`). This connects [[80 - Unrolling]] back to scheduling: a `par` factor does not merely annotate a scalar loop; it creates lane-specific substitutions, valid bits, and sometimes controller copies.

## Reference Implementation

Argon is normative for block scheduling; Spatial passes are normative for hardware-stage shape. `SimpleScheduler`'s code-motion output is empty, so any observed motion comes from CSE cache inheritance, transformer rewrites, `PipeInserter`, or unrolling, not from the scheduler itself (`argon/src/argon/schedule/SimpleScheduler.scala:30`). `SwitchScheduler`, described in [[10 - Controllers]], is the main custom scheduler exception: it keeps `SwitchCase` nodes in the switch body and motions other statements out. This synthesis does not add a new scheduler semantics beyond those lower-level entries.

## HLS Implications

The HLS rewrite should preserve Argon's source-ordered staging and effect-based anti-dependencies even if the final HLS compiler can schedule operations more aggressively. `PipeInserter` is marked rework because HLS tools can infer many registers, but the explicit holder semantics are still observable in Scalagen and later passes. A Rust IR can represent schedule as a block plus dependency edges, then lower `Pipe`, `ParallelPipe`, and unrolled lanes to HLS `pipeline`, `dataflow`, and `unroll` pragmas. The important part is to avoid treating `SimpleScheduler` as a full optimizer; it is an idempotent DCE pass plus block packager.

## Open questions

- [[open-questions-semantics#Q-sem-03 - 2026-04-25 Default scheduler motion semantics]] asks whether the dead `defaultSched` motion branch and empty `SimpleScheduler` motion output should be deleted or generalized in Rust.
- [[open-questions-semantics#Q-sem-04 - 2026-04-25 Pipe holder observability in HLS]] asks which `PipeInserter` holder effects must remain visible in an HLS backend that could otherwise rely on SSA scheduling.
