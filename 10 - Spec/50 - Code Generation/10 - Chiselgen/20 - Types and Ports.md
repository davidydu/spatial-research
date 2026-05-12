---
type: spec
concept: chiselgen-types-and-ports
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:315-321"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:323-331"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:336-391"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:394-455"
  - "spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:457-480"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStruct.scala:11-14"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:107-123"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:347-358"
  - "spatial/src/spatial/codegen/chiselgen/AppProperties.scala:1-27"
  - "spatial/src/spatial/codegen/chiselgen/RemapSignal.scala:1-34"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[10 - Overview]]"
status: draft
---

# Chiselgen — Types and Ports

## Summary

Chiselgen has to translate Spatial's IR types into a few different Chisel surface forms. The same Spatial `FixPtType(s,d,f)` value can appear in four very different positions in the generated code: as a constant literal, as a wire/register declaration, as a function-argument type passed through Scala kernel modularization, or as a Chisel `IO(new Bundle { … })` port. Chiselgen ships a separate "type remapper" function for each of these positions: `quoteConst`, `remap`, `arg`, and `port`. There is also a fifth helper, `param`, that produces the `(…, …)` payload registered with `ModuleParams.addParams("<sym>_p", …)` so the corresponding bundle's runtime params can be looked up by interface code in another generated file. Two cross-cutting enum sidecars (`AppProperties`, `RemapSignal`) annotate the type system: 23 app-level feature flags fold into a comment in `AccelWrapper.scala`, and 29 controller-signal labels are exported but unused inside this directory.

## Semantics

### The four type-remappers

Each function answers a different question about a Spatial type or symbol:

- `quoteConst(tp, c)` — "How do I print a constant of this type as Chisel literal syntax?"
- `remap(tp)` — "What is the wire/value declaration form?" (used by `Wire(...)`, `RegInit(...)`, etc.)
- `arg(tp, node)` — "What's the bare Scala/Chisel type name when this value is passed through a Scala function?"
- `port(tp, node)` — "How do I declare this as a port inside `IO(new Bundle { … })`, including direction wrapping (`Input`, `Output`, `Flipped`, `Decoupled`)?"

