---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-23
date_updated: 2026-04-25
---

# HLS Mapping - Clean

Constructs that translate directly to HLS C++ or to target-independent Rust compiler structures.

Each line is generated from spec-entry `hls_status` frontmatter. Entries marked `unknown` are included with a suggested classification rather than modifying the source spec.

[[10 - Controllers]] — Surface construct has a direct HLS C++ expression or structured-control analogue.
[[20 - Memories]] — Surface construct has a direct HLS C++ expression or structured-control analogue.
[[30 - Primitives]] — Surface construct has a direct HLS C++ expression or structured-control analogue.
[[50 - Math and Helpers]] — Surface construct has a direct HLS C++ expression or structured-control analogue.
[[10 - Effects and Aliasing]] — Semantic rule is target-independent and should be preserved directly in the rewrite.
[[10 - Symbols and Types]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[20 - Ops and Blocks]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[30 - Effects and Aliasing]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[40 - Metadata Model]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[50 - Staging Pipeline]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[70 - Rewrites and Flows]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[80 - Passes]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[A0 - Codegen Skeleton]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[D0 - DSL Base Types]] — Core staged-IR abstraction is target-independent and can be represented directly in a Rust compiler IR.
[[50 - Primitives]] — Primitive IR node semantics are target-independent and lower naturally to HLS expressions.
[[80 - Types]] — Structural metadata is compiler bookkeeping and can map to Rust-side annotations without changing HLS semantics.
[[A0 - Debug]] — Structural metadata is compiler bookkeeping and can map to Rust-side annotations without changing HLS semantics.
[[A0 - Flattening and Binding]] — Transformation is target-independent cleanup or binding logic that can be ported directly.
[[E0 - Cleanup]] — Transformation is target-independent cleanup or binding logic that can be ported directly.
[[10 - ISL Binding]] — Math and constraint representation can carry over to drive HLS banking, partitioning, and access analysis.
[[20 - Access Algebra]] — Math and constraint representation can carry over to drive HLS banking, partitioning, and access analysis.
[[30 - Banking Math]] — Math and constraint representation can carry over to drive HLS banking, partitioning, and access analysis.
[[60 - CSV Model Format]] — Data format is portable and can be consumed by an HLS-oriented model pipeline.
