---
type: "research"
decision: "D-24"
angle: 7
topic: "implementation-cost-migration"
---

# D-24 Angle 7: Implementation Cost And Migration

## Cost Drivers

D-24 is small as an algorithm but broad as an ABI migration. The legacy split is explicit: Cppgen converts fractional fixed values to raw shifted integers with `toTrueFix`, converts raw values back with `toApproxFix`, maps fractional `FixPtType` host values to `double`, and parses fractional fixed text with `stod` (`src/spatial/codegen/cppgen/CppGenCommon.scala:36-49`, `:75-89`, `:102-119`). The same policy appears at scalar boundaries: `SetReg` multiplies by `1 << f`, while `GetReg` sign-extends and divides by `1 << f` (`src/spatial/codegen/cppgen/CppGenInterface.scala:42-80`). But Scalagen/emul stores `FixedPoint(value: BigInt, valid, fmt)`, shifts integer constructors by `fbits`, parses decimals by multiplying by `2^fbits`, and wraps by raw bits (`emul/src/emul/FixedPoint.scala:3`, `:150-159`, `:203-209`). So any Rust default touches host conversion, manifests, tests, reports, and every transfer surface, not just one helper.

## Policy Cost Comparison

`cppgen_fractional_double_shift_v1` as the default is the lowest implementation cost: copy Cppgen's `double` host representation, `std::stod` style parsing, C cast after multiplying by `2^f`, register sign extension, and approximate readback. It preserves existing host expectations around `FixPtArgInOut` (`test/spatial/tests/feature/unit/ArgInOut.scala:64-90`) and avoids immediate golden churn. The migration risk is long-lived: structs store raw fields but print approximate values and field reads return stored raw fields directly (`src/spatial/codegen/cppgen/CppGenArray.scala:153-170`, `:200-206`), and Cppgen fixed arithmetic is ordinary C++ `+`, `*`, `/` on doubles (`src/spatial/codegen/cppgen/CppGenMath.scala:26-34`).

`bit_exact_scaled_integer_v1` as the default is medium-high cost but cleaner. Rust needs a fixed runtime representation with signedness, integer bits, fractional bits, sign extension, wrapping, raw hex/decimal formatting, and exact parse or explicit rejection. This aligns with emul arithmetic on raw values (`emul/src/emul/FixedPoint.scala:14-17`) and bit layout (`emul/src/emul/FixedPoint.scala:45`, `:176-188`). It also aligns with the C++ fixed helper's raw API, where `from_base` bypasses scaling and `to_raw` exposes storage (`resources/synth/datastructures/Fixed.hpp:289-315`, `:450-459`). Cost comes from updating tests to compare raw payloads in addition to logical decimals.

Dual mode with bit-exact default plus Cppgen-compatible legacy is highest one-time implementation cost but lowest migration risk. It needs an enum in Rust host bindings, manifest readback, diagnostics, two fixture modes, and explicit report provenance. D-23 already reserved `conversion_policy` in `numeric_formats` and asks Rust bindings to consume the manifest for scalar writes, DRAM copy, files, streams, counters, and lifecycle (`D-23.md:61-67`, `:83-93`). This mode lets old generated Cppgen runs remain reproducible while new Rust/HLS runs become bit-exact by default.

`target_native` is deceptively expensive. D-23 explicitly rejects target-native HLS ABI as the source contract because vendor signatures should be projections, not Spatial semantics (`D-23.md:73-77`). It would multiply the test matrix across VCS/AWS/Zynq/KCU/ZCU-style runtimes, all of which expose raw `setArg`, `getArg`, and `memcpy` mechanics behind target contexts (`resources/synth/vcs.sw-resources/FringeContextBase.h:16-23`). Treat it as an adapter label, not the default.

## Affected Surfaces

Runtime libraries: Rust host runtime needs the real implementation; Cppgen compatibility needs a faithful clone of `toTrueFix`/`toApproxFix`; Scalagen/emul remains the bit-exact oracle. Host bindings must apply the policy before `setArg`, after `getArg`, and around `memcpy` (`src/spatial/lang/api/TransferAPI.scala:9-24`, `:37-44`; `src/spatial/codegen/cppgen/CppGenInterface.scala:85-131`). Manifest changes are already scoped by D-23: `host_abi`, `memories`, `streams`, `host_files`, `numeric_formats`, `lifecycle`, and `diagnostics` all need policy fields or references (`D-23.md:55-63`).

CLI and files are a separate migration lane. Cppgen builds `argv` as strings (`src/spatial/codegen/cppgen/CppFileGen.scala:131-143`), CSV loading maps tokens through `token.to[T]`, and fixed CSV output calls `toText` (`src/spatial/lang/api/FileIOAPI.scala:50-79`). Binary file IO already rawifies fixed data on write and approximates it on read (`src/spatial/codegen/cppgen/CppGenFileIO.scala:40-68`, `:73-86`). DRAM transfers, structs, and vectors need raw fixtures: DRAM rejects fractional subbyte payloads and packs subbyte integers LSB-first (`src/spatial/codegen/cppgen/CppGenInterface.scala:95-103`, `:120-128`); vector and bit views are LSB-first (`src/spatial/codegen/cppgen/CppGenArray.scala:111-151`); struct transfer tests include fractional fixed fields (`test/spatial/tests/feature/transfers/TransferStruct.scala:9-16`, `:39-42`).

## Staged Rollout

Stage 1 should only emit and read `conversion_policy`, defaulting legacy generated Cppgen to `cppgen_fractional_double_shift_v1` while recording raw and decimal values in reports; reports already print ArgIns/ArgIOs and instrumentation without policy provenance (`src/spatial/codegen/cppgen/CppGenAccel.scala:64-89`). Stage 2 adds Rust bit-exact converters plus compatibility converters and golden tests for `FixPtArgInOut`, fixed DRAM/math, CSV, binary, vectors, and structs (`test/spatial/tests/feature/math/FixBasics.scala:51-85`; `test/spatial/tests/feature/host/ReadCSV1D.scala:8-33`; `test/spatial/tests/feature/host/BinaryFileIO.scala:5-59`; `test/spatial/tests/feature/vectors/UserVectors.scala:31-67`). Stage 3 flips new Rust/HLS manifests to bit-exact default, requiring opt-in legacy mode for Cppgen replay. Stage 4 permits `target_native` only when a backend report names the adapter and the comparison mode.
