---
type: coverage
subsystem: Codegen B (sim + alt targets)
paths:
  - "src/spatial/codegen/scalagen/"
  - "src/spatial/codegen/pirgen/"
  - "src/spatial/codegen/roguegen/"
  - "src/spatial/codegen/tsthgen/"
file_count: 76
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

Codegen B bundles four of Spatial's non-Chisel emitters. It sits at the tail of the Spatial pass pipeline, after retiming, banking, and unrolling have finalized the IR (`spatial/Spatial.scala:240-252`). Each emitter walks the post-unroll Spatial IR and prints a target-specific text representation.

The four subdirectories split along two axes. **scalagen** emits Scala simulation code (`ScalaCodegen.scala:14` declares `lang = "scala"`), imports the `emul` runtime, and is gated by `--sim`. **pirgen** emits Plasticine IR (PIR) Scala DSL calls for the Plasticine CGRA backend, gated by `--pir`. **roguegen** emits Python driver scripts for the SLAC Rogue (SURF) runtime — it runs whenever `spatialConfig.target.host == "rogue"` and produces `TopHost.py`, `ConnectStreams.py`, `_AccelUnit.py`. **tsthgen** emits C++ host-side code for the "Tungsten" simulation harness that pairs with PIR.

**Reference-semantics flag**: scalagen is arguably the de facto reference semantics for Spatial. It is the only target that emits a directly executable program backed by the `emul` package (shared FixedPoint/FloatPoint/Bool, `OOB` out-of-bounds tracking, `BankedMemory`, `ShiftableMemory`, `Queue`/`Stack` adapters). Every semantic question — "what does `SRAMBankedRead` return when the address overflows?", "what does `FIFOBankedDeq` do when empty?", "how is `FixRecip` rounded?" — is answered by a readable one-liner in scalagen. Chisel generation has to match these, not the other way around. Any spec effort should treat `ScalaGen*.scala` as the ground truth.

## 2. File inventory

### scalagen (29 files)

