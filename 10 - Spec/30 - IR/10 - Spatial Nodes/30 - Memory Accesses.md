---
type: spec
concept: spatial-ir-memory-accesses
source_files:
  - "src/spatial/node/HierarchyAccess.scala:1-156"
  - "src/spatial/node/HierarchyUnrolled.scala:1-154"
  - "src/spatial/node/Reg.scala:17-61"
  - "src/spatial/node/SRAM.scala:20-70"
  - "src/spatial/node/RegFile.scala:16-131"
  - "src/spatial/node/FIFO.scala:22-72"
  - "src/spatial/node/LIFO.scala:11-35"
  - "src/spatial/node/LUT.scala:25-50"
  - "src/spatial/node/LineBuffer.scala:11-30"
  - "src/spatial/node/MergeBuffer.scala:12-29"
  - "src/spatial/node/LockMem.scala:19-136"
  - "src/spatial/node/StreamIn.scala:11-20"
  - "src/spatial/node/StreamOut.scala:11-27"
  - "src/spatial/node/DRAM.scala:17-45"
  - "src/spatial/node/DenseTransfer.scala:34-394"
  - "src/spatial/node/SparseTransfer.scala:27-175"
  - "src/spatial/node/FrameTransmit.scala:26-89"
  - "src/spatial/node/Fringe.scala:7-66"
  - "src/spatial/node/HierarchyMemory.scala:48-110"
  - "argon/src/argon/node/Enabled.scala:6-21"
  - "argon/src/argon/Op.scala:115-117"
source_notes:
  - "[[spatial-ir-nodes]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[10 - Controllers]]"
  - "[[40 - Counters and Iterators]]"
status: draft
---

# Memory Accesses (IR nodes)

## Summary

This entry covers every access node — reads, writes, resets, enqueues, dequeues, status reads, vector variants, banked variants, register getters/setters, DRAM transfer wrappers, and memory aliases. There are two parallel hierarchies: a **pre-unroll** form (`Reader`/`Writer`/`Dequeuer`/`Enqueuer`/`StatusReader`/`Resetter`, `src/spatial/node/HierarchyAccess.scala:45-156`) emitted by the DSL layer, and a **post-unroll** banked/vectored form (`BankedReader`/`BankedWriter`/`VectorReader`/`VectorWriter`/`BankedDequeue`/`BankedEnqueue`/`Accumulator`, `src/spatial/node/HierarchyUnrolled.scala:22-154`) produced by the unroller after banking analysis. Every accessor is `EnPrimitive[R]` — carrying an enable set via the argon `Enabled` trait. For the HLS rewrite, accesses map onto HLS's memory-port model (RAM_1P, RAM_2P, stream.read/write); banking emerges from array-partition pragmas, not explicit post-unroll nodes.

## Syntax / API

The DSL layer stages one accessor per language call:
- `reg := data` / `Reg.write(reg, data, ens)` → `RegWrite` (`src/spatial/lang/Reg.scala:62-65`).
- `reg.value` / `Reg.read(reg)` → `RegRead` (`src/spatial/lang/Reg.scala:58-61`).
- `sram.read(addr, ens)` → `SRAMRead` (`src/spatial/lang/SRAM.scala:33-36`).
- `sram.write(data, addr, ens)` → `SRAMWrite` (`src/spatial/lang/SRAM.scala:42-45`).
- `fifo.enq(data, en)` → `FIFOEnq` (`src/spatial/lang/FIFO.scala:35`).
- `fifo.deq(en)` → `FIFODeq` (`src/spatial/lang/FIFO.scala:56`).
- `fifo.enqVec(data, en)` → `FIFOVecEnq` (`src/spatial/lang/FIFO.scala:41`).
- `fifo.deqVec(addr, en)` → `FIFOVecDeq` (`src/spatial/lang/FIFO.scala:47-50`).
- `streamIn.value(en)` → `StreamInRead` (`src/spatial/lang/StreamIn.scala:15`).
- `streamOut := data` → `StreamOutWrite` (`src/spatial/lang/StreamOut.scala:15-16`).
- Transfers (`load`/`store` on `LocalMem1` and descendants) stage `DenseTransfer`/`SparseTransfer`/`FrameTransmit`.

## Semantics

### Pre-unroll access contracts

