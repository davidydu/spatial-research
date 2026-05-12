---
type: spec
concept: banking
source_files:
  - "src/spatial/traversal/AccessAnalyzer.scala:1-322"
  - "src/spatial/traversal/AccessExpansion.scala:1-129"
  - "src/spatial/traversal/MemoryAnalyzer.scala:1-168"
  - "src/spatial/traversal/MemoryAllocator.scala:1-107"
  - "src/spatial/traversal/banking/BankingStrategy.scala:1-29"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala:1-818"
  - "src/spatial/traversal/banking/ExhaustiveBanking.scala:1-487"
  - "src/spatial/traversal/banking/FullyBanked.scala:1-298"
  - "src/spatial/traversal/banking/CustomBanked.scala:1-24"
  - "src/spatial/traversal/banking/FIFOConfigurer.scala:1-102"
  - "src/spatial/Spatial.scala:142"
  - "src/spatial/Spatial.scala:203"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[Memories]]"
  - "[[10 - Flows and Rewrites]]"
status: draft
---

# Banking

## Summary

Banking is the analysis pipeline that turns abstract memory accesses into concrete physical-bank assignments, buffer depths, port numberings, and hardware-resource bindings. It runs as the `bankingAnalysis` sub-sequence (`src/spatial/Spatial.scala:142, 203`) which expands to `retimeAnalysisPasses ++ Seq(accessAnalyzer, iterationDiffAnalyzer, printer, memoryAnalyzer, memoryAllocator, printer)`. Its three pillars are: (1) `AccessAnalyzer` extracts affine access patterns and stages them as access matrices; (2) `MemoryAnalyzer` (a `Codegen`) iterates `LocalMemories.all` and runs a per-memory `MemoryConfigurer` that drives `BankingStrategy.bankAccesses` to find a banking scheme of minimum estimated cost; (3) `MemoryAllocator` greedily assigns each computed duplicate to a physical `MemoryResource` (URAM → BRAM → LUTRAM) using a first-fit bin-pack.

## Stage 1 — `AccessAnalyzer.Affine` extraction

`case class AccessAnalyzer(IR: State) extends Traversal with AccessExpansion` (`traversal/AccessAnalyzer.scala:19`) walks the IR inside loops, building affine descriptions of every memory access. The analyzer's heart is the `Affine` extractor object (`:140-177`) which recursively pattern-matches an `Idx` value against four sub-extractors and returns `Option[(Seq[AffineComponent], Sum, Modulus)]` — components, constant offset, and modulus.

The four sub-extractors live at `:75-88`:

```scala
object Plus  { def unapply[W](x: Ind[W]): Option[(Ind[W],Ind[W])] = x.op.collect{case FixAdd(LU(a),LU(b)) => (a,b) }}
object Minus { def unapply[W](x: Ind[W]): Option[(Ind[W],Ind[W])] = x.op.collect{case FixSub(LU(a),LU(b)) => (a,b) }}
object Times { def unapply[W](x: Ind[W]): Option[(Ind[W],Ind[W])] = x.op.collect{
  case FixMul(LU(a),LU(b)) => (a,b)
  case FixSLA(LU(a),Expect(b)) => (a,a.from(scala.math.pow(2,b)))
}}
object Read  { def unapply[W](x: Ind[W]): Option[Ind[W]] = x.op.collect{case RegRead(reg) if mostRecentWrite.contains(reg) => mostRecentWrite(reg).asInstanceOf[Ind[W]]}}
```

`LU` (look-up) substitutes the most recent write to a `Reg` for its `RegRead` (`:87`); `Read` is the same substitution but only fires if the unapply succeeds. `Times` includes the `FixSLA(a, const)` shift-left-arithmetic sugar as `a * 2^b` (`:79`). `Plus` and `Minus` are straightforward. `Times` only matches if the multiplier is loop-invariant w.r.t. the iterators in the affine component (`:165-166`).

`combine(a1, a2)` (`:125-138`) is the canceller: when adding `a1` and `-a2`, any `AffineComponent` in `a1 ++ (-a2)` whose negation appears elsewhere is cancelled. The remaining components form the merged sum.

`Affine.unapply` recursion (`:150-176`):

