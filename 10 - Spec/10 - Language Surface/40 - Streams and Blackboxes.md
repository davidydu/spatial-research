---
type: spec
concept: streams-and-blackboxes-language-surface
source_files:
  - "src/spatial/lang/StreamIn.scala:1-28"
  - "src/spatial/lang/StreamOut.scala:1-29"
  - "src/spatial/lang/StreamStruct.scala:1-37"
  - "src/spatial/lang/Blackbox.scala:1-124"
  - "src/spatial/lang/Bus.scala:1-87"
  - "src/spatial/metadata/blackbox/BlackboxData.scala:1-17"
  - "src/spatial/metadata/blackbox/package.scala:7-23"
source_notes:
  - "[[language-surface]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Primitives]]"
  - "[[60 - Streams and Blackboxes]]"
status: draft
---

# Streams and Blackboxes

## Summary

This entry documents the DSL-side surface for Spatial streams, stream-structured ports, bus descriptors, and blackbox construction. `StreamIn[A]` and `StreamOut[A]` are both zero-rank local memories and remote memories over a `scala.collection.mutable.Queue[Any]`, which gives them ordinary memory access hooks plus a host/fringe-facing allocation lifetime (`src/spatial/lang/StreamIn.scala:7-12`, `src/spatial/lang/StreamOut.scala:8-13`). `StreamStruct[A]` is a struct-like handle whose field reads lower to per-field dequeue nodes; the source comment states that each field is decoupled and "reading a field is a dequeue operation" (`src/spatial/lang/StreamStruct.scala:7-18`). Blackboxes split into Spatial-defined primitive/controller handles and Verilog primitive/controller uses, with metadata stored as `BlackboxConfig(file, moduleName, latency, pf, params)` on each use symbol (`src/spatial/lang/Blackbox.scala:11-32`, `src/spatial/metadata/blackbox/BlackboxData.scala:6-17`). The IR-node side is covered in [[60 - Streams and Blackboxes]].

## Syntax or API

```scala
val in  = StreamIn[A](bus)                         // StreamIn.scala:26-28
val x   = in.value(); val y = in.value(en)         // StreamIn.scala:14-15

val out = StreamOut[A](bus)                        // StreamOut.scala:27-29
out := data; out := (data, en)                     // StreamOut.scala:15-16

struct.field[F]("name")                            // StreamStruct.scala:17
StreamStruct[S]("a" -> a, "b" -> b)                // StreamStruct.scala:34

Blackbox.SpatialPrimitive[A,B]{ in => out }        // Blackbox.scala:41-49
Blackbox.SpatialController[A,B]{ in => out }       // Blackbox.scala:54-62
Blackbox.VerilogPrimitive(inputs)(file, mod, lat)  // Blackbox.scala:70-74
Blackbox.VerilogController(inputs)(file, mod)      // Blackbox.scala:90-95
Blackbox.GEMM(y,a,b,c,alpha,beta,i,j,k,mt,nt)     // Blackbox.scala:101-119
```

## Semantics

`StreamIn.apply[A](bus)` stages `StreamInNew[A](bus)`, so the bus descriptor is part of allocation rather than a later annotation (`src/spatial/lang/StreamIn.scala:26-28`). `StreamIn.value()` and `StreamIn.value(en)` stage `StreamInRead(this, Set.empty)` and `StreamInRead(this, Set(en))`, respectively (`src/spatial/lang/StreamIn.scala:14-15`). Its memory typeclass read hook ignores addresses and enables and delegates to `value()`, while its write hook emits an error and returns `err[Void]`, making the surface read-only (`src/spatial/lang/StreamIn.scala:17-24`).

`StreamOut.apply[A](bus)` stages `StreamOutNew[A](bus)` (`src/spatial/lang/StreamOut.scala:27-29`). `StreamOut := data` and `StreamOut := (data, en)` stage `StreamOutWrite(this, data, Set.empty)` and `StreamOutWrite(this, data, Set(en))` (`src/spatial/lang/StreamOut.scala:15-16`). Its typeclass write hook stages `StreamOutWrite(this, data, ens)`, while its read hook emits an error and returns `err[A]`, making the surface write-only (`src/spatial/lang/StreamOut.scala:18-25`).

`StreamStruct[A]` exposes named fields through `field[F](name)`, which delegates to `StreamStruct.field[A,F]` (`src/spatial/lang/StreamStruct.scala:17`). The companion `field` stages `FieldDeq[S,A](StreamStruct.tp[S].box(struct), name, Set[Bit]())`, so a field read is a stream dequeue with an empty enable set at the surface (`src/spatial/lang/StreamStruct.scala:31-36`). `field_update` stages `FieldEnq`, but the main user-facing contract in this file is read-as-dequeue (`src/spatial/lang/StreamStruct.scala:34-36`). Equality and inequality compare the per-field `fieldMap` values pairwise and reduce with OR or AND, so equality itself triggers field reads (`src/spatial/lang/StreamStruct.scala:24-28`).

