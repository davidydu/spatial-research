---
type: open-questions
topic: stdlib
session: 2026-04-25
date_started: 2026-04-25
---

# Open Questions - Standard Library Session

Questions raised while documenting Spatial standard-library templates under `src/spatial/lib/*` and the companion `src/spatial/math/LinearAlgebra.scala`.

## Q-lib-01 - BLAS parameter contract for unused stride/scalar/leading-dimension arguments

Several BLAS signatures accept classic BLAS parameters, but the current bodies do not use all of them. `Dot` accepts `incX` and `incY` while loading contiguous slices from `X` and `Y`; `Gemm` accepts `alpha`, `beta`, `lda`, `ldb`, and `ldc` while computing and storing only accumulated products; `Gemv` accepts `alpha` and `beta` while storing the unscaled matrix-vector reduction; `Ger` accepts `alpha` while storing the unscaled outer product.

Spec question: Should the Rust+HLS surface preserve the current Spatial template behavior exactly, or should these APIs be upgraded to full BLAS semantics?

Source: `src/spatial/lib/BLAS.scala:10-23`, `src/spatial/lib/BLAS.scala:61-99`, `src/spatial/lib/BLAS.scala:104-139`, `src/spatial/lib/BLAS.scala:142-170`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-02 - GEMM blackbox versus generated HLS kernel

`spatial.math.LinearAlgebra.gemm` fixes `MT` and `NT` to 16 and stages `Blackbox.GEMM` for each output tile, while `src/spatial/lib/BLAS.scala` contains an explicit tiled `MemReduce` GEMM pattern.

Spec question: Should the HLS rewrite keep a named external GEMM blackbox, generate C++ for the tile loop, or support both with a policy knob?

Source: `src/spatial/math/LinearAlgebra.scala:47-52`, `src/spatial/lib/BLAS.scala:69-99`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-03 - Stable HLS scheduling schema for ML reductions

`sum_flat`, `sum_tiled`, and `denselayer` expose schedule choices as positional arguments such as `ip`, `ts`, `op`, and `mp`, and then encode the schedule through named Spatial reductions and `Foreach` controllers.

Spec question: Should the port preserve those arguments literally, or introduce a structured HLS schedule object with tile, unroll, and pipeline fields?

Source: `src/spatial/lib/ML.scala:46-76`, `src/spatial/lib/ML.scala:153-187`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-04 - Low-precision rounding, saturation, and zero-scale behavior

`ConvertTo8Bit` computes `delta = 2 * maxo / 127` and casts `sram_in(jj) / delta` to `Byte`; a comment states that statistical rounding is not implemented. `ConvertTo8Bit_Buggy` comments that `SF` becomes zero and output SRAMs become infinity due to a hardware control issue.

Spec question: What exact rounding and zero-scale semantics should the HLS low-precision library guarantee?

Source: `src/spatial/lib/LowPrecision.scala:29-43`, `src/spatial/lib/LowPrecision.scala:236-267`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-05 - Normative status of HostML reference functions

`ML` extends `HostML`, and `HostML` provides unstaged references for dot product, dense layer, MLP, loss, activations, kernels, and SVM inference.

Spec question: Are the `HostML` implementations normative golden models for corresponding staged kernels, or are they only convenience test utilities?

Source: `src/spatial/lib/ML.scala:11-12`, `src/spatial/lib/HostML.scala:8-32`, `src/spatial/lib/HostML.scala:80-187`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-06 - Final destination contract for DRAM mergeSort

The DRAM `mergeSort` pre-sorts chunks back into `src`, then alternates merge-pass reads and writes between `src` and `dst` under `doubleBuf`.

Spec question: Should the public contract state that the final sorted data may reside in either `src` or `dst` depending on pass parity, or should the implementation guarantee that `dst` contains the final result?

Source: `src/spatial/lib/Sort.scala:71-81`, `src/spatial/lib/Sort.scala:101-132`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-07 - Domain restrictions for sort sizes and merge factors

The sort implementation derives `levelCount` with a logarithm and divides `mergeCount` by `ways` after each level. The source does not show tail handling for non-exact merge levels.

Spec question: Should `numel`, `ways`, and `mergePar` be constrained to exact powers/factors, or should the HLS rewrite add explicit tail handling?

Source: `src/spatial/lib/Sort.scala:16-21`, `src/spatial/lib/Sort.scala:86-90`, `src/spatial/lib/Sort.scala:127-132`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-08 - Exception safety of withEns scope restoration

`withEns` appends enable bits, evaluates a by-name block, removes those bits, and returns the result. The implementation does not show a `try/finally` restoration guard.

Spec question: Should exception-safe restoration be part of the DSL contract, or are staging-time exceptions outside the supported `withEns` semantics?

Source: `src/spatial/lib/MetaProgramming.scala:14-20`.
Blocked by: -
Status: open
Resolution: (empty)

## Q-lib-09 - Accessor coverage for EnableRewrite

`EnableRewrite` handles FIFO enqueue, FIFO dequeue, SRAM read, and SRAM write, after skipping accessors that already contain the current enables. The source does not show equivalent rewrites for other memory/accessor families.

Spec question: Should the Rust+HLS frontend keep this FIFO/SRAM-only contract, or define a broader accessor-enable rule?

Source: `src/spatial/lib/MetaProgramming.scala:26-40`.
Blocked by: -
Status: open
Resolution: (empty)
