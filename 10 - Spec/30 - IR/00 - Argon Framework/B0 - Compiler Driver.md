---
type: spec
concept: Argon Compiler Driver
source_files:
  - "argon/src/argon/Compiler.scala:10-317"
  - "argon/src/argon/DSLApp.scala:1-8"
  - "argon/src/argon/DSLRunnable.scala:5-27"
  - "argon/src/argon/DSLTest.scala:11-334"
  - "argon/src/argon/DSLTestbench.scala:9-31"
  - "argon/src/argon/Error.scala:7-36"
  - "argon/src/argon/Config.scala:5-94"
  - "argon/src/argon/State.scala:216-233"
  - "argon/src/argon/passes/Pass.scala:39-73"
source_notes:
  - "[[argon-framework]]"
hls_status: rework
depends_on:
  - "[[50 - Staging Pipeline]]"
  - "[[60 - Scopes and Scheduling]]"
  - "[[90 - Transformers]]"
status: draft
---

# Argon Compiler Driver

## Summary

The Argon driver is the host-side orchestration layer around staging, pass execution, logging, errors, CLI parsing, and tests. `Compiler` is the central trait: it requires `stageApp(args)` and `runPasses(block)`, provides `stageProgram`, `compileProgram`, `runPass`, the `==>` pass-composition syntax, and the top-level `compile(args)` entry (`argon/src/argon/Compiler.scala:77-132`; `argon/src/argon/Compiler.scala:198-224`; `argon/src/argon/Compiler.scala:304-316`). `DSLApp` turns any compiler into a runnable app with one `main(args) = compile(args)` line (`argon/src/argon/DSLApp.scala:4-7`). `DSLRunnable` supplies the implicit lazy `IR: State`, initializes default log/gen/report directories, sets verbosity, and starts an initial scope that allows global declarations (`argon/src/argon/DSLRunnable.scala:5-20`).

## Syntax or API

The required compiler API is intentionally small: subclasses implement `stageApp(args: Array[String]): Block[_]` and `runPasses[R](b: Block[R]): Block[R]` (`argon/src/argon/Compiler.scala:77-80`). `runPass(t, block)` wraps a pass in instrumentation, checks the `--stop` gate, logs pass names, initializes the pass, executes `t.run(block)`, checks unresolved issues, bugs, and errors, then returns the transformed block (`argon/src/argon/Compiler.scala:81-98`). The `Pass.run` method increments `state.pass`, applies per-pass verbosity overrides, opens the pass log, times execution, and calls `preprocess`, `process`, and `postprocess` through `execute` (`argon/src/argon/passes/Pass.scala:39-73`).

The block-and-pass combinator is `block ==> pass`, `block ==> passSeq`, or `block ==> (cond ? passSeq)` (`argon/src/argon/Compiler.scala:203-224`). The sequence case runs each pass in order, threading the current block through `runPass` (`argon/src/argon/Compiler.scala:205-218`). CLI options are defined with `scopt.OptionParser[Unit]`: verbosity flags, output/log/report paths, naming, `max_cycles`, hidden `--test`, and hidden `--stop` are installed by `defineOpts` (`argon/src/argon/Compiler.scala:134-157`). `init(args)` partitions `-D` directives, constructs the `scopt` parser, calls `defineOpts`, parses non-directive args, calls `settings`, normalizes output directories, then calls `flows()` and `rewrites()` (`argon/src/argon/Compiler.scala:165-195`).

Application-level directives are separate from `scopt`: `init` stores `-Dkey=value` pairs in the lowercase `directives` map, and `define(name, default)` parses that map into primitive Scala types or reports a compiler error when parsing fails (`argon/src/argon/Compiler.scala:18-44`; `argon/src/argon/Compiler.scala:165-176`). This makes app-defined parameters visible during staging without adding every parameter to the command-line parser (`argon/src/argon/Compiler.scala:18-44`; `argon/src/argon/Compiler.scala:170-176`).

## Semantics

`compile(args)` resets the compiler instrument, runs `execute(args)` inside a broad catch, stores the translated failure from `handleException`, and then calls `complete(failure)` (`argon/src/argon/Compiler.scala:307-316`). `execute` calls `init(args)` and `compileProgram(args)` (`argon/src/argon/Compiler.scala:198-201`). `compileProgram` checks staging errors, logs compile metadata, deletes old log files, stages the app with `stageProgram`, runs `runPasses`, and calls `postprocess` (`argon/src/argon/Compiler.scala:119-132`). `stageProgram` logs registered rewrite and flow names and then invokes `stageApp(args)` inside `0000_Staging.log` (`argon/src/argon/Compiler.scala:100-112`).

