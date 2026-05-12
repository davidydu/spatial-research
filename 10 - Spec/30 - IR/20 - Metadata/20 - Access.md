---
type: spec
concept: Spatial IR Metadata - Access
source_files:
  - "src/spatial/metadata/access/AccessData.scala:8-86"
  - "src/spatial/metadata/access/AccessPatterns.scala:14-268"
  - "src/spatial/metadata/access/AffineData.scala:14-154"
  - "src/spatial/metadata/access/package.scala:16-459"
source_notes:
  - "direct-source-reading"
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
  - "[[10 - Control]]"
  - "[[30 - Memory]]"
status: draft
---

# Access

## Summary

Access metadata describes how staged memory accesses are used, which accesses conflict, and how addresses map into affine spaces for banking and dependence analysis (`src/spatial/metadata/access/AccessData.scala:8-86`, `src/spatial/metadata/access/AffineData.scala:14-154`). It combines small tags (`UnusedAccess`, `Users`, `ReadUses`, `PriorityDeqGroup`, `DoesNotConflictWith`, `DependencyEdges`) with a symbolic affine IR (`Prod`, `Sum`, `Modulus`, `AffineComponent`, `AffineProduct`, `AddressPattern`, `AccessPattern`, `AccessMatrix`, `AffineMatrices`, `Domain`) (`src/spatial/metadata/access/AccessData.scala:8-86`, `src/spatial/metadata/access/AccessPatterns.scala:14-268`, `src/spatial/metadata/access/AffineData.scala:24-153`). The package API also supplies access-class predicates, stream-stage predicates, iterator extraction, dephasing analysis, reaching-write dataflow, and flat-index construction (`src/spatial/metadata/access/package.scala:16-459`).

## Syntax / API

`UnusedAccess` is `SetBy.Analysis.Consumer`; `Users` is `SetBy.Analysis.Consumer`; `ReadUses` is `SetBy.Flow.Consumer`; `PriorityDeqGroup` is `SetBy.Analysis.Self`; `DoesNotConflictWith` is `Transfer.Mirror` with a custom `mirror` implementation over the stored symbol set; `DependencyEdges` is `Transfer.Mirror` (`src/spatial/metadata/access/AccessData.scala:8-86`). `User(sym, blk)` records a consumer and raw block for ephemeral-node removal (`src/spatial/metadata/access/AccessData.scala:16-25`). `DependencyEdge` carries `src`, `dst`, send/receive predicates over a `TimeStamp`, source/destination iterator support sets, and an `isPseudoEdge` hook whose metadata default is false (`src/spatial/metadata/access/AccessData.scala:49-60`). `TimeStamp` abstracts current iterator values plus first/last-iteration predicates and support (`src/spatial/metadata/access/AccessData.scala:71-84`).

The affine IR starts with `Prod(xs, m)`, which represents a product of index symbols and an integer multiplier, including static divisibility checks (`src/spatial/metadata/access/AccessPatterns.scala:14-71`). `Sum(ps, b)` represents sums of products plus an integer offset and defines algebra, division, divisibility, and partial evaluation (`src/spatial/metadata/access/AccessPatterns.scala:73-159`). `Modulus` stores an optional modulus value and combines with `+` and `%` using the source's set/unset rules (`src/spatial/metadata/access/AccessPatterns.scala:161-175`). `AffineProduct(a, i)` is a sum-of-products multiplier on one loop index, and `AddressPattern` stores affine components, offset, all-iterator provenance, and iterator starts (`src/spatial/metadata/access/AccessPatterns.scala:178-215`).

## Semantics

`AccessMatrix(access, matrix, unroll, isReader)` is the normalized dependence-analysis carrier; it records the symbol, sparse address matrix, surrounding unroll id, and read/write class (`src/spatial/metadata/access/AffineData.scala:14-31`). Its ISL-backed predicates check overlap, superset, and intersection over sparse matrices (`src/spatial/metadata/access/AffineData.scala:38-48`). `AffineMatrices` and `Domain` are both `Transfer.Remove`, so affine access spaces and symbolic constraints are analysis products that must be recomputed after transformations (`src/spatial/metadata/access/AffineData.scala:133-153`). `AccessPattern` is also `Transfer.Remove`, which matches its role as a pre-banking address-analysis product (`src/spatial/metadata/access/AccessPatterns.scala:261-268`).

`AddressPattern.getSparseVector` partially evaluates `Expect` constants in component multipliers and offsets, then returns a sparse vector only when component multipliers are constant or partially constant and the offset is constant or symbol-with-multiplier form (`src/spatial/metadata/access/AccessPatterns.scala:222-244`). Non-affine components are represented by a fresh `boundVar[I32]` random dimension whose `allIters` points back to the unresolved component iterators (`src/spatial/metadata/access/AccessPatterns.scala:232-242`). `toSparseVector` falls back to a caller-created random index with coefficient one and offset zero when `getSparseVector` returns `None` (`src/spatial/metadata/access/AccessPatterns.scala:246-254`).

