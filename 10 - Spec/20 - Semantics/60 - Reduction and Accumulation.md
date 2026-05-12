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

## Summary

Spatial has two related but distinct semantics: structured reductions from controller nodes and optimized register accumulations from cycle analysis. [[10 - Controllers]] defines `OpReduce` and `OpMemReduce` as loop controllers with dedicated map/load/reduce/store bodies. [[60 - Use and Access Analysis]] and [[B0 - Accum Specialization]] detect closed write-after-read accumulator cycles and replace them with `RegAccumOp` or `RegAccumFMA`. [[60 - Counters and Primitives]] defines Scalagen's runtime behavior for those specialized nodes. For Rust+HLS, the correctness requirement is to preserve first-iteration behavior, enable sets, reduction identity/fold distinctions, accumulator-cycle legality, and the known FMA precision divergence.

## Formal Semantics

`OpReduce` is a `Loop[Void]` with one counter chain, an accumulator memory, map/load/reduce/store blocks, optional identity, a `fold` flag, iterator bindings, and optional `stopWhen` (`src/spatial/node/Control.scala:57-76`). Its bodies are a pseudo map stage followed by an inner stage containing load, reduce, and store blocks. `OpMemReduce` generalizes this to separate map and reduce counter chains and a local memory accumulator; its inner stage contains load-result, load-accumulator, reduce, and store-accumulator blocks with different iterator visibility per sub-block (`src/spatial/node/Control.scala:78-101`). These body shapes are the formal basis for [[80 - Unrolling]] and retiming.

Fold vs reduce is carried explicitly. The DSL creates `Reduce`, `Fold`, `MemReduce`, and `MemFold` variants; the IR stores a `fold` boolean and optional identity (`src/spatial/lang/control/ReduceClass.scala:38-51`, `src/spatial/lang/control/MemReduceClass.scala:74-91`). In unrolling, identity-bearing reductions replace invalid lane inputs with the identity; identity-free reductions propagate a validity bit and mux between the accumulated value and the first valid lane (`src/spatial/transform/unrolling/ReduceUnrolling.scala:152-168`). This synthesis treats "fold" as the variant in which the accumulator carries prior state across iterations, while "reduce" is the structured tree/identity reduction shape, matching the lower-level entries (inferred, unverified where the `fold` flag itself is not separately defined).

Accumulator-cycle detection is analysis driven. `AccumAnalyzer` visits hardware controls, runs latency/cycle analysis, keeps `WARCycle`s, rejects cycles that overlap, expose intermediates, target non-local memory, have multiple writers, or match disallowed outer reduce writers, then attaches copied `reduceCycle` metadata to every symbol in the accepted cycle (`src/spatial/traversal/AccumAnalyzer.scala:29-103`). `AssociateReduce` recognizes register-write shapes for add, multiply, min, max, and FMA over a `RegRead` of the same register, including muxed first-iteration forms and an `invert` flag (`src/spatial/traversal/AccumAnalyzer.scala:195-241`). The marker is either `AccumMarker.Reg.Op(reg, data, written, first, ens, op, invert)` or `AccumMarker.Reg.FMA(reg, m0, m1, written, first, ens, invert)` (`src/spatial/node/Accumulator.scala:18-28`).

`AccumTransformer` consumes those markers. It partitions statements into cycle and non-cycle groups, keeps feed statements before the cycle, keeps users and later memory reads after it, and replaces each accepted cycle with a single `RegAccumOp` or `RegAccumFMA` (`src/spatial/transform/AccumTransformer.scala:50-95`). For `Reg.Op`, it stages a `RegAccumOp` and substitutes the old writer to `void` and the old written value to the accumulator result; for `Reg.FMA`, it stages `RegAccumFMA` with analogous substitutions (`src/spatial/transform/AccumTransformer.scala:96-122`). The replacement nodes extend `RegAccum`, which extends the post-unroll `Accumulator` accessor with `Effects.Writes(mem)` and `data = Nil` (`src/spatial/node/Accumulator.scala:30-57`, `src/spatial/node/HierarchyUnrolled.scala:143-154`).

