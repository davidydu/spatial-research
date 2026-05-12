---
type: spec
concept: blackbox-lowering
source_files:
  - "src/spatial/Spatial.scala:101-105"
  - "src/spatial/Spatial.scala:171-188"
  - "src/spatial/Spatial.scala:196-200"
  - "src/spatial/transform/BlackboxLowering.scala:12-81"
  - "src/spatial/transform/MemoryDealiasing.scala:12-163"
  - "src/spatial/transform/LaneStaticTransformer.scala:24-75"
  - "src/spatial/transform/StreamTransformer.scala:14-88"
  - "src/spatial/transform/StreamConditionSplitTransformer.scala:7-11"
  - "src/spatial/node/DenseTransfer.scala:34-63"
  - "src/spatial/node/SparseTransfer.scala:27-44"
  - "src/spatial/node/FrameTransmit.scala:26-43"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[30 - Switch and Conditional]]"
  - "[[50 - Pipe Insertion]]"
  - "[[70 - Banking]]"
status: draft
---

# Blackbox Lowering

## Summary

This entry covers the lowering cluster around early blackboxes, aliases, lane-static arithmetic, and stream-counter distribution. Spatial constructs two `BlackboxLowering` instances, one with `lowerTransfers = false` and one with `lowerTransfers = true`; they run back-to-back after the first switch optimization round (`src/spatial/Spatial.scala:101-104`, `src/spatial/Spatial.scala:171-175`). `MemoryDealiasing` and `LaneStaticTransformer` run later in the second lowering round before pipe insertion, and `LaneStaticTransformer` is gated by `!spatialConfig.vecInnerLoop` (`src/spatial/Spatial.scala:185-188`). `StreamTransformer` is a later stream-controller rewrite gated by `spatialConfig.distributeStreamCtr`, and `StreamConditionSplitTransformer` exists but is currently a pass-through stub (`src/spatial/Spatial.scala:196-200`, `src/spatial/transform/StreamConditionSplitTransformer.scala:7-11`).

## Pass list and roles

- `BlackboxLowering` lowers variable shifts in hardware on both invocations and lowers dense, sparse, and frame transfers only when `lowerTransfers` is true (`src/spatial/transform/BlackboxLowering.scala:69-79`).
- `MemoryDealiasing` rewrites dense/sparse memory aliases and alias-derived address/dimension/length/rank/origin/par queries into muxed values, and it rewrites dense-alias reads, writes, resets, and status reads into per-alias operations guarded by alias conditions (`src/spatial/transform/MemoryDealiasing.scala:84-163`).
- `LaneStaticTransformer` runs before unrolling and before pipe insertion to replace arithmetic that will resolve per lane after unrolling with `LaneStatic` nodes (`src/spatial/transform/LaneStaticTransformer.scala:24-29`, `src/spatial/Spatial.scala:188-190`).
- `StreamTransformer` distributes the counter chain of an outer stream `Foreach` into child controllers when stream-counter modification is enabled (`src/spatial/transform/StreamTransformer.scala:14-19`, `src/spatial/transform/StreamTransformer.scala:77-83`).
- `StreamConditionSplitTransformer` simply delegates to `super.transform`, so it currently establishes no behavior beyond traversal (`src/spatial/transform/StreamConditionSplitTransformer.scala:7-11`).

## Algorithms

`BlackboxLowering` has three shift helpers. Constant shifts and PIR-enabled compiles stage the original shift directly; otherwise `expandSLA`, `expandSRA`, and `expandSRU` allocate a `Reg`, iterate `Foreach(abs(b.to[I32]) by 1)`, shift by one per iteration according to the sign of the shift amount, and select the original input when the shift amount is zero (`src/spatial/transform/BlackboxLowering.scala:14-30`, `src/spatial/transform/BlackboxLowering.scala:32-49`, `src/spatial/transform/BlackboxLowering.scala:51-67`). The visitor enters `AccelScope` and blackbox implementations with traversal flags, dispatches `DenseTransfer.lower`, `SparseTransfer.lower`, and `FrameTransmit.lower` only under `lowerTransfers`, and dispatches shift lowering for `FixSLA`, `FixSRA`, and `FixSRU` only in hardware (`src/spatial/transform/BlackboxLowering.scala:69-79`).

