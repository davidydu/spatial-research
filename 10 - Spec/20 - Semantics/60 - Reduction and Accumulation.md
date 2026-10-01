---
type: spec
status: draft
concept: reduction-and-accumulation
source_files:
  - "src/spatial/node/Control.scala:57-101"
  - "src/spatial/node/Accumulator.scala:9-57"
  - "src/spatial/node/HierarchyUnrolled.scala:143-154"
  - "src/spatial/traversal/AccumAnalyzer.scala:14-244"
  - "src/spatial/transform/AccumTransformer.scala:13-137"
  - "src/spatial/traversal/IterationDiffAnalyzer.scala:15-217"
  - "src/spatial/metadata/memory/AccumulatorData.scala:5-103"
  - "src/spatial/metadata/memory/package.scala:14-43"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-64"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-96"
  - "spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-75"
  - "spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:201-223"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:844-867"
  - "spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:671-677"
source_notes:
  - "[[10 - Controllers]]"
  - "[[B0 - Accum Specialization]]"
  - "[[60 - Use and Access Analysis]]"
  - "[[60 - Counters and Primitives]]"
  - "[[30 - Memory]]"
  - "[[20 - Numeric Reference Semantics]]"
hls_status: rework
depends_on:
  - "[[10 - Controllers]]"
  - "[[B0 - Accum Specialization]]"
  - "[[60 - Use and Access Analysis]]"
  - "[[60 - Counters and Primitives]]"
  - "[[30 - Memory]]"
  - "[[20 - Numeric Reference Semantics]]"
  - "[[80 - Unrolling]]"
---

# Reduction and Accumulation

> [!note] Source correction — 30 September 2026
> Reinspection corrected the scalar-versus-memory `fold` fields and an unsupported blanket claim about fixed-point hardware FMA precision. The pinned evidence is recorded below and in [[02 - Python Research Review Log]]. These corrections describe original source; proposed Python semantics are a separate decision.

## Summary

Spatial has two related but distinct semantics: structured reductions from controller nodes and optimized register accumulations from cycle analysis. [[10 - Controllers]] defines `OpReduce` and `OpMemReduce` as loop controllers with dedicated map/load/reduce/store bodies. [[60 - Use and Access Analysis]] and [[B0 - Accum Specialization]] detect closed write-after-read accumulator cycles and replace them with `RegAccumOp` or `RegAccumFMA`. [[60 - Counters and Primitives]] defines Scalagen's runtime behavior for those specialized nodes. A rewrite must define first-iteration behavior, enable sets, reduction identity/fold distinctions, accumulator-cycle legality, and the arithmetic behavior of each specific FMA path.

## Formal Semantics

`OpReduce` is a `Loop[Void]` with one counter chain, an accumulator memory, map/load/reduce/store blocks, optional identity, an optional fold initializer (`fold: Option[A]`), iterator bindings, and optional `stopWhen` (`spatial@e7a8f2f:src/spatial/node/Control.scala:57-76`). Its bodies are a pseudo map stage followed by an inner stage containing load, reduce, and store blocks. `OpMemReduce` has separate map and reduce counter chains, a local memory accumulator, and a Boolean `fold` mode; its inner stage contains load-result, load-accumulator, reduce, and store-accumulator blocks with different iterator visibility per sub-block (`spatial@e7a8f2f:src/spatial/node/Control.scala:78-101`). These body shapes are the formal basis for [[80 - Unrolling]] and retiming.

The scalar DSL separates identity, fold initializer, and explicit accumulator. The `Fold` overload accepting a lifted value uses `isFold = true`; the overload accepting a symbol uses `isFold = false` in this revision (`spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-96`). Full scalar unrolling prepends the optional initializer to the reduction-tree inputs; partial unrolling combines `treeResult` with the selected initial/prior accumulator value (`spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:55-75`, `spatial@e7a8f2f:src/spatial/transform/unrolling/ReduceUnrolling.scala:201-223`). Consequently, the name `Fold` alone does not establish an ordered left fold for an arbitrary combining function. Identity-bearing reductions and identity-free validity handling must also remain distinct (`src/spatial/transform/unrolling/ReduceUnrolling.scala:152-168`).

Accumulator-cycle detection is analysis driven. `AccumAnalyzer` visits hardware controls, runs latency/cycle analysis, keeps `WARCycle`s, rejects cycles that overlap, expose intermediates, target non-local memory, have multiple writers, or match disallowed outer reduce writers, then attaches copied `reduceCycle` metadata to every symbol in the accepted cycle (`src/spatial/traversal/AccumAnalyzer.scala:29-103`). `AssociateReduce` recognizes register-write shapes for add, multiply, min, max, and FMA over a `RegRead` of the same register, including muxed first-iteration forms and an `invert` flag (`src/spatial/traversal/AccumAnalyzer.scala:195-241`). The marker is either `AccumMarker.Reg.Op(reg, data, written, first, ens, op, invert)` or `AccumMarker.Reg.FMA(reg, m0, m1, written, first, ens, invert)` (`src/spatial/node/Accumulator.scala:18-28`).

