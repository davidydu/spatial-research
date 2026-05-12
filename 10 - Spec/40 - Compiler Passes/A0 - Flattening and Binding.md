---
type: spec
concept: flattening-and-binding
source_files:
  - "src/spatial/transform/FlatteningTransformer.scala:13-117"
  - "src/spatial/transform/BindingTransformer.scala:17-134"
  - "src/spatial/transform/AllocMotion.scala:11-58"
  - "src/spatial/Spatial.scala:112-118"
  - "src/spatial/Spatial.scala:218-222"
source_notes:
  - "[[pass-pipeline]]"
hls_status: clean
depends_on:
  - "[[50 - Pipe Insertion]]"
  - "[[80 - Unrolling]]"
status: draft
---

# Flattening and Binding

## Summary

`FlatteningTransformer` and `BindingTransformer` run as a tight post-rewrite, post-`memoryCleanup` control-shape wave: Spatial invokes `memoryCleanup`, then `flatteningTransformer ==> bindingTransformer`, then `bufferRecompute` (`src/spatial/Spatial.scala:217-222`). The pair is concerned with controller shape, not memory banking itself: flattening removes unnecessary unit-pipe nesting and converts inner-stage switches into mux expressions, while binding wraps consecutive non-conflicting child controllers in `ParallelPipe` groups (`src/spatial/transform/FlatteningTransformer.scala:13-16`, `src/spatial/transform/BindingTransformer.scala:17-19`). `AllocMotion` is a nearby transformer that moves memory/counter allocation nodes to the top of outer `Foreach`/`UnitPipe` blocks, but current `Spatial.scala` only constructs it as a lazy val and does not include it in the visible `runPasses` chain, which is tracked as Q-pp-15 (`src/spatial/Spatial.scala:118`, `src/spatial/Spatial.scala:164-235`).

## Pass list and roles

`FlatteningTransformer` has three source-visible jobs. First, when it visits an inner controller or a controller body containing an inner stage, it transforms those blocks with `flattenSwitch = true`; any `Switch` encountered in that mode is converted to a `mux` for two selectors, `oneHotMux` for larger bit-typed switches, `void` for void switches, or an ordinary `Switch.op_switch` for non-bit values (`src/spatial/transform/FlatteningTransformer.scala:21-37`, `src/spatial/transform/FlatteningTransformer.scala:85-96`). Second, for an outer control with exactly one child, it can delete a single non-stream `UnitPipe` child and inline that child into the parent when the child inputs are not needed by the parent block and neither side is stream/blackbox/unrolled-PIR protected (`src/spatial/transform/FlatteningTransformer.scala:47-66`, `src/spatial/transform/FlatteningTransformer.scala:98-107`). Third, for an outer `UnitPipe` parent with a single child, it can delete the parent and inline the child directly under the parent context, again guarded by the same parent-needed, stream, blackbox, and unroll checks (`src/spatial/transform/FlatteningTransformer.scala:67-78`).

`BindingTransformer` works after flattening. It precomputes child groups left-to-right, then rewrites each block by replaying statements in original order and replacing any group with more than one controller by a `ParallelPipe(Set.empty, ...)` (`src/spatial/transform/BindingTransformer.scala:21-66`, `src/spatial/transform/BindingTransformer.scala:68-91`). The transformer applies this grouping to outer pipe/seq `UnrolledForeach`, outer pipe/seq `UnrolledReduce`, void-valued outer `SwitchCase`, and outer `AccelScope` blocks, but only when `spatialConfig.enableParallelBinding` is true and there is more than one child (`src/spatial/transform/BindingTransformer.scala:93-120`). The CLI flag `--noBindParallels` clears that config bit (`src/spatial/Spatial.scala:364-366`).

## Algorithms

Flattening's switch path is block-local: `transformCtrl` pre-visits only bodies that are already inner stages or belong to inner controllers, registers transformed block substitutions, and then mirrors the controller with those substitutions in place (`src/spatial/transform/FlatteningTransformer.scala:21-38`). The same `flattenSwitch` mode is forced through `SpatialBlackboxImpl` function blocks, so a Spatial blackbox body can also have switch values flattened while the transformer is in blackbox scope (`src/spatial/transform/FlatteningTransformer.scala:39-45`, `src/spatial/transform/FlatteningTransformer.scala:110-112`). The child-delete path uses `deleteChild` as a dynamic flag: while the parent body is transformed, any nested `Control` seen in that mode inlines its blocks and returns `void`, with an exception that preserves the flag while recursively deleting the exact single-UnitPipe nesting case (`src/spatial/transform/FlatteningTransformer.scala:54-65`, `src/spatial/transform/FlatteningTransformer.scala:98-107`).