`SpatialBlackbox[A,B]` is a handle over struct inputs and outputs, and `SpatialBlackbox.apply(in, params)` stages `SpatialBlackboxUse[A,B](this, in)` (`src/spatial/lang/Blackbox.scala:11-18`). A curious detail: `SpatialBlackbox.apply` attaches `BlackboxConfig("", None, 0, 0, params)` to the use symbol, leaving file and module name empty and forcing latency/pipeline factor to zero (`src/spatial/lang/Blackbox.scala:15-18`, `src/spatial/metadata/blackbox/BlackboxData.scala:6`). `SpatialCtrlBlackbox.apply` does the same empty-file, empty-module, zero-latency, zero-pipeline-factor metadata attachment for controller uses (`src/spatial/lang/Blackbox.scala:23-30`). This is tracked as Q-lang-08.

`Blackbox.SpatialPrimitive` stages a lambda body from a bound input and returns a `SpatialBlackboxImpl` handle through `stageWithFlow` (`src/spatial/lang/Blackbox.scala:40-49`). `Blackbox.SpatialController` repeats that pattern for `StreamStruct` inputs and outputs and returns a `SpatialCtrlBlackboxImpl` handle (`src/spatial/lang/Blackbox.scala:54-62`). `VerilogPrimitive` stages a `VerilogBlackbox` use immediately and attaches the supplied `file`, optional `moduleName`, `latency`, `pipelineFactor`, and `params` as `BlackboxConfig` (`src/spatial/lang/Blackbox.scala:64-74`). `VerilogController` stages a `VerilogCtrlBlackbox`, attaches `BlackboxConfig(file, moduleName, 1, 1, params)`, and marks the result `rawLevel = Inner` (`src/spatial/lang/Blackbox.scala:77-95`). `GEMM` is a built-in function blackbox: it creates a tunable parameter `PP = 1 (1 -> 16)`, builds `1 until k par PP`, wraps that in a `CounterChain`, and stages `GEMMBox` (`src/spatial/lang/Blackbox.scala:97-119`). `GEMV`, `CONV`, and `SHIFT` are declared but remain `???` stubs (`src/spatial/lang/Blackbox.scala:121-123`).

## Implementation

`Bus` is an abstract `Mirrorable[Bus]` with an `nbits` method and identity `mirror`, so bus objects are staging metadata rather than mutable IR nodes (`src/spatial/lang/Bus.scala:13-16`). `Bus.apply(valid, data*)` constructs a `PinBus` either from `Pin` values or strings converted to `Pin`, and `PinBus.nbits` is the number of data pins (`src/spatial/lang/Bus.scala:18-26`). AXI stream helpers define `AxiStream64`, `AxiStream256`, and `AxiStream512` structs plus data constructors and bus descriptors with fixed `nbits` values of 64, 256, and 512 (`src/spatial/lang/Bus.scala:28-50`). `DRAMBus[A]` computes width from `Bits[A].nbits`, and the burst/gather/scatter bus cases specialize that base for command, acknowledge, data, and address flows (`src/spatial/lang/Bus.scala:57-87`).

File-backed buses are implemented in `Bus.scala` rather than the file IO API. `FileBus[A]` only requires `Bits[A]` and reports `Bits[A].nbits`; it does not inspect struct fields (`src/spatial/lang/Bus.scala:59-63`). `FileEOFBus[A]` performs the construction-time shape check: if `Type[A]` is not a `Struct` whose last field has type `Bit`, it emits an error and calls `state.logError()` (`src/spatial/lang/Bus.scala:64-75`). The requested shorthand "FileBus / FileEOFBus check struct shape" is therefore only confirmed for `FileEOFBus`; `FileBus` is tracked separately as Q-lang-07.

## Interactions

The blackbox metadata API exposes `getBboxInfo`, defaulting `bboxInfo` to `BlackboxConfig("")`, writes metadata through `bboxInfo_=`, and computes `bboxII` from `BlackboxConfig.pf`, a Spatial primitive blackbox's `II`, or `1.0` (`src/spatial/metadata/blackbox/package.scala:9-14`). The same metadata helpers classify symbols as controller blackboxes, blackbox implementations, blackbox uses, or Spatial primitive blackbox implementations by pattern matching on blackbox IR classes (`src/spatial/metadata/blackbox/package.scala:19-22`). `StreamStruct` and controller blackboxes interact directly because `SpatialCtrlBlackbox` and `VerilogController` require `A: StreamStruct, B: StreamStruct`, not ordinary `Struct` (`src/spatial/lang/Blackbox.scala:23-30`, `src/spatial/lang/Blackbox.scala:90-95`).

## HLS notes

`hls_status: rework`. `StreamIn` and `StreamOut` map naturally to `hls::stream<T>` at a high level, but `StreamStruct.field` as a per-field dequeue is a Spatial-specific surface and likely needs an explicit bundle-of-streams model in HLS (inferred, unverified; source behavior at `src/spatial/lang/StreamStruct.scala:17-36`). Verilog blackboxes map to HLS external RTL/IP only if file/module metadata is complete, but Spatial blackbox uses deliberately attach empty file/module metadata and zero latency/pipeline factors at use sites (`src/spatial/lang/Blackbox.scala:15-18`, `src/spatial/lang/Blackbox.scala:27-30`).

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-07 (`FileBus` has no struct-shape check in source), Q-lang-08 (empty `BlackboxConfig` details on Spatial blackbox uses), and Q-lang-09 (`GEMV`/`CONV`/`SHIFT` are declared stubs).