Exception handling is explicit but asymmetric. `CompilerBugs`, `CompilerErrors`, and `RequirementFailure` get dedicated cases in `handleException` (`argon/src/argon/Compiler.scala:226-238`). All other throwables, including `EarlyStop` from `runPass` unless a subclass intercepts it, go through `onException`, get wrapped in `UnhandledException`, and are returned as failures (`argon/src/argon/Compiler.scala:239-244`; `argon/src/argon/Compiler.scala:81-83`). The exception ADTs are defined in `Error.scala`: `UnhandledException`, `EarlyStop`, `CompilerErrors`, `CompilerBugs`, `RequirementFailure`, `MissingDataFolder`, `CompilerTimeout`, and `BackendTimeout` (`argon/src/argon/Error.scala:7-36`). `complete` prints warnings, chooses a success/failure tag from `IR.hadBugs`, `IR.hadErrors`, and `failure`, stops memory logging, dumps profiling data in debug mode, closes streams, throws in test mode on failure, and otherwise exits with code 1 on failure (`argon/src/argon/Compiler.scala:246-301`).

## Implementation

`DSLRunnable` is stateful by construction. Its `IR` is a `final protected[argon] implicit lazy val`, so an app instance gets one lazy `State` object unless a subclass adds extra reset logic (`argon/src/argon/DSLRunnable.scala:8-20`). The TODO at `DSLRunnable.scala:8` asks how to support multiple compile runs and preserve globals, and `Config.reset()` only resets verbosity flags, not paths, testing flags, naming, or `max_cycles` (`argon/src/argon/DSLRunnable.scala:8`; `argon/src/argon/Config.scala:75-81`). `State.reset()` does reset ids, bundles, globals, pass counter, logs, streams, counts, and issues, but it delegates config reset to the limited `Config.reset()` implementation (`argon/src/argon/State.scala:216-233`; `argon/src/argon/Config.scala:75-81`). Thread safety is therefore not guaranteed by these files, because mutable compiler state and config live on the shared `State` (`argon/src/argon/DSLRunnable.scala:8-20`; `argon/src/argon/State.scala:216-233`).

`DSLTest` builds on `Compiler` with compile/runtime/model argument lists, staged `assert`, unstaged `require`, and a `Backend` abstraction (`argon/src/argon/DSLTest.scala:11-75`; `argon/src/argon/DSLTest.scala:81-115`). `Backend.compile` imports `scala.concurrent.ExecutionContext.Implicits.global`, runs `init`, directory overrides, and `compileProgram` inside a blocking `Future`, and waits with `Await.result(..., Duration(makeTimeout, "sec"))` (`argon/src/argon/DSLTest.scala:133-153`). `Backend.command` uses the same global execution context for subprocess `make`, `run`, or `model` commands and kills the subprocess in `finally` if it is still alive (`argon/src/argon/DSLTest.scala:167-209`). Compile timeout produces `CompileError(CompilerTimeout(...))`, while backend command timeout records an error string rather than constructing `BackendTimeout` (`argon/src/argon/DSLTest.scala:156-163`; `argon/src/argon/DSLTest.scala:200-203`; `argon/src/argon/Error.scala:30-36`).

`DSLTestbench` is the lighter IR-checking helper. It provides `req`, `reqOp`, `reqWarn`, and `checks()`, where `reqOp` verifies an op class with `utils.isSubtype`, `reqWarn` captures `state.out` through `CaptureStream`, and the trait registers a single test that calls `checks()` (`argon/src/argon/DSLTestbench.scala:9-31`).

## Interactions

The driver is the point where rewrite and flow registration become visible to staging: `init` calls `flows()` and `rewrites()`, and `stageProgram` logs the names held by `IR.rewrites.names` and `IR.flows.names` before calling `stageApp` (`argon/src/argon/Compiler.scala:100-108`; `argon/src/argon/Compiler.scala:162-195`). Passes are responsible for all post-staging transformation and analysis, and the `==>` syntax is only a thin wrapper around `runPass` (`argon/src/argon/Compiler.scala:203-224`).

## HLS notes

This driver is host infrastructure rather than IR semantics. A reimplementation can preserve the staging/pass/check ordering, but the Scala-specific pieces need redesign: `scopt`, broad `Throwable` handling, singleton lazy state, mutable global config, blocking Futures, and `ExecutionContext.Implicits.global` are JVM/Scala contracts, not HLS contracts (`argon/src/argon/Compiler.scala:134-157`; `argon/src/argon/DSLRunnable.scala:8-20`; `argon/src/argon/DSLTest.scala:133-153`; `argon/src/argon/DSLTest.scala:167-209`).

## Open questions

- See [[open-questions-argon-supplemental#Q-arg-05]]: multiple `compile` runs share a lazy `IR`, and `Config.reset()` is incomplete.
- See [[open-questions-argon-supplemental#Q-arg-06]]: `DSLTest` uses `ExecutionContext.Implicits.global` for blocking compilation and subprocess waits.
