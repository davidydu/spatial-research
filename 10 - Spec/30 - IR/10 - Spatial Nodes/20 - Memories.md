---
type: spec
concept: spatial-ir-memories
source_files:
  - "src/spatial/node/HierarchyMemory.scala:1-120"
  - "src/spatial/node/Reg.scala:1-61"
  - "src/spatial/node/SRAM.scala:1-70"
  - "src/spatial/node/FIFO.scala:1-71"
  - "src/spatial/node/LIFO.scala:1-34"
  - "src/spatial/node/RegFile.scala:1-131"
  - "src/spatial/node/LUT.scala:1-49"
  - "src/spatial/node/LineBuffer.scala:1-30"
  - "src/spatial/node/MergeBuffer.scala:1-28"
  - "src/spatial/node/DRAM.scala:1-45"
  - "src/spatial/node/LockMem.scala:1-147"
  - "src/spatial/node/StreamIn.scala:1-20"
  - "src/spatial/node/StreamOut.scala:1-27"
  - "src/spatial/node/Frame.scala:1-36"
  - "src/spatial/node/Accumulator.scala:1-57"
  - "src/spatial/lang/types/Mem.scala:9-50"
  - "src/spatial/lang/Reg.scala:9-66"
  - "src/spatial/lang/SRAM.scala:10-100"
  - "src/spatial/lang/FIFO.scala:10-80"
  - "src/spatial/lang/DRAM.scala:8-60"
  - "src/spatial/lang/StreamIn.scala:9-28"
  - "src/spatial/lang/StreamOut.scala:10-28"
  - "argon/src/argon/node/DSLOp.scala:29-37"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: rework
depends_on:
  - "[[30 - Memory Accesses]]"
  - "[[10 - Controllers]]"
status: draft
---

# Memories (IR nodes)

## Summary

Spatial's memory-allocation nodes are the IR-level "new" for every on-chip and off-chip storage primitive in the DSL. They share a common base `MemAlloc[A,C]` (`src/spatial/node/HierarchyMemory.scala:9-20`) which extends argon's `Alloc[T]` (`argon/src/argon/node/DSLOp.scala:29-31`). The DSL-surface types in `src/spatial/lang/types/Mem.scala:9-50` — `Mem[A,C]`, `LocalMem[A,C]`, `RemoteMem[A,C]`, `TensorMem[A]` — determine which allocation nodes can be read/written by which accessor forms, and whether the memory lives on-chip or off-chip. For the HLS rewrite, this entire family maps to HLS's own memory intrinsics (`#pragma HLS RESOURCE`, `ap_memory`, `hls::stream`, etc.) and requires a reworked mapping.

## Syntax / API

Each DSL memory constructor ends in a `stage(...)` of the corresponding IR node:

| DSL call | IR node | File:Line |
|---|---|---|
| `Reg[A]` | `RegNew[A](init)` | `src/spatial/lang/Reg.scala:57` → `src/spatial/node/Reg.scala:11` |
| `ArgIn[A]` | `ArgInNew[A](init)` | `src/spatial/node/Reg.scala:13` |
| `ArgOut[A]` | `ArgOutNew[A](init)` | `src/spatial/node/Reg.scala:14` |
| `HostIO[A]` | `HostIONew[A](init)` | `src/spatial/node/Reg.scala:15` |
| `FIFOReg[A]` | `FIFORegNew[A](init)` | `src/spatial/node/Reg.scala:12` |
| `SRAM[A](dims)` | `SRAMNew[A,C](dims)` | `src/spatial/node/SRAM.scala:10-13` |
| `RegFile[A](dims)` | `RegFileNew[A,C](dims, inits)` | `src/spatial/node/RegFile.scala:10-14` |
| `FIFO[A](depth)` | `FIFONew[A](depth)` | `src/spatial/node/FIFO.scala:7-19` |
| `LIFO[A](depth)` | `LIFONew[A](depth)` | `src/spatial/node/LIFO.scala:7-9` |
| `LUT[A].fromSeq(...)` | `LUTNew[A,C](dims, elems)` | `src/spatial/node/LUT.scala:10-14` |
| `LUT.fromFile[A](...)` | `FileLUTNew[A,C](dims, path)` | `src/spatial/node/LUT.scala:19-23` |
| `LineBuffer[A](rows, cols, stride)` | `LineBufferNew[A](rows, cols, stride)` | `src/spatial/node/LineBuffer.scala:7-9` |
| `MergeBuffer[A](ways, par)` | `MergeBufferNew[A](ways, par)` | `src/spatial/node/MergeBuffer.scala:8-10` |
| `DRAM[A](dims…)` | `DRAMHostNew[A,C](dims, zero)` | `src/spatial/lang/DRAM.scala:42-54` → `src/spatial/node/DRAM.scala:11` |
| `DRAM.accel[A](rank)` | `DRAMAccelNew[A,C](dim)` | `src/spatial/node/DRAM.scala:13-15` |
| `LockDRAM[A](dims)` | `LockDRAMHostNew[A,C](dims, zero)` | `src/spatial/node/LockMem.scala:8` |
| `LockSRAM[A](dims)` | `LockSRAMNew[A,C](dims)` | `src/spatial/node/LockMem.scala:74-77` |
| `Lock[A](depth)` | `LockNew[A](depth)` | `src/spatial/node/LockMem.scala:141-144` |
| `StreamIn[A](bus)` | `StreamInNew[A](bus)` | `src/spatial/lang/StreamIn.scala:27` → `src/spatial/node/StreamIn.scala:7` |
| `StreamOut[A](bus)` | `StreamOutNew[A](bus)` | `src/spatial/lang/StreamOut.scala:28` → `src/spatial/node/StreamOut.scala:7` |
| (frame grabber) | `FrameHostNew[A,C](dims, zero, stream)` | `src/spatial/node/Frame.scala:11` |

