---
type: open-questions
date_started: 2026-04-25
---

# Infrastructure Open Questions

## Q-inf-01 -- [2026-04-25] Is `brokenByRetimeGate` meant to be part of the modeling API?

The requested spec list names `brokenByRetimeGate` with top-level modeling APIs, but source shows it is a nested helper inside `findAccumCycles`. Confirm whether the HLS-facing spec should expose it as a conceptual API or keep it documented as an internal guard.

Source: src/spatial/util/modeling.scala:144-180
Blocked by: HLS retiming design
Status: open
Resolution:

## Q-inf-02 -- [2026-04-25] Which area analyzer should infrastructure docs name as the active modeling caller?

The request listed `AreaAnalyzer` as a caller, but `src/spatial/traversal/AreaAnalyzer.scala` appears commented while `src/spatial/dse/DSEAreaAnalyzer.scala` actively imports and calls modeling helpers. Confirm whether future specs should use `DSEAreaAnalyzer` as the active area-analysis caller.

Source: src/spatial/traversal/AreaAnalyzer.scala:1-180; src/spatial/dse/DSEAreaAnalyzer.scala:1-240
Blocked by: Area/modeling ownership cleanup
Status: open
Resolution:

## Q-inf-03 -- [2026-04-25] What is the intended coverage boundary for the Scala executor?

`ControlExecutor.scala` and the fringe executor cover many controller and DRAM-transfer cases, while `OpResolver` handles local ops via mix-ins. Confirm which IR nodes are expected to be executable under `--scalaExec` and whether unimplemented resolver cases are acceptable as simulator limitations.

Source: src/spatial/executor/scala/ControlExecutor.scala:16-1069; src/spatial/executor/scala/resolvers/OpResolver.scala:43-56
Blocked by: Scala executor maintenance status
Status: open
Resolution:

## Q-inf-04 -- [2026-04-25] Should `ControlPrimitiveMix` be an error issue or a bug issue?

The issue subclass overrides `onUnresolved` but calls `bug`, unlike the other requested issue subclasses that call `error(ctx, ...)`. Decide whether this is intentional compiler-invariant reporting or should be normalized to an error-style unresolved issue.

Source: src/spatial/issues/ControlPrimitiveMix.scala:6-14; argon/src/argon/static/Printing.scala:80-93
Blocked by: Diagnostics policy
Status: open
Resolution:

## Q-inf-05 -- [2026-04-25] Should HLS reports preserve `Memories.report` and `Retime.report` shapes?

`MemoryReporter` and `RetimeReporter` produce Spatial-specific text reports. For an HLS rewrite, decide whether to preserve these exact reports for compatibility or emit HLS-native summaries for array partitioning, pipeline II, and delay-line insertion.

Source: src/spatial/report/MemoryReporter.scala:13-108; src/spatial/report/RetimeReporter.scala:10-65
Blocked by: HLS diagnostics design
Status: open
Resolution:

## Q-inf-06 -- [2026-04-25] Where are raised issues removed or discharged?

`raiseIssue` adds to `state.issues`, and `Compiler.runPass` escalates issues that persist across a pass boundary. The requested files do not show the resolution/removal path. Confirm which pass or helper clears resolved Spatial issues.

Source: argon/src/argon/static/Printing.scala:16-16; argon/src/argon/Compiler.scala:84-95
Blocked by: Full issue lifecycle read
Status: open
Resolution:
