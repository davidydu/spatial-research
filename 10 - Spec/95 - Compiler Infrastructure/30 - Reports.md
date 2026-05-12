---
type: spec
concept: "Compiler Infrastructure Reports"
source_files:
  - "src/spatial/report/MemoryReporter.scala:1-108"
  - "src/spatial/report/RetimeReporter.scala:1-66"
  - "src/spatial/Spatial.scala:224-238"
  - "src/spatial/codegen/resourcegen/ResourceReporter.scala:22-30"
  - "src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-24"
source_notes:
  - "[[open-questions-infra]]"
hls_status: unknown
depends_on:
  - "[[10 - Modeling Utilities]]"
  - "[[70 - Banking]]"
  - "[[70 - Naming and Resource Reports]]"
status: draft
---

# Reports

## Summary

This entry covers two compiler-side diagnostic reporters in `src/spatial/report`: `MemoryReporter` and `RetimeReporter`. They are informational reports, not code generators. `MemoryReporter` writes `Memories.report` when `config.enInfo` is enabled `src/spatial/report/MemoryReporter.scala:13-27`. `RetimeReporter` writes `Retime.report` when both `config.enInfo` and `spatialConfig.enableRetiming` are enabled `src/spatial/report/RetimeReporter.scala:10-15`. In the main Spatial pipeline, the retime report runs immediately after the retiming transformer and checks, while the memory report runs later in the final reports section before final IR printing and final sanity checks `src/spatial/Spatial.scala:224-238`.

## API

`MemoryReporter(IR)(implicit mlModel)` is an Argon `Pass` with `shouldRun = config.enInfo`; its `process` method calls `run()` and returns the original block unchanged `src/spatial/report/MemoryReporter.scala:13-18`. `RetimeReporter(IR)` is an `AccelTraversal` with `shouldRun = config.enInfo && spatialConfig.enableRetiming`; its `process` wraps traversal in `inGen(config.repDir, "Retime.report")` `src/spatial/report/RetimeReporter.scala:10-15`.

The related codegen reporters are already specced under [[70 - Naming and Resource Reports]]. `ResourceReporter` and `ResourceCountReporter` are `NamedCodegen`-based report codegens with `lang = "reports"` and `ext = "json"` `src/spatial/codegen/resourcegen/ResourceReporter.scala:22-30` `src/spatial/codegen/resourcegen/ResourceCountReporter.scala:19-24`.

Both infrastructure reporters are read-only with respect to IR structure: `MemoryReporter.process` calls `run()` and returns `block`, and `RetimeReporter.process` delegates traversal to `super.process(block)` inside report-file generation `src/spatial/report/MemoryReporter.scala:16-18` `src/spatial/report/RetimeReporter.scala:13-15`.

## Implementation

`MemoryReporter` first gathers `LocalMemories.all`, filters out controller blackbox memories, computes area with `areaModel(mlModel).areaOf(s, d, inHwScope = true, inReduce = false)`, and sorts memories by area `src/spatial/report/MemoryReporter.scala:21-24`. Its `Memories.report` header folds all areas with `NoArea` and emits an estimated total by resource key `src/spatial/report/MemoryReporter.scala:26-34`. For each memory, it prints name, type, source location and source text, symbol, duplicate instance count, and per-resource area lines `src/spatial/report/MemoryReporter.scala:36-49`.

The per-memory detail is a banking and port summary. For each duplicate instance, `MemoryReporter` destructures `Memory(banking, depth, padding, isAccum)`, prints resource, depth, padding, accumulation flag, hierarchical/flat bank count, and every banking group `src/spatial/report/MemoryReporter.scala:52-63`. It then builds port summaries by buffer port and mux port: `portStr` finds accesses dispatched to the current duplicate, filters the instance's port map by buffer port, groups them by `muxPort`, and emits each access's source line plus direct-banking and port offset/castgroup/broadcast metadata `src/spatial/report/MemoryReporter.scala:65-95`. The report ends each memory with a control tree over the memory's readers and writers `src/spatial/report/MemoryReporter.scala:98-103`. The phrase "port histogram" here means this grouped buffer-port/mux-port listing, not a numeric histogram object.

`RetimeReporter` walks accelerator IR and prints one stanza per visited symbol. For each `lhs = rhs`, it emits the op, optional symbol name, type, reduce-cycle membership, target latency, reduce latency, whether registers are required, built-in latency, and delay-line consumers discovered by recursively following `DelayLine` users `src/spatial/report/RetimeReporter.scala:27-59`. It recursively prints nested blocks with indentation so the report preserves block structure around retimed symbols `src/spatial/report/RetimeReporter.scala:17-25` `src/spatial/report/RetimeReporter.scala:61-64`.

The reports are intentionally human-readable. `MemoryReporter` emits source context and source text for each memory, then repeats contextual lines for every port/mux access so a user can trace a banking decision back to staged code `src/spatial/report/MemoryReporter.scala:36-46` `src/spatial/report/MemoryReporter.scala:74-83`. `RetimeReporter` emits both cycle membership and delay-line consumers for the same symbol, making it a compact check of whether the retiming analyzer's cycle view matches inserted `DelayLine` nodes `src/spatial/report/RetimeReporter.scala:40-58`.

## Interactions

Both reporters depend on [[10 - Modeling Utilities]]. `MemoryReporter` imports `spatial.util.modeling._` for `areaModel`, `NoArea`, and `ctrlTree` `src/spatial/report/MemoryReporter.scala:5-10`. `RetimeReporter` imports `spatial.util.modeling._` for latency model access and delay discovery context `src/spatial/report/RetimeReporter.scala:3-8`. Memory report content also depends on banking metadata from [[70 - Banking]], because duplicate instances, dispatches, ports, mux ports, bank groups, and padding are established by banking analysis and configuration.

The resource codegen reports are adjacent but distinct. `ResourceReporter` and `ResourceCountReporter` run through the codegen/reporting path and are configured by `spatialConfig.reportArea` and `spatialConfig.countResources`, while `MemoryReporter` and `RetimeReporter` are normal compiler passes gated by `config.enInfo` and retiming configuration `src/spatial/Spatial.scala:224-250`.

## HLS notes

These reports are mostly portable as diagnostics, but their content depends on Spatial-specific memory metadata and target model names. For HLS, the open question is whether to preserve these report names and shapes or emit HLS-native summaries for array partitioning, pipeline II, and inserted delay lines.

## Open questions

See [[open-questions-infra#Q-inf-05]] for the HLS report-shape question.
