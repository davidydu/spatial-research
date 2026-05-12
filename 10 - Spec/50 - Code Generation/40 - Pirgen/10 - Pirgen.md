---
type: spec
concept: Pirgen Plasticine code generation
source_files:
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-42"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:17-127"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:14-89"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenHelper.scala:14-87"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRSplitGen.scala:10-65"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenController.scala:13-86"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSRAM.scala:10-25"
  - "/Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenFIFO.scala:13-49"
source_notes:
  - "[[other-codegens]]"
hls_status: chisel-specific
depends_on:
  - "[[30 - Cppgen]]"
status: draft
---

# Pirgen

## Summary

Pirgen emits a Scala `PIRApp` for the Plasticine CGRA stack, not an HLS host or RTL backend. `PIRCodegen` declares `lang = "pir"`, `ext = "scala"`, `backend = "accel"`, and `entryFile = "AccelMain.scala"` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:17-27. The requested "32 trait mixins" is not literally active in `PIRGenSpatial`: the directory has a broad set of PIR traits, but the source composite actively extends `PIRCodegen` with controller, array, bits, bit, fixed-point, floating-point, structs, text, debugging, counter, DRAM, FIFO, reg, SRAM, lock, merge-buffer, vec, stream, reg-file, LUTs, and split traits, while `PIRGenVoid`, `PIRGenVar`, `PIRGenLIFO`, `PIRGenSeries`, `PIRGenFileIO`, and `PIRGenDelays` are commented out /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32. This discrepancy is tracked as [[open-questions-other-codegens#Q-oc-01]].

## Syntax or API

The emitted program starts with PIR imports, opens `object AccelMain extends PIRApp`, opens `def staging(top: Top)`, imports `pirgenStaging` and `top._`, and sets `top.name` from the Spatial config /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:63-79. `PIRCodegen.gen` only sends accelerator-scope and hardware-side nodes to `genAccel`; host-side nodes without special cases only recurse through their blocks /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:28-41. Unmatched accelerator nodes emit a comment of the form `// lhs = rhs TODO: Unmatched Node` and then recurse through blocks /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:120-123.

## Semantics

`PIRFormatGen` defines `Lhs(sym, postFix)` so one Spatial symbol can produce multiple named PIR values such as field memories or internal FIFOs /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:14-17. `state(lhs)(rhs)` appends `.sctx`, derives or receives a PIR type string, adds `.name`, `.count`, `.barrier`, `.waitFors`, and `.progorder` metadata when present, and delegates to `emitStm` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:25-50. `alias(lhs)(rhs)` reuses an already emitted `Lhs` and its `typeMap` entry rather than generating a new builder expression /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:52-63. The default statement emitter writes `val <lhs> = <rhs> // comment` and records the PIR type in `typeMap` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:73-76.

## Implementation

`PIRGenHelper.assertOne` throws when a PIR codegen path sees more than one element in a vector-like collection, which is the local enforcement point for single-lane accesses /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenHelper.scala:14-21. `stateMem` adds `.inits`, `.depth`, `.dims`, `.banks`, `.tp`, and `.isInnerAccum` to a memory builder using the Spatial memory instance metadata /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenHelper.scala:23-36. `stateStruct` splits struct-typed memories by field, while `stateAccess` adds `.setMem`, `.en`, optional `.data`, `.port`, `.muxPort`, `.broadcast`, `.castgroup`, and optional `.isInnerReduceOp(true)` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenHelper.scala:38-76. `genOp` emits generic `OpDef(op=...).addInput(...).tp(...)` nodes for arithmetic and logic families /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenHelper.scala:78-87.

`PIRSplitGen` changes every statement to `save("lhs", rhs)`, stores types in `typeMap`, and chunks the emitted staging body after `splitThreshold = 10` statements /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRSplitGen.scala:10-33. It opens splitting inside `emitAccelHeader`, closes it inside `emitAccelFooter`, and rewrites references outside the current chunk to `lookup[type]("name")` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRSplitGen.scala:35-65.

`PIRGenController.emitController` creates `UnitController` or `LoopController` nodes, attaches counter chains, enables, stop conditions, and unroll parallelism, then emits `CounterIter` and `CounterValid` nodes per lane before the block body /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenController.scala:13-52. `AccelScope`, `UnitPipe`, `ParallelPipe`, `UnrolledForeach`, `UnrolledReduce`, and `Switch` are all lowered through `emitController`; `StateMachine` is only a TODO comment /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenController.scala:54-85.

The memory traits reuse helper primitives. SRAM reads and writes use `stateAccess` with `BankedRead` or `BankedWrite` and `assertOne` on bank and offset lanes /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSRAM.scala:10-25. FIFO creation uses `FIFO()` with depth from `Expect(size)`, while FIFO deq/enq use `MemRead` and `MemWrite` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenFIFO.scala:13-49. Lock generation emits `Lock`, `LockOnKeys`, `LockMem(false)`, `LockMem(true)`, `LockRead`, and `LockWrite`, selecting bank or offset as the emitted address /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenLock.scala:10-47. Merge buffers compute the LCA of all accesses, bracket internal reads and writes with `beginState(lca.getCtrl)` and `endState[Ctrl]`, and create internal input, output, bound, and init FIFOs /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenMergeBuffer.scala:17-68.

## Interactions

Pirgen depends on earlier unrolling or rewriting to reduce vectors to width one. `VecApply` calls `bug` and `IR.logBug()` when `i != 0`, and `VecAlloc` calls the same bug path when the element count is not one /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenVec.scala:9-29. `VecSlice` emits `vector.slice(start, end+1)` even though the source comment says "end is non-inclusive," which is tracked as [[open-questions-other-codegens#Q-oc-03]] /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenVec.scala:19-20.

The main Spatial CLI path enables both PIR and Tungsten host generation for `--pir`, disables interpretation, synthesis, and retiming, enables `vecInnerLoop`, switches the target name to `Plasticine`, enables force banking, disables parallel binding, and disables buffer coalescing /Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:307-323. The PIR generator then copies `pir.Makefile`, `run.sh`, `build.sbt`, `build.properties`, and `run_trace.sh` into the generated project dependencies /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:35-41.

## HLS notes

Pirgen is Plasticine-specific and should not be treated as a direct Rust+HLS template. It lowers Spatial nodes to PIR builder calls, not C host calls or HLS pragmas /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRCodegen.scala:63-79 /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRFormatGen.scala:25-76.

## Open questions

`PIRGenFIFO` explicitly calls `error` for `FIFO.isEmpty`, `isFull`, `almostEmpty`, `almostFull`, `peek`, and `numel` /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenFIFO.scala:16-24. `PIRGenLineBuffer` calls `error` for `LineBufferNew`, enqueue, and read, but `PIRGenLineBuffer` is not mixed into `PIRGenSpatial`; see [[open-questions-other-codegens#Q-oc-02]] /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenLineBuffer.scala:13-20 /Users/david/Documents/David_code/spatial/src/spatial/codegen/pirgen/PIRGenSpatial.scala:5-32.
