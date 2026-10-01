---
type: reference
title: "Python rewrite coverage ledger"
project: spatial-python
date: 2026-09-30
status: inventory
---

## Purpose

Account for the full original Spatial research base while designing the Python rewrite. The introductory programs are not the scope limit. This ledger supports R04 in [[03 - Managed Research Execution]] and PY-Q009 in [[02 - Python Open Questions]].

**Current status: inventory only.** Rows identify source-spec subjects and their required research destination. They do not establish semantic preservation, implemented support, or HLS eligibility. A completed review must replace each destination with a substantive study/contract link and an explicit disposition. Merely assigning a row to a folder does not close it.

The inventory is derived from `type: spec` frontmatter in the original `10 - Spec/` tree at vault revision `7a15c26`. It contains 106 documents, including index-shaped pages that declare themselves `type: spec`. The count is a document count, not a feature count. Historical notes and their HLS labels are evidence to inspect, not new Python conclusions.

## Subject accounting

| Original section | Documents | Responsibility to address |
|---|---:|---|
| `10 - Language Surface` | 15 | Public language and library coverage |
| `20 - Semantics` | 9 | Language contract and observable behavior |
| `30 - IR` | 31 | Representation, effects, and derived analyses |
| `40 - Compiler Passes` | 14 | Analysis, transformation, and optimization responsibilities |
| `50 - Code Generation` | 17 | Simulator behavior or backend obligations; backend identity is separate from language semantics |
| `60 - Polyhedral Model` | 3 | Dependence/access analysis and banking strategy |
| `70 - Models and DSE` | 6 | Target models, tuning parameters, search, and measured reports |
| `80 - Runtime and Fringe` | 6 | Device interfaces, protocol, buffering, and runtime responsibilities |
| `95 - Compiler Infrastructure` | 5 | Compiler services, diagnostics, reports, and execution |

## Source-family gap check

The pinned original source has language entry points and node families that can be broader than one document title. Review `spatial@e7a8f2f` under `src/spatial/lang/` and `src/spatial/node/`, then include Argon numeric/aggregate types and `src/spatial/lib/`. Check at least the families below against the final contract and implementation stages:

- Scalars, exact literals, fixed/floating formats, vectors/structs, casts, math, muxes, shuffles, and debug/control exits.
- Counters, runtime bounds, sequential/pipelined/parallel/stream controllers, scalar and memory reductions/folds, FSMs, termination, and timing directives.
- SRAM, DRAM, register files, scalar/FIFO registers, LUT/file LUT, views and aliases, dense/sparse transfers, gather/scatter, dimensions, masks, and tails.
- FIFO/LIFO, line/merge buffers, locks and locked memories, priority/round-robin consuming operations, external streams, frames, buses, blackboxes, and foreign modules.
- Host arrays/tensors/files, scalar/memory ports, data movement, specialization/generation, standard libraries, reports, tuning parameters, targets, banking, resource models, and DSE.

This is an inventory checklist, not a claim that all original backends share the same semantics. Source-family review and per-family dispositions are still required. The full rewrite must distinguish a target-specific implementation mechanism from a language capability; replacing the former must not silently discard the latter.

## Per-document inventory

For each row, record one of: preserve an observable rule, deliberately redesign it, replace its compiler mechanism, use it as backend evidence, or exclude an obsolete implementation detail with an explicit reason. An implementation stage and its evidence gates do not substitute for a semantic decision.

