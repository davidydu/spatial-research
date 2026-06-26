---
type: hls-mapping
construct: ee109-mvp-blocker-matrix
category: rework
date: 2026-06-25
status: draft
---

# EE109 MVP Blocker Matrix

This matrix reclassifies the broad Spatial/Rust/HLS decision queue against the selected EE109 HLS MVP described in [[2026-06-25-ee109-hls-mvp-plan]]. The controlling corpus is the Stage 0-4 ladder: Lab1Part1 scalar register add, Lab 1 dense SRAM/DRAM load-store, `Lab2Part4LUT.scala`, `Lab2Part3BasicCondFSM.scala`, and `Lab3.scala`.

## Classification vocabulary

- `blocking-ee109`: the selected EE109 Stage 0-4 MVP cannot be generated, lowered, or verified without an explicit policy.
- `conditional-ee109`: blocks only if a conditional EE109 example, performance/reporting goal, or stricter simulator parity mode is pulled into the MVP.
- `defer-ee109`: a real full-Spatial/HLS decision, but the selected EE109 examples avoid the feature; reject or bypass it for the MVP.
- `irrelevant-ee109`: no selected or conditional EE109 path exercises the feature; it is outside the MVP slice.

## Required topic crosswalk

| Required topic | Matrix coverage |
|---|---|
| FMA | D-19 is `defer-ee109`; selected EE109 uses integer multiply/add reductions in `Lab3.scala:59-67`, not `FixFMA`, floating FMA, or fused precision behavior. |
| Unbiased rounding | D-09 and D-17 are `defer-ee109`; [[02-ee109-examples]] reports no explicit fixed-point formats, while selected examples use `Int`, predicates, and generic `T:Num` without fixed-point rounding. |
| FloatPoint clamp | D-18 is `defer-ee109`; selected EE109 has no `FloatPoint`, `Float`, or transcendental numeric path. |
| Streams | D-22 is `conditional-ee109` for stream back-pressure, but selected EE109 has no `StreamIn`, `StreamOut`, or stream controllers; [[02-ee109-examples]] marks streams absent from the corpus. |
| Blackboxes | D-01 and D-14 are non-blocking for EE109; [[02-ee109-examples]] reports no blackbox use and no external bus/blackbox interfaces. |
| BigIP | D-01 is `defer-ee109`; selected EE109 relies on integer arithmetic, `abs`, `mux`, LUTs, and local memories, not BigIP optional arithmetic. |
| OneHotMux | D-25 is `defer-ee109`; selected EE109 needs binary `mux` in `Lab3.scala:72`, while `Lab2Part3BasicCondFSM.scala:24` only comments on a Mux1H-style case and has no explicit `OneHotMux` API use. |
| FIFO/LIFO | D-22 is `conditional-ee109`; FIFO/LIFO are absent from the selected Stage 0-4 corpus, but Lab 1 FIFO becomes blocking if the user selects that lab example. |
| Host ABI | D-23 is `blocking-ee109`; Stage 0, `Lab2Part4LUT.scala:19-29`, and `Lab3.scala:16-23,78` require scalar args, ArgOut, DRAM pointers, `setArg`, `getArg`, `setMem`, and `getMatrix`. |
| Banking | D-07 is `blocking-ee109` for the Lab3 `par` subset; selected EE109 has `par` in `Lab3.scala:39,44,56,57,63,64,74` but no explicit `.bank` or `.banking` hints. |
| II/runtime model | D-08 and D-21 are `conditional-ee109`; functional compilation can proceed without DSE parity, but performance reports must record HLS-accepted II separately from Spatial metadata. |

## Decision queue classification

