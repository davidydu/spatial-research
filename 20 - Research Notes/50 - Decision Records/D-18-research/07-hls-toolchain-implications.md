---
type: "research"
decision: "D-18"
angle: 7
---

# HLS Toolchain Implications for FloatPoint.clamp

## 1. Boundary to preserve

D-18 is not a generic "can HLS do floats?" question. The queue asks whether Rust float packing reproduces the `FloatPoint.clamp` `x > 1.9` heuristic bit-for-bit or adopts a cleaner custom-float algorithm with accepted divergence (`20 - Research Notes/40 - Decision Queue.md:79-81`). In current Scalagen semantics, `FltFormat` defines the custom width contract, including `sbits`, `ebits`, `bias`, `MIN_E`, `MAX_E`, and `SUB_E` (`emul/src/emul/FltFormat.scala:3-8`). `FloatPoint.bits` calls `clamp`, then emits mantissa bits, exponent bits, and sign (`emul/src/emul/FloatPoint.scala:120-126`), while arithmetic operators reclamp every finite result through `FloatPoint.clamped` (`emul/src/emul/FloatPoint.scala:153-165`, `emul/src/emul/FloatPoint.scala:417-433`). Therefore bit parity covers constants, casts, arithmetic results, and bit reinterpretation, not just file I/O. See [[20 - Numeric Reference Semantics]] and [[D-18-research/01-source-algorithm-call-surface]].

## 2. What native libraries can cover

Existing Chisel/Fringe already separates the packed float wire type from the arithmetic implementation. `fringe.templates.math.FloatingPoint` stores a raw `UInt`, maps `FltFormat` to `(m = sbits + 1, e = ebits)`, and delegates `+`, `-`, `*`, `/`, comparisons, fixed/float casts, and float/float casts into `Math.*` and then `globals.bigIP` (`fringe/src/fringe/templates/math/FloatingPoint.scala:8-12`, `fringe/src/fringe/templates/math/FloatingPoint.scala:47-83`; `fringe/src/fringe/templates/math/Math.scala:548-678`, `fringe/src/fringe/templates/math/Math.scala:680-700`, `fringe/src/fringe/templates/math/Math.scala:794-798`). Zynq/CXP targets instantiate Xilinx floating-point IP for custom add and conversion widths (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:397-442`, `fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:929-1065`). General HLS claim, unverified: modern HLS libraries can synthesize native `float`/`double`, vendor custom float/fixed types, and float IP for common arithmetic. That is useful for an HLS-native mode, but it does not prove `FloatPoint.clamp` parity.

## 3. Bit-parity contract

For Rust simulation, bit parity requires a compatibility clone of the Scala path: `log2BigDecimal`, `floor`, `BigDecimal` division by powers of two, the `y < SUB_E && x > 1.9` adjustment, `x >= 2`, the cutoff guard, normal/subnormal one-guard-bit rounding, signed-zero underflow, and the inverse `convertBackToValue` round trip (`emul/src/emul/FloatPoint.scala:300-309`, `emul/src/emul/FloatPoint.scala:318-398`, `emul/src/emul/FloatPoint.scala:399-433`). Scalagen bit casts also demand the same pack/unpack surface: `DataAsBits` emits `.bits`, and `BitsAsData` rebuilds with `FloatPoint.fromBits` (`src/spatial/codegen/scalagen/ScalaGenBits.scala:47-55`; `emul/src/emul/FloatPoint.scala:435-458`). The spec is explicit that the Rust simulator needs arbitrary-precision equivalents and bit-for-bit Scalagen matching on numeric op families (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:92-94`), and [[50 - Data Types]] warns that custom floats cannot be delegated to native `f32`/`f64` when bit parity is required (`10 - Spec/20 - Semantics/50 - Data Types.md:64-66`).

## 4. Cost of exact custom packing

In Rust, the exact clone is mostly maintenance cost: a decimal/bigint implementation, fixtures around subnormal boundaries, and tests against Scala-generated bits. In HLS hardware, exact custom packing is a larger toolchain choice. If constants are prepacked by Rust, HLS only carries raw bit patterns. If runtime `FixToFlt`, `FltToFlt`, or custom arithmetic results must match `clamp`, native vendor IP is suspect because current simulation IP hardcodes rounding and tininess choices for HardFloat conversions (`fringe/src/fringe/targets/BigIPSim.scala:125-133`, `fringe/src/fringe/targets/BigIPSim.scala:275-291`), while vendor IP parameters expose their own custom precision behavior (`fringe/src/fringe/targets/zynq/ZynqBlackBoxes.scala:960-1065`). General HLS cost claim, unverified: a custom packer can be pipelined, but it brings leading-one/exponent logic, variable shifts, guard-bit rounding, overflow/subnormal checks, and additional compare/add stages; exact area and II need reports.

## 5. Capability and fallback options

Recommended capability split: `scalagen_parity` clones `FloatPoint.clamp` in Rust, precomputes constants, verifies `.bits`/`fromBits`, and either rejects HLS runtime casts needing exact custom packing or lowers them to a local custom packer. `hls_native` uses HLS/vendor float libraries for arithmetic and conversions, records provenance, and accepts possible bit divergence. `clean_custom` uses the deterministic exact-normalization candidate from [[D-18-research/06-cleaner-algorithm-candidates]] for a new portable reference, not legacy parity. A hybrid can use native HLS arithmetic plus parity packing at host/test boundaries, but it must be labelled as a fallback because [[30 - HLS Mapping/20 - Needs Rework]] says reference semantics still need Rust tests, models, or HLS-compatible runtime code (`30 - HLS Mapping/20 - Needs Rework.md:57-62`).
