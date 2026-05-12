---
type: spec
concept: chiselgen-math-and-primitives
source_files:
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:17-22"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:24-105"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:107-275"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:155-168"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDelay.scala:1-37"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenStruct.scala:9-46"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenVec.scala:7-43"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:19-73"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:74-165"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:166-211"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenBlackbox.scala:240-314"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenDebug.scala:1-43"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:63-70"
  - "spatial/src/spatial/codegen/chiselgen/ChiselGenCommon.scala:281-300"
source_notes:
  - "[[chiselgen]]"
hls_status: chisel-specific
depends_on:
  - "[[10 - Overview]]"
  - "[[20 - Types and Ports]]"
status: draft
---

# Chiselgen — Math and Primitives

## Summary

This entry covers the per-node primitive emitters: `ChiselGenMath` (every fixed-point and floating-point arithmetic op), `ChiselGenDelay` (the retiming `DelayLine` glue), `ChiselGenStruct` (struct packing/unpacking via `ConvAndCat`), `ChiselGenVec` (vector alloc/apply/slice/concat/popcount/shuffle), `ChiselGenBlackbox` (Verilog and Spatial blackbox wrappers), and `ChiselGenDebug` (text/print stubs and breakpoint registration). Math ops uniformly route through `Math.<op>(x, y, lat, backpressure, …, "name")` calls with per-op latency looked up via `latencyOption(op, Some(bitWidth))` from the target's latency model. The retiming wrapper `DL(name, latency, isBit)` switches between `.DS(lat, rr, bp & fp)` for single-bit values and `getRetimed(...)` for words. Math, delay, and blackbox emission all participate in the global `maxretime` accumulator that drives `accelUnit.max_latency` for the retime counter. Debug ops are silent on the accelerator (every text/print compiles to `val $lhs = ""`) except for early-exit registrations into the breakpoint Vec.

## Semantics

### `ChiselGenMath` — per-op latency-aware arithmetic

Every fixed/float arithmetic op flows through `MathDL(lhs, rhs, nodelat)` at `ChiselGenMath.scala:24-105`. The dispatch at lines 107-275 computes `nodelat` from `latencyOption(op, Some(bitWidth(lhs.tp)))` and forwards to `MathDL`.

`latencyOption(op, b)` at `ChiselGenCommon.scala:63-70` reads `spatialConfig.target.latencyModel.exactModel(op)("b" -> b.get)("LatencyOf")` when retiming is enabled, else 0.0. The latency model is per-target — the same op name `"FixMul"` maps to different latencies on Zynq, ZCU, ASIC, or VCS.

`MathDL` emits a wire declaration and the `Math.<op>(x, y, $lat, $backpressure, [Rounding, Overflow,] "$lhs")` call. `$lat` is `Some($nodelat)` unless rounding integer-casts disagree, in which case `Some($nodelat + 1.0)` (line 31). The rounding/overflow modes are part of the op constructor name in Spatial IR:

- `FixMul`/`UnbMul`/`SatMul`/`UnbSatMul` → `Math.mul(x, y, $lat, $bp, {Truncate|Unbiased}, {Wrapping|Saturating}, "$lhs")`.
- Same for `Div`/`Mod` variants.

Floating ops route through `Math.fadd`/`fsub`/`fmul`/`fdiv`/`fsqrt`/`feql`/`flt`/`flte`/`fneq`. Comparisons `FixLst`/`FixLeq`/`FixEql`/`FixNeq` become `Math.lt`/`lte`/`eql`/`neq`. Conversions: `FixToFix(x, fmt)` → `Math.fix2fix(x, sign, ibits, fbits, $lat, $bp, Truncate, Wrapping, "$lhs")`. `FixToFlt`/`FltToFix`/`FltToFlt` similar (lines 92-102).

### `ensig` deduplication

`newEnsig(code)` at `ChiselGenMath.scala:17-22` is a per-controller dedup table for back-pressure expressions: emit `val ensig<N> = Wire(Bool()); ensig<N> := $code` once, reuse the name on every subsequent occurrence. In `MathDL` (lines 28-30), the back-pressure raw expression is checked against the existing `ensigs` list; if already emitted, reuse `ensig<N>`. This saves significant code size in inner loops where every Math op uses the same back-pressure composition. `ensigs` is reset in `enterCtrl(lhs)` at `ChiselGenCommon.scala:76` so the table is per-controller.

