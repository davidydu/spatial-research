---
type: spec
concept: "Compiler Infrastructure"
source_files:
  - "src/spatial/util/modeling.scala:1-992"
  - "src/spatial/executor/scala/ExecutorPass.scala:1-106"
  - "src/spatial/report/MemoryReporter.scala:1-108"
  - "src/spatial/issues/UnbankableGroup.scala:1-20"
source_notes:
  - "[[open-questions-infra]]"
hls_status: unknown
depends_on:
  - "[[00 - Spec Index]]"
status: draft
---

# Infrastructure Index

## Summary

This folder covers compiler support code that is not a single front-end construct, IR node family, compiler pass, backend, or runtime target. It is the map for four infrastructure areas: [[10 - Modeling Utilities]], [[20 - Scala Executor]], [[30 - Reports]], and [[40 - Issues and Diagnostics]]. These entries connect utility APIs, reference execution, diagnostic reports, and deferred issue handling back to the rest of the Spatial spec. The source root for citations is `/Users/david/Documents/David_code/spatial`.

## API

Use this MOC as the entry point when a behavior question is about compiler plumbing rather than Spatial language semantics. [[10 - Modeling Utilities]] is the cycle, latency, area-model, graph-search, retiming-delay, and memory-token helper layer. [[20 - Scala Executor]] is the `--scalaExec` interpreter path. [[30 - Reports]] covers `Memories.report` and `Retime.report`. [[40 - Issues and Diagnostics]] covers `argon.Issue`, Spatial issue subclasses, and where those diagnostics are raised.

## Implementation

The modeling utility object is a large singleton under `src/spatial/util/modeling.scala:1-992`. The Scala executor is rooted at `src/spatial/executor/scala/ExecutorPass.scala:10-106` and dispatches through `src/spatial/executor/scala/ControlExecutor.scala:16-1069`. Reports live in `src/spatial/report/MemoryReporter.scala:13-108` and `src/spatial/report/RetimeReporter.scala:10-65`. Deferred diagnostics use the Argon base in `argon/src/argon/Issue.scala:10-19` plus Spatial cases under `src/spatial/issues/*.scala`.

## Interactions

These entries cross-link to [[70 - Timing Model]], [[10 - Area Model]], [[C0 - Retiming]], [[70 - Banking]], [[20 - Scalagen]], and [[70 - Naming and Resource Reports]]. The infrastructure code is mostly consumed by analyses, transformations, and diagnostics rather than directly by user-facing DSL nodes.

## HLS notes

HLS portability is mixed. The reports and issue model are mostly compiler-side diagnostics. Modeling and the Scala executor need HLS-specific interpretation because they encode Spatial's existing target latency assumptions and simulator architecture.

## Open questions

See [[open-questions-infra]] for infrastructure-specific unresolved questions.
