---
type: open-questions
topic: language-surface
session: 2026-04-24
date_started: 2026-04-24
---

# Open Questions — Language Surface Session

Questions raised while documenting the Spatial language surface (`spatial.lang.*`, `spatial.dsl`, `spatial.libdsl`). To be escalated to `20 - Open Questions.md` by the main session.

## Q-lang-01 — Hash-collision risk in `prDeqGrp` group-id assignment

`priorityDeq` and `roundRobinDeq` (`src/spatial/lang/api/PriorityDeqAPI.scala:17, 47, 97`) tag every staged `FIFOPriorityDeq` with `prDeqGrp = fifo.head.toString.hashCode()`. The author's own `// TODO: this is probably an unsafe way to compute a group id` comment (`PriorityDeqAPI.scala:11, 26`) flags the risk: two unrelated dequeue calls whose head-fifo `toString` representations collide under `Int.hashCode()` would be grouped together by `MemoryUnrolling.scala:303-304`.

**Spec question.** What is the contract `prDeqGrp` is supposed to enforce? Is it "all dequeue ports of a single `priorityDeq` call form one group" (the documented intent), or "all dequeue ports across the whole program that share a group ID form one hardware unit" (the implemented behavior, with hash collisions as a footgun)? For the Rust port, this should be replaced with an explicit fused `PriorityDeqGroup(fifos, conds)` IR construct, but the spec needs to confirm the intended semantics first.

Source: `src/spatial/lang/api/PriorityDeqAPI.scala:11, 17, 26, 47, 97`, `src/spatial/metadata/access/AccessData.scala:43`, `src/spatial/transform/unrolling/MemoryUnrolling.scala:303-304`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-07 — `FileBus` has no struct-shape check in source

The language-surface request expected `FileBus` and `FileEOFBus` to check struct shape at construction time. The source confirms the check only for `FileEOFBus`: it pattern matches `Type[A]`, accepts a struct whose last field is `Bit`, and otherwise calls `state.logError()`. `FileBus[A]` only requires `Bits[A]` and returns `Bits[A].nbits`.

**Spec question.** Should plain `FileBus[A]` validate CSV struct shape, or is it intentionally permissive while `FileEOFBus[A]` is the checked EOF-delimited variant?

Source: `src/spatial/lang/Bus.scala:59-75`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-08 — Spatial blackbox uses attach empty file/module metadata

`SpatialBlackbox.apply` and `SpatialCtrlBlackbox.apply` attach `BlackboxConfig("", None, 0, 0, params)` to use symbols. The empty file/module fields make sense for Spatial-defined blackboxes, but the zero latency and pipeline factor differ from the default `BlackboxConfig` values of `1` and `1`.

**Spec question.** Are zero latency and zero pipeline factor semantic for Spatial blackbox uses, or are they placeholders that downstream passes replace from implementation metadata?

Source: `src/spatial/lang/Blackbox.scala:15-18, 27-30`, `src/spatial/metadata/blackbox/BlackboxData.scala:6`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-09 — `GEMV`, `CONV`, and `SHIFT` blackbox builtins are declared stubs

`Blackbox.GEMM` stages a concrete `GEMMBox`, but `GEMV`, `CONV`, and `SHIFT(validAfter)` are declared as `???`.

**Spec question.** Should the HLS language surface expose only `GEMM`, or should it reserve names for `GEMV`, `CONV`, and `SHIFT` even though the current Scala implementation does not define them?

Source: `src/spatial/lang/Blackbox.scala:101-123`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-10 — `Array.toeplitz` uses stride math despite a TODO saying stride is not incorporated

`Array.toeplitz` has a `// TODO: Incorporate stride` comment, but the implementation uses `stride0` and `stride1` in padding, output rows, and slide offsets. It is unclear whether the remaining TODO refers to a missing stride case or stale documentation.

**Spec question.** What is the intended Toeplitz layout contract for strides greater than one?

Source: `src/spatial/lang/host/Array.scala:150-174`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-11 — `Tensor3.update` indexing differs from `Tensor3.apply`

`Tensor3.apply(i,j,k)` indexes `data` with `i*dim1*dim2 + j*dim2 + k`. `Tensor3.update(i,j,k,elem)` indexes with `i*dim1*dim2 + j*dim1 + k`. For non-square `dim1`/`dim2`, these addresses differ.

