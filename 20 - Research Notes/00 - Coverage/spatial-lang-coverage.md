---
type: coverage
subsystem: Spatial language surface
paths:
  - "src/spatial/lang/"
  - "src/spatial/dsl.scala"
  - "src/spatial/Spatial.scala"
  - "src/spatial/SpatialApp.scala"
  - "src/spatial/SpatialConfig.scala"
file_count: 62
date: 2026-04-21
verified:
  - 2026-04-21
---

## 1. Purpose

This subsystem is the **user-facing DSL surface** of Spatial. It defines the Scala types, objects, macro entry points, and implicit conversions that application writers actually type (e.g. `Accel`, `Foreach`, `Reduce`, `DRAM`, `SRAM`, `FIFO`, `Reg`). It sits at the *frontmost* layer of the Spatial compilation pipeline: applications inherit `SpatialApp`, which mixes in `Spatial` (the compiler driver) and Argon's `DSLApp`, and import from either `spatial.dsl` or `spatial.libdsl` to get all the symbols in scope. When the user writes `Foreach(0 until N){ i => ... }`, these files translate that surface syntax into staged IR node allocations (in `spatial.node.*`) that the rest of the pipeline then analyzes, transforms, and code-generates. The layer is deliberately thin: most control/mem classes are `@api` wrapper methods that `stage(...)` a node and sometimes attach metadata via `stageWithFlow`.

## 2. File inventory

