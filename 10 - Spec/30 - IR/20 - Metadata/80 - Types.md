---
type: spec
concept: Types metadata helpers
source_files:
  - "src/spatial/metadata/types.scala:8-43"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: clean
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Types

## Summary

`types.scala` is a helper file rather than a metadata-data file: it defines type-classification and symbol-classification helpers, and it contains no `Data[...]` case class in the visible helper definitions (src/spatial/metadata/types.scala:8-43). The file is small but important because it centralizes `isIdx`, `isBits`, `nbits`, bit-input extraction, and parameter-to-`Int` conversion helpers used by other metadata packages (src/spatial/metadata/types.scala:18-42).

## Fields

- There are no `Mirror`, `Remove`, `SetBy`, or `GlobalData` transfer policies in this file because the file defines implicit helper classes and an object rather than metadata fields (src/spatial/metadata/types.scala:8-43).
- `TypeUtils[A]` classifies `Type[A]` values with `isNum`, `isBits`, `isVoid`, and `isString`, where `isString` checks whether the first type argument is `Text` (src/spatial/metadata/types.scala:8-14).
- `types.nbits(e)` returns `bT.nbits` when `e.tp` matches `Bits(bT)` and returns `0` otherwise (src/spatial/metadata/types.scala:17-19).
- `SymUtils[A].isIdx` treats a symbol as an index when its type matches `FixPtType(_,_,0)` (src/spatial/metadata/types.scala:21-25).
- `SymUtils[A]` also exposes `isNum`, `isBits`, `isVoid`, `isString`, and `bitInputs`, where `bitInputs` reads the symbol's op and falls back to `Nil` when no op exists (src/spatial/metadata/types.scala:26-32).
- `OpUtils.bitInputs` filters `op.expInputs` to symbols whose `isBits` helper returns true (src/spatial/metadata/types.scala:34-36).
- `ParamHelpers.toInt` returns `c` for symbols matching `Expect(c)` and throws when a symbol cannot be converted to a constant integer (src/spatial/metadata/types.scala:38-42).

## Implementation

`UtilsIRLowPriority` holds `TypeUtils`, and `object types` extends that trait to package the lower-priority type helpers with the symbol, op, and parameter helpers (src/spatial/metadata/types.scala:8-17). The type-level `isBits` test is based on `x.isInstanceOf[Bits[_]]`, while the symbol-level `isBits` test is based on `x.isInstanceOf[Bits[_]]` as written in the source rather than by matching `x.tp` (src/spatial/metadata/types.scala:9-14; src/spatial/metadata/types.scala:26-29). The index classifier is more specific than the generic numeric classifier because it matches `FixPtType(_,_,0)` on the symbol type (src/spatial/metadata/types.scala:21-25).

The bit-input helpers preserve a symbol/op distinction. A symbol asks its optional op for `bitInputs` and returns `Nil` without an op, while an op computes bit inputs by filtering expression inputs through the symbol-level `isBits` helper (src/spatial/metadata/types.scala:31-36). The integer conversion helper delegates to the bounds extractor `Expect`, which means it accepts either an integer value or bound-derived value according to the bounds extractor implementation rather than reading a local type metadata field (src/spatial/metadata/types.scala:38-42; src/spatial/metadata/bounds/BoundData.scala:73-76).

## Interactions

Bounds and params are the two visible local interactions in these source files. `types.scala` imports `spatial.metadata.bounds.Expect`, and `ParamHelpers.toInt` pattern-matches that extractor (src/spatial/metadata/types.scala:6; src/spatial/metadata/types.scala:38-42). Params imports `spatial.metadata.types._`, and `Restrict.ParamValue.v` uses `x.toInt` during restriction evaluation (src/spatial/metadata/params/DSEData.scala:7; src/spatial/metadata/params/DSEData.scala:96-103).

## HLS notes

These helpers should translate cleanly to Rust-side compiler predicates over the rewritten IR type model, but the rewrite must decide whether the current symbol-level `isNum` and `isBits` implementations intentionally test the symbol object or should test `x.tp` like `isIdx` and `isString` do (src/spatial/metadata/types.scala:21-29). No HLS hardware metadata is implied by this file because no `Data[...]` field is declared here (src/spatial/metadata/types.scala:8-43).

## Open questions

- Q-meta-16 asks whether `SymUtils.isNum`, `isBits`, and `isVoid` should test the symbol object as written or should mirror the type-level checks on `x.tp` (src/spatial/metadata/types.scala:21-29).
