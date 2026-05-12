---
type: "research"
decision: "D-03"
angle: 2
---

## Finding

Current Spatial behavior is frontend rejection, not an alternate loop or early-exit semantics. The Forge control layer exposes virtualization hooks for `__return`, `__whileDo`, and `__doWhile`, and its comments describe `@staged` as rewriting source control constructs to such hook calls when the DSL provides them (forge/src/forge/EmbeddedControls.scala:14-31, forge/src/forge/EmbeddedControls.scala:48-52). Spatial then overrides those hooks with diagnostics only: `__return` reports "return is not yet supported within spatial applications"; `__whileDo` reports "while loops are not yet supported within spatial applications"; `__doWhile` reports "do while loops are not yet supported within spatial applications" (src/spatial/lang/api/SpatialVirtualization.scala:103-113).

I did not find a Rust frontend under the given source root during this pass, so the Rust/HLS conclusion is a port-policy inference: preserving Spatial means rejecting these constructs before HLS emission; giving them HLS-visible behavior would be a deliberate new semantics choice (unverified).

## Diagnostic Mechanics

The common idiom is `error(ctx, message)` followed by `error(ctx)`. The first call logs to the debug log when enabled, prints a user-facing error through `state.out.error(ctx, msg)`, and increments `state.errors` unless `noError = true` is passed (argon/src/argon/static/Printing.scala:71-77). The second call is not another counted error: `error(ctx)` delegates to `error(ctx, showCaret = true)`, which logs/prints source context but does not call `state.logError()` (argon/src/argon/static/Printing.scala:66-70). The terminal printer formats `error(ctx, x)` as `file:line: message`, while `error(ctx, showCaret = true)` prints the captured source line and a caret at `ctx.column` when `ctx.content` is present (utils/src/utils/implicits/terminal.scala:24-30). `SrcCtx` stores `file`, `line`, `column`, optional source `content`, and previous contexts, so diagnostics have enough data for this two-part message plus caret pattern (forge/src/forge/SrcCtx.scala:5-12).

For unsupported `while` and `return`, this means one counted compiler error per rejected construct, plus a source-line/caret companion print. The diagnostic is hard, but it is not thrown immediately from `error(...)` itself.

## Stop Mechanics

Errors stop compilation at compiler checkpoints. `State` owns the error counter, `hadErrors` is `errors > 0`, and `logError()` increments the counter (argon/src/argon/State.scala:189-192). `Compiler.checkErrors(stage)` throws `CompilerErrors(stage, IR.errors)` when any errors have accumulated (argon/src/argon/Compiler.scala:46-47; argon/src/argon/Error.scala:14-16). During staging, the compiler runs `stageApp(args)`, then immediately checks bugs and errors; the comment explicitly says this exits after staging if errors were found (argon/src/argon/Compiler.scala:100-112). During later passes, `runPass` also checks unresolved issues, bugs, and errors after `t.run(block)` (argon/src/argon/Compiler.scala:81-97).

`CompilerErrors` is handled separately from compiler bugs and unhandled exceptions: `handleException` prints a summary like "`N` errors found during `stage`" and records the failure (argon/src/argon/Compiler.scala:226-233). Completion then reports failed status and exits with code 1 when there is a failure or accumulated errors, except test mode rethrows the failure (argon/src/argon/Compiler.scala:246-300). The testing harness relies on this counter: `IllegalExample` compiles with expected errors and asserts both `IR.hadErrors` and the exact `IR.errors` count (argon/src/argon/DSLTest.scala:263-278).

## Comparison

This is consistent with other Spatial restrictions. Type-mismatched staged variable assignment reports a contextual message and then calls `error(ctx)` for the source caret, just like unsupported `return` and `while` (src/spatial/lang/api/SpatialVirtualization.scala:51-64). Host/accelerator placement restrictions in `FriendlyTransformer` also use the message-plus-caret shape, then add `IR.logError()` before returning an error symbol, so those paths may count more heavily than the syntax hooks while presenting a similar diagnostic style (src/spatial/transform/FriendlyTransformer.scala:84-89, src/spatial/transform/FriendlyTransformer.scala:138-148). `UserSanityChecks` likewise rejects ArgOut reads and ArgIn writes inside `Accel` with a primary message, explanatory text, source caret, and explicit `IR.logError()` (src/spatial/traversal/UserSanityChecks.scala:34-45). Some API-level restrictions are terser: dynamic SRAM dimensions call only `error(ctx, message)`, so they increment once and provide a file/line message without the separate caret call (src/spatial/lang/SRAM.scala:140-172).

## D-03 Implication

The safest compatibility rule is reject-by-default. A Rust/HLS frontend that preserves Spatial should detect `while`, `do while`, and source `return` in the Spatial application subset, report one hard frontend diagnostic with source span/caret, and avoid producing HLS code for those constructs. Lowering them to HLS `while` or C++ `return` would not be preserving current Spatial behavior; it would introduce new user-visible control semantics and should be decided explicitly under D-03 (unverified).