| ID | title | classification | EE109 rationale | initial policy | source link |
|---|---|---|---|---|---|
| D-01 | Choose the HLS policy for BigIP optional arithmetic operations and simulator placeholders. | defer-ee109 | BigIP is not exercised by the selected EE109 corpus. [[02-ee109-examples]] lists arithmetic, comparisons, `abs`, and binary `mux`, and marks blackboxes absent. | Reject BigIP optional arithmetic and simulator placeholders in the EE109 path; revisit vendor/library lowering after the MVP. | [[40 - Decision Queue]]; Q-036 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| D-02 | Define the grouping contract for priority and round-robin dequeues without relying on hash collisions. | irrelevant-ee109 | Selected EE109 has no priority dequeue, round-robin dequeue, FIFO/LIFO, or stream queue use; [[02-ee109-examples]] marks priority dequeue-style helpers outside the MVP surface. | Do not implement priority or round-robin dequeue grouping for EE109; reject these APIs if encountered. | [[40 - Decision Queue]]; Q-038 in [[20 - Open Questions]] |
| D-03 | Decide whether the HLS frontend preserves Spatial unsupported `while`/`return` behavior. | irrelevant-ee109 | Stage 0-4 examples use `Accel`, `Foreach`, `Sequential.Foreach`, `Pipe`, `Reduce`, and `FSM`, not source-level `while` or `return`. | Preserve the existing unsupported restriction for EE109 and fail fast on `while` or `return`. | [[40 - Decision Queue]]; Q-048 in [[20 - Open Questions]] |
| D-04 | Define the HLS memory-resource taxonomy and allocator catch-all behavior. | blocking-ee109 | Lab2 and Lab3 require `DRAM`, `SRAM`, `Reg`, `LUT`, `LineBuffer`, and `RegFile` (`Lab2Part3BasicCondFSM.scala:10-13`, `Lab2Part4LUT.scala:25`, `Lab3.scala:20,26,35,36`). | Define `ee109_mem_kind_v0` for `Reg`, `SRAM`, `LUT`, `RegFile`, `LineBuffer`, and dense `DRAM`; unsupported memory resources are explicit errors. | [[40 - Decision Queue]]; Q-079 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| D-05 | Design the Rust/HLS replacement for Chisel instantiation globals. | blocking-ee109 | Every selected example has one top-level `Accel`, and the MVP needs a deterministic HLS kernel/interface manifest instead of mutable Chisel/Fringe globals. | Use one generated HLS kernel function per `Accel`; capture target, scalar args, DRAM pointers, local memories, and file dependencies in an explicit manifest. | [[40 - Decision Queue]]; Q-083 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-06 | Choose the role of Spatial iteration-diff analysis in the HLS scheduler. | conditional-ee109 | Lab3 uses `par`, nested `Foreach`, and nested `Reduce`, but functional lowering can start with structured loops and rule-based pragmas before full `iterDiff` parity. | Treat `iterDiff` as diagnostic for the MVP; require a real dependence/schedule model only when chasing requested II or conflicting `par` schedules. | [[40 - Decision Queue]]; Q-103 in [[20 - Open Questions]] |
| D-07 | Choose the HLS banking-search pruning and partition-planning strategy. | blocking-ee109 | Lab3's `par` annotations over `LineBuffer`, `RegFile`, `SRAM`, and dense stores require enough partition/port planning to produce legal HLS arrays; explicit `.bank` and `.banking` hints are absent. | Implement a narrow HLS partition planner from `par` and local-memory access shape; do not port the full Spatial alpha/N/B banking search for the MVP. | [[40 - Decision Queue]]; Q-112 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-08 | Choose the latency source for HLS DSE. | conditional-ee109 | The selected MVP is functional-first. EE109 uses `par` and nested reductions in Lab3, but no acceptance criterion requires DSE latency parity before code generation works. | Use HLS reports later as the latency source; keep DSE and Spatial runtime-model parity out of the functional MVP gate. | [[40 - Decision Queue]]; Q-116 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-09 | Choose deterministic or nondeterministic unbiased rounding for the Rust simulator. | defer-ee109 | [[02-ee109-examples]] reports no explicit fixed-point types, no fixed-to-float conversions, and no unbiased rounding use in the selected EE109 examples. | Do not implement unbiased rounding for EE109; reject fixed-point rounding nodes or route them to a later numeric-semantics milestone. | [[40 - Decision Queue]]; Q-118 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| D-10 | Choose the Rust reference precision for transcendental functions. | defer-ee109 | Selected EE109 has no `sin`, `cos`, `exp`, `log`, `sqrt`, or `tanh`; Lab3 comments about `sqrt` but uses `abs` and addition at `Lab3.scala:72`. | Support integer arithmetic, comparisons, `abs`, and `mux`; reject transcendental functions in the EE109 MVP. | [[40 - Decision Queue]]; Q-130 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| D-11 | Choose Rust simulator semantics for `breakWhen`. | irrelevant-ee109 | No selected EE109 example uses `breakWhen`; loop/control needs are `Foreach`, `Sequential.Foreach`, `Pipe`, `Reduce`, and `FSM`. | Leave `breakWhen` unsupported in the EE109 compiler path. | [[40 - Decision Queue]]; Q-132 in [[20 - Open Questions]] |
| D-12 | Choose how Rust ownership handles Spatial mutable aliases. | defer-ee109 | Selected examples use DSL state (`Reg`, `SRAM`, `RegFile`) but do not rely on user-visible mutable aliasing or the `enableMutableAliases` compatibility flag. | Keep the MVP IR single-owner by construction; reject ambiguous mutable aliases until the broader Rust ownership policy is needed. | [[40 - Decision Queue]]; Q-137 in [[20 - Open Questions]] |
| D-13 | Choose whether HLS lowering preserves pipe holders as observable state. | blocking-ee109 | Lab3 uses `Pipe` at `Lab3.scala:42`, `RegFile` shift-in at `Lab3.scala:44`, and `Reg` accumulators at `Lab3.scala:53-54`; lowering must preserve observable state where the course kernel depends on it. | Preserve `Reg`, `RegFile`, and other pipe-holder state in generated C++ first; apply SSA cleanup only after proving it does not change the selected examples. | [[40 - Decision Queue]]; Q-139 in [[20 - Open Questions]] |
| D-14 | Define operational semantics for `Fork`, `ForkJoin`, and `PrimitiveBox`. | irrelevant-ee109 | Selected EE109 has no `Fork`, `ForkJoin`, `PrimitiveBox`, or blackbox controller use; every example has a single top-level `Accel`. | Keep these constructs outside the EE109 subset and reject them if encountered. | [[40 - Decision Queue]]; Q-140 in [[20 - Open Questions]] |
| D-15 | Choose simulation semantics for `ParallelPipe`. | irrelevant-ee109 | Lab3 uses `Pipe` and `par`, but [[02-ee109-examples]] reports no `ParallelPipe` or `Parallel` controller in the corpus. | Implement ordinary `Pipe` lowering for Lab3; leave `ParallelPipe` simulator semantics out of scope. | [[40 - Decision Queue]]; Q-141 in [[20 - Open Questions]] |
| D-16 | Choose the Rust policy for out-of-bounds simulator versus synthesis behavior. | conditional-ee109 | EE109 uses dense memory accesses and Lab3 boundary `mux` logic at `Lab3.scala:72`, but the selected examples are expected to be in-bounds when lowered correctly. | For functional HLS, generate normal C++ memory accesses plus optional debug assertions; only define Scalagen-compatible invalid-value OOB behavior if simulator parity becomes an acceptance target. | [[40 - Decision Queue]]; Q-142 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-17 | Choose the canonical unbiased rounding policy. | defer-ee109 | This duplicates the fixed-point rounding issue in D-09 for the EE109 slice; selected examples avoid explicit fixed-point formats and unbiased rounding. | Record as a later numeric-reference decision; do not let it block integer EE109 kernels. | [[40 - Decision Queue]]; Q-144 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-18 | Choose whether to reproduce `FloatPoint.clamp` heuristics bit-for-bit. | defer-ee109 | [[02-ee109-examples]] reports no `Float`, `Flt`, `FloatPoint`, or transcendental path in selected EE109. | Omit `FloatPoint.clamp` from the MVP; reject FloatPoint lowering until a floating example is selected. | [[40 - Decision Queue]]; Q-145 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| D-19 | Choose fused or unfused FMA precision for Rust+HLS. | defer-ee109 | Lab3 has integer multiply/add reductions (`Lab3.scala:59-67`), but no selected example uses `FixFMA`, `RegAccumFMA`, floating FMA, or fused precision behavior. | Lower integer multiply/add normally; leave fused versus unfused FMA precision to the later fixed/floating numeric milestone. | [[40 - Decision Queue]]; Q-146 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-20 | Choose value-only or cycle-aware `DelayLine` semantics. | defer-ee109 | Selected EE109 has no explicit `DelayLine`, and [[02-ee109-examples]] lists retiming helpers among features deferred for an EE109-only MVP. | Use value-functional lowering for the MVP; do not model cycle-aware retiming registers unless an HLS schedule test requires them. | [[40 - Decision Queue]]; Q-148 in [[20 - Open Questions]] |
| D-21 | Define the contract for HLS tool-accepted II versus compiler II metadata. | conditional-ee109 | EE109 examples prefer direct controller syntax and no explicit `.II`; Lab3 `par` may later need performance reporting, but functional correctness does not require exact `compilerII` parity. | Record requested II, emitted pragmas, and HLS-accepted II when reports exist; do not block Stage 0-4 functional compilation on II agreement. | [[40 - Decision Queue]]; Q-149 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-22 | Choose FIFO/LIFO/stream elastic simulation versus bounded back-pressure semantics. | conditional-ee109 | Selected Stage 0-4 excludes FIFO, LIFO, FIFOReg, StreamIn, and StreamOut, but the MVP plan names Lab 1 FIFO as a conditional addition. | If Lab 1 FIFO is selected, use bounded HLS FIFO semantics with overflow/back-pressure checks; otherwise reject FIFO/LIFO/stream APIs and defer stream semantics. | [[40 - Decision Queue]]; Q-150 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-23 | Define the Rust/HLS host ABI manifest. | blocking-ee109 | Stage 0 needs `ArgIn`/`ArgOut`; `Lab2Part4LUT.scala:19-29` uses `setArg` and `getArg`; Lab3 uses `setArg`, `setMem`, dense `DRAM`, and `getMatrix` at `Lab3.scala:16-23,78`. | Define `ee109_abi_manifest_v0` with scalar args, ArgOuts, dense DRAM pointers, set/get calls, kernel name, and test-oracle metadata before lowering beyond Lab1Part1. | [[40 - Decision Queue]]; Q-152 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |
| D-24 | Choose bit-exact or Cppgen-compatible fixed-point host conversion. | defer-ee109 | Selected EE109 uses integer scalar args and integer matrix data; [[02-ee109-examples]] reports no explicit fixed-point host conversion. | Use plain integer host conversion for EE109; reject fixed-point host values until a fixed-point example is selected. | [[40 - Decision Queue]]; Q-153 in [[20 - Open Questions]] |
| D-25 | Define multi-true `OneHotMux` semantics. | defer-ee109 | Selected EE109 needs binary `mux` in `Lab3.scala:72`; no explicit `OneHotMux` API appears, and the Lab2 FSM Mux1H mention is only a comment. | Implement binary `mux`; reject `OneHotMux` or assert one-hotness only when a selected example uses it. | [[40 - Decision Queue]]; Q-154 in [[20 - Open Questions]]; [[40 - Open HLS Questions]] |