## Semantics

### Base class: `MemAlloc[A,C]`

```scala
abstract class MemAlloc[A:Bits,C[T]](
    mutable: Boolean = true
  )(implicit C: Type[C[A]])
  extends Alloc[C[A]] {

  val A: Bits[A] = Bits[A]
  @stateful def nbits: Int = A.nbits
  def dims: Seq[I32]
  def rank: Seq[Int] = Seq.tabulate(dims.length){i => i}
  override def effects: Effects = if (mutable) Effects.Mutable else super.effects
}
```
(`src/spatial/node/HierarchyMemory.scala:9-20`).

Contracts a subclass must satisfy:
- `dims: Seq[I32]` — concrete dimensions. Some subclasses construct this from constructor args (e.g., `FIFONew.dims = Seq(depth)` at `FIFO.scala:8`); others take `dims` directly (`SRAMNew`, `LUTNew`).
- `rank: Seq[Int]` — index positions that "count" for access-matrix computation. Default is `0..dims.length-1`.
- Effects default to `Effects.Mutable` — the Rust rewrite must treat allocation as a mutable side-effect unless `mutable=false` (used for `LUTNew` and `FileLUTNew`, since LUT contents are static).

### Memory taxonomy

`src/spatial/lang/types/Mem.scala:9-50` defines the DSL-level mixins:

- `Mem[A,C] extends Top[C[A]]` (line 9): root type for every memory; requires `A: Bits`; `__neverMutable = false`.
- `TensorMem[A]` (line 16-33): mixin providing `dims`, `size = product(dims)`, `dim0..dim4`.
- `RemoteMem[A,C] extends Mem[A,C]` (line 35-38): off-chip; no `__read`/`__write` (accessor only via transfer nodes).
- `LocalMem[A,C] extends Mem[A,C]` (line 40-49): on-chip; requires `__read`, `__write`, `__reset` — the accessor surface.

Concrete DSL classes inherit one or more of these:
- `Reg[A]` extends `LocalMem0[A,Reg]` (`src/spatial/lang/Reg.scala:9`).
- `FIFOReg[A]` extends `LocalMem0[A,FIFOReg]` (`src/spatial/lang/Reg.scala:68-71`).
- `SRAM[A,C]` extends `LocalMem[A,C] with TensorMem[A]` (`src/spatial/lang/SRAM.scala:10`).
- `FIFO[A]` extends `LocalMem1[A,FIFO]` (`src/spatial/lang/FIFO.scala:10-12`).
- `DRAM[A,C]` extends `RemoteMem[A,C] with TensorMem[A]` (`src/spatial/lang/DRAM.scala:8`).
- `StreamIn[A]`/`StreamOut[A]` extend *both* `LocalMem0[A,…]` and `RemoteMem[A,…]` (`src/spatial/lang/StreamIn.scala:9`, `src/spatial/lang/StreamOut.scala:10`) — local for access, remote for lifetime.