The specialized runtime semantics are explicit in Scalagen. `RegAccumOp(reg, in, en, op, first)` computes `reg.value + in`, `reg.value * in`, `Number.max`, or `Number.min` depending on `op`; when enabled, it writes `in` on first iteration and the computed value otherwise, then returns `reg.value` (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:41-55`). `AccumFMA` and `AccumUnk` in `RegAccumOp` throw `"This shouldn't happen!"`, so the upstream invariant is that FMA has already been split and unknown accumulation has been rejected (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:49-50`). `RegAccumFMA(reg, m0, m1, en, first)` writes `m0*m1` on first iteration and `m0*m1 + reg.value` otherwise (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`).

FMA precision is a required divergence note. Scalagen emits `FixFMA` as `($m1 * $m2) + $add`, so the multiply rounds before the add (`spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`). `RegAccumFMA` uses the same unfused multiply-then-add structure (`spatial/src/spatial/codegen/scalagen/ScalaGenReg.scala:57-64`). The lower-level Scalagen notes state this diverges from Chisel hardware FMA precision. The Rust+HLS port must choose which behavior to match: Scalagen for simulator parity, or Chisel/HLS fused behavior for hardware parity. This is not a harmless optimization because fixed-point low bits can differ.

`AccumType` is the metadata lattice that classifies memory accumulation behavior. The requested semantic order is `Fold > Reduce > Buff > None > Unknown`, but [[30 - Memory]] records a source-level contradiction: the current `>` methods implement `Fold > all`, `Buff > Reduce/None/Unknown`, `Reduce > None/Unknown`, `None > Unknown`, and `Unknown > nothing` (`src/spatial/metadata/memory/AccumulatorData.scala:11-45`). The accessor also defaults to `Unknown` while the metadata comment says `None` (`src/spatial/metadata/memory/AccumulatorData.scala:49-57`, `src/spatial/metadata/memory/package.scala:14-16`). This synthesis records the intended lattice while flagging the implementation mismatch for main-session resolution.

Iteration distance affects reduction II. `IterationDiffAnalyzer` calls `findAccumCycles`, computes minimum ticks to overlap and segment mappings, sets `OpMemReduce` iterDiff to zero and `OpReduce` iterDiff to one, and writes iterDiff to reader, writer, and memory metadata (`src/spatial/traversal/IterationDiffAnalyzer.scala:17-118`, `src/spatial/traversal/IterationDiffAnalyzer.scala:193-210`). `InitiationAnalyzer` later uses `iterDiff` to compute `compilerII = ceil(interval / iterDiff)` or force II=1 for nonpositive distances (`src/spatial/traversal/InitiationAnalyzer.scala:23-41`). This closes the loop from structured reductions to timing.

## Reference Implementation

For dynamic behavior, [[60 - Counters and Primitives]] is normative for `RegAccumOp` and `RegAccumFMA`, and [[20 - Numeric Reference Semantics]] is normative for fixed-point and FMA lowering. For legality and IR rewriting, [[B0 - Accum Specialization]] and [[60 - Use and Access Analysis]] are normative. The current implementation does not state that `AccumTransformer` directly sets II; it relies on specialized nodes, retiming, and codegen paths, which is already tracked in the pass-level notes (`src/spatial/transform/AccumTransformer.scala:39-48`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`).

## HLS Implications

HLS can express reductions naturally, but Spatial's semantics are more precise than "use a reduction pragma." The Rust compiler needs to reproduce the cycle legality proof, preserve enable and first-iteration signals, and decide FMA parity. The simulator should match Scalagen's unfused behavior unless project policy chooses hardware parity; the HLS backend may still emit a fused operator if that choice is documented and tests are split accordingly.

## Open questions

- [[open-questions-semantics#Q-sem-11 - 2026-04-25 FMA fused versus Scalagen unfused semantics]] tracks the Rust+HLS choice for `FixFMA` and `RegAccumFMA`.
- [[open-questions-semantics#Q-sem-12 - 2026-04-25 AccumType lattice contradiction]] tracks whether `Fold > Reduce > Buff > None > Unknown` or current source `Fold > Buff > Reduce > None > Unknown` is authoritative.
