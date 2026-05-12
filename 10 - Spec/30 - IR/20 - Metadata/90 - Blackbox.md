---
type: spec
concept: Blackbox metadata
source_files:
  - "src/spatial/metadata/blackbox/BlackboxData.scala:6-17"
  - "src/spatial/metadata/blackbox/package.scala:9-23"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: rework
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Blackbox

## Summary

Blackbox metadata carries configuration for external blackbox modules and tracks user nodes associated with a blackbox symbol. `BlackboxConfig` stores a file path, optional module name, latency, pipeline factor `pf`, and a string-keyed map of value parameters with defaults of empty module name, latency `1`, `pf` `1`, and empty params (src/spatial/metadata/blackbox/BlackboxData.scala:6-6). `BlackboxInfo` wraps that config as user-set metadata, and `BlackboxUserNodes` stores a sequence of symbols as flow-consumer metadata (src/spatial/metadata/blackbox/BlackboxData.scala:8-17).

## Fields

- `BlackboxConfig(file, moduleName, latency, pf, params)` is a plain case class and therefore has no transfer policy by itself (src/spatial/metadata/blackbox/BlackboxData.scala:6-6).
- `BlackboxInfo(cfg)` uses `SetBy.User`, so the blackbox configuration is user-owned metadata on the symbol (src/spatial/metadata/blackbox/BlackboxData.scala:8-15).
- `BlackboxUserNodes(node)` uses `SetBy.Flow.Consumer`, so user-node tracking is flow-owned consumer metadata (src/spatial/metadata/blackbox/BlackboxData.scala:17-17).
- `getBboxInfo` returns an optional config, while `bboxInfo` falls back to `BlackboxConfig("")` when no config is stored (src/spatial/metadata/blackbox/package.scala:9-12).
- `getUserNodes`, `userNodes`, and `addUserNode` read the stored sequence, default it to an empty `Seq[Sym[_]]`, and append by replacing the metadata with `userNodes :+ node` (src/spatial/metadata/blackbox/package.scala:15-17).

## Implementation

The package object imports `spatial.node._`, which is where the blackbox node classes used by the predicates come from (src/spatial/metadata/blackbox/package.scala:3-5). `bboxII` returns `bboxInfo.pf` when explicit blackbox metadata exists, otherwise returns the symbol's `II` when `isSpatialPrimitiveBlackbox` is true, and otherwise returns `1.0` (src/spatial/metadata/blackbox/package.scala:10-13). `isCtrlBlackbox` recognizes `VerilogCtrlBlackbox`, `SpatialCtrlBlackboxUse`, and `SpatialCtrlBlackboxImpl` node shapes (src/spatial/metadata/blackbox/package.scala:19-19). `isBlackboxImpl` recognizes `BlackboxImpl`, `isBlackboxUse` recognizes `CtrlBlackboxUse`, and `isSpatialPrimitiveBlackbox` recognizes `SpatialBlackboxImpl` (src/spatial/metadata/blackbox/package.scala:20-22).

The getter and setter surface is intentionally narrow. `bboxInfo_=` writes `BlackboxInfo(cfg)`, and there is no separate setter for the individual fields inside `BlackboxConfig` in this package (src/spatial/metadata/blackbox/package.scala:10-12). `addUserNode` does not mutate the stored sequence in place; it reads `userNodes`, appends one symbol, and writes a fresh `BlackboxUserNodes` wrapper (src/spatial/metadata/blackbox/package.scala:15-17).

## Interactions

Blackbox metadata interacts with control metadata because the package imports `spatial.metadata.control._` and uses `s.II` as the fallback initiation interval for spatial primitive blackboxes (src/spatial/metadata/blackbox/package.scala:5-13). Blackbox metadata also interacts with node classification because all four predicate helpers inspect `s.op` and pattern-match node classes rather than metadata fields (src/spatial/metadata/blackbox/package.scala:19-22).

## HLS notes

Rust+HLS needs a new blackbox binding design rather than a direct copy of Verilog-oriented assumptions (inferred, unverified). The parts that must be preserved from source are the user-owned config payload, the pipeline-factor fallback used by `bboxII`, and the distinction among control blackboxes, implementations, uses, and spatial primitive implementations (src/spatial/metadata/blackbox/BlackboxData.scala:6-17; src/spatial/metadata/blackbox/package.scala:10-22).

## Open questions

- Q-meta-17 asks how `BlackboxConfig.file`, `moduleName`, `latency`, `pf`, and `params` should map to the Rust+HLS blackbox ABI rather than the existing Spatial/Verilog model (src/spatial/metadata/blackbox/BlackboxData.scala:6-15).