- A loop iterator alone returns `Some(Seq(AffineComponent(stride(i), i)), Zero, NotSet)` (`:152`).
- A null-counter iterator (start=0, end=1) returns `Some(Nil, Zero, NotSet)` (`:153`).
- `Plus(Affine(a1,b1,_), Affine(a2,b2,_))` returns `Some(combine(a1,a2), b1+b2, NotSet)` (`:156`).
- `Minus(Affine(...), Affine(...))` returns `Some(combine(a1,-a2), b1-b2, NotSet)` (`:159`).
- `Times` cases (`:165-166`) distribute a loop-invariant multiplier through.
- Default `case s` returns `Some(Nil, Sum.single(s), NotSet)` (`:175`) — the symbol becomes a single offset, not an iterator-component.

The pass's `visit` (`:265-321`) handles three top-level cases: counter newing (extracts patterns for start/end/step), loops (sets up `iters`, `iterStarts`, `loops`, `scopes` and recurses into bodies via `inLoop`), and `Reader`/`Writer`/`Dequeuer`/`Enqueuer` accesses (calls `setAccessPattern` or `setStreamingPattern`).

## Stage 2 — `AccessExpansion` materializes access matrices

`trait AccessExpansion` (`traversal/AccessExpansion.scala:15`) is mixed into `AccessAnalyzer`. After `getAccessAddressPattern` produces a per-dimension `AddressPattern`, `getUnrolledMatrices` (`:66-127`) materializes one `AccessMatrix` per unroll ID. The cross-product `multiLoop(ps)` (`:83`) iterates all UID combinations from the outer iterators' parallelism. For each UID:

- For each iterator-keyed input column, compute `(a = vec(x)*ps(idx), b = vec(x)*uid(idx))` (`:91-94`) — the post-unroll stride and the constant-offset shift due to this lane.
- For non-iterator inputs, `unrolled(x, xid)` (`:26-31`) substitutes either a `LaneStatic` resolution (`Right(int)`, `:28`) or a fresh bound variable cached by `(x, uid)` keys (`Left(idx)`, `:29`).

Per-access metadata `accessPattern` and `affineMatrices` is written at `traversal/AccessAnalyzer.scala:224-225`.

`getOrAddDomain` (`AccessExpansion.scala:42-52`) caches `ConstraintMatrix[Idx]` for each `Idx`, building min/max constraints from `ctrStart`/`ctrEnd` via `constraint`. This is what gives the polyhedral solver in banking its boundary conditions.

## Stage 3 — `MemoryAnalyzer` is a `Codegen` (not a `Pass`)

`case class MemoryAnalyzer(IR: State)(implicit isl: ISL, areamodel: AreaEstimator) extends Codegen` (`traversal/MemoryAnalyzer.scala:17`). The `Codegen` parent gives it `withGen(out, entryFile){ … }` machinery; it sets `override val ext: String = "html"` (`:22`) and `override def entryFile: String = s"decisions_${state.pass}.html"` (`:24`) so each invocation writes a per-pass HTML decision report. The analysis itself happens as a side effect of `process` (`:111-123`):

```scala
override protected def process[R](block: Block[R]): Block[R] = {
  config.enGen = true
  withGen(out, entryFile) {
    emitHeader()
    run()
    emitFooter()
  }
  …
  block
}
```

`run()` (`:141-167`) partitions `LocalMemories.all` into `(frozen, memories)` based on `freezeMem`, then for each non-frozen memory calls `configurer(m).configure()` and times it. Final HTML emits two collapsible reports: sorted by estimated area, sorted by total search time (`:153-163`).

The configurer dispatch (`:125-139`) selects `BankingStrategy` per memory type:

- `SRAM`, `LineBuffer`, `FIFO` (via `FIFOConfigurer`), `LIFO` (via `FIFOConfigurer`), `StreamIn`, `StreamOut` → `ExhaustiveBanking`.
- `RegFile`, `LUT`, `Reg`, `FIFOReg` → `FullyBanked`.
- `MergeBuffer`, `LockSRAM` → `CustomBanked`.

## Stage 4 — `MemoryConfigurer.configure()`

`class MemoryConfigurer[+C[_]](mem: Mem[_,C], strategy: BankingStrategy)` (`traversal/banking/MemoryConfigurer.scala:21`) is the per-memory orchestrator and the largest file in this subsystem at 818 lines. Its top-level entry point is `configure()` (`:55-83`):

```scala
def configure(): Unit = {
  …
  resetData(readers, writers)
  val readMatrices = readers.flatMap{rd => rd.affineMatrices }
  val writeMatrices = writers.flatMap{wr => wr.affineMatrices}
  val instances = bank(readMatrices, writeMatrices)
  summarize(instances)
  finalize(instances)
  pirCheck(instances)
}
```

