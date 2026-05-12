---
type: spec
concept: Argon Rewrites and Flows
source_files:
  - "argon/src/argon/Rewrites.scala:8-59"
  - "argon/src/argon/Flows.scala:7-52"
  - "argon/src/argon/Op.scala:69-74"
  - "argon/src/argon/State.scala:65-70"
  - "argon/src/argon/static/Staging.scala:77-78"
  - "argon/src/argon/static/Staging.scala:80-153"
  - "argon/src/argon/static/Staging.scala:168-192"
  - "argon/src/argon/Compiler.scala:100-108"
  - "argon/src/argon/Compiler.scala:162-194"
  - "argon/src/argon/Compiler.scala:277-282"
  - "forge/src/forge/tags/rewrite.scala:33-64"
  - "forge/src/forge/tags/flow.scala:27-53"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[40 - Metadata Model]]"
  - "[[50 - Staging Pipeline]]"
  - "[[90 - Transformers]]"
status: draft
---

# Argon Rewrites and Flows

## Summary

Argon has two staging-time extension registries: `Rewrites`, which may replace an op with an already staged value before the op is registered, and `Flows`, which runs ordered side-effecting dataflow callbacks after a new symbol has been created and annotated. `State` allocates one `Rewrites` and one `Flows` registry per compiler state (`argon/src/argon/State.scala:65-70`). `Staging.rewrite(op)` delegates to `state.rewrites.apply(op)`, and `Staging.runFlows(sym, op)` delegates to `state.flows.apply(sym, op)` (`argon/src/argon/static/Staging.scala:77-78`). The compiler exposes empty `flows()` and `rewrites()` hooks and calls them during `init` after CLI and settings processing (`argon/src/argon/Compiler.scala:162-194`).

## Syntax or API

`Rewrites` stores `RewriteRule = PartialFunction[(Op[_],SrcCtx,State),Option[Sym[_]]]` (`argon/src/argon/Rewrites.scala:15-17`). It has an exact-class registry `rules: HashMap[Class[_], ArrayBuffer[RewriteRule]]`, a global rule buffer, and a `names` set that suppresses duplicate registration by name (`argon/src/argon/Rewrites.scala:20-31`; `argon/src/argon/Rewrites.scala:35-40`). `add[O <: Op[_]]` uses a `Manifest` runtime class as the key, while `addGlobal` appends to the global buffer (`argon/src/argon/Rewrites.scala:18-22`; `argon/src/argon/Rewrites.scala:30-40`).

`Flows` stores `ArrayBuffer[(String, PartialFunction[(Sym[_],Op[_],SrcCtx,State),Unit])]` and a `names` set (`argon/src/argon/Flows.scala:15-18`). `add` appends, `prepend` inserts at the front, and `remove` deletes the first named entry and removes that name from the set (`argon/src/argon/Flows.scala:21-34`). `save` creates a new `Flows` object and copies the rule buffer and name set, while `restore` replaces the active buffer and set with a saved registry (`argon/src/argon/Flows.scala:43-52`). `withFlow(name, flow, prepend)(scope)` builds a total flow partial function over `(lhs, _, _, _)`, saves the registry, registers the temporary rule, runs `scope`, and restores the saved registry (`argon/src/argon/static/Staging.scala:184-192`).

## Semantics

Rewrites run at register step 1, before alias extraction, effect computation, CSE lookup, symbol creation, consumer registration, immediate flow, registered flows, and alias checking (`argon/src/argon/static/Staging.scala:80-153`). If `rewrite(op)` returns `Some(s)`, `register` returns `s` directly and the remaining registration steps do not run for the original op (`argon/src/argon/static/Staging.scala:102-105`). If it returns `None`, staging computes aliases and effects, checks the CSE cache, creates a symbol, registers metadata, and runs flows (`argon/src/argon/static/Staging.scala:106-150`).

Rewrite dispatch is three-tiered. `Rewrites.apply` first checks the op's own `op.rewrite`, then class-specific rules from `rules.getOrElse(op.getClass, Nil)`, then global rules (`argon/src/argon/Rewrites.scala:50-53`). The default `Op.rewrite` is `null.asInstanceOf[R]`, so `Option(op.rewrite)` is empty unless a node overrides it (`argon/src/argon/Op.scala:69-74`; `argon/src/argon/Rewrites.scala:50-52`). `applyRule` accepts only `Some(s)` values whose `s.tp <:< Type[A]`; if a rule returns `Some(s)` with the wrong type, it returns `None` rather than warning or throwing (`argon/src/argon/Rewrites.scala:42-47`). This is the rejection mode: wrong-typed rewrites are silently skipped by the registry, not surfaced as compiler errors (`argon/src/argon/Rewrites.scala:42-47`).

Flows run later in the same `register` call. The staging comment labels step 7 as immediate metadata and step 8 as registered `@flow` passes (`argon/src/argon/static/Staging.scala:88-91`). The code executes `flowImmediate(sym)` first, then `runFlows(sym,op)` (`argon/src/argon/static/Staging.scala:134-140`). `stage(op)` supplies an immediate flow that sets `t.ctx = ctx`, while `stageWithFlow(op)(flow)` sets `ctx` and then executes the caller's flow callback before registered flows (`argon/src/argon/static/Staging.scala:168-182`). This is the source-visible "deferred" ordering: registered flows are deferred until after effects, aliases, consumers, and immediate flow, but before logging and `checkAliases` (`argon/src/argon/static/Staging.scala:124-148`).

`Flows.apply` evaluates rules in buffer order and calls a rule only when `rule.isDefinedAt(tuple)` is true; the body is wrapped in `instrument(name){ ... }` for per-flow timing (`argon/src/argon/Flows.scala:36-41`). Because `prepend` inserts at the head and `add` appends at the tail, scoped transfer flows that pass `prepend = true` run before already registered flows (`argon/src/argon/Flows.scala:21-29`; `argon/src/argon/transform/Transformer.scala:111-134`). The compiler dumps aggregate flow instrumentation to `flows.log` when debug logging is enabled (`argon/src/argon/Compiler.scala:277-282`).

## Implementation

The `@rewrite` macro emits a `PartialFunction[(Op[_],SrcCtx,State),Option[Sym[_]]]` that casts `__op` to the user parameter type, installs implicit `ctx` and `state`, converts the user's match into `PartialFunction[Op[_],Sym[_]]`, and returns `Some(func.apply(...))` only when the user PF is defined (`forge/src/forge/tags/rewrite.scala:33-56`). It registers with `IR.rewrites.add[Type]` when the parameter type is not textual `Op[...]`, otherwise with `IR.rewrites.addGlobal` (`forge/src/forge/tags/rewrite.scala:57-64`). The exact-class registry means local rules are selected by `op.getClass`, not by subtype search (`argon/src/argon/Rewrites.scala:28`; `argon/src/argon/Rewrites.scala:35-40`).

The `@flow` macro enforces one explicit parameter list of `(lhs: Sym[_], rhs: Op[_])` after `@api` has injected implicit `SrcCtx` and `State` (`forge/src/forge/tags/flow.scala:27-36`). It uses `isWildcardType` to require wildcard type arguments for `Sym` and `Op` (`forge/src/forge/tags/flow.scala:32-36`; `utils/src/utils/tags/MacroUtils.scala:61-64`). The generated PF binds the tuple fields to user names, installs implicit `ctx` and `state`, runs the user body, and registers with `IR.flows.add(name, pf)` (`forge/src/forge/tags/flow.scala:40-53`).

## Interactions

Rewrites interact with effects by avoiding them: a successful rewrite returns before `computeEffects(op)` is called (`argon/src/argon/static/Staging.scala:102-110`). Flows interact with metadata by running after `sym.effects`, `sym.deepAliases`, `sym.shallowAliases`, reverse aliases, and `Consumers` have been installed (`argon/src/argon/static/Staging.scala:124-140`). Transformer metadata transfer relies on this ordering by installing transfer callbacks as immediate or prepended flows (`argon/src/argon/transform/Transformer.scala:111-134`; `argon/src/argon/static/Staging.scala:134-140`).

## HLS notes

The behavior ports cleanly as two ordered registries: a rewrite registry returning optional replacement ids before node insertion, and a flow registry running side-effecting callbacks after metadata initialization (inferred, unverified). The required compatibility point is the silent type rejection in `applyRule`, because a stricter implementation would change which malformed rewrite rules are observable (`argon/src/argon/Rewrites.scala:42-47`).

## Open questions

- See [[open-questions-argon-supplemental#Q-arg-03]]: `withFlow` restores the registry only after normal scope completion; there is no `try/finally` in the implementation.
- See [[open-questions-argon-supplemental#Q-arg-04]]: the source has no separate end-of-pass deferred-flow queue beyond the registered-flow step at the end of `register`.