`quoteConst` at `spatial/src/spatial/codegen/chiselgen/ChiselCodegen.scala:315-321` formats `FixPtType(s,d,f)` as `"<c>.FP(s, d, f)"` — with an `"L"` suffix when the integer-decimal sum overflows 32 bits and `f == 0` (Scala's `Int.toLong` literal). `FltPtType(g,e)` becomes `"<c>.FlP(g, e)"`. `BitType()` constants become `"<c.value>.B"`. Strings pass through.

`remap` at lines 323-331 is the data-side counterpart: `FixPtType(s,d,f)` → `"new FixedPoint(s, d, f)"`, `FltPtType(m,e)` → `"new FloatingPoint(m, e)"`, `BitType()` → `"Bool()"`, `Vec[_]` → `"Vec(width, remap(inner))"`. Trait extension is the design lever here. `ChiselGenStruct.remap` at `ChiselGenStruct.scala:11-14` adds a single override:

```scala
override protected def remap(tp: Type[_]): String = tp match {
  case _: Struct[_] => s"UInt(${bitWidth(tp)}.W)"
  case _ => super.remap(tp)
}
```

Structs are erased to packed `UInt`s in the data-side remapper. Field accessors elsewhere reach into specific bit ranges via `getField` at `ChiselGenCommon.scala:180-188`.

### `arg` — function argument types and node-shape dispatch

`arg(tp, node)` at `ChiselCodegen.scala:336-391` is the fattest of the four. Type fan-out: `FixPtType` → `"FixedPoint"` (unless the node is a `FIFODeqInterface`), `FltPtType` → `"FloatingPoint"`, `Bit` → `"Bool"`, `Vec[_]` → `"Vec[<inner>]"`, `Struct[_]` → `"UInt"`, `StreamStruct[_]` → `"StreamStructInterface"`. `Var[_]` → `"String"` (chiselgen never emits real variables).

When the type alone is ambiguous, `arg` switches on the node's RHS at lines 345-389. Memory allocators each map to a specific Chisel interface bundle name: `RegNew` → `"StandardInterface"` (or `"FixOpAccumBundle"` for `AccumAdd`/`Mul`/`Min`/`Max`, `"FixFMAAccumBundle"` for `AccumFMA` — lines 354-356). `RegFileNew` → `"ShiftRegFileInterface"`. `LUTNew`/`SRAMNew` → `"StandardInterface"`. `FIFONew`/`FIFORegNew`/`LIFONew` → `"FIFOInterface"`. `MergeBufferNew` → `"MergeBufferFullIO"`. `DRAMHostNew` → `"FixedPoint"`. `DRAMAccelNew` → `"DRAMAllocatorIO"`. Counter chains return `"CtrObject"` (for `CounterNew`/`ForeverNew`) or `"CounterChainInterface"`.

Streams are keyed by bus type (lines 366-387). `StreamInNew`: `BurstDataBus` → `"DecoupledIO[AppLoadData]"`, `BurstAckBus` → `"DecoupledIO[Bool]"`, `GatherDataBus` → `"DecoupledIO[Vec[UInt]]"`, `ScatterAckBus` → `"DecoupledIO[Bool]"`, `AxiStream{64,256,512}Bus` → `"AXI4Stream"`, fallback → `"DecoupledIO[UInt]"`. `StreamOutNew` mirrors with `"DecoupledIO[AppCommandDense]"`, `"DecoupledIO[AppStoreData]"`, `"DecoupledIO[AppCommandSparse]"`, `"DecoupledIO[ScatterCmdStream]"`. `arg` is also where ArgIn → `"UInt"` and ArgOut/HostIO → `"MultiArgOut"` map.

### `port` — IO directional wrapping

`port(tp, node)` at lines 394-455 is the IO-form of `arg`: same dispatch shape, but each result is wrapped in the Chisel direction qualifier (`Input`, `Output`, `Flipped`, `Decoupled`) for an `IO(new Bundle { … })` declaration. Primitive types: `FixPtType`/`FltPtType` → `"Input(<remap>)"`, `BitType()` → `"Input(Bool())"`, `Vec` → `"Vec(width, port(inner))"`, `Struct[_]` → `"Input(UInt(<bitWidth>.W))"`, `StreamStruct[_]` → `"Flipped(new StreamStructInterface(Map(...)))"` with widths inlined.

For nodes, each interface bundle's parameters are looked up at elaboration time from the `ModuleParams` registry. NBuffered memories: `"Flipped(new NBufInterface(ModuleParams.getParams(\"<sym>_p\").asInstanceOf[NBufParams]))"` (line 406). Non-NBuffered memories: `"Flipped(new <Interface>(ModuleParams.getParams(\"<sym>_p\").asInstanceOf[MemParams]))"` (lines 418-425). Accumulator-specialized registers skip `MemParams` and inline the bundle widths: `FixFMAAccumBundle(numWriters, d, f)` and `FixOpAccumBundle(numWriters, d, f)` (lines 412-417). `MultiArgOut` is sized by the count of non-host writers, not by `MemParams` (lines 408-409). For streams, AXI types use fixed-width literals `"new AXI4Stream(AXI4StreamParameters(W, 8, 32))"` (with `"Flipped(...)"` for `StreamOutNew`); other buses pull widths from `ModuleParams.getParams("<sym>_p")` cast to a tuple type.

### `param` — `ModuleParams.addParams` payloads

`param(node)` at `ChiselCodegen.scala:457-480` returns `Option[String]`, with `None` for nodes that don't need a runtime params lookup. It is called from `createMemObject` at `ChiselGenCommon.scala:347-358` to emit `ModuleParams.addParams("<sym>_p", <payload>)` inside the per-memory `class <lhs> { … }` wrapper (only when `spatialConfig.enableModular` is true). Payload shapes:

- NBuffered memories → `"m.io.np"` — pulls `NBufParams` off the bundle.
- `MergeBufferNew` → `"(m.io.ways, m.io.par, m.io.bitWidth, m.io.readers)"` — a tuple of integers.
- Memory primitives (`isMemPrimitive`) → `"m.io.p"` — pulls `MemParams`.
- `DRAMAccelNew` → `"($node.rank, $node.appReqCount)"` — DRAM allocator dimensions and request count.
- Counter chains (`isCounterChain`) → `"($x<sfx>.par, $x<sfx>.widths)"` — a `(List[Int], List[Int])` for parallelism and widths, with `<sfx>` either empty or `_copy<c>` if the chain belongs to a stream-controller fan-out (line 463).
- `StreamInNew(BurstDataBus)` → `"($x.bits.v, $x.bits.w)"`.
- `StreamOutNew`: `BurstCmdBus` → `"($x.bits.addrWidth, $x.bits.sizeWidth)"`, `BurstFullDataBus` → `"($x.bits.v, $x.bits.w)"`, `GatherAddrBus` → `"($x.bits.v, $x.bits.addrWidth)"`, `ScatterCmdBus` → `"$x.bits.p"`.

The asymmetry with `port` is deliberate. `port` writes the IO declaration that *consumes* params from the registry; `param` writes the payload string that *produces* the params from a memory's instantiation site. Both must agree on the cast type (`MemParams`, `NBufParams`, `(Int, Int)`, etc.).

### `enableModular` — kernel shape toggle

`spatialConfig.enableModular` is a global codegen toggle that selects between two textual forms for every kernel body. Modular off (the legacy form) inlines the controller body inside `kernel()` and references `cchain.head.output.done` directly; modular on (the standard form) emits an inner abstract class `<lhs>_module(depth: Int)` carrying a Chisel `IO(new Bundle)` whose fields are the kernel inputs and the `sigsIn`/`sigsOut` signal bundles, plus a concrete subclass `<lhs>_concrete(depth)` with the body. Three helpers in `ChiselGenCommon` (lines 107-110) encode the difference at the source-string level:

```scala
protected def iodot: String = if (spatialConfig.enableModular) "io." else ""
protected def dotio: String = if (spatialConfig.enableModular) ".io" else ""
protected def cchainOutput: String =
  if (spatialConfig.enableModular) "io.sigsIn.cchainOutputs.head"
  else "cchain.head.output"
protected def cchainCopyOutput(ii: Int): String =
  if (spatialConfig.enableModular) s"io.sigsIn.cchainOutputs($ii)"
  else s"cchain($ii).output"
```

A representative consumer is the `datapathEn`/`break`/`done`/`baseEn`/`mask`/`ctrDone`/`iiDone`/`iiIssue`/`backpressure`/`forwardpressure` accessor bank at `ChiselGenCommon.scala:124-136` — every call to those fields hits `iodot`, so without `enableModular` the body refers to the parent kernel's own `sigsIn` directly, while with it the body refers to `io.sigsIn.<sig>` on the inner module's IO bundle. The `param` registration at `createMemObject` is also gated by `enableModular`: `"ModuleParams.addParams(\"<lhs>_p\", <param.get>)"` is emitted only when modular is on (line 352). The non-modular path side-steps the registry entirely because parameters are visible in lexical scope.

### `ledgerized(node)` — partial-IO discrimination

`ledgerized(node)` at `ChiselCodegen.scala:482-489` answers a third question that's adjacent to but not the same as the type-remapper questions: "is this node going to have its IO partially connected per-controller, requiring a `connectLedger` call instead of a plain `<>` wire?" It returns `true` when:

1. The node is a memory but not a DRAM, ArgIn, or stream (so the typical `Reg`/`SRAM`/`FIFO` etc.).
2. The node is a `DRAMAccel`.
3. The node is a `CtrlBlackbox`.
4. The node is a bound symbol inside a `BlackboxImpl`.
5. The node is a `BlackboxUse`.

This drives the `connectWires<i>` emission at `ChiselGenController.scala:163-177`: ledgerized inputs get `<in>.connectLedger(module.io.in_<in>)` plus follow-up wiring specific to the interface kind (`port.zip(...)` for `MultiArgOut`, `<>` on `output`/`rPort` for special memories). Non-ledgerized inputs get `module.io.in_<in> <> <in>` directly, and counter-chain copies get `input <> input; output <> output` (line 173).

### AppProperties — 23 app-level feature flags

`sealed trait AppProperties` at `AppProperties.scala:1-27` with 23 case objects: `HasLineBuffer`, `HasNBufSRAM`, `HasNBufRegFile`, `HasGeneralFifo`, `HasTileStore`, `HasTileLoad`, `HasGather`, `HasScatter`, `HasLUT`, `HasBreakpoint`, `HasAlignedLoad`, `HasAlignedStore`, `HasUnalignedLoad`, `HasUnalignedStore`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`, `HasBroadcastRead`, `HasAccumSegmentation`, `HasDephasedAccess`, `HasFSM`. These accumulate into `ChiselGenCommon.appPropertyStats: Set[AppProperties]` and are emitted as a single comma-separated comment line in `AccelWrapper.scala` via `ChiselGenController.scala:557`.

### RemapSignal — 29 controller-signal labels

`sealed trait RemapSignal` at `RemapSignal.scala:1-34` with 29 case objects, organized as "Standard Signals" (`En`, `Done`, `BaseEn`, `Mask`, `Resetter`, `DatapathEn`, `CtrTrivial` — lines 5-11) and "non-canonical signals" (`DoneCondition`, `IIDone`, `RstEn`, `CtrEn`, `Ready`, `Valid`, `NowValid`, `Inhibitor`, `Wren`, `Chain`, `Blank`, `DataOptions`, `ValidOptions`, `ReadyOptions`, `EnOptions`, `RVec`, `WVec`, `Latency`, `II`, `SM`, `Inhibit`, `Flow` — lines 13-34). The full list of 29 is exported as a sealed trait, but no use site for `RemapSignal` exists inside the chiselgen subdirectory. See open question Q-cgs-01.

## Interactions

- The four remappers compose via Scala trait linearization: `ChiselCodegen` defines the bases; `ChiselGenStruct` overrides `remap` for `Struct[_]`. New types added to Spatial would need new cases in `quoteConst`, `remap`, `arg`, and `port` simultaneously to be representable.
- `ModuleParams.addParams` is the runtime side of the `port` ↔ `param` contract. The registry is keyed by `"<sym>_p"`. Both sides must agree on the cast type; a mismatch is silent until elaboration.
- `enableModular` interacts with every per-controller emission path (`ChiselGenController`), every memory wrapper (`createMemObject` → `ModuleParams.addParams`), every signal access (`iodot`/`dotio`), and the spatial blackbox path (`SpatialCtrlBlackboxImpl` requires modular to be on, `ChiselGenBlackbox.scala:242`).

## HLS notes

The four-way remapper split is largely an artifact of Chisel's textual generation model: `arg` and `port` differ only because Chisel's `IO` macro requires a directional qualifier that doesn't exist on a Scala parameter. An HLS port can collapse `arg`/`port`/`remap` into a single typed AST node decorated with direction. `param` is more fundamental — it's the late-binding mechanism for memory parameters across separately-compiled files. In an HLS port that emits monolithic C++ templates, the params can be inlined at the call site, making `ModuleParams.addParams` unnecessary.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md`:
- Q-cgs-01: Is `RemapSignal` dead code in the chiselgen subdirectory?
- Q-cgs-02: What sets the unregistered `AppProperties` flags (`HasLineBuffer`, `HasNBufRegFile`, `HasGeneralFifo`, `HasLUT`, `HasStaticCtr`, `HasVariableCtrBounds`, `HasVariableCtrStride`, `HasFloats`, `HasVariableCtrSyms`)?
- Q-cgs-03: Is the non-modular `enableModular = false` path legacy or actively maintained?
