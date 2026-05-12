---
type: spec
concept: Argon Passes
source_files:
  - "argon/src/argon/passes/Pass.scala:8-75"
  - "argon/src/argon/passes/Traversal.scala:6-50"
  - "argon/src/argon/passes/RepeatedTraversal.scala:5-45"
  - "argon/src/argon/passes/IRPrinter.scala:5-45"
  - "argon/src/argon/Issue.scala:5-20"
  - "argon/src/argon/Compiler.scala:81-98"
  - "argon/src/argon/Compiler.scala:253-282"
  - "argon/src/argon/State.scala:161-165"
  - "argon/src/argon/State.scala:199-201"
  - "argon/src/argon/static/Printing.scala:16-17"
  - "argon/src/argon/static/Printing.scala:234-244"
  - "argon/src/argon/transform/Transformer.scala:20-28"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[50 - Staging Pipeline]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[90 - Transformers]]"
status: draft
---

# Argon Passes

## Summary

Argon's pass layer is the common execution shell for analyses, transformations, printers, and code generators: `Pass` is the base trait, and the source comment explicitly says to extend it directly when a pass does not need graph traversal and to extend `Traversal` otherwise (`argon/src/argon/passes/Pass.scala:8-14`). A pass owns the active `State` through `val IR` and exposes it implicitly as `__IR`, so all staged logging, issue, and metadata helpers inside a pass operate against the same compiler state (`argon/src/argon/passes/Pass.scala:14-18`). The global pass number lives on `State.pass`, with `paddedPass` used for pass-numbered log names and `isStaging` defined as `pass == 0` (`argon/src/argon/State.scala:161-165`).

## Syntax / API

`Pass` provides override points for `shouldRun`, `init`, `execute`, `preprocess`, `process`, and `postprocess`; only `process` is abstract, while `execute` runs the three-stage `preprocess -> process -> postprocess` pipeline (`argon/src/argon/passes/Pass.scala:25-33`, `argon/src/argon/passes/Pass.scala:59-73`). `Pass.run` is final, checks `shouldRun`, increments `state.pass`, installs per-pass verbosity overrides, opens a pass-specific log file, records elapsed wall-clock time into `lastTime` and `totalTime`, and returns the original block unchanged when `shouldRun` is false (`argon/src/argon/passes/Pass.scala:20-24`, `argon/src/argon/passes/Pass.scala:35-57`). `silence()` is a convenience API that disables warning, error, and info output and drops the log level to zero for that pass (`argon/src/argon/passes/Pass.scala:27-32`).

`Traversal` extends `Pass` and introduces `Recurse.Always`, `Recurse.Default`, and `Recurse.Never` as the recursive block traversal modes (`argon/src/argon/passes/Traversal.scala:9-20`). Its `process` implementation delegates to `visitBlock`, and `visitBlock` visits `block.stms` with `visit` under one level of `state.logTab` indentation (`argon/src/argon/passes/Traversal.scala:24-37`). The public extension point for node-specific work is `visit[A](lhs: Sym[A], rhs: Op[A])`, whose default behavior recursively visits child blocks only when `recurse == Default`; the final unary `visit(lhs)` wrapper calls that hook and then recurses into blocks when `recurse == Always` (`argon/src/argon/passes/Traversal.scala:39-48`).

`RepeatableTraversal` is a marker-style traversal with a mutable `converged` flag, and `RepeatedTraversal` wraps a sequence of passes plus optional per-iteration `postIter` passes until every repeatable pass reports convergence or `maxIters` is reached (`argon/src/argon/passes/RepeatedTraversal.scala:5-17`, `argon/src/argon/passes/RepeatedTraversal.scala:27-45`). `IRPrinter` is a concrete traversal whose pass name is `"IR"`, whose `shouldRun` is controlled by its constructor flag, and whose visit rule prints `lhs = rhs`, symbol metadata, bound inputs, and recursively printed blocks (`argon/src/argon/passes/IRPrinter.scala:5-15`, `argon/src/argon/passes/IRPrinter.scala:17-45`).

## Semantics

