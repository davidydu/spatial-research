---
type: spec
concept: Argon Metadata Model
source_files:
  - "argon/src/argon/Data.scala:8-132"
  - "argon/src/argon/Ref.scala:123-126"
  - "argon/src/argon/Mirrorable.scala:5-8"
  - "argon/src/argon/GlobalMetadata.scala:7-34"
  - "argon/src/argon/ScratchpadMetadata.scala:7-31"
  - "argon/src/argon/Consumers.scala:1-3"
  - "argon/src/argon/Aliases.scala:1-5"
  - "argon/src/argon/NestedInputs.scala:1-3"
  - "argon/src/argon/Effects.scala:5-30"
  - "argon/src/argon/State.scala:157-159"
  - "argon/src/argon/static/Staging.scala:124-140"
  - "argon/src/argon/static/Implicits.scala:136-167"
  - "argon/src/argon/transform/Transformer.scala:94-138"
  - "argon/src/argon/transform/Transformer.scala:228-233"
source_notes:
  - "[[argon-framework]]"
hls_status: clean
depends_on:
  - "[[30 - Effects and Aliasing]]"
  - "[[50 - Staging Pipeline]]"
  - "[[90 - Transformers]]"
status: draft
---

# Argon Metadata Model

## Summary

Argon stores compiler facts as typed `Data[T]` values attached either to symbols, to compiler-global state, or to a scratchpad keyed by `(Sym, metadata class)`. The per-symbol storage is the `_data: mutable.Map[Class[_],Data[_]]` field on every `Exp` (`argon/src/argon/Ref.scala:123-126`). The `metadata` object wraps that map with typed `add`, `remove`, `clear`, `apply`, and sorted `all` accessors (`argon/src/argon/Data.scala:87-123`). The compiler state owns the global and scratchpad stores as `val globals: GlobalMetadata` and `val scratchpad: ScratchpadMetadata` (`argon/src/argon/State.scala:157-159`). The main semantic hook is `Data.transfer`, which tells transformers whether a fact is mirrored, removed, or ignored during graph rewriting (`argon/src/argon/Data.scala:36-60`).

## Syntax or API

All metadata classes extend `abstract class Data[T](val transfer: Transfer.Transfer)` (`argon/src/argon/Data.scala:71-83`). A metadata class may pass an explicit `Transfer` value, or it may use the secondary constructor `def this(setBy: SetBy) = this(Transfer(setBy))` (`argon/src/argon/Data.scala:76`). `SetBy` classifies the producer as user, flow-self, flow-consumer, analysis-self, analysis-consumer, global-user, global-flow, or global-analysis data (`argon/src/argon/Data.scala:8-34`). `Transfer.apply` maps `User`, `Flow.Self`, `Analysis.Self`, and `GlobalData.User` to `Mirror`, while `Flow.Consumer`, `Analysis.Consumer`, `GlobalData.Flow`, and `GlobalData.Analysis` map to `Remove` (`argon/src/argon/Data.scala:51-60`).

`Data.mirror(f)` defaults to returning `this` cast to `T`, so metadata with embedded symbols must override it if those symbols need transformer substitution (`argon/src/argon/Data.scala:78-80`). The separate `Mirrorable[A]` trait is the non-metadata analogue: it requires `def mirror(f: Tx): A` for values that `Transformer.apply` can recursively mirror (`argon/src/argon/Mirrorable.scala:5-8`; `argon/src/argon/transform/Transformer.scala:40-43`). Metadata identity is class-keyed: `Data.key` returns `self.getClass`, and `Data.hashCode` is final on that key (`argon/src/argon/Data.scala:81-83`).

## Semantics

For symbol metadata, `Transfer.Mirror` copies metadata from source to destination by calling the transformer mirror hook, `Transfer.Remove` explicitly removes that key from the destination, and `Transfer.Ignore` leaves the destination untouched (`argon/src/argon/transform/Transformer.scala:99-108`). The actual mirror call is `metadata.add(dest, k, mirror(m))`, where transformer-local `mirror(m)` delegates to `m.mirror(f)` (`argon/src/argon/transform/Transformer.scala:104-105`; `argon/src/argon/transform/Transformer.scala:137-138`). This means `Mirror` preserves a fact only if the metadata object itself knows how to rewrite its internal references; otherwise the default `Data.mirror` preserves object identity (`argon/src/argon/Data.scala:78-80`).

Several core metadata classes make the policy explicit. `Consumers(users)` is `SetBy.Flow.Consumer`, so it transfers as `Remove` (`argon/src/argon/Consumers.scala:1-3`; `argon/src/argon/Data.scala:54`). `NestedInputs(inputs)` is also removed during transformation (`argon/src/argon/NestedInputs.scala:1-3`). `ShallowAliases` and `DeepAliases` use `Transfer.Ignore`, so the transformer does not overwrite them through `transferData` (`argon/src/argon/Aliases.scala:1-5`; `argon/src/argon/transform/Transformer.scala:104-108`). `Effects` also uses `Transfer.Ignore`, with the source comment explaining that effects are created during staging and should not be removed by metadata transfer (`argon/src/argon/Effects.scala:5-30`).

