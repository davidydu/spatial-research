---
type: spec
concept: standard-library-meta-programming
source_files:
  - "src/spatial/lib/MetaProgramming.scala:9-120"
source_notes:
  - "[[open-questions-stdlib]]"
hls_status: clean
depends_on:
  - "[[10 - Controllers]]"
  - "[[20 - Memories]]"
status: draft
---

# Meta Programming

## Summary

`trait MetaProgramming` is a user-facing helper layer under `spatial.lib.metaprogramming` that extends `SpatialApp` and changes staging behavior for scoped accessor enables (`src/spatial/lib/MetaProgramming.scala:1-15`). Its central API is `withEns(ens: Bit*)(block)`, which pushes enable bits into a mutable `_ens` buffer before evaluating `block`, removes those bits afterward, and returns the block result (`src/spatial/lib/MetaProgramming.scala:14-20`). The behavior is implemented by overriding `rewrites()`, calling `super.rewrites()`, and installing a global rewrite named `EnableRewrite` into `IR.rewrites` (`src/spatial/lib/MetaProgramming.scala:22-42`). The same trait also defines `MForeach`, `MReduce`, `ForeachWithLane`, `ReduceWithLane`, and a duplicated-FIFO helper `FIFOs` (`src/spatial/lib/MetaProgramming.scala:46-118`). This entry is `hls_status: clean` because the intended output is simple enable-bit plumbing and lane-aware loops, but the Rust+HLS rewrite should avoid depending on a globally mutable rewrite table if a lexical builder scope can encode the same contract (`src/spatial/lib/MetaProgramming.scala:22-42`).

## API

`withEns[T](ens: Bit*)(block: => T): T` is a scoped staging helper, not a runtime controller: it mutates `_ens`, evaluates the by-name `block`, mutates `_ens` again, and returns `res` (`src/spatial/lib/MetaProgramming.scala:14-20`). `rewrites()` installs `EnableRewrite`; the rewrite does nothing when `_ens` is empty, and it also does nothing for an `Accessor` whose existing enable set already contains every enable in `_ens` (`src/spatial/lib/MetaProgramming.scala:22-28`). For FIFO enqueue/dequeue, the rewrite restages `FIFOEnq` or `FIFODeq` with `ens ++ _ens` (`src/spatial/lib/MetaProgramming.scala:29-34`). For SRAM reads and writes, the rewrite restages `SRAMRead` or `SRAMWrite` with `op.ens ++ _ens` (`src/spatial/lib/MetaProgramming.scala:35-40`).

`MForeach(series)(block)` exposes a lane-valid loop shape where `block` receives `(iter, p, valid)` (`src/spatial/lib/MetaProgramming.scala:46-60`). `MReduce(reg)(series)(block)(reduceFunc)` exposes the same lane-valid shape inside a reduction (`src/spatial/lib/MetaProgramming.scala:62-76`). `ForeachWithLane(series)(block)` and `ReduceWithLane(reg)(series)(block)(reduceFunc)` compute a lane number for a normal parallel `Foreach` or `Reduce` and pass `(i, lane)` to the block (`src/spatial/lib/MetaProgramming.scala:78-102`). `FIFOs[T](dup, depth)` allocates `dup` FIFOs, provides a `deq(i, ens*)` method that gates each duplicate by `i === ii`, and provides an `enq(i, data, ens*)` method that sends the data to all duplicates with per-duplicate enable sets (`src/spatial/lib/MetaProgramming.scala:104-118`).

## Algorithm

The enable rewriter is global but conditionally active. When `_ens` is non-empty, any newly staged FIFO or SRAM accessor that lacks at least one current enable is restaged with the accumulated enables appended (`src/spatial/lib/MetaProgramming.scala:26-40`). The duplicate check uses `op.ens.contains(en)` for every current enable, so nested `withEns` scopes do not repeatedly append the same bit to an accessor that already has it (`src/spatial/lib/MetaProgramming.scala:27-28`). The implementation mutates `_ens` with `_ens ++= ens` before the block and `_ens --= ens` after the block, so normal completion restores the previous enable stack (`src/spatial/lib/MetaProgramming.scala:15-20`).

`MForeach` decomposes a possibly non-divisible parallel loop into coarse iterations and explicit lanes. It reads `start`, `end`, `step`, and `par` from the series, computes `stride = step * parFactor`, and runs `Foreach(start until end by stride, parFactor by 1 par parFactor)` (`src/spatial/lib/MetaProgramming.scala:47-54`). Inside the loop, `iter = i + p * step`, `valid = iter < end`, and `withEns(valid)` wraps the user block, so accessors in overrun lanes receive the valid bit automatically (`src/spatial/lib/MetaProgramming.scala:54-58`). `MReduce` repeats the same iteration and valid-bit construction inside a `Reduce` and applies the caller's `reduceFunc` (`src/spatial/lib/MetaProgramming.scala:63-75`).

The lane-only helpers do not add enable bits. `ForeachWithLane` uses the original `start until end by step par parFactor` series and computes `lane = ((i-start) / step) % parFactor` (`src/spatial/lib/MetaProgramming.scala:79-88`). `ReduceWithLane` uses the same lane calculation in a reduction (`src/spatial/lib/MetaProgramming.scala:91-101`). `FIFOs.deq` stages one guarded dequeue per duplicate FIFO, returns `value` only for the selected duplicate, returns `0.to[T]` for all other duplicates, and sums those muxed values (`src/spatial/lib/MetaProgramming.scala:104-112`). `FIFOs.enq` stages an enqueue to every duplicate FIFO with enable `i === ii` plus caller-provided enables (`src/spatial/lib/MetaProgramming.scala:113-116`).

## HLS notes

For HLS, `withEns` should become a lexical enable stack in the builder or AST elaborator, not a late global rewrite pass. The Scala implementation mutates `IR.rewrites` through `addGlobal`, so rewrite order and registration lifetime are implicit in the current compiler state (`src/spatial/lib/MetaProgramming.scala:22-42`). The emitted hardware intent is simpler than the staging mechanism: FIFO and SRAM accessors inside the scope receive additional enable predicates, and `MForeach`/`MReduce` use those predicates to suppress overrun lanes (`src/spatial/lib/MetaProgramming.scala:47-75`). `FIFOs` can lower directly to duplicated FIFO objects with per-duplicate write enables and selected read enables (`src/spatial/lib/MetaProgramming.scala:104-118`).

## Open questions

- Q-lib-08: Should `withEns` specify exception-safe stack restoration, or is normal block completion the only supported staging path (`src/spatial/lib/MetaProgramming.scala:15-20`)?
- Q-lib-09: Should the enable rewrite apply only to FIFO and SRAM accessors as it does today, or should a Rust+HLS frontend define a broader accessor-enable contract for other memories (`src/spatial/lib/MetaProgramming.scala:29-40`)?