### Dimensionality conventions

| Node | `dims` source |
|---|---|
| `RegNew`, `FIFORegNew`, `ArgInNew`, `ArgOutNew`, `HostIONew` | `dims = Nil` (`Reg.scala:11-15`) |
| `SRAMNew` | `dims: Seq[I32]` (constructor arg) |
| `RegFileNew` | `dims: Seq[I32]` (constructor arg) |
| `FIFONew` | `dims = Seq(depth)` (`FIFO.scala:8`) |
| `LIFONew` | `dims = Seq(depth)` (`LIFO.scala:8`) |
| `LUTNew`/`FileLUTNew` | `dims: Seq[I32]` (constructor arg) |
| `LineBufferNew` | `dims = Seq(rows, cols)` (`LineBuffer.scala:8`; `stride` is carried but not in `dims`) |
| `MergeBufferNew` | `dims = Seq(I32(128))` (`MergeBuffer.scala:9`) — fixed synthesis-time size |
| `DRAMHostNew` | `dims: Seq[I32]` (constructor arg) |
| `DRAMAccelNew` | `dims = Seq.fill(dim)(I32(0))` (`DRAM.scala:14`) — rank-only, symbolic dims |
| `LockDRAMHostNew` | `dims: Seq[I32]` |
| `LockSRAMNew` | `dims: Seq[I32]` |
| `LockNew` | `dims = Seq(depth)` |
| `StreamInNew`/`StreamOutNew` | `dims = Seq(I32(1))` (`StreamIn.scala:8`, `StreamOut.scala:8`) |
| `FrameHostNew` | `dims: Seq[I32]` |

### Register allocations

All register-family allocations share a `RegAlloc[A,C]` base (`src/spatial/node/Reg.scala:7-9`):
```scala
abstract class RegAlloc[A:Bits, C[T]](implicit C: Type[C[A]]) extends MemAlloc[A, C] {
  def init: Bits[A]
}
```
- `RegNew[A](init)` — generic register; init is the reset value.
- `FIFORegNew[A](init)` — single-entry FIFO with reset value.
- `ArgInNew[A](init)` — AccelScope-input register.
- `ArgOutNew[A](init)` — AccelScope-output register.
- `HostIONew[A](init)` — bidirectional host-interface register.

All four have `dims = Nil` — they are scalar.

### Non-mutable memories

`LUTNew` and `FileLUTNew` are the only memories whose constructors let the user mark them non-mutable — LUT contents are static, so writes are impossible; `MemAlloc.effects` falls through to `super.effects` (pure) when `mutable = false` (`HierarchyMemory.scala:19`). This lets DCE remove unused LUTs. Current code path does NOT pass `mutable = false` at the case-class level; the coverage of that path is through later analysis.

### Memory aliases

`MemAlias[A,Src,Alias]` (`HierarchyMemory.scala:28-38`) is the base for view-like operations:
- `MemDenseAlias[A,Src,Alias](cond: Seq[Bit], mem: Seq[Src[A]], ranges: Seq[Seq[Series[Idx]]])` (lines 48-63) — a dense sub-region view. Stores a *union* of aliases; each entry pairs one `cond` with one `mem` and its `ranges`. `sparseRank` returns the set of non-unit dimensions; `rawRank` returns all dimensions. `aliases = syms(mem)`.
- `MemSparseAlias[A,Addr,W,Src,Alias](cond: Seq[Bit], mem: Seq[Src[A]], addr: Seq[Addr[Ind[W]]], size: Seq[I32], origin: Seq[Ind[W]])` (lines 81-98) — a gather/scatter view, rank 1. `sparseRank = Seq(0)`, `rawRank = Seq(0)`.

Both carry `mutable = true` and override `aliases` to declare the aliasing relationship.

Dimension-query transients — `MemStart`, `MemStep`, `MemEnd`, `MemPar`, `MemLen`, `MemOrigin`, `MemDim`, `MemRank` (`HierarchyMemory.scala:112-120`) — are `Transient[I32]` (or `Transient[Ind[W]]`) nodes generated by the DSL to query dimension metadata of a memory symbol. They are inlined away after analysis.

### Accumulator memories