## Top Open HLS Questions not captured cleanly by D IDs

Most of the top ten in [[40 - Open HLS Questions]] map directly to D IDs above: FMA to D-19, unbiased rounding to D-17 and D-09, FIFO/LIFO/streams to D-22, II to D-21, banking to D-07, host ABI to D-23, Chisel globals to D-05, OOB to D-16, OneHotMux to D-25, and runtime model to D-08.

| Question | classification | EE109 rationale | initial policy | source link |
|---|---|---|---|---|
| Q-114 dense-load latency model replacement | conditional-ee109 | Lab3 and the Lab 1 memory stage need dense `load` and `store` functionally, but Q-114 is about the latency model path rather than transfer correctness. `Lab3.scala:39` and `Lab3.scala:74` are covered by functional dense transfer lowering; DSE latency remains conditional. | Implement dense contiguous transfers for correctness; defer deleting, restoring, or retraining the dense-load latency model until the runtime/DSE milestone. | [[20 - Open Questions]]; [[40 - Open HLS Questions]] secondary candidate |
| Stream and blackbox semantic family beyond D-22 and D-14 | irrelevant-ee109 | The selected EE109 corpus has zero `StreamIn`, `StreamOut`, `StreamStruct`, and blackbox APIs, while [[02-ee109-examples]] explicitly marks streams and blackboxes absent. | Keep stream fields, stream filenames, Verilog/Spatial blackboxes, and blackbox back-pressure outside the EE109 MVP; reject them in the selected compiler path. | [[20 - Open Questions]] Q-151, Q-163, Q-164; [[02-ee109-examples]] |

## EE109 blocking set

The selected EE109 HLS MVP has five blocking decision rows:

- D-04 memory-resource taxonomy for the EE109 memory subset.
- D-05 HLS replacement for Chisel/Fringe instantiation globals.
- D-07 banking and partitioning subset for Lab3 `par`.
- D-13 pipe-holder state preservation for Lab3 `Pipe`, `Reg`, and `RegFile`.
- D-23 host ABI manifest for scalar args, ArgOuts, dense DRAM pointers, and host set/get calls.

The conditional rows are D-06, D-08, D-16, D-21, D-22, and Q-114. Everything else is either deferred or irrelevant for the selected EE109 MVP and should not block the first functional HLS path.