**Spec question.** Is `Tensor3.update` a bug that should use `j*dim2`, or is there an undocumented storage-layout reason for the difference?

Source: `src/spatial/lang/host/Tensor3.scala:28-31`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-12 — `readBinary` accepts `isASCIITextFile` but does not use it

`readBinary[A:Num](file, isASCIITextFile: Boolean = false)` stages `ReadBinaryFile(file)` and ignores the flag.

**Spec question.** Is `isASCIITextFile` obsolete, or should `ReadBinaryFile` carry the flag so binary loading can distinguish raw numeric binary from ASCII text?

Source: `src/spatial/lang/api/FileIOAPI.scala:98-100`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-13 — HLS policy for `printSRAM1/2/3`

`printSRAM1`, `printSRAM2`, and `printSRAM3` emit `Foreach` loops over accelerator SRAMs. That differs from host tensor printing, which traverses host arrays and matrices.

**Spec question.** Should SRAM printing be simulation-only, synthesized as debug I/O, or rejected in HLS builds?

Source: `src/spatial/lang/api/DebuggingAPI.scala:98-132`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-14 — `approxEql` relative-error behavior near zero

Scalar numeric `approxEql(a,b,margin)` checks `abs(a - b) <= margin.to[T] * abs(a)`. When `a` is zero, the tolerance is zero regardless of `margin`.

**Spec question.** Is the asymmetric relative tolerance intentional, or should this use an absolute floor or `max(abs(a), abs(b))` style tolerance?

Source: `src/spatial/lang/api/DebuggingAPI.scala:152-160`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-15 — `throw` is not staged into Spatial IR

`SpatialVirtualization.__throw` delegates to `forge.EmbeddedControls.throwImpl`; unlike `return`, `while`, and `do while`, it does not emit a Spatial-specific error in this file. The source also does not stage a Spatial IR node for exceptions.

**Spec question.** Should `throw` be considered unsupported user syntax like `while`, or should it remain a staging-time Scala exception escape hatch?

Source: `src/spatial/lang/api/SpatialVirtualization.scala:103-116`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-16 — Should HLS preserve Spatial's no-while/no-return limitation?

`__return`, `__whileDo`, and `__doWhile` all emit explicit "not yet supported" errors. HLS C++ supports `while` and `return` syntactically, but Spatial currently avoids defining accelerator semantics for these virtualized constructs.

**Spec question.** Should a port inherit the current Spatial restriction exactly, or define new semantics for `while`/`return` in the HLS frontend?

Source: `src/spatial/lang/api/SpatialVirtualization.scala:103-114`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-17 — Parameter-domain metadata shape for HLS/Rust

`IntParameters` stores range domains with `(start, stride, end)` and explicit alternatives as parameter metadata on `I32.p(default)`.

**Spec question.** Should the port preserve this exact domain shape, or normalize range and explicit domains into a single parameter-domain enum?

Source: `src/spatial/lang/api/Implicits.scala:18-39, 46-55`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-18 — `@streamstruct` parent classes are collected but not rejected

The stream-struct macro collects parent names and has a TODO asking what to do if the class has parents, but it does not currently reject parent classes.

**Spec question.** Are parent classes meant to be allowed for `@streamstruct`, or should the macro reject them like methods, type parameters, and `var` fields?

Source: `src/spatial/tags/StreamStructs.scala:47-62`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-19 — Why do stream structs require both `Bits` and `Arith`?

`StagedStreamStructsMacro` generates both Bits and Arith typeclasses and injects `box` evidence requiring `StreamStruct`, `Bits`, and `Arith`.

**Spec question.** Is `Arith` required for all stream structs, or is it generated for historical consistency even when a stream port is not arithmetically meaningful?

Source: `src/spatial/tags/StreamStructs.scala:32-35, 83-99`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-20 — Duplicated macro declarations in `dsl` and `libdsl`

`@spatial`, `@struct`, and `@streamstruct` are declared independently inside both `spatial.libdsl` and `spatial.dsl`.

**Spec question.** Is the duplication required by Scala annotation resolution, or can the declarations be factored while preserving both import scopes?

Source: `src/spatial/dsl.scala:14-25, 34-45`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-02 — `log_taylor` lacks the domain guard that `exp_taylor` has