`AccumMarker` (`src/spatial/node/Accumulator.scala:18-28`) is metadata-adjacent — it's a compile-time tag for specific accumulator patterns. `RegAccumFMA`, `RegAccumOp`, `RegAccumLambda` extend `RegAccum[A]` (lines 30-33) which itself extends `Accumulator[A]` (a post-unroll accessor, documented in [[30 - Memory Accesses]]). The `Accum` enum (`AccumAdd`/`AccumMul`/`AccumMin`/`AccumMax`/`AccumFMA`/`AccumUnk`, lines 9-16) specifies the reduction function.

### Lock primitives

`LockNew[A](depth)` (`LockMem.scala:141-144`) allocates a `Lock[A]` whose `dims = Seq(depth)`. `LockOnKeys[A](lock, keys)` (lines 146-147) extends `Alloc[LockWithKeys[A]]` — it is itself an allocation of a typed "locked view" (lock + selected keys). The `lock: Option[LockWithKeys[I32]]` fields on `LockDRAMRead`/`LockDRAMWrite`/`LockSRAMRead`/`LockSRAMWrite` (and their banked variants) attach this capability at access sites; see [[30 - Memory Accesses]] for the read/write protocol.

## Implementation

### Effects summary

| Node | Effects |
|---|---|
| All `MemAlloc` subclasses (default `mutable=true`) | `Effects.Mutable` (`HierarchyMemory.scala:19`) |
| `LUTNew`/`FileLUTNew` when `mutable=false` | pure (falls to `super.effects`) |
| `DRAMAlloc` | `Effects.Writes(dram)` (`DRAM.scala:26`) |
| `DRAMDealloc` | `Effects.Writes(dram)` (`DRAM.scala:31`) |
| `FrameAlloc` | `Effects.Writes(dram)` (`Frame.scala:22`) |
| `FrameDealloc` | `Effects.Writes(dram)` (`Frame.scala:27`) |
| `SetMem`/`GetMem`/`SetLockMem`/`GetLockMem` | `Effects.Writes(...)` (`DRAM.scala:35, 38, 41, 44`) |

### DRAM specifics

`DRAMNew[A,C]` is the intermediate abstract (`DRAM.scala:9`). Concrete flavors:
- `DRAMHostNew[A,C](dims, zero)` — allocated on the host and DMA'd to accelerator.
- `DRAMAccelNew[A,C](dim)` — allocated inside Accel scope; only the rank is fixed at construction time.
- `DRAMAddress(dram)` — returns `I64` base address (`DRAM.scala:17-19`); `Primitive[I64]`.
- `DRAMIsAlloc(dram)` — returns `Bit`; `Primitive[Bit]` (`DRAM.scala:21`).
- `DRAMAlloc(dram, dims)` — dynamic resize of an Accel-side DRAM allocation; `EnPrimitive[Void]` with `Effects.Writes(dram)` (`DRAM.scala:23-27`).
- `DRAMDealloc(dram)` — free the Accel-side allocation; `EnPrimitive[Void]` (`DRAM.scala:29-32`).
- `SetMem(dram, data: Tensor1[A])` — host-side set: `Effects.Writes(dram)` (`DRAM.scala:34-36`).
- `GetMem(dram, data: Tensor1[A])` — host-side copy-out: `Effects.Writes(data)` (`DRAM.scala:37-39`).

Lock variants `SetLockMem`/`GetLockMem` (lines 40-45) are analogous but for `LockDRAM`.

### FIFO specifics

`FIFONew[A](depth)` exposes a `resize(newDepth: I32)` method (`FIFO.scala:9-18`) that mutates the node's `depth` via an `update` transformer rule:
```scala
def resize(newDepth: I32): Unit = {
  this.update(new Tx {
    def apply[T](v: T): T = v match {
      case x: I32 if x == depth => newDepth.asInstanceOf[T]
      case _ => v
    }
  })
}
```
This allows later passes (e.g., pipe insertion, buffer sizing) to adjust FIFO capacity after staging. A reimplementer must provide an equivalent "mutate-in-place" hook or accept the extra cost of re-allocation.

### Stream memories

`StreamInNew[A](bus: Bus)` and `StreamOutNew[A](bus: Bus)` (`StreamIn.scala:7-9`, `StreamOut.scala:7-9`) carry a `Bus` instance rather than a dimension. The `Bus` hierarchy (`src/spatial/lang/Bus.scala:13-87`) includes `BurstCmdBus`, `BurstAckBus`, `BurstDataBus[A]`, `BurstFullDataBus[A]`, `GatherAddrBus`, `GatherDataBus[A]`, `ScatterCmdBus[A]`, `ScatterAckBus`, `AxiStream64Bus`/`AxiStream256Bus`/`AxiStream512Bus`, `FileBus[A]`, `FileEOFBus[A]`, `PinBus`. The bus determines the wire-level protocol; fringe lowering (see [[30 - Memory Accesses]]) depends on which bus is attached.

