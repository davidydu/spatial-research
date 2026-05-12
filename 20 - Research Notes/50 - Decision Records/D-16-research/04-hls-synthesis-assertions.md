---
type: "research"
decision: "D-16"
angle: 4
title: "HLS Synthesis Behavior And Assertion Options"
date: 2026-04-27
---

# HLS Synthesis Behavior And Assertion Options

## Source Boundary

Scalagen defines a recoverable simulator behavior, not a plausible physical-memory contract. `OOB.readOrElse` catches `ArrayIndexOutOfBoundsException`, logs `[OOB]`, and returns the caller's invalid value; `OOB.writeOrElse` logs and drops the write (`emul/src/emul/OOB.scala:19-38`). The generated Scala helper repeats that shape for other memory code: it emits a `try` / `catch`, prints an out-of-bounds warning, and substitutes `invalid(tp)` only on reads (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`). Type invalids are real values with validity metadata for fixed, float, and bit types (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:26-28`; `src/spatial/codegen/scalagen/ScalaGenBit.scala:21-23`; `emul/src/emul/FixedPoint.scala:161`; `emul/src/emul/FloatPoint.scala:287`).

## Hardware Contrast

The Chisel path connects bank, offset, data, and enable signals into memory ports; it does not emit a logfile, exception recovery path, or typed invalid fallback on OOB memory reads (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:73-103`). Fringe `Mem1D` gates writes with an in-bound predicate, but reads either use mux/default behavior for small register memories or directly index a memory for larger cases (`fringe/src/fringe/templates/memory/MemPrimitives.scala:727-775`). That is already a hardware divergence: at best, an illegal read returns implementation-dependent data or a default zero-like value, not `FixedPoint.invalid`. Unverified HLS implication: C/C++ array OOB should be treated as undefined/unsafe for final hardware, especially for external-memory pointers where an OOB address may become a real AXI transaction.

## Assert Versus Assume

Assertions have two meanings that D-16 must not collapse. Unverified HLS framing: a runtime assertion is hardware logic, comparing address terms against extents, OR-ing lane failures, and stopping/reporting through a chosen mechanism. An optimizer assertion or assumption is a contract: it tells the compiler that bad addresses never occur, allowing narrower counters or removed guards. AMD documentation is mixed across versions: UG1399 2021.1 says C `assert` can provide range information and reduce hardware, while UG1399 2021.2 says C/C++ `assert` is not supported and may create bad logic or block optimization ([AMD 2021.1 assertions](https://docs.amd.com/r/2021.1-English/ug1399-vitis-hls/Assertions); [AMD 2021.2 assertions](https://docs.amd.com/r/2021.2-English/ug1399-vitis-hls/Assertions)). Current Vitis docs instead emphasize C-simulation sanitizers for address and undefined-behavior failures, plus `__SYNTHESIS__` only for excluding non-synthesizable code ([AMD `csim_design`](https://docs.amd.com/r/en-US/ug1399-vitis-hls/csim_design); [AMD system calls](https://docs.amd.com/r/en-US/ug1399-vitis-hls/System-Calls)). Therefore final HLS should not rely on bare C `assert` as the only hardware safety story.

## Cost And Macro Policy

Unverified HLS cost model: per-access bounds checks add comparators for each dimension or flattened address, lane-wise enable gating, read-data muxes for invalid/default values if recovery is required, and write masks. In an unrolled banked memory, that cost multiplies by lanes and can lengthen the address-to-enable path, raising LUT use or initiation interval. Statically proved accesses should compile with no dynamic guard. Spatial already has bounds metadata for exact, expected, and user upper bounds (`src/spatial/metadata/bounds/BoundData.scala:23-38`; `src/spatial/metadata/bounds/package.scala:10-19`), API rank checks for SRAM index arity rather than dynamic range (`src/spatial/lang/SRAM.scala:281-295`), and loop-lane valid bits from counter-chain OOBs (`src/spatial/codegen/chiselgen/ChiselGenController.scala:68-97`). The HLS backend should reuse those facts before inserting checks.

Use macros only to select observability, not semantics. AMD warns that `__SYNTHESIS__` can make C simulation and synthesis differ, and says not to use it to change functionality ([AMD system calls](https://docs.amd.com/r/en-US/ug1399-vitis-hls/System-Calls)). So `#ifndef __SYNTHESIS__` logging, sanitizer helpers, or rich diagnostic strings are fine; changing OOB reads from invalid in C-sim to unchecked reads in synthesis must be a named D-16 mode, not a hidden macro fork.

## Final HLS Emission

Unverified HLS recommendation: emit three distinct artifacts/policies. `compat_sim` keeps Scalagen-style log/invalid/drop in Rust and optional HLS C simulation wrappers. `checked_hls` emits explicit synthesized address-failure logic only in debug/conformance builds, preferably routed to the same breakpoint/status channel used by Spatial assertions: Chisel turns `AssertIf` into breakpoint wiring, not memory invalid propagation (`src/spatial/codegen/chiselgen/ChiselGenDebug.scala:29-34`). `release_hls` emits no recovery guards after proof or explicit waiver, but records an `assume_inbounds` contract in the manifest. For final synthesis, the default should be checked during validation and assume/prove in release; never synthesize Scalagen's invalid-value recovery as the hardware default.
