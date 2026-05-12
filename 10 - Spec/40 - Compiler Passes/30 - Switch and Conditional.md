---
type: spec
concept: switch-and-conditional
source_files:
  - "src/spatial/Spatial.scala:101-104"
  - "src/spatial/Spatial.scala:171-175"
  - "src/spatial/Spatial.scala:185-186"
  - "src/spatial/transform/SwitchTransformer.scala:33-94"
  - "src/spatial/transform/SwitchOptimizer.scala:14-89"
  - "src/spatial/node/Switch.scala:8-69"
  - "src/spatial/metadata/memory/MemoryData.scala:67-78"
  - "src/spatial/metadata/memory/package.scala:289-304"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[10 - Flows and Rewrites]]"
  - "[[50 - Pipe Insertion]]"
status: draft
---

# Switch and Conditional

## Summary

Spatial lowers hardware `IfThenElse` chains into explicit `Switch` and `SwitchCase` nodes before blackbox lowering, and it repeats the switch transformer/optimizer pair later because DSE may introduce new branches (`src/spatial/Spatial.scala:171-175`, `src/spatial/Spatial.scala:185-186`). `SwitchTransformer` is the structural lowering pass, `SwitchOptimizer` removes trivial cases and converts motion-safe value switches into muxes, and `SwitchScheduler` is a custom scheduler that motions all non-`SwitchCase` operations out of the switch body (`src/spatial/transform/SwitchTransformer.scala:52-85`, `src/spatial/transform/SwitchOptimizer.scala:40-82`, `src/spatial/node/Switch.scala:8-29`).

## Pass list and roles

- `SwitchTransformer` enters `AccelScope` and blackbox implementations with the corresponding traversal flags, then rewrites hardware `IfThenElse` to `Switch.op_switch(selects, cases)` (`src/spatial/transform/SwitchTransformer.scala:73-87`).
- `SwitchTransformer.extractSwitches` recursively walks the `else` block when the else block result is another `IfThenElse` and `shouldMotionFromConditional(block.stms, inHw)` allows motion of the condition-computation statements (`src/spatial/transform/SwitchTransformer.scala:52-71`).
- `SwitchOptimizer` marks hot-swap reader/writer relationships before optimizing a `Switch`, then filters disabled selectors, inlines single true/single-case switches, and muxes motion-safe bit-valued cases (`src/spatial/transform/SwitchOptimizer.scala:16-30`, `src/spatial/transform/SwitchOptimizer.scala:40-82`).
- `SwitchScheduler` is part of the node definition, not the transformer; `Switch.op_switch` installs it with `BlockOptions(sched = Some(SwitchScheduler))` before staging the `Switch` (`src/spatial/node/Switch.scala:62-69`).

## Algorithms

`createCase` wraps a case body in `withEns(Set(cond))` and stages `Switch.op_case(f(body))`, so each case body inherits the already-computed selector as an enable (`src/spatial/transform/SwitchTransformer.scala:44-49`). The top-level transform handles `IfThenElse(cond, thenBlk, elseBlk)` only in hardware, transforms `cond` through the current substitution, creates the first case for `cond2`, and starts else-chain extraction with `elseCond = !cond2` (`src/spatial/transform/SwitchTransformer.scala:77-85`).

`extractSwitches` is the else-chain flattener. When the else block itself ends in `IfThenElse(cond, thenBlk, elseBlk)` and motion is allowed, it visits all statements except the nested if result under the previous else-path enable, transforms the nested condition, and builds two path-qualified selectors: `thenCond = cond2 & prevCond` and `elseCond = !cond2 & prevCond` (`src/spatial/transform/SwitchTransformer.scala:57-66`). The source therefore shows AND-gated path conditions, not OR-combined conditions; the wording mismatch is tracked as an open question. When the else block does not match, the whole block becomes the final `prevCond` case (`src/spatial/transform/SwitchTransformer.scala:68-70`).

`Switch.op_switch` stages all case thunks in one `stageScope`, returns the last case result as the switch block result, and then stages `Switch(selects, block)` (`src/spatial/node/Switch.scala:62-69`). `SwitchScheduler` always reports `mustMotion = true`, partitions the switch scope into `keep` operations that are `SwitchCase` nodes and `motion` operations that are not, summarizes effects over only kept impure statements, and returns a `Schedule` whose motion list contains the non-case operations (`src/spatial/node/Switch.scala:8-29`). This means a normal block scheduler is not equivalent for `Switch`; using the wrong scheduler would keep condition-setup statements in the switch body instead of hoisting them (`src/spatial/node/Switch.scala:23-28`).

