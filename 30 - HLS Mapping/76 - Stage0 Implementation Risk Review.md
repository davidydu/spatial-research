---
type: hls-mapping
construct: stage0-implementation-risk-review
category: rework
status: draft
date: 2026-06-25
---

# Stage0 Implementation Risk Review

## Go/no-go assessment for Stage 0

Assessment: conditional go for a tightly gated Stage 0 implementation. The scalar Lab1Part1 lowering is implementable safely now if the patch is limited to the two-input scalar-add tracer bullet and rejects everything outside that shape. It is not safe to broaden into Stage 1 memory, general registers, loops, or a generic HLS backend in the same patch.

The technical basis is solid: the Stage 0 contract is exactly `ArgIn`, `ArgOut`, `setArg`, `getArg`, `Accel`, `RegRead`, `RegWrite`, and integer add (`/Users/david/Documents/Spatial Research/30 - HLS Mapping/60 - EE109 HLS Lowering Map.md:21-24`), and the tracer bullet requires one `AccelScope`, two `ArgInNew`s, one `ArgOutNew`, two host `SetReg`s, one host `GetReg`, two kernel `RegRead`s, one `FixAdd`, and one `RegWrite` (`/Users/david/Documents/Spatial Research/30 - HLS Mapping/70 - Lab1Part1 Tracer Bullet.md:35-51`). The required C++ target and host check are also narrow and do not require Vitis for the first proof (`/Users/david/Documents/Spatial Research/30 - HLS Mapping/70 - Lab1Part1 Tracer Bullet.md:85-123`).

The current source evidence supports the shape. The nested selected Lab1Part1 file is a two-input scalar add with `runtimeArgs = "3 5"` and expected output `M + N` (`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala:5-32`). The existing early IR log shows the exact Stage 0 body under `AccelScope` (`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part1RegExample/0001_IR.log:43-160`), and the final IR log still preserves the same pattern after renumbering and metadata insertion (`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part1RegExample/0090_IR.log:48-206`).

The main safety caveat is source selection. The lab repository also contains `src/test/scala/Lab1.scala`, where `Lab1Part1RegExample` currently has three ArgIns and sums three values (`/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/src/test/scala/Lab1.scala:7-44`). Stage 0 is a go only if the manager pins the canonical two-input source or updates the manifest and tracer bullet intentionally. A bare `testOnly Lab1Part1RegExample` in that lab root is not a safe acceptance target until the source ambiguity is resolved.

There is already uncommitted HLS work in the Spatial tree: `Spatial.scala` imports `hlsgen`, constructs `HLSGen`, and runs it under `enableHLS` (`/Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:9`, `/Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:147-151`, `/Users/david/Documents/David_code/spatial/src/spatial/Spatial.scala:242-250`); `SpatialConfig` carries `enableHLS` (`/Users/david/Documents/David_code/spatial/src/spatial/SpatialConfig.scala:21-25`, `/Users/david/Documents/David_code/spatial/src/spatial/SpatialConfig.scala:103-116`). Treat that as concurrent implementation state, not as blank ground.

## Hidden risks and how to constrain them

| Risk | Evidence | Constraint |
|---|---|---|
| Source ambiguity can make the patch pass the wrong Lab1Part1. | The Wave 1 tracer points at the nested two-input file, while the lab root has a same-named three-input class. | Require the manager patch or runbook to state the exact source path used for Stage 0 and the exact expected manifest: two scalar inputs, one scalar output, expected `8`. |
| The existing Cppgen path is not a kernel emitter. | Cppgen records ArgIns and ArgOuts but leaves ArgOut allocation and RegWrite as comments, and `AccelScope` emits Fringe runtime calls (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenInterface.scala:20-35`; `/Users/david/Documents/David_code/spatial/src/spatial/codegen/cppgen/CppGenAccel.scala:16-36`). | Keep HLS generation separate from Cppgen/Fringe. Reuse node knowledge, not emitted Cppgen text. |
| Pass timing can hide brittle symbol assumptions. | Final IR still has the desired nodes, but symbol IDs changed from `x5/x6/x9/x14` to `x74/x75/x78/x46`. | Match by node type, memory role, and `AccelScope` membership, never by symbol IDs or log line names. |
| Current HLS scaffold accepts too broad an input count. | `HLSGen` only requires at least one ArgIn and exactly one ArgOut (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:60-66`). | For Stage 0 Lab1Part1, require exactly two ArgIns unless the manifest explicitly changes. |
| The generated harness can share the same bug as the kernel lowering. | `HLSGen` computes `expected` from `expr(outData)`, the same expression used to emit the kernel assignment (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:103`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:121-128`). | Compare against the independent manifest/source oracle: inputs `3`, `5`, expected `8`. Do not derive the expected value from the lowered kernel expression alone. |
| Missing runtime args can be silently converted into a passing-looking harness. | `HLSGen` uses `runtimeValues.lift(i).getOrElse("0")` for inputs (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:49-51`, `/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:108-124`). | Fail if runtime values do not cover every Stage 0 ArgIn. Preserve the manifest values in emitted comments or a side record. |
| Unsupported diagnostics can look like compiler bugs. | `hlsFail` throws a generic exception, while existing sanity checks use `error(ctx, ...)` plus `IR.logError()` for user-facing violations (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/hlsgen/HLSGen.scala:45-47`; `/Users/david/Documents/David_code/spatial/src/spatial/traversal/UserSanityChecks.scala:34-45`). | For unsupported user programs, emit clear HLS-subset diagnostics with source context where available. Reserve exceptions for internal impossible states. |
| No HLS regression backend is wired into `SpatialTest`. | `SpatialTest.backends` lists Scala, FPGA, and CS217 backends, but no HLS backend (`/Users/david/Documents/David_code/spatial/src/spatial/SpatialTest.scala:80-89`, `/Users/david/Documents/David_code/spatial/src/spatial/SpatialTest.scala:151`). | First patch can be CLI-driven, but the review gate should include an explicit command that compiles generated C++ and runs the harness. |