Binding starts each parent with group 0 containing the first child, plus two rolling memory sets: `prevMems` for previous reads/writes/transient reads and `prevWrMems` for previous writes (`src/spatial/transform/BindingTransformer.scala:21-29`). For each next child, it computes `activeMems`, `addressableMems = (activeMems ++ prevMems).filter(!_.isSingleton).filter(!_.isDRAM)`, and `activeWrMems`; a new group starts if previous and active memory sets overlap through a write or non-singleton non-DRAM addressable memory, or if `shouldNotBind`, stream, first-child stream, or breakWhen boundaries fire (`src/spatial/transform/BindingTransformer.scala:30-42`). If no conflict fires, the child is appended to the current group; in both cases the rolling memory sets are updated after the decision, so the algorithm never reorders children or looks ahead past a boundary (`src/spatial/transform/BindingTransformer.scala:52-61`, `src/spatial/transform/BindingTransformer.scala:72-87`).

`AllocMotion` is simpler: inside accelerator scope, it only rewrites outer `Foreach` and `UnitPipe` controls; it registers every block to `motionAllocs`, which stages all movable memory allocations, counters, and counter chains before visiting all other statements in original order (`src/spatial/transform/AllocMotion.scala:14-22`, `src/spatial/transform/AllocMotion.scala:28-57`). `canMove` returns true for memories, counters whose inputs are movable, and counter chains whose counters are movable (`src/spatial/transform/AllocMotion.scala:28-33`).

## Metadata produced/consumed

Flattening consumes control-level metadata such as `isInnerControl`, `isInnerStage`, `isOuterControl`, `children`, `isUnitPipe`, `isStreamControl`, `isCtrlBlackbox`, and `unrollBy` to guard inlining and switch flattening (`src/spatial/transform/FlatteningTransformer.scala:21-31`, `src/spatial/transform/FlatteningTransformer.scala:47-68`). Binding consumes nested memory summaries (`nestedWrittenMems`, `nestedWrittenDRAMs`, `nestedReadMems`, `nestedReadDRAMs`, `nestedTransientReadMems`), stream ancestry, `shouldNotBind`, `breaker`, and memory singleton/DRAM classifications when it chooses group boundaries (`src/spatial/transform/BindingTransformer.scala:26-42`). Both passes preserve existing metadata on newly staged controls through `stageWithFlow`/`transferData` where the source explicitly creates replacement controls (`src/spatial/transform/BindingTransformer.scala:93-120`).

## Invariants established

After flattening, inner-stage bit-valued switches are represented as muxes rather than control switches, and eligible single-child non-stream/non-blackbox unit-pipe nesting is inlined away (`src/spatial/transform/FlatteningTransformer.scala:85-107`). After binding, consecutive sibling controls that are memory-independent under the pass's conservative grouping rule can be executed under a `ParallelPipe`, while stream, break, and `shouldNotBind` boundaries remain sequential because they force new groups (`src/spatial/transform/BindingTransformer.scala:35-42`, `src/spatial/transform/BindingTransformer.scala:80-83`).

## HLS notes

These patterns are mostly clean for HLS: switch-to-mux conversion maps to expression selection, unit-pipe inlining maps to block flattening, and binding maps to grouping independent adjacent stages for parallel scheduling (`src/spatial/transform/FlatteningTransformer.scala:85-96`, `src/spatial/transform/FlatteningTransformer.scala:47-78`, `src/spatial/transform/BindingTransformer.scala:68-91`). The main HLS caution is that Spatial's binding legality is metadata-driven and conservative around streams and breakWhen memories; an HLS implementation should preserve those boundaries rather than relying only on syntactic independence (`src/spatial/transform/BindingTransformer.scala:35-42`).

## Open questions

Q-pp-15 asks whether `AllocMotion` is intentionally out of the canonical chain or is a stale pass: the transformer exists and has concrete behavior, but the current pipeline constructs it without invoking it in `runPasses` (`src/spatial/Spatial.scala:118`, `src/spatial/transform/AllocMotion.scala:11-58`).