`SwitchOptimizer` first calls `markHotSwaps(Seq(), bodies(0), bodies(1))` on the first two switch-case bodies (`src/spatial/transform/SwitchOptimizer.scala:40-43`). `markHotSwaps` collects register writers in the first block, finds a nested switch in the second block, records readers in the second block that read either prior hot-swap registers or newly written registers, and updates the memory's `hotSwapPairings` map from reader to conflicting writers (`src/spatial/transform/SwitchOptimizer.scala:16-29`). The metadata comment explains the intended case: an if/else-if chain where the first branch writes a register and a later branch condition reads that register after branch squashing (`src/spatial/metadata/memory/MemoryData.scala:67-78`).

After hot-swap marking, the optimizer transforms selectors with `f(selects)`, zips them with case statements, drops entries whose selector is `Const(FALSE)`, extracts `SwitchCase` ops, and computes the indices of `Const(TRUE)` selectors (`src/spatial/transform/SwitchOptimizer.scala:45-50`). If exactly one selector is true, it inlines that case body; if only one case remains, it inlines that body regardless of selector count (`src/spatial/transform/SwitchOptimizer.scala:57-63`). Otherwise it warns on no true selectors or multiple true selectors, checks every case body with `shouldMotionFromConditional`, and for bit-typed results with motion-safe bodies it inlines each body and emits `mux` for two selectors or `oneHotMux` for more than two (`src/spatial/transform/SwitchOptimizer.scala:64-79`). Non-bit or non-motion-safe switches are restaged as `Switch.op_switch` with thunks that visit each original case statement and return `f(s)` (`src/spatial/transform/SwitchOptimizer.scala:80-82`).

## Metadata produced/consumed

`Switch` consumes selector bits and case-body symbols as inputs, and its aliases are the case body results (`src/spatial/node/Switch.scala:46-58`). The optimizer produces `hotSwapPairings` on the memory being read; the metadata API stores a `Map[Sym[_], Set[Sym[_]]]`, and `substHotSwap` keeps the map consistent when accesses are substituted during memory unrolling (`src/spatial/metadata/memory/package.scala:289-304`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:306-309`). A direct downstream consumer verified in source is the RAW-cycle protection logic, which excludes register writes listed in `reg.hotSwapPairings.getOrElse(reader, Set())` (`src/spatial/util/modeling.scala:474-483`).

## Invariants established

After `SwitchTransformer`, a hardware else-if chain that passes `shouldMotionFromConditional` is represented as one flat `Switch` with one `SwitchCase` per path and selectors already gated by earlier path conditions (`src/spatial/transform/SwitchTransformer.scala:52-85`). After `SwitchOptimizer`, switches with false selectors, a single true selector, or a single surviving case are reduced away, and motion-safe bit-valued switches become mux-style dataflow (`src/spatial/transform/SwitchOptimizer.scala:45-82`). The custom scheduler ensures the block inside a staged `Switch` contains only `SwitchCase` operations as kept statements (`src/spatial/node/Switch.scala:23-28`).

## HLS notes

HLS status is **rework**. The semantic target is simple branch selection, but a Rust+HLS implementation must decide whether to preserve explicit `SwitchCase` nodes, generate mutually exclusive if/else code, or synthesize muxes for motion-safe bit-valued bodies (`src/spatial/transform/SwitchOptimizer.scala:70-82`). The custom scheduler is the main Spatial-specific detail: it motions non-case operations out of the switch body, and a reimplementation needs an equivalent hoisting rule before lowering to HLS control flow (`src/spatial/node/Switch.scala:8-29`). Hot-swap metadata is also compiler-internal and should be revisited with the HLS retiming and RAW-cycle model rather than copied blindly (`src/spatial/metadata/memory/MemoryData.scala:67-78`, `src/spatial/util/modeling.scala:474-483`).

## Open questions

- Q-pp-07 - source code shows AND-gated flattened selectors, while the work order described "pre-OR'd" conditions.
- Q-pp-08 - direct source consumers of `hotSwapPairings` are modeling/retiming and memory unrolling; confirm whether banking or codegen also consumes it indirectly.
