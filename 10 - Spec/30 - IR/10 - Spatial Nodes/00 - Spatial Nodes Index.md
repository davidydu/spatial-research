---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Spatial Nodes — Index

Per-node entries for IR ops defined under `src/spatial/node/`.

## Categories

- `10 - Controllers/` — `AccelScope`, `UnitPipe`, `ParallelPipe`, `OpForeach`/`UnrolledForeach`, `OpReduce`/`UnrolledReduce`, `OpMemReduce`, `StateMachine`, `Switch`/`SwitchCase`.
- `20 - Memories/` — alloc nodes: `SRAMNew`, `DRAMHostNew`/`DRAMAccelNew`/`DRAMAlloc`/`DRAMDealloc`, `RegNew`/`RegFileNew`, `FIFONew`/`LIFONew`/`FIFORegNew`, `LineBufferNew`, `LUTNew`/`FileLUTNew`, `MergeBufferNew`, `LockSRAMNew`/`LockDRAMNew`, `StreamInNew`/`StreamOutNew`, `FrameNew`.
- `30 - Memory Accesses/` — dense, sparse, vector, banked variants; `*Read`, `*Write`, `*BankedRead`, `*BankedWrite`, `SetReg`/`GetReg`, `*Enq`/`*Deq`/`*EnqVec`/`*DeqVec`, `DenseTransfer`/`SparseTransfer`, `FrameTransmit`, `MemDenseAlias`/`MemSparseAlias`.
- `40 - Counters and Iterators/` — `CounterNew`, `CounterChainNew`, `ForeverNew`, `LaneStatic`.
- `50 - Arithmetic and Primitives/` — mostly reused from argon (`Fix*`/`Flt*`/`Bit*`); Spatial-specific additions (`RegAccumOp`/`RegAccumFMA`, `OneHotMux`, `PriorityMux`, `DelayLine`, `RetimeGate`, `ShuffleCompress`).
- `60 - Streams/` — stream dequeue (`FieldDeq`), `StreamIn.value`, `StreamOut := `, stream-based transfer.
- `70 - Blackboxes/` — `SpatialBlackboxImpl`, `SpatialBlackboxUse`, `VerilogBlackbox`, `BlackboxImpl`, boundary config.
- `80 - Host Ops/` — `ArrayNew`, `ArrayApply`, `ArrayUpdate`, `ArrayMap`, `ArrayReduce`, `ArrayFilter`, `ArrayFlatMap`, `ArrayZip`, `ArrayMkString`, `MatrixNew`, file I/O nodes.
- `90 - Debugging/` — `PrintIf`, `AssertIf`, `BreakpointIf`, `ExitIf`, instrumentation counters.

## Metadata (separate index)

→ [[20 - Metadata/00 - Metadata Index]]

## Source

- `src/spatial/node/` (core node definitions)
- [[spatial-ir-coverage]] — Phase 1 coverage note
