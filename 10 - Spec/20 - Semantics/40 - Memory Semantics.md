---
type: spec
status: draft
concept: memory-semantics
source_files:
  - "src/spatial/node/HierarchyMemory.scala:9-120"
  - "src/spatial/node/HierarchyAccess.scala:45-156"
  - "src/spatial/node/HierarchyUnrolled.scala:22-154"
  - "src/spatial/lang/types/Mem.scala:9-50"
  - "src/spatial/metadata/memory/LocalMemories.scala:6-17"
  - "src/spatial/metadata/memory/RemoteMemories.scala:6-16"
  - "src/spatial/metadata/memory/BankingData.scala:49-254"
  - "src/spatial/metadata/memory/package.scala:168-258"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala:115-163"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala:610-682"
  - "spatial/emul/src/emul/OOB.scala:1-40"
  - "spatial/emul/src/emul/BankedMemory.scala:5-49"
  - "spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:26-50"
source_notes:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[70 - Banking]]"
  - "[[30 - Memory]]"
  - "[[30 - Memory Simulator]]"
  - "[[20 - Access]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Memory Accesses]]"
  - "[[70 - Banking]]"
  - "[[30 - Memory]]"
  - "[[30 - Memory Simulator]]"
  - "[[20 - Access]]"
  - "[[10 - Control]]"
---

# Memory Semantics

## Summary

Spatial memory semantics span allocation nodes, access nodes, banking metadata, and Scalagen's runtime memory model. [[20 - Memories]] defines what memory symbols are; [[30 - Memory Accesses]] defines how they are read, written, reset, enqueued, and dequeued; [[70 - Banking]] and [[30 - Memory]] define how abstract accesses become physical banks, duplicates, ports, and N-buffer depths; [[30 - Memory Simulator]] is normative for runtime behavior, especially out-of-bounds access. The HLS rewrite should not collapse these into a generic array model too early: Spatial distinguishes local vs remote lifetime, pre-unroll vs post-unroll access shape, and compiler-time banking decisions from runtime memory state.

## Formal Semantics

A memory allocation is a `MemAlloc[A,C]` with element type `A`, container type `C[A]`, dimensions `dims`, rank, and default mutable allocation effect (`src/spatial/node/HierarchyMemory.scala:9-20`). The DSL type hierarchy defines `Mem`, `TensorMem`, `RemoteMem`, and `LocalMem`; remote memories have off-chip lifetime and no direct local access hooks, while local memories provide `__read`, `__write`, and `__reset` (`src/spatial/lang/types/Mem.scala:9-50`). Streams are the notable mixed case: [[60 - Streams and Blackboxes]] documents that `StreamIn` and `StreamOut` are both local for access and remote for lifetime.

Local memory invariants are structural. Pre-unroll readers and writers expose `localRead` or `localWrite` records with `(mem, addr, ens)` or `(mem, data, addr, ens)`, and writers/dequeuers/resetters carry `Effects.Writes(mem)` so scheduling treats them as mutations (`src/spatial/node/HierarchyAccess.scala:45-156`). Post-unroll accessors expose `unrolledRead` or `unrolledWrite` records with lane-indexed banks, offsets, vector addresses, and lane enable sets (`src/spatial/node/HierarchyUnrolled.scala:22-154`). A dequeue or enqueue has no address, so its bank and offset are `Nil`, but it still participates in the banked hierarchy for uniformity.

Remote memory invariants are transfer-oriented. `DRAM`, `LockDRAM`, and `Frame` allocations are not directly read or written as local arrays; they are manipulated through `SetMem`, `GetMem`, dense/sparse transfers, frame transmit nodes, and fringe DMA nodes in [[30 - Memory Accesses]]. Their effects are writes to the remote memory or host tensor, and their allocation ownership crosses the host-accelerator boundary.

The local/remote split is also recorded as global flow metadata. `LocalMemories` and `RemoteMemories` are mirrored global metadata sets that accumulate discovered memories during traversal, expose sorted symbol lists, and transfer through mirror operations (`src/spatial/metadata/memory/LocalMemories.scala:6-17`, `src/spatial/metadata/memory/RemoteMemories.scala:6-16`). This is a compiler invariant used by later passes, not merely a type-system distinction.

The banking scheme is represented as one or more `Banking` values per physical `Memory` duplicate. The concrete `ModBanking(N, B, alpha, axes, P, ...)` implements the bank-select equation `(alpha dot addr / B) mod N`, where `N` is number of banks, `B` is the block-cyclic block size, `alpha` is the integer coefficient vector, `axes` selects address dimensions, and `P` records padding/block-period information (`src/spatial/metadata/memory/BankingData.scala:49-70`). A flat `Memory.bankSelects` returns one bank coordinate; a hierarchical memory returns one bank coordinate per sparse-rank dimension. `Memory.bankOffset` computes the within-bank offset, including intrablock offsets derived from alpha-weighted addresses modulo block size (`src/spatial/metadata/memory/BankingData.scala:202-254`).