`resetData` (`:85-91`) clears `Dispatch`/`Ports` on accesses and `Duplicates` on `mem`. `bank` (`:440-446`) groups accesses, then calls `mergeReadGroups` (`:748-806`) (or `mergeWriteGroups` when no readers exist) which iterates groups, calls `bankGroups` per group, and greedily merges into existing instances when `getMergeAttemptError`/`getMergeError` allow (`:707-745`).

`schemesInfo` (`:52`) is a `HashMap[Int, HashMap[(BankingOptions, Int), Seq[DUPLICATE]]]` where the inner `DUPLICATE = (Seq[Banking], Seq[Int], Seq[String], Seq[Double])` records the chosen banking, mux-width histogram, auxiliary nodes, and 7-element cost breakdown. The HTML report (`MemoryAnalyzer.report`, `traversal/MemoryAnalyzer.scala:52-109`) reads `schemesInfo` to render per-instance scheme tables.

`cost` (`:449-519`) computes a `DUPLICATE` cost per banking choice. Memory-type dispatch:

- `SRAM[_,_]` (`:468-487`): asks `areamodel.estimateMem("LUTs"/"FFs"/"RAMB18"/"RAMB32", "SRAMNew", …)` then divides by per-resource weights (`lutWeight = 34260/100`, `ffWeight = 548160/100`, `bramWeight = 912/100` at `:456-458`). Adds auxiliary-node cost from `arithmeticNodes`.
- `RegFile`, `LineBufferNew`, fall-through (`:488-517`): same area model, no aux nodes.

`bank` produces one `Instance` per banked group set; `finalize` (`:115-163`) writes `mem.duplicates`, then for each instance writes `Dispatch`, `Ports`, and `GroupId` per access via `addPort`/`addDispatch`/`addGroupId` (`:122-135`). It also warns about read-before-write via `mem.hasInitialValues` checks (`:138-145`) and tags `isUnusedAccess = true` for accesses not consumed by any instance (`:148-161`).

`requireConcurrentPortAccess(a, b)` (`:427-437`) is the 7-disjunct concurrency rule that determines whether two accesses must share a buffer port:

```scala
(a.access == b.access && a.unroll != b.unroll) ||
  lca.isInnerPipeLoop ||
  (lca.isInnerSeqControl && lca.isFullyUnrolledLoop) ||
  (lca.isOuterPipeLoop && !isWrittenIn(lca)) ||
  (a.access.delayDefined && b.access.delayDefined && a.access.parent == b.access.parent && a.access.fullDelay == b.access.fullDelay) ||
  ((a.access.delayDefined && b.access.delayDefined && a.access.parent == b.access.parent && a.access.fullDelay != b.access.fullDelay) && (controllerLCA.isDefined && controllerLCA.get.isLoopControl)) ||
  (lca.isParallel || (a.access.parent == b.access.parent && (Seq(lca) ++ lca.ancestors).exists(_.willUnroll))) || (lca.isOuterControl && lca.isStreamControl)
```

This is consumed in `groupAccessesDefault` (`:233-300`) and `groupAccessUnroll` (`:343-398`) to decide whether two accesses must group together.

## Stage 5 — `BankingStrategy.bankAccesses`

`abstract class BankingStrategy` (`traversal/banking/BankingStrategy.scala:7-29`) is the polymorphic interface for finding a banking scheme:

```scala
def bankAccesses(
  mem:    Sym[_],
  rank:   Int,
  reads:  Set[Set[AccessMatrix]],
  writes: Set[Set[AccessMatrix]],
  attemptDirectives: Seq[BankingOptions],
  depth: Int
): Map[BankingOptions, Map[AccessGroups, FullBankingChoices]]
```

`FullBanking = Seq[Banking]` (`:9`) is a banking scheme; `FullBankingChoices = Seq[FullBanking]` (`:13`) is a list of valid schemes; `AccessGroups = Set[Set[AccessMatrix]]` (`:17`) is the multiset of access-group sets covered by a scheme.

The orchestrator is `MemoryConfigurer.bankGroups` (`:610-682`), which:

1. Computes `(metapipe, bufPorts, issue) = computeMemoryBufferPorts(...)` (`:631`) and derives `depth = bufPorts.values.collect{case Some(p) => p}.maxOrElse(0) + 1` (`:632`).
2. Builds the `BankingOptions` candidate grid: `combs(bankViews × nStricts × aStricts × dimensionDuplication)` (`:616`), then sorts by penalty `(view.P, N.P, alpha.P, regroup.P)` (`:619`) and partitions into "good" (low-penalty) and "bad" (high-penalty) directives.
3. Calls `strategy.bankAccesses(mem, rank, rdGroups, reachingWrGroups, attemptDirectives, depth)` (`:633`).
4. For each returned scheme, calls `cost(opt, depth, rds, reachingWrGroups)` (`:646`) to score it; picks the minimum (`:659`).
5. Materializes an `Instance(winningRdGrps, reachingWrGroups, ctrls, metapipe, winningBanking, depth, …)` (`:668`) including padding (`mem.stagedDims % p`) and accumulator type via `AccumType.Buff` if any read parent matches a write parent.

`bankViews` / `nStricts` / `aStricts` / `dimensionDuplication` (`:25-48`) are derived from memory metadata: explicit-banking forces a single-element set; `enableForceBanking` overrides the default; `mem.isLineBuffer` forces hierarchical with the last dim segregated; `mem.isFullFission` forces all-axes regroup.

## Stage 6 — `ExhaustiveBanking` search

`case class ExhaustiveBanking()` (`traversal/banking/ExhaustiveBanking.scala:27`) is the main strategy. It tries `BankingView × NStrictness × AlphaStrictness × RegroupDims` combinations subject to two effort gates.

`solutionCache` (`:45`) keys on `(regroupedAccs, nStricts, aStricts, axes)` and avoids re-solving the same projected-access problem.

`schemesFoundCount` (`:47`) tracks per-(view, regroup) hit counts. `wantScheme` (`:188-198`) implements 3-level effort semantics:

- `effort == 0` — quit after the first scheme is found anywhere (`:189`).
- `effort == 1` (default) — at most one scheme per (view, regroup), and only allow regroup that is fully empty or fully covers the view rank (the "4 regions" — flat/hierarchical × full-duplication or no-regroup) (`:190-193`).
- `effort == 2` — at most 2 schemes per (view, regroup), regardless of regroup pattern (`:194-197`).

The two-step process (`:330-358`):

1. **Iterator dephasing**: `generateSubstRules(reads)` and `generateSubstRules(writes)` (`:63-69`) call `dephasingIters(a, …, mem)` and produce `Map[(Idx, Seq[Int]), (Idx, Int)]` — each unrolled-iterator-uid pair is mapped either to itself with an integer offset (deterministic dephasing) or to a fresh bound `boundVar[I32]` (non-determinable dephasing, treated as a random variable).
2. **Rewrite**: `rewriteAccesses(reads, readIterSubsts)` (`:70-92`) calls `a.substituteKeys(keyRules)` per access matrix, recording `accMatrixMapping[newa] = a` so the original access can be recovered later via `reverseAM`.

After dephasing, `findSchemes` (`:180-325`) iterates `attemptDirectives`. For each scheme passing `wantScheme`, it `view.expand()` to enumerate axis subsets, projects each group onto the active dimensions via `projectGroup` (`:94-103`), and `repackageGroup` (`:106-149`) regroups under the projection considering "non-conflicting prior/post complement" XOR — a hierarchical-banking subtlety where if two accesses' un-banked dimensions don't conflict, they don't need to be in the same group.

`findBanking` (`:367-433`) performs the polyhedral search:

- `Nmin = max(Nmin_writes, Nmin_reads_or_half-if-dual-port)` (`:374-377`).
- `Ncap = stagedDims.product max Nmin` (`:378`).
- For each `N in nStricts.expand(Nmin, Ncap, dims, …)`:
  - For each `alpha in aStricts.expand(rank, N, stagedDims, axes)`:
    - If `B == 1`: try `checkCyclic(mem, N, alpha, regroupedGrps, dualPortHalve)` (`:443-460`) — every pair `(a0, a1)` in each group must have `(alpha*(a0-a1) + (k,N)) === 0` ⇒ empty domain.
    - Else try `checkBlockCyclic(mem, N, B, alpha, …)` (`:462-485`) — adds 4-constraint Presburger system with `B`-stride.
- Bounded by `attempts < spatialConfig.bankingTimeout` (`:392, 430`) and `validSchemesFound < spatialConfig.numSchemesPerRegion` (`:392, 405`).

