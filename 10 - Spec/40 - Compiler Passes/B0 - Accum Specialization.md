---
type: spec
concept: accum-specialization
source_files:
  - "src/spatial/transform/AccumTransformer.scala:13-137"
  - "src/spatial/traversal/AccumAnalyzer.scala:14-244"
  - "src/spatial/node/Accumulator.scala:18-50"
  - "src/spatial/metadata/memory/package.scala:358-365"
  - "src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292"
  - "src/spatial/Spatial.scala:215-225"
  - "src/spatial/SpatialConfig.scala:39"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[60 - Use and Access Analysis]]"
  - "[[90 - Rewrite Transformer]]"
  - "[[C0 - Retiming]]"
status: draft
---

# Accum Specialization

## Summary

Accumulator specialization is the optional pass family that turns closed register accumulation WAR cycles into single accumulator writer nodes (`src/spatial/transform/AccumTransformer.scala:50-135`). Spatial gates both the second `accumAnalyzer` run and `accumTransformer` on `spatialConfig.enableOptimizedReduce`, whose default is true but is disabled by `--noretime` and other runtime paths (`src/spatial/Spatial.scala:223-225`, `src/spatial/SpatialConfig.scala:39`, `src/spatial/Spatial.scala:449-452`). The first optional `accumAnalyzer` run happens before `rewriteTransformer`, so FMA fusion can see accumulator-specialization markers; the second run happens after rewrite and before `accumTransformer`, so the final cycle markers match the rewritten graph (`src/spatial/Spatial.scala:215-225`, `src/spatial/transform/RewriteTransformer.scala:28-40`).

## Pass list and roles

`AccumAnalyzer` is the producer of the metadata. It visits controls in hardware scope, marks inner blocks, runs `latenciesAndCycles(block, true)`, collects `WARCycle`s, and assigns a nonnegative `cycleID` only when the candidate is disjoint, has no visible intermediates, targets local memory, has exactly one writer, and is not an outer-reduce unit-pipe writer (`src/spatial/traversal/AccumAnalyzer.scala:29-43`, `src/spatial/traversal/AccumAnalyzer.scala:52-101`). The marker comes from `AssociateReduce`, which matches register writes whose written value is add, multiply, min, max, or FMA over a `RegRead` of the same register, including muxed first-iteration forms with an `invert` bit (`src/spatial/traversal/AccumAnalyzer.scala:195-240`). The marker data shape is defined as `AccumMarker.Reg.Op(reg, data, written, first, ens, op, invert)` or `AccumMarker.Reg.FMA(reg, m0, m1, written, first, ens, invert)` (`src/spatial/node/Accumulator.scala:18-27`).

`AccumTransformer` is the consumer. It enters accelerators and blackboxes, avoids inner switches and PIR mode, and registers each inner-stage or inner-control block to `optimizeAccumulators` (`src/spatial/transform/AccumTransformer.scala:15-35`). The replacement nodes are `RegAccumOp` and `RegAccumFMA`, staged by helpers that apply the `invert` flag to the first-iteration bit (`src/spatial/transform/AccumTransformer.scala:39-48`). Those accumulator nodes are concrete Spatial ops extending `RegAccum`, and memory metadata reports a register as optimized when one of its writers is a `RegAccum` op (`src/spatial/node/Accumulator.scala:30-50`, `src/spatial/metadata/memory/package.scala:358-365`).

## Algorithms

`optimizeAccumulators` starts by partitioning a block's statements into `cycles` and `nonCycles`, where a cycle statement must be `isInCycle` and have `reduceCycle.cycleID > -1` (`src/spatial/transform/AccumTransformer.scala:50-54`). It identifies cycle writer nodes, maps their written memories to writer indices in the original statement list, then classifies non-cycle statements as `beforeCycles` or `afterCycles`: a statement is after the specialized cycle if it uses a cycle node, reads a cycle memory after that memory's accumulation write, or depends on something already classified after the cycle (`src/spatial/transform/AccumTransformer.scala:55-71`). The code comments state the key precondition: analysis must have marked only closed accumulation cycles with no overlap and no partial outputs used outside the cycle (`src/spatial/transform/AccumTransformer.scala:73-79`).

