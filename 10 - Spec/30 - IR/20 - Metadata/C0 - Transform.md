---
type: spec
concept: Transform metadata
source_files:
  - "src/spatial/metadata/transform/TransformData.scala:5-19"
  - "src/spatial/metadata/transform/package.scala:8-31"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Transform

## Summary

Transform metadata contains two mirrored boolean fields: `StreamPrimitive` and `FreezeMem`. `StreamPrimitive` marks whether streamification should dig deeper into a structure, according to its source comment, and `FreezeMem` marks whether a memory's banking patterns and related analysis should be changed (src/spatial/metadata/transform/TransformData.scala:5-19). The package object adds symbol-level accessors for both flags and control-level ancestor helpers for stream-primitive detection (src/spatial/metadata/transform/package.scala:8-31).

## Fields

- `StreamPrimitive(flag)` uses `Transfer.Mirror`, so stream-primitive classification is carried across mirrored symbols (src/spatial/metadata/transform/TransformData.scala:5-11).
- `FreezeMem(flag)` uses `Transfer.Mirror`, so memory-freeze classification is also carried across mirrored symbols (src/spatial/metadata/transform/TransformData.scala:14-19).
- There are no `Remove`, `SetBy`, or `GlobalData` metadata fields in this transform source; both visible fields are mirrored booleans (src/spatial/metadata/transform/TransformData.scala:5-19).
- `isStreamPrimitive` defaults to false through `metadata[StreamPrimitive](s).exists(_.flag)`, and `isStreamPrimitive_=` writes `StreamPrimitive(flag)` (src/spatial/metadata/transform/package.scala:8-10).
- `freezeMem` defaults to false through `metadata[FreezeMem](s).exists(_.flag)`, and `freezeMem_=` writes `FreezeMem(flag)` (src/spatial/metadata/transform/package.scala:13-14).

## Implementation

The symbol API converts a symbol to a control with `s.toCtrl` before checking for a stream-primitive ancestor, so stream-primitive ancestry is expressed over the control hierarchy rather than raw symbols alone (src/spatial/metadata/transform/package.scala:8-12). `TransformCtrlOps.getStreamPrimitiveAncestor` walks `s.ancestors` and returns the first ancestor whose shape is `Ctrl.Node(c, _)` and whose underlying symbol has `isStreamPrimitive` set (src/spatial/metadata/transform/package.scala:17-23). The control-level `isStreamPrimitive` helper returns true only for `Ctrl.Node(s, _)` whose symbol is stream-primitive, and returns false for non-node controls (src/spatial/metadata/transform/package.scala:25-28). `hasStreamPrimitiveAncestor` is a convenience boolean defined as `getStreamPrimitiveAncestor.nonEmpty` (src/spatial/metadata/transform/package.scala:30-30).

`FreezeMem` has no ancestor helper in this package; its API is only the symbol getter and setter over `FreezeMem(flag)` (src/spatial/metadata/transform/package.scala:13-14). The source comment for `FreezeMem` is incomplete after "Generally useful for when", so only the explicit banking-analysis freeze statement is proven by this file (src/spatial/metadata/transform/TransformData.scala:14-19).

## Interactions

Transform metadata depends on control metadata because the package imports `spatial.metadata.control._` and defines helper methods over `Ctrl` plus `s.toCtrl` (src/spatial/metadata/transform/package.scala:3-7; src/spatial/metadata/transform/package.scala:11-31). `StreamPrimitive` interacts with control hierarchy traversal because the ancestor helper scans `s.ancestors` for `Ctrl.Node` entries and checks their symbols' stream-primitive flags (src/spatial/metadata/transform/package.scala:17-23). `FreezeMem` interacts with memory/banking analysis by intent according to the source comment, but this file does not show the downstream reader (src/spatial/metadata/transform/TransformData.scala:14-19).

## HLS notes

`StreamPrimitive` likely becomes a compiler transform marker for HLS stream lowering, while `FreezeMem` likely becomes a guard around banking/layout rewrites in the Rust implementation (inferred, unverified). The behavior that must be preserved from source is mirrored transfer, default-false getters, symbol-level setters, and control-ancestor walking through `Ctrl.Node` (src/spatial/metadata/transform/TransformData.scala:5-19; src/spatial/metadata/transform/package.scala:8-31).

## Open questions

- Q-meta-21 asks what exact situations the unfinished `FreezeMem` comment intended to name after "Generally useful for when" (src/spatial/metadata/transform/TransformData.scala:14-19).
