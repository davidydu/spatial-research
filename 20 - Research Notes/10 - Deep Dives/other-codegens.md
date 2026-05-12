---
type: deep-dive
topic: other-codegens
source_files:
  - "src/spatial/codegen/cppgen/CppGen.scala"
  - "src/spatial/codegen/cppgen/CppCodegen.scala"
  - "src/spatial/codegen/cppgen/CppFileGen.scala"
  - "src/spatial/codegen/cppgen/CppGenCommon.scala"
  - "src/spatial/codegen/cppgen/CppGenAccel.scala"
  - "src/spatial/codegen/cppgen/CppGenInterface.scala"
  - "src/spatial/codegen/cppgen/CppGenArray.scala"
  - "src/spatial/codegen/cppgen/CppGenMath.scala"
  - "src/spatial/codegen/cppgen/CppGenFileIO.scala"
  - "src/spatial/codegen/cppgen/CppGenDebug.scala"
  - "src/spatial/codegen/pirgen/PIRCodegen.scala"
  - "src/spatial/codegen/pirgen/PIRGenSpatial.scala"
  - "src/spatial/codegen/pirgen/PIRFormatGen.scala"
  - "src/spatial/codegen/pirgen/PIRGenHelper.scala"
  - "src/spatial/codegen/pirgen/PIRSplitGen.scala"
  - "src/spatial/codegen/pirgen/PIRGenController.scala"
  - "src/spatial/codegen/pirgen/PIRGenCounter.scala"
  - "src/spatial/codegen/pirgen/PIRGenSRAM.scala"
  - "src/spatial/codegen/pirgen/PIRGenFIFO.scala"
  - "src/spatial/codegen/pirgen/PIRGenLIFO.scala"
  - "src/spatial/codegen/pirgen/PIRGenRegFile.scala"
  - "src/spatial/codegen/pirgen/PIRGenLUTs.scala"
  - "src/spatial/codegen/pirgen/PIRGenReg.scala"
  - "src/spatial/codegen/pirgen/PIRGenDRAM.scala"
  - "src/spatial/codegen/pirgen/PIRGenStream.scala"
  - "src/spatial/codegen/pirgen/PIRGenMergeBuffer.scala"
  - "src/spatial/codegen/pirgen/PIRGenLock.scala"
  - "src/spatial/codegen/pirgen/PIRGenLineBuffer.scala"
  - "src/spatial/codegen/pirgen/PIRGenStructs.scala"
  - "src/spatial/codegen/pirgen/PIRGenVec.scala"
  - "src/spatial/codegen/pirgen/PIRGenFixPt.scala"
  - "src/spatial/codegen/pirgen/PIRGenFltPt.scala"
  - "src/spatial/codegen/pirgen/PIRGenBit.scala"
  - "src/spatial/codegen/pirgen/PIRGenBits.scala"
  - "src/spatial/codegen/pirgen/PIRGenDebugging.scala"
  - "src/spatial/codegen/pirgen/PIRGenText.scala"
  - "src/spatial/codegen/pirgen/PIRGenArray.scala"
  - "src/spatial/codegen/pirgen/PIRGenVar.scala"
  - "src/spatial/codegen/pirgen/PIRGenVoid.scala"
  - "src/spatial/codegen/pirgen/PIRGenSeries.scala"
  - "src/spatial/codegen/pirgen/PIRGenDelays.scala"
  - "src/spatial/codegen/pirgen/PIRGenFileIO.scala"
  - "src/spatial/codegen/roguegen/RogueGen.scala"
  - "src/spatial/codegen/roguegen/RogueCodegen.scala"
  - "src/spatial/codegen/roguegen/RogueFileGen.scala"
  - "src/spatial/codegen/roguegen/RogueGenCommon.scala"
  - "src/spatial/codegen/roguegen/RogueGenAccel.scala"
  - "src/spatial/codegen/roguegen/RogueGenInterface.scala"
  - "src/spatial/codegen/roguegen/RogueGenMath.scala"
  - "src/spatial/codegen/roguegen/RogueGenArray.scala"
  - "src/spatial/codegen/roguegen/RogueGenDebug.scala"
  - "src/spatial/codegen/tsthgen/TungstenHostGen.scala"
  - "src/spatial/codegen/tsthgen/TungstenHostCodegen.scala"
  - "src/spatial/codegen/tsthgen/TungstenGenCommon.scala"
  - "src/spatial/codegen/tsthgen/TungstenHostGenInterface.scala"
  - "src/spatial/codegen/tsthgen/TungstenHostGenArray.scala"
  - "src/spatial/codegen/tsthgen/TungstenHostGenAccel.scala"
  - "src/spatial/codegen/dotgen/DotCodegen.scala"
  - "src/spatial/codegen/dotgen/DotFlatCodegen.scala"
  - "src/spatial/codegen/dotgen/DotHierarchicalCodegen.scala"
  - "src/spatial/codegen/dotgen/DotGenSpatial.scala"
  - "src/spatial/codegen/dotgen/DotHtmlCodegen.scala"
  - "src/spatial/codegen/dotgen/HtmlIRGen.scala"
  - "src/spatial/codegen/dotgen/HtmlIRGenSpatial.scala"
  - "src/spatial/codegen/treegen/TreeGen.scala"
  - "src/spatial/codegen/naming/NamedCodegen.scala"
  - "src/spatial/codegen/resourcegen/ResourceReporter.scala"
  - "src/spatial/codegen/resourcegen/ResourceCountReporter.scala"
  - "src/spatial/Spatial.scala"
session: 2026-04-23
status: ready-to-distill
feeds_spec:
  - "[[10 - Cppgen]]"
  - "[[20 - Per-Target Files]]"
  - "[[10 - Pirgen]]"
  - "[[50 - Other Codegens]]"
  - "[[70 - Naming and Resource Reports]]"
---

# Other Codegens Deep Dive (non-Chiselgen, non-Scalagen backends)

## Reading log

Read the two Phase 1 coverage notes for orientation, then every file in scope in this order: cppgen (10 files), pirgen (32 files, focusing first on `PIRCodegen`/`PIRFormatGen`/`PIRGenHelper`/`PIRSplitGen`/`PIRGenSpatial`, then per-construct traits), roguegen (9 files), tsthgen (6 files), dotgen (7 files), treegen (1 file), naming (1 file), resourcegen (2 files). Finally cross-referenced `spatial/Spatial.scala:130-253` for registration and gating.

## Observations

### 1. Composition pattern

Every top-level codegen in this bundle follows the same two-layer shape:

```scala
trait XCodegen extends argon.codegen.Codegen with FileDependencies with AccelTraversal { ... }   // base trait
case class XGen(IR: State) extends XCodegen with XGenInterface with XGenArray with ... { }      // mixin composition
```

