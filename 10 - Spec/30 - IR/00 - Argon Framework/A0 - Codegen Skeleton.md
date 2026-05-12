---
type: spec
concept: Argon Codegen Skeleton
source_files:
  - "argon/src/argon/codegen/Codegen.scala:10-202"
  - "argon/src/argon/codegen/StructCodegen.scala:8-25"
  - "argon/src/argon/codegen/FileDependencies.scala:8-74"
  - "argon/src/argon/static/Printing.scala:19-24"
  - "argon/src/argon/static/Printing.scala:213-225"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[80 - Passes]]"
  - "[[20 - Ops and Blocks]]"
  - "[[90 - Transformers]]"
status: draft
---

# Argon Codegen Skeleton

## Summary

Argon's code generation base is a specialized traversal: `Codegen` extends `Traversal`, sets `recurse` to `Recurse.Never`, and leaves backend traversal of nested blocks under explicit backend control (`argon/src/argon/codegen/Codegen.scala:10-12`). The base trait owns the generated-language identity through abstract `lang` and `ext`, derives an output directory under `config.genDir/lang`, and defaults the entry file to `Main.$ext` (`argon/src/argon/codegen/Codegen.scala:12-16`). The framework-provided process phase opens the entry output stream, emits a header, emits the program entry, emits a footer, and returns the input block unchanged (`argon/src/argon/codegen/Codegen.scala:75-82`). This means codegen passes are compiler passes for lifecycle purposes but are side-effecting printers for output purposes.

## Syntax / API

Every backend must provide at least `lang`, `ext`, and `emitEntry(block)` because those members are abstract or consumed by the base `process` implementation (`argon/src/argon/codegen/Codegen.scala:12-24`, `argon/src/argon/codegen/Codegen.scala:75-80`). Backends commonly override `emitHeader` and `emitFooter` to surround the entry body, while the base defaults are empty methods (`argon/src/argon/codegen/Codegen.scala:21-24`). Backends must also define node-level generation rules by overriding `gen(lhs,rhs)`, because the base implementation throws when generation is enabled and no rule is defined (`argon/src/argon/codegen/Codegen.scala:84-93`).

The quoting API is the shared bridge from Argon IR values to target-language syntax. `remap(tp)` defaults to `tp.typeName`, `quoteConst(tp,c)` is deliberately unimplemented and throws, `named(s,id)` defaults to `x$id` after `nameMap`, and `quote(s)` handles type refs, constants, parameters, bound symbols, node symbols, and error symbols by dispatching on `s.rhs` (`argon/src/argon/codegen/Codegen.scala:35-52`). `quoteOrRemap` handles sequences, arrays, refs, strings, primitive Scala constants, `SrcCtx`, and options, and the `src` string interpolator applies `quoteOrRemap` to interpolated arguments before stripping margins (`argon/src/argon/codegen/Codegen.scala:54-73`). Output indentation and emission are inherited from printing helpers: `emit`, `open`, and `close` write to `state.gen` when `config.enGen` is enabled, and `inGen` temporarily swaps the active generation stream (`argon/src/argon/static/Printing.scala:19-24`, `argon/src/argon/static/Printing.scala:213-225`).

## Semantics

`preprocess` clears old generated files with the backend extension before generation, so a fresh run deletes matching extension files below the backend output directory (`argon/src/argon/codegen/Codegen.scala:17-29`). Since `Codegen.recurse` is `Never`, child blocks are not automatically walked through the traversal recursion hook; backend code calls `gen(block)` or `ret(block)`, and both route to `visitBlock` with an optional return flag available to overrides (`argon/src/argon/codegen/Codegen.scala:10-12`, `argon/src/argon/codegen/Codegen.scala:84-88`). The final `visit(lhs,rhs)` method delegates every statement to `gen(lhs,rhs)`, enforcing a single node-dispatch path for backend rules (`argon/src/argon/codegen/Codegen.scala:89-93`).

`kernel(sym)` is a helper for side files named `${sym}_kernel.$ext` in the backend output directory (`argon/src/argon/codegen/Codegen.scala:201-202`). The base `postprocess` does not add behavior, but mixins such as `StructCodegen` and `FileDependencies` use `postprocess` to emit shared structures and copy resources after the entry file is generated (`argon/src/argon/codegen/Codegen.scala:31-33`, `argon/src/argon/codegen/StructCodegen.scala:22-25`, `argon/src/argon/codegen/FileDependencies.scala:70-73`).

## Implementation

`javaStyleChunk` is the largest helper in the base trait. It accepts weighted statements, a `code_window`, a hierarchy depth, a global block ID, liveness and branch-suffix functions, a type-to-argument renderer, a chunk-state initializer, and a visit rule (`argon/src/argon/codegen/Codegen.scala:107-116`). At hierarchy depth zero, it simply visits every statement in order and returns the incoming block ID (`argon/src/argon/codegen/Codegen.scala:128-131`). At hierarchy depth one, it increments the block ID, partitions statements into windows by accumulated weight, emits `object Block${blockID}Chunker${chunkID}` wrappers, emits a `gen(): Map[String, Any]`, records live escaping symbols in `scoped`, and emits a value that calls each chunk object's `gen()` (`argon/src/argon/codegen/Codegen.scala:132-155`). For hierarchy depths greater than one, it emits a two-level structure: outer `Block...Chunker...` objects contain inner `Block...Chunker...Sub...` objects, each subchunk returns a live-value map, and the outer chunk remaps live names through `scoped` before returning its own map (`argon/src/argon/codegen/Codegen.scala:156-198`).

The stated backend reason to use `javaStyleChunk` is to keep giant generated Scala-like backend bodies below compiler limits (inferred, unverified); the verified mechanism is the source-level split into generated singleton objects, chunk `gen()` methods, live-value maps, and `scoped` remapping (`argon/src/argon/codegen/Codegen.scala:143-152`, `argon/src/argon/codegen/Codegen.scala:177-194`). The helper only implements direct emission, one-level chunking, and a two-level fallback; the comment explicitly asks what happens for blocks larger than `code_window * code_window * code_window`, so deeper splitting is not implemented here (`argon/src/argon/codegen/Codegen.scala:156-158`).

`StructCodegen` is a mixin for backends that need explicit data-structure prelude emission. It tracks `encounteredStructs` from `Struct[_]` type remaps, assigns each new struct a monotonically increasing `structNumber`, delegates non-struct type remaps to the superclass, and requires backend implementations of `structName` and `emitDataStructures` (`argon/src/argon/codegen/StructCodegen.scala:8-21`). Its `postprocess` emits data structures and then delegates to the superclass postprocess, so it runs after normal entry generation (`argon/src/argon/codegen/StructCodegen.scala:22-25`).

`FileDependencies` is the resource-copy mixin. It stores a `dependencies` list, defines `FileDep` and `DirDep`, requires a `/files_list` resource for directory expansion, copies individual resources with `files.copyResource`, expands directory dependencies by filtering `files_list`, and copies all dependencies in `postprocess` (`argon/src/argon/codegen/FileDependencies.scala:8-18`, `argon/src/argon/codegen/FileDependencies.scala:20-39`, `argon/src/argon/codegen/FileDependencies.scala:41-68`, `argon/src/argon/codegen/FileDependencies.scala:70-73`).

## Interactions

`[[80 - Passes]]` supplies the pass lifecycle, logging, timing, and pass-number behavior that codegen inherits. `[[20 - Ops and Blocks]]` supplies the `Block`, `Sym`, `Op`, `Type`, and `Def` cases that `gen`, `quote`, and `remap` consume (`argon/src/argon/codegen/Codegen.scala:35-52`, `argon/src/argon/codegen/Codegen.scala:84-93`). `[[90 - Transformers]]` is adjacent rather than inherited: both transform and codegen passes are run by the same compiler driver, but codegen is intentionally output-side-effecting and returns the original block (`argon/src/argon/codegen/Codegen.scala:75-82`).

## HLS notes

The skeleton is HLS-clean because it is an emitter scaffold, not a hardware semantic. A Rust-native port should keep the abstract hooks, quote/remap split, explicit block generation, struct prelude hook, and dependency-copy hook, but it does not need to preserve Scala singleton-object chunking unless the chosen backend has equivalent compiler limits. The source behavior to preserve is that each backend owns target language naming, target file extension, constants, type remapping, node emission rules, and optional prelude/footer/resource behavior (`argon/src/argon/codegen/Codegen.scala:12-24`, `argon/src/argon/codegen/Codegen.scala:35-73`, `argon/src/argon/codegen/StructCodegen.scala:12-25`, `argon/src/argon/codegen/FileDependencies.scala:66-73`).

## Open questions

- See `[[open-questions-argon-supplemental]]` Q-arg-002: what backend size limits determine `javaStyleChunk`'s `code_window`, and are blocks larger than the implemented two-level chunking expected (`argon/src/argon/codegen/Codegen.scala:156-158`)?
