---
type: "research"
decision: "D-24"
angle: 8
topic: "policy-options-contract"
---

# D-24 Angle 8: Policy Options And Conversion Contract

## 1. Policy Names And Claims

Use four versioned policy labels. `cppgen_fractional_double_shift_v1` claims legacy Cppgen host-source compatibility only: fractional `FixPtType` is a host `double`, but transport is `toTrueFix(x) = raw(x * (1 << f))`, and readback is `toApproxFix(raw) = double(raw)/(1 << f)` (`src/spatial/codegen/cppgen/CppGenCommon.scala:36-49`, `:75-89`; `src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`). It does not claim raw-bit reproducibility for values that `double` cannot represent. `bit_exact_scaled_integer_v1` claims raw scaled-integer parity with `emul.FixedPoint(value, valid, fmt)`, where `FixFormat.bits = ibits + fbits` and min/max are scaled integers (`emul/src/emul/FixedPoint.scala:3`; `emul/src/emul/FixFormat.scala:3-11`). `dual_manifest_labelled_v1` claims both lanes only when each ABI entry declares its lane. `target_native_fixed_v1` claims only target/tool co-sim behavior unless a separate proof maps vendor rounding and overflow to the bit-exact lane.

## 2. Scalar Input, Rounding, And Rejection

Under Cppgen compatibility, accepted host input for fractional fixed is decimal/binary `double`; CLI/text uses `std::stod`, while integer fixed uses `sto*` and refuses 128-bit string parsing (`CppGenCommon.scala:102-119`; `src/spatial/codegen/cppgen/CppGenDebug.scala:26`). Conversion multiplies by `2^f` in host floating point and C++-casts to the raw integer, so fractional parts after scaling are truncated by C++ cast rules; host conversion does not saturate (`CppGenInterface.scala:42-51`). Readback sign-extends signed raw values before dividing to host `double` (`CppGenInterface.scala:64-80`). Under bit-exact, primary input is raw signed or unsigned storage bits; logical decimal text is an adapter, parsed exactly, scaled by `2^f`, then truncated toward zero through the emul `BigDecimal(...).toBigInt` path (`FixedPoint.scala:156-167`). Overflow wraps through `clamped` unless the caller selects a strict diagnostic mode; saturation is reserved for explicit `FixToFixSat`/`Sat*` semantics (`FixedPoint.scala:203-221`; `src/spatial/codegen/scalagen/ScalaGenFixPt.scala:92-114`).

## 3. Raw APIs, CLI, And Files

The Rust API should expose `from_raw_bits`, `from_scaled_int`, `to_raw_bits`, and `to_scaled_int` for `bit_exact_scaled_integer_v1`; these APIs never round and reject wrong-width values before launch. For `cppgen_fractional_double_shift_v1`, raw APIs are transport escape hatches and must be labelled as bypassing legacy double approximation. Plain CLI arguments remain decimal compatibility because Cppgen copies `argv` to `vector<string>` and `InputArguments()` exposes strings (`src/spatial/codegen/cppgen/CppFileGen.scala:131-143`; `src/spatial/codegen/cppgen/CppGenArray.scala:94-104`). A raw CLI value needs an explicit prefix or manifest field such as `raw_fixpt`. Binary FileIO follows the selected storage policy: Cppgen reads raw bytes into `vector<rawtp>` then divides fixed values, and writes fixed values as `raw = value * (1 << f)` before `fstream.write` (`src/spatial/codegen/cppgen/CppGenFileIO.scala:40-68`, `:73-86`). CSV remains text tokens unless a column declares raw integer fixed (`CppGenFileIO.scala:92-134`).

## 4. DRAM, Vectors, Structs, And Bit Views

DRAM/vector packing must be raw and LSB0 under bit-exact and dual labelled mode. Cppgen already rawifies fractional fixed vectors width >= 8, packs integer subbyte lanes with element `j` at `j * width`, and rejects fractional subbyte fixed (`src/spatial/codegen/cppgen/CppGenInterface.scala:85-131`). Scalagen bit views are also LSB-first through `.bits` and `FixedPoint.fromBits`; `fromBits` treats `fmt.bits - 1` as sign and preserves validity across all bits (`src/spatial/codegen/scalagen/ScalaGenBits.scala:47-74`; `emul/src/emul/FixedPoint.scala:45`, `:171-188`). Struct fields are raw storage: Cppgen `SimpleStruct` stores `asIntType`, setters call `toTrueFix`, `toString` calls `toApproxFix`, and `toRaw` concatenates fields by cumulative bit offset (`src/spatial/codegen/cppgen/CppGenArray.scala:153-192`). Therefore struct field manifests need field policy labels, raw offset, logical format, and pretty-print policy.

## 5. Diagnostics And Recommendation

Every mismatch should report `conversion_policy`, `type_ref`, signedness, `ibits`, `fbits`, raw hex, scaled integer, logical decimal if representable, input surface, truncation, wrap/saturate/reject decision, and comparison mode. Required errors: invalid parse, lossy decimal in strict bit-exact mode, out-of-width raw integer, fractional subbyte transfer, manifest-policy mismatch, and target-native incomparable result. D-23 already reserves `host_conversion_policy` in `numeric_formats` and asks diagnostics to carry policy labels (`D-23-research/06-abi-manifest-schema.md:26`, `:30`). Recommend `dual_manifest_labelled_v1` as the project contract, with `bit_exact_scaled_integer_v1` as the default golden lane, `cppgen_fractional_double_shift_v1` as a legacy adapter, and `target_native_fixed_v1` as report/co-sim evidence only. This matches the D-24 queue boundary: choose fixed-point host conversion without taking over D-17 rounding, D-18 float packing, D-19 FMA, or D-23 ABI ordering (`20 - Research Notes/40 - Decision Queue.md:103-105`; `D-24-research/05-overlap-numeric-abi.md:30-32`).
