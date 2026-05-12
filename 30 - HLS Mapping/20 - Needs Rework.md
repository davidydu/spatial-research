---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-23
date_updated: 2026-04-25
---

# HLS Mapping - Needs Rework

Constructs that are conceptually portable but need HLS-specific design work.

Each line is generated from spec-entry `hls_status` frontmatter. Entries marked `unknown` are included with a suggested classification rather than modifying the source spec.

[[40 - Streams and Blackboxes]] — Surface feature is portable, but backend lowering or runtime support needs HLS-specific design.
[[60 - Host and IO]] — Surface feature is portable, but backend lowering or runtime support needs HLS-specific design.
[[70 - Debugging and Checking]] — Mixed status: textual prints are direct, but printSRAM, approximate equality, and golden checks need HLS-aware runtime/testbench support.
[[80 - Virtualization]] — Surface feature is portable, but backend lowering or runtime support needs HLS-specific design.
[[90 - Aliases and Shadowing]] — Surface feature is portable, but backend lowering or runtime support needs HLS-specific design.
[[99 - Macros]] — Surface feature is portable, but backend lowering or runtime support needs HLS-specific design.
[[20 - Scheduling Model]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[30 - Control Semantics]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[40 - Memory Semantics]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[50 - Data Types]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[60 - Reduction and Accumulation]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[80 - Streaming]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[90 - Host-Accel Boundary]] — Semantic intent is portable, but exact scheduling, memory, or numeric behavior needs HLS architecture decisions.
[[60 - Scopes and Scheduling]] — Concept is portable but needs an HLS-specific representation or implementation strategy.
[[90 - Transformers]] — Concept is portable but needs an HLS-specific representation or implementation strategy.
[[B0 - Compiler Driver]] — Concept is portable but needs an HLS-specific representation or implementation strategy.
[[C0 - Macro Annotations]] — Concept is portable but needs an HLS-specific representation or implementation strategy.
[[10 - Controllers]] — IR construct is portable, but lowering and runtime behavior need explicit HLS design.
[[20 - Memories]] — IR construct is portable, but lowering and runtime behavior need explicit HLS design.
[[30 - Memory Accesses]] — IR construct is portable, but lowering and runtime behavior need explicit HLS design.
[[40 - Counters and Iterators]] — IR construct is portable, but lowering and runtime behavior need explicit HLS design.
[[60 - Streams and Blackboxes]] — IR construct is portable, but lowering and runtime behavior need explicit HLS design.
[[10 - Control]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[20 - Access]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[30 - Memory]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[40 - Retiming]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[50 - Bounds]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[60 - Math]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[70 - Params]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[90 - Blackbox]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[B0 - Rewrites]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[C0 - Transform]] — Metadata concept is portable, but consumers and invariants need a Rust/HLS data model.
[[10 - Flows and Rewrites]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[20 - Friendly and Sanity]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[30 - Switch and Conditional]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[40 - Blackbox Lowering]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[50 - Pipe Insertion]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[60 - Use and Access Analysis]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[70 - Banking]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[80 - Unrolling]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[90 - Rewrite Transformer]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[B0 - Accum Specialization]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[D0 - Streamify]] — Algorithm is portable, but its outputs and invariants must be adapted to HLS scheduling and pragmas.
[[10 - Overview]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[20 - Numeric Reference Semantics]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[30 - Memory Simulator]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[40 - FIFO LIFO Stream Simulation]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[50 - Controller Emission]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[60 - Counters and Primitives]] — Reference semantics are essential, but the JVM simulator path must become Rust tests, models, or HLS-compatible runtime code.
[[70 - Naming and Resource Reports]] — Suggested rework: naming policy and resource reports are portable diagnostics, but need Rust/HLS naming and area-model choices.
[[10 - Cppgen]] — Host/codegen concept is portable, but file layout and interfaces must be reauthored for the HLS toolchain.
[[20 - Per-Target Files]] — Host/codegen concept is portable, but file layout and interfaces must be reauthored for the HLS toolchain.
[[50 - Other Codegens]] — Host/codegen concept is portable, but file layout and interfaces must be reauthored for the HLS toolchain.
[[10 - Area Model]] — Modeling concept is portable, but estimates and target constraints must be recalibrated for HLS.
[[20 - Latency Model]] — Modeling concept is portable, but estimates and target constraints must be recalibrated for HLS.
[[30 - Target Hardware Specs]] — Modeling concept is portable, but estimates and target constraints must be recalibrated for HLS.
[[40 - Design Space Exploration]] — Modeling concept is portable, but estimates and target constraints must be recalibrated for HLS.
[[50 - Memory Resources]] — Modeling concept is portable, but estimates and target constraints must be recalibrated for HLS.
