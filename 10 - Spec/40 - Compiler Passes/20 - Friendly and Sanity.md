---
type: spec
concept: friendly-and-sanity
source_files:
  - "src/spatial/Spatial.scala:68-76"
  - "src/spatial/Spatial.scala:166-176"
  - "src/spatial/transform/FriendlyTransformer.scala:12-207"
  - "src/spatial/transform/TextCleanup.scala:9-20"
  - "src/spatial/traversal/CLINaming.scala:10-35"
  - "src/spatial/traversal/AbstractSanityChecks.scala:6-13"
  - "src/spatial/traversal/UserSanityChecks.scala:13-109"
  - "src/spatial/traversal/CompilerSanityChecks.scala:14-174"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[10 - Flows and Rewrites]]"
  - "[[50 - Pipe Insertion]]"
status: draft
---

# Friendly and Sanity

## Summary

The friendly and sanity passes guard the host/accelerator boundary before the main lowering pipeline gets destructive. `CLINaming` runs immediately after the first printer, `FriendlyTransformer` runs next, `UserSanityChecks` runs after the friendly rewrite, and `CompilerSanityChecks` is reused as `transformerChecks`, `streamChecks`, and `finalSanityChecks` around later phases (`src/spatial/Spatial.scala:68-76`, `src/spatial/Spatial.scala:166-176`, `src/spatial/Spatial.scala:238-239`). The group has two different purposes: `FriendlyTransformer` mutates user-written IR into something more explicit, while the sanity traversals report either user-facing errors or compiler invariant violations (`src/spatial/transform/FriendlyTransformer.scala:12-207`, `src/spatial/traversal/UserSanityChecks.scala:13-109`, `src/spatial/traversal/CompilerSanityChecks.scala:14-174`).

## Pass list and roles

- `CLINaming` traces `ArrayApply(InputArguments(), i)` through up to six consumers to find an argument name and records it in `CLIArgs(ii)` (`src/spatial/traversal/CLINaming.scala:12-30`).
- `FriendlyTransformer` is the first mutating Spatial pass in the chain and wraps host values used inside `AccelScope` with inferred `ArgIn`s, normalizes DRAM dimension values, and rewrites incorrect register host/accelerator access syntax (`src/spatial/Spatial.scala:166-169`, `src/spatial/transform/FriendlyTransformer.scala:17-23`, `src/spatial/transform/FriendlyTransformer.scala:49-75`, `src/spatial/transform/FriendlyTransformer.scala:77-197`).
- `TextCleanup` is optional and runs only under `spatialConfig.textCleanup`; the CLI text describes it as removing nodes with `canAccel=false` from the accelerator block (`src/spatial/Spatial.scala:176`, `src/spatial/Spatial.scala:361-362`, `src/spatial/transform/TextCleanup.scala:9-20`).
- `UserSanityChecks` is enabled unless `allowInsanity` is set and emits warnings/errors for patterns that should be explained to the user, including accelerator reads of host-style `GetReg`, accelerator writes via `SetReg`, zero-step counters, nonconstant register resets, registers created outside `Accel`, stream bus width mismatch, and LUT size mismatch (`src/spatial/Spatial.scala:71`, `src/spatial/traversal/UserSanityChecks.scala:13-28`, `src/spatial/traversal/UserSanityChecks.scala:34-109`).
- `CompilerSanityChecks` is an internal invariant pass: it checks undefined non-block inputs, duplicate statement definitions, host values illegally used in `AccelScope`, type/bit-width invariants, FIFO and SRAM shape invariants, the post-pipe no-primitive-mixed-with-outer-control invariant, and retime-gate ordering (`src/spatial/traversal/CompilerSanityChecks.scala:35-51`, `src/spatial/traversal/CompilerSanityChecks.scala:53-152`).
- `AbstractSanityChecks` supplies the shared `disallowedInputs` helper that rejects host-defined inputs unless `allowSharingBetweenHostAndAccel` accepts the value (`src/spatial/traversal/AbstractSanityChecks.scala:6-13`).