| path | one-line purpose |
|------|------------------|
| `spatial/codegen/scalagen/ScalaCodegen.scala` | Base trait; `lang="scala"`, emits `import emul._`, wraps `object Main { def main ... }`, Java-style block chunking via `javaStyleChunk` |
| `spatial/codegen/scalagen/ScalaGenSpatial.scala` | `case class ScalaGenSpatial(IR: State)` — composes all 22 sub-traits; copies `sim.Makefile`, `run.sh`, `build.sbt` dependencies |
| `spatial/codegen/scalagen/ScalaGenBits.scala` | Base bit-manip trait: `Mux`, `OneHotMux`, `PriorityMux`, `DataAsBits`, `BitsAsData`, `DataAsVec`, `VecAsData` |
| `spatial/codegen/scalagen/ScalaGenBit.scala` | `Not/And/Or/Xor/Xnor/BitRandom/TextToBit/BitToText` — remaps `Bit -> Bool` |
| `spatial/codegen/scalagen/ScalaGenFixPt.scala` | All fixed-point ops (+,-,*,/,recip,mod,mul-sat,unb mul, FMA, etc.) delegating to `emul.FixedPoint` and `Number.*` |
| `spatial/codegen/scalagen/ScalaGenFltPt.scala` | All floating-point ops, including `FltIsPosInf/NegInf/NaN` and transcendentals |
| `spatial/codegen/scalagen/ScalaGenVec.scala` | `Vec` as `Array[A]`; `VecAlloc`, `VecApply`, `VecSlice`, `VecConcat` |
| `spatial/codegen/scalagen/ScalaGenText.scala` | `Text -> String`; `TextConcat`, `TextEql`, `TextApply`, `GenericToText` via `emitToString` hook |
| `spatial/codegen/scalagen/ScalaGenVoid.scala` | `Void -> Unit` trivial remap |
| `spatial/codegen/scalagen/ScalaGenVar.scala` | `Var -> Ptr[A]`; `VarNew`, `VarRead`, `VarAssign` |
| `spatial/codegen/scalagen/ScalaGenStructs.scala` | Emits `case class Struct<N>(...)` into `Structs.scala`, mixes in `StructCodegen` |
| `spatial/codegen/scalagen/ScalaGenArray.scala` | Host `Tensor1 -> Array[A]`; `ArrayNew/Apply/Update/Map/ForEach/Reduce/Fold/Filter/FlatMap/ZipMkString` |
| `spatial/codegen/scalagen/ScalaGenSeries.scala` | `SeriesForeach` as a Scala `for ... until ... by ...` |
| `spatial/codegen/scalagen/ScalaGenDebugging.scala` | `PrintIf`, `AssertIf`, `BreakpointIf`, `ExitIf`, `RetimeGate` emission |
| `spatial/codegen/scalagen/ScalaGenFileIO.scala` | CSV + binary file open/read/write, `LoadDRAMWithASCIIText` |
| `spatial/codegen/scalagen/ScalaGenDelays.scala` | `DelayLine` handling — constants skipped (handled by NamedCodegen) |
| `spatial/codegen/scalagen/ScalaGenCounter.scala` | `CounterNew`, `CounterChainNew`, `ForeverNew` — emit `emul.Counter`, `Counterlike`, `Forever` |
| `spatial/codegen/scalagen/ScalaGenControl.scala` | Abstract hooks `emitControlDone`, `emitControlIncrement` |
| `spatial/codegen/scalagen/ScalaGenController.scala` | Emits outer-stream loops, unrolled loops, switches, FSMs, AccelScope; wraps each controller in `object X_kernel { def run(...) }` |
| `spatial/codegen/scalagen/ScalaGenMemories.scala` | Shared memory helpers: `BankedMemory`/`ShiftableMemory` emit, `OOB` wrapper, `flattenAddress`, `emitBankedLoad/Store`, `emitVectorLoad/Store` |
| `spatial/codegen/scalagen/ScalaGenReg.scala` | `Reg`, `ArgIn`, `ArgOut`, `HostIO -> emul.Ptr[A]`; `RegAccumOp` and `RegAccumFMA` dispatch on `AccumAdd/Mul/Max/Min/FMA` |
| `spatial/codegen/scalagen/ScalaGenSRAM.scala` | `SRAMNew`, `SRAMBankedRead`, `SRAMBankedWrite` — delegate to `emitBankedInitMem/Load/Store` |
| `spatial/codegen/scalagen/ScalaGenFIFO.scala` | `FIFO -> scala.collection.mutable.Queue`; `enq/deq/isEmpty/isFull/peek/almostEmpty/almostFull/numel`, `FIFORegNew/Enq/Deq` |
| `spatial/codegen/scalagen/ScalaGenLIFO.scala` | `LIFO -> scala.collection.mutable.Stack`; same op set as FIFO |
| `spatial/codegen/scalagen/ScalaGenRegFile.scala` | `RegFileNew`, shift-in variants, vector read/write, banked shift-in |
| `spatial/codegen/scalagen/ScalaGenLUTs.scala` | `LUTNew`, `LUTBankedRead` via `emitBankedInitMem` + `emitVectorLoad` |
| `spatial/codegen/scalagen/ScalaGenLineBuffer.scala` | `LineBufferNew` + banked enq/read; sets up `lineBufSwappers` map consumed by controller codegen |
| `spatial/codegen/scalagen/ScalaGenDRAM.scala` | `DRAMHostNew`, `SetMem`/`GetMem` copy loops, `FringeDenseLoad/Store/SparseLoad/Store` as stream-driven for-loops, `MemDenseAlias`, `MemSparseAlias` |
| `spatial/codegen/scalagen/ScalaGenStream.scala` | `StreamIn`/`StreamOut` as `emul.StreamIn`/`StreamOut` with `bitsFromString`/`bitsToString` encoders; `StreamInBankedRead`, `StreamOutBankedWrite` |

### pirgen (32 files)