The base trait pins `lang`, `ext`, `entryFile`, and `copyDependencies`. Each sibling trait overrides `gen(lhs, rhs)` with `case` clauses for a family of Ops; the `case _ => super.gen(lhs, rhs)` tail makes the chain linearizable. Specifically:

- `CppGen(IR: State) extends CppCodegen with CppFileGen with CppGenCommon with CppGenInterface with CppGenAccel with CppGenDebug with CppGenMath with CppGenArray with CppGenFileIO` (`cppgen/CppGen.scala:5-13`). 8 mixins.
- `PIRGenSpatial(IR: State) extends PIRCodegen with PIRGenController with PIRGenArray with PIRGenBits with PIRGenBit with PIRGenFixPt with PIRGenFltPt with PIRGenStructs with PIRGenText with PIRGenDebugging with PIRGenCounter with PIRGenDRAM with PIRGenFIFO with PIRGenReg with PIRGenSRAM with PIRGenLock with PIRGenMergeBuffers with PIRGenVec with PIRGenStream with PIRGenRegFile with PIRGenLUTs with PIRSplitGen` (`pirgen/PIRGenSpatial.scala:5-33`). **32 files in the directory, only ~22 traits actually mixed in.** The commented-out traits at `pirgen/PIRGenSpatial.scala:14`-30 are `PIRGenVoid`, `PIRGenVar`, `PIRGenLIFO`, `PIRGenSeries`, `PIRGenFileIO`, `PIRGenDelays`. Note also that `PIRGenLineBuffer` is neither in the mixin list nor commented out — it is **silently excluded**, which means its error-on-LineBuffer code (`pirgen/PIRGenLineBuffer.scala:16-18`) never fires and a user app with LineBuffers will instead hit `PIRCodegen.genAccel`'s fallback "TODO: Unmatched Node" comment at `pirgen/PIRCodegen.scala:121`. **Likely a bug, filed as an open question.**
- `RogueGen(IR: State) extends RogueCodegen with RogueFileGen with RogueGenCommon with RogueGenInterface with RogueGenAccel with RogueGenDebug with RogueGenMath with RogueGenArray` (`roguegen/RogueGen.scala:5-13`). 7 mixins, FileIO trait commented out on line 13 (there is no `RogueGenFileIO.scala` in the directory anyway).
- `TungstenHostGenSpatial(IR: State) extends TungstenHostCodegen with TungstenHostGenCommon with CppGenDebug with CppGenMath with TungstenHostGenArray with CppGenFileIO with TungstenHostGenInterface with TungstenHostGenAccel` (`tsthgen/TungstenHostGen.scala:6-14`). Important: `CppGenDebug`, `CppGenMath`, `CppGenFileIO` are reused verbatim from cppgen. tsthgen is largely a C++-host specialization.

### 2. Cppgen base structure and file emission

`CppCodegen` (`cppgen/CppCodegen.scala:9-85`) pins `lang="cpp"`, `ext="cpp"`, entry `TopHost.cpp`, and `backend="cpp"` (set by `CppFileGen:9`). `copyDependencies` (lines 20-82) does a three-part registration:

1. Fixed: `synth/datastructures`, `synth/SW`, `synth/scripts` (lines 26-37).
2. Per-target: each of 9 targets `{VCS, Zynq, ZedBoard, ZCU, CXP, AWS_F1, DE1, Arria10, ASIC}` (lines 38-75) gets `<target>.sw-resources/` (directory), `<target>.hw-resources/` (directory), and `<target>.Makefile` (renamed to `Makefile`).
3. Trailing: `build.sbt`, `run.sh` (lines 77-79).

`CppFileGen` emits six files in `emitHeader` (`cppgen/CppFileGen.scala:11-100`):

- `cpptypes.hpp` — just header guards (lines 13-17).
- `functions.hpp` — header guards + include of `functions.hpp` inside `functions.cpp` (lines 19-27).
- `functions.cpp` — one-line include (lines 25-27).
- `structs.hpp` — ~20 standard-library includes + `#include "Fixed.hpp"` + typedef `int128_t` (lines 29-53).
- `ArgAPI.hpp` — empty comment header; filled in at `emitFooter` (line 55-57; footer at `cppgen/CppGenInterface.scala:138-166`).
- `TopHost.cpp` — includes, `#define MAX_CYCLES`, `FringeContext` construction, `void Application(...)` opener (lines 59-100).

`emitFooter` (`CppFileGen.scala:106-148`) closes `Application`, emits `printHelp()` using CLIArgs, and emits `int main` that parses argv and invokes `Application`.

### 3. Cppgen host-driver seam

`CppGenAccel.AccelScope` (`cppgen/CppGenAccel.scala:16-102`) is where the host learns about the accelerator. After visiting the function body (which stages all the host-side setup: arg allocation, DRAM creation, set/get), it emits the FringeContext driver sequence:

```cpp
c1->setNumArgIns(argIns.length + drams.length + argIOs.length);
c1->setNumArgIOs(argIOs.length);
c1->setNumArgOuts(argOuts.length);
c1->setNumArgOutInstrs(instrumentCounterArgs() or 0);
c1->setNumEarlyExits(earlyExits.length);
c1->flushCache(1024);
time_t tstart = time(0);
c1->run();
time_t tend = time(0);
// ... reporting
c1->flushCache(1024);
```

(`cppgen/CppGenAccel.scala:24-37`). The ArgIn/ArgIO/ArgOut counts come from `CppGenCommon` mutable `ArrayBuffer`s (`cppgen/CppGenCommon.scala:31-34`). If `spatialConfig.enableInstrumentation` is set, the block at lines 58-101 iterates `instrumentCounters` to pull cycles/iters per controller and prints a nested indent-by-depth report to stdout and `./instrumentation.txt`.

`CppGenInterface` (`cppgen/CppGenInterface.scala:19-134`) emits the concrete marshalling:

- `ArgInNew(init)` → `${lhs.tp} $lhs = $init;` — plain C++ local (line 21-22).
- `DRAMHostNew(dims)` → `uint64_t $lhs = c1->malloc(sizeof(tp) * prod(dims));` + `c1->setArg(argHandle(lhs)_ptr, $lhs, false);` (lines 37-40).
- `SetReg(reg, v)` for `FixPtType(s,d,f)` with `f != 0`: bit-shift left by `f` bits before `c1->setArg` (lines 44-47) — "true-fix" bit-level marshalling.
- `SetReg(reg, v)` for `FltPtType(g,e)`: `memcpy` to an `int64_t` and mask to `(g+e)` bits (lines 52-57).
- `GetReg(reg)` mirrors, with sign-extension (lines 64-80): `bool sgned = s & ((tmp & ((int64_t)1 << (d+f-1))) > 0); if (sgned) tmp = tmp | ~(((int64_t)1 << (d+f))-1);`. This is a reverse of `toTrueFix` in `CppGenCommon:37-42`.
- `SetMem(dram, data)` / `GetMem(dram, data)` — bulk memcpy. Fixed-point with `f > 0 && width >= 8` rawify into an `int` vector first; small widths (`< 8`) are packed 8-to-1 (lines 85-131).

