---
type: "research"
decision: "D-18"
angle: 10
---

# Recommendation Matrix

## Decision Frame

[[D-18]] asks whether the Rust/HLS rewrite should reproduce `FloatPoint.clamp` bit-for-bit, including the `x > 1.9` subnormal guard, or adopt a cleaner custom-float algorithm with accepted divergence (`20 - Research Notes/40 - Decision Queue.md:79-81`). The source behavior is not isolated to formatting. `FloatPoint.clamped` calls `clamp` for every finite `Value`, and ordinary float operators reclamp finite results after arithmetic (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:153-165`, `/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:417-433`). Packing also calls the same routine through `Value.bits`, so `DataAsBits`/`BitsAsData` compatibility depends on it (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:120-126`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenBits.scala:47-55`).

## Option Matrix

| Option | Strength | Problem | D-18 disposition |
|---|---|---|---|
| Bit-for-bit legacy clamp | Matches Scalagen/emul, current spec language, constants, arithmetic reclamping, and packed bit views. | Copies magic `x > 1.9`, approximate log decomposition, one-guard-bit rounding, and other compatibility debt. | Recommend as default/reference policy. |
| Cleaner canonical custom float | Easier to explain: exact normalization, explicit rounding, principled subnormal/overflow boundaries. | Changes existing reference behavior and can silently break bit tests, casts, and memory bit layouts. | Keep as explicit experimental/future policy. |
| Dual-mode legacy plus clean | Supports replay now and semantic cleanup later. | Requires provenance and tests so goldens, simulator, and HLS do not compare across modes accidentally. | Recommend as structure, with legacy as default. |
| HLS/native approximation | Cheap for generated C++/HLS and aligned with existing divergent backends. | Cppgen and Chisel/Fringe already diverge from `FloatPoint.clamp`; native behavior is not Scalagen parity. | Allow only as declared non-reference backend behavior. |

## Recommendation

Adopt **Legacy Clamp as the canonical reference policy**, with a named mode such as:

`float_pack_policy = scalagen_legacy_clamp_v1`

Rust reference simulation should reproduce `FloatPoint.clamp` exactly enough for bit-for-bit parity, including the `x > 1.9` guard, `x >= 2` repair, cutoff repair, overflow-to-infinity, normal and subnormal packing, one-discarded-bit rounding, signed-zero underflow, NaN/infinity/zero encodings, and `convertBackToValue` canonicalization (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:318-433`; [[01-source-algorithm-call-surface]]). The ugly rule should be quarantined by name, not cleaned away silently.

This recommendation follows the spec hierarchy. [[20 - Numeric Reference Semantics]] and [[50 - Data Types]] already treat Scalagen/emul as the reference when native hardware or JVM intuitions disagree, and they explicitly warn that custom floating formats cannot be delegated to native `f32`/`f64` if bit parity is required. [[03-tests-apps-usage]] also shows the current test suite does not protect clamp boundaries directly, so a clean replacement would look safe until exact bit fixtures are added.

## Rejected Alternatives

Reject **cleaner custom float as the immediate default**. It is the right long-term engineering direction if the project wants a principled numeric spec, but it is a semantic migration. D-18 should not hide that migration inside a Rust rewrite. Keep it as `clean_custom_float_vNext` or similar, with tests that intentionally show how it diverges from `scalagen_legacy_clamp_v1`.

Reject **HLS/native approximation as reference parity**. Cppgen maps custom `FltPtType` values to native `float` and plain C casts, while Chisel/Fringe delegate runtime float arithmetic and conversions to BigIP/HardFloat-style hooks rather than the Scala clamp algorithm (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenCommon.scala:75-93`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenMath.scala:136-138`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:51-65`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/chiselgen/ChiselGenMath.scala:92-102`; [[05-backend-codegen-variation]]). Those are backend policies, not the Rust reference contract.

Allow **dual mode** only with provenance. Every simulator run, golden file, mismatch report, and HLS artifact that handles custom floats should record `float_pack_policy`, `rounding_algorithm`, backend capability, and fallback. Without that, dual mode creates exactly the silent-divergence risk D-18 is meant to remove.