| ID | Original document | Required research destination | Disposition |
|---|---|---|---|
| DOC-001 | [[10 - Spec/10 - Language Surface/10 - Controllers\|controllers]] | Programming model and full-scope study | Review pending |
| DOC-002 | [[10 - Spec/10 - Language Surface/20 - Memories\|memories]] | Programming model and full-scope study | Review pending |
| DOC-003 | [[10 - Spec/10 - Language Surface/30 - Primitives\|primitives]] | Programming model and full-scope study | Review pending |
| DOC-004 | [[10 - Spec/10 - Language Surface/40 - Streams and Blackboxes\|streams-and-blackboxes-language-surface]] | Programming model and full-scope study | Review pending |
| DOC-005 | [[10 - Spec/10 - Language Surface/50 - Math and Helpers\|math-and-helpers]] | Programming model and full-scope study | Review pending |
| DOC-006 | [[10 - Spec/10 - Language Surface/60 - Host and IO\|host-and-io-language-surface]] | Programming model and full-scope study | Review pending |
| DOC-007 | [[10 - Spec/10 - Language Surface/70 - Debugging and Checking\|debugging-and-checking-language-surface]] | Programming model and full-scope study | Review pending |
| DOC-008 | [[10 - Spec/10 - Language Surface/80 - Virtualization\|virtualization-language-surface]] | Programming model and full-scope study | Review pending |
| DOC-009 | [[10 - Spec/10 - Language Surface/90 - Aliases and Shadowing\|aliases-and-shadowing]] | Programming model and full-scope study | Review pending |
| DOC-010 | [[10 - Spec/10 - Language Surface/99 - Macros\|macros-language-surface]] | Programming model and full-scope study | Review pending |
| DOC-011 | [[10 - Spec/10 - Language Surface/A0 - Standard Library/00 - Standard Library Index\|standard-library-index]] | Programming model and full-scope study | Review pending |
| DOC-012 | [[10 - Spec/10 - Language Surface/A0 - Standard Library/10 - BLAS and Linear Algebra\|standard-library-blas-linear-algebra]] | Programming model and full-scope study | Review pending |
| DOC-013 | [[10 - Spec/10 - Language Surface/A0 - Standard Library/20 - ML Primitives\|standard-library-ml-primitives]] | Programming model and full-scope study | Review pending |
| DOC-014 | [[10 - Spec/10 - Language Surface/A0 - Standard Library/30 - Sort and Scan\|standard-library-sort-scan]] | Programming model and full-scope study | Review pending |
| DOC-015 | [[10 - Spec/10 - Language Surface/A0 - Standard Library/40 - Meta Programming\|standard-library-meta-programming]] | Programming model and full-scope study | Review pending |
| DOC-016 | [[10 - Spec/20 - Semantics/10 - Effects and Aliasing\|effects-and-aliasing-semantics]] | Numeric and control studies | Review pending |
| DOC-017 | [[10 - Spec/20 - Semantics/20 - Scheduling Model\|scheduling-model]] | Numeric and control studies | Review pending |
| DOC-018 | [[10 - Spec/20 - Semantics/30 - Control Semantics\|control-semantics]] | Numeric and control studies | Review pending |
| DOC-019 | [[10 - Spec/20 - Semantics/40 - Memory Semantics\|memory-semantics]] | Numeric and control studies | Review pending |
| DOC-020 | [[10 - Spec/20 - Semantics/50 - Data Types\|data-types]] | Numeric and control studies | Review pending |
| DOC-021 | [[10 - Spec/20 - Semantics/60 - Reduction and Accumulation\|reduction-and-accumulation]] | Numeric and control studies | Review pending |
| DOC-022 | [[10 - Spec/20 - Semantics/70 - Timing Model\|timing-model]] | Numeric and control studies | Review pending |
| DOC-023 | [[10 - Spec/20 - Semantics/80 - Streaming\|streaming-semantics]] | Numeric and control studies | Review pending |
| DOC-024 | [[10 - Spec/20 - Semantics/90 - Host-Accel Boundary\|host-accelerator-boundary]] | Numeric and control studies | Review pending |
| DOC-025 | [[10 - Spec/30 - IR/00 - Argon Framework/10 - Symbols and Types\|Argon Symbols and Types]] | Compiler architecture study | Review pending |
| DOC-026 | [[10 - Spec/30 - IR/00 - Argon Framework/20 - Ops and Blocks\|Argon Ops and Blocks]] | Compiler architecture study | Review pending |
| DOC-027 | [[10 - Spec/30 - IR/00 - Argon Framework/30 - Effects and Aliasing\|Argon Effects and Aliasing]] | Compiler architecture study | Review pending |
| DOC-028 | [[10 - Spec/30 - IR/00 - Argon Framework/40 - Metadata Model\|Argon Metadata Model]] | Compiler architecture study | Review pending |
| DOC-029 | [[10 - Spec/30 - IR/00 - Argon Framework/50 - Staging Pipeline\|Argon Staging Pipeline]] | Compiler architecture study | Review pending |
| DOC-030 | [[10 - Spec/30 - IR/00 - Argon Framework/60 - Scopes and Scheduling\|Argon Scopes and Scheduling]] | Compiler architecture study | Review pending |
| DOC-031 | [[10 - Spec/30 - IR/00 - Argon Framework/70 - Rewrites and Flows\|Argon Rewrites and Flows]] | Compiler architecture study | Review pending |
| DOC-032 | [[10 - Spec/30 - IR/00 - Argon Framework/80 - Passes\|Argon Passes]] | Compiler architecture study | Review pending |
| DOC-033 | [[10 - Spec/30 - IR/00 - Argon Framework/90 - Transformers\|Argon Transformers]] | Compiler architecture study | Review pending |
| DOC-034 | [[10 - Spec/30 - IR/00 - Argon Framework/A0 - Codegen Skeleton\|Argon Codegen Skeleton]] | Compiler architecture study | Review pending |
| DOC-035 | [[10 - Spec/30 - IR/00 - Argon Framework/B0 - Compiler Driver\|Argon Compiler Driver]] | Compiler architecture study | Review pending |
| DOC-036 | [[10 - Spec/30 - IR/00 - Argon Framework/C0 - Macro Annotations\|Argon and Forge Macro Annotations]] | Compiler architecture study | Review pending |
| DOC-037 | [[10 - Spec/30 - IR/00 - Argon Framework/D0 - DSL Base Types\|Argon DSL Base Types]] | Compiler architecture study | Review pending |
| DOC-038 | [[10 - Spec/30 - IR/10 - Spatial Nodes/10 - Controllers\|spatial-ir-controllers]] | Compiler architecture study | Review pending |
| DOC-039 | [[10 - Spec/30 - IR/10 - Spatial Nodes/20 - Memories\|spatial-ir-memories]] | Compiler architecture study | Review pending |
| DOC-040 | [[10 - Spec/30 - IR/10 - Spatial Nodes/30 - Memory Accesses\|spatial-ir-memory-accesses]] | Compiler architecture study | Review pending |
| DOC-041 | [[10 - Spec/30 - IR/10 - Spatial Nodes/40 - Counters and Iterators\|spatial-ir-counters-iterators]] | Compiler architecture study | Review pending |
| DOC-042 | [[10 - Spec/30 - IR/10 - Spatial Nodes/50 - Primitives\|spatial-ir-primitives]] | Compiler architecture study | Review pending |
| DOC-043 | [[10 - Spec/30 - IR/10 - Spatial Nodes/60 - Streams and Blackboxes\|spatial-ir-streams-blackboxes]] | Compiler architecture study | Review pending |
| DOC-044 | [[10 - Spec/30 - IR/20 - Metadata/10 - Control\|Spatial IR Metadata - Control]] | Compiler architecture study | Review pending |
| DOC-045 | [[10 - Spec/30 - IR/20 - Metadata/20 - Access\|Spatial IR Metadata - Access]] | Compiler architecture study | Review pending |
| DOC-046 | [[10 - Spec/30 - IR/20 - Metadata/30 - Memory\|Spatial IR Metadata - Memory]] | Compiler architecture study | Review pending |
| DOC-047 | [[10 - Spec/30 - IR/20 - Metadata/40 - Retiming\|Spatial IR Metadata - Retiming]] | Compiler architecture study | Review pending |
| DOC-048 | [[10 - Spec/30 - IR/20 - Metadata/50 - Bounds\|Bounds metadata]] | Compiler architecture study | Review pending |
| DOC-049 | [[10 - Spec/30 - IR/20 - Metadata/60 - Math\|Math metadata]] | Compiler architecture study | Review pending |
| DOC-050 | [[10 - Spec/30 - IR/20 - Metadata/70 - Params\|Params metadata]] | Compiler architecture study | Review pending |
| DOC-051 | [[10 - Spec/30 - IR/20 - Metadata/80 - Types\|Types metadata helpers]] | Compiler architecture study | Review pending |
| DOC-052 | [[10 - Spec/30 - IR/20 - Metadata/90 - Blackbox\|Blackbox metadata]] | Compiler architecture study | Review pending |
| DOC-053 | [[10 - Spec/30 - IR/20 - Metadata/A0 - Debug\|Debug metadata]] | Compiler architecture study | Review pending |
| DOC-054 | [[10 - Spec/30 - IR/20 - Metadata/B0 - Rewrites\|Rewrites metadata]] | Compiler architecture study | Review pending |
| DOC-055 | [[10 - Spec/30 - IR/20 - Metadata/C0 - Transform\|Transform metadata]] | Compiler architecture study | Review pending |
| DOC-056 | [[10 - Spec/40 - Compiler Passes/10 - Flows and Rewrites\|flows-and-rewrites]] | Compiler architecture and HLS studies | Review pending |
| DOC-057 | [[10 - Spec/40 - Compiler Passes/20 - Friendly and Sanity\|friendly-and-sanity]] | Compiler architecture and HLS studies | Review pending |
| DOC-058 | [[10 - Spec/40 - Compiler Passes/30 - Switch and Conditional\|switch-and-conditional]] | Compiler architecture and HLS studies | Review pending |
| DOC-059 | [[10 - Spec/40 - Compiler Passes/40 - Blackbox Lowering\|blackbox-lowering]] | Compiler architecture and HLS studies | Review pending |
| DOC-060 | [[10 - Spec/40 - Compiler Passes/50 - Pipe Insertion\|pipe-insertion]] | Compiler architecture and HLS studies | Review pending |
| DOC-061 | [[10 - Spec/40 - Compiler Passes/60 - Use and Access Analysis\|use-and-access-analysis]] | Compiler architecture and HLS studies | Review pending |
| DOC-062 | [[10 - Spec/40 - Compiler Passes/70 - Banking\|banking]] | Compiler architecture and HLS studies | Review pending |
| DOC-063 | [[10 - Spec/40 - Compiler Passes/80 - Unrolling\|unrolling]] | Compiler architecture and HLS studies | Review pending |
| DOC-064 | [[10 - Spec/40 - Compiler Passes/90 - Rewrite Transformer\|rewrite-transformer]] | Compiler architecture and HLS studies | Review pending |
| DOC-065 | [[10 - Spec/40 - Compiler Passes/A0 - Flattening and Binding\|flattening-and-binding]] | Compiler architecture and HLS studies | Review pending |
| DOC-066 | [[10 - Spec/40 - Compiler Passes/B0 - Accum Specialization\|accum-specialization]] | Compiler architecture and HLS studies | Review pending |
| DOC-067 | [[10 - Spec/40 - Compiler Passes/C0 - Retiming\|retiming]] | Compiler architecture and HLS studies | Review pending |
| DOC-068 | [[10 - Spec/40 - Compiler Passes/D0 - Streamify\|streamify]] | Compiler architecture and HLS studies | Review pending |
| DOC-069 | [[10 - Spec/40 - Compiler Passes/E0 - Cleanup\|cleanup]] | Compiler architecture and HLS studies | Review pending |
| DOC-070 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/10 - Overview\|chiselgen-overview]] | Compiler architecture and HLS studies | Review pending |
| DOC-071 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/20 - Types and Ports\|chiselgen-types-and-ports]] | Compiler architecture and HLS studies | Review pending |
| DOC-072 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/30 - Memory Emission\|chiselgen-memory-emission]] | Compiler architecture and HLS studies | Review pending |
| DOC-073 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/40 - Controller Emission\|chiselgen-controller-emission]] | Compiler architecture and HLS studies | Review pending |
| DOC-074 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/50 - Streams and DRAM\|chiselgen-streams-and-dram]] | Compiler architecture and HLS studies | Review pending |
| DOC-075 | [[10 - Spec/50 - Code Generation/10 - Chiselgen/60 - Math and Primitives\|chiselgen-math-and-primitives]] | Compiler architecture and HLS studies | Review pending |
| DOC-076 | [[10 - Spec/50 - Code Generation/20 - Scalagen/10 - Overview\|scalagen-overview]] | Compiler architecture and HLS studies | Review pending |
| DOC-077 | [[10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics\|scalagen-numeric-reference-semantics]] | Compiler architecture and HLS studies | Review pending |
| DOC-078 | [[10 - Spec/50 - Code Generation/20 - Scalagen/30 - Memory Simulator\|scalagen-memory-simulator]] | Compiler architecture and HLS studies | Review pending |
| DOC-079 | [[10 - Spec/50 - Code Generation/20 - Scalagen/40 - FIFO LIFO Stream Simulation\|scalagen-fifo-lifo-stream]] | Compiler architecture and HLS studies | Review pending |
| DOC-080 | [[10 - Spec/50 - Code Generation/20 - Scalagen/50 - Controller Emission\|scalagen-controller-emission]] | Compiler architecture and HLS studies | Review pending |
| DOC-081 | [[10 - Spec/50 - Code Generation/20 - Scalagen/60 - Counters and Primitives\|scalagen-counters-and-primitives]] | Compiler architecture and HLS studies | Review pending |
| DOC-082 | [[10 - Spec/50 - Code Generation/20 - Scalagen/70 - Naming and Resource Reports\|Naming and resource reports]] | Compiler architecture and HLS studies | Review pending |
| DOC-083 | [[10 - Spec/50 - Code Generation/30 - Cppgen/10 - Cppgen\|Cppgen host code generation]] | Compiler architecture and HLS studies | Review pending |
| DOC-084 | [[10 - Spec/50 - Code Generation/30 - Cppgen/20 - Per-Target Files\|Cppgen per-target dependency files]] | Compiler architecture and HLS studies | Review pending |
| DOC-085 | [[10 - Spec/50 - Code Generation/40 - Pirgen/10 - Pirgen\|Pirgen Plasticine code generation]] | Compiler architecture and HLS studies | Review pending |
| DOC-086 | [[10 - Spec/50 - Code Generation/50 - Other Codegens\|Other non-Chisel codegens]] | Compiler architecture and HLS studies | Review pending |
| DOC-087 | [[10 - Spec/60 - Polyhedral Model/10 - ISL Binding\|ISL Binding]] | Analysis and HLS studies | Review pending |
| DOC-088 | [[10 - Spec/60 - Polyhedral Model/20 - Access Algebra\|Access Algebra]] | Analysis and HLS studies | Review pending |
| DOC-089 | [[10 - Spec/60 - Polyhedral Model/30 - Banking Math\|Banking Math]] | Analysis and HLS studies | Review pending |
| DOC-090 | [[10 - Spec/70 - Models and DSE/10 - Area Model\|Area Model]] | Compiler architecture and HLS studies | Review pending |
| DOC-091 | [[10 - Spec/70 - Models and DSE/20 - Latency Model\|Latency Model]] | Compiler architecture and HLS studies | Review pending |
| DOC-092 | [[10 - Spec/70 - Models and DSE/30 - Target Hardware Specs\|Target Hardware Specs]] | Compiler architecture and HLS studies | Review pending |
| DOC-093 | [[10 - Spec/70 - Models and DSE/40 - Design Space Exploration\|Design Space Exploration]] | Compiler architecture and HLS studies | Review pending |
| DOC-094 | [[10 - Spec/70 - Models and DSE/50 - Memory Resources\|Memory Resources]] | Compiler architecture and HLS studies | Review pending |
| DOC-095 | [[10 - Spec/70 - Models and DSE/60 - CSV Model Format\|CSV Model Format]] | Compiler architecture and HLS studies | Review pending |
| DOC-096 | [[10 - Spec/80 - Runtime and Fringe/10 - Fringe Architecture\|Fringe Architecture]] | Host workflow and HLS studies | Review pending |
| DOC-097 | [[10 - Spec/80 - Runtime and Fringe/20 - DRAM Arbiter and AXI\|DRAM Arbiter and AXI]] | Host workflow and HLS studies | Review pending |
| DOC-098 | [[10 - Spec/80 - Runtime and Fringe/30 - Ledger and Kernel\|Ledger and Kernel]] | Host workflow and HLS studies | Review pending |
| DOC-099 | [[10 - Spec/80 - Runtime and Fringe/40 - Hardware Templates\|Hardware Templates]] | Host workflow and HLS studies | Review pending |
| DOC-100 | [[10 - Spec/80 - Runtime and Fringe/50 - BigIP and Arithmetic\|BigIP and Arithmetic]] | Host workflow and HLS studies | Review pending |
| DOC-101 | [[10 - Spec/80 - Runtime and Fringe/60 - Instantiation\|Instantiation]] | Host workflow and HLS studies | Review pending |
| DOC-102 | [[10 - Spec/95 - Compiler Infrastructure/00 - Infrastructure Index\|Compiler Infrastructure]] | Compiler architecture and host workflow studies | Review pending |
| DOC-103 | [[10 - Spec/95 - Compiler Infrastructure/10 - Modeling Utilities\|Modeling Utilities]] | Compiler architecture and host workflow studies | Review pending |
| DOC-104 | [[10 - Spec/95 - Compiler Infrastructure/20 - Scala Executor\|Scala Executor]] | Compiler architecture and host workflow studies | Review pending |
| DOC-105 | [[10 - Spec/95 - Compiler Infrastructure/30 - Reports\|Compiler Infrastructure Reports]] | Compiler architecture and host workflow studies | Review pending |
| DOC-106 | [[10 - Spec/95 - Compiler Infrastructure/40 - Issues and Diagnostics\|Issues and Diagnostics]] | Compiler architecture and host workflow studies | Review pending |