| Path | One-line purpose |
|------|------------------|
| `src/spatial/dsl.scala` | Defines `trait SpatialDSL`; `object dsl` (with Scala name shadowing) and `object libdsl` (library view); hosts `@spatial`, `@struct`, `@streamstruct` macro annotation classes. |
| `src/spatial/Spatial.scala` | `trait Spatial extends Compiler`: the compiler driver. Declares all passes (analyzers, transformers, codegens), the `runPasses` pipeline DAG, CLI option definitions (`defineOpts`), target resolution (`settings`). |
| `src/spatial/SpatialApp.scala` | One-liner: `trait SpatialApp extends Spatial with DSLApp`. Application entry trait. |
| `src/spatial/SpatialConfig.scala` | `class SpatialConfig extends argon.Config`: mutable compiler flags (targetName, dseMode, enableSim/Synth/PIR/Tsth, banking effort knobs, retiming, stream/unroll toggles, scalaExec, etc.) plus `copyTo`. |
| `src/spatial/lang/package.scala` | `package object lang extends api.StaticAPI_Internal`. |
| `src/spatial/lang/Aliases.scala` | `InternalAliases`, `ExternalAliases`, `ShadowingAliases` traits — the name-for-name mapping from `spatial.lang.X` to what the user sees (also shadows `Int`/`Float`/`Boolean`/etc. with `argon.lang.Fix`/`Flt`/`Bit`). |
| `src/spatial/lang/api/package.scala` | `package object api extends ExternalAliases`. |
| `src/spatial/lang/api/StaticAPI.scala` | Layered application-view traits: `StaticAPI_Internal`, `StaticAPI_External`, `StaticAPI_Frontend`, `StaticAPI_Shadowing`. These compose all the per-topic API traits below. |
| `src/spatial/lang/api/Implicits.scala` | Implicit conversions (Reg auto-read, Wildcard→Counter, Series→Counter, `IntParameters` for `1 (1 -> 5)` param syntax, `:+=`/`:-=`/`:*=` on Reg, Bit↔Fix casts). |
| `src/spatial/lang/api/ControlAPI.scala` | `SymbolOps` implicit that names a block of code via `NamedClass`. |
| `src/spatial/lang/api/ArrayAPI.scala` | `flatten` for nested Tensor1[Tensor1[A]]; `charArrayToString`. |
| `src/spatial/lang/api/MathAPI.scala` | `sum`, `product`, `reduce`, `min`/`max`/`pow`/`abs`/`exp`/`ln`/`sqrt`/`sin`/`cos`/... plus Taylor-expansion helpers (`exp_taylor`, `log_taylor`, `sqrt_approx`). Also `SeqMathOps` (`reduceTree`, `sumTree`). |
| `src/spatial/lang/api/MiscAPI.scala` | `void`, `*` (Wildcard), `retimeGate`, `retime(delay,payload)`, Text `map`/`toCharArray`. |
| `src/spatial/lang/api/MuxAPI.scala` | `mux(s,a,b)`, `oneHotMux`, `priorityMux`. |
| `src/spatial/lang/api/PriorityDeqAPI.scala` | `priorityDeq`, `roundRobinDeq` implementations over FIFO lists. |
| `src/spatial/lang/api/ShuffleAPI.scala` | `compress` (stages `ShuffleCompress`). |
| `src/spatial/lang/api/SpatialVirtualization.scala` | Scala-virtualized `__newVar`, `__assign`, `__ifThenElse`, `__whileDo` (disabled), `__return` (disabled), `__throw`. |
| `src/spatial/lang/api/DebuggingAPI.scala` | `DebuggingAPI_Internal`/`_Shadowing`: `printArray`/`printMatrix`/`printTensor3-5`, `printSRAM1-3`, `approxEql`, `checkGold`, the `r"..."` string interpolator, unstaged `If`/`IfElse`, `sleep`. |
| `src/spatial/lang/api/FileIOAPI.scala` | `parseValue`, `loadConstants`, CSV open/read/write (`openCSV`, `readTokens`, `writeTokens`, `loadCSV1D/2D`, `writeCSV1D/2D`), binary file ops, `loadNumpy1D/2D`, `loadDRAMWithASCIIText`. |
| `src/spatial/lang/api/TensorConstructorAPI.scala` | `Tensor1Constructor` … `Tensor5Constructor` (`(r) apply func`, `foreach` over ranges). |
| `src/spatial/lang/api/TransferAPI.scala` | `setArg`, `getArg`, `setMem`/`getMem`/`getMatrix`/`getTensor3-5`, `setFrame`/`getFrame`, LockDRAM variants. |
| `src/spatial/lang/api/UserData.scala` | `bound.update(x, bound)` sets `UpperBound` metadata. |
| `src/spatial/lang/control/Control.scala` | Core schedule directives: `abstract class Directives`, `Pipe`/`Stream`/`Sequential` classes (+ their `II`/`POM`/`MOP`/`NoBind`/`haltIfStarved` builders), singleton objects `Accel`/`Foreach`/`Reduce`/`Fold`/`MemReduce`/`MemFold`/`Pipe`/`Sequential`/`Stream`/`Named`. |
| `src/spatial/lang/control/CtrlOpt.scala` | `case class CtrlOpt(name, sched, ii, stopWhen, mop, pom, nobind, haltIfStarved)` with `set[A](x)` applier. |
| `src/spatial/lang/control/AccelClass.scala` | `AccelClass` with `apply(scope: => Any)` that stages `AccelScope(stageBlock{...})`, and a `apply(wild)(scope)` that wraps in `Stream.Foreach(*)`. |
| `src/spatial/lang/control/ForeachClass.scala` | `ForeachClass`: overloads 1–N counters; stages `OpForeach(Set.empty, cchain, block, iters, stopWhen)`. |
| `src/spatial/lang/control/ReduceClass.scala` | `ReduceLike` trait; `ReduceAccum` (implicit accum reg, stages `OpReduce`); `ReduceConstant` (zero/fold literal); `ReduceClass`/`FoldClass`. |
| `src/spatial/lang/control/MemReduceClass.scala` | `MemReduceAccum`, `MemReduceClass`, `MemFoldClass`: stages `OpMemReduce` over nested `mapBlk`/`redBlk`/`resLd`/`accLd`/`accSt` lambdas. |
| `src/spatial/lang/control/Parallel.scala` | `object Parallel.apply(scope)` stages `ParallelPipe`. |
| `src/spatial/lang/control/FSM.scala` | `FSM.apply(init)(notDone)(action)(next)` stages `StateMachine`. |
| `src/spatial/lang/control/NamedClass.scala` | `NamedClass(name)` extending `Directives`, exposing `.Accel`/`.Pipe`/`.Stream`/`.Sequential` with the name attached. |
| `src/spatial/lang/control/SpatialModuleClass.scala` | Skeleton for a (currently commented-out) `SpatialModuleScope`. |
| `src/spatial/lang/types/Mem.scala` | Root memory typeclass traits: `Mem`, `TensorMem`, `RemoteMem`, `LocalMem`, `LocalMem0-5`, `Mem1-5`, `MemN`, `ReadMem1-5`. Defines `__read`/`__write`/`__reset`, dense `apply(row,col)`/`(r,c)` slicing that stages `MemDenseAlias`, and `load`/`alignload`/`gather` that stage `DenseTransfer`/`SparseTransfer`. |
| `src/spatial/lang/host/Array.scala` | Host `Array[A]` (aka `Tensor1`): `length`, `apply`, `update`, `foreach`, `map`, `zip`, `reduce`, `fold`, `filter`, `flatMap`, `mkString`, `reshape`, `toeplitz`, concat `++`. `Array` companion: `tabulate`, `fill`, `empty`, `apply(elems*)`, `fromSeq`. |
| `src/spatial/lang/host/Matrix.scala` | Host `Matrix[A]` (aka `Tensor2`) as `Struct` with `data`/`rows`/`cols`; `apply(i,j)`, `flatten`, `t`, `reorder`, `tabulate`. |
| `src/spatial/lang/host/Tensor3.scala`, `Tensor4.scala`, `Tensor5.scala` | Same pattern for 3/4/5-dim host tensors, each a `Struct` with `data`+per-dim fields, `apply`, `update`, `map`, `zip`, `reduce`, `reorder`, `tabulate`, `fill`. |
| `src/spatial/lang/host/CSVFile.scala`, `BinaryFile.scala` | Tiny `@ref class` shells extending `Top`/`Ref` for file handles (consumed by `FileIOAPI`). |
| `src/spatial/lang/host/TensorData.scala` | `case class TensorData(shape, data)` — runtime companion struct. |
| `src/spatial/lang/DRAM.scala` | `abstract class DRAM[A,C]` (extends `RemoteMem` + `TensorMem`); concrete `DRAM1-5` and `DRAMSparseTile`; `DRAM.apply` stages `DRAMHostNew`, `.alloc` stages `DRAMAlloc`, `.store` stages `DenseTransfer`, sparse views stage `MemSparseAlias`. |
| `src/spatial/lang/SRAM.scala` | `abstract class SRAM[A,C]`; `SRAM1-5` and `SRAMN`; dozens of tuning flags (`.buffer`, `.nonbuffer`, `.hierarchical`, `.flat`, `.fullfission`, `.nofission`, `.nBest`, `.alphaBest`, `.blockcyclic_Bs`, `.effort`, `.bank`, `.forcebank`, `.fullybanked`, `.dontTouch`, `.conflictable`, etc.). `SRAM.apply` stages `SRAMNew`. |
| `src/spatial/lang/FIFO.scala` | `@ref class FIFO`: `enq`/`deq`/`peek`/`isEmpty`/`isFull`/`numel`/`enqVec`/`deqVec`/`deqInterface`; `.conflictable`, `.noduplicate`, `.resize`. `FIFO.apply` stages `FIFONew`. |
| `src/spatial/lang/LIFO.scala` | `@ref class LIFO`: `push`/`pop`/`peek`/status flags. `LIFO.apply` stages `LIFONew`. |
| `src/spatial/lang/Reg.scala` | `@ref class Reg`, `FIFOReg`; `:=`, `.value`, `.reset`, `.buffer`/`.nonbuffer`/`.conflictable`/`.dontTouch`. Plus `object ArgIn`, `ArgOut`, `HostIO`. |
| `src/spatial/lang/RegFile.scala` | `abstract class RegFile[A,C]` + `RegFile1-3`; `<<=` shift-in, `<<=` vector shift-in, `RegFileView(s, addr, axis)`. |
| `src/spatial/lang/LineBuffer.scala` | `@ref class LineBuffer`: `apply(row,col)`, `enqAt`, `load(DRAM1)`. Strided variant via `LineBuffer.strided`. |
| `src/spatial/lang/LockMem.scala` | `LockDRAM`/`LockDRAM1`, `LockSRAM`/`LockSRAM1`, `Lock`/`LockWithKeys`. Read/write with optional `Option[LockWithKeys[I32]]` argument. |
| `src/spatial/lang/LUT.scala` | `abstract class LUT[A,C]` + `LUT1-5`; `apply` from literal elements, `fromSeq`, `fromFile` (CSV at compile time), separate `FileLUT` that stages `FileLUTNew`. |
| `src/spatial/lang/MergeBuffer.scala` | `@ref class MergeBuffer`: `enq(way,data)`, `bound`, `init`, `deq`. Auto-sets `isWriteBuffer` and `isMustMerge`. |
| `src/spatial/lang/Counter.scala` | `@ref class Counter[A:Num]`; `Counter(start,end,step,par)` and `Counter.from(series)`. |
| `src/spatial/lang/CounterChain.scala` | `@ref class CounterChain`; `CounterChain(ctrs: Seq[Counter[_]])`. |
| `src/spatial/lang/Frame.scala` | Stream-only off-chip memory (AXI4-Stream). `Frame1` supports `.store[Local]` → `FrameTransmit`. |
| `src/spatial/lang/Blackbox.scala` | `SpatialBlackbox`, `SpatialCtrlBlackbox`; `Blackbox.SpatialPrimitive`, `SpatialController`, `VerilogPrimitive`, `VerilogController`, `GEMM` (others stubbed). `BlackboxConfig` metadata attached per-use. |
| `src/spatial/lang/StreamIn.scala`, `StreamOut.scala` | `@ref class StreamIn/StreamOut`: `.value()`/`:=` plus Bus-based constructors. |
| `src/spatial/lang/StreamStruct.scala` | `trait StreamStruct` — a struct where each field read is a `FieldDeq` on the matching stream. |
| `src/spatial/lang/Bus.scala` | `case class Pin`, `abstract class Bus`; `PinBus`, `AxiStream64/256/512`+`AxiStream*Bus`, `FileBus`, `FileEOFBus`, `BurstCmd`/`IssuedCmd`, `BurstCmdBus`, `BurstDataBus`, `GatherAddrBus`, `ScatterCmdBus`, etc. |
| `src/spatial/lang/Latency.scala` | `object ForcedLatency.apply(latency)(block)` — wraps a `withFlow` that sets `x.forcedLatency`. |
| `src/spatial/lang/Wildcard.scala` | `class Wildcard` — single-line sentinel type for the `*` wildcard syntax. |
| `src/spatial/lang/Box.scala` | `abstract class Box[A]` — tiny helper base for self-referencing typed refs. |

## 3. Key types / traits / objects

### Traits that form the app writer's view

- **`StaticAPI_Internal` / `StaticAPI_External` / `StaticAPI_Frontend` / `StaticAPI_Shadowing`** (`src/spatial/lang/api/StaticAPI.scala:7-36`). Composed stack of mixins. `SpatialDSL` at `dsl.scala:6` extends `StaticAPI_Frontend`; `object dsl` additionally mixes `StaticAPI_Shadowing` (Scala `Int`→`Fix[TRUE,_32,_0]` etc., per `Aliases.scala:156-197`).
- **`InternalAliases`** (`Aliases.scala:7-52`), **`ExternalAliases`** (`Aliases.scala:58-153`), **`ShadowingAliases`** (`Aliases.scala:156-198`). These provide the `type` and `lazy val` aliases that let users write `Accel`, `Foreach`, `DRAM`, `Counter`, etc. without qualifying them. `ShadowingAliases` is the subtle piece: it redefines Scala's `Int`, `Float`, `Boolean`, `String`, `Array` as Argon/Spatial staged types, plus opens a nested `object gen` with the real Scala names for escape hatches.

### Control directives
- **`abstract class Directives(options: CtrlOpt)`** (`control/Control.scala:9-20`). Super for everything that staging control wrappers. Exposes lazy `Foreach`/`Reduce`/`Fold`/`MemReduce`/`MemFold` builders plus a protected `unit_pipe(func, ens, stopWhen)` helper that stages `UnitPipe`.
- **`Pipe`, `Stream`, `Sequential` classes + objects** (`Control.scala:22-65`). `Pipe.II(ii)`/`.POM`/`.MOP`/`.NoBind`/`.haltIfStarved` return new `Pipe` instances with updated `CtrlOpt`. Users rely on these being `lazy val`s so the builder syntax works cleanly.
- **`AccelClass`** (`AccelClass.scala:8-20`). `Accel { ... }` stages `AccelScope(stageBlock{...})`. `Accel(*) {...}` wraps body in `Stream.Foreach(*)`.
- **`ForeachClass`** (`ForeachClass.scala:9-35`). Overloaded `apply` stages `OpForeach`. Critically, it assigns each `i.counter = IndexCounterInfo(ctr, …)` metadata (line 29), so downstream passes know each iter's counter and its parallelism lanes.
- **`ReduceLike` / `ReduceAccum` / `ReduceConstant` / `ReduceClass` / `FoldClass`** (`ReduceClass.scala:9-97`). `Reduce(zero){...}{reduce}` dispatches through `ReduceConstant`; `Reduce(reg)` goes through `ReduceAccum` (line 82–84: the `Op(RegRead(reg))` match is the "hack to get explicit accum"). Stages `OpReduce` at line 49.
- **`MemReduceAccum` / `MemReduceClass` / `MemFoldClass`** (`MemReduceClass.scala:11-104`). Builds a *second* counter chain over the accumulator's sparse rank (lines 52-55), stages `OpMemReduce` with `mapBlk`, `resLd`, `accLd`, `redBlk`, `accSt`.
- **`FSM`** (`FSM.scala:8-25`). Stages `StateMachine` from three staged lambdas (notDone, action, nextState).
- **`CtrlOpt`** (`CtrlOpt.scala:8-27`). Aggregator for scheduling knobs. `set[A](x)` applies `x.userSchedule`, `x.userII`, `x.unrollAsMOP`/`unrollAsPOM`, `x.shouldNotBind`, `x.haltIfStarved` — the metadata channel that flows from DSL directives into later passes.
- **`NamedClass`** (`NamedClass.scala:4-9`). `Named("foo").Pipe`, `.Stream`, etc. — lazily rewraps `Pipe`/`Stream`/`Sequential`/`Accel` with a name.

