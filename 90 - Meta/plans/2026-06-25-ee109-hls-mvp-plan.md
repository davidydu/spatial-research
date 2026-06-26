---
type: plan
project: spatial-spec
date: 2026-06-25
status: draft
scope: ee109-hls-mvp
source_notes:
  - "[[02-ee109-examples]]"
  - "[[03-mvp-subset-recommendation]]"
related:
  - "[[40 - Open HLS Questions]]"
  - "[[20 - Open Questions]]"
---

# EE109 HLS MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support compilation from selected EE109 Spatial examples to HLS C++ before attempting full Spatial semantic cleanup.

**Architecture:** Treat EE109 as the controlling corpus and build a narrow vertical compiler path around the examples, not the entire Spatial language. Resolve only design decisions that block those examples. Defer rare, unused, or non-EE109 features until a selected example forces them.

**Tech Stack:** Spatial CS217 source at `/Users/david/Documents/David_code/spatial`; EE109 course examples from local checkouts and the Digital Systems Design Lab site; Obsidian research vault; future HLS target assumed Vitis-compatible C++ unless the user selects a different tool.

---

## Current Goal Shift

The previous Phase 3 queue asked the project to settle broad Rust plus HLS architecture decisions. The new research priority is narrower:

- Compile selected EE109 lab examples from Spatial to HLS.
- Use the existing spec only as a reference.
- Do not resolve all 25 architectural decisions before starting.
- Classify each decision by whether it blocks the selected EE109 slice.

This plan supersedes the broad "resolve top HLS questions first" ordering for this research phase.

## Evidence Base

- The EE109 site presents the course as Spatial-based digital systems design, using the CS217 branch of Spatial and labs around controllers, memories, pipelining, parallelism, and Vitis/HLS flow.
- Lab 1 introduces DRAM, Register, SRAM, FIFO, ArgIn, ArgOut, Foreach, Fold, and Reduce.
- Lab 3's public page centers on Sobel-style convolution with LineBuffer, RegFile shift-register behavior, LUT kernels, SRAM row staging, and dense DRAM stores.
- The local Spatial source contains three EE109 tests: `Lab2Part3BasicCondFSM.scala`, `Lab2Part4LUT.scala`, and `Lab3.scala`.
- A local Lab 1 checkout exists at `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1`, including `Lab1Part1RegExample.scala`.

## Target Corpus

Freeze the selected examples before implementation. Start with a minimal ladder:

| Stage | Example | Why it comes here | Required Spatial surface |
|---|---|---|---|
| 0 | `Lab1Part1RegExample.scala` | Smallest end-to-end host/accelerator path | `@spatial`, `SpatialTest`, `runtimeArgs`, `ArgIn`, `ArgOut`, `setArg`, `getArg`, `Accel`, register read, assignment, integer add |
| 1 | Lab 1 SRAM/DRAM load-store example | First memory hierarchy path | `DRAM`, `SRAM`, dense `load`, dense `store`, `Foreach`, host arrays |
| 2 | `Lab2Part4LUT.scala` | Read-only local memory and index args | 2D `LUT`, dynamic indexing through ArgIn values, scalar host ABI |
| 3 | `Lab2Part3BasicCondFSM.scala` | First non-loop control state machine | `FSM`, nested conditionals, `Reg`, `SRAM`, dense `store`, `getMem` |
| 4 | `Lab3.scala` | Full course-relevant hardware kernel | 2D `DRAM`, `LineBuffer`, `RegFile`, `SRAM`, `LUT`, `Pipe`, nested `Foreach`, nested `Reduce`, `par`, `mux`, `abs`, `getMatrix` |

Conditional additions:

- Include Lab 1 FIFO only if the user selects that example. If selected, FIFO depth and back-pressure become blocking.
- Include Fold/MemReduce only if the selected Lab 1 controller examples require them.
- Do not include streams, blackboxes, floating point, file I/O, or explicit banking hints unless a selected example uses them.

## Decision Triage

### Blocking For EE109 HLS MVP