### Shifts and special ops

Shifts (`FixSLA`/`FixSRA`/`FixDivSRA`/`FixSRU`) require the shift amount to be a constant or parameter, traced via `DLTrace` (`ChiselGenCommon.scala:281-286`); a non-constant shift throws (`ChiselGenMath.scala:79-90`). The `replaceAll` strips Spatial constant suffixes (`.FP(s,d,f)`, `.U(W)`, `.S(W)`, trailing `L`).

`FixRandom`/`BitRandom` (`ChiselGenMath.scala:153-168`) synthesize a `Module(new PRNG($seed))` with `$seed = (scala.math.random*1000).toInt` — a host-time-dependent RNG seed picked at codegen time. Bitstreams compiled at different times produce different RNG sequences.

`FixAbs(x)` → `Mux(x < 0.U, -x, x)`. `FixFloor`/`FixCeil` take integer-decimal bits and zero-pad the fraction. `DataAsBits`/`DataAsVec`/`VecAsData`/`BitsAsData` (lines 259-267) reshape between bit and vector views. `FixRecipSqrt` composes two Math calls (line 49): `Math.div(<lhs>_one, Math.sqrt(x, sqrtLat, bp), divLat, bp, …)`.

### `ChiselGenDelay` — `DelayLine` → `getRetimed`

`ChiselGenDelay.gen` at `ChiselGenDelay.scala:16-34` handles `DelayLine(delay, data)`:

- If the data is a `Const` or `Param`, do nothing — constants have no clock-domain mapping that needs delaying.
- Otherwise, bump `maxretime = max(maxretime, delay)` and emit:

```scala
val $lhs = Wire(<tp>).suggestName("${lhs}_<dataname>_D<delay>")
// for Vec data:
(0 until <width>).foreach{i => ${lhs}(i).r := DL(${data}(i).r, delay)}
// for non-Vec:
${lhs}.r := DL(${data}.r, delay, false)
```

`maxretime` is later emitted in `AccelWrapper.scala` as `val max_latency = $maxretime` (`ChiselGenController.scala:564`). This sets the size of the `retime_counter` instantiated at `AccelScope` (`ChiselGenController.scala:378-380`) — it counts up to `max_latency` and then sets `rr` (retime-released), which gates the start of any datapath operation that uses retimed signals.

### `DL(name, latency, isBit=false)` and `DLo`

`DL` at `ChiselGenCommon.scala:288-293`: for single-bit values, emits `($name).DS($lat.toInt, rr, bpressure & fpressure)` (the Fringe `.DS` shift register). For multi-bit words, `getRetimed($name, $lat.toInt, bpressure & fpressure)`. The `rr` retime-released bit is *only* AND'd into `.DS`, not into `getRetimed` — bit-domain registers are part of the controller's idle state, while retimed words don't gate on global retime release.

The `forwardpressure` term is conditional on `controllerStack.head.haltIfStarved` — the metadata bit set when a controller's body must halt rather than tolerate stale data. Without it, a starving controller is allowed to keep iterating with stale values. `ChiselGenMem.implicitEnableWrite` (`ChiselGenMem.scala:45-51`) similarly gates on `haltIfStarved`.

`DLo(name, latency, smname, isBit)` at `ChiselGenCommon.scala:296-300` is the cross-controller variant — emits delays on a parent's signal while we're emitting in a child's scope. Back-pressure is read off `<smname>.sm.io.backpressure` (the parent's SM module). Used in `connectChains` (`ChiselGenController.scala:40-45`).

### `ChiselGenStruct` — `ConvAndCat` packing

`ChiselGenStruct.gen` at `ChiselGenStruct.scala:16-44`:

- **`SimpleStruct(fields)`**: packs fields into `UInt(<bitWidth>.W)` via `ConvAndCat`, with field order reversed for big-endian packing (line 19).
- **`SimpleStreamStruct(fields)`**: builds a `Wire(Flipped(new StreamStructInterface(Map("name" -> width, …))))` with bits/valid/active/ready/activeIn plumbing per field — the analogue of `SimpleStruct` for blackbox stream interfaces.
- **`FieldDeq(struct, field, ens)`**: reads bits, sets ready via `$ens & ~$break && DL($datapathEn & $iiIssue, fullDelay, true)`, sets activeIn, plus `Ledger.connectStructPort($struct.hashCode, "$field")` so the runtime ledger can fan-in this partial connection.
- **`FieldApply(struct, field)`**: a plain bit-range extract: `$lhs.r := $struct($start, $end)` where `(start, end) = getField(struct.tp, field)` (`ChiselGenCommon.scala:180-188`).

### `ChiselGenVec` — vector ops

`ChiselGenVec.gen` at `ChiselGenVec.scala:9-41`: `VecAlloc` → `VecInit($elems)`. `VecSlice(vec, start, stop)` → `$lhs.zipWithIndex.foreach{case(w,i) => w := $vec(i+$stop)}` (note: anchored at `stop`, not `start`). `VecConcat(list)` → zips inputs concatenated as Scala lists. `VecApply` → indexed read. `ShuffleCompressVec` calls `Shuffle.compress(Vec($data), Vec($mask))` and recombines. `BitsPopcount` uses Chisel's `PopCount(Seq($data))`.

### `ChiselGenBlackbox` — Verilog and Spatial blackbox wrappers

Four blackbox node kinds:

**`VerilogBlackbox(inputs)`** at `ChiselGenBlackbox.scala:20-73` — pure-combinational user-supplied Verilog. Emits `bb_<lhs>.scala` with two nested classes: a `<bbName>_<lhs>_wrapper()` Chisel `Module` with the user's input/output fields as plain `Input(UInt)`/`Output(UInt)` ports, and the actual `<bbName>(params: Map[String, chisel3.core.Param]) extends BlackBox(params)` class — only emitted once per unique `bbName` (tracked by `createdBoxes: ArrayBuffer[String]` at line 17). The blackbox class runs `Files.copy(<userVerilogFile>, System.getProperty("user.dir") + "/<filename>", REPLACE_EXISTING)` at elaboration time so the Verilog source ends up in the build directory. The use site instantiates the wrapper, wires clock/reset, slices packed inputs into per-field wires, and Cat's outputs into `val $lhs = Cat(<outputs>)`.

**`VerilogCtrlBlackbox(ens, inputs)`** at lines 74-165 — Verilog that's also a controller. The wrapper exposes `enable`/`done` plus a `StreamStructInterface` for I/O (each field has its own `valid`/`ready`). The use site wires `<lhs>_bbox.io.enable := io.sigsIn.smEnableOuts(<idx>) & <ens>` and routes `<lhs>_bbox.io.done` into `io.sigsOut.cchainEnable(<idx>)` (for loops) or `io.sigsOut.smCtrCopyDone(<idx>)`.

**`SpatialBlackboxImpl(func)`** at lines 166-211 — a "blackbox" written in Spatial syntax. Codegen recursively descends into `func`. The wrapping is `class $lhs(PARAMS: Map[String, Any])(implicit stack) extends Module()`. The input is reconstituted via `Cat(io.in_<f0>, io.in_<f1>, …)`, then `gen(func)` emits the body, and per-output-field bit-range extracts: `io.<field> := $func.result($start, $end).r`.

**`SpatialCtrlBlackboxImpl(func)`** at lines 240-314 — the controlled spatial blackbox. Throws if `!enableModular` (line 242) — see Q-cgs-13. Mirrors `writeKernelClass`: `<lhs>_kernel(in, PARAMS, parent, cchain, childId, …, rr) extends Kernel`, with inner abstract `<lhs>_module(depth)` and concrete `<lhs>_concrete(depth)` carrying `gen(func)`. The corresponding `SpatialCtrlBlackboxUse` (lines 316-344) mirrors `instantiateKernel`: emits the bbox, wires `ctrDone := risingEdge(...)`, sets `backpressure`/`forwardpressure`/`break`/`mask`/`configure`, calls `kernel()`.