### Memory types (local & remote)

- **`Mem[A,C[_]]`** (`types/Mem.scala:9-14`), **`LocalMem[A,C[_]]`** (`types/Mem.scala:40-49`) with abstract `__read(addr, ens)`, `__write(data, addr, ens)`, `__reset(ens)`. Every concrete memory class implements these, which is how transformers (e.g. unrolling) call into a memory generically.
- **`Mem1[A,M1[T]]` through `Mem5`** (`types/Mem.scala:125-298`). Provide `apply(range)`, `apply(row, cols)`, etc. that stage `MemDenseAlias`. `Mem5` is the big one — 30+ overloads for mixed Idx/Rng combinations.
- **`DRAM[A,C]`** (`DRAM.scala:8-39`). Concrete: `DRAM1`..`DRAM5`, `DRAMSparseTile` (`DRAM.scala:58-217`). Stages `DenseTransfer` / `SparseTransfer` / `MemSparseAlias`.
- **`SRAM[A,C]`** (`SRAM.scala:10-137`). Concrete: `SRAM1`..`SRAM5`, `SRAMN` (`SRAM.scala:177-300`). Dozens of banking hints.
- **`RegFile[A,C]`** (`RegFile.scala:11-73`). `RegFile1`..`RegFile3` plus `RegFileView`. Shifts (`<<=`) stage `RegFileShiftIn` / `RegFileShiftInVector`.
- **`LUT[A,C]`** (`LUT.scala:12-48`). `LUT1`..`LUT5`. Constructors accept literal `elems: Bits[A]*`, `fromSeq`, `fromFile(filename)` — the last reads a CSV at compile time via `loadCSVNow`. Also `FileLUT` (`LUT.scala:158+`).
- **`FIFO`** (`FIFO.scala:10-98`). Enqueue/dequeue/peek/vector/status.
- **`LIFO`** (`LIFO.scala:9-52`). Push/pop/peek.
- **`Reg[A]`**, **`FIFOReg[A]`** (`Reg.scala:9-99`) plus **`ArgIn`**, **`ArgOut`**, **`HostIO`** (`Reg.scala:101-111`). All are 0-dim local memories; `ArgIn`/`ArgOut` alloc via dedicated nodes for host↔accel.
- **`LineBuffer[A]`** (`LineBuffer.scala:9-39`).
- **`MergeBuffer[A]`** (`MergeBuffer.scala:10-34`).
- **`LockDRAM`/`LockDRAM1`, `LockSRAM`/`LockSRAM1`, `Lock`/`LockWithKeys`** (`LockMem.scala:11-182`).
- **`StreamIn[A]`, `StreamOut[A]`** (`StreamIn.scala`, `StreamOut.scala`). Backed by a `Bus`.
- **`Frame[A,C]`, `Frame1[A]`** (`Frame.scala:20-64`). AXI4-Stream off-chip memory (Rogue host interface).
- **`SpatialBlackbox[A,B]`, `SpatialCtrlBlackbox[A,B]`** (`Blackbox.scala:11-32`). Blackbox handles; `Blackbox.apply(in, params)` attaches `BlackboxConfig`.
- **`StreamStruct[A]`** (`StreamStruct.scala:12-37`). Each field read is a `FieldDeq` stream dequeue.

