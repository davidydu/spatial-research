---
type: research-checkpoint
title: "HLS feasibility: keep the Python core, test hardware mapping earlier"
project: spatial-python
date: 2026-10-21
status: direction-agreed
---

# HLS feasibility checkpoint — 21 October 2026

## Agreed direction

David agreed with the scaling review: **keep the Python compiler foundation, but bring a small hardware feasibility check forward.** HLS remains the ultimate target. We should not finish every language feature before learning whether the supported programs map to useful hardware.

This revises the 17 October language-first sequencing in [[04 - Python Implementation Roadmap]]. It preserves the language contract, the full rewrite goal, Labs 1–3 as coverage anchors, and the unfinished [[80 - Initial Compiler Goal|initial acceptance obligations]]. It does not record professor approval of every detail in [[D-28]]. This checkpoint records a discussion and next research task; no backend implementation or HLS instance was started.

## Why the existing foundation is useful

Python runs the compiler passes. Those passes will produce HLS C++; the Python interpreter itself is not the hardware design.

The current checked program already retains the information needed to begin that lowering: exact Int32 rules, explicit SRAM/DRAM and views, shapes and lifetimes, backing identities, ordered effects, structured loops and parallelism requests. **SRAM capacities are already static and finite.** Immutable program records are separate from mutable invocation state. Keep the frontend, records, checker and reference engine; the review found no reason to restart in Rust or replace the semantic core with a framework.

This is an architecture assessment, not a synthesis result. Current reference correctness has substantially more evidence than target feasibility or hardware performance.

## Questions the hardware mapping must answer

| Existing meaning | Hardware question |
|---|---|
| Exact Index arithmetic and runtime domains | What finite widths and admitted input bounds preserve the operations? Which conditions must reject or retain guards? Runtime loop bounds alone do not imply unsynthesizability. |
| Static SRAM capacities and logical views | How are storage, banks, ports and strides implemented? Can required accesses sustain the intended throughput? |
| Aliases, full-source snapshot copies and ordered faults | Which copies/checks can be proved unnecessary? What buffers and fault behavior are required when they cannot? |
| Fresh local lifetimes and initialization | Can storage be safely reused? Is initialization implicit, eliminated by proof, or paid for in hardware? |
| Ordered effects and retained parallelism requests | Which dependencies permit pipelining or overlap? A parallelism request is not a proof of independence. |
| Host bindings and outputs | What are the target interfaces, alias restrictions and observable failure behavior? |

The simulator's debugging traces and step-by-step execution must not automatically become hardware state or force one operation per cycle. The proposed universal protocol-machine fallback could serialize ordinary workloads like a small processor. That is a risk to investigate, **not a measured failure**. Evaluate direct structured lowering for ordinary tiled programs, and use protocol machinery where the program needs it. Any optimization must preserve the adopted observable behavior; silently dropping guards, aliasing or snapshot semantics is not an optimization.

## Next work

1. **Write a bounded hardware-mapping and cost audit before further broad language expansion.** Trace the existing Lab 1 tiled-memory program and a harder composed program using views, helpers and aliases. For each operation, record what disappears at compile time, required finite widths and buffers, guards and dependencies, interface assumptions, lowering route and likely bottleneck. The tiled-scale example has two 16-element SRAM buffers, not one.
2. **Define a small general lowering experiment from that audit.** Select several programs and independent expectations; specify correctness, storage/resource and throughput criteria before implementation. Use common operation-based rules, never kernel names, lab labels or whole-program recognizers. Existing public check/prepare, genuine resumption and full initial-goal obligations remain pending; this research checkpoint does not declare them complete or cancel them.
3. **Collect target evidence in stages.** Generated C++ checks and functional tests come first; vendor C simulation, synthesis reports and C/RTL co-simulation establish separate claims. For finite channels, C simulation alone cannot establish correct backpressure/deadlock behavior. Judge hardware cost and performance as well as output correctness.

Keep the HLS instance stopped while preparing the audit and experiment. Notify David when the scoped plan, generated source and testbench are ready to use it; record the actual toolchain, device and clock then. Completion of every language family is no longer a prerequisite for that bounded check. The experiment must still meet the applicable scoped planning and validation gates; it is not full S6/S7 completion.

## Evidence boundary at this checkpoint

- **Verified path:** authored Python Spatial source → checked records → Python reference execution → independently specified expected values/effects. This is not automatic Scala-to-Python translation or a Scala/Python runtime differential test.
- **Recorded evidence:** compiler `0c79140` was inspected; the accepted 18 October checkpoint has 1,244 source tests and 1,244 isolated-wheel tests. The 21 October demos and accepted-composition replay are bounded checks, not a rerun of those full suites; see [[2026-10-21-python-progress-presentation]].
- **Still absent:** a Python-generated HLS backend, vendor synthesis, RTL co-simulation and board evidence. Historical Rust HLS results do not establish any of these for Python.

The source review used the pinned [record schema](https://github.com/davidydu/spatial-py/blob/0c79140/src/spatial/schema/registry.py), [static SRAM checks](https://github.com/davidydu/spatial-py/blob/0c79140/src/spatial/check/memory_maps.py), [Index semantics](https://github.com/davidydu/spatial-py/blob/0c79140/src/spatial/numeric/index.py) and [reference copy/execution rules](https://github.com/davidydu/spatial-py/blob/0c79140/src/spatial/runtime/reference.py). The proposed target structure remains in [[30 - State Simulator and HLS Blueprint]] and [[PY-R017 - Compiler Representation Comparison]].

AMD's documentation explains the relevant [memory-port and partitioning tradeoffs](https://docs.amd.com/r/2023.1-English/ug1399-vitis-hls/Array-Partitioning) and the [difference between ordinary stream C models and finite RTL channels](https://docs.amd.com/r/2023.1-English/ug1399-vitis-hls/C-Modeling-and-RTL-Implementation). These are background constraints, not evidence that our compiler has passed a particular installed vendor release.
