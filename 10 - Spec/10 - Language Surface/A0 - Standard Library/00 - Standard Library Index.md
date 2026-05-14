---
type: spec
concept: standard-library-index
aliases:
  - "A0 - Standard Library"
source_files:
  - "src/spatial/lib/BLAS.scala:8-210"
  - "src/spatial/lib/LinearAlgebra.scala:7-257"
  - "src/spatial/math/LinearAlgebra.scala:8-60"
  - "src/spatial/lib/ML.scala:11-304"
  - "src/spatial/lib/HostML.scala:6-187"
  - "src/spatial/lib/LowPrecision.scala:6-329"
  - "src/spatial/lib/Sort.scala:6-137"
  - "src/spatial/lib/Scan.scala:6-40"
  - "src/spatial/lib/MetaProgramming.scala:9-120"
source_notes:
  - "[[open-questions-stdlib]]"
hls_status: rework
depends_on:
  - "[[20 - Memories]]"
  - "[[50 - Math and Helpers]]"
status: draft
---

# Standard Library Index

## Summary

This subsection documents the user-callable templates under `src/spatial/lib/*` plus the staging companion in `src/spatial/math/LinearAlgebra.scala`. The library is a mixed surface: BLAS exposes DRAM-oriented `Dot`, `Axpy`, `Gemm`, `Gemv`, `Ger`, `Scal`, and `Axpby` templates in one object (`src/spatial/lib/BLAS.scala:8-210`); `spatial.lib.LinearAlgebra` exposes on-chip `matmult`, overloaded `gemm`, `gemm_fpga_fix`, and small NN helpers in one trait (`src/spatial/lib/LinearAlgebra.scala:7-257`); `spatial.math.LinearAlgebra` exposes lower-level `transpose` and `gemm` staging helpers, with the latter issuing `Blackbox.GEMM` tiles (`src/spatial/math/LinearAlgebra.scala:8-60`). ML primitives are split between staged kernels in `ML`, unstaged Scala references in `HostML`, and quantized arithmetic in `LowPrecision` (`src/spatial/lib/ML.scala:11-304`, `src/spatial/lib/HostML.scala:6-187`, `src/spatial/lib/LowPrecision.scala:6-329`). Sort, scan, and meta-programming are smaller library layers around `MergeBuffer`, FIFO compaction, and accessor-enable rewriting (`src/spatial/lib/Sort.scala:10-135`, `src/spatial/lib/Scan.scala:8-38`, `src/spatial/lib/MetaProgramming.scala:14-42`).

The entries are grouped by the implementation pattern a Rust+HLS rewrite must preserve. BLAS and ML are arithmetic templates whose observable result depends on loop tiling, reductions, and local buffering (`src/spatial/lib/BLAS.scala:15-30`, `src/spatial/lib/BLAS.scala:69-99`, `src/spatial/lib/ML.scala:46-76`). Sort and scan are data-movement templates over merge buffers and FIFOs (`src/spatial/lib/Sort.scala:23-47`, `src/spatial/lib/Scan.scala:27-37`). Meta programming is an elaboration-time helper whose visible behavior is enable propagation on FIFO/SRAM accessors (`src/spatial/lib/MetaProgramming.scala:26-40`).

## API

- [[00 - Standard Library Index]] - this MOC for the five-note standard-library subsection.
- [[10 - BLAS and Linear Algebra]] - BLAS DRAM kernels, on-chip matrix multiply, scalar/vector/matrix `C` broadcast for `gemm`, and the `Blackbox.GEMM` staging path (`src/spatial/lib/BLAS.scala:61-102`, `src/spatial/lib/LinearAlgebra.scala:37-206`, `src/spatial/math/LinearAlgebra.scala:27-60`).
- [[20 - ML Primitives]] - staged dot/sum/dense-layer helpers, host-side reference implementations, and low-precision quantization/dequantization helpers (`src/spatial/lib/ML.scala:21-187`, `src/spatial/lib/HostML.scala:8-32`, `src/spatial/lib/LowPrecision.scala:8-107`).
- [[30 - Sort and Scan]] - merge-sort templates over SRAM and DRAM plus predicate-to-mask and FIFO-compacting scans (`src/spatial/lib/Sort.scala:10-135`, `src/spatial/lib/Scan.scala:8-38`).
- [[40 - Meta Programming]] - `withEns`, `MForeach`, `MReduce`, lane-aware loops, and a duplicate-FIFO helper that relies on an `IR.rewrites.addGlobal` accessor rewrite (`src/spatial/lib/MetaProgramming.scala:14-120`).

