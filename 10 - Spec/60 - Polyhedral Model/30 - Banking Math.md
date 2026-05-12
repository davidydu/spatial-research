---
type: spec
concept: Banking Math
source_files:
  - "src/spatial/metadata/access/AffineData.scala:24-131"
  - "src/spatial/metadata/access/AccessPatterns.scala:14-268"
  - "utils/src/utils/math/package.scala:7-229"
  - "src/spatial/metadata/memory/BankingData.scala:547-625"
  - "src/spatial/traversal/banking/ExhaustiveBanking.scala:367-486"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala:440-633"
source_notes:
  - "[[poly-models-dse]]"
hls_status: clean
depends_on:
  - "[[10 - ISL Binding]]"
  - "[[20 - Access Algebra]]"
status: draft
---

# Banking Math

## Summary

Spatial's banking math connects symbolic address expressions, sparse affine matrices, ISL emptiness checks, and hardware banking parameters `(N, B, alpha, P)`. `AccessMatrix` pairs an access symbol with a `SparseMatrix[Idx]`, an unroll index, and a reader flag, giving banking code one affine matrix per unrolled access lane (`src/spatial/metadata/access/AffineData.scala:14-29`). The symbolic front end is `AddressPattern`, which represents sums of products over loop indices and offsets before attempting conversion to a `SparseVector[Idx]` (`src/spatial/metadata/access/AccessPatterns.scala:195-244`). The math helpers in `utils.math` define the bank-period correction, volume estimates, and arithmetic predicates used by the search (`utils/src/utils/math/package.scala:7-37`, `utils/src/utils/math/package.scala:134-229`).

## Syntax or API

`AccessMatrix` exposes `overlapsAddress`, `isSuperset`, and `intersects`; these delegate to the implicit `ISL` instance and inherit its current implementation state, including the `isSuperset` and `intersects` stubs (`src/spatial/metadata/access/AffineData.scala:38-48`, `poly/src/poly/ISL.scala:164-174`). It exposes `isDirectlyBanked(N,B,alpha)` as `bankMuxWidth(N,B,alpha) == 1` (`src/spatial/metadata/access/AffineData.scala:73-76`). `bankMuxWidth` returns the number of distinct banks an access may touch under a candidate scheme: flat banking multiplies `alpha` by the matrix into one sparse bank vector, while hierarchical banking multiplies each dimension separately and multiplies per-dimension residual sizes (`src/spatial/metadata/access/AffineData.scala:78-89`).

`arithmeticNodes(N,B,alpha)` estimates runtime arithmetic needed for bank resolution and returns tuples `(opName, operand1, operand2)` (`src/spatial/metadata/access/AffineData.scala:91-124`). It emits no nodes when the access is directly banked; otherwise it estimates affine adds, partition-factor multiplies, block dividers, and modulo operators, skipping power-of-two multiply/divide/mod cases (`src/spatial/metadata/access/AffineData.scala:91-108`, `src/spatial/metadata/access/AffineData.scala:109-121`). `MemoryConfigurer.cost` uses `bankMuxWidth` to build read/write histograms and uses `arithmeticNodes` to estimate auxiliary arithmetic area for SRAM banking (`src/spatial/traversal/banking/MemoryConfigurer.scala:448-487`).

## Semantics

`AddressPattern` is the symbolic bridge into sparse algebra. `Prod` models a coefficient product with symbol list `xs` and multiplier `m`, with static division allowed only when the divisor's symbols and coefficient divide the product (`src/spatial/metadata/access/AccessPatterns.scala:14-64`). `Sum` models a sum of `Prod` plus a constant `b`, supports product expansion, addition, subtraction, exact static division where legal, and partial evaluation of `Expect(c)` symbols (`src/spatial/metadata/access/AccessPatterns.scala:73-151`). `Modulus` tracks whether a modulus is set, adds set moduli by summing them, combines `%` by taking the minimum set modulus, and serializes unset as `0` through `toInt` (`src/spatial/metadata/access/AccessPatterns.scala:161-175`). `AffineProduct` and `AffineComponent` attach those symbolic multipliers to loop indices (`src/spatial/metadata/access/AccessPatterns.scala:178-192`).

`AddressPattern.getSparseVector` partially evaluates constants, accepts expressions where all or at least one loop multiplier is constant and the offset is constant or a sum of symbol-with-multiplier products, and then partitions constant-affine components from random components (`src/spatial/metadata/access/AccessPatterns.scala:222-241`). If non-affine components remain, it introduces a fresh bound variable as a random dimension whose `allIters` depend on the original non-affine iterators (`src/spatial/metadata/access/AccessPatterns.scala:232-241`). `toSparseVector` falls back to `SparseVector(Map(y -> 1), 0, ...)` for expressions that cannot be represented, so non-affine addresses become a fresh unknown dimension rather than being dropped (`src/spatial/metadata/access/AccessPatterns.scala:246-254`).

