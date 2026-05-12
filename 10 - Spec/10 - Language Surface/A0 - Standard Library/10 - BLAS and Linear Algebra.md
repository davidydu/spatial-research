---
type: spec
concept: standard-library-blas-linear-algebra
source_files:
  - "src/spatial/lib/BLAS.scala:8-210"
  - "src/spatial/lib/LinearAlgebra.scala:7-257"
  - "src/spatial/math/LinearAlgebra.scala:8-60"
source_notes:
  - "[[open-questions-stdlib]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[50 - Math and Helpers]]"
status: draft
---

# BLAS and Linear Algebra

## Summary

Spatial has two standard-library linear algebra layers and one math-staging companion. `object BLAS` exposes DRAM-facing BLAS-style templates: `Dot`, `Axpy`, `Gemm`, `Gemv`, `Ger`, `Scal`, and `Axpby` (`src/spatial/lib/BLAS.scala:8-210`). `trait LinearAlgebra` exposes on-chip SRAM matrix helpers: `matmult`, three overloaded `gemm` entrypoints for scalar/vector/matrix `C`, one `gemm_fpga_fix` scalar-`C` variant, and additional image/NN routines below the GEMM region (`src/spatial/lib/LinearAlgebra.scala:7-257`). `object spatial.math.LinearAlgebra` provides a lower-level `transpose` helper and a scalar-`C` `gemm` that stages `Blackbox.GEMM` over output tiles (`src/spatial/math/LinearAlgebra.scala:8-60`). This entry is `hls_status: rework` because the current APIs are clean user templates, but the BLAS/GEMM kernels encode tile sizes, parallel factors, blackbox calls, and some unused BLAS parameters directly in Scala source (`src/spatial/lib/BLAS.scala:15-25`, `src/spatial/lib/BLAS.scala:61-99`, `src/spatial/math/LinearAlgebra.scala:47-52`).

## API

`BLAS.Dot[T:Num](N, X, incX, Y, incY): T` reduces a tiled product of `X` and `Y` and returns `out.value` (`src/spatial/lib/BLAS.scala:8-31`). Its signature includes `incX` and `incY`, but the body loads contiguous slices `X(i::i+elements)` and `Y(i::i+elements)` instead of using those increments (`src/spatial/lib/BLAS.scala:10-23`). `BLAS.Axpy` accepts `alpha`, `X`, `Y`, and `res`; each tile computes `alpha * x_tile(j) + y_tile(j)` and stores to `res` (`src/spatial/lib/BLAS.scala:33-57`). `BLAS.Gemm` accepts `alpha`, `beta`, and leading-dimension parameters, but the implemented body accumulates only products from `A` and `B` into `c_tile` and stores that tile to `C` (`src/spatial/lib/BLAS.scala:61-99`). `BLAS.Gemv` accepts `alpha` and `beta`, but the body reduces `A(i,j) * X(j)` into `y_tile` and stores it to `Y` (`src/spatial/lib/BLAS.scala:104-139`). `BLAS.Ger` accepts `alpha`, but the body stores `x_tile(ii) * y_tile(jj)` into `A` (`src/spatial/lib/BLAS.scala:142-170`). `BLAS.Scal` uses `alpha` to scale `X` into `Y`, and `Axpby` composes `Scal` followed by `Axpy` (`src/spatial/lib/BLAS.scala:175-210`).

`LinearAlgebra.matmult` takes output/input SRAM2 memories plus `transA`, `transB`, `transY`, and parallel factors `mp`, `kp`, `np` (`src/spatial/lib/LinearAlgebra.scala:8-19`). It derives `M`, `K`, and `N` from the transpose flags, builds `getA`, `getB`, and `storeY`, and reduces over `K` for each output element (`src/spatial/lib/LinearAlgebra.scala:20-34`). `LinearAlgebra.gemm` overloads wrap scalar `C`, vector `C`, or matrix `C` in `CScalar`, `CVector`, or `CMatrix` before dispatching to `gemm_generalized` (`src/spatial/lib/LinearAlgebra.scala:37-101`). `gemm_generalized` supports `transA`, `transB`, `transY`, `sumY`, `alpha`, and `beta`, and its `getC` helper broadcasts scalar `C`, indexes vector `C` by column, or indexes matrix `C` by row/column (`src/spatial/lib/LinearAlgebra.scala:108-142`).