| Topic | Why blocking | Initial policy |
|---|---|---|
| Host ABI manifest | Needed for ArgIn, ArgOut, DRAM pointers, set/get calls, and test harnesses | Define a small `ee109_abi_manifest_v0` before lowering beyond Lab1Part1 |
| HLS top-level interface | Needed to turn `Accel` body into an HLS function | One generated kernel function per `Accel`; scalar args and DRAM pointers explicit |
| Dense DRAM transfer model | Needed for Lab 1, Lab 2 FSM, Lab 3 | Support contiguous dense slices first; reject gather/scatter |
| Local memory lowering | Needed for SRAM, LUT, RegFile, LineBuffer | Map to local arrays with generated partition pragmas where `par` demands ports |
| Controller lowering | Needed for Accel, Foreach, Sequential.Foreach, Pipe, Reduce, FSM | Lower to structured C++ loops and state machines; emit pragmas from `par` |
| Banking and partitioning subset | Needed for Lab3 parallelism and multi-port local memory access | Start with rule-based partitioning from `par`, not full Spatial banking search |
| Integer and Bool semantics | Used everywhere | Support `Int`, predicates, comparisons, mux, abs, plus/minus/multiply |
| Test oracle path | Needed to know HLS output is right | Reuse host gold models when available; generate C++ or Python harness around ABI manifest |

### Conditional Blocking

| Topic | Condition | Initial policy |
|---|---|---|
| FIFO/LIFO back-pressure | Only if Lab 1 FIFO is selected | Prefer bounded HLS FIFO semantics over Scalagen elastic queues for HLS; preserve a compatibility note |
| Fold/MemReduce | Only if selected Lab 1 controller examples require them | Implement as reductions after basic `Reduce` works |
| Runtime model and II reporting | Only if research output needs performance metrics early | Record requested II and HLS-reported II, but do not block functional compilation on exact model parity |

### Defer For EE109 MVP

| Topic | Reason to defer |
|---|---|
| FMA fused versus unfused semantics | EE109 selected examples are integer kernels without active FMA dependence |
| Unbiased rounding nondeterminism | No explicit fixed-point stochastic rounding in selected EE109 corpus |
| FloatPoint clamp, transcendental precision, MPFR policy | No floating-point or transcendental examples in the selected EE109 floor |
| Streams and external buses | Not in the local EE109 tests; public Lab 3 uses memory-backed convolution |
| Blackboxes and BigIP optional arithmetic | Not used by selected examples |
| OneHotMux multi-true policy | Lab2 FSM uses conditionals, not an explicit `oneHotMux` API in the selected source |
| Full DSE and area/latency model replacement | Useful later, not required for first functional HLS output |
| Explicit banking hints | EE109 examples rely on compiler-managed banking and `par`, not `.banking` or `.bufferAmount` |

## Output Artifacts To Create Next

These are the next durable files. They should be created before major compiler implementation starts.

| Artifact | Path | Purpose |
|---|---|---|
| Target corpus note | `/Users/david/Documents/Spatial Research/20 - Research Notes/30 - MVP Examples Analysis/04-ee109-hls-target-corpus.md` | Exact selected examples, source paths, feature inventory, and acceptance tests |
| Blocker matrix | `/Users/david/Documents/Spatial Research/30 - HLS Mapping/50 - EE109 MVP Blocker Matrix.md` | Decision queue reclassified as blocking, conditional, deferred, or irrelevant |
| Lowering map | `/Users/david/Documents/Spatial Research/30 - HLS Mapping/60 - EE109 HLS Lowering Map.md` | Spatial construct to HLS C++ lowering rules for the selected subset |
| Tracer bullet spec | `/Users/david/Documents/Spatial Research/30 - HLS Mapping/70 - Lab1Part1 Tracer Bullet.md` | End-to-end `ArgIn` to `ArgOut` compilation target, ABI, C++ shape, and verification oracle |

## Future Six-Agent Distribution Model

Do not dispatch subagents until the user explicitly approves the distribution. When the user gives full control, dispatch at most six GPT-5.5 xhigh agents at a time. Each agent gets a disjoint artifact or code area.

### Proposed Wave 1: Planning And Feasibility

| Agent | Ownership | Output |
|---|---|---|
| 1. Corpus Agent | Local EE109 files, public course pages, Lab 1 checkout | `04-ee109-hls-target-corpus.md` with exact selected examples and feature matrix |
| 2. Decision Agent | `20 - Open Questions.md`, `40 - Decision Queue.md`, decision records D-01 through D-25 | `50 - EE109 MVP Blocker Matrix.md` |
| 3. Frontend Agent | `@spatial`, `SpatialTest`, parser/staging path, IR for Lab1Part1 | Minimal frontend-to-IR path report |
| 4. ABI Agent | ArgIn, ArgOut, DRAM, set/get calls, Cppgen and Chisel host interfaces | `ee109_abi_manifest_v0` proposal |
| 5. Lowering Agent | Accel, Foreach, Sequential, Pipe, Reduce, FSM, mux, arithmetic | Controller and primitive HLS lowering report |
| 6. Memory Agent | DRAM, SRAM, LUT, RegFile, LineBuffer, dense load/store, `par` | Local memory and partitioning lowering report |

Manager responsibilities:

- Approve no file edits outside each agent's assigned artifact.
- Review returned artifacts before the next wave.
- Merge findings into the blocker matrix and lowering map.
- Keep user-facing progress in `90 - Meta/progress-log.md`.

### Proposed Wave 2: Tracer Bullet Design

Run only after Wave 1 artifacts exist.

| Agent | Ownership | Output |
|---|---|---|
| 1. Lab1Part1 ABI | Scalar args and result path | Concrete function signature and host harness shape |
| 2. Lab1Part1 IR | Staging logs and generated IR from existing Spatial | Minimal IR pattern to support |
| 3. HLS C++ Skeleton | Generated kernel C++ for scalar add | Compilable HLS C++ sketch |
| 4. Test Harness | Python or C++ oracle runner | Functional comparison harness |
| 5. Build Flow | Vitis-compatible invocation options | Minimal local or documented build command |
| 6. Risk Review | Cross-check gaps and unsupported constructs | Stop/go report for implementation |

## Task Plan

### Task 1: Freeze The Selected EE109 Corpus

**Files:**
- Create: `/Users/david/Documents/Spatial Research/20 - Research Notes/30 - MVP Examples Analysis/04-ee109-hls-target-corpus.md`
- Read: `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala`
- Read: `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala`
- Read: `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part4LUT.scala`
- Read: `/Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala`

- [ ] **Step 1: List the local target files**

Run: `find /Users/david/Documents/David_code -path '*/target/*' -prune -o -type f -name '*.scala' -print | rg 'Lab1Part1RegExample|Lab2Part3BasicCondFSM|Lab2Part4LUT|Lab3\\.scala'`

Expected: the four local files above are visible.

- [ ] **Step 2: Extract constructs per file**

Run: `rg -n 'ArgIn|ArgOut|DRAM|SRAM|LUT|LineBuffer|RegFile|Reg\\[|Accel|Foreach|Sequential|Pipe|Reduce|FSM|par|mux|abs|setArg|getArg|setMem|getMem|getMatrix|load|store' /Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab2Part4LUT.scala /Users/david/Documents/David_code/spatial/test/spatial/tests/ee109/Lab3.scala`

Expected: every construct in the target corpus table has at least one hit.

- [ ] **Step 3: Write the target corpus note**

The note must include:

- exact source path for each selected example
- one-line purpose per example
- feature matrix by example
- acceptance condition per example
- conditional examples not yet selected, especially FIFO and Fold/MemReduce

### Task 2: Build The EE109 Blocker Matrix

**Files:**
- Create: `/Users/david/Documents/Spatial Research/30 - HLS Mapping/50 - EE109 MVP Blocker Matrix.md`
- Read: `/Users/david/Documents/Spatial Research/20 - Research Notes/20 - Open Questions.md`
- Read: `/Users/david/Documents/Spatial Research/20 - Research Notes/40 - Decision Queue.md`
- Read: `/Users/david/Documents/Spatial Research/30 - HLS Mapping/40 - Open HLS Questions.md`

- [ ] **Step 1: Extract architecture-decision IDs**

Run: `rg -n '^## D-|^## Q-|FMA|rounding|FIFO|host ABI|banking|II|OneHotMux|BigIP|FloatPoint|OOB' '/Users/david/Documents/Spatial Research/20 - Research Notes/40 - Decision Queue.md' '/Users/david/Documents/Spatial Research/20 - Research Notes/20 - Open Questions.md' '/Users/david/Documents/Spatial Research/30 - HLS Mapping/40 - Open HLS Questions.md'`

Expected: decision and question references for the broad Phase 3 queue.

- [ ] **Step 2: Classify each top decision**

Use four statuses:

- `blocking-ee109`
- `conditional-ee109`
- `defer-ee109`
- `irrelevant-ee109`

Initial classification must match the Decision Triage section above unless the source evidence contradicts it.

- [ ] **Step 3: Write the blocker matrix**