The transfer node methods are the actual lowering bodies. `DenseTransfer.lower` calls `DenseTransfer.transfer`; the transfer computes sparse rank, lengths, strides, pars, request length, byte packing information, and rejects non-byte-packable per-cycle widths (`src/spatial/node/DenseTransfer.scala:34-63`, `src/spatial/node/DenseTransfer.scala:79-99`). Dense transfer then builds either `DenseTransfer.Stream.Foreach` over outer counters or a scalar `DenseTransfer.Stream`, marks the emitted top controller as a stream primitive, and records `loweredTransfer` and `loweredTransferSize` metadata (`src/spatial/node/DenseTransfer.scala:100-129`). Its aligned/unaligned store and load paths create command/data/ack streams and call `Fringe.denseStore` or `Fringe.denseLoad` with `transferSyncMeta` (`src/spatial/node/DenseTransfer.scala:163-190`, `src/spatial/node/DenseTransfer.scala:273-320`, `src/spatial/node/DenseTransfer.scala:324-364`).

`SparseTransfer.lower` similarly delegates to `SparseTransfer.transfer`; the transfer creates a `Stream`, computes address streams from sparse addresses and origins, rounds non-PIR iteration counts to a multiple of 16, and emits `Fringe.sparseLoad` or `Fringe.sparseStore` plus receive loops (`src/spatial/node/SparseTransfer.scala:27-44`, `src/spatial/node/SparseTransfer.scala:59-75`, `src/spatial/node/SparseTransfer.scala:79-123`, `src/spatial/node/SparseTransfer.scala:127-168`). `FrameTransmit.lower` delegates to `FrameTransmit.transfer`, rejects non-byte-packable frame element widths, emits a `Stream`, writes stream input data into local memory for loads, or reads local memory and packs `AxiStream64` words for stores (`src/spatial/node/FrameTransmit.scala:26-43`, `src/spatial/node/FrameTransmit.scala:60-87`).

`MemoryDealiasing.readMux` recomputes each alias address by applying the alias series start and step to the requested address, performs one read per candidate memory under `ens + c`, and returns `oneHotMux(conds, reads)` (`src/spatial/transform/MemoryDealiasing.scala:14-35`). `writeDemux` and `resetDemux` perform the symmetric per-candidate writes/resets under `ens + c` (`src/spatial/transform/MemoryDealiasing.scala:37-61`). The main visitor collapses single-member aliases, muxes `DRAMAddress`, `MemDim`, `MemLen`, and sparse origins, returns dense/sparse ranks, and rewrites dense-alias `Reader`, `Writer`, `Resetter`, and `StatusReader` operations (`src/spatial/transform/MemoryDealiasing.scala:84-163`).

`LaneStaticTransformer` handles arithmetic already involving `LaneStatic`: negation, add, subtract, multiply, and shift-left by a final constant all restage a new `LaneStatic` with transformed element values (`src/spatial/transform/LaneStaticTransformer.scala:36-51`). For `FixMod(x, Final(y))` in hardware, it peels simple affine forms such as `x + c`, `x - c`, `c * x`, and `FixFMA(c, x, ofs)`, then checks that the candidate iterator has a counter, has more than one lane, and satisfies `staticMod(mul, iter, y)` before replacing the mod with `LaneStatic(iter, getPosMod(...))` (`src/spatial/transform/LaneStaticTransformer.scala:53-70`). `staticMod` itself requires a static start/step non-forever counter and returns true only when the gcd test proves all lanes resolve to one residue under the modulus (`src/spatial/util/math.scala:40-50`).