| path | one-line purpose |
|------|------------------|
| `spatial/codegen/pirgen/PIRCodegen.scala` | Base trait; `lang="pir"`, `ext="scala"`, `entryFile="AccelMain.$ext"`, mixes `AccelTraversal`; emits PIR DSL header `object AccelMain extends PIRApp { def staging(top:Top) = ...}` |
| `spatial/codegen/pirgen/PIRGenSpatial.scala` | Top case class — composes PIRGenController/Array/Bits/Bit/FixPt/FltPt/Structs/Text/Debugging/Counter/DRAM/FIFO/Reg/SRAM/Lock/MergeBuffers/Vec/Stream/RegFile/LUTs/SplitGen. Comments out several traits not supported on Plasticine (Void/Var/LIFO/Series/FileIO/Delays) |
| `spatial/codegen/pirgen/PIRFormatGen.scala` | `state(lhs)(rhs)` / `alias(lhs)(rhs)` / `stateOrAlias(...)` core emit primitives; `Lhs(sym, postFix)` wrapper for struct-field subnames; `typeMap` bookkeeping; `emitBlk` helper |
| `spatial/codegen/pirgen/PIRGenHelper.scala` | `stateMem`, `stateStruct`, `stateAccess`, `genOp` helpers; port/mux/bufferport/castgroup/broadcast plumbing; `assertOne` assertion for vector width 1 |
| `spatial/codegen/pirgen/PIRSplitGen.scala` | Splits emitted PIR body into `def split1 = {...}; split1; def split2 = {...}; split2; ...` chunks of `splitThreshold=10` stmts to work around JVM method size; `lookup[tp]("name")` cross-chunk refs |
| `spatial/codegen/pirgen/PIRGenController.scala` | Emits `UnitController`/`LoopController` + `CounterIter`/`CounterValid` per-lane, handles `AccelScope/UnitPipe/ParallelPipe/UnrolledForeach/UnrolledReduce/Switch/SwitchCase`; `StateMachine` => TODO stub |
| `spatial/codegen/pirgen/PIRGenCounter.scala` | `Counter(par=N).min/step/max`, `ForeverNew`, `LaneStaticNew` as `Const(List(...))` |
| `spatial/codegen/pirgen/PIRGenFixPt.scala` | Every fix-op goes through `genOp(lhs)` which prints `OpDef(op=FixAdd).addInput(...).tp(...)` |
| `spatial/codegen/pirgen/PIRGenFltPt.scala` | Same pattern for flt-ops |
| `spatial/codegen/pirgen/PIRGenBit.scala` | Not/And/Or/Xor/Xnor/BitRandom/BitToText via `genOp` |
| `spatial/codegen/pirgen/PIRGenBits.scala` | `Mux`, `OneHotMuxN`, `DataAsBits` (as alias), `BitsAsData` |
| `spatial/codegen/pirgen/PIRGenStructs.scala` | `StructAlloc` flattens to `Lhs(sym, fieldName)`; `FieldApply` becomes `alias` |
| `spatial/codegen/pirgen/PIRGenText.scala` | Text ops via `genOp`, `Text -> Text` remap |
| `spatial/codegen/pirgen/PIRGenDebugging.scala` | `PrintIf`, `AssertIf`, `ExitIf` as PIR-native nodes |
| `spatial/codegen/pirgen/PIRGenReg.scala` | `Reg()`, `argIn`, `hostIO`, `argOut`, `RegReset`, `RegRead`/`Write` via `MemRead`/`MemWrite`, `RegAccumOp`, `RegAccumFMA` |
| `spatial/codegen/pirgen/PIRGenSRAM.scala` | `SRAM()`, `BankedRead/BankedWrite` with `.bank(...)`.offset(...) |
| `spatial/codegen/pirgen/PIRGenFIFO.scala` | `FIFO()` with `.depth(size)`; `MemRead`/`MemWrite`; **errors out** on `isEmpty`/`isFull`/`peek`/`numel`/almostEmpty/almostFull — those are unsupported on Plasticine |
| `spatial/codegen/pirgen/PIRGenLock.scala` | `LockNew`, `LockOnKeys`, `LockSRAMNew/LockDRAMHostNew` as `LockMem(is_dram)`, `LockRead`/`LockWrite` with `.addr(...).lock(...)` |
| `spatial/codegen/pirgen/PIRGenMergeBuffer.scala` | `MergeBuffer(ways, par)` wired via synthesized `inputFIFO`/`outputFIFO`/`boundFIFO`/`initFIFO`; uses `LCA(...)` to place internal ctrl state (`withinCtrl`) |
| `spatial/codegen/pirgen/PIRGenRegFile.scala` | `RegFile()` + BankedRead/Write with `Const(0)` offset vector (most shift variants commented out) |
| `spatial/codegen/pirgen/PIRGenLUTs.scala` | `LUT()`, `FileLUT` via `"file:$filename"` init, `BankedRead` |
| `spatial/codegen/pirgen/PIRGenStream.scala` | `StreamIn/Out` as `FIFO()` + `streamIn(streams, bus)` / `streamOut(...)` calls; quotes `DRAMBus` specially |
| `spatial/codegen/pirgen/PIRGenDRAM.scala` | `DRAM("name").dims(...)`; `DRAMAddress` via `dramAddress(dram)`; `FringeDenseLoad/Store/SparseLoad/Store` with separate streams for offset/size/data/ack |
| `spatial/codegen/pirgen/PIRGenVec.scala` | Enforces `VecAlloc` size 1 (`bug` otherwise); `VecApply(v, 0)` aliases to struct field |
| `spatial/codegen/pirgen/PIRGenLineBuffer.scala` | Unconditionally `error("Plasticine doesn't support LineBuffer")` |
| `spatial/codegen/pirgen/PIRGenLIFO.scala` | `LIFO()` + BankedPop/Push only — all is/numel/peek variants commented out |
| `spatial/codegen/pirgen/PIRGenArray.scala`, `PIRGenVar.scala`, `PIRGenVoid.scala`, `PIRGenFileIO.scala`, `PIRGenSeries.scala`, `PIRGenDelays.scala` | Empty or near-empty trait bodies — host-only constructs don't survive unrolling into PIR; present for composition symmetry with scalagen |