`AccumTransformer` consumes those markers. It partitions statements into cycle and non-cycle groups, keeps feed statements before the cycle, keeps users and later memory reads after it, and replaces each accepted cycle with a single `RegAccumOp` or `RegAccumFMA` (`src/spatial/transform/AccumTransformer.scala:50-95`). For `Reg.Op`, it stages a `RegAccumOp` and substitutes the old writer to `void` and the old written value to the accumulator result; for `Reg.FMA`, it stages `RegAccumFMA` with analogous substitutions (`src/spatial/transform/AccumTransformer.scala:96-122`). The replacement nodes extend `RegAccum`, which extends the post-unroll `Accumulator` accessor with `Effects.Writes(mem)` and `data = Nil` (`src/spatial/node/Accumulator.scala:30-57`, `src/spatial/node/HierarchyUnrolled.scala:143-154`).

The specialized runtime semantics are explicit in Scalagen. `RegAccumOp(reg, in, en, op, first)` computes `reg.value + in`, `reg.value * in`, `Number.max`, or `Number.min` depending on `op`; when enabled, it writes `in` on first iteration and the computed value otherwise, then returns `reg.value` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-55`). `AccumFMA` and `AccumUnk` in `RegAccumOp` throw `"This shouldn't happen!"`, so the upstream invariant is that FMA has already been split and unknown accumulation has been rejected (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:49-50`). `RegAccumFMA(reg, m0, m1, en, first)` writes `m0*m1` on first iteration and `m0*m1 + reg.value` otherwise (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`).

FMA paths require separate inspection. Scalagen emits `FixFMA` as `($m1 * $m2) + $add` (`spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`). The generic fixed-point hardware template also explicitly multiplies with truncation/wrapping and then adds; this code does not support the earlier claim that the fixed-point hardware path necessarily preserves fused intermediate precision (`spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:844-867`). Floating-point Scalagen emits multiply then add, while its hardware template calls `ffma` (`spatial@e7a8f2f:src/spatial/codegen/scalagen/ScalaGenFltPt.scala:120`; `spatial@e7a8f2f:fringe/src/fringe/templates/math/Math.scala:671-677`). The selected arithmetic implementation and specialized accumulator paths need their own evidence; inspection of these generic templates is not a hardware-equivalence test.

`AccumType` is the metadata lattice that classifies memory accumulation behavior. The requested semantic order is `Fold > Reduce > Buff > None > Unknown`, but [[30 - Memory]] records a source-level contradiction: the current `>` methods implement `Fold > all`, `Buff > Reduce/None/Unknown`, `Reduce > None/Unknown`, `None > Unknown`, and `Unknown > nothing` (`src/spatial/metadata/memory/AccumulatorData.scala:11-45`). The accessor also defaults to `Unknown` while the metadata comment says `None` (`src/spatial/metadata/memory/AccumulatorData.scala:49-57`, `src/spatial/metadata/memory/package.scala:14-16`). This synthesis records the intended lattice while flagging the implementation mismatch for main-session resolution.

Iteration distance affects reduction II. `IterationDiffAnalyzer` calls `findAccumCycles`, computes minimum ticks to overlap and segment mappings, sets `OpMemReduce` iterDiff to zero and `OpReduce` iterDiff to one, and writes iterDiff to reader, writer, and memory metadata (`src/spatial/traversal/IterationDiffAnalyzer.scala:17-118`, `src/spatial/traversal/IterationDiffAnalyzer.scala:193-210`). `InitiationAnalyzer` later uses `iterDiff` to compute `compilerII = ceil(interval / iterDiff)` or force II=1 for nonpositive distances (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). This closes the loop from structured reductions to timing.

## Reference Implementation

For dynamic behavior, [[60 - Counters and Primitives]] is normative for `RegAccumOp` and `RegAccumFMA`, and [[20 - Numeric Reference Semantics]] is normative for fixed-point and FMA lowering. For legality and IR rewriting, [[B0 - Accum Specialization]] and [[60 - Use and Access Analysis]] are normative. The current implementation does not state that `AccumTransformer` directly sets II; it relies on specialized nodes, retiming, and codegen paths, which is already tracked in the pass-level notes (`src/spatial/transform/AccumTransformer.scala:39-48`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`).

## HLS Implications

HLS reduction design must specify the contribution effects, combining topology, seed/identity behavior, and enable/first-iteration rules. The compiler and simulator need one explicit arithmetic contract, with any contraction or reassociation justified against it. A pragma or a shared operator name does not establish equivalence between the original implementation, Python simulation, and generated hardware.

## Open questions

- [[open-questions-semantics#Q-sem-11 - 2026-04-25 FMA fused versus Scalagen unfused semantics]] tracks the Rust+HLS choice for `FixFMA` and `RegAccumFMA`.
- [[open-questions-semantics#Q-sem-12 - 2026-04-25 AccumType lattice contradiction]] tracks whether `Fold > Reduce > Buff > None > Unknown` or current source `Fold > Buff > Reduce > None > Unknown` is authoritative.
