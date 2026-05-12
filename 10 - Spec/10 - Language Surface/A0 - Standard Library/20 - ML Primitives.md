---
type: spec
concept: standard-library-ml-primitives
source_files:
  - "src/spatial/lib/ML.scala:11-304"
  - "src/spatial/lib/HostML.scala:6-187"
  - "src/spatial/lib/LowPrecision.scala:6-329"
source_notes:
  - "[[open-questions-stdlib]]"
hls_status: rework
depends_on:
  - "[[10 - BLAS and Linear Algebra]]"
  - "[[50 - Math and Helpers]]"
status: draft
---

# ML Primitives

## Summary

`object ML` is a staged machine-learning helper library layered on top of reductions, SRAM/LUT reads, and dense-layer templates, and it extends `HostML` so the same object also exposes unstaged Scala reference functions (`src/spatial/lib/ML.scala:11-12`, `src/spatial/lib/HostML.scala:6-187`). The primary staged building blocks are `dp_flat`, `dp_tiled`, `sum_flat`, `sum_tiled`, `mlp_forward`, and `denselayer` (`src/spatial/lib/ML.scala:21-187`). `HostML` mirrors the dot product and dense-layer behavior with Scala collections for reference testing, including `unstaged_dp`, `unstaged_denselayer`, and `unstaged_mlp` (`src/spatial/lib/HostML.scala:8-32`, `src/spatial/lib/HostML.scala:80-98`). `LowPrecision` adds conversion, quantization, low-precision matrix multiply, low-precision add, and dequantization helpers for SRAM/DRAM data (`src/spatial/lib/LowPrecision.scala:8-146`, `src/spatial/lib/LowPrecision.scala:196-234`). This entry is `hls_status: rework` because the algorithms are suitable for HLS, but tile sizes, unroll factors, scale handling, and rounding policy need an explicit HLS contract (`src/spatial/lib/ML.scala:60-76`, `src/spatial/lib/ML.scala:153-187`, `src/spatial/lib/LowPrecision.scala:29-43`).

## API

`dp_flat[T:Num](N, ip)(input)` maps each index to a pair `(a,b)`, multiplies the pair, and delegates the reduction to `sum_flat` (`src/spatial/lib/ML.scala:21-26`). `dp_tiled[T:Num](N, ts, op, ip)(input)` does the same product mapping but delegates to `sum_tiled` (`src/spatial/lib/ML.scala:37-44`). `sum_flat` returns `input(0)` for `N == 1`; otherwise it allocates a `Reg[T]`, runs a named `'DP_Tiled.Reduce` with parallelism `Math.min(ip,N)`, and returns `sum.value` (`src/spatial/lib/ML.scala:46-57`). `sum_tiled` calls `sum_flat` for a tile, uses the direct inner path when `N <= ts`, and otherwise reduces tile sums through a named `'Sum_Tiled.Reduce` into a register explicitly named `SumValue` (`src/spatial/lib/ML.scala:60-76`).

`mlp_forward` accepts sequences of 2D weights and 1D biases, an activation function, an input accessor, an output updater, and per-layer `ips`, `mps`, and `ops` defaults (`src/spatial/lib/ML.scala:90-100`). It derives layer dimensions from weight and bias constant dimensions, allocates hidden SRAMs for intermediate layers, selects input/output functions for each adjacent layer pair, uses `identity` for the last layer and `relu` for hidden layers, asserts unroll bounds, and calls `denselayer` for each layer (`src/spatial/lib/ML.scala:101-135`). `denselayer` reads weight dimensions `I` and `O`, computes each output as `dp_tiled` over `in(i) * w(i,o)`, adds `b(o)`, emits both linear and activated outputs through callbacks, returns `Some(value)` for `O == 1`, and otherwise launches an output-parallel `'Denselayer.Foreach` and returns `None` (`src/spatial/lib/ML.scala:153-187`).