`Access` is a **plain** (non-`Op`) case-class-like ADT (`HierarchyAccess.scala:9-15`) used as a *return type* of per-accessor helpers:
```scala
abstract class Access {
  def mem:  Sym[_]
  def addr: Seq[Idx]
  def ens:  Set[Bit]
}
case class Read(mem, addr, ens) extends Access
case class Write(mem, data, addr, ens) extends Access
```
It is not itself an IR op. IR accessors extend `EnPrimitive[R]` (hence `Primitive[R] with Enabled[R]`) and expose `localRead: Option[Read]` and `localWrite: Option[Write]` that build the appropriate `Access` record on demand.

The concrete hierarchy (`HierarchyAccess.scala:45-156`):

```
EnPrimitive[R]
  Accessor[A,R]              (line 45-53)
    Reader[A,R]               (line 65-68)   — localRead = Some(Read(mem,addr,ens)); localWrite = None
      DequeuerLike[A,R]       (line 79-82)   — adds effects = Writes(mem)
        Dequeuer[A,R]         (line 92-94)   — addr = Nil
          VectorDequeuer[A]   (line 104)
    Writer[A]                  (line 116-122) — effects = Writes(mem); localWrite = Some(Write(...))
      EnqueuerLike[A]         (line 133)
        Enqueuer[A]           (line 136-138) — addr = Nil
          VectorEnqueuer[A]   (line 148)
```

Two parallel siblings:
- `StatusReader[R:Bits]` (`HierarchyAccess.scala:18-28`) — for `FIFOIsEmpty`, `FIFONumel`, etc. Abstract `mem: Sym[_]`; extends `EnPrimitive[R]`.
- `Resetter[A:Type]` (`HierarchyAccess.scala:31-42`) — `EnPrimitive[Void]` with `Effects.Writes(mem)`.

All of these carry `ens: Set[Bit]` (inherited from `Enabled`) — the pre-unroll enable conjunction. The enable is a `Set` because it's a conjunctive bag of predicates, not an ordered list.

### Pre-unroll examples

| Memory | Reader concretion | Writer concretion | Reset |
|---|---|---|---|
| `Reg` | `RegRead(mem)` (`Reg.scala:29-37`) — `addr=Nil`, `ens=Set.empty`, `isTransient=true`, `effects = Unique` | `RegWrite(mem,data,ens)` (`Reg.scala:17-21`) — `Enqueuer[A]` (addr=Nil) | `RegReset(mem,ens)` (`Reg.scala:47`) |
| `FIFOReg` | `FIFORegDeq(mem,ens)` (`Reg.scala:39-45`) — `Dequeuer`, `isTransient=true`, `Unique` | `FIFORegEnq(mem,data,ens)` (`Reg.scala:23-27`) — `Enqueuer` | — |
| `SRAM` | `SRAMRead(mem,addr,ens)` (`SRAM.scala:20-24`) — `Reader` | `SRAMWrite(mem,data,addr,ens)` (`SRAM.scala:32-37`) — `Writer` | — |
| `RegFile` | `RegFileRead(mem,addr,ens)` (`RegFile.scala:21-25`) — `Reader` | `RegFileWrite(mem,data,addr,ens)` (`RegFile.scala:33-38`) — `Writer`; plus `RegFileShiftIn`/`RegFileBankedShiftIn`/`RegFileShiftInVector` (lines 50-105) | `RegFileReset(mem,ens)` (lines 82-85) |
| `FIFO` | `FIFODeq`/`FIFOPriorityDeq`/`FIFODeqInterface`/`FIFOPeek`, status readers (`FIFO.scala:23-52`) | `FIFOEnq` (`FIFO.scala:22`), vector `FIFOVecEnq` (lines 31-38) | — |
| `LIFO` | `LIFOPop`/`LIFOPeek` + status readers (`LIFO.scala:12-21`) | `LIFOPush` (line 11) | — |
| `LUT` | `LUTRead(mem,addr,ens)` (`LUT.scala:30-34`) | (no writer; LUT is read-only) | — |
| `LineBuffer` | `LineBufferRead(mem,addr,ens)` (`LineBuffer.scala:14`) | `LineBufferEnq(mem,data,addrs,ens)` (lines 11-13) — uses `addrs` as internal position | — |
| `MergeBuffer` | `MergeBufferDeq(mem,ens)` (`MergeBuffer.scala:15`) | `MergeBufferEnq(mem,way,data,ens)`, `MergeBufferBound`, `MergeBufferInit` (lines 12-14) | — |
| `StreamIn` | `StreamInRead(mem,ens)` (`StreamIn.scala:11-14`) — `Dequeuer` (no data) | — | — |
| `StreamOut` | — | `StreamOutWrite(mem,data,ens)` (`StreamOut.scala:11-15`) — `Enqueuer` | — |
| `LockSRAM` | `LockSRAMRead(mem,addr,lock,ens)` (`LockMem.scala:84-89`) — `Reader` | `LockSRAMWrite(mem,data,addr,lock,ens)` (lines 97-103) — `Writer` | — |
| `LockDRAM` | `LockDRAMRead(mem,addr,lock,ens)` (`LockMem.scala:19-24`) | `LockDRAMWrite(mem,data,addr,lock,ens)` (lines 32-38) | — |