## Stage 7 — `FullyBanked`

`case class FullyBanked()` (`traversal/banking/FullyBanked.scala:16`) is the strategy used for `Reg`/`RegFile`/`LUT`/`FIFOReg`. It mirrors `ExhaustiveBanking`'s scaffolding but its `findBanking` (`:275-283`) is trivial:

```scala
val N = filteredStagedDims.head
Option(Seq(ModBanking.Simple(N, axes, 1)))
```

i.e. the full per-axis dimension count becomes the bank count, with stride 1 — a literal flip-flop bank per element. `FullyBanked` still runs the dephasing pipeline and `wantScheme` gating but `findBanking` short-circuits the polyhedral search.

`MemoryConfigurer.bankViews`/`nStricts`/`aStricts`/`dimensionDuplication` for FullyBanked are forced single-element: `Seq(Hierarchical(rank))`, `Seq(NRelaxed)`, `Seq(AlphaRelaxed)`, `RegroupHelper.regroupNone` (`MemoryConfigurer.scala:25, 34, 38, 42`).

## Stage 8 — `CustomBanked`

`case class CustomBanked()` (`traversal/banking/CustomBanked.scala:11`) is a no-op strategy used for `LockSRAM` and `MergeBuffer` where the user or backend (Plasticine) inherently promises correctness:

```scala
override def bankAccesses(...): Map[BankingOptions, Map[AccessGroups, FullBankingChoices]] = {
  Map(attemptDirectives.head -> Map(reads ++ writes -> Seq(Seq(UnspecifiedBanking(Seq.tabulate(rank){i => i})))))
}
```

The single returned scheme is `UnspecifiedBanking` covering all axes (`:21`); no analysis is performed.

## Stage 9 — `FIFOConfigurer`

`class FIFOConfigurer[+C[_]]` (`traversal/banking/FIFOConfigurer.scala:16`) extends `MemoryConfigurer` for `FIFO`/`LIFO`. It overrides `requireConcurrentPortAccess` to a 5-case rule (`:20-26`):

```scala
(a.access == b.access && (a.unroll != b.unroll || a.access.isVectorAccess)) ||
  lca.isPipeLoop || lca.isOuterStreamLoop ||
  (lca.isInnerSeqControl && lca.isFullyUnrolledLoop) ||
  lca.isParallel
```

vs. the 7-case general rule. The dropped cases are `lca.isOuterPipeLoop && !isWrittenIn(lca)` and the `delayDefined`/`fullDelay` pair — these don't apply to FIFOs because FIFOs are not N-buffered, so "write reaches buffer port" questions are meaningless.

Critically, `FIFOConfigurer.bankGroups` (`:62-100`) refuses to bank groups that happen concurrently:

```scala
if (haveConcurrentReads || haveConcurrentWrites) {
  Left(UnbankableGroup(mem,rdGroups.flatten,wrGroups.flatten))
}
```

This raises `UnbankableGroup` rather than guessing. FIFOConfigurer also forces `depth = 1` (`:76, 91`) since FIFOs cannot be N-buffered.

## Stage 10 — `MemoryAllocator`

`case class MemoryAllocator(IR: State)(implicit mlModel: AreaEstimator) extends Pass` (`traversal/MemoryAllocator.scala:12`) is the final step. After `MemoryAnalyzer` has set `mem.duplicates` for every memory, `MemoryAllocator.allocate()` (`:25-104`) greedy first-fits each duplicate to a `MemoryResource`.

Algorithm:

1. Partition `LocalMemories.all.filter(!_.isCtrlBlackbox)` into `(sramAble, nonSRAM)` via `canSRAM(mem) = mem.isSRAM || mem.isFIFO || mem.isLIFO` (`:21-23, 36`).
2. Initialize `unassigned` from each `sramAble` mem's duplicates with `Instance(mem, dup, idx)` (`:38-40`).
3. Initialize `capacity = target.capacity` (`:46`).
4. Iterate `target.memoryResources` in order, **dropping the last** (`:59`) — for Xilinx this is `URAM_RESOURCE`, `BRAM_RESOURCE`, `URAM_RESOURCE_OVERFLOW` (skipping `LUTs_RESOURCE`).
5. For each resource, sort unassigned by `-rawCount` (descending area cost, `:78`) and iterate. Per instance:
   - `area = areaMetric(mem, dup, resource)` (`:31-33`).
   - `depth = areaModel.memoryBankDepth(mem, dup)` (`:83`).
   - Assign iff `area ≤ capacity && depth ≥ resource.minDepth` (`:85`):

     ```scala
     dup.resourceType = Some(resource)
     capacity -= area
     assigned += inst
     ```

   - Skip with debug log otherwise.