## Algorithms

`CLINaming.traceName` first consults `lhs.name`; if the symbol is unnamed, it recursively scans consumers until depth six, falling back to `[unnamed (line ...)]` only at the root (`src/spatial/traversal/CLINaming.scala:12-22`). The visitor only handles `ArrayApply(Op(InputArguments()), i)`, converts constant indices to integers, and updates `CLIArgs` with the traced name (`src/spatial/traversal/CLINaming.scala:24-32`).

`FriendlyTransformer.argIn` stages `ArgInNew` with a zero reset, calls `setArg(arg, x.unbox)`, and returns `arg.value`; this is the helper used for inferred accelerator inputs (`src/spatial/transform/FriendlyTransformer.scala:17-23`). On `AccelScope`, the pass collects `block.nestedInputs`, drops remote memories and values already mapped in `addedArgIns`, keeps bit-typed inputs, appends `(original -> inferred ArgIn)` pairs, and reruns the scope under `isolateSubstWith` so accelerator uses see the inferred argument value (`src/spatial/transform/FriendlyTransformer.scala:49-58`). On `DRAMHostNew`, it deduplicates dimensions with `dims.distinct`, preserves dimensions that are already `ArgIn`, `HostIO`, or constants, reuses existing `dimMapping`, and creates a new inferred `ArgIn` for the remaining dimension values (`src/spatial/transform/FriendlyTransformer.scala:64-75`).

The same pass also lifts common `GetReg`, `RegRead`, `RegWrite`, and `SetReg` misuse. Outside hardware, host reads of `ArgIn` or `HostIO` try `extract`, which can replace the read with the most recent write when the ancestry check allows it, while missing writes warn and return zero (`src/spatial/transform/FriendlyTransformer.scala:25-46`, `src/spatial/transform/FriendlyTransformer.scala:91-119`). Inside hardware, host-style `GetReg` emits a warning and rewrites to `reg.value`; inside hardware, host-style `SetReg` emits a warning and rewrites to `reg := f(data)` for `HostIO`, `ArgOut`, and ordinary registers, while `ArgIn` writes are rejected (`src/spatial/transform/FriendlyTransformer.scala:77-102`, `src/spatial/transform/FriendlyTransformer.scala:164-197`). `RegWrite` similarly records `mostRecentWrite`, rewrites host-side `ArgIn` and `HostIO` writes to `setArg`, rejects host-side `ArgOut` writes, and rejects accelerator-side `ArgIn` writes (`src/spatial/transform/FriendlyTransformer.scala:128-161`).

`TextCleanup` is intentionally small: it enters `AccelScope`, and any `DSLOp` seen inside accelerator scope with `canAccel == false` is replaced with `Invalid` (`src/spatial/transform/TextCleanup.scala:10-17`). This is why the pass is optional; it removes text/print-style helpers rather than proving a structural invariant (`src/spatial/Spatial.scala:176`, `src/spatial/Spatial.scala:361-362`).

`UserSanityChecks` is direct pattern matching. It treats `GetReg` inside hardware as "reading ArgOuts within Accel" and `SetReg` inside hardware as "writing ArgIn within Accel" errors after the friendly pass has had the chance to rewrite friendlier cases (`src/spatial/traversal/UserSanityChecks.scala:34-47`). It warns when counter parallelization exceeds a statically computed trip count, errors on zero counter step, errors when `RegNew` reset data is not fixed bits, and errors when `RegNew` appears outside hardware (`src/spatial/traversal/UserSanityChecks.scala:64-89`). Stream bus width checks compare element bit width against the bus bit width and warn in either direction (`src/spatial/traversal/UserSanityChecks.scala:17-28`, `src/spatial/traversal/UserSanityChecks.scala:91-92`).