## Required unsupported diagnostics

The Stage 0 path should reject unsupported input before emitting partial HLS output. Required diagnostic categories:

- Shape mismatch: expected exactly one `AccelScope`, exactly two `ArgIn[Int]`, exactly one `ArgOut[Int]`, exactly two host `SetReg`s to those inputs, exactly one host `GetReg` from the output, and exactly one kernel `RegWrite`.
- Source mismatch: if the selected source has three ArgIns or a three-term sum, report that it is not the Stage 0 Lab1Part1 manifest being implemented.
- Type mismatch: only signed or unsigned integer `Fix` with zero fractional bits and width up to the chosen C++ scalar support is accepted. Fractional fixed point, floating point, FMA, unbiased rounding, and FloatPoint behavior remain deferred by the MVP matrix (`/Users/david/Documents/Spatial Research/30 - HLS Mapping/50 - EE109 MVP Blocker Matrix.md:20-34`, `/Users/david/Documents/Spatial Research/30 - HLS Mapping/50 - EE109 MVP Blocker Matrix.md:55-64`).
- Kernel node mismatch: inside `AccelScope`, only `RegRead` from Stage 0 ArgIns, nested `FixAdd` over supported expressions, constants, and `RegWrite` to the Stage 0 ArgOut are allowed.
- Host/kernel boundary mismatch: `setArg` and `getArg` are host transfers only; use inside `Accel` should remain rejected, matching existing Spatial sanity behavior (`/Users/david/Documents/David_code/spatial/src/spatial/traversal/UserSanityChecks.scala:34-47`).
- Memory/control mismatch: reject DRAM, SRAM, LUT, RegFile, LineBuffer, FIFO/LIFO, streams, blackboxes, `Foreach`, `Reduce`, `FSM`, `Pipe`, `par`, dense transfers, sparse transfers, and explicit banking hints in Stage 0. These are later-stage or deferred constructs (`/Users/david/Documents/Spatial Research/30 - HLS Mapping/60 - EE109 HLS Lowering Map.md:31-56`, `/Users/david/Documents/Spatial Research/30 - HLS Mapping/60 - EE109 HLS Lowering Map.md:68-79`).
- Oracle mismatch: if the generated harness cannot recover the manifest oracle value `8`, fail with an ABI/oracle diagnostic instead of emitting a self-referential expected expression.

## Review checklist for the manager's eventual code patch

- Confirms whether the existing uncommitted `hlsgen` scaffold is adopted, replaced, or merged, without overwriting unrelated workspace edits.
- Pins the Stage 0 input source to the nested two-input Lab1Part1 file or updates the Wave 1 manifest deliberately before changing compiler code.
- Adds or preserves a single HLS codegen gate, disabled by default, so normal `--synth`, Cppgen, Chiselgen, CS217, and Scala simulation behavior stay unchanged.
- Emits the Stage 0 kernel from IR, not from a handwritten source template disconnected from `ArgInNew`, `ArgOutNew`, `SetReg`, `GetReg`, `AccelScope`, `RegRead`, `FixAdd`, and `RegWrite`.
- Produces a kernel equivalent to `extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut)` with AXI-Lite pragmas and `*argRegOut = argRegIn0 + argRegIn1`.
- Produces a harness or test command that compiles the generated C++ with a normal C++ compiler and independently checks `3`, `5`, and `8`; Vitis/Vivado HLS remains outside the first completion gate.
- Fails closed on non-Stage-0 constructs with the diagnostics above, and does not silently skip unsupported kernel statements.
- Does not change Cppgen ABI ordering, Chiselgen ABI ordering, Fringe runtime setup, memory banking, retiming, DSE latency, or Stage 1-4 lowering in the same patch.
- Includes a negative check for the same-named three-input lab-root variant so the implementation cannot accidentally certify the wrong source.