## Algorithm

The library entries should be read as templates that app code calls directly, not as compiler passes. BLAS templates allocate fixed-size SRAM tiles, load DRAM slices into those tiles, run nested `Foreach`/`Reduce` or `MemReduce` controllers, and store the result back to DRAM (`src/spatial/lib/BLAS.scala:15-30`, `src/spatial/lib/BLAS.scala:41-57`, `src/spatial/lib/BLAS.scala:69-99`). On-chip matrix helpers use SRAM dimensions and transpose flags to select indices, then write the output SRAM either normally or transposed (`src/spatial/lib/LinearAlgebra.scala:20-34`, `src/spatial/lib/LinearAlgebra.scala:123-142`). ML templates factor dot products through `sum_flat`/`sum_tiled`, use explicit named reductions, and stage dense layers as output-parallel dot-plus-bias-plus-activation computations (`src/spatial/lib/ML.scala:21-77`, `src/spatial/lib/ML.scala:153-187`). Sort uses `MergeBuffer` to merge fixed-size SRAM blocks and then alternates DRAM source/destination streams with a `doubleBuf` register (`src/spatial/lib/Sort.scala:23-60`, `src/spatial/lib/Sort.scala:92-132`). Scan either writes a `1`/`0` predicate mask or enqueues matching values into a FIFO before writing the compacted prefix (`src/spatial/lib/Scan.scala:14-17`, `src/spatial/lib/Scan.scala:27-37`). Meta programming changes staging behavior by pushing enable bits into `_ens` and globally rewriting FIFO/SRAM accessors to append those enable bits (`src/spatial/lib/MetaProgramming.scala:14-42`).

## HLS notes

Overall `hls_status: rework` because the folder mixes clean templates with kernels that should become HLS-specific tiled primitives. Sort, scan, and the meta-programming loop helpers are structurally direct HLS translations because their source is already expressed with finite controllers, SRAM/FIFO buffers, and simple enable logic (`src/spatial/lib/Sort.scala:29-55`, `src/spatial/lib/Scan.scala:29-37`, `src/spatial/lib/MetaProgramming.scala:47-75`). BLAS and ML need rework because their fixed tile sizes and pipeline shapes are embedded as Scala constants and `par` parameters rather than as an HLS scheduling contract (`src/spatial/lib/BLAS.scala:15-25`, `src/spatial/lib/BLAS.scala:69-99`, `src/spatial/lib/ML.scala:60-76`, `src/spatial/lib/ML.scala:169-187`). `spatial.math.LinearAlgebra.gemm` already delegates to `Blackbox.GEMM`, so the Rust+HLS rewrite needs to decide whether that remains a blackbox or becomes generated C++ with tile and pipeline pragmas (`src/spatial/math/LinearAlgebra.scala:47-52`).

## Open questions

See [[open-questions-stdlib]] Q-lib-01 through Q-lib-09. The highest-priority questions are the BLAS scalar/stride parameters that are accepted but not consumed by several current bodies (`src/spatial/lib/BLAS.scala:61-99`, `src/spatial/lib/BLAS.scala:105-139`, `src/spatial/lib/BLAS.scala:142-170`), the `Blackbox.GEMM` versus portable-HLS policy (`src/spatial/math/LinearAlgebra.scala:50-52`), the quantization rounding/zero-scale behavior (`src/spatial/lib/LowPrecision.scala:29-43`, `src/spatial/lib/LowPrecision.scala:236-267`), and the global-mutable rewrite contract in `MetaProgramming.rewrites` (`src/spatial/lib/MetaProgramming.scala:22-42`).
