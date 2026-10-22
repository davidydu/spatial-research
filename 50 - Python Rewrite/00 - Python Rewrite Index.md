---
type: moc
title: "Python Spatial research"
project: spatial-python
date_started: 2026-09-30
updated: 2026-10-22
---

Research before implementation: establish what Spatial programs mean in Python, decide how the compiler represents and checks them, then study HLS lowering.

**For students:** [[00 - Python Spatial Student Guide|Student guide preview]] starts with [[10 - Testing a Spatial Program|functional software tests]] and [[20 - Testing Your Own Project|custom final-project tests]]. The agreed student default is generated C++ execution from ordinary Python tests; the Python reference interpreter remains an internal verification tool. Public test helpers are planned and clearly marked.

**Current phase — 22 October:** a pure Python compiler checks and executes an admitted memory-program subset and generates C++ through a general backend. The saved scalar/shift batch now passes vendor C simulation, synthesis and RTL co-simulation. [[80 - Initial Compiler Goal]] owns the unfinished initial goal and public-workflow obligations.

**Latest hardware checkpoint:** [[2026-10-22-scalar-vitis-checkpoint]] records **12 projects and 32 cases** passing all three vendor stages at unchanged production `1e55eb8`: 27 normal completions and five expected faults. The batch includes scalar state, shifts, dot products, ordered updates, tiled maps and the independent directional-follower composition. Vitis preserved the checked logical behavior, but ignored the requested depth-one memory interfaces and chose scalar protocols. The subsequent local correction makes that policy explicit; validating the new wrapper against fresh synthesis reports is next, followed by a matched cost study before optimization.

[[2026-10-21-scalar-target-checkpoint]] owns the earlier local reference/native/wrapper agreement and **1,329 tests per source and isolated-package route**; the full suites were not rerun for this vendor-only checkpoint. [[2026-10-21-vitis-rtl-checkpoint]] remains the separate earlier four-kernel, nine-case hardware evidence. Reg, Reduce/Fold, public check/prepare, real resumption, full checked target planning and board integration remain open. The sequential measurements do not establish optimized parallelism or routed timing.

**Reference replay earlier on 21 October:** the Lab 1 tiled-scale example and public capture-once/specialize-twice example were replayed. The accepted 18 October checkpoint passed **1,244 tests from source and 1,244 from an isolated installed wheel**; the meeting checks were a bounded replay of that checkpoint. [[2026-10-21-python-progress-presentation|The dated presentation notes]] preserve its outputs, composition replay and unchanged file manifests.

The full-language architecture and [[07 - Python Implementation Readiness Audit|implementation-readiness review]] remain research checkpoints. [[PY-E002 - Spatial to Python Syntax Atlas|The course syntax atlas]] and [[60 - Course Syntax and Compiler Trace]] connect that proposal to the professor's examples. The full design uses captured kernels, Python-owned semantics and simulation, immutable program/plan records, and a checked HLS backend. xDSL is an optional derived adapter under [[PY-R017 - Compiler Representation Comparison]]. [[D-28]] remains proposed for professor review; current reference execution does not establish the complete design or hardware support.

**Latest local change:** [[2026-10-22-scalar-interface-checkpoint]] replaces inferred singleton ports with explicit seeds and separate output snapshots. The semantic core and C++ kernels are unchanged. Fresh synthesis/RTL evidence is pending.

## Read first

**Active implementation goal, 4 October:** David authorized [[80 - Initial Compiler Goal|the initial composed-memory compiler goal]]. Its frozen subset, independent expectations, unseen-composition gate and structural rewrite checks test the proposed plan locally before HLS. The detailed full-language architecture remains proposed; implementation progress is recorded separately from completed compiler support.

**Latest refinement:** [[11 - Design Refinement Iterations]] records the Codex/Fable repair, challenge and verification rounds. [[PY-R015 - Numeric Status Repair and Independent Oracles]] repairs the confirmed underflow rule; [[PY-R016 - Source and Host Workflow Refinement]] completes the source/host proposal; [[PY-R017 - Compiler Representation Comparison]] supports the new immutable-record recommendation; [[PY-R018 - Protocol Policy Refinement]] makes the remaining policy boundaries explicit. Earlier [[09 - Fable Design Review|findings]] and [[10 - Fable Reconciled Feedback|external feedback]] remain dated evidence.