### Register getters/setters

`GetReg[A]` and `SetReg[A]` (`Reg.scala:49-61`) are `Reader`/`Writer` variants with `addr = Nil` and `ens = Set.empty` (non-enable-aware). They exist as separate node types from `RegRead`/`RegWrite` because `GetReg`/`SetReg` are used in non-accelerator contexts (host-side register access) and don't have the `isTransient = true` / `Effects.Unique` flags that `RegRead`/`RegWrite` do.

### Post-unroll contracts

After unrolling + banking, pre-unroll accessors are lowered to `UnrolledAccessor[A,R]` (`HierarchyUnrolled.scala:22-40`):
```scala
abstract class UnrolledAccessor[A:Type,R:Type] extends EnPrimitive[R] {
  def mem: Sym[_]
  def unrolledRead: Option[UnrolledRead]
  def unrolledWrite: Option[UnrolledWrite]
  final var ens: Set[Bit] = Set.empty    // (line 27)
  var enss: Seq[Set[Bit]]                 // (line 28) — per-lane enables
  def width: Int = enss.length
}
```

Concrete subclasses provide a per-lane address/bank mapping:
- `VectorReader[A]` (`HierarchyUnrolled.scala:72-76`): `addr: Seq[Seq[Idx]]`; `unrolledRead = Some(VectorRead(mem, addr, enss))`.
- `VectorWriter[A]` (lines 105-111): `addr`, `data: Seq[Sym[_]]`; `unrolledWrite = Some(VectorWrite(mem, data, addr, enss))`; `Effects.Writes(mem)`.
- `BankedAccessor[A,R]` (lines 58-61): adds `bank: Seq[Seq[Idx]]`, `ofs: Seq[Idx]`.
- `BankedReader[A]` (lines 86-89): `unrolledRead = Some(BankedRead(mem, bank, ofs, enss))`.
- `BankedDequeue[A]` (lines 99-103): extends `BankedReader` with `bank = Nil`, `ofs = Nil`, `Effects.Writes(mem)`.
- `BankedWriter[A]` (lines 121-126): `data: Seq[Sym[_]]`; `unrolledWrite = Some(BankedWrite(mem, data, bank, ofs, enss))`; `Effects.Writes`.
- `BankedEnqueue[A]` (lines 136-139): extends `BankedWriter` with `bank = Nil`, `ofs = Nil`.
- `Accumulator[A]` (lines 143-154): `data = Nil` (no syntactic data symbol!), `bank`, `ofs`, `first: Bit`, `enss = Seq(en)`; `Effects.Writes(mem)`.

The post-unroll plain-ADT `UnrolledRead`/`UnrolledWrite` records (lines 7-20) are analogous to the pre-unroll `Read`/`Write` records but with per-lane banks/addresses/enables.

### Concrete post-unroll accessors per memory

- `SRAMBankedRead(mem, bank, ofs, enss)` / `SRAMBankedWrite(mem, data, bank, ofs, enss)` (`SRAM.scala:48-69`).
- `RegFileVectorRead` / `RegFileVectorWrite` / `RegFileBankedShiftIn` / `RegFileShiftInVector` (`RegFile.scala:68-130`).
- `FIFOBankedEnq`, `FIFOBankedDeq`, `FIFOBankedPriorityDeq` (`FIFO.scala:54-71`).
- `LIFOBankedPush`, `LIFOBankedPop` (`LIFO.scala:23-34`).
- `LUTBankedRead` (`LUT.scala:43-49`).
- `LineBufferBankedEnq`, `LineBufferBankedRead` (`LineBuffer.scala:16-30`).
- `MergeBufferBankedEnq`, `MergeBufferBankedDeq` (`MergeBuffer.scala:17-28`).
- `LockDRAMBankedRead`/`LockDRAMBankedWrite`, `LockSRAMBankedRead`/`LockSRAMBankedWrite` (`LockMem.scala:46-135`) — each carries `lock: Option[Seq[LockWithKeys[I32]]]`.
- `StreamInBankedRead` (`StreamIn.scala:16-20`), `StreamOutBankedWrite` (`StreamOut.scala:22-27`).