### Counters / ranges / host
- **`Counter[A:Num]`** (`Counter.scala:9-29`). `Counter(start, end, step, par)` stages `CounterNew`. `Counter.from(series)` uses a `Series[A]` destructure.
- **`CounterChain`** (`CounterChain.scala:7-13`). Wraps a `Seq[Counter[_]]` into a single staged sym.
- **Host `Array[A]` / `Matrix[A]` / `Tensor3-5[A]`** (`lang/host/*.scala`). Pure host-side computation over `ArrayMap`/`ArrayReduce` etc. nodes.

### Top-level plumbing
- **`trait Spatial extends Compiler with ParamLoader`** (`Spatial.scala:33-647`). Declares all passes, wires the compilation DAG in `runPasses` (lines 60-257), defines `override def initConfig() = new SpatialConfig`, parses CLI flags, resolves targets in `settings()`.
- **`trait SpatialApp extends Spatial with DSLApp`** (`SpatialApp.scala:5`).
- **`object dsl` / `object libdsl`** (`dsl.scala:9-46`). Provide the `@spatial`, `@struct`, `@streamstruct` macro annotations.

## 4. Entry points

The integration seams with the rest of Spatial and with user apps:

- **User-app facing:** `import spatial.dsl._` (or `libdsl`). Provides every user-visible name listed in `Aliases.scala`. Users extend `SpatialApp` / `SpatialTest` / `SpatialTestbench`.
- **Macro entry points:** `@spatial` (from `dsl.scala:15-18`), `@struct`, `@streamstruct`. The macro expansion calls into `forge.tags.AppTag("spatial", "SpatialApp")`.
- **Compiler driver entry:** `Spatial.runPasses` (`Spatial.scala:60-257`) is called by the argon runner with a staged `Block[_]` coming out of `stageApp` (`Spatial.scala:51-54`, which calls `main(args)`).
- **Argon interface:** this subsystem consumes `argon._` heavily (`Sym`, `Bits`, `Num`, `Type`, `stage`, `stageBlock`, `stageLambda*`, `stageWithFlow`, `boundVar`, `Lift`, `Struct`, `@ref`, `@api`, `@rig`, `@virtualize`) and extends `argon.lang.ExternalAliases`.
- **Node staging:** every DSL method ends in `stage(<spatial.node.*>)`. So the `spatial.node` subsystem is the direct downstream consumer. All IR allocation is routed through `stage()`.
- **Metadata attachment:** `CtrlOpt.set` at `CtrlOpt.scala:18-26`, and the many hint methods on `SRAM`/`FIFO`/`Reg` write into `spatial.metadata.memory._` and `spatial.metadata.control._` fields.

## 5. Dependencies

**Upstream (this subsystem uses):**
- `argon._` — core staging framework (`Sym`, `Bits`, `Num`, `Type`, `stage`, `Lift`, `Block`, `Lambda*`, `@ref`, `@api`, `Ref`, `Top`, `Exp`, `Config`, `Compiler`). E.g. `Reg extends LocalMem0[A,Reg] with StagedVarLike[A] with Ref[Ptr[Any],Reg[A]]` (`Reg.scala:9`).
- `argon.lang._` (`ExternalAliases`, `Fix`, `Flt`, `Bit`, `Text`, `Tup2`, `Void`, etc.).
- `argon.tags.StagedStructsMacro`, `argon.passes.IRPrinter`.
- `argon.lang.api.{BitsAPI, TuplesAPI, Implicits, DebuggingAPI_*}` (composed into `StaticAPI_Internal` at `StaticAPI.scala:9-22`).
- `forge.tags._` (`@api`, `@rig`, `@stateful`, `@virtualize`, `AppTag`), `forge.{Ptr, VarLike, SrcCtx}`, `forge.EmbeddedControls`.
- `spatial.node._` — every `stage(…)` call names a node defined there.
- `spatial.metadata.*` — control/memory/access/params/retiming/bounds/blackbox metadata modules. Nearly every hint method mutates this.
- `spatial.tags.StagedStreamStructsMacro` (`dsl.scala:4`).
- `spatial.util._`, `utils.math.ReduceTree`, `utils.implicits.collections._`, `utils.io.files._`, `emul.FixedPointRange`.
- `poly.{ConstraintMatrix, ISL}`, `models.AreaEstimator` (Spatial.scala:3-4, used in `SpatialISL` and `mlModel`).
- `spatial.targets.HardwareTarget`, `spatial.dse._`.

**Downstream (what uses this subsystem):**
- **Every user application and test** — the entire `test/` tree and any app imports `spatial.dsl._`.
- **`spatial.tags.StagedStreamStructsMacro`** — references `StreamStruct`.
- **All the transforms/traversals** — they consume the IR nodes produced via these `stage()` calls, and they read the metadata fields set by hint methods (e.g. `isWriteBuffer`, `isNoFlatBank`, `userSchedule`, `userII`).
- **Codegens** (`chiselgen`, `cppgen`, `scalagen`, `pirgen`, etc.) — they pattern-match on the node types staged here.
- **`Spatial.scala` itself** — `runPasses` relies on the DSL types only indirectly, but the `main` / `stageApp` path depends on `Tensor1[Text]`, `Void` aliases (imported from `spatial.lang`).

## 6. Key algorithms

