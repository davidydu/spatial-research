# D-16 Research: Current Emul OOB Behavior

## Scope

This note covers the present Scala simulator/emulation behavior for out-of-bounds memory access, not the final D-16 Rust policy. The relevant implementation is split across two surfaces. First, `emul.OOB` owns process-level OOB logging and the reusable `readOrElse` / `writeOrElse` wrappers. Second, `ScalaGenMemories` emits simulator lifecycle calls and also contains a codegen-local OOB helper that wraps generated memory operations in `try` / `catch`.

`OOB` creates two lazy `PrintStream`s, one for `./logs/writes.log` and one for `./logs/reads.log` (`emul/src/emul/OOB.scala:6-8`). `open()` creates `./logs/` and forces both streams to initialize; `close()` closes both streams (`emul/src/emul/OOB.scala:9-17`). ScalaGen wires that lifecycle around generated simulator execution by emitting `OOB.open()` before main and `OOB.close()` after main (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:14-21`).

## `readOrElse`

`readOrElse` takes a memory name, address string, invalid value, enable bit, and by-name read expression (`emul/src/emul/OOB.scala:19`). It always enters the `try` and evaluates the supplied read block; the enable only controls logging, not evaluation (`emul/src/emul/OOB.scala:20-23`). Current memory callers therefore carry the real enable guard inside the by-name block, returning `invalid` instead of touching the array when disabled, for example in `BankedMemory.apply` and `ShiftableMemory.apply` (`emul/src/emul/BankedMemory.scala:31-33`, `emul/src/emul/ShiftableMemory.scala:41-43`).

For an in-bounds enabled read, the stream receives `Mem: <mem>; Addr: <addr>` and the data is returned (`emul/src/emul/OOB.scala:21-23`). If the read throws `java.lang.ArrayIndexOutOfBoundsException`, the catch logs the same memory/address with `[OOB]` when enabled, then returns the caller-provided invalid value (`emul/src/emul/OOB.scala:25-28`). No exception is rethrown. Other exception types are outside this catch and will still escape.

## `writeOrElse`

`writeOrElse` mirrors the read wrapper for writes: memory name, address string, data value, enable bit, and by-name write expression (`emul/src/emul/OOB.scala:30`). It evaluates the write block inside `try`; if that block completes and the operation was enabled, it appends `Mem: <mem>; Addr: <addr>; Data: <data>` to `writes.log` (`emul/src/emul/OOB.scala:31-34`). As with reads, callers guard the actual array update inside the block, so disabled writes normally do no work and do not log (`emul/src/emul/BankedMemory.scala:40-42`, `emul/src/emul/LineBuffer.scala:52-57`).

On `java.lang.ArrayIndexOutOfBoundsException`, enabled writes log the attempted memory, address, and data with `[OOB]`, then return `Unit` without retrying or rethrowing (`emul/src/emul/OOB.scala:35-37`). The practical simulator behavior is write discard: the invalid write has no side effect except the OOB log entry. There is no assertion, panic, or fail-fast mode in this wrapper.

## ScalaGen OOB Helper

`ScalaGenMemories.oob` is a separate generated-code pattern. It derives a memory display name, formats the address either from indices or from `err.getMessage`, emits a `try` block around the supplied memory code, and catches only `java.lang.ArrayIndexOutOfBoundsException` (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-47`). On catch it emits a stdout warning of the form `[warn] <ctx> Memory <name>: Out of bounds <read|write> at address ...` (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:41-48`).

For generated reads, the catch also emits `invalid(tp)` as the expression value (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:48`). For generated writes, no value is emitted after the warning, so the write is effectively discarded after warning (`src/spatial/codegen/scalagen/ScalaGenMemories.scala:48-49`). The invalid value is type-directed elsewhere, e.g. fixed point uses `FixedPoint.invalid(...)`, floating point uses `FloatPoint.invalid(...)`, and bit uses `Bool(false,false)` (`src/spatial/codegen/scalagen/ScalaGenFixPt.scala:26-28`, `src/spatial/codegen/scalagen/ScalaGenFltPt.scala:32-34`, `src/spatial/codegen/scalagen/ScalaGenBit.scala:21-23`).

## Rust Policy Pressure

A Scalagen-compatible Rust simulator should not model OOB as an ordinary Rust panic. The closest behavioral match is explicit bounds checking around simulator memory access: enabled in-bounds reads and writes log normal accesses; enabled OOB reads log OOB and return the memory type's invalid value; enabled OOB writes log OOB and discard the write. Disabled operations should preserve the existing caller-level convention: no log and no array touch, with reads producing invalid only because the disabled read path asks for it.

Synthesis assertions are a stricter policy than the current emul surface. They may be desirable for hardware-facing Rust or IR validation, but they would not reproduce the existing simulator contract. The current evidence therefore favors separate simulator and synthesis modes as an option to keep compatibility: simulator mode preserves log/invalid/discard behavior, while synthesis mode can assert or reject OOB according to hardware policy. This is only the current-behavior angle, not the final D-16 synthesis.