### roguegen (9 files) — Python emitter for SLAC Rogue/SURF runtime

| path | one-line purpose |
|------|------------------|
| `spatial/codegen/roguegen/RogueCodegen.scala` | Base trait; `lang="rogue"`, `ext="py"`, `entryFile="TopHost.$ext"`; copies `synth/scripts`, `synth/build.sbt`, `synth/run.sh`; branches on `KCU1500` target to copy board-specific Makefile and resources |
| `spatial/codegen/roguegen/RogueGen.scala` | Top case class composing `RogueFileGen/Common/Interface/Accel/Debug/Math/Array` (FileIO trait commented out) |
| `spatial/codegen/roguegen/RogueFileGen.scala` | Emits Python preamble for `TopHost.py` and `ConnectStreams.py`; imports `pyrogue`, `axipcie`, `rogue.interfaces.stream`, `numpy`; opens `def execute(base, cliargs):` |
| `spatial/codegen/roguegen/RogueGenCommon.scala` | Tracks `argIns`, `argIOs`, `argOuts`, `frames`, `earlyExits`, `instrumentCounters`, `controllerStack`; `argHandle` for duplicate-name collision handling; type remap coercing all fixed-point types to `double` when fractional bits exist |
| `spatial/codegen/roguegen/RogueGenAccel.scala` | `AccelScope` emits `accel.Enable.set(1); while (done == 0): ...`; traverses UnitPipe/UnrolledForeach/UnrolledReduce/ParallelPipe/Switch/StateMachine for instrumentation counter tallying |
| `spatial/codegen/roguegen/RogueGenInterface.scala` | `ArgInNew/HostIONew/ArgOutNew` as Python assignments; `DRAMHostNew` is explicitly **unsupported**; `StreamInNew/StreamOutNew` bind AxiStream64/256/512 buses to TCP clients; `SetFrame`/`GetFrame` via `sendFrame`/`getFrame`; `_AccelUnit.py` builds `pyrogue.Device` with remote variable offsets aligning with chisel accel interface |
| `spatial/codegen/roguegen/RogueGenMath.scala` | Per-op Python translations (most arithmetic and transcendentals via `math.*`); `Mux(sel,a,b)` -> `a if sel else b` |
| `spatial/codegen/roguegen/RogueGenArray.scala` | Host-array translation using numpy; `MapIndices/ArrayFold/Reduce/Zip/Map/Foreach/FlatMap/Filter/MkString`; also handles `SimpleStruct`/`FieldApply`/`VecAlloc`/`VecApply`/`IfThenElse` |
| `spatial/codegen/roguegen/RogueGenDebug.scala` | Text/print ops (`FixToText`, `FltToText`, `TextConcat`, `PrintIf`) in Python; `VarNew`/`VarRead`/`VarAssign` |

### tsthgen (6 files) — C++ host emitter for "Tungsten" PIR harness