### Address patterns

Pre-unroll addresses are `Seq[Idx]` (where `Idx` is `I32`) — one per dimension of the memory. Post-unroll addresses split into:
- `bank: Seq[Seq[Idx]]` — per-lane, per-dim bank indices. The outer sequence is lanes; the inner is dim count.
- `ofs: Seq[Idx]` — per-lane offset within a bank (flat index).
- `addr: Seq[Seq[Idx]]` (for vector accessors without explicit banking) — per-lane per-dim addresses.

### Enable signals

Enable signals are `Set[Bit]` — interpreted as *conjunction*: the access fires iff all bits in the set are high. The use of a `Set` (rather than a single `Bit`) lets passes accumulate nested enables without synthesizing AND gates until codegen. `UnrolledAccessor.enss` is `Seq[Set[Bit]]` — one enable set per lane. `Accumulator.enss = Seq(en)` collapses to a single-element sequence.

`Enabled.mirrorEn` and `Enabled.updateEn` (`argon/src/argon/node/Enabled.scala:9-20`) propagate enables when mirroring. The `UnrolledAccessor` overrides (`HierarchyUnrolled.scala:32-39`) apply the added enable to every lane's `enss` entry. A few accessors (`RegRead`, `GetReg`, `SetReg`, `AccelScope`) override `updateEn`/`mirrorEn` to be no-ops because they have no real enable wire (`Reg.scala:35-36, 52-53, 58-60`; `Control.scala:26-27`).

### `AtomicRead` trait

Defined in `argon/src/argon/Op.scala:115-117`:
```scala
trait AtomicRead[M] { def coll: Sym[M] }
```
Used by `ArrayApply[A]` (`src/spatial/node/Array.scala:18-20`) to mark reads that are atomic with respect to mutable host arrays. No Spatial memory accessor uses this trait directly — it's for host-side arrays only.

### Transfers (DenseTransfer, SparseTransfer, FrameTransmit)

All three extend `EarlyBlackbox[Void]` (`src/spatial/node/Blackbox.scala:11-16`), meaning they are lowered early in the compiler (after initial analyses) by `blackboxLowering1`/`blackboxLowering2`.

`DenseTransfer[A,Dram,Local](dram, local, isLoad, forceAlign, ens)` (`DenseTransfer.scala:34-63`) — the EarlyBlackbox constructor carries alignment, direction, and enable. `lower(old)` calls `DenseTransfer.transfer(...)` (lines 66-392) which:
1. Computes sparse rank, lens, strides, pars from `dram.sparseRank` / `sparseLens()` / etc.
2. Checks byte-alignment (`A.nbits * lastPar % 8 != 0` throws at line 97).
3. Checks non-leading parallelism constraint (`outerPars > 1` throws at line 92).
4. Stages a `Stream { ... }` block with `BurstCmdBus`/`BurstDataBus[A]`/`BurstAckBus` streams and a `Fringe.denseLoad`/`Fringe.denseStore` call.
5. Handles aligned vs. unaligned paths (`alignedStore`/`unalignedStore`/`alignedLoad`/`unalignedLoad` helpers, lines 163-391).
6. Sets `loweredTransfer = DenseLoad` or `DenseStore` and `isStreamPrimitive = true` on the generated outer controller (lines 114-115, 126-127).

`SparseTransfer[A,Local](dram: DRAMSparseTile[A], local, isGather, ens)` (`SparseTransfer.scala:27-44`) lowers to a `Stream { Foreach { addrBus := addr; ... } Foreach { dataBus.value() } }` pattern with `GatherAddrBus`/`GatherDataBus[A]` for loads or `ScatterCmdBus[A]`/`ScatterAckBus` for stores (lines 75-170). Pads request length to a multiple of 16 for non-PIR targets (lines 66-73).

`FrameTransmit[A,Frame,Local](frame, local, isLoad, forceAlign, ens)` (`FrameTransmit.scala:26-43`) lowers to a `Stream.Foreach(len by 1){ ... }` with AXI-Stream protocol encoding. Hardcoded fallback `(tid=0, tdest=0)` when the stream isn't `AxiStream64Bus` (line 79).