## Implementation

The key banking-period function is `computeP(n, b, alpha, stagedDims, errmsg)` (`utils/src/utils/math/package.scala:134-209`). Its source comment is explicit that it is a paper corrigendum to Wang et al. FPGA '14: the paper assumed unit periodicity in the leading dimension, which the code marks wrong with `alpha = [1,2], N = 4, B = 1` as the motivating example (`utils/src/utils/math/package.scala:134-149`). The correction computes `P_raw_i = n*b/gcd(n*b, alpha_i)` and uses `1` when `alpha_i == 0` (`utils/src/utils/math/package.scala:192-194`). It expands each dimension with divisors of `P_raw_i` plus the staged dimension when `P_raw_i != 1 && b == 1`, takes Cartesian products, filters by a volume constraint, and then filters by `spansAllBanks` (`utils/src/utils/math/package.scala:193-203`).

`spansAllBanks(p,a,N,B)` enumerates `allLoops(p,a,B,Nil)`, reduces addresses modulo `N`, and checks that every bank appears no more than `B` times in the fenced region (`utils/src/utils/math/package.scala:103-115`). `allLoops` recursively enumerates a hypercube of loop values and adds `i*a.head/B` for each dimension, so block size participates by integer division before bank reduction (`utils/src/utils/math/package.scala:103-111`). `hiddenVolume`, `volume`, and `numBanks` compute padded physical storage estimates: `hiddenVolume` is zero with no `P`, has a special flat-banking case for one `N`, and otherwise multiplies per-dimension hidden extents; `volume` adds logical element count, and `numBanks` multiplies `Ns` (`utils/src/utils/math/package.scala:219-229`).

The math package also carries hardware-oriented arithmetic helpers. `isPow2`, `gcd`, `coprime`, and `divisors` are direct integer predicates used throughout search (`utils/src/utils/math/package.scala:7-37`). `modifiedCrandallSW(x,t,c)` is a software simulation of Crandall division by a Mersenne or pseudo-Mersenne divisor: it asserts `t+c` is a power of two, iterates quotient/residue refinements, applies a final correction loop, and prints diagnostics if the result disagrees with naive division or modulo (`utils/src/utils/math/package.scala:73-101`).

## Interactions

Banking search is exhaustive within its configured candidate sets. `MemoryConfigurer` selects views, `NStrictness`, `AlphaStrictness`, and dimension-duplication strategies based on user constraints and defaults (`src/spatial/traversal/banking/MemoryConfigurer.scala:25-48`). It then builds all combinations of those directives and asks the banking strategy to find candidate bankings for read/write groups (`src/spatial/traversal/banking/MemoryConfigurer.scala:610-633`). `ExhaustiveBanking.findBanking` expands possible `N` values, expands alpha vectors for each `N`, tries cyclic banking first, then block-cyclic banking, and calls `computeP` for every successful `(N,B,alpha)` scheme (`src/spatial/traversal/banking/ExhaustiveBanking.scala:367-431`). The conflict checks are ISL emptiness queries over cyclic equalities or block-cyclic inequality systems (`src/spatial/traversal/banking/ExhaustiveBanking.scala:443-486`).

Two runtime bottlenecks are worth preserving as explicit design constraints. `NBestGuess.factorize` enumerates `1..number` and filters divisors, so it is O(N) per call; `NBestGuess.expand` calls it across access counts and staged-dimension product, and banking search then iterates candidate `N` and alpha combinations, making the practical search easy to push toward O(N^2)-like behavior for large memory sizes (`src/spatial/metadata/memory/BankingData.scala:547-563`, `src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431`). Alpha search is also broad: `AlphaBestGuess` forms access-based products, dimension-based products, coprimes, and easy power-of-two/sum-of-power-of-two values, then generates distinct coprime vectors through `selectAs` (`src/spatial/metadata/memory/BankingData.scala:581-625`).

## HLS notes

This concept is clean for HLS. The target-specific part is not the math but how the chosen banks, blocks, alphas, and offset chunks become memories and address logic. The rewrite should keep `computeP`'s Wang et al. correction, `spansAllBanks`, residual-bank enumeration, and the distinction between direct and crossbar banking (`utils/src/utils/math/package.scala:134-203`, `src/spatial/metadata/access/AffineData.scala:73-89`). The exhaustive search bottleneck should be revisited before scaling HLS design-space runs, because the current candidate enumeration is intentionally simple rather than asymptotically careful (`src/spatial/metadata/memory/BankingData.scala:547-563`, `src/spatial/traversal/banking/ExhaustiveBanking.scala:392-431`).

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-04 - 2026-04-24 Banking-search pruning strategy for HLS|Q-pmd-04]]