Most files are surface staging, not algorithms. The substantive pieces:

- **Compiler pass pipeline (the DAG itself).** `Spatial.scala:164-253`. Abbreviated view (see `spatial-passes-coverage` §8 for canonical step-by-step enumeration): Block → `friendlyTransformer` → `switchTransformer` → `switchOptimizer` → `blackboxLowering1/2` → DSE (optional) → `switchTransformer` → `switchOptimizer` → `memoryDealiasing` → `laneStaticTransformer` (optional) → `pipeInserter` → `regReadCSE` → DCE → `streamify` (optional) → `streamTransformer` → FIFO init → `bankingAnalysis` → `counterIterSynchronization` → `unrollTransformer` → rewrites → `flatteningTransformer` → `bindingTransformer` → `bufferRecompute` → `accumTransformer` → `retimingAnalyzer`/`retiming` → `broadcastCleanup` → `initiationAnalyzer` → reports → codegen selection. Not an algorithm per se, but **the** map of Spatial's compilation flow.
- **Target resolution in `Spatial.settings()`** (`Spatial.scala:583-645`). Looks up `spatialConfig.targetName` in `targets.all`, defaults to `targets.Default`, and initializes `target.areaModel(mlModel).init()` and `target.latencyModel.init()`.
- **MemReduce's dual counter-chain construction** (`MemReduceClass.scala:52-73`). Derives a reduction-iteration counter chain from the accumulator's `sparseRank`/`sparseStarts`/`sparseSteps`/`sparseEnds`/`sparsePars`, then stages two nested blocks: one to fetch from the map result, one to fetch from the accumulator, one to combine, one to store.
- **`priorityDeq` / `roundRobinDeq`** (`PriorityDeqAPI.scala:10-107`). Builds cumulative-enable bit vectors (`cumulativeEnabled.scanLeft`, `deqEnablesWithPriorities`), stages `FIFOPriorityDeq` plus `PriorityMux`, and uses `prDeqGrp` hashing for codegen grouping. `roundRobinDeq` rotates priorities by `iter`.
- **Taylor expansions for transcendentals** (`MathAPI.scala:81-111`): `exp_taylor`, `log_taylor`, `sin_taylor`, `cos_taylor`, `sqrt_approx` — piecewise-linear / polynomial approximations.
- **`Array.toeplitz` layout math** (`host/Array.scala:151-174`). Computes Toeplitz matrix dimensions from filter/image/stride sizes and indexes rows/cols accordingly.

## 7. Invariants / IR state read or written

**Metadata written (selected):**
- `x.name`, `x.userSchedule`, `x.userII`, `x.unrollAsMOP`, `x.unrollAsPOM`, `x.shouldNotBind`, `x.haltIfStarved` — `CtrlOpt.set` (`CtrlOpt.scala:19-26`).
- `x.forcedLatency` — `ForcedLatency.apply` via `withFlow` (`Latency.scala:8-11`).
- `x.userInjectedDelay = true` — `MiscAPI.retime` (`MiscAPI.scala:29`).
- `i.counter = IndexCounterInfo(ctr, lanes)` — set on every iter variable in `ForeachClass.apply` (`ForeachClass.scala:29`), `ReduceAccum` (`ReduceClass.scala:44`), `MemReduceAccum` (`MemReduceClass.scala:61-62`).
- `s.explicitName` (Reg naming: `Reg.scala:53`).
- `mem.isWriteBuffer`, `mem.isNonBuffer`, `mem.shouldIgnoreConflicts`, `mem.keepUnused`, `mem.isNoFission`, `mem.isFullFission`, `mem.isNoFlatBank`, `mem.isNoHierarchicalBank`, `mem.isMustMerge`, `mem.nConstraints`, `mem.alphaConstraints`, `mem.noBlockCyclic`, `mem.onlyBlockCyclic`, `mem.blockCyclicBs`, `mem.bankingEffort`, `mem.explicitBanking`, `mem.forceExplicitBanking`, `mem.fullyBankDims`, `mem.duplicateOnAxes`, `mem.shouldCoalesce`, `mem.isDualPortedRead` — all set by the chaining methods on `SRAM`/`RegFile`/`LockSRAM`/`FIFO`/`Reg`. Definitions are in `spatial.metadata.memory`, but **set here**.
- `x.bound = UpperBound(n)` — `UserData.bound.update` (`UserData.scala:10`).
- `x.rangeParamDomain`, `x.explicitParamDomain` — `Implicits.createParam` (`Implicits.scala:46-56`), set on `I32.p(default)` params.
- `x.prDeqGrp = fifo.head.toString.hashCode()` — `PriorityDeqAPI` grouping codegen hint.
- `bbox.bboxInfo = BlackboxConfig(file, moduleName, latency, pipelineFactor, params)` — `Blackbox.scala:17,30,72,92`.
- `vbbox.rawLevel = Inner` — `Blackbox.VerilogController` (`Blackbox.scala:93`).
- `x.isWriteBuffer`, `x.isMustMerge` auto-set on every `MergeBuffer` — `MergeBuffer.scala:30-31`.

**Config written:** `SpatialConfig` fields are mutated by CLI flag handlers in `Spatial.defineOpts` (`Spatial.scala:259-576`). E.g. `--pir` sets `enablePIR=true`, `enableInterpret=false`, `enableSynth=false`, `enableRetiming=false`, `vecInnerLoop=true`, `enableBufferCoalescing=false`, `groupUnrolledAccess=true`, `targetName="Plasticine"`, `enableForceBanking=true`, `enableParallelBinding=false` (`Spatial.scala:307-323`). This is the implicit invariant: *PIR mode disables many other modes in one click.*