| path | one-line purpose |
|------|------------------|
| `spatial/codegen/tsthgen/TungstenHostCodegen.scala` | Base trait extending `CppCodegen`; `lang="tungsten"`, `ext="cc"`, `entryFile="main.cc"`, output path is `src/` subdir; emits `main()` with `--help`/`--gen-link` handling and `RunAccel()` entry |
| `spatial/codegen/tsthgen/TungstenHostGen.scala` | Top case class composing `TungstenHostGenCommon/Array/Interface/Accel` + reused `CppGenDebug/Math/FileIO` from cppgen |
| `spatial/codegen/tsthgen/TungstenGenCommon.scala` | Overrides remap: `FixPtType(_,d,f)` with f != 0 becomes `float` (d+f ≤ 32) or `double` (≤ 64) — sim uses IEEE 754, not bit-exact fixed-point |
| `spatial/codegen/tsthgen/TungstenHostGenInterface.scala` | Places allocations behind `AllocAllMems()` in a generated `hostio.h`; `DRAMHostNew`/`LockDRAMHostNew` `malloc` with 64-byte burst alignment |
| `spatial/codegen/tsthgen/TungstenHostGenArray.scala` | Emits a packed C++ `struct` with `toString`, `toRaw`, and raw-bits constructor for each `SimpleStruct` encountered |
| `spatial/codegen/tsthgen/TungstenHostGenAccel.scala` | Reuses CppGenAccel for most ops; delegates hardware block to `RunAccel()` |

## 3. Key types / traits / objects

- **`ScalaGenSpatial(IR: State)` / `PIRGenSpatial(IR: State)` / `RogueGen(IR: State)` / `TungstenHostGenSpatial(IR: State)`** — top-level codegen case classes, each composed via `with ...` from their sibling traits.
- **`trait ScalaCodegen extends Codegen with FileDependencies with NamedCodegen`** — `emitHeader` injects `import emul._`; `emitEntry` wraps in `object Main { def main ... }`; `gen(block)` uses `javaStyleChunk` to split large blocks into hierarchical Scala methods.
- **`trait PIRCodegen extends Codegen with FileDependencies with AccelTraversal with PIRFormatGen with PIRGenHelper`** — Critical override: `gen(lhs, rhs)` dispatches host-interface ops to `genAccel` even outside `inHw`.
- **`case class Lhs(sym: Sym[_], postFix: Option[String]=None)`** — enables emitting a family of statements for a single Sym (e.g. `lhs_offset`, `lhs_size`, `lhs_write`).
- **`trait RogueCodegen extends FileDependencies with AccelTraversal`** — Python codegen; note it does **not** extend `Codegen` directly.
- **`trait TungstenHostCodegen extends FileDependencies with CppCodegen`** — reuses the existing cppgen backend.
- **`def stateMem(lhs, rhs, inits, tp, depth)`** — the universal PIR memory emit.
- **`def stateAccess(lhs, mem, ens, data)`** — universal PIR load/store emit.

## 4. Entry points

- `ScalaGenSpatial(state)`, `PIRGenSpatial(state)`, `RogueGen(state)`, `TungstenHostGenSpatial(state)` — sole constructors called from `Spatial.scala:147-160`. They are registered in the pass pipeline via `==>` chains at `Spatial.scala:241-252`.
- Each `Codegen` implements `emitEntry(block: Block[_])`. scalagen wraps in `object Main { def main(...) }`. pirgen just calls `gen(block)` wrapped by the PIR header/footer. roguegen: `gen(block)` inside a `def execute(base, cliargs)` Python function. tsthgen opens a C++ `int main`.
- Copy-dependency entries bring in backend-specific build harnesses.

## 5. Dependencies

**Upstream (consumed)**:
- `argon._` — base `State`, `Sym`, `Op`, `Block`, `Type`, `stm`, `quote`, `src`, `ctx`; `argon.codegen.{Codegen, FileDependencies, StructCodegen}`; `argon.node._`.
- `spatial.lang._` — `Reg`, `SRAM`, `FIFO`, `LIFO`, `DRAM`, `RegFile`, `LUT`, `LineBuffer`, `Counter`, `Bit`, `Vec`, `Text`, `Tensor1`, `Fix`, `Flt`, `StreamIn`, `StreamOut`, `Bits`.
- `spatial.node._` — all Spatial Op case classes.
- `spatial.metadata.*` — `memory._`, `control._`, `access._`, `retiming._`, `types._`, `bounds._`, `CLIArgs`.
- `spatial.util.spatialConfig` — `enableResourceReporter`, `enableInstrumentation`, `enableSim`, `enablePIR`, `enableTsth`, `codeWindow`, `name`, `target`.
- `spatial.traversal.AccelTraversal` — `inAccel`, `inHw`, `visitBlock`, `getReadStreams`, `getWriteStreams`.
- `spatial.codegen.cppgen._` — tsthgen reuses `CppCodegen`, `CppGenAccel`, `CppGenArray`, `CppGenCommon`, `CppGenDebug`, `CppGenMath`, `CppGenFileIO`.
- `spatial.codegen.naming.NamedCodegen` — scalagen mixes in name resolution.
- `emul._` and `emul.implicits._` — the Scala reference runtime referenced in emitted scalagen code.
- `spatial.targets._` — `KCU1500` referenced in roguegen; PIR mode forces target `"Plasticine"`.