### Fringe DMA nodes

The post-lowering fringe nodes live at `src/spatial/node/Fringe.scala:7-38`:
- `FringeDenseLoad[A,C](dram, cmdStream, dataStream)` — `Effects.Writes(dataStream)`.
- `FringeDenseStore[A,C](dram, cmdStream, dataStream, ackStream)` — `Effects.Writes(ackStream, dram)`.
- `FringeSparseLoad[A,C](dram, addrStream, dataStream)` — `Effects.Writes(dataStream)`.
- `FringeSparseStore[A,C](dram, cmdStream, ackStream)` — `Effects.Writes(ackStream, dram)`.

All four extend `FringeNode[A,Void]` which is a `DSLOp[Void]` (`src/spatial/node/HierarchyControl.scala:7-15`). Staging helpers: `Fringe.denseLoad`/`denseStore`/`sparseLoad`/`sparseStore` at lines 42-65.

### Memory aliases as accesses

`MemDenseAlias` and `MemSparseAlias` (`src/spatial/node/HierarchyMemory.scala:48-110`) are extensively documented in [[20 - Memories]] as allocations; they also function as access expressions (a dense or sparse slice of another memory). The `addr` component for `MemSparseAlias` is `Seq[Addr[Ind[W]]]` — gather/scatter addresses read from another memory.

## Implementation

### Effects summary