`FetchBlackboxParam(field)` (line 346) emits `$lhs := PARAMS("$field").asInstanceOf[scala.Float].FP(s, d, f).r` for elaboration-time parameter lookup.

### `ChiselGenDebug` — silent text + breakpoints

`ChiselGenDebug.gen` at `ChiselGenDebug.scala:12-43` mostly stubs everything out. Text/print/var ops compile to `val $lhs = ""`:

- `FixToText`, `TextConcat`, `PrintIf`, `BitToText`, `GenericToText`.
- `VarNew`, `VarRead`, `VarAssign`.

The accelerator does no host-side I/O during execution; these ops are simulator-only and the chiselgen path makes them no-ops.

`RetimeGate()` (line 27) emits a comment-only line: `// RETIME GATE ----------------`.

The non-stub debug ops register breakpoints into the `breakpoints` Vec via `Ledger.tieBreakpoint`:

- **`ExitIf(en)`** (lines 22-25): `Ledger.tieBreakpoint(breakpoints, <N>, <ens> & ($datapathEn).D(<lhs.fullDelay>))`, then appends `lhs` to `earlyExits`.
- **`AssertIf(en, cond, _)`** (lines 29-34): same as `ExitIf` but with `& ~<cond>` — a failed assertion is a breakpoint.
- **`BreakpointIf(en)`** (lines 36-39): same as `ExitIf`. The semantic difference between `ExitIf` and `BreakpointIf` is in the breakpoint context map (which is emitted in `Instantiator.scala` as `/* Breakpoint Contexts */`), not in the runtime trigger.

`earlyExits` is consumed in `ChiselGenController.AccelScope` (lines 398-407): if non-empty, register `HasBreakpoint`, emit per-exit `argOuts(api.<exit>_exit_arg)` wirings, and feed `breakpoints.reduce{_|_}` into the `done_latch` so any breakpoint terminates the accelerator.

## Interactions

- **Latency model**: `ChiselGenMath` reads `spatialConfig.target.latencyModel.exactModel(op)("b" -> b.get)("LatencyOf")` — the same model that fed `lhs.bodyLatency` upstream during retiming analysis. The two views must agree, otherwise the codegen-emitted latency disagrees with the IR's recorded latency.
- **`maxretime`**: bumped by every `DelayLine`, written into `AccelWrapper.scala` as `val max_latency`, used to size the AccelScope's `retime_counter`.
- **`earlyExits`**: bumped by `ChiselGenDebug` (and indirectly by `ChiselGenController.AccelScope`'s breakpoint wiring), consumed by `ChiselGenController.emitPostMain` and `ChiselGenInterface.emitPostMain` (which writes the per-exit `<SYM>_exit_arg` index into `ArgAPI.scala`).
- **`createdBoxes`**: per-Verilog-file dedup so each unique blackbox file is copied/declared only once across multiple `VerilogBlackbox` use sites.

## HLS notes

The per-op latency lookup is the cleanest Spatial-to-HLS handoff: every Math.<op> call has a single integer latency parameter, and HLS pragmas can directly target this same number. The `ensigs` deduplication is a textual code-size optimization with no semantic content. The `DelayLine` → `getRetimed` translation only matters in Chisel because retiming is implemented as explicit shift registers; in HLS, the retiming pragma replaces the explicit `DelayLine` insertion entirely. Blackbox emission is the single largest portability cliff: Verilog blackboxes have no HLS analogue and must be wrapped in HLS-compatible kernels. Spatial blackboxes (which are written in Spatial syntax) translate naturally if the inner `gen(func)` recursively descends.

`SpatialCtrlBlackboxImpl` requiring `enableModular` is a strong signal that any HLS port should standardize on the modular kernel shape — see open question Q-cgs-13.

## Open questions

See `20 - Research Notes/10 - Deep Dives/open-questions-chiselgen.md`:
- Q-cgs-13: `SpatialCtrlBlackboxImpl` requires `enableModular`. Is the non-modular path effectively dead?
- Q-cgs-14: `FixRandom` uses a host-time-dependent seed picked at codegen time. Is that the intended semantics?