<a href="https://davidydu.github.io/spatial-research-site/presentation/python/" data-router-ignore target="_blank" rel="noopener noreferrer">Open Spatial in Python — seven-slide presentation</a> · [[2026-10-22-python-pipeline-presentation|Ten-minute outline, speaker notes and dated evidence]]. The talk covers the fully Python compiler and one existing Lab 1 result through generated C++, HLS and RTL simulation. Interactive illustrations are explanatory; linked output records come from actual compiler runs.

1. [[D-27|Direction and authority]] — what the professor and David have settled.
2. [[05 - Python Professor Brief|Professor brief]] — the proposal, progress, main tradeoff, and approval boundary.
3. [[D-28|Architecture recommendation]] — selected design, alternatives, and reversal conditions.
4. [[00 - Implementation Design Index|Implementation design]] — concrete algorithms, interfaces, libraries, and independent acceptance cases.
5. [[04 - Python Implementation Roadmap|Implementation sequence]] — complete vertical paths, dependencies, and evidence gates after approval.
6. [[02 - Python Open Questions|Question register]] — research answers, adoption status, and remaining evidence.

[[03 - Managed Research Execution|Managed research execution]] records the completed research package, parallel work, and completion evidence.

[[70 - Engineering Architecture Map|Engineering architecture map]] — the big picture and implementation details on one zoomable Excalidraw canvas, with the EE109 lab sequence below.

[[01 - Python Research Plan|Research method]] · [[PY-R001 - Programming Model Study|Paired Python programs]] · [[PY-E001 - Initial Example Corpus|Shared example cases]]

## Foundation studies

For “what would Python look like?”, start with [[PY-E002 - Spatial to Python Syntax Atlas]]. It links complete proposed programs and the exact original spellings:

- [[PY-R012 - Lab1 Syntax and Host Mapping]] — ports, registers, memories, queues, scalar reductions and host workflow.
- [[PY-R013 - Controllers Reductions and Lab2 Mapping]] — control, memory reductions, FSMs and tiled GEMM.
- [[PY-R014 - Convolution Windows and Lab3 Mapping]] — line history, shift registers, lookup tables and convolution.
- [[08 - Course Syntax and Architecture Audit]] — source scope, independent checks, repairs and remaining implementation evidence.

- [[PY-R002 - Numeric and Reduction Semantics]] — exact arithmetic, literals, reductions, folds, and disagreements in the original implementation.
- [[PY-R003 - Control Memory and Effects]] — operation order, lazy branches, state lifetime, aliases, and the need for communicating tasks.
- [[PY-R004 - Capture Composition and Diagnostics]] — source versus builder, reusable kernels, notebook/file capture, and matched errors.

## Full language and compiler

- [[PY-R005 - Full Language Coverage and Migration]] — 18 language/infrastructure families and their migration and acceptance gates.
- [[PY-R006 - Compiler Architecture and Framework Choice]] — representations, xDSL comparison/probes, semantic ownership, and pass invariants.
- [[PY-R007 - Host Workflow Reproducibility and Validation]] — input preparation, packaging, artifact identity, diagnostics, and measured-workload targets.
- [[PY-R008 - Advanced State and Communication Protocols]] — queues, locks, windows, streams, transfers, FSMs, and cancellation.

## Proposed contracts

[[10 - Python Language Contract|Language and capture]] · [[20 - Python Numeric Contract|Numbers and reductions]] · [[30 - Python State and Protocol Contract|State and communication]] · [[40 - Python Compiler and HLS Contract|Compiler and HLS boundary]]

These distill the studies for review. Document review, design adoption, and implemented support have separate status fields.

## HLS studies

- [[2026-10-22-scalar-interface-checkpoint]] — explicit singleton transport, local regression and report-checking evidence; fresh vendor validation pending.

