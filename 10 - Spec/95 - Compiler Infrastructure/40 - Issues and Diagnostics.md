---
type: spec
concept: "Issues and Diagnostics"
source_files:
  - "argon/src/argon/Issue.scala:1-20"
  - "argon/src/argon/Compiler.scala:80-96"
  - "argon/src/argon/static/Printing.scala:16-18"
  - "argon/src/argon/static/Printing.scala:61-78"
  - "argon/src/argon/State.scala:189-202"
  - "src/spatial/issues/AmbiguousMetaPipes.scala:1-44"
  - "src/spatial/issues/ControlPrimitiveMix.scala:1-15"
  - "src/spatial/issues/PotentialBufferHazard.scala:1-28"
  - "src/spatial/issues/UnbankableGroup.scala:1-20"
  - "src/spatial/metadata/control/package.scala:1292-1325"
  - "src/spatial/traversal/CompilerSanityChecks.scala:115-124"
  - "src/spatial/traversal/banking/MemoryConfigurer.scala:626-676"
  - "src/spatial/traversal/banking/FIFOConfigurer.scala:62-102"
source_notes:
  - "[[open-questions-infra]]"
hls_status: clean
depends_on:
  - "[[20 - Friendly and Sanity]]"
  - "[[70 - Banking]]"
  - "[[30 - Memory]]"
status: draft
---

# Issues and Diagnostics

## Summary

`argon.Issue` is the compiler's deferred diagnostic mechanism. The base class describes issues as problems that must be resolved by the end of the pass after they were raised; otherwise they become errors `argon/src/argon/Issue.scala:5-19`. Spatial defines several issue subclasses for cases where a pass can detect a structural problem but a later pass may still resolve or discharge it. This entry covers four Spatial issues: `AmbiguousMetaPipes`, `ControlPrimitiveMix`, `PotentialBufferHazard`, and `UnbankableGroup`.

## API

The base API is small. `Issue` is an abstract class requiring `Product`; `name` is `productPrefix`, and `onUnresolved(traversal)` emits an unresolved-issue error and calls `state.logError()` `argon/src/argon/Issue.scala:10-19`. `raiseIssue(issue)` appends an issue to `state.issues` `argon/src/argon/static/Printing.scala:16-16`. `Compiler.runPass` snapshots `issuesBefore`, runs the pass, intersects with `issuesAfter`, and calls `onUnresolved` on any issue still present after the next traversal boundary `argon/src/argon/Compiler.scala:81-95`. `State` stores `errors`, `hadErrors`, `logError`, and the active `issues` set `argon/src/argon/State.scala:189-202`.

Spatial issue case classes extend `Issue` and override `onUnresolved`. Three of the four call `error(ctx, ...)` in their first diagnostic line, which increments `state.errors` through `Printing.error(ctx, x, noError = false)` `argon/src/argon/static/Printing.scala:71-77`. `ControlPrimitiveMix` is the exception: it calls `bug(...)`, not `error(...)`, so it reports a compiler bug path rather than a normal user error path `src/spatial/issues/ControlPrimitiveMix.scala:6-14`. This differs from the prompt's blanket "increments `state.hadErrors`" wording; see [[open-questions-infra#Q-inf-04]].

Immediate `error` calls and deferred `Issue`s therefore have different lifetimes. An immediate `error(ctx, message)` increments the error count as soon as it is called, while an issue only becomes fatal if it remains in `state.issues` across the compiler pass boundary checked by `Compiler.runPass` `argon/src/argon/static/Printing.scala:71-77` `argon/src/argon/Compiler.scala:84-95`.

## Implementation

`AmbiguousMetaPipes(mem, mps)` reports a memory used across multiple pipelines and says hierarchical buffering is disallowed. It emits the memory context, each first/conflicting pipeline context, and debug details for pipeline/access pairs `src/spatial/issues/AmbiguousMetaPipes.scala:7-42`. It is constructed by `computeMemoryBufferPorts` when `findAllMetaPipes` finds more than one metapipe LCA for a memory's readers/writers `src/spatial/metadata/control/package.scala:1292-1302`.

`PotentialBufferHazard(mem, bad)` reports a likely buffer hazard and tells the user to choose `.buffer` or `.nonbuffer`. It prints the memory and each bad writer/access port pair `src/spatial/issues/PotentialBufferHazard.scala:7-27`. It is also constructed in `computeMemoryBufferPorts`: after port distances are normalized, writers with a positive buffer port become `bufferHazards`, and a hazard issue is returned unless the memory is already write-buffered or non-buffered `src/spatial/metadata/control/package.scala:1315-1320`.

`ControlPrimitiveMix(parent, ctrl, prim)` reports an illegal mix of child controls and primitives under an outer control. `CompilerSanityChecks` raises it when `allowPrimitivesInOuterControl` is false, the current node is outer control, a block contains non-branch controls, and that same block contains non-transient primitives `src/spatial/traversal/CompilerSanityChecks.scala:115-124`.

`UnbankableGroup(mem, reads, writes)` reports access matrices that banking could not legally place into groups. `MemoryConfigurer` returns it when banking finds no viable banking schemes, then later raises any `Left(issue)` produced during read-group or write-group merging `src/spatial/traversal/banking/MemoryConfigurer.scala:626-676` `src/spatial/traversal/banking/MemoryConfigurer.scala:796-815`. `FIFOConfigurer` returns the same issue when FIFO read or write groups are concurrent or when no banking option exists `src/spatial/traversal/banking/FIFOConfigurer.scala:62-102`.

The issue payloads are deliberately diagnostic-rich. `AmbiguousMetaPipes` stores the conflicting metapipe map, `PotentialBufferHazard` stores bad access/port pairs, and `UnbankableGroup` stores the read/write `AccessMatrix` sets that failed banking. Those payloads let `onUnresolved` point at both the memory declaration and the specific access/control contexts rather than reporting only the pass that failed `src/spatial/issues/AmbiguousMetaPipes.scala:7-42` `src/spatial/issues/PotentialBufferHazard.scala:7-27` `src/spatial/issues/UnbankableGroup.scala:7-19`.

## Interactions

Issue lifetimes span passes: a pass raises an issue into `state.issues`, a later pass may remove or avoid preserving it (not shown in the requested files), and `Compiler.runPass` escalates any issue that persists across the pass boundary `argon/src/argon/Compiler.scala:84-95`. This makes issues different from immediate `error` calls: they can represent "this must be resolved by later analysis/configuration" rather than "abort now."

## HLS notes

The mechanism is `clean` for HLS as a compiler architecture pattern: deferred diagnostics and structured issue subclasses port directly. The individual Spatial issues remain tied to Spatial banking, buffer, and controller invariants, so an HLS implementation would need equivalent issue types for array partitioning, buffering, and mixed control/data legality.

## Open questions

See [[open-questions-infra#Q-inf-04]] for the `ControlPrimitiveMix` error-versus-bug mismatch and [[open-questions-infra#Q-inf-06]] for unresolved issue discharge semantics.
