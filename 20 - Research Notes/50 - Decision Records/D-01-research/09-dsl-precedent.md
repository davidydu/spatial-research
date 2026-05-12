---
type: research
decision: D-01
angle: 9
---

## Per-project survey

**LegUp HLS.** LegUp compiles C/C++-style input toward FPGA hardware and appears to depend mostly on compiler-recognized operators, C library calls, and target resource binding rather than a separate portable math-op dialect (unverified). When a math operation lacks a realizable hardware implementation, the practical policy appears to be rejection, unsupported-code diagnostics, or requiring the user to provide a library, intrinsic, or external implementation (unverified). This looks closer to “legalize before or at HLS boundary” than to automatic cross-vendor repair (unverified).

**Bambu / PandA.** Bambu appears to expose a more explicit allocation and binding model, where operations can be mapped onto technology libraries, generated hardware resources, or externally described components (unverified). Its precedent is that vendor or device gaps are handled through technology characterization and resource libraries when available, while missing operators become unsupported synthesis cases or require user-provided components (unverified). This is a pluggable-backend policy rather than a promise that every source-level math op is always available (unverified).

**Calyx.** Calyx uses an intermediate representation centered on components, cells, and primitive libraries, so math support appears to live in the available primitive definitions and backend lowering rules (unverified). If a backend does not define or lower a primitive, the gap is expected to surface as a compile-time/backend error instead of silent substitution (unverified). The extensibility point is clear: add a primitive, add a backend-specific implementation, or rewrite the program before backend emission (unverified).

**Halide HLS.** Halide separates algorithm from schedule and HLS-oriented flows have historically emitted restricted C/C++ or accelerator-oriented code for downstream HLS tools (unverified). Math operations outside the supported subset appear to be handled by staying within the targetable subset, using explicit extern/intrinsic hooks, or letting the downstream HLS compiler reject the operation (unverified). The policy is therefore pragmatic: Halide can stage code generation, but vendor-specific math legality is usually resolved at the backend boundary or by user-visible escape hatches (unverified).

**HeteroCL.** HeteroCL presents a Python-embedded DSL for heterogeneous accelerator generation and commonly lowers toward vendor HLS flows such as C/C++ for FPGA synthesis (unverified). Its math-op policy appears to inherit much of the downstream HLS tool’s supported subset, with type control and scheduling exposed in the DSL but not a universal abstraction over all vendor math IP gaps (unverified). When gaps occur, the likely strategies are restriction, custom intrinsics, or backend-specific code paths rather than implicit emulation (unverified).

**hls4ml / FINN.** hls4ml and FINN target neural-network inference, so they narrow the math surface to quantized layers, activation functions, lookup tables, and streaming datapaths rather than arbitrary scalar math (unverified). Unsupported or inefficient operations are often avoided by model conversion constraints, quantization choices, lookup-table approximations, or custom layer implementations (unverified). Their precedent is domain restriction plus explicit extension points, not broad vendor-neutral math completeness (unverified).

## Patterns

Across these systems, the common pattern is to avoid pretending that all math operations are portable across FPGA vendors and HLS backends (unverified). The dominant strategies are: reject unsupported operations early, restrict the source language or model format, lower only to a known-supported subset, route operations through explicit intrinsics or externs, and provide backend resource libraries or primitive definitions for vendor-specific implementations (unverified). Silent fallback appears uncommon because latency, area, precision, and timing can change materially when a math op is replaced (unverified).

## Implications for D-01

For D-01, precedent supports a typed legalization layer with explicit capability checks before Chisel or backend-specific emission (unverified). The Spatial DSL should treat math ops as abstract in the frontend, require a target capability table or primitive-library match during lowering, and fail with actionable diagnostics when no legal implementation exists (unverified). Vendor IP, lookup-table approximations, fixed-point rewrites, or custom RTL should be explicit lowering choices with visible precision and latency contracts (unverified). This precedent is informative, not binding, but it argues against silently mapping unsupported math to whatever a downstream tool happens to accept (unverified).
