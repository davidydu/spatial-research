---
type: spec
concept: standard-library-sort-scan
source_files:
  - "src/spatial/lib/Sort.scala:6-137"
  - "src/spatial/lib/Scan.scala:6-40"
source_notes:
  - "[[open-questions-stdlib]]"
hls_status: clean
depends_on:
  - "[[20 - Memories]]"
  - "[[10 - Controllers]]"
status: draft
---

# Sort and Scan

## Summary

The sort/scan standard-library surface is compact and structurally close to hardware. `object Sort` defines one helper `log` and two `mergeSort` APIs: an in-place SRAM sort and a DRAM-to-DRAM sort (`src/spatial/lib/Sort.scala:6-69`). The SRAM sorter is a fixed 256-element merge network using `MergeBuffer[T](ways, mergePar)` (`src/spatial/lib/Sort.scala:16-24`). The DRAM sorter first sorts 256-element chunks in an SRAM, then performs off-chip merge passes with a `doubleBuf` register and one FIFO per merge way (`src/spatial/lib/Sort.scala:71-135`). `trait Scan` defines `filter`, which writes a mask of predicate results, and `filter_fifo`, which writes the compacted matching values plus their count (`src/spatial/lib/Scan.scala:6-38`). This entry is `hls_status: clean` because the source is already finite controller code over SRAM, FIFO, and `MergeBuffer` primitives, with no blackbox call or compiler-global rewrite requirement (`src/spatial/lib/Sort.scala:29-55`, `src/spatial/lib/Sort.scala:101-132`, `src/spatial/lib/Scan.scala:14-37`).

## API

`Sort.mergeSort[T:Num](mem: SRAM1[T], mergePar: Int, ways: Int): Unit` sorts an on-chip SRAM in place (`src/spatial/lib/Sort.scala:10-15`). It fixes `sramBlockSize = 256`, derives initial block, merge, and merge-count values from `mergePar` and `ways`, computes `levelCount = log(sramBlockSize / blockSizeInit, ways) + 1`, and allocates one `MergeBuffer` (`src/spatial/lib/Sort.scala:16-24`). `Sort.mergeSort[T:Num](src: DRAM1[T], dst: DRAM1[T], mergePar: Int = 2, ways: Int = 2, numel: Int): Unit` performs a chunked SRAM pre-sort followed by DRAM merge passes (`src/spatial/lib/Sort.scala:62-90`). The DRAM API allocates `FIFO[T](numel)` for each way and a `MergeBuffer[T](ways, mergePar)` for each off-chip merge pass (`src/spatial/lib/Sort.scala:92-99`).

`Scan.filter[T:Num](Y, P, X)` takes output SRAM `Y`, predicate `P: T => Boolean`, and input SRAM `X` (`src/spatial/lib/Scan.scala:8-13`). It writes `1.to[T]` for elements where `P(X(i))` is true and `0.to[T]` otherwise (`src/spatial/lib/Scan.scala:14-17`). `Scan.filter_fifo[T:Num](Y, P, X, YS)` takes the same predicate and input/output SRAMs plus a count register `YS` (`src/spatial/lib/Scan.scala:20-26`). It allocates a FIFO with depth equal to `X.length`, enqueues matching values, writes `YS := fifo.numel`, and drains that many values into `Y` (`src/spatial/lib/Scan.scala:27-37`).

## Algorithm

The SRAM sorter proceeds level by level. For each level, it computes `initMerge = (level == 0)`, calls `sramMergeBuf.init(initMerge)`, iterates current merge blocks sequentially, bounds each merge input with `sramMergeBuf.bound(i, blockSize)`, computes the starting address for each way, enqueues `blockSize` values from each way into the merge buffer, then streams `mergeSize` dequeues back into the first address range (`src/spatial/lib/Sort.scala:29-47`). After each non-initial level, it multiplies `blockSize` and `mergeSize` by `ways` and divides `mergeCount` by `ways`; after the algorithm, it restores the three registers to their initial values (`src/spatial/lib/Sort.scala:48-60`). The restore means this template does not leave caller-visible control registers in a grown state after sorting (`src/spatial/lib/Sort.scala:57-59`).

The DRAM sorter has two phases. The first phase allocates a 256-element SRAM, walks `numel` in 256-element chunks, loads each chunk from `src`, calls the SRAM `mergeSort`, and stores the sorted chunk back to `src` (`src/spatial/lib/Sort.scala:71-81`). The second phase initializes `blockSize`, `mergeSize`, and `mergeCount` from the 256-element chunk size, sets `doubleBuf := true`, allocates one FIFO per merge way, and runs `levelCount = log(numel / blockSizeInit, ways)` merge levels (`src/spatial/lib/Sort.scala:84-101`). Within each level, each way loads from `src` when `doubleBuf` is true and from `dst` otherwise; the merged stream stores to `dst` when `doubleBuf` is true and to `src` otherwise (`src/spatial/lib/Sort.scala:101-125`). At the end of each level, the block sizes grow, merge count shrinks, and `doubleBuf` toggles (`src/spatial/lib/Sort.scala:127-132`).

`filter` is a mask transform, not a compaction transform: output index `i` always corresponds to input index `i` (`src/spatial/lib/Scan.scala:14-17`). `filter_fifo` is a compaction transform: only passing values enter the FIFO, `YS` records the number of passing values, and output indices `0 until YS` receive FIFO-dequeued values in encounter order (`src/spatial/lib/Scan.scala:27-37`).

## HLS notes

The HLS translation can be direct. The SRAM sorter maps to local arrays plus a merge-buffer primitive or an equivalent compare/dequeue network, and the source already exposes the controlling parameters `mergePar` and `ways` (`src/spatial/lib/Sort.scala:10-24`). The DRAM sorter needs the same double-buffer parity as the Scala template because source and destination alternate by level (`src/spatial/lib/Sort.scala:107-132`). `filter` maps to a simple loop producing a predicate mask, while `filter_fifo` maps to a stream compactor with an output counter (`src/spatial/lib/Scan.scala:14-37`). Resource sizing still needs policy: the current DRAM sorter allocates one FIFO per way with depth `numel`, which is correct as a template behavior but may be too large for a default HLS implementation (`src/spatial/lib/Sort.scala:92-95`).

## Open questions

- Q-lib-06: For DRAM `mergeSort`, should the user contract specify which DRAM contains the final sorted result after the last `doubleBuf` toggle, or should the implementation copy back to `dst` unconditionally (`src/spatial/lib/Sort.scala:101-132`)?
- Q-lib-07: Should the public API require `numel` to be compatible with `sramBlockSize`, `ways`, and `mergePar`, or should the HLS rewrite add tail handling for non-exact merge levels (`src/spatial/lib/Sort.scala:16-21`, `src/spatial/lib/Sort.scala:86-90`)?