The transformer then recreates the block in a fresh stage scope, visits all `beforeCycles`, groups cycle statements by `reduceCycle.cycleID`, and handles each group according to the marker on the group's `WARCycle` (`src/spatial/transform/AccumTransformer.scala:80-95`). For `AccumMarker.Reg.Op`, it stages `RegAccumOp(f(reg), f(data), f(first), f(ens), op, invert)`, registers the original writer to `void`, and registers the original written value to the accumulator result (`src/spatial/transform/AccumTransformer.scala:96-108`). For `AccumMarker.Reg.FMA`, it stages `RegAccumFMA(f(reg), f(m0), f(m1), f(first), f(ens), invert)` and applies the same writer/value substitutions (`src/spatial/transform/AccumTransformer.scala:110-122`). Unmarked cycles fall back to visiting their original symbols, and all `afterCycles` are visited after replacements are staged (`src/spatial/transform/AccumTransformer.scala:124-132`).

## Metadata produced/consumed

`AccumAnalyzer` writes `reduceCycle` metadata onto every symbol in an accepted WAR cycle, preserving the marker and assigning the cycle id (`src/spatial/traversal/AccumAnalyzer.scala:96-101`). `AccumTransformer` consumes `isInCycle`, `reduceCycle.cycleID`, `WARCycle.reader`, `WARCycle.writer`, `WARCycle.symbols`, and `WARCycle.marker` (`src/spatial/transform/AccumTransformer.scala:50-57`, `src/spatial/transform/AccumTransformer.scala:84-96`). The replacement also changes downstream memory metadata indirectly: `mem.isOptimizedReg` becomes true when a register has a `RegAccum` writer, and `optimizedRegType` distinguishes `AccumAdd`, `AccumMul`, `AccumMin`, `AccumMax`, `AccumFMA`, and `AccumUnk` (`src/spatial/metadata/memory/package.scala:358-365`). Chisel codegen uses that metadata on `RegNew` to instantiate specialized `FixOpAccum` or `FixFMAAccum` memories with op/cycle latency parameters, then emits `RegAccumOp`/`RegAccumFMA` writer ports that connect first-iteration and enable signals (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-276`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:281-292`).

## Invariants established

After this pass, an accepted closed accumulation cycle has one visible accumulator node replacing the reader/writer pair's written value, and the old writer symbol is substituted to `void` (`src/spatial/transform/AccumTransformer.scala:96-122`). Statements that feed the cycle remain before it, while statements using cycle results or later memory values remain after it, preserving local dataflow around the specialized node (`src/spatial/transform/AccumTransformer.scala:61-71`, `src/spatial/transform/AccumTransformer.scala:80-132`). The source-level evidence for the "II=1 accumulator node" role is the single `RegAccumOp`/`RegAccumFMA` replacement plus specialized codegen module path; the exact II guarantee is tracked as Q-pp-16 because `AccumTransformer` itself does not write `II` metadata (`src/spatial/transform/AccumTransformer.scala:39-48`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`).

## HLS notes

This is rework for HLS. The concept maps cleanly to recognizing reductions and using an HLS accumulator/resource pattern, but Spatial's legality proof depends on `WARCycle` analysis, closed-cycle checks, `AccumMarker` shape, and register-writer metadata rather than only loop syntax (`src/spatial/traversal/AccumAnalyzer.scala:38-101`, `src/spatial/traversal/AccumAnalyzer.scala:195-240`). The HLS version should preserve the same visible semantics of first-iteration selection, enable sets, and invert handling, because those are explicit operands on the specialized nodes (`src/spatial/node/Accumulator.scala:24-25`, `src/spatial/transform/AccumTransformer.scala:39-48`).

## Open questions

Q-pp-16 asks where the II=1 contract is formally enforced: the pass emits single accumulator nodes and codegen instantiates specialized accumulator modules, but the transformer does not directly set controller `II` metadata (`src/spatial/transform/AccumTransformer.scala:39-48`, `src/spatial/codegen/chiselgen/ChiselGenMem.scala:226-292`).