`exp_taylor` (`src/spatial/lang/api/MathAPI.scala:81-85`) is a *piecewise* approximation: zero below `-3.5`, linear between `-3.5` and `-1.2`, fifth-order Taylor above `-1.2`. By contrast, `log_taylor` (`MathAPI.scala:88-91`) is a single fourth-order Taylor expansion of `ln(x)` around `x = 1`, with no range gate. Outside `(0, 2]` the error grows fast (the Taylor series diverges).

**Spec question.** Is the difference intentional (e.g. caller is expected to pre-clip the input to a known range), or is `log_taylor` an incomplete implementation that should follow the same piecewise pattern? The `sqrt_approx` author comment (`MathAPI.scala:105`) suggests these helpers are placeholders — see Q-lang-03.

Source: `src/spatial/lang/api/MathAPI.scala:81-91`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-03 — `sqrt_approx` "placeholder until floats" — what is the intended replacement?

`sqrt_approx` (`MathAPI.scala:104-111`) carries the comment `// I don't care how inefficient this is, it is just a placeholder for backprop until we implement floats`. The implementation is a five-region piecewise fit. The comment implies that there will eventually be a float-native `sqrt` (presumably hardware-implemented, mapped to a Spatial primitive that lowers to a Xilinx CORDIC IP or similar).

**Spec question.** Is the planned replacement (a) a hardware sqrt primitive that lowers to vendor IP, (b) a higher-order Taylor expansion with float domain handling, or (c) something else? The Rust port needs to know whether to keep the piecewise approximation or to expose a single `sqrt` that dispatches to a float instruction.

Source: `src/spatial/lang/api/MathAPI.scala:104-111`, comment at line 105.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-04 — `AxiStream256` is promoted to `ShadowingAliases` but `AxiStream64`/`AxiStream512` are not

`Aliases.scala:178-180` lifts three names — `AxiStream256`, `AxiStream256Bus`, `AxiStream256Data` — into the `ShadowingAliases` layer, but `AxiStream64`/`AxiStream512` (and their Bus/Data variants) remain only in `ExternalAliases`. So app code under `import spatial.dsl._` can write `AxiStream256` directly but must spell `spatial.lang.AxiStream64` for the 64-bit variant.

**Spec question.** Is 256-bit the canonical default bus width (justifying the special promotion), or is this an oversight that should be either (a) extended to all three widths or (b) demoted? The design implication for the Rust port is whether to expose all three at the same level or to single out 256-bit as canonical.

Source: `src/spatial/lang/Aliases.scala:178-180`, `src/spatial/lang/Bus.scala:28-50`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-05 — `Label` is the only Scala-native type promoted to the root of `ShadowingAliases`

`Aliases.scala:169` declares `type Label = java.lang.String` at the same level as the *shadowed* names (`Int`, `Float`, `Boolean`). Other Scala types — `scala.Char`, `scala.Float`, `scala.Array`, etc. — are only available through `gen.*` (`Aliases.scala:184-197`). The asymmetry seems to exist because `String` is shadowed and there's no other way to get a host string for a name in `Reg[I32](0, "regName")`. But the same argument applies to other Scala types in some contexts.

**Spec question.** Is `Label` a one-off promoted name (justified by the `String → Text` shadowing being more disruptive than other primitives), or should other Scala types get equivalent shortcuts? For the Rust port, the convention should probably be a single `gen` namespace for *all* Scala-native escapes.

Source: `src/spatial/lang/Aliases.scala:168-169, 184-197`.
Blocked by: —
Status: open
Resolution: (empty)

## Q-lang-06 — Empty `argon.lang.ShadowingAliases` — extension hook or vestigial?

Argon defines its own `ShadowingAliases` trait (parallel to its `InternalAliases` and `ExternalAliases`) but it is empty (or near-empty). Spatial's `ShadowingAliases` extends `argon.lang.ExternalAliases` indirectly (via `InternalAliases extends argon.lang.ExternalAliases`, `Aliases.scala:7`), not argon's `ShadowingAliases`.

**Spec question.** Is argon's empty `ShadowingAliases` an intentional extension point (left empty so downstream DSLs like Spatial fill it via their own trait, as Spatial does with its own `ShadowingAliases`), or vestigial scaffolding from an earlier design? If intentional, what is the convention for downstream DSLs to layer their shadowing on top? If vestigial, can it be deleted?

Source: `argon/src/argon/lang/Aliases.scala`, `src/spatial/lang/Aliases.scala:7, 156`.
Blocked by: —
Status: open
Resolution: (empty)
