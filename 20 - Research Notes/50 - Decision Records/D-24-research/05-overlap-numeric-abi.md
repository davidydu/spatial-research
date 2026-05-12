---
type: "research"
decision: "D-24"
angle: 5
topic: "overlap-numeric-abi"
---

# D-24 Angle 5: Overlap With Numeric Decisions And ABI Manifest

## 1. Scope Boundary

D-24 should be a host-boundary fixed-point conversion decision, not a new numeric semantics umbrella. The immediate source split is that Cppgen maps fractional `FixPtType` host values to `double`, while `toTrueFix` and transport paths multiply by `1 << f` into an integer storage type, and `toApproxFix` divides that raw integer back to an approximate host value (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:36-100`). Scalar registers repeat the split: `SetReg` shifts fractional fixed values before `setArg`, while `GetReg` sign-extends the raw value and divides by `1 << f` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`). DRAM copies rawify fractional fixed vectors for widths at least 8 and reject fractional subbyte payloads (`CppGenInterface.scala:85-131`). D-24 therefore decides how Rust host bindings turn host-visible values into raw fixed bits and back.

## 2. Composition With D-17

[[D-17]] owns the meaning of `Unbiased`: seeded stable stochastic rounding, four guard bits, legacy negative threshold behavior, seed/event provenance, and declared backend fallbacks. D-24 composes before and after those events. A host input conversion chooses the raw scaled integer that enters the simulator or HLS kernel; D-17 then decides how `*&`, `/&`, `FixToFixUnb`, and saturating variants round inside execution. A host output conversion chooses how the final raw fixed value is reported to the host. D-24 should not decide stochastic seeds, guard-bit counts, event identities, or whether unbiased rounding becomes deterministic. It should require that host conversion provenance be visible next to D-17 rounding provenance so a mismatch can distinguish "different input bits" from "different stochastic event."

## 3. Composition With D-18 And D-19

[[D-18]] is the float-packing decision. D-24 should not redefine `FloatPoint.clamp`, custom float bit layouts, NaN/inf/zero canonicalization, or native float fallbacks. It may only say how fixed values at the host boundary are represented when a host API accepts decimal-like values. Fixed-to-float and float-to-fixed arithmetic casts inside the program remain governed by the numeric operation policy and, for custom floats, by D-18.

[[D-19]] decides how many arithmetic rounding or reclamp events an FMA-shaped program has. Under `scalagen_unfused_two_round_v1`, fixed `FixFMA` behaves like multiply, clamp/truncate, add, then clamp/truncate; Scalagen emits `($m1 * $m2) + $add`, and `FixedPoint.*` shifts by `fmt.fbits` before `FixedPoint.clamped` while `FixedPoint.+` clamps again (`ScalaGenFixPt.scala:150`; `/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:14-17`). D-24 only supplies initial raw bits and decodes final raw bits. It should not choose fused versus unfused FMA, contraction controls, or the count of internal fixed-point rounding points.

## 4. ABI Manifest Contract

[[D-23]] should carry D-24 as data. Its `numeric_formats` and ABI entries need logical fixed format, storage bits, signedness, fractional bits, host representation, transport representation, sign-extension rule, subbyte packing rule, and a required `conversion_policy`. The D-23 overlap note already proposes labels such as `cppgen_fractional_double_shift_v1`, `bit_exact_scaled_integer_v1`, `raw_memcpy_v1`, `packed_subbyte_lsb0_v1`, and `unsupported_fractional_subbyte_v1` ([[D-23-research/04-fixed-point-d24-overlap]]; [[D-23-research/06-abi-manifest-schema]]). D-24 chooses which fixed-point labels mean what, and which one is the Rust default. D-23 decides where those labels appear: scalar args, ArgIO/ArgOut readback, DRAMs, streams, host files, structs, vectors, and diagnostics.

## 5. What D-24 Should Decide

D-24 should define the Rust host fixed-point policy enum and exact conversion algorithms. For a Cppgen-compatible mode, it should specify decimal or binary floating parsing, multiplication by `2^f`, C/C++ cast compatibility, overflow behavior, signed extension on readback, and which Cppgen approximations are intentionally preserved. For a bit-exact mode, it should specify scaled-integer inputs, exact decimal parsing if accepted, wrap versus reject behavior on out-of-range host values, readback formatting, and fixture generation. It should also define diagnostics for lossy host values, subbyte fractional rejection, manifest mismatch, and comparison of raw bits versus host approximations.

D-24 should not decide ABI ordering, stream/file lifecycle, custom float packing, unbiased rounding, FMA fusion, or HLS target capability fallback names beyond fixed host conversion. Its clean output is a versioned fixed conversion contract that the [[D-23]] manifest records and that [[D-17]], [[D-18]], and [[D-19]] can consume without losing their own authority.