- [[2026-10-22-scalar-vitis-checkpoint]] — 12 projects and 32 cases through HLS/RTL, measured scaling and the scalar interface mismatch to resolve next.
- [[2026-10-21-scalar-target-checkpoint]] — locally validated scalar state and shifts, prepared scaling cases and next vendor measurements.
- [[2026-10-21-vitis-rtl-checkpoint]] — generated hardware, nine independent checks, measured baseline and remaining gaps.
- [[2026-10-21-generated-cpp-checkpoint]] — executable generated C++, reviewed boundaries, saved examples and next vendor steps.
- [[2026-10-21-hls-feasibility-checkpoint]] — agreed sequence change, current foundations, hardware risks and next audit.
- [[PY-R009 - HLS Boundary and Control Lowering]] — compiler/vendor responsibilities, control routes, faults, ABI, and evidence levels.
- [[PY-R010 - Memory Scheduling and Design Space Exploration]] — physical memory, transfers, banking, scheduling, and legal tuning.
- [[PY-R011 - Numeric Lowering and Intrinsic Profiles]] — numeric profiles, random/math operations, and vendor primitive compatibility.

## Documentation structure

| Location | What belongs here |
|---|---|
| `10 - Research/` | Questions, source readings, alternatives, experiments, limitations, and proposed conclusions |
| `20 - Examples/` | Shared example cases: source programs, intended behavior, expected outputs and effects; competing Python forms stay in the linked studies |
| Shared `20 - Research Notes/50 - Decision Records/` | Proposed and adopted choices with authority, alternatives, and reversal conditions; continue the existing D-number sequence |
| `30 - Implementation Design/` | Concrete algorithms, records, APIs, module ownership, library recipes, and implementation acceptance cases |
| `40 - Specification/` | Proposed Python language/compiler contracts for review, then adopted contracts with explicit authority |
| `50 - HLS Lowering/` | Mapping the checked Python program to hardware plans, HLS, and target validation |
| `60 - Validation/` | How claims will be checked; later, reproducible results and their limits |
| `70 - Student Guide/` | Student tutorials and testing examples, including open-ended projects; distinguish runnable tools from planned public interfaces |

[[00 - Python Validation Plan|Validation plan]] · [[01 - Python Coverage Ledger|Full-scope coverage ledger]] · [[02 - Python Research Review Log|Source checks and reviews]]

[[03 - Independent Architecture Review|Architecture review]] · [[04 - Independent Numeric Review|Numeric review]] · [[05 - Independent Protocol and HLS Review|Protocol/HLS review]] · [[06 - Python Research Completion Audit|Requirement-by-requirement audit]]

**Specification status:** proposed full contracts; the bounded initial implementation has its own authorized contract. **HLS status:** the original memory and newer scalar/shift batches have separate bounded vendor checkpoints. The scalar interface policy and manifest need to match the generated hardware before broader integration. Full checked target planning and wider hardware support remain open. Create new topic pages for substantive work, and link evidence rather than copying status claims between pages.

## How the earlier work fits

- `10 - Spec/` documents original Spatial. It is source evidence for this rewrite, not automatically the Python contract.
- `20 - Research Notes/` keeps the earlier research and the dated [[2026-09-30-pure-python-programming-model|direction]] and [[2026-09-30-pure-python-feasibility|feasibility]] notes. Their existing URLs remain valid.
- `30 - HLS Mapping/` contains earlier backend research. Recheck it against the eventual Python contract before adopting it.
- `35 - Python Surface Mapping/` contains the D-26 comparisons against the earlier external DSL. Use their findings and examples while reviewing any inherited Rust-specific policies.
- The frozen D-26 record, earlier decisions, presentation, and Rust prototype remain historical artifacts. New Python studies, examples, and questions use `PY-` identifiers; decisions continue in the shared D-number sequence with an explicit scope.

The vault is the source of truth; the website renders the same files. Progress stays in [[progress-log]]. Research conclusions must be traceable to inspected sources or recorded experiments; a subagent's opinion is not evidence by itself.