`StreamTransformer.injectCtrs` duplicates incoming counters, prepends them to child `CounterChainNew` nodes, registers substituted counter chains, and creates new bound iterator variables with `IndexCounterInfo(ctr, 0 until par)` (`src/spatial/transform/StreamTransformer.scala:21-48`). For nested stream controls it rewrites an outer stream `Foreach` to a `UnitPipe`, and for child `UnitPipe` nodes it creates a new `OpForeach` around the old unit-pipe body and sets outer-control schedules to `Sequenced` (`src/spatial/transform/StreamTransformer.scala:35-67`). The top-level transform refuses the optimization if a child is a controller blackbox or blackbox use, warning and leaving the stream unchanged (`src/spatial/transform/StreamTransformer.scala:77-83`).

## Metadata produced/consumed

Transfer lowering writes `loweredTransfer`, `loweredTransferSize`, and `isStreamPrimitive` on the emitted dense transfer top controllers, and calls `transferSyncMeta` on the newly emitted fringe operation (`src/spatial/node/DenseTransfer.scala:114-129`, `src/spatial/node/DenseTransfer.scala:184-186`, `src/spatial/node/DenseTransfer.scala:337-339`). `MemoryDealiasing` consumes alias conditions, memory lists, and alias ranges and removes most alias reads/writes before unrolling (`src/spatial/transform/MemoryDealiasing.scala:135-163`). `LaneStaticTransformer` emits `LaneStatic` nodes that `AccessExpansion` later resolves to constant unrolled offsets when the unroll id contains the lane-static iterator (`src/spatial/transform/LaneStaticTransformer.scala:65-70`, `src/spatial/traversal/AccessExpansion.scala:26-31`). `StreamTransformer` rewrites counter metadata on newly bound iterators through `IndexCounterInfo` (`src/spatial/transform/StreamTransformer.scala:40-46`, `src/spatial/transform/StreamTransformer.scala:57-63`).

## Invariants established

After the second `BlackboxLowering` pass, encountered dense, sparse, and frame transfer early blackboxes have been lowered to stream/fringe IR rather than left as `EarlyBlackbox` transfer nodes (`src/spatial/transform/BlackboxLowering.scala:72-74`, `src/spatial/node/DenseTransfer.scala:100-129`, `src/spatial/node/SparseTransfer.scala:75-171`, `src/spatial/node/FrameTransmit.scala:65-87`). After `MemoryDealiasing`, dense-alias accesses are explicit one-hot mux/demux operations over concrete memories (`src/spatial/transform/MemoryDealiasing.scala:22-61`, `src/spatial/transform/MemoryDealiasing.scala:135-159`). When `!vecInnerLoop` is true, static lane residues can be represented as transient `LaneStatic` nodes before pipe insertion wraps primitive runs (`src/spatial/Spatial.scala:188-190`, `src/spatial/transform/LaneStaticTransformer.scala:24-29`).

## HLS notes

HLS status is **rework**. Variable shift lowering could map directly to HLS operators if the backend accepts variable shifts; Spatial's fallback loop/reg implementation is a hardware workaround, not a semantic requirement (`src/spatial/transform/BlackboxLowering.scala:20-67`). Transfer lowering is more Spatial-specific because it targets `Fringe.*` nodes and Spatial stream types; an HLS implementation should map the same dense/sparse/frame transfer semantics to `hls::stream`, AXI burst, or vendor DMA interfaces (`src/spatial/node/DenseTransfer.scala:163-190`, `src/spatial/node/SparseTransfer.scala:79-168`, `src/spatial/node/FrameTransmit.scala:65-87`). `LaneStaticTransformer` is conceptually useful for banking and unrolling, but the `!vecInnerLoop` gate is tied to Spatial/PIR vectorization policy (`src/spatial/Spatial.scala:188`, `src/spatial/Spatial.scala:307-315`).

## Open questions

- Q-pp-10 - whether `StreamConditionSplitTransformer` is intentionally reserved for future stream-condition lowering or is obsolete.