Each row must include: ID, title, status, selected-example reason, initial policy, and source note link.

### Task 3: Define The Lab1Part1 Tracer Bullet

**Files:**
- Create: `/Users/david/Documents/Spatial Research/30 - HLS Mapping/70 - Lab1Part1 Tracer Bullet.md`
- Read: `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/Lab1Part1RegExample/src/Lab1Part1RegExample.scala`
- Read: `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part1RegExample/0000_Staging.log`
- Read: `/Users/david/Documents/David_code/lab-1-accelerator-bandits-1/logs/CS217/Lab1Part1RegExample/0094_ChiselGen.log`

- [ ] **Step 1: Capture the source kernel**

Record the exact host inputs, ArgIn values, Accel body, ArgOut assignment, and checksum condition.

- [ ] **Step 2: Define the generated HLS kernel shape**

Initial C++ shape:

```cpp
extern "C" void Lab1Part1RegExample_kernel(int argRegIn0, int argRegIn1, int *argRegOut) {
#pragma HLS INTERFACE s_axilite port=argRegIn0 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegIn1 bundle=control
#pragma HLS INTERFACE s_axilite port=argRegOut bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
  *argRegOut = argRegIn0 + argRegIn1;
}
```

This is the behavioral target, not the final generator implementation.

- [ ] **Step 3: Define the verification oracle**

Inputs: `3`, `5`.

Expected output: `8`.

Pass condition: generated kernel output equals host gold `M + N`.

### Task 4: Draft The EE109 HLS Lowering Map

**Files:**
- Create: `/Users/david/Documents/Spatial Research/30 - HLS Mapping/60 - EE109 HLS Lowering Map.md`
- Read: `/Users/david/Documents/Spatial Research/20 - Research Notes/30 - MVP Examples Analysis/04-ee109-hls-target-corpus.md`
- Read: `/Users/david/Documents/Spatial Research/30 - HLS Mapping/50 - EE109 MVP Blocker Matrix.md`

- [ ] **Step 1: Create lowering rows for each selected construct**

Rows must cover:

- host/test harness: `SpatialTest`, `runtimeArgs`, print/assert
- ABI: `ArgIn`, `ArgOut`, `DRAM`, `setArg`, `getArg`, `setMem`, `getMem`, `getMatrix`
- control: `Accel`, `Foreach`, `Sequential.Foreach`, `Pipe`, `Reduce`, `FSM`
- memory: `Reg`, `SRAM`, `LUT`, `RegFile`, `LineBuffer`
- operators: arithmetic, comparisons, `mux`, `abs`, `par`, dense ranges

- [ ] **Step 2: Assign HLS policy per row**

Each row must include: Spatial construct, selected example, HLS representation, required pragmas, unsupported cases, and first implementation stage.

- [ ] **Step 3: Mark unsupported cases explicitly**

Unsupported cases for the MVP:

- non-dense gather/scatter
- streams and external buses
- floating point and custom fixed point
- blackboxes
- explicit banking hints
- DSE parameter search

### Task 5: Update The Progress Log

**Files:**
- Modify: `/Users/david/Documents/Spatial Research/90 - Meta/progress-log.md`

- [ ] **Step 1: Append a June 25 entry**

Add one line noting that the broad Phase 3 queue has been reframed as an EE109 HLS MVP and link to this plan.

- [ ] **Step 2: Run markdown sanity checks**

Run: `rg -n 'T[B]D|TO[D]O|PLACE[H]OLDER|\\?\\?\\?' '/Users/david/Documents/Spatial Research/90 - Meta/plans/2026-06-25-ee109-hls-mvp-plan.md'`

Expected: no output.

Run: `git -C '/Users/david/Documents/Spatial Research' diff --check`

Expected: no output.

## Stop Conditions

Stop this planning phase when:

- the target corpus file exists,
- the blocker matrix exists,
- the lowering map exists,
- the Lab1Part1 tracer bullet spec exists,
- the progress log points to those artifacts,
- the user has approved the first six-agent execution wave.

Do not start compiler implementation until those artifacts exist or the user explicitly waives them.

## Manager Notes

Before any future subagent wave, report:

1. the six agents,
2. each agent's ownership,
3. each agent's output file,
4. whether the agent may edit files,
5. the verification the manager will run after all six return.

Wait for brief user approval before dispatch. After approval, use GPT-5.5 with xhigh reasoning for each subagent if available in the current tool surface.