Duplicates are the semantic bridge between abstract memory and physical memories. An analysis-time `Instance` records access groups, controllers, metapipe information, chosen banking, depth, padding, cost, and accumulator type; a final `Memory` stores the physical duplicate's banking, depth, padding, and mutable `resourceType` (`src/spatial/metadata/memory/BankingData.scala:108-188`). `MemoryConfigurer.finalize` writes `mem.duplicates`, then attaches `Dispatch`, `Ports`, and `GroupId` metadata to each access; unused accesses are explicitly marked (`src/spatial/traversal/banking/MemoryConfigurer.scala:115-163`). Dispatch chooses which duplicate a lane/access uses. Port metadata `Port(bufferPort, muxPort, muxOfs, castgroup, broadcast)` distinguishes N-buffer port selection from time-multiplexed mux placement; `bufferPort = None` means the access is outside the metapipeline buffer (`src/spatial/metadata/memory/BankingData.scala:76-105`).

Post-unroll access emission consumes these facts, not the original abstract memory alone. `MemoryUnrolling` looks up access dispatches, ports, group ids, lane ids, bank selects, and offsets, then stages concrete `SRAMBankedRead`, `SRAMBankedWrite`, `FIFOBankedEnq`, `StreamOutBankedWrite`, and related node forms (`src/spatial/transform/unrolling/MemoryUnrolling.scala:165-340`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:509-577`). That makes dispatch and port assignment observable in the IR shape.

N-buffering is therefore not a separate memory kind. It is `depth` on each `Memory` duplicate plus per-access `bufferPort` assignments. Banking computes initial depth by `computeMemoryBufferPorts` inside `bankGroups`; post-unroll repair can recompute depth and update duplicates when new accesses change port requirements (`src/spatial/traversal/banking/MemoryConfigurer.scala:610-682`, `src/spatial/traversal/BufferRecompute.scala:29-48`). LockDRAM is a special fallback: metadata accessors return a one-bank unit memory, dispatch `{0}`, and `Port(None, 0, 0, Seq(0), Seq(0))` for LockDRAM accesses (`src/spatial/metadata/memory/package.scala:168-245`). This is preserved as current behavior but tracked as a portability question.

## Reference Implementation

Runtime memory behavior is defined by Scalagen and `emul`; this entry treats [[30 - Memory Simulator]] as normative. Address flattening is row-major: strides are `[d1*...*dn, ..., 1]`, and the same rule appears in `ScalaGenMemories.flattenAddress`, `BankedMemory.flattenAddress`, and `ShiftableMemory.flattenAddress` (`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:26-34`, `spatial/emul/src/emul/BankedMemory.scala:23-26`). Banked SRAM uses `Array[Array[T]]` indexed by flattened bank coordinate and offset; each lane returns invalid when disabled and wraps enabled access in OOB handling (`spatial/emul/src/emul/BankedMemory.scala:28-44`).

Out-of-bounds behavior is defined by Scalagen and should be cited as reference semantics: `OOB.readOrElse` logs and returns the caller's invalid value; `OOB.writeOrElse` logs and discards the write; neither aborts (`spatial/emul/src/emul/OOB.scala:19-38`). Codegen also emits a catch wrapper around memory operations that prints a warning and substitutes `invalid(tp)` (`spatial/src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`). Hardware may behave differently, but the Rust simulator should match this unless a deliberate divergence mode is chosen.

## HLS Implications

HLS memory lowering should map `Memory` duplicates and `ModBanking` choices to array partitioning, banking, and buffering pragmas, not rediscover a different memory layout after the fact. Local memories map to partitioned arrays, registers, line buffers, or HLS streams; remote memories map to `m_axi`/host buffers. The simulator should implement the Scalagen `OOB` contract, while synthesis-mode code may emit assertions or assume in-bounds access. FIFO/LIFO stream back-pressure is covered separately in [[80 - Streaming]].

## Open questions

- [[open-questions-semantics#Q-sem-07 - 2026-04-25 OOB simulator versus synthesized hardware]] tracks whether Rust should offer both Scalagen-compatible log-and-invalid OOB and stricter assertion modes.
- [[open-questions-semantics#Q-sem-08 - 2026-04-25 LockDRAM fallback banking semantics]] tracks whether LockDRAM's unit dispatch/port behavior is a required semantic or a temporary compatibility path.