## Algorithm

The BLAS kernels use explicit block tiles. `Dot` iterates `N by 64`, bounds the tail with `min(64, N - i)`, loads two SRAM tiles, then reduces the elementwise product across the local tile before the outer reduce combines tiles (`src/spatial/lib/BLAS.scala:15-30`). `Axpy` uses the same 64-wide tile shape, adds a destination tile, computes the scaled vector sum, and stores the active slice (`src/spatial/lib/BLAS.scala:41-57`). `BLAS.Gemm` is the clearest block-tile plus accumulate pattern: outer loops tile `M` and `N` by 64, `MemReduce` iterates `K by 64`, `Parallel` loads matching `A` and `B` tiles, nested loops reduce `elements_k` products into `c_tile_local`, and the `MemReduce` combiner accumulates local tiles into `c_tile` (`src/spatial/lib/BLAS.scala:69-99`).

`LinearAlgebra.gemm_generalized` first detects special vector shapes. It treats row-vector times column-vector or column-vector times row-vector as an outer-product case and writes `getA(i,0) * getB(0,j) * alpha + getC(i,j) * beta` for every `(i,j)` (`src/spatial/lib/LinearAlgebra.scala:144-170`). It treats matching row-vector or matching column-vector pairs as an inner product, reduces over `K`, then writes one output element after applying `alpha`, `beta`, and `getC(0,0)` (`src/spatial/lib/LinearAlgebra.scala:156-177`). The general GEMM path streams over `(M,N)`, enqueues the `K` reduction into a FIFO of depth 2, then dequeues it in a second `Pipe` to apply `alpha`, `beta`, `getC`, and `storeY` (`src/spatial/lib/LinearAlgebra.scala:178-196`). The `gemm_fpga_fix` variant uses `MemReduce(Y)` when `sumY` is true and direct `Foreach` writes otherwise (`src/spatial/lib/LinearAlgebra.scala:208-257`).

In `spatial.math.LinearAlgebra`, `transpose` accepts only `Seq(0,1)` and `Seq(1,0)` and throws for other 2D permutations (`src/spatial/math/LinearAlgebra.scala:8-25`). Its `gemm` computes `M`, `P`, and `N`, chooses `MP` and `NP` from optional parameters or defaults, fixes output tile sizes `MT` and `NT` to 16, and calls `Blackbox.GEMM(Y,A,B,C,alpha,beta,i,j,P,MT,NT)` for each output tile (`src/spatial/math/LinearAlgebra.scala:27-60`).

## HLS notes

The Rust+HLS rewrite should preserve the DSL-level call surface, but the implementation should not copy every Scala detail literally. The BLAS `Gemm` tile-and-accumulate skeleton maps naturally to a generated HLS triple-tile loop with local arrays and pipelined inner products (`src/spatial/lib/BLAS.scala:69-99`). The `LinearAlgebra.gemm_generalized` stream/FIFO split is a staging workaround around reductions and output scaling, so an HLS implementation can express the same data dependence as a pipelined dot-product followed by one scaled write (`src/spatial/lib/LinearAlgebra.scala:188-196`). The `Blackbox.GEMM` path is an explicit blackbox handoff today, so the HLS port needs a policy choice: keep GEMM as a named external kernel or generate C++ for the tile loop (`src/spatial/math/LinearAlgebra.scala:47-52`).

## Open questions

- Q-lib-01: Should the Rust+HLS surface preserve current BLAS signatures whose `inc*`, `lda`/`ldb`/`ldc`, `alpha`, or `beta` parameters are accepted but unused in some bodies, or should the new implementation honor BLAS semantics exactly (`src/spatial/lib/BLAS.scala:10-23`, `src/spatial/lib/BLAS.scala:61-99`, `src/spatial/lib/BLAS.scala:104-170`)?
- Q-lib-02: Should `spatial.math.LinearAlgebra.gemm` remain a `Blackbox.GEMM` staging API, or should it lower into the same generated tile-and-accumulate implementation as the library GEMM (`src/spatial/math/LinearAlgebra.scala:47-52`)?
