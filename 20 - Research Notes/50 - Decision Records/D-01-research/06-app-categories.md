---
type: research
decision: D-01
angle: 6
---

## App categories

The actual application surface is mostly under `test/spatial/tests`; `apps/src/HelloSpatial.scala` and `apps/src/TextFileIO.scala` are tutorial/file-I/O examples rather than math-heavy kernels. The major categories I found are:

- Dense linear algebra / BLAS: `src/spatial/lib/BLAS.scala`, `src/spatial/lib/LinearAlgebra.scala`, `test/spatial/tests/feature/dense/BasicBLAS.scala`, `GEMMLibTest.scala`, `DotProduct.scala`, `TRSM.scala`, and MachSuite GEMM sections. `regressions/pir.list` explicitly includes DotProduct, BlackScholes, GDA, LogReg, and GEMV.
- ML and statistical inference/training: `src/spatial/lib/ML.scala`, `src/spatial/lib/LowPrecision.scala`, `test/spatial/tests/feature/dense/LogReg.scala`, `test/spatial/tests/apps/Inference.scala`, and Rosetta `SpamFiltering.scala` / `BNN.scala`.
- FFT / DSP: MachSuite `FFT_Strided` and `FFT_Transpose` in `test/spatial/tests/apps/MachSuite.scala`, plus `feature/math/FunctionApproximations.scala`.
- Image, stencil, and CNN convolution: `feature/dense/Sobel.scala`, `Convolution_FPGA.scala`, `apps/Inference.scala`, and library `conv2d`, pooling, and batchNorm in `LinearAlgebra.scala`.
- Sparse graph, sparse matrix, and scatter-gather: `feature/sparse/PageRank.scala`, `SparseMatrixCOO.scala`, MachSuite `SPMV_CRS` / `SPMV_ELL`, and transfer tests such as `ScatterGatherSRAM.scala`.
- Scientific / finance simulation: `feature/dense/BlackScholes.scala`, MachSuite MD kernels, and `feature/dense/Gibbs_Ising2D.scala`.
- Sorting / scan / histogram: `src/spatial/lib/Sort.scala`, `feature/dense/MergeSort.scala`, and MachSuite `Sort_Merge` / `Sort_Radix`.

## Math-op dependence per category

Dense linear algebra directly needs `fmul` and `fadd` for reductions (`BLAS.Dot`, `Gemm`, `Gemv`, `LinearAlgebra.gemm`). `ffma` is inferred where multiply-add forms could be fused; it is not usually named directly, although the math tests include an `fffma_out` expression. `TRSM.scala` directly adds `fdiv` for triangular solves.

ML/CNN workloads need `fmul`, `fadd`, `fsub`, and often inferred `ffma` for dot products and dense layers. `ML.denselayer_backward` uses division by batch size; `ML.polynomial_kernel` uses `pow`; `LogReg.scala` directly calls `sigmoid`; `SigmoidFloat.scala` implements sigmoid as `1 / (1 + exp(-x))`; `LowPrecision.scala` uses `abs`, `max`, and `fdiv`; `LinearAlgebra.batchNorm2d` uses `pow`, `sqrt`, `fdiv`, `fmul`, and `fadd`.

FFT/DSP needs complex add/sub/multiply. `FFT_Strided` loads twiddle factors and then uses `fmul`, `fadd`, and `fsub`; `FFT_Transpose` computes twiddles in the accelerator with `sin_taylor` and `cos_taylor`, plus phase-scaling division.

Image/stencil kernels mostly need `fmul`, `fadd`, `fsub`, `fabs`, and `fmax`: Sobel and convolution tests use multiply-reduce plus `abs(horz)+abs(vert)`, while CNN ReLU uses `max`. True Sobel magnitude via `sqrt(horz**2 + vert**2)` is only noted in comments, so `fsqrt` for that path is inferred; batchNorm’s `sqrt` is directly observed in the library.

Sparse/graph kernels need `fmul`/`fadd` for SpMV and COO sparse-dense multiply, and `fdiv` for PageRank rank normalization. Scatter-gather tests are memory-routing workloads, not BigIP math users.

Scientific/finance needs the broadest set: Black-Scholes uses `abs`, `exp_taylor`, `log_taylor`, `sqrt_approx`, `fdiv`, and polynomial multiply/add; MachSuite MD uses `fdiv`, repeated `fmul`, `fadd`, and `fsub`. Gibbs precomputes `exp` tables on the host/staging side, so accelerator `fexp` dependence is not directly observed there.

Sorting/radix sort is mostly integer compare, shift, add, and address logic. A floating-point sort would imply `fcmp`, but the observed MachSuite sort tests are integer.

## Per-category pain

Dense BLAS breaks immediately if `fmul`/`fadd` or reductions over them are rejected; missing `fdiv` blocks TRSM. ML can degrade to fixed-point ReLU-only demos, but LogReg, batchNorm, quantization, and polynomial kernels reject without sigmoid/exp, sqrt, pow, abs/max, and division support or accepted arithmetic fallbacks. FFT_Strided survives with preloaded twiddles if base arithmetic works, but FFT_Transpose rejects if sin/cos Taylor lowering is treated as unsupported. Image convolution survives base arithmetic; batchNorm, average pool, and true gradient magnitude do not. Sparse SpMV survives base arithmetic, but PageRank rejects without division. Sorting should not be penalized by BigIP coverage gaps.

## Implications for D-01

V1 must support the categories already in regression and library surfaces: dense BLAS/GEMM/GEMV, LogReg-style ML, CNN/image convolution, sparse SpMV/PageRank, FFT, and Black-Scholes/MD-style scientific kernels. The mandatory BigIP set is therefore `fadd`, `fsub`, `fmul`, `fdiv`, comparisons, `fabs`, `fmax`, `fsqrt`/reciprocal-sqrt, and multiply-add patterns (`ffma` or unfused `fmul`+`fadd`). `exp`, `log`, `pow`, `sin`, `cos`, `sigmoid`, and `tanh` should either have native support or guaranteed accepted library/Taylor/LUT lowerings; otherwise reject-on-unsupported will exclude visible Spatial app categories rather than just edge cases.