**Invariants relied on:**
- `SRAM`/`RegFile`/`LUT` constructor dims must be params or consts — checked via `if (!length.isParam && !length.isConst) error(...)` (e.g. `SRAM.scala:141`). This is a **staging-time invariant**.
- DRAM comparison (`eql`/`neql`) is explicitly *not supported* — `DRAM.scala:29-38` errors.
- `LUT.__write` is an error path: `"Cannot write to LUT"` (`LUT.scala:42-46`).
- `StreamIn.__write` and `StreamOut.__read` error (`StreamIn.scala:19-23`, `StreamOut.scala:19-23`).
- `allowLargeDelayFIFODeq = true` and `allowPrimitivesInOuterControl = true` in `SpatialConfig` are **internal invariants flipped by passes**; they gate later-pass checks.
- `config.enableMutableAliases = true` set in `Spatial.settings` (`Spatial.scala:585`) — Spatial relies on being able to alias mutable DRAM/SRAM symbols.

## 8. Notable complexities or surprises

- **Scala name shadowing is opt-in.** `libdsl` (`dsl.scala:9`) uses `StaticAPI_Frontend` only. `dsl` (`dsl.scala:29`) adds `StaticAPI_Shadowing`, which shadows `Int`, `Float`, `Boolean`, `String`, `Array`, even `Unit` with staged types (`Aliases.scala:156-197`). A nested `object gen` then re-exposes the Scala originals. *Any Phase 2 work touching app semantics has to remember that `Int` ≠ `scala.Int` in user code.*
- **The `Pipe`/`Stream`/`Sequential` singleton objects are `class` instances pre-configured with `None`/`false`** (`Control.scala:63-65`). This is so that `Pipe.II(3).Foreach(...)` returns a new configured `Pipe` without having to re-call a constructor. Similar for `Named`.
- **`Reduce(reg)` detection via `Op(RegRead(reg))` pattern match** (`ReduceClass.scala:81-84`) is called out in-source as "Hack to get explicit accum". If the accum register isn't read via exactly that shape, it falls back to `ReduceConstant`.
- **`MemReduceAccum` queries accumulator metadata** (`sparseRank`, `sparseStarts`, `sparseSteps`, `sparseEnds`, `sparsePars`) *at staging time* to build the reduction counter chain (`MemReduceClass.scala:52`). This means that the DSL layer has visibility into banking/access-related metadata.
- **SRAM has ~25 tuning hint methods.** (`SRAM.scala:55-131`). Many (`noflat`, `nohierarchical`, `nobank`, `nPow2`, `alphaPow2`) throw exceptions redirecting to their renamed counterparts — deprecation warts live on as runtime errors. `dualportedwrite` also unconditionally throws.
- **Virtualized control-flow bailouts.** `__whileDo`, `__doWhile`, `__return` in `SpatialVirtualization.scala:107-114` all emit `error` and are "not yet supported" — surprising limitations for app writers.
- **`FileBus`/`FileEOFBus` check struct shape at construction time.** `FileEOFBus` requires last struct field to be `Bit`; otherwise logs error and calls `state.logError()` (`Bus.scala:69-74`). Staging-time contract with runtime feedback.
- **`retime(delay, payload)`** (`MiscAPI.scala:23-33`) negative-delay check throws `IllegalArgumentException` — not the usual `error(ctx, ...)` path.
- **`SpatialConfig.copyTo`** (`SpatialConfig.scala:102-143`) copies only a subset of fields — e.g. it omits `enableLooseIterDiffs`, `streamify`, `useCrandallMod`, etc. Likely a maintenance hazard.
- **The TODO at `spatial.lang.api.PriorityDeqAPI.scala:11,26`**: *"this is probably an unsafe way to compute a group id"* — flagged by the author.
- **`LUT.fromFile` reads the CSV at *compile time*** via `loadCSVNow` (`LUT.scala:120`). Contrasted with `FileLUT` which stages `FileLUTNew` (`LUT.scala:159`) and reads at codegen time.
- **Accel with wildcard** (`AccelClass.scala:11-14`) auto-wraps scope in `Stream.Foreach(*)` — implicit outer stream loop that users may not realize is happening.
- **`Spatial.runPasses` DAG is very long** (~90 lines of pipeline steps). Optional branches gate off `spatialConfig.*` bits. **Order matters**: certain passes depend on metadata set by earlier passes (e.g. `retimingAnalyzer` before `retiming`, `accumAnalyzer` before `accumTransformer`).
- **Mutable singletons.** `Accel`, `Foreach`, `Reduce`, etc. are `object`s subclassing parameterized classes. They capture the default `CtrlOpt` at class init time and use `lazy val` for sub-builders. Thread-safety / test isolation is implicit.

## 9. Open questions