`CompilerSanityChecks` tracks `nestedScope`, `visitedStms`, and the current parent. On each statement, it computes `rhs.nonBlockSymInputs`, removes scoped inputs and vector constants, and reports undefined values; it also reports duplicate definitions before adding `rhs.binds + lhs` to scope (`src/spatial/traversal/CompilerSanityChecks.scala:27-51`). For `AccelScope`, it calls `disallowedInputs(stms, inputs, allowArgInference = true)`, so bits may be legal if arg inference is allowed, but other host-defined values produce compiler bugs with the first accelerator use location (`src/spatial/traversal/CompilerSanityChecks.scala:53-67`, `src/spatial/metadata/control/package.scala:1104-1114`). After pipe insertion flips `allowPrimitivesInOuterControl` false, the compiler check raises `ControlPrimitiveMix` when an outer controller block contains both control statements and non-transient primitives (`src/spatial/traversal/CompilerSanityChecks.scala:115-126`, `src/spatial/transform/PipeInserter.scala:317-321`).

## Metadata produced/consumed

`CLINaming` writes global `CLIArgs` names; duplicate names at the same index are concatenated by the `CLIArgs.update` helper (`src/spatial/traversal/CLINaming.scala:24-30`, `src/spatial/metadata/CLIArgs.scala:19-33`). `FriendlyTransformer` produces new `ArgInNew` nodes and substitutions but does not define a persistent analysis metadata record; it relies on control metadata such as `isRemoteMem`, `isArgIn`, `isHostIO`, and `isArgOut` (`src/spatial/transform/FriendlyTransformer.scala:49-75`, `src/spatial/transform/FriendlyTransformer.scala:91-124`). `CompilerSanityChecks` consumes flow metadata including `blk`, `parent`, `isOuterControl`, `isPrimitive`, `isTransient`, `fullDelay`, and retime-gate markers to validate postconditions rather than to produce new metadata (`src/spatial/traversal/CompilerSanityChecks.scala:27-51`, `src/spatial/traversal/CompilerSanityChecks.scala:115-152`).

## Invariants established

Before the first lowering round, arbitrary bit values referenced inside `AccelScope` should have explicit `ArgIn` substitutions unless they are remote memories or already mapped (`src/spatial/transform/FriendlyTransformer.scala:49-58`). DRAM dimension values are deduplicated through `dimMapping`, which prevents repeated inferred argument creation for the same dimension symbol (`src/spatial/transform/FriendlyTransformer.scala:64-75`). User-facing errors should catch obvious illegal boundary operations before structural lowering and before pipe insertion create less recognizable IR (`src/spatial/Spatial.scala:168-176`, `src/spatial/traversal/UserSanityChecks.scala:34-109`). After pipe insertion, the compiler check enforces that outer-control bodies are no longer mixed primitive/control blocks (`src/spatial/Spatial.scala:190`, `src/spatial/traversal/CompilerSanityChecks.scala:115-126`).

## HLS notes

HLS status is **rework**. The diagnostics transfer conceptually, but the friendly rewrite is Spatial-specific because it stages `ArgInNew`, calls `setArg`, and rewrites `RegRead`/`RegWrite` syntax around Spatial's host/accelerator split (`src/spatial/transform/FriendlyTransformer.scala:17-23`, `src/spatial/transform/FriendlyTransformer.scala:91-161`). A Rust+HLS front end can preserve the invariant by making kernel arguments explicit during type checking instead of staging inferred `ArgIn` nodes. The compiler checks should remain as hard assertions, especially undefined input detection and the post-pipe outer-control mix check (`src/spatial/traversal/CompilerSanityChecks.scala:35-67`, `src/spatial/traversal/CompilerSanityChecks.scala:115-126`).

## Open questions

- Q-pp-10 - whether `TextCleanup` should remain a mutating compiler pass or become a frontend/debug-mode filter in an HLS implementation.