`emitFooter` in `CppGenInterface` writes `ArgAPI.hpp` (lines 138-166): sequential `#define <HANDLE>_arg <id>` for ArgIns, `#define <HANDLE>_ptr <id>` for DRAM handles (offset by `argIns.length`), then ArgIOs, ArgOuts, instrumentation counters, early-exit handles — all indexing into one flat register bank shared with the Chisel `Instantiator.scala`. The `_cycles_arg` / `_iters_arg` / `_stalled_arg` / `_idle_arg` per-controller quadruple is emitted conditionally on `hasBackPressure`/`hasForwardPressure`.

### 4. CppGenCommon shared machinery

`CppGenCommon` (`cppgen/CppGenCommon.scala:11-159`) is the mixin shared by every `CppGen*` trait. Key fields:

- `instrumentCounters: List[(Sym[_], Int)]` — `(sym, depth)` for every controller seen; used by both `CppGenAccel` and the footer. Depth comes from `controllerStack.length` at entry time (`CppGenAccel.scala:19`).
- `earlyExits: List[Sym[_]]` — ExitIf/AssertIf/BreakpointIf seen `inHw`.
- `controllerStack`, `argOuts`, `argIOs`, `argIns`, `drams` — four `ArrayBuffer[Sym[_]]`s feed the footer.
- `asIntType(tp)` (lines 51-73) — largest of `bool`/`int8_t`/`int16_t`/`int32_t`/`int64_t`/`int128_t`/`int256_t` that fits the bit width. Used to pick the host-side container for bit-level DRAM payloads.
- `remap(tp)` (lines 75-100) — `FixPtType` with `f==0` → `uint{N}_t`/`int{N}_t`; `f!=0` → `double`; `FltPtType` → `float`; `Text` → `string`; `Vec[T]` / `host.Array[T]` → `vector<T>`. **Critical semantic point: Cppgen maps every fixed-point with fractional bits to `double`, discarding the bit-exact fixpoint semantics.**
- `toTrueFix(x, tp)` / `toApproxFix(x, tp)` (lines 37-49) — the bit-shift marshalling primitive. `toTrueFix` produces `(int) (x * (1 << f))`; `toApproxFix` reverses it.
- `argHandle(sym)` (lines 134-149) — duplicates `SYM_NAME`, `SYM_NAME_dup1`, etc., resolves naming collisions.
- `hasBackPressure` / `hasForwardPressure` (lines 122-123) — true when a stream ancestor carries reads/writes respectively.

### 5. Cppgen's wider op coverage

`CppGenMath` (`cppgen/CppGenMath.scala`) — ~70 math ops → C/libm one-liners. Notable: `FixFMA` is two-op `a*b+c` (line 34), not an actual fused op. `FixMod` wraps with +modulus-trick: `(a%b + b) % b` (line 55-56). `FixSLA/FixSRA` on non-zero-fractional FixPt translate to `x * pow(2.,y)` / `x / pow(2.,y)` (lines 144-151) — floating-point shifts, not bit shifts, again reinforcing the double-cast semantic choice.

`CppGenArray` (`cppgen/CppGenArray.scala`, 433 LOC, largest file) handles host-side collection literals. `SimpleStruct` (lines 153-198) emits a C++ `struct` into `structs.hpp` with `__attribute__((packed))`, a no-arg constructor, a value-taking constructor, `toString()` using `toApproxFix`, per-field setters with `toTrueFix` conversion, **and** `toRaw()` (lines 172-190) that bit-concatenates fields into an `int128_t` (or size appropriate). A matching `${struct}(int128_t bits)` constructor decodes the raw bits. This is the same pattern tsthgen borrows (`tsthgen/TungstenHostGenArray.scala:22-68`) for PIR-host parity. The `try { ... } catch { _: Throwable => }` wrapping (lines 172, 190) is a silent fallback for non-bit-packable types.

`CppGenArray` also handles all the host-side `Array*` ops: `ArrayNew`, `ArrayLength`, `ArrayApply`, `ArrayUpdate`, `ArrayMap`, `ArrayReduce`, `ArrayZip`, `ArrayFlatMap`, `ArrayFilter`, `ArrayForeach`, `ArrayFold`, `ArrayFromSeq`, `ArrayMkString`, `MapIndices`, `SeriesForeach`, `IfThenElse` (host), `Switch` (host), `UnrolledForeach` (host — non-inHw), `VecAlloc`, `VecApply`, `VecSlice`, `VecConcat`. Each emits a direct C++ `for`/`if` loop with `(*arr)[i]` indexing. `IfThenElse` has an `isArrayType` branch (lines 249-259) that emits `${tp}*` for array-returning conditionals.

`CppGenFileIO` (`cppgen/CppGenFileIO.scala:7-140`) — `LoadDRAMWithASCIIText(dram, file)` (lines 10-31), `OpenBinaryFile` with `std::ifstream`/`std::ofstream` (line 35-38), `ReadBinaryFile` that allocates `std::vector<char>`, `memcpy`s to `std::vector<rawtp>`, then converts each element with `toApproxFix` (lines 40-71). `WriteBinaryFile` (lines 73-86) for `FixPtType` writes bit-shifted raw, otherwise a raw write. `OpenCSVFile` / `ReadTokens` / `WriteTokens` handle CSV I/O.

`CppGenDebug` (`cppgen/CppGenDebug.scala:10-62`) handles all the text ops: `FixToText`, `FltToText`, `TextConcat`, `TextSlice`, `TextApply`, `TextEql`, `TextLength`, `TextToBit`, `TextToFix`, `CharArrayToText`, `PrintIf`, `BitToText`. Also `VarNew`/`VarRead`/`VarAssign` → simple C++ locals, and `DelayLine` → identity `${lhs.tp} $lhs = $data`.

### 6. Pirgen: the `state` / `alias` DSL

PIR codegen produces a `PIRApp` Scala program that the PIR compiler stack later ingests. The emit shape is not idiomatic Scala — each statement is a PIR DSL builder call chained with `.sctx`/`.name`/`.count`/`.barrier`/`.waitFors`/`.progorder` (`pirgen/PIRFormatGen.scala:25-50`).

`PIRFormatGen.state(lhs, tp=None)(rhs)` (`pirgen/PIRFormatGen.scala:25-50`) is the core primitive:

```scala
def state(lhs:Lhs, tp:Option[String]=None)(rhs: Any) = {
  var rhsStr = src"$rhs.sctx(\"${lhs.sym.ctx}\")"
  val tpStr = tp match { case Some(t) => t; case None => rhsStr.split("\\(")(0) }
  // append .name() based on (name, postFix)
  // append .count / .barrier / .waitFors / .progorder if metadata present
  emitStm(lhs, tpStr, rhsStr)
}
```

`emitStm` (`PIRFormatGen.scala:73-76`): `emit(src"val $lhs = $rhsStr // ${comment(...)}")`, and records the type in `typeMap: mutable.Map[Lhs,String]`. `PIRSplitGen.emitStm` (`pirgen/PIRSplitGen.scala:21-33`) overrides this to call `save("$lhs", $rhsStr)` instead of plain assignment — the emitted PIR DSL has a global `save/lookup` machinery.

`alias(lhs)(rhsFunc)` (`PIRFormatGen.scala:52-55`) re-uses an existing symbol's typeMap entry without re-emitting the rhs; used for pass-through ops like `DataAsBits` (`pirgen/PIRGenBits.scala:15`) and `FieldApply` (`pirgen/PIRGenStructs.scala:19`).

`Lhs(sym, postFix=None)` (`PIRFormatGen.scala:14-17`) is a wrapper for emitting subnames: e.g. merge-buffer plumbing emits `Lhs(lhs, "inputFIFO")` which renders as `${sym}_inputFIFO`. This is used whenever a single Spatial symbol produces multiple PIR memory objects.

### 7. Pirgen memory emitters

`stateMem(lhs, rhs, inits, tp, depth)` in `PIRGenHelper` (`pirgen/PIRGenHelper.scala:23-36`) is the universal memory constructor. It wraps the base `rhs` with `.inits(...)`, `.depth(...)`, `.dims(...)`, `.banks(...)`, `.tp(...)`, `.isInnerAccum(...)` — reading per-mem `instance.depth`/`instance.banking.map(_.nBanks)`/`constDims`/`padding`/`isInnerAccum` metadata. Then splits per struct field via `stateStruct(lhs, A)` (line 38-43) — a struct-typed memory becomes N separate named memories (one per field).

`stateAccess(lhs, mem, ens, data?)(body)` (`PIRGenHelper.scala:54-76`) wraps a body with `.setMem(mem).en(ens).data(data?).port(bufferPort).muxPort(muxPort).broadcast(broadcast).castgroup(castgroup).isInnerReduceOp(...)`. Reads `lhs.port.bufferPort`, `.muxPort`, `.broadcast`, `.castgroup` metadata. The `data` argument is `Option[Seq[Sym]]` — PIR codegen enforces single-lane with `assertOne(ens)` and `assertOne(data)` (`PIRGenHelper.scala:14-21`; throws if more than one).

`genOp(lhs, op=None, inputs=None)` (`PIRGenHelper.scala:78-87`) — the workhorse for arithmetic/logic: emits `OpDef(op=$opStr).addInput($ins).tp(${lhs.sym.tp})(.isInnerReduceOp(true)?)`. `PIRGenFixPt`/`PIRGenFltPt`/`PIRGenBit`/`PIRGenBits`/`PIRGenText` are almost entirely `case FixAdd(x,y) => genOp(lhs)` one-liners (`pirgen/PIRGenFixPt.scala:19-74`).

### 8. PIR controller emission

`PIRGenController.emitController` (`pirgen/PIRGenController.scala:13-52`): every control emits `createCtrl(schedule=${lhs.sym.schedule})(UnitController() or LoopController().cchain($cc).par($par).en($ens).stopWhen(MemRead().setMem($reg)))`. Then for every iter and valid, emits a `CounterIter(lanes).counter($lhs.cchain.T($i)).resetParent($lhs).tp(tp)` and `CounterValid(...)` (lines 40-48) — one PIR sym per Spatial lane. `StateMachine` is currently a stub: `emit(s"//TODO: ${qdef(lhs)}")` (line 81). Switch emission (lines 70-75) rewrites cases as `case.en(selects(i))` after staging the body.

### 9. PIRSplitGen chunking

`PIRSplitGen` (`pirgen/PIRSplitGen.scala:10-65`) is the PIR analog of scalagen/chiselgen `javaStyleChunk`: emits `def split1 = { ... }; split1` blocks of `splitThreshold = 10` statements (`PIRSplitGen.scala:15`). On each `emitStm`, the line counter increments; if over threshold, it calls `splitEnd` (closes current chunk) and `splitStart` (opens a fresh `defsplit${++splitCount} = {`). Cross-chunk references require `lookup[type]("name")` (line 60), not a raw `val` reference. The chunker wraps only the inside of `emitAccelHeader`/`emitAccelFooter` — host code outside `Accel` is not split.

### 10. PIR-specific constructs

**Lock** (`pirgen/PIRGenLock.scala:10-48`): `LockNew(depth)` → `Lock()`. `LockOnKeys(lock, keys)` → `LockOnKeys().key(keys).lock(lock)` (with `assertOne(keys)`). `LockSRAMNew` → `LockMem(false)`, `LockDRAMHostNew` → `LockMem(true)`. `LockSRAMBankedRead/Write` and `LockDRAMBankedRead/Write` → `LockRead()`/`LockWrite()` with `.addr(bank or ofs).lock(lock)`. No scalagen or chisel analog for `Lock` exists in the reference-semantics sense — it's a PIR-native construct.

**MergeBuffer** (`pirgen/PIRGenMergeBuffer.scala:10-72`): LCA-based placement. `MergeBufferNew(ways, par)` → `MergeBuffer(ways, par)`. For each enqueue (`BankedEnq`), dequeue (`BankedDeq`), bound (`Bound`), init, synthesizes a per-way FIFO (`inputFIFO`, `outputFIFO`, `boundFIFO`, `initFIFO`) with single-bank `.banks(List(par))`/`.banks(List(1))`, then places the PIR internal `MemRead().out(mem.inputs(way))` etc. inside the LCA of all accesses via `withinCtrl(mem)` — which `beginState(lca.getCtrl); block; endState[Ctrl]` brackets the inner ops (lines 17-22). `MergeBufferBankedDeq` also calls `mem.ctrl(lca.getCtrl, true)` (line 47) to tag the merge node with its LCA.

**Vec width-1 invariant**: `PIRGenVec.VecApply(vector, i)` bugs if `i != 0` (`pirgen/PIRGenVec.scala:11-14`). `VecAlloc(elems)` bugs if `elems.size != 1` (lines 22-26). This assumes all Vec traffic reaching pirgen codegen has been unrolled to width-1 by the unroller. `VecSlice` emits `vector.slice(start, end+1)` (line 20) — inclusive-end semantics; the comment claims "end is non-inclusive" but subtracts one from end, which is contradictory, filed as an open question.