**Downstream (consumers)**: The emitted files are consumed by external tooling, not by other Scala source.

## 6. Key algorithms

- **Java-style block chunking**: `ScalaCodegen.gen(b: Block[_])` invokes `javaStyleChunk` to partition symbols into hierarchical objects so the emitted Scala stays under JVM method-size limits.
- **Controller kernelization**: `ScalaGenController.emitControlObject` inlines every AccelScope/UnitPipe/Foreach/Reduce/Switch into its own `object X_kernel { def run(captured inputs): returnTp = if (ens) { body } else null.asInstanceOf[T] }` file.
- **Outer-stream hand-pumped loop**: `ScalaGenController.emitControlBlock` when controller is `isOuterStreamControl` wraps each child in `while (hasItems_parent_child) { visit(child) }` — a HACK to drain streaming inputs.
- **PIR block splitting**: `PIRSplitGen.emitStm` increments a line counter per emitted `val` and starts a new `def splitN = { ... }; splitN` every `splitThreshold = 10` stmts.
- **Merge-buffer plumbing**: `PIRGenMergeBuffer` synthesizes an input FIFO per way, wires `MemWrite` → `MemRead → merger.inputs(way)` inside the LCA of the merge buffer's accesses.
- **OOB-checked memory access**: `ScalaGenMemories.oob` wraps each emitted banked-load/store in `try { body } catch { case err: ArrayIndexOutOfBoundsException => ...}`. This is the canonical OOB semantics.
- **Address flattening**: `ScalaGenMemories.flattenAddress(dims, indices, ofs?)` computes `sum(idx * stride[i]) + ofs`.
- **Banked memory initialization layout**: `ScalaGenMemories.emitBankedInitMem` for `RegFile`/`LUT` emits one flat `ShiftableMemory`, otherwise builds a 2D array of (nBanks × bankDepth) by running `inst.bankSelects` and `inst.bankOffset`.
- **Rogue instrumentation offsets**: `RogueGenCommon.instrumentCounterIndex` + `RogueGenInterface._AccelUnit` compute per-controller AXI register offsets.
- **Tungsten struct compaction**: `TungstenHostGenArray.SimpleStruct` emits a packed C++ struct plus a `toRaw()` bit-concatenation method and a `bits`-constructor for round-tripping with PIR-side opaque bit unions.

## 7. Invariants / IR state read or written

Metadata these emitters **consume**:
- `lhs.schedule`, `lhs.unrollBy`, `lhs.children`, `lhs.toCtrl`, `lhs.isInnerControl`, `lhs.isOuterStreamControl`, `lhs.parent`.
- `lhs.instance`, `lhs.instance.banking`, `lhs.instance.nBanks`, `lhs.instance.totalBanks`, `lhs.instance.bankSelects(mem, is)`, `lhs.instance.bankOffset`, `lhs.instance.depth`, `lhs.constDims`, `lhs.padding`, `lhs.port`, `lhs.port.bufferPort`, `lhs.port.muxPort`, `lhs.port.broadcast`, `lhs.port.castgroup`.
- `lhs.isInnerAccum`, `lhs.isInnerReduceOp` — consumed by `PIRGenHelper.stateMem` to tag PIR accumulators.
- `mem.accesses`, `mem.swappers`, `mem.readers`, `mem.fullname`, `mem.name`, `lhs.stagedSize`, `lhs.readWidths`, `lhs.writeWidths`.
- `lhs.count`, `lhs.barrier`, `lhs.waitFors`, `lhs.progorder` — PIR-only metadata.
- `Expect(par)`, `Expect(size)` — compile-time constants required by PIR hardware nodes.

Metadata these emitters **produce**: none. Codegen is side-effect-only (writes files). They do mutate local codegen-scoped collections.

Invariants assumed:
- All memories have non-None `lhs.instance`, `lhs.constDims`, `lhs.padding`, banking info.
- Every symbol entering codegen has a fully-resolved `schedule`, `unrollBy`, and `port`.
- pirgen assumes every vector has width 1 by the time codegen runs.
- roguegen assumes host-only DRAM usage.

