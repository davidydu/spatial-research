---
type: "research"
decision: "D-16"
angle: 6
---

# Rust Mode Design And Diagnostics

## Frame And Constraints

D-16 is not just a question of whether Rust should "check bounds." Current Scalagen behavior is explicitly non-aborting: enabled reads and writes are wrapped by `OOB.readOrElse` / `OOB.writeOrElse`; reads return the caller-provided invalid value on `ArrayIndexOutOfBoundsException`, and writes are dropped after logging (`emul/src/emul/OOB.scala:19-38`). Scalagen also emits an outer catch that prints a stdout warning and returns `invalid(tp)` for OOB reads (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`). The vault already classifies this as a simulator-versus-synthesis split, not settled language semantics ([[20 - Open Questions]], [[30 - Adversarial Review]], [[scalagen-reference-semantics]]).

The Rust design should therefore make mode provenance first-class. A run must say whether it is answering "what did Scalagen historically do?", "where would hardware be unsafe?", or "what assumptions did synthesis rely on?" A single unlabelled default would collapse those questions.

## Runtime Modes

`compat_log_invalid` matches Scalagen for legacy comparison. For enabled accesses, it logs normal and OOB events, returns typed invalid on OOB reads, and suppresses OOB writes. Disabled accesses return invalid without an OOB event, following `BankedMemory.apply` and `ShiftableMemory.apply`, where the guarded body only touches storage when `en.value` is true (`emul/src/emul/BankedMemory.scala:28-42`; `emul/src/emul/ShiftableMemory.scala:36-58`). This mode should be exact enough to reproduce old goldens and `./logs/reads.log` / `./logs/writes.log` expectations.

`strict_trap` treats any enabled OOB as a simulator error. It should stop before returning invalid or committing later side effects, preserving the failed access diagnostic. This is the cleanest mode for CI tests that intend hardware legality.

`assert_collect` is a non-halting debug mode: record every enabled OOB assertion failure, then continue with the `compat_log_invalid` data behavior. It is useful when one run should reveal all bad lanes or all bad memories, but its final values must be labelled contaminated.

`synth_assert` is a lowering policy, not merely a simulator policy. It emits or preserves a bounds assertion in the HLS/synthesis-facing artifact and ties the assertion to the same static access identity used by the simulator.

`assume_inbounds` removes dynamic checking only under proof or explicit waiver. Its artifact must carry the assumption as a contract; violating it is outside the defined simulator result rather than a new invalid-value behavior.

## Diagnostics And Replay

Keep Scalagen-compatible text mirrors, but make Rust's canonical log JSON Lines. Legacy mirrors:

`reads.log`: `Mem: <mem>; Addr: <addr>[ [OOB]]`

`writes.log`: `Mem: <mem>; Addr: <addr>; Data: <data>[ [OOB]]`

Canonical records should include: `event`, `simulator_mode`, `access_kind`, `mem`, `mem_id`, `ctx`, `static_op_id`, `dynamic_instance_id`, `lane`, `enabled`, `addr_kind`, `indices`, `bank`, `offset`, `flattened_addr`, `extent`, `in_bounds`, `data`, `returned`, `write_committed`, `assertion_id`, `source_loc`, and `replay_step`. For deterministic replay, `replay_step` should be assigned by stable execution order inside the selected simulator mode, not by wall-clock order or host thread scheduling. A replay manifest should also record mode, queue/back-pressure policy if relevant, random seed if any other simulator feature uses randomness, and the Rust runtime version. This mirrors the D-09/D-15 pattern of persisting simulator policy rather than trusting ambient execution state ([[D-09]], [[D-15]]).

Invalid values should use the existing typed representation. Fixed-point invalid is `FixedPoint.invalid(FixFormat(...))`, represented in emul as value `-1` with `valid=false`; float invalid is `FloatPoint.invalid(FltFormat(...))`, represented as `NaN` with `valid=false`; bit invalid is `Bool(false,false)` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:26-28`; `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:32-34`; `src/spatial/codegen/scalagen/ScalaGenBit.scala:21-23`; `emul/src/emul/FixedPoint.scala:161`; `emul/src/emul/FloatPoint.scala:287`). Rust should model this as typed values with validity, not as host `Option<T>` alone, because downstream arithmetic propagates `valid=false` and prints `"X"` in current emul ([[scalagen-reference-semantics]]).

## Synthesis Relationship And Preliminary Recommendation

Chisel/HLS-facing memory emission connects banks, offsets, and enables into physical memory ports; there is no Scalagen-style logfile or invalid-value fallback in the hardware path (`src/spatial/codegen/chiselgen/ChiselGenMem.scala:64-117`; `fringe/src/fringe/templates/memory/MemPrimitives.scala:727-776`). Therefore the Rust simulator should not advertise `compat_log_invalid` as synthesis-faithful.

Preliminary recommendation: support all five modes, with `compat_log_invalid` as the explicit legacy profile, `assert_collect` as the default exploratory Rust simulator profile, and `strict_trap` as the HLS-conformance test profile. Synthesis builds should default to `synth_assert` in checked configurations and allow `assume_inbounds` only when static analysis proves the address contract or the user records a waiver. This preserves Scalagen debugging behavior without making OOB invalid propagation the silent contract for generated hardware. This is an angle recommendation only, not final D-16.
