---
type: spec
concept: Bounds metadata
source_files:
  - "src/spatial/metadata/bounds/BoundData.scala:10-118"
  - "src/spatial/metadata/bounds/package.scala:9-32"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Bounds

## Summary

Bounds metadata records integer knowledge about symbols through a small `Bound` lattice and several related flags. `Bound` is an `Int` payload with `toInt`, a mutable `isFinal` flag, and a `meet` operation that keeps `Expect` only when both sides are `Expect`, keeps `Final` only when both sides are `Final`, and otherwise returns an `UpperBound` over the larger integer value (src/spatial/metadata/bounds/BoundData.scala:10-21). The source has a TODO noting that `Bound` is currently expressed in terms of `Int`, so a rewrite should not silently widen the meaning without checking all consumers (src/spatial/metadata/bounds/BoundData.scala:9-11).

## Fields

- `Bound`, `Final`, `Expect`, and `UpperBound` are payload types rather than `Data` fields; transfer policy applies when a bound is carried by `SymbolBound` (src/spatial/metadata/bounds/BoundData.scala:10-25).
- `SymbolBound(bound)` uses `SetBy.Analysis.Self`, so analysis owns the symbol-bound value and ordinary mirroring is not the declared transfer policy (src/spatial/metadata/bounds/BoundData.scala:27-38).
- `Global(flag)` uses `SetBy.Flow.Self`, and the comment defines a global as a value depending only on inputs and constants before the main computation starts (src/spatial/metadata/bounds/BoundData.scala:40-49).
- `FixedBits(flag)` uses `SetBy.Flow.Self`, and its comment says the symbol is representable as a statically known list of bits (src/spatial/metadata/bounds/BoundData.scala:51-57).
- `Count(c)` uses `SetBy.User`, while `VecConst(vs)` uses `SetBy.Analysis.Self` for vector-constant metadata used by inner-loop vectorization for PIR (src/spatial/metadata/bounds/BoundData.scala:89-96).

## Implementation

`getBound` first recognizes literal `Int` values as `Final`, then checks scratchpad `SymbolBound`, then recognizes exact fixed-point parameters as `Expect` when no normal `SymbolBound` exists, and finally checks normal metadata `SymbolBound` (src/spatial/metadata/bounds/package.scala:10-15). The throwing `bound` getter requires a present bound, while `bound_=` writes `SymbolBound` into the scratchpad rather than the normal metadata store (src/spatial/metadata/bounds/package.scala:16-18). `makeFinal` mutates the current bound's `isFinal` flag and then writes a new `Final(x)` into `bound`, which is a source-level ordering the rewrite must preserve or deliberately change (src/spatial/metadata/bounds/BoundData.scala:13-21; src/spatial/metadata/bounds/package.scala:19).

The extractors encode three related but distinct reads. `Final.unapply(Bound)` only accepts the `Final` case, while `Final.unapply(Sym[_])` accepts a stored `Final` or an `Expect` with `isFinal` set and then asks for the symbol's integer value (src/spatial/metadata/bounds/BoundData.scala:60-70). `Expect.unapply(Bound)` returns any bound's integer payload, while `Expect.unapply(Sym[_])` prefers `getIntValue` and falls back to `getBound.map(_.toInt)` (src/spatial/metadata/bounds/BoundData.scala:73-76). `Upper.unapply` only accepts a stored `UpperBound`, and `Bounded.unapply` forwards `getBound` directly (src/spatial/metadata/bounds/BoundData.scala:78-87).

`Global` and `FixedBits` both default to true for value symbols and otherwise read their respective flags, while their setters add metadata through the normal metadata store (src/spatial/metadata/bounds/package.scala:21-25). `VecConst.unapply` exposes the vector payload only for a `Sym[_]` with stored `vecConst`, and `VecConst.broadcast` combines vector/scalar or vector/vector operands into a new `boundVar` whose `vecConst` is set to the computed sequence (src/spatial/metadata/bounds/BoundData.scala:97-117; src/spatial/metadata/bounds/package.scala:27-28). `count` and `count_=` are thin accessors over `Count(c)` (src/spatial/metadata/bounds/package.scala:30-31).

## Interactions

Bounds interacts directly with parameter handling because `BoundData.scala` imports `spatial.metadata.params._`, and `getBound` treats exact fixed-point params as `Expect` bounds when no normal symbol bound is stored (src/spatial/metadata/bounds/BoundData.scala:5; src/spatial/metadata/bounds/package.scala:10-15). Bounds also feeds type helpers indirectly because `ParamHelpers.toInt` in the types metadata package pattern-matches `Expect(c)` before returning an integer (src/spatial/metadata/types.scala:38-42).

## HLS notes

The Rust+HLS rewrite should model these as compiler metadata, not runtime hardware state (inferred, unverified). The `makeFinal` ordering around `isFinal` is worth preserving during migration until its intent is resolved, because the source mutates one bound object and then stores another (src/spatial/metadata/bounds/BoundData.scala:13-21; src/spatial/metadata/bounds/package.scala:19).

## Open questions

- Q-meta-13 asks whether `makeFinal` is intentionally setting `isFinal` on the old bound object before replacing it with a fresh `Final(x)` (src/spatial/metadata/bounds/package.scala:19).