### 11. PIR unsupported-ops (late errors)

`PIRGenFIFO` errors at codegen for `FIFOIsEmpty`, `FIFOIsFull`, `FIFOIsAlmostEmpty`, `FIFOIsAlmostFull`, `FIFOPeek`, `FIFONumel` (`pirgen/PIRGenFIFO.scala:16-24`) — `error(...)` which just prints a message via `argon.Reporting`. No exception is thrown; compilation will proceed with invalid output. These are all supported in scalagen. `PIRGenLineBuffer` errors on `LineBufferNew`/`LineBufferBankedEnq`/`LineBufferBankedRead` (`pirgen/PIRGenLineBuffer.scala:16-18`), but — critical caveat from §1 — the trait is not mixed in, so the errors never fire. `PIRGenLIFO` commented out all `isEmpty/isFull/peek/numel/almostEmpty/almostFull` (`pirgen/PIRGenLIFO.scala:15-20`) — also unsupported but silently unhandled.

### 12. Roguegen: Python for SLAC Rogue

`RogueCodegen` (`roguegen/RogueCodegen.scala:10-47`) is `lang="rogue"`, `ext="py"`, entry `TopHost.py`. `backend="python"` is set in `RogueFileGen:9`. `copyDependencies` branches only on `KCU1500` (`RogueCodegen.scala:31-35`) — all other targets produce nothing target-specific. `build.sbt`, `run.sh`, `scripts/` directory copied unconditionally.

`RogueFileGen.emitHeader` (`roguegen/RogueFileGen.scala:11-70`) opens `TopHost.py` with a fixed preamble: `#!/usr/bin/env python3`, imports of `rogue`, `rogue.hardware.axi`, `rogue.interfaces.stream`, `rogue.interfaces.memory`, `pyrogue as pr`, `pyrogue.gui`, `axipcie as pcie`, plus `time`, `math`, `random`, `struct`, `numpy as np`. Opens `def execute(base, cliargs):` with the initial hardware reset sequence:

```python
accel = base.Fpga.SpatialBox
accel.Reset.set(1); accel.Enable.set(0); time.sleep(0.01); accel.Reset.set(0)
print("Starting TopHost.py...")
```

Also opens `ConnectStreams.py` with its own imports (including `FrameSlave`, `FrameMaster`) and a `def connect(base):` opener.

`RogueGenCommon.remap` (`roguegen/RogueGenCommon.scala:58-82`) — unlike cppgen, this produces strings like `uint32`/`int64` with NO `_t` suffix (Python/numpy-ish), and fractional fixpoints still coerce to `double`. `FloatType()` → `float`, `FltPtType` → `float` (not `double`; float is the generic Python name for IEEE 754). Text → `string`. Vec/Tup/Reg cases are commented out.

`RogueGenAccel.AccelScope` (`roguegen/RogueGenAccel.scala:14-75`) emits the classic polling loop:

```python
done = accel.Done.get()
ctr = 0
accel.Enable.set(1)
while (done == 0):
    done = accel.Done.get()
    time.sleep(0.01)
    ctr = ctr + 1
    if (ctr % 75 == 0): print("  Polled flag %d times..." % ctr)
```

Followed by optional instrumentation printout per controller with per-access `time.sleep(0.0001)` between reads — this is a real hardware-bus polling delay, not a benign no-op.

`RogueGenInterface` (`roguegen/RogueGenInterface.scala:10-182`):

- `ArgInNew` / `HostIONew` → plain Python assignment (lines 20-26).
- `DRAMHostNew` → **throws an Exception** (line 32): `"DRAM nodes not currently supported in Rogue!"`. So rogue apps cannot use DRAM; only `FrameHostNew` + AXI streams.
- `FrameHostNew(dim, _, stream)` (lines 33-45): creates `base.${lhs}_frame = FrameMaster()` or `FrameSlave()` depending on the direction, and `pyrogue.streamConnect(...)` in ConnectStreams.py.
- `SetReg` → `accel.${argHandle(reg)}_arg.set(v); print(...); time.sleep(0.001)` (lines 46-48).
- `GetReg` → `accel.${argHandle(reg)}_arg.get(); time.sleep(0.0001)` (line 53).
- `StreamInNew(bus)` / `StreamOutNew(bus)` for AxiStream64/256/512Bus → `base.${lhs}_port = rogue.interfaces.stream.TcpClient('localhost', 8000 + ($tdest+1)*2 + $tid * 512)` (lines 56-72). **All three bus widths use the same port formula.**
- `SetFrame`/`GetFrame` → `base.${frame}_frame.sendFrame(data.astype(dtype='uint64'))` / `np.frombuffer(lhs, dtype='uint8').astype(dtype='${tp}')` (lines 75-80).

`emitFooter` (lines 87-180) writes `_AccelUnit.py`: a `pyrogue.Device` subclass with `RemoteVariable` entries at fixed 4-byte-aligned offsets for `Enable` (0x000 bit 0), `Reset` (0x000 bit 1), `Done` (0x004, 32 bits RO), then per-argIn/argIO/argOut/instrumentation counter/early-exit at offsets `*4 + 8` into a shared register map. This register map must match the Chisel side.

`RogueGenArray` (`roguegen/RogueGenArray.scala`) — numpy-based host array ops. `ArrayNew(size)` → `np.zeros(size, dtype='${tp}')`; `ArrayFromSeq(seq)` → `np.array([...], dtype='${tp}')`; `ArrayMap/Zip/Foreach/Reduce/Fold/Filter/FlatMap` emit Python for-loops with numpy indexing.

`RogueGenMath` (`roguegen/RogueGenMath.scala`) — Python + `math.*` translations. `Mux(sel,a,b)` → `a if sel else b` (line 100).

### 13. Tsthgen: tungsten C++ specialization

`TungstenHostCodegen` (`tsthgen/TungstenHostCodegen.scala:12-75`): `lang="tungsten"`, `ext="cc"`, entry `main.cc`. `override def out = buildPath(super.out, "src")` (line 16) — output goes to a `src/` subdirectory. `emitEntry` (lines 22-63) writes fixed boilerplate including `#include "repl.h"`, `#include "DUT.h"`, `#include "cppgenutil.h"`, two functions `printHelp()` and `genLink()` (creates a `Top`, a `Module DUT({top}, "DUT")`, a `REPL repl(&DUT, std::cout)`, and calls `repl.Command("source script_link")`), then `int main(int argc, char **argv)` which parses argv, matches `--help`/`--gen-link` specially, then `gen(block)` (line 60), then `cout << "Complete Simulation"`. `gen(lhs, rhs)` default (line 65-68) emits `// TODO: Unmatched node $lhs = $rhs` — tsthgen relies entirely on mixin dispatch.