| Class | Effects |
|---|---|
| `Reader[A,R]` (default) | inherits block effects (pure unless inputs force otherwise) |
| `DequeuerLike[A,R]` | `Effects.Writes(mem)` (`HierarchyAccess.scala:80`) — destructive read |
| `Writer[A]` | `Effects.Writes(mem)` (`HierarchyAccess.scala:117`) |
| `StatusReader[R]` | inherits |
| `Resetter[A]` | `Effects.Writes(mem)` (`HierarchyAccess.scala:32`) |
| `VectorWriter[A]` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:106`) |
| `BankedDequeue[A]` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:100`) |
| `BankedWriter[A]` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:122`) |
| `Accumulator[A]` | `Effects.Writes(mem)` (`HierarchyUnrolled.scala:152`) |
| `RegRead` | `Unique`, `isTransient = true` (`Reg.scala:30-31`) |
| `FIFORegDeq` | `Unique`, `isTransient = true` (`Reg.scala:40-41`) |

### Extractors

`HierarchyAccess.scala` and `HierarchyUnrolled.scala` define companion extractors that return tuples of the access's operational state:
- `Reader.unapply(x: Sym[_]): Option[(Sym[_], Seq[Idx], Set[Bit])]` (`HierarchyAccess.scala:70-76`) — `(mem, addr, ens)`.
- `Writer.unapply`: `(Sym[_], Sym[_], Seq[Idx], Set[Bit])` — `(mem, data, addr, ens)` (lines 124-130).
- `Dequeuer.unapply`, `VectorDequeuer.unapply`, `Enqueuer.unapply`, `VectorEnqueuer.unapply` follow the same pattern.
- `BankedReader.unapply`, `BankedWriter.unapply`, `VectorReader.unapply`, `VectorWriter.unapply` (`HierarchyUnrolled.scala:91-134`) return banked tuples.
- `Accessor.unapply(x): Option[(Option[Write], Option[Read])]` (`HierarchyAccess.scala:55-62`) — for generic matching.
- `UnrolledAccessor.unapply`, `UnrolledReader.unapply`, `UnrolledWriter.unapply` (`HierarchyUnrolled.scala:42-70`).

### DSL layer staging

`SRAM.read` and `SRAM.write` (`src/spatial/lang/SRAM.scala:33-52`) call `checkDims(addr.length)` to verify rank match and then `stage(SRAMRead[A,C](me, addr, ens))` / `stage(SRAMWrite[A,C](me, data, addr, ens))`. The `me` self-reference is the DSL instance.

`Reg.read` and `Reg.write` (`src/spatial/lang/Reg.scala:58-65`) stage `RegRead(reg)` with no addr/ens, and `RegWrite(reg, data, ens)` accepting an enable.

`FIFO.deq/enq/deqVec/enqVec` (`src/spatial/lang/FIFO.scala:32-56`) stage `FIFODeq`/`FIFOEnq`/`FIFOVecDeq`/`FIFOVecEnq`. The vector variants compute a `Vec.bits[A](addr.size)` type witness (line 48).

### Stream-struct accesses

`FieldDeq[S,A:Bits](struct: StreamStruct[S], field: String, ens: Set[Bit])` (`src/spatial/node/StreamStruct.scala:12-15`) is an `EnPrimitive[A]` extracting a named field from a `StreamStruct`. The commented-out `Effects.Writes(struct)` (lines 14-15) is a TODO about whether field-deq counts as a mutation of the struct's state.

`FieldEnq[S,A:Type]` (`StreamStruct.scala:18-22`) writes a field with `Effects.Writes(struct)`, `canAccel = true`. Note the `TODO: FieldEnq may not actually be used anywhere` (line 18).

## Interactions

**Written by:**
- DSL layer for pre-unroll accesses.
- `transform/unrolling/MemoryUnrolling` — rewrites pre-unroll accesses into post-unroll (banked/vector) accesses per the banking decision attached to each memory.
- `transform/blackboxLowering` — lowers `DenseTransfer`/`SparseTransfer`/`FrameTransmit` into Stream + Fringe* patterns.

**Read by:**
- `traversal/AccessAnalyzer`, `AccessExpansion`, `IterationDiffAnalyzer` — walk accessors to build `AccessMatrix`, `AffineMatrices`, `Domain`.
- `transform/MemoryAnalyzer` (banking/duplicate/port decisions).
- `codegen/chiselgen/ChiselGen*Mem` — match on accessor class to emit RTL.
- `transform/retiming/RetimingTransformer` — uses `isInCycle` and cycle annotations.

**Key invariants:**
- `Enabled.ens` is the authoritative pre-unroll enable; `UnrolledAccessor.enss` is authoritative post-unroll (the shared `ens` field on `UnrolledAccessor` is held at `Set.empty`, `HierarchyUnrolled.scala:27`).
- `Writer.data` is a `Bits[A]` or `Sym[A]`; banked writers carry `data: Seq[Sym[A]]` (one per lane).
- `Accumulator.data = Nil` — an intentional absence of a write-data symbol. Any consumer of `localWrite.data` must guard against this.
- `DequeuerLike` has `Effects.Writes(mem)` because dequeue mutates the queue state — scheduler treats it as a write, not a read.
- Pre-unroll accesses have `ens: Set[Bit]` (flat). Post-unroll accesses use `enss: Seq[Set[Bit]]` where index `i` is lane `i`.
- `BankedDequeue` / `BankedEnqueue` set `bank = Nil, ofs = Nil` — no address, but still extend the banked hierarchy for uniformity.
- `LockDRAM*Read`/`Write`/banked variants carry a `lock: Option[LockWithKeys[I32]]` parameter; banking analysis currently returns empty banking and `dispatch = {0}` for these, per the coverage note.

## HLS notes

`hls_status: rework`. HLS targets express memory access through:
- Array read/write syntax on partitioned arrays (for SRAM/RegFile).
- `hls::stream<T>::read()` and `write()` (for FIFO/StreamIn/StreamOut).
- Burst transfers via `memcpy`-like patterns or `m_axi` interfaces (for DRAM).

The Rust-over-HLS rewrite will need:
1. A generic "Access<Mem>" enum with kind (read/write/dequeue/enqueue/reset/status), addr, data, ens, and a post-unroll banking extension (bank, ofs, enss).
2. A lowering pass to emit HLS-appropriate C++ for each access kind.
3. Preserve the pre-unroll/post-unroll distinction or collapse them — HLS can derive banking from array partition pragmas, so post-unroll banking might become implicit.
4. `DenseTransfer`/`SparseTransfer`/`FrameTransmit` lowering to `Stream { Fringe* }` is a Spatial idiom; the HLS equivalent is direct `m_axi` burst access.
5. `MemDenseAlias`/`MemSparseAlias` need resolution before emission.

See `30 - HLS Mapping/` for the per-construct categorization.

## Open questions

- Q-012 in `20 - Open Questions.md` — `LockDRAM*` banking: codebase hardcodes empty banking + `dispatch = {0}`; what's the rationale and does it hold for multi-lock scenarios?
- Q-013 — Is there a canonical way to tell whether a pre-unroll access has been visited by the unroller (e.g., is there an "unrolled" flag or is it purely structural: "if you see SRAMBankedRead you know we're post-unroll")?
