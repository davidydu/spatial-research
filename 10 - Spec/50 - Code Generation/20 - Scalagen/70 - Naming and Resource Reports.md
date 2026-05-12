---
type: spec
concept: Naming and resource reports
source_files:
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:13-110"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:1-25"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:1-35"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:17-198"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-161"
source_notes:
  - "[[other-codegens]]"
hls_status: unknown
depends_on:
  - "[[20 - Scalagen]]"
status: draft
---

# Naming and Resource Reports

## Summary

`NamedCodegen` is the naming policy trait under `src/spatial/codegen/naming`; it overrides `named(s, id)` so generated symbols carry Spatial roles such as controller kind, memory kind, access kind, or arithmetic kind instead of only Argon node ids /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:13-23. The naming directory appears to contain only this file (inferred, unverified). Source shows `NamedCodegen` is mixed into `ScalaCodegen`, `ChiselCodegen`, `ResourceReporter`, and `ResourceCountReporter`; `TreeGen` extends `AccelTraversal with argon.codegen.Codegen` directly, so it does not receive this naming policy /Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaCodegen.scala:1-25 /Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:1-35 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:17-24 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-21 /Users/david/Documents/David_code/spatial/src/spatial/codegen/treegen/TreeGen.scala:19-27. The prompt omitted `ScalaCodegen` from the mixin list; this is tracked as [[open-questions-other-codegens#Q-oc-04]].

## Syntax or API

`local(s)` returns the raw symbol string without scoped lookup, and `memNameOr` builds memory names from the symbol, `nameOr(default)`, and any explicit name with `Const`, quotes, and closing parens stripped /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:15-21. Controller nodes receive names that encode inner/outer status and kind: `AccelScope` becomes `<sym>_inr_RootController<name>` or `<sym>_outr_RootController<name>`, `UnitPipe` becomes `<sym>_inr_UnitPipe<name>` or outer, `UnrolledForeach` becomes `<sym>_inr_Foreach<name>` or outer, `UnrolledReduce` becomes reduce, `Switch` becomes switch, and `StateMachine` becomes FSM /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:23-31. Counters become `<sym>_ctr` and counter chains become `<sym>_ctrchain` /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:32-33.

## Semantics

Memory names encode memory role and user names. `RegNew`, `FIFORegNew`, `RegFileNew`, `LineBufferNew`, `FIFONew`, and `LIFONew` all route through `memNameOr`, while `SRAMNew` appends `"sram"` and may append `_dualread` when dual-read configuration or metadata applies /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:37-48. Access names encode operations such as set/get, reg read/write, FIFOReg enqueue/dequeue, SRAM read/write, merge-buffer enqueue/dequeue, FIFO status and numel, and LIFO push/pop/status/numel /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:50-79. Vector, struct, arithmetic, blackbox, and constant delay-line cases get special names before falling back to `super.named(s, id)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:81-106.

## Implementation

`ResourceArea` is an additive record of LUT, Reg, BRAM, and DSP estimates; its `and` method adds each corresponding field and its `toString` renders those four categories /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:17-20. `ResourceReporter` extends `NamedCodegen with FileDependencies with AccelTraversal`, declares `lang = "reports"` and `ext = "json"`, and traverses only from `AccelScope` to estimate hardware area /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-29 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:183-194.

`ResourceReporter.estimateMem` computes memory cost from Spatial memory metadata. It reads `depth`, dimensions, banking factors, alphas, physical bank counts, padding factors, and effective `nBanks`, treating LUTs and RegFiles as dimension-banked /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:60-69. It builds read and write histograms by pairing `residualGenerators` with `port.broadcast`, filtering to non-broadcast lanes, expanding each residual generator by bank count, multiplying lane widths into a muxwidth bin, and counting lanes per bin /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:70-74. It then passes the flattened histogram to `AreaEstimator.estimateMem` for LUTs, FFs, RAMB18, and RAMB32 across SRAM, RegFile, LineBuffer, FIFO, and fallback memory cases /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:76-103. For `RegNew`, it returns `ResourceArea(0,1,0,0)` directly /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:97-98.

`estimateArea` recursively enters controls with `inCtrl`, sums child areas, estimates `MemAlloc` nodes through `estimateMem`, and counts fixed-point arithmetic nodes such as `FixMul`, `FixDiv`, `FixMod`, `FixSub`, `FixAdd`, `FixFMA`, and `FixToFix` through `AreaEstimator.estimateArithmetic` calls /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:107-180. The emitted report is text-like despite `ext = "json"` because it emits lines such as `Controller:`, per-node summaries, and `Total area` rather than building JSON objects /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:41-48 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:183-190.

`ResourceCountReporter` is the JSON-shaped count reporter. It extends `NamedCodegen with FileDependencies with AccelTraversal`, sets `lang = "reports"` and `ext = "json"`, and inherits the base `Codegen` default `entryFile = "Main.$ext"`, so its generated file path is `reports/Main.json` under the codegen output root /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-24 /Users/david/Documents/David_code/spatial/argon/src/argon/codegen/Codegen.scala:10-16. Its header emits `{`, its footer emits one dictionary per memory type from `dataMap`, and then emits `"fixed_ops": <count>` /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:32-58. `emitMem` stores each memory entry as bit width, dimensions, padding, and depth under a type key such as `"bram"` or `"reg"` /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:60-63. `countResource` maps SRAM, FIFO, LIFO, LineBuffer, and RegFile to `"bram"`, maps Reg, FIFOReg, LUT, and MergeBuffer to `"reg"`, and increments `fixOp` for a broad set of fixed-point arithmetic, comparison, conversion, random, transcendental, and FMA operations /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:85-104 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:105-156.

## Interactions

The main Spatial pipeline runs `resourceReporter` when `spatialConfig.reportArea` is true and `ResourceCountReporter(state)` when `spatialConfig.countResources` is true /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:249-250. Because both reporters mix in `NamedCodegen`, their output keys and diagnostic lines can use the same names as Chisel and Scala codegen for many controls and memories /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:22-24 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-21.

## HLS notes

For Rust+HLS, `NamedCodegen` is useful as a stable naming policy only if the rewrite preserves Spatial symbol roles; its current cases are tied to old Spatial op classes and would need a Rust enum or trait equivalent /Users/david/Documents/David_code/spatial/src/spatial/codegen/naming/NamedCodegen.scala:23-106. The resource reporters are diagnostic models rather than host or accelerator codegens, and their HLS status is unknown because the area estimator calls are target/model-specific /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceReporter.scala:76-103 /Users/david/Documents/David_code/spatial/src/spatial/codegen/resourcegen/ResourceCountReporter.scala:85-156.

## Open questions

See [[open-questions-other-codegens#Q-oc-04]] for the source/request mismatch on ScalaCodegen and [[open-questions-other-codegens#Q-oc-08]] for the `ResourceReporter` text-in-`.json` output question.