`TungstenHostGenCommon.remap` (`tsthgen/TungstenGenCommon.scala:9-14`) — the killer remap:

```scala
case FixPtType(s,d,f) if f != 0 && d+f <= 32 => "float"
case FixPtType(s,d,f) if f != 0 && d+f <= 64 => "double"
```

So fractional fixed-point coerces to `float` for ≤32 bits total, `double` for ≤64 bits total. The super-class (cppgen's `CppGenCommon.remap`) coerces everything with `f != 0` to `double`. Tsthgen's floats are less precise than cppgen's but match the Tungsten simulator's C++ harness conventions.

`TungstenHostGenInterface` (`tsthgen/TungstenHostGenInterface.scala:11-132`) — allocation separation. Every `ArgInNew`/`HostIONew`/`ArgOutNew`/`DRAMHostNew`/`LockDRAMHostNew` goes through `genIO { ... }` which wraps its content in `inGen(out, "hostio.h")` (line 39-43). So all allocations land in a single `hostio.h` instead of the main `main.cc`. `genAlloc(lhs, inFunc)(block)` (lines 45-58) wraps a block in `void Alloc${lhs}() { ... }` if `inFunc`, registers it in `allocated: ListBuffer[String]`, and emits a call to it. `emitFooter` writes `void AllocAllMems() { Alloc$i(); ... }` to `hostio.h` (lines 27-37), producing a deterministic deferred-allocation sequence.

`DRAMHostNew` (lines 91-102) allocates burst-aligned: `malloc(sizeof(tp) * prod(dims) + bytePerBurst); lhs = (void*)(((uint64_t)lhs + bytePerBurst - 1) / bytePerBurst * bytePerBurst);` with `bytePerBurst = 64` (line 60) — a 64-byte alignment round-up. `LockDRAMHostNew` follows the same pattern.

`TungstenHostGenArray` (`tsthgen/TungstenHostGenArray.scala:11-72`) — same `SimpleStruct` pattern as cppgen's `CppGenArray` but targets `hostio.h` (via `genIO`) and emits `typedef __int128 int128_t` in its header (line 17). Struct also has `toRaw()` + raw-bits constructor (lines 42-59).

`TungstenHostGenAccel` (`tsthgen/TungstenHostGenAccel.scala:11-39`) is a **skeleton**: the main `AccelScope` emission is just `emit("RunAccel();")` (line 16). All controller traversal logic is inherited from `CppGenAccel`. ExitIf/AssertIf/BreakpointIf mirror cppgen. The accel side of tsthgen is simulated by a `RunAccel()` function defined in the Tungsten runtime library linked externally; tsthgen does not emit controller bodies into `main.cc`.

### 14. Dotgen layout families

`DotCodegen` (`dotgen/DotCodegen.scala:10-215`) is the generic Graphviz base: `lang="info"`, `ext="dot"`, one `Scope` per subgraph, each with `_nodes`, `externNodes`, `edges` (`case class Scope(sym: Option[Sym])`, lines 30-84). `scopes: Map[Option[Sym],Scope]` (line 17) indexes scopes by the enclosing control symbol (or `None` for top-level). `emitEntry` (lines 86-91) begins the top scope and then `scopes.values.foreach(_.end)` closes every scope at the tail — each becomes one `.dot` file.

`postprocess` (lines 94-112) spawns `dot -Tsvg -o ${scope.htmlPath} ${scope.dotPath}` for every scope and logs to `dot.log`. Detects three common failure modes: "triangulation failed" → Graph too large; "command not found" → graphviz absent; "trouble in init_ran" → graph too large, suggest update.

Two layout strategies:

**Flat** (`dotgen/DotFlatCodegen.scala:9-41`): `entryFile = "Main.dot"`. One file for everything. Each control node emits `subgraph cluster_${lhs} { ... }` wrapping its body (lines 17-33). `graphAttr` for blocks gets a `URL -> $lhs.html` so the rendered cluster links to an IR page.

**Hierarchical** (`dotgen/DotHierarchicalCodegen.scala:11-95`): `entryFile = "Top.dot"`. Each control node gets its own `.dot` file; its body emits into `scope(Some(lhs))`. The critical algorithm is `addEdge` (lines 54-80): when a target node is outside the current scope, it uses `ancestryBetween(from, to)` to compute `(shared, fromBranch, toBranch)` and registers the edge in every scope along both branches, adding `externNode` stubs for the foreign endpoints. The LCA is `shared.headOption`. `ancestryBetween` (lines 47-52) walks `sym.blk.s` up via `ancestors` (lines 38-41), then splits ancestors into shared vs per-branch by intersect.

**Spatial overlay** (`dotgen/DotGenSpatial.scala:9-103`): `inputs(lhs)` adds DRAM consumers, stream-in consumers, memory writers (lines 11-28). `nodeAttr(lhs)` colors `SRAM/LockSRAM/MergeBuffer/RegFile/LUT` → `forestgreen`; `Lock` → `crimson`; `Reg` → `chartreuse2`; `FIFO/FIFOReg/StreamIn/StreamOut` → `gold`; `DRAM` → `blueviolet` (lines 30-42) — all `shape=box`. `label(lhs)` concatenates src ctx; for Counter/DRAMAddress includes par info. `inputGroups(lhs)` partitions node inputs into named sub-nodes (`data`, `bank`, `ofs`, `enss`, `ens`, `selects`) so each edge bundle gets its own invhouse-shaped group-node emitter.

Concrete classes (`dotgen/DotGenSpatial.scala:102-103`): `case class DotFlatGenSpatial(IR: State) extends DotFlatCodegen with DotGenSpatial` and `case class DotHierarchicalGenSpatial(IR: State) extends DotHierarchicalCodegen with DotGenSpatial`.

**HtmlIRGen**: `HtmlIRCodegen` (`dotgen/HtmlIRGen.scala:6-107`) is a generic per-sym HTML dump: each symbol becomes `<h3 id="$sym">$sym = $op</h3>` plus a metadata table with every `Data` on the symbol. `HtmlIRGenSpatial` (`dotgen/HtmlIRGenSpatial.scala:10-134`) specializes `quote` to wrap each symbol in `<a href="$filename.html#$q">` so the rendered HTML is cross-linked to the dot SVGs, overrides `emitMeta` to link each symbol to its parent dot graph (scope file), and produces a `Duplicates` expansion with nested banking details. It also dumps per-memory metadata into a separate `Mem.html` file via `inGen(out, "Mem.$ext")` at `HtmlIRGenSpatial.scala:97-131`.

**DotHtmlCodegen** (`dotgen/DotHtmlCodegen.scala:6-34`) is a dead-looking object: loads a rendered SVG with `scala.xml.XML.loadFile`, applies a `RewriteRule` that prints titles and noops on rect-shaped nodes. Never referenced from the codegen pipeline — appears to be abandoned tooltip-injection code.

### 15. Treegen: the controller tree

`TreeGen` (`treegen/TreeGen.scala:19-267`) is the human-facing controller visualization. Extends `AccelTraversal with argon.codegen.Codegen` — notably does NOT extend `NamedCodegen` (unlike every other `AccelTraversal`-based codegen). Constructor has two optional args: `filename = "controller_tree"`, `IRFile = "IR"` (line 19). The latter is used for `link(s: String) = s"<a href=$IRFile.html#$s target=_blank>$s</a>"` (line 88), cross-linking to HtmlIRGenSpatial's output.

The mechanics:

- `gen(lhs, rhs)` (lines 40-46): only matches `AccelScope`, `SpatialCtrlBlackboxUse`, `Control[_] if inHw`, and `MemAlloc[_,_] if inHw` — everything else recurses into blocks. Memory-seeing path calls `logMem` (lines 98-114) which reads `lhs.instance.depth` and either `assignColor(lhs)` with a random index into the 23-color palette if depth > 1 (nBuf), or `assignColor(lhs, Some(0))` for non-buffered mems (going into `nonBufMems: mutable.Set`).
- `memColors` (lines 28-31): a 23-entry palette of hex strings (pastel blues/greens/pinks/purples/yellows). Used as a repeating palette for NBuf memories.
- `swappers: HashMap[Sym,Set[Sym]]` (line 24) — map from controller sym to the set of NBuf memories it swaps. Populated by `logMem` reading `lhs.swappers` (line 102-104).
- `printControl` (lines 116-157) emits the collapsible `<TD>` cell with a `<font size="6">` header showing the link, schedule, operation name, level, ctx, source line, plus `Latency=${lat}, II=${ii}` (bolded if > 1) + `CompilerII` if mismatched.
- `print_stream_info` (lines 159-177) puts the pushes/listens into a `<div style="border:1px solid black">`; `readers` include both regular `getReadStreams` and `getReadPriorityStreams` (unwrapped as `prDeq[...]`).
- `emitHeader` (lines 181-202) writes the jQuery Mobile 1.4.5 bootstrap: `<link rel="stylesheet" href="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">`, `<script src="http://code.jquery.com/jquery-1.11.3.min.js">`. That's three remote-CDN requests at page load — an unusual choice for a build-time artifact.
- `emitFooter` (lines 208-266) after closing the tree emits two summary tables: "NBuf Mems" (from `swappers`) and "Single-Buffered Mems" (from `nonBufMems`), each sorted by total volume descending. For each, computes `histR`/`histW`: muxwidth histograms of read/write lanes (using `residualGenerators`, `port.broadcast`, and `nBanks`) and emits a 3-column CSS-grid `<div>` with `[muxwidth, # R lanes, # W Lanes]`.

### 16. NamedCodegen

`naming/NamedCodegen.scala:13-108`. Trait. Overrides `named(s: Sym[_], id: Int): String` to produce Spatial-specific identifiers. Each case reads `s.op` and returns a suffixed string:

- Controllers: `AccelScope` → `${s}_inr_RootController${s._name}` (inner) or `${s}_outr_RootController${s._name}` (outer); similarly for `UnitPipe`, `UnrolledForeach → ...Foreach...`, `UnrolledReduce → ...Reduce...`, `Switch`, `SwitchCase`, `StateMachine → ...FSM...`.
- Counters: `CounterNew` → `${s}_ctr`; `CounterChainNew` → `${s}_ctrchain`.
- Memories: `RegNew` → `${memNameOr(s,"reg")}`; `SRAMNew` → `${memNameOr(s,"sram")}` with suffix `_dualread` if `spatialConfig.dualReadPort || s.isDualPortedRead` (line 47).
- `memNameOr(s, default)` (lines 18-21): `${s}_${s.nameOr(default)}${s.explicitName.getOrElse("").replace("Const(","").replace("\"","").replace(")","")}` — appends user-provided explicit names with string sanitization.
- Accessors: `FIFOBankedEnq(fifo,_,_)` → `${s}_${s.nameOr(s"enq_${local(fifo)}")}`, etc. (lines 61-79).
- Math: `FixAdd` → `${s}_${s.nameOr("sum")}`, `FixSub → sub`, `FixMul → mul`, `FixDiv → div`, `FixNeg(x) → neg$x` (lines 87-92).
- Blackbox: `SpatialCtrlBlackboxImpl → ${s}_sctrlbox_${nameOr("impl")}`, `SpatialCtrlBlackboxUse(_,box,_) → ${s}_${box}_${nameOr("use")}` (lines 94-99).
- `DelayLine(size, data)` where `data.isConst` → `src"$data"` (line 101) — collapses constant-delayed values to just their data literal.

Mixin consumers: `ChiselCodegen`, `ScalaCodegen`, `ResourceReporter`, `ResourceCountReporter` all `extends NamedCodegen`. Pirgen / roguegen / dotgen / treegen / tsthgen do NOT extend it (though tsthgen transitively does through `CppCodegen`, which transitively inherits through `CppGenCommon`'s mixin chain — wait no, `CppCodegen extends FileDependencies with AccelTraversal`, no Named. Let me double check — actually `chiselgen` inherits NamedCodegen, but cppgen does not; cppgen's quoting is its own. Tsthgen extends CppCodegen, so also does not inherit Named). **This is important**: Rogue, PIR, Dot, Tree, Cppgen, and Tsthgen all use Argon's default `named`, which just returns `"x${id}"`. Only the Chisel/Scala/Resource side of the compiler uses the Spatial-aware identifier scheme.

### 17. Resourcegen: area and count reports

**`ResourceReporter`** (`resourcegen/ResourceReporter.scala:17-198`) — ML-area-model-driven resource estimation. `case class ResourceArea(LUT, Reg, BRAM, DSP)` with `.and(other)` additive combinator (lines 17-20). Constructor takes `AreaEstimator` (from `models.AreaEstimator`).

- `estimateMem(mem)` (lines 61-105) — computes `histR`/`histW` muxwidth histograms (same formula as TreeGen.emitFooter, lines 70-71), flattens into `histRaw: List[Int]` (line 74), then pattern-matches mem type and calls `areamodel.estimateMem(category, memKind, dims, bitwidth, depth, Bs, nBanks, alphas, Ps, histRaw)` for `"LUTs"`/`"FFs"`/`"RAMB18"`/`"RAMB32"` for SRAM, RegFile, LineBuffer, FIFO. `RegNew` hard-codes `ResourceArea(0, 1, 0, 0)` (line 97). BRAM is the sum of `RAMB18 + RAMB32` estimates.
- `estimateArea(block)` (lines 107-181) — recurses into controllers via `inCtrl(x){ x.blocks.map(estimateArea).fold(...)(_.and(_)) }`. For each `MemAlloc` calls `estimateMem`. For `FixMul`, `FixDiv`, `FixMod`, `FixSub`, `FixAdd`, `FixFMA`, `FixToFix` calls `areamodel.estimateArithmetic("LUTs|FFs|RAMB18|RAMB32|DSPs", opName, List(0,0,bitWidth(tp),0,1))`.
- `gen(lhs, rhs)` (lines 183-194) only matches `AccelScope`, runs `inAccel { inCtrl { spatialConfig.enGen = true; val area = estimateArea(func); emit(s"Total area: $area"); spatialConfig.enGen = false; area } }`. **Side effect: toggles `spatialConfig.enGen` to force gen to actually emit — an unusual coupling.**
- Output: a plain-text hierarchical report, one entry per controller, with `$ctrler total area: ResourceArea(...)` summaries. The `ext = "json"` is misleading — the content is plain text with the `.json` extension (line 24).

**`ResourceCountReporter`** (`resourcegen/ResourceCountReporter.scala:19-161`) — simpler histogram variant. Emits JSON:

- `dataMap: mutable.Map[String, mutable.Map[String, String]]` (line 39) — two-level map: category → sym → csv-string.
- `countResource` (lines 85-157): per-mem-type calls `emitMem(lhs, "bram", constDims, padding, depth)` for SRAM/FIFO/LIFO/LineBuffer/RegFile, `"reg"` for Reg/FIFOReg/LUT/MergeBuffer. For every fix-arithmetic op (`FixAdd`, `FixSub`, ..., `FixSigmoid`), `fixOp += 1`.
- `emitFooter` (lines 41-58): writes JSON `{ "bram": { "sym1": [bitwidth, [dims], [padding], depth], ... }, "reg": { ... }, "fixed_ops": N }`.

Both reporters mix in `NamedCodegen` (lines 22, 19) — their sym names in the output use the Spatial identifier scheme.

### 18. Integration matrix — which flag turns which generator on?

From `spatial/Spatial.scala:241-252`:

```
treeCodegen         ==>                              // always runs
irCodegen           ==>                              // always runs
enableFlatDot       ? dotFlatGen ==>
enableDot           ? dotHierGen ==>
enableSim           ? scalaCodegen ==>
enableSynth         ? chiselCodegen ==>
enableSynth && target.host == "cpp"  ? cppCodegen ==>
target.host == "rogue"               ? rogueCodegen ==>
reportArea          ? resourceReporter ==>
countResources      ? ResourceCountReporter(state) ==>
enablePIR           ? pirCodegen ==>
enableTsth          ? tsthCodegen
```

`HardwareTarget.host = "cpp"` by default (`targets/HardwareTarget.scala:10`); `KCU1500` overrides to `"rogue"` (`targets/xilinx/KCU1500.scala:7`). `createDump(n)` (`Spatial.scala:136`) is `Seq(TreeGen(state, n, s"${n}_IR"), HtmlIRGenSpatial(state, s"${n}_IR"))` — called at 6 pipeline checkpoints (`PreEarlyUnroll`, `PreFlatten`, `PostStream`, `PostInit`, `PreExecution`, `PostExecution`) to dump intermediate IR for debugging.

## Open questions

Filed to `20 - Research Notes/10 - Deep Dives/open-questions-other-codegens.md`:

1. **PIRGenLineBuffer omitted from PIRGenSpatial mixin list**: file exists, has error checks, but never runs.
2. **PIRGenVec.VecSlice "end is non-inclusive" comment contradicts the code**: `vector.slice(start, end+1)` plus the comment says end is non-inclusive — ambiguous intent.
3. **PIR's `bug(...)` and `error(...)` calls return normally**: do they actually abort compilation, or produce malformed output and proceed?
4. **Treegen uses jQuery Mobile 1.4.5 over HTTP CDN**: why not vendor the JS/CSS locally? Offline builds would fail to render.
5. **DotHtmlCodegen is an unreferenced object**: is it dead code or invoked via reflection / external sbt task?
6. **Cppgen `int256_t` handling**: `asIntType` produces `"int256_t"` for width-256 types, but `structs.hpp` only typedefs `int128_t`. Is `int256_t` defined somewhere I haven't seen?
7. **Cppgen's `remap` turns every fractional FixPt into `double`**: which means cppgen's host-side numerics silently diverge from the bit-exact FPGA side for non-power-of-2 fractions. What invariant protects against this?
8. **Rogue `SetMem`/`GetMem` are empty case handlers** (`RogueGenInterface.scala:73-74`): which means mem transfers silently emit nothing. Is the expected path exclusively through Frame?
9. **Tsthgen `AccelScope` emits only `RunAccel();`**: no lowered body. Where does `RunAccel()` come from — a hand-written Tungsten runtime library, or something synthesized by pirgen? Presumably the latter (tsthgen + pirgen pair up), but that coupling isn't documented.
10. **Tsthgen's `float`/`double` coercion by width is semantically lossy**: how does it match PIR-side fixed-point behavior? PIR ostensibly preserves fixed-point in its Plasticine stack, so the tsthgen host side is using a different numeric representation than the accel — cast boundary at `RunAccel()` presumably.
11. **Rogue's TCP port formula `8000 + ($tdest+1)*2 + $tid * 512` has a collision mode**: for `tid > 0` and large `tdest`, ports above 65535 collide with stack. Is the typical Spatial app small enough to avoid this?
12. **Pirgen errors at codegen for FIFO status ops**: what does the user see? `argon.error` is a reporting-level function, not a throw. Likely compilation continues with bad output.

## Distillation plan

- Cppgen overview → `10 - Spec/50 - Code Generation/30 - Cppgen/10 - Cppgen.md` — host emission surface, trait mixin composition, file layout.
- Cppgen per-target fan-out → `10 - Spec/50 - Code Generation/30 - Cppgen/20 - Per-Target Files.md` — `copyDependencies`, 9-target matrix, build harness.
- Pirgen overview → `10 - Spec/50 - Code Generation/40 - Pirgen/10 - Pirgen.md` — DSL shape, `state/alias`, `stateMem/stateAccess`, split chunking, Lock/MergeBuffer, width-1 vector invariant, unsupported ops.
- Visualization backends → `10 - Spec/50 - Code Generation/50 - Other Codegens.md` — Roguegen + Tsthgen + Dotgen + Treegen + HtmlIRGenSpatial consolidated.
- Naming and resource reports → `10 - Spec/50 - Code Generation/20 - Scalagen/70 - Naming and Resource Reports.md` — `NamedCodegen` identifier grammar; `ResourceReporter` + `ResourceCountReporter`.