The pass driver is strict about pass order and error handling: `Compiler.runPass` wraps every pass in `instrument(t.name)`, snapshots `state.issues` before the pass, initializes the pass if needed, calls `t.run(block)`, intersects pre-pass and post-pass issue sets, calls `onUnresolved` for persisting issues, and then checks compiler bugs and errors (`argon/src/argon/Compiler.scala:81-98`). An `Issue` is therefore a one-pass obligation: its source comment states that an issue raised by one pass must be resolved by the end of the next pass, and the default `onUnresolved` reports an error and increments the state's error count (`argon/src/argon/Issue.scala:5-20`). Issues are stored as a `Set[Issue]` on `State`, and `raiseIssue` appends to that set (`argon/src/argon/State.scala:199-201`, `argon/src/argon/static/Printing.scala:16-17`).

Traversal recursion is opt-in at the point of the traversal trait: `Default` lets the pass-specific `visit(lhs,rhs)` run before recursing into child blocks, `Always` makes the final wrapper recurse after the custom visit, and `Never` suppresses the default child-block recursion unless the override calls `visitBlock` itself (`argon/src/argon/passes/Traversal.scala:39-48`). This distinction is why code generators can extend traversal but disable automatic recursion, while analyses can inherit the default recursive walk.

## Implementation

Pass logging is file-scoped: `logFile` is `state.paddedPass + "_" + name + ".log"`, and `run` wraps execution in `withLog(config.logDir, logFile)` (`argon/src/argon/passes/Pass.scala:17-18`, `argon/src/argon/passes/Pass.scala:48-55`). Pass-local timing uses `System.currentTimeMillis` and accumulates milliseconds in floating-point fields, while compiler-wide instrumentation uses `utils.Instrument` through `Compiler`'s private `instrument` value (`argon/src/argon/passes/Pass.scala:35-37`, `argon/src/argon/passes/Pass.scala:49-54`, `argon/src/argon/Compiler.scala:1-12`). Debug builds dump the aggregate profiling report to `9999_Timing.log`, then dump and reset each `Instrumented` instance and the flow-rule instrument (`argon/src/argon/Compiler.scala:253-282`).

`IRPrinter` relies on the shared metadata printing helper: `strMeta(lhs)` prints names, previous names, type, source context, and sorted metadata entries for the symbol (`argon/src/argon/static/Printing.scala:234-244`). Its block printer emits each nested block's effects before traversing that block's statements, so an IR dump includes both node structure and block summaries (`argon/src/argon/passes/IRPrinter.scala:17-26`). One implementation detail to preserve or intentionally change in a port: `RepeatedTraversal.process` maintains a mutable `blk`, but each inner pass currently receives `block` rather than `blk` (`argon/src/argon/passes/RepeatedTraversal.scala:27-40`); see Q-arg-001.

## Interactions

Transformers are ordinary passes: `Transformer` imports `argon.passes.Pass` and extends `Pass with TransformerInterface`, so transformer-specific substitution logic still runs through the same `run`, issue, logging, and timing shell (`argon/src/argon/transform/Transformer.scala:4-5`, `argon/src/argon/transform/Transformer.scala:20-28`). `[[90 - Transformers]]` therefore depends on this entry for lifecycle semantics, while `[[60 - Scopes and Scheduling]]` explains the `Block` inputs that traversals visit.

## HLS notes

The pass abstraction is HLS-clean because it is a compiler-control concept rather than a hardware semantic. A Rust port should keep the same split between a pass shell, a traversal subclass or trait, and an issue-resolution check, while replacing `withLog`, Scala implicits, and mutable `State` access with Rust-native context parameters. The important source-level behaviors to match are pass counter increments, per-pass logs, issue persistence checks, and recursive block traversal modes (`argon/src/argon/passes/Pass.scala:39-57`, `argon/src/argon/Compiler.scala:81-98`, `argon/src/argon/passes/Traversal.scala:39-48`).

## Open questions

- See `[[open-questions-argon-supplemental]]` Q-arg-001: should `RepeatedTraversal` pass the accumulated `blk` to each inner pass, or is the current `pass.run(block)` behavior intentional (`argon/src/argon/passes/RepeatedTraversal.scala:27-40`)?
