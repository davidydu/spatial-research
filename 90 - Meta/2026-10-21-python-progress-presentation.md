---
type: reference
title: "Python Spatial — progress presentation, 21 October 2026"
project: spatial-python
date: 2026-10-21
verified: 2026-10-21
scope: "Seven slides on working reference execution, reusable features and the next implementation steps"
---

# Python Spatial: working reference, broader Spatial next

**Later discussion, 21 October:** [[2026-10-21-hls-feasibility-checkpoint]] revises
the next-work sequence: hardware-mapping research now, then a bounded HLS
feasibility experiment before all language families are complete. The slides and
script below preserve the earlier briefing; the checkpoint and roadmap own the
current direction. The recorded execution evidence is unchanged.

[Open the presentation](https://davidydu.github.io/spatial-research-site/presentation/python/) · [[05 - Python Professor Brief|Short professor brief]] · [[80 - Initial Compiler Goal|Current implementation evidence]].

Seven slides, about ten minutes before discussion. The professor already knows Spatial. Lead with what now runs, how the pieces connect, and what comes next. Keep source code and detailed compiler internals for questions. These notes supersede the meeting status and sequence in [[2026-10-01-python-professor-presentation-outline|the earlier presentation]]; preserve that dated outline as history.

## Story and timing

| Slide | Headline | Time | Elapsed |
|---|---|---|---|
| 1 | Python Spatial now runs memory programs | 1:00 | 1:00 |
| 2 | One program model connects the system | 1:30 | 2:30 |
| 3 | The first Lab 1 memory example works | 1:30 | 4:00 |
| 4 | The same rules support new combinations | 1:45 | 5:45 |
| 5 | We check more than the final answer | 1:45 | 7:30 |
| 6 | Finish the workflow. Broaden the language. | 1:30 | 9:00 |
| 7 | A working reference. Broader Spatial next. | 1:00 | 10:00 |

This is a pacing target, not a measured rehearsal. Allow a short pause on the pipeline, tile picture and evidence comparison. The architecture explorer is available for discussion; opening every detailed section will exceed the ten-minute main talk.

## 1. Python Spatial now runs memory programs · 1:00

**Main idea:** Python source, compiler and reference execution now form a working path for an admitted memory-program subset.

### Spoken script

The main update is that Python Spatial now runs small memory programs through a real compiler and reference execution path. We can start with Spatial written in a defined Python subset, check it, prepare its inputs, and obtain the expected results.

The frontend, compiler and reference engine are implemented in Python. Spatial still has explicit arithmetic, memory and control rules. HLS remains the eventual hardware destination.

I’ll show one concrete tiled-memory result, then the reusable features that now work together. I’ll also separate what we have demonstrated from the public workflow and language coverage that still need work. The old presentation stopped at compiler components; today the useful change is that these pieces execute programs together.

**Evidence:** [current source-to-reference runner](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_lab1_reference.py#L22-L55) and [[80 - Initial Compiler Goal]]. The latest frozen production files were checked again on 21 October; the full accepted package runs are dated 18 October.

## 2. One program model connects the system · 1:30

**Main idea:** Source capture and specialization produce a candidate; the shared checker establishes the program consumed by reference execution. The full architecture also describes future hardware work.

### Spoken script

The organizing idea is one explicit model of the Spatial program. Source is captured as data. Compile-time settings specialize that source into a candidate program. The checker then validates the admitted program before the reference engine runs it with prepared inputs.

The model records the arithmetic, storage, views, control and order of state changes. Python is the implementation language, while these records and rules define Spatial’s behavior. That is how fixed-width integer overflow can remain predictable even though ordinary Python integers have different behavior.

The same model gives us a place to add reusable language features. A helper, a memory window and a loop participate in the same checking and execution rules. We do not need a separate compiler path for each example.

The embedded engineering map shows the larger design, including future transformations, saved artifacts and hardware planning. HLS will require additional target-specific work and validation. For today, the solid result is the source-to-reference path for the supported subset. The map is useful for seeing how that path fits into the eventual system.

**Evidence:** [[70 - Engineering Architecture Map|Full engineering architecture]]; [current architecture and scope](https://github.com/davidydu/spatial-py/blob/8152d4e/CONTEXT.md#L15-L54); [public capture trust boundary](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/plans/2026-10-18-public-source.md#L63-L86). Source bodies, decorators and annotations are not executed during capture. The full map describes planned capabilities as well as implemented ones.

## 3. The first Lab 1 memory example works · 1:30

**Main idea:** A real tiled DRAM/SRAM source completes ordinary and overflow cases through the reference path.

### Spoken script

The first concrete example is a tiled-scale memory program based on Lab 1. It processes thirty-two values in two tiles of sixteen. Each tile moves from external memory into local SRAM, is multiplied by a scale, and is written back.

With inputs zero through thirty-one and a scale of two, the output is zero, two, four, and so on through sixty-two. A second input includes integer boundary values, and its overflow results agree with the independently specified Int32 expectations.

This is actual source going through the compiler, checking, input preparation and reference execution. The run also records the local allocations, transfers, reads, writes and cleanup. Seven required checks are proved during checking; four are enforced by runtime guards.

Both cases were rerun today. Their values and recorded behavior match the saved expectations. This establishes the tiled-memory example and the features it uses. Lab 1’s registers, FIFOs and reduction or fold families remain to be implemented, and this result does not establish hardware behavior.

**Evidence:** [11-line source](https://github.com/davidydu/spatial-py/blob/8152d4e/tests/fixtures/sources/lab1_tiled_scale.py#L1-L11), [runner and oracle comparison](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_lab1_reference.py#L22-L55), [21 October output](https://davidydu.github.io/spatial-research-site/presentation/python/assets/lab1-reference-fresh-output.json). Each case reports 4 allocations, 4 snapshot copies, 96 writes, 32 reads and 4 deallocations. The historical output's revision identifier differs from today's identifier; see the verification record below.

## 4. The same rules support new combinations · 1:45

**Main idea:** Memory, control, helpers and compile-time configuration compose through the same path.

### Spoken script

The progress beyond that one example falls into four groups. First, memory: local storage, transfers, named views and helpers that return memory windows. Second, control: ordinary branches, loops and scopes with explicit cleanup. Third, helpers: calls, nested helpers and captured values or memory. Fourth, compile-time configuration: constants, parameters, helper specialization and finite static expansion.

The useful point is how these features combine. A helper can work on a selected memory window. A compile-time choice can generate scopes that each allocate their own scratch memory. Those pieces still pass through the same checker and reference engine.

The latest increment makes source capture and specialization public. One captured template can be used with different settings. In the example, inputs three, seven and eleven with bias minus two produce one, five and nine. The same template, specialized for two inputs with bias four, produces seven and eleven. The two runs use three and two fresh scratch lifetimes, and the original host buffers remain unchanged.

The public entry point is still deliberately bounded: one core module with no dependencies. Checking, preparation and execution in this example currently use the private bridge. Finishing that public invocation workflow is the next step.

**Evidence:** [feature support ledger](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/support-ledger.md#L30-L151), [capture-once example](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_public_source.py#L19-L67), [21 October output](https://davidydu.github.io/spatial-research-site/presentation/python/assets/public-source-fresh-output.json), [single-module boundary](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/plans/2026-10-18-public-source.md#L43-L61). Closed scalar aliases are supported; resource aliases remain excluded by the pinned contract.

## 5. We check more than the final answer · 1:45

**Main idea:** Independent outputs, ordered effects and fresh compositions provide different kinds of evidence.

### Spoken script

A matching output is necessary, but memory programs have other ways to go wrong. A temporary buffer might outlive its scope, a write might happen in the wrong order, or a fault might occur after an effect that should never have happened.

Our checks therefore include independently written expected values and ordered observations of calls, memory operations, branches and cleanup. Some tests compare source programs with separately written common program records. Other tests deliberately exercise rejected programs or faults.

We also freeze the implementation before an independent author writes a new composition. The latest accepted case combines static expansion, a nested helper, a mutable scalar cell, scratch SRAM and a runtime branch. Its three handwritten answers are sixty, zero and minus nine. All expected ordered events match as well. That unchanged test was replayed today, and all three scenarios passed.

The accepted package checkpoint on eighteen October passed twelve hundred and forty-four tests from source, and the same number from an isolated installed wheel. Today’s checks were narrower: the two demonstrations, that composition, and unchanged file manifests. These results give us concrete regression and composition evidence. Full-compiler acceptance and useful-workload performance measurements remain separate work.

**Evidence:** [fresh composition and literal expectations](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source-acceptance-second.md#L15-L50), [pin and original replay](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source-acceptance-second.md#L52-L79), [1,244-test package verification](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source.md#L69-L87). The composition checks 26 / 26 / 2 ordered events. The first post-freeze case required an observer correction and remains a regression; the second independent case supplies fresh acceptance.

## 6. Finish the workflow. Broaden the language. · 1:30

**Main idea:** Complete public invocation and real resumption, then use Labs 1–3 to prioritize reusable language families. HLS follows planned language support.

### Spoken script

The next implementation step is to expose checking and input preparation through a documented public workflow, using the checker and preparation path we already have.

Before exposing public simulation, we also need real resumption: a run should be able to stop at a supported effect boundary and continue with validated state and cumulative budgets, without replaying effects. The current private resource-limit result does not provide that continuation.

After the current initial-contract work, the labs give us a useful language sequence. Lab 1 adds registers, FIFOs and reductions or folds. Lab 2 brings memory reductions, finite-state control, lookup tables and fixed-point tiles. Lab 3 brings line and shift buffers and convolution. We should implement those as reusable features and test new combinations as we go.

HLS remains the agreed destination after the planned language and reference support. The trigger for starting vendor validation is a scoped target program, generated code and a testbench. That makes the next stages concrete while keeping the current reference result separate from a hardware claim.

**Evidence:** [current public-workflow restart task](https://github.com/davidydu/spatial-py/blob/work/initial-reference/PROJECT_STATE.md#L97-L116), [[04 - Python Implementation Roadmap|language and HLS sequence]], [[80 - Initial Compiler Goal|remaining initial-goal obligations]]. Dependency linking, artifacts, pending effects, cache/direct agreement, verified editing and final whole-compiler acceptance remain open. Keep the HLS instance stopped until the scoped code and testbench are ready for vendor validation.

## 7. A working reference. Broader Spatial next. · 1:00

**Main idea:** The project has moved from tested components to executable compositions; the next work completes the public workflow and grows coverage.

### Spoken script

The takeaway is that we now have a working Python reference path for a useful memory-program subset. The tiled Lab 1 example runs, reusable features compose, and one captured source can produce multiple checked and executed specializations through the current bridge.

The next milestone is a complete public invocation workflow, followed by broader language coverage guided by the three labs. HLS remains the later hardware stage.

The links here provide the research site, the full architecture, the progress record, and both repositories. We can use them to inspect a result or discuss a missing capability without turning the main presentation into a code walkthrough. The most useful discussion now is which language combinations should shape the next acceptance examples.

**Links on screen:**

- [Research site](https://davidydu.github.io/spatial-research-site/)
- [Full architecture](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/70---Engineering-Architecture-Map.html)
- [Current progress and acceptance](https://davidydu.github.io/spatial-research-site/50---Python-Rewrite/30---Implementation-Design/80---Initial-Compiler-Goal.html)
- [Compiler repository — implementation branch](https://github.com/davidydu/spatial-py/tree/work/initial-reference)
- [Research repository](https://github.com/davidydu/spatial-research)

## Verification record — 21 October 2026

This is a bounded meeting replay. It does not replace the complete accepted package runs.

| Item | Evidence and result |
|---|---|
| Current compiler checkout | `work/initial-reference`, HEAD `0c7914057970d1cdf3b6a3361f68e761c812b0a6`; CPython 3.14.5 |
| Accepted behavior | Behavior `da6c722`; production freeze `06060a0`; acceptance `8152d4e`, 18 October |
| Lab 1 replay | `examples/run_lab1_reference.py` exits successfully; ordinary and overflow outputs, demand counts and trace counts agree with the recorded cases |
| Public-source replay | `examples/run_public_source.py` exits successfully; the entire parsed JSON equals the saved public-source output |
| Independent composition replay | `tests.runtime.test_public_source_fresh_second`: 1 test covering 3 scenarios, PASS in 0.905 s |
| Current files versus accepted manifests | All 75 production entries and all 268 execution entries match their recorded SHA-256 values |
| Complete package suites | Recorded 18 October: 1,244 source tests in 151.331 s and 1,244 isolated-wheel tests in 151.417 s; not rerun on 21 October |

The fresh composition file still hashes to `d2fcbceb82576765e32f693e51a00146dfb8f4f1a4edc0e0856558ab898400fb`, matching its precommitted pin. The production and execution manifests are [saved with the accepted checkpoint](https://github.com/davidydu/spatial-py/tree/8152d4e/docs/evidence). Test timings are observations from verification, not performance benchmarks.

The Lab 1 JSON has one metadata difference. The recorded `semantic_revision` is `f021a0009281610e753d63ccfcd112f20b62d5da2ac3b59eb507f1cbc66c07dc`; today's is `95002f6b98d592353790a951a079db183f0fe37440dc53d85b32004751be4472`. Every other top-level field, including both complete case observations, matches. The historical record is preserved; do not describe the full Lab 1 JSON as identical.

For reproduction from the implementation checkout, use its `.venv` with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=src` for the two example scripts; use `PYTHONPATH=src:.` for the named unittest. No compiler source or tracked test was edited during this replay.

## Presentation boundaries and fallback

- **Reference versus hardware:** show the results as Python reference execution. No HLS, synthesis, FPGA performance or full Lab 1 claim follows.
- **Public versus private:** capture and specialization are public for one core module with empty dependencies. Checking, preparation and execution use the private bridge. A captured template alone is not a checked program.
- **Design versus completion:** the architecture explorer includes planned artifacts, transformations, continuations and target machinery. Use the current progress page for implementation status. Visual illustrations are not live compiler executions.
- **If a live demo is inconvenient:** use the two dated output records linked above. State that they were replayed on 21 October. The output records and literal values remain useful without a terminal or repository access.
- **If the architecture explorer or network fails:** use the visible source → specialization → checking → reference path. The full map and linked evidence can be opened after the talk.
- **If asked whether Spatial is complete:** identify the demonstrated memory subset, the private invocation boundary and the remaining initial-goal/lab obligations. The 1,244-test count and bounded fresh composition do not establish every possible program or the final whole-compiler gate.