`HostML.unstaged_dp` zips two Scala sequences, multiplies pairs, and reduces by addition (`src/spatial/lib/HostML.scala:8-12`). `HostML.unstaged_denselayer` transposes weights, computes `dot + bias` for each output, maps the activation, and returns `(nlout, lout)` (`src/spatial/lib/HostML.scala:14-32`). `LowPrecision.ConvertTo8Bit` writes bytes to DRAM, writes a scale factor to `SF`, and reads float weights from DRAM in `size` chunks (`src/spatial/lib/LowPrecision.scala:8-14`). `LowPrecision.quantize` has separate 2D and 1D SRAM overloads with a `parent` label, output `Y`, scale register `SF`, float input `X`, `factor`, and `precision` (`src/spatial/lib/LowPrecision.scala:47-107`).

## Algorithm

The staged dot-product algorithm is intentionally factored: `dp_*` only builds the elementwise product, while `sum_*` defines the reduction schedule (`src/spatial/lib/ML.scala:21-44`). `sum_tiled` performs a two-level reduction when `N > ts`: inner tile sums call `sum_flat(ts, ip)`, and the outer named reduce iterates `N by ts` with parallelism `Math.min(N/ts, op)` (`src/spatial/lib/ML.scala:66-75`). Dense layers reuse that schedule directly; `InnerNN(o)` computes a dot over input dimension `I` with tile size `ip`, outer reduction parallelism `mp`, and inner reduction parallelism `ip`, then applies bias, linear-output callback, activation, and nonlinear-output callback (`src/spatial/lib/ML.scala:169-177`). Multi-output layers parallelize across `O par op`; single-output layers return the computed value to the caller instead of staging the output loop (`src/spatial/lib/ML.scala:179-185`).

`LowPrecision.ConvertTo8Bit` first reduces over DRAM chunks to find the maximum absolute input, computes `delta = 2 * maxo / 127`, converts each float chunk to byte by dividing by `delta`, stores each byte chunk, and finally writes `SF := delta` (`src/spatial/lib/LowPrecision.scala:16-43`). The 2D `quantize` overload computes signed saturation bounds from `precision` and `factor`, reduces absolute max over all matrix elements, computes `delta`, converts each element to `Int`, clamps to `[sat_neg, sat_pos]` with nested `mux`, and writes `SF := delta.value` (`src/spatial/lib/LowPrecision.scala:56-76`). The 1D overload performs the same saturation, max, delta, clamp, and scale write over vector length (`src/spatial/lib/LowPrecision.scala:88-107`). `mmlp` multiplies low-precision matrices by converting inputs to output type during the reduction, writes transposed or normal output, and sets output scale to `ASF.value * BSF.value` (`src/spatial/lib/LowPrecision.scala:110-146`). `dequant` reconstructs floats by multiplying quantized elements by `SF.value` (`src/spatial/lib/LowPrecision.scala:224-234`).

## HLS notes

The HLS rewrite should keep the staged API shape but turn schedule arguments into explicit tile, unroll, and pipeline pragmas. `sum_flat` and `sum_tiled` already expose inner parallelism, tile size, and outer parallelism, but they encode the schedule through Spatial `Reduce` names rather than through an HLS pragma vocabulary (`src/spatial/lib/ML.scala:46-76`). `denselayer` is a natural HLS kernel: one output lane owns a tiled dot product, bias add, activation, and writeback (`src/spatial/lib/ML.scala:169-185`). Low-precision code needs rework because the source comments say statistical rounding is not implemented in `ConvertTo8Bit`, and `ConvertTo8Bit_Buggy` documents a hardware issue where `SF` becomes zero and outputs become infinity (`src/spatial/lib/LowPrecision.scala:29-30`, `src/spatial/lib/LowPrecision.scala:236-267`).

## Open questions

- Q-lib-03: Should `sum_flat`, `sum_tiled`, and `denselayer` expose a stable HLS scheduling schema, or should the Rust port keep the current positional `ip`/`mp`/`op` argument convention (`src/spatial/lib/ML.scala:46-76`, `src/spatial/lib/ML.scala:153-187`)?
- Q-lib-04: What rounding, saturation, and zero-scale semantics should low-precision conversion guarantee when the source currently uses truncating casts and comments that statistical rounding is missing (`src/spatial/lib/LowPrecision.scala:29-43`, `src/spatial/lib/LowPrecision.scala:56-76`)?
- Q-lib-05: Are `HostML` references intended to be normative golden models for all staged ML helpers, or only convenient test utilities for the functions they mirror directly (`src/spatial/lib/HostML.scala:8-32`, `src/spatial/lib/HostML.scala:80-98`)?