1. What are the exact boundary rules between `libdsl` (no shadowing) and `dsl` (shadowing)? Are there app features only available via the shadowed view? (Shadowing traits mix in extra `DebuggingAPI_Shadowing` — `StaticAPI.scala:36` — so yes, there's behavior only in one.)
2. How do the many per-memory hints (`.buffer`, `.nonbuffer`, `.nofission`, `.fullfission`, `.bank(...)`, `.forcebank(...)`, `.axesfission(...)`) interact when multiple are set? Is there a precedence rule or do they compose additively into metadata?
3. Why does `FoldClass` in `ReduceClass.scala:90-97` call `ReduceConstant` with `isFold = true` for `Lift[A]` zero but `isFold = false` for `Sym[A]` zero? Asymmetry looks intentional but is not documented.
4. `Spatial.runPasses` has a commented-out duplicate `blackboxLowering` at line 184. Left over or intentional?
5. What is `allowPrimitivesInOuterControl` (default `true`) actually gating? Its comment says "flag used to mark whether unit pipe transformer has been run or not", yet the default is `true`. Who flips it?
6. `SpatialBlackbox.apply` always attaches `BlackboxConfig("", None, 0, 0, params)` with empty file/moduleName (`Blackbox.scala:17`). Is this overwritten elsewhere or is the Spatial-side primitive blackbox supposed to have no Verilog source?
7. The `SpatialModuleClass` apply method is commented out (`SpatialModuleClass.scala:11-13`). Is this a feature in-flight?
8. `allowLargeDelayFIFODeq = true` in `SpatialConfig.scala:86` — when is this read, and what's the invariant if it's false?
9. Why does `Aliases.scala` distinguish between `Frame1` aliased under `ExternalAliases` but `Frame` also aliased — while `DRAM1`–`DRAM5` each individually aliased? Is it intentional that only Frame1 exists (i.e. Frame is always 1D)?
10. `StreamStruct` (`StreamStruct.scala:12`) extends `Ref[Nothing, A]` — what are the implications of `Nothing` as the data-type there?

## 10. Suggested spec sections

The Spatial language surface most directly feeds these spec areas under `10 - Spec/`:

- **`10 - Spec/10 - Frontend DSL/`**
  - `Controllers.md` — `Accel`, `Foreach`, `Reduce`, `Fold`, `MemReduce`, `MemFold`, `Pipe`, `Stream`, `Sequential`, `Parallel`, `FSM`, `Named`, `II`/`POM`/`MOP`/`NoBind`/`haltIfStarved` modifiers, `ForcedLatency`.
  - `Memories.md` — `DRAM`, `SRAM`, `RegFile`, `Reg`, `FIFO`, `LIFO`, `LineBuffer`, `MergeBuffer`, `LUT`/`FileLUT`, `LockMem` family, `Frame`. Each should cover dimensionality, constructors, read/write API, and the full set of banking/tuning hints.
  - `Primitives.md` — `Counter`, `CounterChain`, `Wildcard`, `Bus` family (`PinBus`, `AxiStream*`, `DRAMBus`, `FileBus`, `BurstCmdBus`, etc.), `Pin`.
  - `Streams-And-Blackboxes.md` — `StreamIn`, `StreamOut`, `StreamStruct`, `Blackbox`/`SpatialBlackbox`/`SpatialCtrlBlackbox`, `VerilogPrimitive`, `VerilogController`, `GEMM` builtins.
- **`10 - Spec/10 - Frontend DSL/Math-And-Helpers.md`** — `sum`/`product`/`reduce`/`min`/`max`/`pow`/`abs`/`exp`/`ln`/`sqrt`/trig, Taylor approximations, `SeqMathOps`, `SeqBitOps`, `mux`/`oneHotMux`/`priorityMux`, `priorityDeq`/`roundRobinDeq`, `retimeGate`/`retime`.
- **`10 - Spec/10 - Frontend DSL/Host-And-IO.md`** — host `Array`/`Matrix`/`Tensor3-5`, `CSVFile`, `BinaryFile`, `TensorData`, `setArg`/`getArg`/`setMem`/`getMem`/`getMatrix`/`getTensor*`, CSV/binary/numpy file IO, `setFrame`/`getFrame`.
- **`10 - Spec/10 - Frontend DSL/Debugging-And-Checking.md`** — `printArray`/`printMatrix`/`printTensor*`/`printSRAM*`, `approxEql`, `checkGold`, `r"..."` interpolator, unstaged `If`/`IfElse`, `sleep`.
- **`10 - Spec/10 - Frontend DSL/Virtualization.md`** — the `SpatialVirtualization` scheme: `__newVar`/`__assign`/`__use`/`__ifThenElse`/`__whileDo`/`__doWhile`/`__return`/`__throw`, `@virtualize` integration.
- **`10 - Spec/10 - Frontend DSL/Aliases-And-Shadowing.md`** — the three alias traits (`InternalAliases`/`ExternalAliases`/`ShadowingAliases`), the `gen.*` Scala-native escape hatch, and the `dsl` vs `libdsl` distinction.
- **`10 - Spec/20 - Compiler Driver/`**
  - `Pipeline.md` — the `Spatial.runPasses` DAG step-by-step, with which config flags gate which passes.
  - `Config.md` — every `SpatialConfig` field: default, purpose, interacting CLI flag, who reads it.
  - `CLI-Flags.md` — the full `defineOpts` surface, grouped (backends, DSE, retiming, banking, unrolling, experimental).
  - `Target-Resolution.md` — `settings()` logic for matching `--fpga <name>` to `targets.all`.
- **`10 - Spec/20 - Compiler Driver/App-Macros.md`** — `@spatial` macro, `@struct`, `@streamstruct`; `SpatialApp` / `SpatialTest` / `SpatialTestbench` trait structure.
- **`10 - Spec/30 - IR Interaction/Metadata-From-DSL.md`** — catalog which metadata fields are written from DSL surface methods (the full list in section 7 above).