`bankMuxWidth(N, B, alpha)` computes how many banks an access may touch under a proposed banking scheme: flat banking uses `alpha flatMul matrix`, residual `span`, and distinct expansion count, while hierarchical banking computes one residual span per row and multiplies the per-dimension counts (`src/spatial/metadata/access/AffineData.scala:73-89`). `arithmeticNodes` returns no nodes for directly banked accesses, otherwise estimates required `FixAdd`, `FixMul`, `FixDiv`, and `FixMod` nodes while treating multiply/divide/mod by powers of two as free and filtering zero operands in the hierarchical path (`src/spatial/metadata/access/AffineData.scala:91-124`).

## Implementation

`OpAccessOps.isParEnq` recognizes banked and scalar enqueues/writes that should be treated as parallel enqueues, including FIFO, merge buffer, LIFO, and SRAM writes (`src/spatial/metadata/access/package.scala:29-41`). `isStreamStageEnabler` recognizes destructive/inbound reads such as FIFO deq, FIFOReg deq, merge-buffer deq, LIFO pop, and stream-in reads; `isStreamStageHolder` recognizes outbound writes such as FIFO enq, FIFOReg enq, merge-buffer enq, LIFO push, and stream-out writes (`src/spatial/metadata/access/package.scala:59-83`). Access predicates classify readers, writers, unrolled readers/writers, vector accesses, deq interfaces, peeks, status readers, and special `RegAccum` writers (`src/spatial/metadata/access/package.scala:121-152`).

`addNonConflicts` stores `DoesNotConflictWith` symmetrically on both accesses, and `independentOf` answers true when either side's non-conflict set contains the other (`src/spatial/metadata/access/package.scala:154-165`). `accessIterators(access, mem)` compares non-master scopes for the memory and access, drops forever counters, and returns `accessIters diff memoryIters`; the comments document the direct hierarchy and MemReduce cross-subcontroller cases that motivated the master/subcontroller distinction (`src/spatial/metadata/access/package.scala:352-387`). `dephasingIters` asks the access leaf's `iterSynchronizationInfo` for offsets from a baseline unroll id, and `divergedIters` only reports offsets when two access matrices have identical access iterator sequences for the same memory (`src/spatial/metadata/access/package.scala:324-348`).

`precedingWrites` filters write matrices that intersect the read matrix and may precede the read, then partitions them by whether they may follow the read (`src/spatial/metadata/access/package.scala:389-406`). `isKilled` removes a write if another write must follow it before the observer read and is a superset of its address space (`src/spatial/metadata/access/package.scala:408-413`). `reachingWrites` returns all writes for global/unread memories, otherwise iterates reads, computes preceding writes over the remaining set, filters killed writes from before/after groups, removes reached writes from the remaining set, and accumulates the visible writes (`src/spatial/metadata/access/package.scala:415-438`). `flatIndex(indices, dims)` computes row-major strides with `dims.drop(d+1).prodTree` and sums `index * stride` (`src/spatial/metadata/access/package.scala:454-457`).

## Interactions

Access metadata depends on control hierarchy for `Ctrl`, `Blk`, `LCAWithDataflowDistance`, `mustFollow`, and scope iterator extraction (`src/spatial/metadata/access/AccessData.scala:6-7`, `src/spatial/metadata/access/package.scala:198-285`, `src/spatial/metadata/access/package.scala:352-387`). It depends on memory metadata for banking residuals, dispatch/bank accessors, and segment mapping used by `AccessMatrix.laneIndex` and `segmentAssignment` (`src/spatial/metadata/access/AffineData.scala:126-131`, `src/spatial/metadata/access/package.scala:167-169`). Pseudo-edge exclusion in downstream dataflow is represented in metadata only by `DependencyEdge.isPseudoEdge`; the exclusion policy itself is outside this metadata package and remains an integration contract (inferred, unverified) (`src/spatial/metadata/access/AccessData.scala:49-60`).

## HLS notes

The affine IR should port as explicit algebraic data plus sparse matrix wrappers, but all `Transfer.Remove` products should be re-derived after Rust/HLS transformations rather than serialized from Scala-era symbols (`src/spatial/metadata/access/AccessPatterns.scala:261-268`, `src/spatial/metadata/access/AffineData.scala:141-153`). HLS memory partitioning should preserve the `(N, B, alpha)` query interface while replacing ISL and residual-generator dependencies with the selected Rust equivalents (inferred, unverified) (`src/spatial/metadata/access/AffineData.scala:73-124`).

## Open questions

- Q-meta-04: Which downstream queries must ignore `DependencyEdge.isPseudoEdge`, and should the exclusion live on the edge type or in the query API?
- Q-meta-05: Should `AddressPattern.getSparseVector` keep representing partially non-affine terms with `boundVar[I32]`, or should the Rust port use an explicit `RandomDimension` node?
- Q-meta-06: Can `accessIterators` be rewritten around explicit MemReduce stage ownership instead of relying on `accessIters diff memoryIters`?
