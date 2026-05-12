---
type: spec
concept: Rewrites metadata
source_files:
  - "src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10"
  - "src/spatial/metadata/rewrites/package.scala:7-9"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Rewrites

## Summary

Rewrites metadata currently consists of one boolean field, `CanFuseFMA`, and one package-level symbol API, `canFuseAsFMA` (src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10; src/spatial/metadata/rewrites/package.scala:7-9). The source comment says the field marks that an addition can be fused into a multiplication, and the public getter/setter names make the intended fused operation an FMA (src/spatial/metadata/rewrites/CanFuseFMA.scala:5-8; src/spatial/metadata/rewrites/package.scala:8-9).

## Fields

- `CanFuseFMA(canFuse)` uses `Transfer.Mirror`, so the rewrite-fusion eligibility flag is preserved across mirrored symbols according to the declared transfer policy (src/spatial/metadata/rewrites/CanFuseFMA.scala:10-10).
- There are no `Remove`, `SetBy`, or `GlobalData` fields in this category's visible source; the only metadata case class is `CanFuseFMA` with `Transfer.Mirror` (src/spatial/metadata/rewrites/CanFuseFMA.scala:1-10).
- `canFuseAsFMA` returns true only when `CanFuseFMA` metadata exists and its `canFuse` field is true, so absent metadata defaults to false (src/spatial/metadata/rewrites/package.scala:7-8).
- `canFuseAsFMA_=` writes a fresh `CanFuseFMA(canFuse)` metadata wrapper on the symbol (src/spatial/metadata/rewrites/package.scala:8-9).

## Implementation

The data file is deliberately minimal: it imports `argon._`, declares the metadata comment, and defines one case class extending `Data[CanFuseFMA]` with `transfer = Transfer.Mirror` (src/spatial/metadata/rewrites/CanFuseFMA.scala:1-10). The package object is also minimal: it imports `argon._`, defines `RewriteDataOps(s: Sym[_])`, and exposes only the getter and setter for the FMA flag (src/spatial/metadata/rewrites/package.scala:1-12). There is no local implementation of the actual arithmetic rewrite in this metadata category; this file only records the legality or preference bit used by other rewrite logic (src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10; src/spatial/metadata/rewrites/package.scala:7-9).

The getter uses `metadata[CanFuseFMA](s).exists(_.canFuse)`, which means both missing metadata and present metadata with `false` collapse to the same observable result (src/spatial/metadata/rewrites/package.scala:8-8). The setter stores the caller-provided boolean directly, which means consumers can explicitly mark a symbol as non-fusible even though the getter behavior cannot distinguish explicit false from absence (src/spatial/metadata/rewrites/package.scala:8-9).

## Interactions

This metadata category relates to math cycle handling because `InCycle` explicitly mentions FMA rewrites as a case where only part of a cycle should not be rewritten, while `CanFuseFMA` is the separate mirrored flag for whether an addition can be fused with a multiplication (src/spatial/metadata/math/MathData.scala:24-32; src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10). The category has no direct imports of math, bounds, control, or memory metadata in its package object, so any cross-category behavior is implemented outside this source file (src/spatial/metadata/rewrites/package.scala:1-12).

## HLS notes

FMA fusion is likely an HLS codegen or optimization decision rather than a hardware-visible metadata field (inferred, unverified). The Rust+HLS rewrite should preserve the boolean eligibility semantics and the mirror transfer policy, then decide whether the flag maps to an HLS intrinsic, compiler optimization hint, or eliminated intermediate rewrite state (src/spatial/metadata/rewrites/CanFuseFMA.scala:5-10; src/spatial/metadata/rewrites/package.scala:7-9).

## Open questions

- Q-meta-20 asks which pass sets `CanFuseFMA(false)` intentionally, because the getter cannot distinguish explicit false from missing metadata (src/spatial/metadata/rewrites/package.scala:8-9).