## 8. Notable complexities or surprises

1. **Scalagen is the ground-truth reference semantics.** This deserves a prominent callout in the spec. When two backends disagree, the scalagen emitted behavior wins.
2. **pirgen is more code than scalagen (32 vs 29 files) despite emitting a simpler output.** The overhead comes from three sources: (a) `PIRSplitGen` for working around JVM method-size limits, (b) `PIRFormatGen`/`PIRGenHelper` for the intermediate `Lhs`/struct-field abstraction, and (c) `PIRGenLock` + `PIRGenMergeBuffer` — two Plasticine-specific constructs that have no scalagen analog.
3. **Many pirgen traits are nearly empty** (`PIRGenArray`, `PIRGenVar`, `PIRGenVoid`, `PIRGenFileIO`, `PIRGenSeries`, `PIRGenDelays`) because those constructs are host-only or have been lowered away before codegen.
4. **pirgen errors at codegen for unsupported operations** (e.g. `FIFO.isEmpty`, `LineBufferNew`). These are late-binding compile errors from the user's perspective.
5. **scalagen's outer-stream handling is a documented HACK.**
6. **roguegen treats DRAM as unsupported.** Rogue uses AXI streams exclusively.
7. **roguegen coerces all fixed-point types with fractional bits to `double`.** This is semantically lossy relative to scalagen's bit-exact `FixedPoint`.
8. **tsthgen inherits cppgen**, so ~70% of its behavior lives in sibling cppgen code.
9. **PIRSplitGen's `lookup[tp]("name")` requires PIR-side runtime type lookup** — the generated code isn't standalone Scala; it depends on a PIR DSL `save`/`lookup` pair.
10. **scalagen's `emitStructs` dumps into `Structs.scala`** via `inGen(getOrCreateStream(out, "Structs.scala"))`. This is a single shared output file, not per-kernel.

## 9. Open questions

1. Is scalagen's `--sim` Makefile guaranteed to produce the same numerical outputs across Scala 2.12 vs 2.13?
2. How does pirgen interact with `CounterIterSynchronization`?
3. `PIRGenDelays` is empty — so what happens to `DelayLine` nodes under `--pir`?
4. `RogueGenAccel` puts controllers into `instrumentCounters` only when `inHw` (except AccelScope itself, which is added unconditionally). What's the ordering invariant vs chisel's side of the same AXI register map?
5. Does the `--tsth` path ever run without `--pir`?
6. The commented-out traits in `PIRGenSpatial.scala:14-30` — are these disabled because they're handled upstream, or because they're unimplemented?
7. scalagen's `RegAccumOp` case throws `new Exception("This shouldn't happen!")` for `AccumFMA` and `AccumUnk` — what guarantees those are rewritten away before codegen?

## 10. Suggested spec sections

- `10 - Spec/60 - Backends/scala-sim.md` — scalagen, with subsections for: simulation runtime (`emul` contract), memory OOB behavior, FIFO/LIFO semantics, FixedPoint/FloatPoint rounding, controller kernelization, Java-style chunking. **Primary source of reference semantics.**
- `10 - Spec/60 - Backends/plasticine-pir.md` — pirgen, with subsections for: PIR DSL output shape, `stateMem`/`stateAccess` helpers, Lock/MergeBuffer plumbing, width-1 vector invariant, PIRSplitGen chunking, list of unsupported ops and where they error.
- `10 - Spec/60 - Backends/rogue-python.md` — roguegen, with subsections for: pyrogue/axipcie device model, AXI register map offsets, instrumentation counter readout, AxiStream bus families, target-specific (KCU1500) resource staging.
- `10 - Spec/60 - Backends/tungsten-cpp.md` — tsthgen, with subsections for: relationship to cppgen, struct packing for PIR-host parity, memory alignment rules, allocator separation via `AllocAllMems()`.
- `10 - Spec/60 - Backends/codegen-pipeline.md` — shared section describing the `--sim` / `--synth` / `--pir` / `--tsth` / `rogue` activation matrix.
- `10 - Spec/10 - Semantics/reference-semantics.md` — call out that scalagen is the executable reference and chisel must match. Cite the concrete `ScalaGen*.scala` files as the normative definition for each op family.
- Cross-references into `10 - Spec/30 - Memory/` and `10 - Spec/40 - Control/` for banking/port/buffer metadata touched here.