### Frame memories

`FrameHostNew[A,C](dims, zero, stream: Sym[_])` (`Frame.scala:11`) is unique among the allocations for carrying a second symbol — the underlying `StreamIn` or `StreamOut` sym that acts as the AXI-stream data source/sink. `FrameTransmit` lowering matches on `Op(FrameHostNew(len, _, dataStream)) = frame` (`src/spatial/node/FrameTransmit.scala:60`) to thread the stream into the generated `Stream { ... }` controller. `FrameAddress`/`FrameIsAlloc`/`FrameAlloc`/`FrameDealloc` mirror the DRAM forms.

## Interactions

**Written by:** DSL layer via `stage(...)` from `src/spatial/lang/{Reg, SRAM, FIFO, LIFO, RegFile, LUT, LineBuffer, MergeBuffer, DRAM, StreamIn, StreamOut, LockMem, Frame}.scala`. `FIFONew.resize` mutates in place.

**Read by:**
- `flows/SpatialFlowRules.scala` attaches ExplicitName, LocalMemories/RemoteMemories globals.
- `transform/MemoryAnalyzer` (banking analysis) — walks allocs to determine `Duplicates`, `Instance`, `Memory`, `Padding`, `Dispatch` metadata.
- `transform/unrolling/MemoryUnrolling` — duplicates allocs per banking decision.
- `codegen/chiselgen/ChiselGen*Mem` emitters — pattern-match on each alloc class to emit the right Chisel module.
- `transform/MemoryDealiasing` — resolves `MemDenseAlias`/`MemSparseAlias` to concrete accesses.

**Key invariants:**
- `MemAlloc.effects` must be `Effects.Mutable` (mutable memories) or pure (LUTs with `mutable=false`); otherwise scheduling will re-order writes.
- `dims` is a `Seq[I32]` — constants folded to `Const(i)` when possible. `DRAMAccelNew.dims` is `Seq.fill(dim)(I32(0))` — a placeholder that encodes rank only.
- `FIFONew.depth` is mutable via `resize`; any metadata keyed on depth must invalidate when `resize` is called.
- `StreamInNew`/`StreamOutNew`'s `bus` field is a non-Sym `Bus` instance; mirroring treats it as-is.
- `FrameHostNew.stream` is a `Sym[_]` — the mirroring transformer walks it as an input.
- `LockDRAMHostNew` extends `DRAMNew` (not a separate root) — it participates in the DRAM family for transfer purposes.

## HLS notes

`hls_status: rework`. HLS targets use a different memory model (no explicit banking; banking is emergent from pragmas; stream types are `hls::stream<T>`). The Rust rewrite needs:

1. A memory-kind enum at the Rust level (Reg/SRAM/FIFO/RegFile/LUT/DRAM/Stream/Frame/Lock-variants).
2. A per-kind lowering to HLS intrinsics — e.g., SRAM → `#pragma HLS RESOURCE variable=… core=RAM_2P`, FIFO → `hls::stream<T>`, RegFile → `#pragma HLS ARRAY_PARTITION`.
3. Preserve the `init` field for `RegAlloc`-family (synthesized to HLS reset).
4. `MemDenseAlias`/`MemSparseAlias` are Spatial-specific; HLS has no direct analog and these probably get resolved to concrete accesses before emission.
5. `Lock*` variants have no direct HLS analog; may need a serialization library or user-defined blackbox.

See `30 - HLS Mapping/` for the per-construct categorization.

## Open questions

- Q-008 in `20 - Open Questions.md` — `MergeBufferNew.dims = Seq(I32(128))` is a fixed magic number; where is 128 justified and is it tunable?
- Q-009 — `DRAMAccelNew.dims = Seq.fill(dim)(I32(0))` encodes rank-only; do subsequent passes fill in real dims via `DRAMAlloc`, or is rank always sufficient?
- Q-010 — `FIFONew.resize` mutates depth post-staging; what's the set of passes allowed to call it, and how do they interact with banking analysis results?
