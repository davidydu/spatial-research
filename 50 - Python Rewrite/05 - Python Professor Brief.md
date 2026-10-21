---
type: reference
title: "Python Spatial — professor discussion brief"
project: spatial-python
date: 2026-10-01
updated: 2026-10-21
verified: 2026-10-21
---

<a href="https://davidydu.github.io/spatial-research-site/presentation/python/" data-router-ignore target="_blank" rel="noopener noreferrer">Open the seven-slide presentation</a> · [[2026-10-21-python-progress-presentation|Ten-minute speaker notes and dated evidence]].

**Python Spatial now runs small memory programs through a Python compiler and reference engine.** Actual source reaches checking, input preparation and execution for the supported subset. HLS remains the eventual hardware destination.

The talk leads with this concrete progress, explains how the system connects, and closes with the public workflow and language families still to build. The professor knows Spatial; detailed syntax and source code can stay in the linked evidence.

## One program model connects the system

Captured source → specialization → shared checking → prepared reference execution. Python implements the compiler; explicit Spatial rules define arithmetic, storage, views, control and the order of effects. Captured bodies, decorators and annotations are read as source data, not executed during acquisition.

The [[70 - Engineering Architecture Map|embedded architecture]] shows how this path fits into the proposed full system, including future artifacts, transformations and HLS planning. The drawing includes unimplemented capabilities. [[80 - Initial Compiler Goal]] owns current support and acceptance status.

## A concrete memory example works

The tiled-scale part of Lab 1 processes **32 values in two tiles of 16**, loading DRAM into SRAM, multiplying and storing the result. With inputs `0…31` and scale `2`, it produces `0,2,…,62`. An independent Int32-overflow vector also passes. Checking proves seven demands and enforces four with runtime guards.

Both cases were rerun on **21 October 2026**, with outputs and effect counts matching their saved expectations. This is reference execution of the tiled-memory example. Reg, FIFO and Reduce/Fold coverage for the rest of Lab 1 remains open. See the [source and runner](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_lab1_reference.py#L22-L55) and [fresh output](https://davidydu.github.io/spatial-research-site/presentation/python/assets/lab1-reference-fresh-output.json).

## Reusable features now compose

The working path includes memory views and transfers; ordinary branches and loops; helpers and lexical captures; borrowed memory results; constants and compile-time parameters; and ordered scopes with finite static expansion. Their [support ledger](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/support-ledger.md#L30-L151) links positive, negative and composition evidence.

The latest public API captures one source template and specializes it repeatedly. The [example](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_public_source.py#L19-L67) produces **`[1,5,9]`** and **`[7,11]`** from two settings, with **3 / 2 fresh scratch lifetimes** and unchanged host buffers. Today's replay exactly matches its [saved output](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/public-source-reference-output.json). Public capture/specialization supports one core module with empty dependencies; checking, preparation and execution still use the private bridge.

## Evidence beyond the final answer

Independent literal expectations check outputs and ordered effects. A fresh composition authored after the production freeze combines static expansion, a nested helper, a mutable cell, scratch SRAM and a runtime branch. It produces **`60 / 0 / -9`**, matching all **`26 / 26 / 2`** ordered events. The unchanged test passed again on 21 October. See the [pin and composition evidence](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source-acceptance-second.md#L15-L79).

The accepted **18 October** checkpoint passed **1,244 tests from source and 1,244 from an isolated installed wheel**. Today's bounded replay checked the two demonstrations, the fresh composition and both frozen file manifests; it did not rerun the complete suites. All 75 production entries and 268 execution entries still match. The [[2026-10-21-python-progress-presentation#Verification record — 21 October 2026|dated verification record]] separates these observations and records the Lab 1 revision-metadata difference. Test counts do not establish full Spatial support or useful-workload performance.

## Next: public workflow, broader language, then HLS

Expose public checking and input preparation through the existing implementation. Add real validated resumption with cumulative budgets before exposing public simulation. Current private resource-limit results have no continuation. Dependency linking, artifacts, verified editing and the remaining initial-goal acceptance work stay open.

Then expand reusable language families using the [[04 - Python Implementation Roadmap|Labs 1–3 sequence]]: **Lab 1 Reg/FIFO/Reduce/Fold → Lab 2 memory reductions/FSM/LUT/fixed-point tiles → Lab 3 line/shift buffers and convolution**. Keep each increment executable and require new feature combinations.

HLS follows planned language/reference support. Keep the instance stopped until a scoped target program, generated code and a testbench are ready for vendor validation. Current results establish reference behavior; hardware results need their own evidence.

**Takeaway:** a working reference path now connects the compiler components. Finish its public workflow and broaden Spatial coverage next.

## Useful links

[[00 - Python Rewrite Index|Research home]] · [[70 - Engineering Architecture Map|Full architecture]] · [[80 - Initial Compiler Goal|Progress and acceptance]] · [[04 - Python Implementation Roadmap|Roadmap]] · [[01 - Python Coverage Ledger|Language coverage]]

[Research site](https://davidydu.github.io/spatial-research-site/) · [Compiler repository](https://github.com/davidydu/spatial-py/tree/work/initial-reference) · [Research repository](https://github.com/davidydu/spatial-research)
