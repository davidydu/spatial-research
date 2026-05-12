---
type: spec
concept: Debug metadata
source_files:
  - "src/spatial/metadata/debug/DebugData.scala:5-15"
  - "src/spatial/metadata/debug/package.scala:6-13"
  - "src/spatial/metadata/CLIArgs.scala:8-47"
  - "src/spatial/metadata/PendingUses.scala:8-24"
source_notes:
  - "No prior deep-dive note; written directly from source."
hls_status: clean
depends_on:
  - "[[00 - Metadata Index]]"
status: draft
---

# Debug

## Summary

Debug metadata is a small collection of flags, annotations, CLI-argument naming data, and ephemeral-node pending-use tracking. `ShouldDumpFinal` is a user-set boolean flag, `NoWarnWriteRead` is a mirrored warning-suppression flag, and `TreeAnnotations` is mirrored string annotation metadata (src/spatial/metadata/debug/DebugData.scala:11-15). `CLIArgs` is global CLI argument naming metadata stored as a `Map[Int,String]`, and `PendingUses` is a global analysis map from ephemeral nodes to the ephemeral nodes they indirectly use (src/spatial/metadata/CLIArgs.scala:8-17; src/spatial/metadata/PendingUses.scala:8-18).

## Fields

- `ShouldDumpFinal(flag)` uses `SetBy.User`, although the immediately preceding comment text still describes reader symbols for local memory and appears stale (src/spatial/metadata/debug/DebugData.scala:5-11).
- `NoWarnWriteRead(flag)` uses `Transfer.Mirror`, so the flag is mirrored across symbol copies according to the declared transfer policy (src/spatial/metadata/debug/DebugData.scala:13-13).
- `TreeAnnotations(str)` uses `Transfer.Mirror`, so tree annotation strings also mirror with transformed symbols (src/spatial/metadata/debug/DebugData.scala:15-15).
- `CLIArgs(map)` uses `Transfer.Mirror`, and its comment defines optional and default access for integer or staged `I32` argument indices (src/spatial/metadata/CLIArgs.scala:8-17).
- `PendingUses(nodes)` uses `GlobalData.Analysis`, so the pending-use tracker is global analysis metadata rather than per-symbol metadata (src/spatial/metadata/PendingUses.scala:17-23).

## Implementation

The debug package exposes `shouldDumpFinal`, `noWarnWR`, and `treeAnnotations` as symbol extension methods over the three debug metadata wrappers (src/spatial/metadata/debug/package.scala:6-13). Both boolean getters use `metadata[...] .exists(_.flag)`, so absent metadata defaults to `false` for `shouldDumpFinal` and `noWarnWR` (src/spatial/metadata/debug/package.scala:7-11). `treeAnnotations` returns `Option[String]`, and `treeAnnotations_=` writes `TreeAnnotations(str)` (src/spatial/metadata/debug/package.scala:12-13).

`CLIArgs.all` reads the global map and defaults to `Map.empty`, while `CLIArgs.get(i: Int)` returns a direct map lookup (src/spatial/metadata/CLIArgs.scala:19-21). `CLIArgs.get(i: I32)` pattern-matches `Final(c)` and delegates to the integer getter, otherwise returning `None` (src/spatial/metadata/CLIArgs.scala:22-25). `CLIArgs.apply` defaults missing indices to `"???"`, and `CLIArgs.update` appends duplicate names as `"old / new"` rather than replacing them (src/spatial/metadata/CLIArgs.scala:27-33). `CLIArgs.listNames` produces a dense listing from index `0` through the maximum stored index, marks holes as `"(no name)"`, and returns `"<No input args>"` when the map is empty (src/spatial/metadata/CLIArgs.scala:35-46). The source says these names are application-runtime CLI names; use by generated code or codegen is inferred rather than proven in this metadata file (src/spatial/metadata/CLIArgs.scala:8-17).

`PendingUses.all` exposes the global mutable `HashMap` and defaults to `HashMap.empty`, while `apply`, `contains`, `+=`, and `reset` provide lookup, membership, mutation, and global reset operations (src/spatial/metadata/PendingUses.scala:17-24). The `PendingUses` comment states that this map supports usage analysis when removing ephemeral nodes (src/spatial/metadata/PendingUses.scala:8-15).

## Interactions

`CLIArgs.get(i: I32)` depends on bounds metadata because it imports `Final` and only resolves staged indices with a `Final(c)` extractor match (src/spatial/metadata/CLIArgs.scala:5-6; src/spatial/metadata/CLIArgs.scala:22-25). `PendingUses` is intentionally global and mutable through the returned `HashMap`, so passes that remove ephemeral nodes must coordinate around the global reset and update surface (src/spatial/metadata/PendingUses.scala:17-24).

## HLS notes

These fields are compiler/debug metadata and should not become HLS hardware state unless a debug instrumentation design explicitly consumes them (inferred, unverified). The source-level behavior to preserve is default-false flags, mirrored warning and annotation data, dense CLI name listing, duplicate-name concatenation, and global pending-use reset semantics (src/spatial/metadata/debug/package.scala:7-13; src/spatial/metadata/CLIArgs.scala:27-46; src/spatial/metadata/PendingUses.scala:19-23).

## Open questions

- Q-meta-18 asks whether the stale `ShouldDumpFinal` comment should be corrected before using it as normative specification text (src/spatial/metadata/debug/DebugData.scala:5-11).
- Q-meta-19 asks which codegen or reporting path consumes `CLIArgs.listNames`, because the metadata source only states application-runtime argument naming (src/spatial/metadata/CLIArgs.scala:8-17; src/spatial/metadata/CLIArgs.scala:35-46).