6. Anything still in `unassigned` after the loop falls through to `resources.last` (typically LUTRAM): `inst.memory.resourceType = Some(resources.last)` (`:102`).
7. All non-SRAM-able memories (Reg/RegFile/LUT/etc.) get `resources.last` unconditionally (`:103`).

This is purely greedy bin-packing: there is no backtracking, no fractional assignment, and the order of `target.memoryResources` defines priority.

## Iterator dephasing (cross-cut)

Iterator dephasing is the mechanism that lets banking analyse N-buffered accesses correctly. `dephasingIters` (called from `ExhaustiveBanking.scala:64` and `FullyBanked.scala:53`) walks `(iter, uid)` pairs for each access and asks: when this iterator's lane fires, is the offset deterministic? If so, return `Some(offset)`; else `None`.

`generateSubstRules` (`ExhaustiveBanking.scala:63-69`) translates this into a substitution table:

```scala
toRewrite.map {
  case ((i, addr), ofs) if ofs.isDefined => (i, addr) -> (i, ofs.get)
  case ((i, addr), ofs) if ofs.isEmpty => (i, addr) -> (boundVar[I32], 0)
}
```

Deterministic offset: keep the iterator, attach the offset to the constant column. Non-deterministic: replace with a fresh bound variable (and offset 0).

`rewriteAccesses` (`:70-92`) applies the rules: for each access matrix, compute `keyRules` from the access's `accessIterators` zipped with `getDephasedUID(aIters, a.unroll, i)` (the dephased UID at iterator-position `i`), invoke `mem.addDephasedAccess(a.access)` if any rule fires, and call `a.substituteKeys(keyRules)`. The new matrix is recorded in `accMatrixMapping[newa] = a` so post-banking code can recover the original access.

## Interactions

- **Reads**: `accessPattern` and `affineMatrices` from `AccessAnalyzer`; `iterDiff` from `IterationDiffAnalyzer`; `fullDelay`/`inCycle` from the first `RetimingAnalyzer` run; `explicitBanking`/`explicitNs`/`explicitAlphas`/`nConstraints`/`alphaConstraints`/`bankingEffort` from user metadata; `target.capacity`/`target.memoryResources`/`resource.minDepth` from the target.
- **Writes**: `Duplicates`, `Dispatch`, `Ports`, `GroupId`, `isDephasedAccess`, `isUnusedAccess` from `MemoryAnalyzer`; `dup.resourceType` from `MemoryAllocator`. The HTML side-effect file `decisions_<pass>.html` is emitted to `out/`.
- **Order in pipeline**: runs at step 13 in the canonical pipeline (`Spatial.scala:142, 203`), i.e. after pipe-insertion and FIFO-init but before `unrollTransformer`. Banking writes the `Duplicates` metadata that `MemoryUnrolling` consumes to materialize per-bank physical memories.

## HLS notes

Banking is **rework**. The polyhedral search in `ExhaustiveBanking.checkCyclic`/`checkBlockCyclic` is general but expensive; HLS tools like Vitis pragmas (`#pragma HLS array_partition`) only support `cyclic`, `block`, and `complete` partition modes per dimension. A Rust+HLS reimplementation would likely emit pragmas directly from the `BankingOptions` choice and let HLS handle the actual partition. The N-buffer machinery (`computeMemoryBufferPorts`, `Instance.metapipe`) maps cleanly to `#pragma HLS dependence` + `#pragma HLS pipeline`.

## Open questions

- `Q-pp-01` — `MemoryAnalyzer` extends `Codegen` rather than `Pass`. The HTML file emission is purely a side effect; is anything downstream actually consuming `decisions_<pass>.html`, or is this strictly a debugging artifact?
- `Q-pp-02` — `MemoryAllocator.allocate` has a `println(s"TODO: un-gut memory allocator")` at `:16`. What is the missing functionality?
- `Q-pp-03` — `FIFOConfigurer.requireConcurrentPortAccess` drops 2 disjuncts vs the general rule. The deep dive infers the dropped cases are because FIFOs aren't N-buffered, but the comment in the source doesn't make this explicit.