Global metadata uses the same `Data.transfer` value but a different invalidation path. `Transformer.preprocess` clears the CSE cache and calls `globals.invalidateBeforeTransform()` before traversing the top-level block (`argon/src/argon/transform/Transformer.scala:228-233`). `GlobalMetadata.invalidateBeforeTransform` removes entries whose transfer is `Transfer.Remove`, and preserves entries whose transfer is `Mirror` or `Ignore` (`argon/src/argon/GlobalMetadata.scala:19-26`). Because `Transfer(GlobalData.Flow)` and `Transfer(GlobalData.Analysis)` both return `Remove`, global flow and analysis facts are dropped before transformers, while `GlobalData.User` is preserved (`argon/src/argon/Data.scala:57-60`; `argon/src/argon/GlobalMetadata.scala:19-26`).

## Implementation

The per-symbol API is just a typed facade over `edge._data`. `metadata.add(edge, key, m)` writes `edge._data += (key -> m)`, and `metadata.remove(edge, key)` calls `edge._data.remove(key)` (`argon/src/argon/Data.scala:96-101`; `argon/src/argon/Data.scala:113-118`). The typed `metadata.apply[M](edge)` computes the runtime class from `Manifest[M]` and casts the stored `Data[_]` back to `M` (`argon/src/argon/Data.scala:94-95`; `argon/src/argon/Data.scala:120-123`). `metadata.all` sorts by class string before iterating, which gives deterministic debug/transfer order but does not change lookup semantics (`argon/src/argon/Data.scala:111`).

The optional add overload treats `Some(data)` as an add and `None` as a removal for that metadata class, so callers can express "set or clear" without separately matching at the call site (`argon/src/argon/Data.scala:105-110`). `ScratchpadMetadata` mirrors that option-add convention for scratchpad entries, but its key includes the symbol as well as the metadata class (`argon/src/argon/ScratchpadMetadata.scala:11-19`).

Staging installs the most important symbol metadata immediately after symbol creation. `register` adds impure effects to `state.impure`, writes `sym.effects`, `sym.deepAliases`, and `sym.shallowAliases`, registers reverse aliases, records `Consumers` on every input, then runs immediate and registered flows (`argon/src/argon/static/Staging.scala:124-140`). The implicit symbol ops expose those fields: `consumers_=` writes `Consumers`, `effects_=` writes `Effects`, and alias setters write `ShallowAliases` and `DeepAliases` (`argon/src/argon/static/Implicits.scala:136-167`). `nestedInputs` is lazily memoized by reading `NestedInputs`, computing external block inputs, and writing `NestedInputs(inputs)` back to metadata (`argon/src/argon/static/Implicits.scala:139-151`).

`GlobalMetadata` is a class-keyed `HashMap[Class[_],Data[_]]` with typed `add`, `apply`, `clear`, `copyTo`, `reset`, and sorted `foreach` (`argon/src/argon/GlobalMetadata.scala:7-34`). `ScratchpadMetadata` is a separate `HashMap[(Sym[_],Class[_]),Data[_]]` and supports typed `add`, option-add, `remove`, `clear`, and `apply` (`argon/src/argon/ScratchpadMetadata.scala:7-31`). The `globals` object in `Data.scala` is annotated with `@data` and delegates `add`, `apply`, `clear`, `invalidateBeforeTransform`, and `foreach` to `state.globals` (`argon/src/argon/Data.scala:125-132`).

## Interactions

Metadata is created by staging, flow rules, user APIs, and analysis passes; its lifetime during transformation is controlled by `Data.transfer` (`argon/src/argon/Data.scala:36-60`). Transformer mirroring calls `stageWithFlow(mirrorNode(rhs)){ lhs2 => transferDataIfNew(lhs,lhs2) }`, so metadata transfer happens inside the staging flow callback and before registered `@flow` rules for the new node (`argon/src/argon/transform/Transformer.scala:146-151`; `argon/src/argon/static/Staging.scala:134-140`). The comment on `transferData` warns that `Transfer.Remove` can be bug-prone for memory metadata because memories may be visited before users, causing reader/writer metadata to disappear too early (`argon/src/argon/transform/Transformer.scala:104-107`).

## HLS notes

This model ports cleanly as a typed side table keyed by symbol id and metadata type (inferred, unverified). The essential compatibility points are class-keyed uniqueness, a three-way transfer policy, and explicit invalidation of global flow/analysis facts before transforms (`argon/src/argon/Data.scala:47-60`; `argon/src/argon/GlobalMetadata.scala:19-26`).

## Open questions

- See [[open-questions-argon-supplemental#Q-arg-01]]: `Data.scala` says global analysis data is dropped if it is Mirror or Remove, but `GlobalMetadata.invalidateBeforeTransform` removes only `Transfer.Remove`.
- See [[open-questions-argon-supplemental#Q-arg-02]]: `Transfer.Remove` is explicitly called bug-prone for memory metadata; the intended replacement policy is not documented in these files.
