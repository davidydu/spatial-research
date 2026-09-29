---
type: "research"
decision: "D-26"
angle: "12"
discriminates: core-language
sources:
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-35"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part5_gemm_fixed_32.scala:29-58"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-58"
  - "spatial-rs@eb49d8b:docs/language-spec.md:35-53"
  - "spatial-rs@eb49d8b:docs/language-spec.md:263-301"
  - "spatial-rs@eb49d8b:docs/language-spec.md:303-348"
  - "spatial-rs@eb49d8b:docs/language-spec.md:611-617"
  - "spatial-rs@eb49d8b:docs/language-spec.md:626-659"
  - "spatial-rs@eb49d8b:docs/language-spec.md:818-850"
  - "spatial-rs@eb49d8b:docs/language-spec.md:886-910"
  - "spatial-rs@eb49d8b:docs/language-spec.md:963-969"
  - "[[D-26#Reversal conditions]]"
  - "[[2026-09-25-python-rust-architecture-research-design]]"
  - "[Reproduction archive](assets/d26-interpreter-spike.zip)"
verified: ["2026-09-28"]
status: draft
---

## Scope

Compare two small node interpreters over identical preconstructed IR: installed CPython and release Rust. This is bounded runtime evidence for [[D-26]], not a compiler implementation, a full acceptance test, or a comparison of student surfaces. Both run the same operations with exact signed Int32 and `FixPt<Signed,24,8>` arithmetic. No NumPy, native numerical kernel, JIT, vendor tool or production repository code participates.

**The registered k=10 simulator-loss condition is triggered for the tested pure-CPython interpreter route.** D-26 expressly admits precedent or spike evidence, and the original research design authorizes a toy-versus-toy comparison on one lab. Requiring a complete compiler before counting this result would add a condition after measurement. This negative result counts against P-* candidates using the tested runtime approach; it does not distinguish X from E or prove that every Python compiler core with a different execution engine must fail.

The workloads, arithmetic, oracle, sizes, repetitions, timers and limits were written in `preregistration.md` before implementation and measurement. The primary run was followed by an independent correctness/reproduction audit without changing frozen sources or replacing primary results. Local file times and the research transcript establish this sequence; hashes are identity checks, not an externally timestamped preregistration. [Reproduction archive](assets/d26-interpreter-spike.zip) contains the preregistration, source, shared programs, full outputs, raw timing samples, environment, hashes and audit evidence. After extraction, `python3 run.py` reproduces the experiment with existing Python and rustc; no additional package is required.

## Findings

### Workloads and shared semantics

[measured] **The frozen primary workloads are dense32, nested-fold32 and GEMM32, all tile16.** Dense follows the original Lab1Part2's two SRAM buffers and multiply-by-3; the canonical Scale example instead uses one in-place tile. This spike deliberately preserves the original kernel's allocation/copy work. Sources: `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-35`; `spatial-rs@eb49d8b:docs/language-spec.md:35-53`.

[measured] Nested-fold32 loads two tiles and performs 32 inner plus two outer ordered additions. It follows Lab1Part6's nested Fold, rather than changing the inner operation to the canonical example's parallel reduce. Sources: `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29`; `spatial-rs@eb49d8b:docs/language-spec.md:263-281`.

[measured] GEMM32 follows Lab2Part5's K/M/N tile order, A/B/C tile loads, per-k partial matrix and product-by-product memory fold; it performs 32,768 fixed multiplications and as many memory-combine additions. Part6 has the same functional traversal with lane requests 2 and 16. Neither hardware parallel execution nor `.buffer` schedule equivalence is simulated. The canonical Tile-K example groups an inner reduction differently and is a semantic reference, not the exact benchmark listing. Sources: `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part5_gemm_fixed_32.scala:29-58`; `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-58`; `spatial-rs@eb49d8b:docs/language-spec.md:303-348`.

[measured] **Both implementations recursively dispatch the same serialized node tables**, loaded at runtime. Nodes cover constants, scalar slots, indexed reads/writes, add/multiply, sequence, allocation, foreach, scalar fold, rectangular snapshot transfer and memory fold. Width is fixed at 32; multiply nodes carry fractional shift 0 or 8. Rust compiles the generic interpreter, not a generated dense/GEMM kernel. There are 21/12/58 static nodes for dense/fold/GEMM. The only declared scaling probes are dense256, fold256 and GEMM64, still tile16. These tables are manually constructed, not produced by either proposed frontend.

[measured] Int operations normalize modulo 2^32 after each operation; fixed multiplication forms an exact signed raw product, shifts arithmetically by eight, then wraps. Python uses explicit normalization of arbitrary integers; Rust uses wrapping conversion/addition and an exact i64 product. Negative fractional products floor, not truncate toward zero. Sources: `spatial-rs@eb49d8b:docs/language-spec.md:611-617`; `spatial-rs@eb49d8b:docs/language-spec.md:634-659`.

[measured] Both evaluate operands left-to-right, assignment indices before the RHS, bounds once per controller entry, ascending iterations and row-major snapshot transfers before writes. Folds normalize each combine. Legal initialized views and effect restrictions are assumed by construction; neither runtime implements the full verifier. Sources: `spatial-rs@eb49d8b:docs/language-spec.md:818-850`; `spatial-rs@eb49d8b:docs/language-spec.md:886-910`; `spatial-rs@eb49d8b:docs/language-spec.md:963-969`.

[measured] **Allocation policy is part of these implementations.** They allocate source-local tiles, including a new partial matrix for each GEMM k iteration, and host-zero-fill the storage. All observed SRAM elements are written before reads. Canonical memfold instead names an already-declared temporary view and invalidates its initialization status each iteration; a conforming engine can reuse storage. The experiment's equal allocation policy does not prove that repeated host allocation is required by the language or that either implementation is a full canonical interpreter. Sources: `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part5_gemm_fixed_32.scala:46-54`; `spatial-rs@eb49d8b:docs/language-spec.md:284-301`; `spatial-rs@eb49d8b:docs/language-spec.md:886-899`.

### Validation and timing

[measured] All ten cases pass full raw-output comparison before timing in both languages: six normal workloads, dense/fold/GEMM32 edge variants, and one eight-operation arithmetic-edge program. The independent scalar oracle uses mathematical modulo and exact Fraction/floor arithmetic, not interpreter nodes or its wrapping helper. Standard GEMM inputs include deterministic positive/negative fractions; edge inputs include INT_MIN/MAX, tiny negative raw values and overflow products. Explicit checks include `(-1*1)>>8 = -1`, `(-129*257)>>8 = -130`, wrapping addition and extreme multiplication. Timed repeats are consumed but not individually oracle-checked; emitted correctness outputs are checked again after each process. An independent audit rebuilt Rust and freshly verified all ten outputs against another direct oracle, with no frozen-source hash mismatch.

[measured] Host: arm64 macOS 26.6.2; CPython 3.14.5; rustc 1.95.0 with `-O --edition 2021`. Each case receives three warmups and nine samples. Sample repetitions are dense32/fold32=1000, dense256/fold256=200, GEMM32=5 and GEMM64=1. Python uses `perf_counter_ns`; Rust uses `Instant`. The tables report the median of the nine per-run sample means. Fresh input/scalar state is prepared outside each timer; runtime tile allocation, transfers, arithmetic, control and stores remain inside. File I/O, process startup, source compilation and validation are excluded. Construction is measured separately. The primary language runs were serial, CPython then Rust, with a 120-second timeout each.

| Workload | CPython execution ms | Rust execution ms | Python/Rust |
|---|---:|---:|---:|
| [measured] dense32 | 0.024369 | 0.001120 | 21.75× |
| [measured] nested-fold32 | 0.011652 | 0.000497 | 23.42× |
| [measured] GEMM32 | 67.315058 | 1.314642 | 51.20× |
| [measured] dense256 probe | 0.198294 | 0.008463 | 23.43× |
| [measured] nested-fold256 probe | 0.090225 | 0.003809 | 23.68× |
| [measured] GEMM64 probe | 545.893667 | 10.516500 | 51.91× |

[measured] Primary GEMM32's nine sample means range from 66.803–68.105 ms in Python and 1.268–1.335 ms in Rust. All raw ranges and samples are in the archive. The independent repeat yielded GEMM32 68.005/1.289 ms and GEMM64 544.795/10.234 ms; it supports the same scale of cost without replacing the pre-registered run. It is the same host and implementation pair, not cross-host validation.

[measured] Construction decodes an already-read IR string, builds nodes and loads initial arrays: three warmups, then nine samples of 50 constructions. Median Python/Rust milliseconds are dense32 0.012919/0.004893; fold32 0.007868/0.002707; GEMM32 0.185343/0.036854; dense256 0.033795/0.007657; fold256 0.018984/0.004286; GEMM64 0.650782/0.110084. These are custom-IR construction times, not Python/Spatial parsing or end-to-end compiler times.

[judgment] **Ratios exceed the unchanged k=10 locally, while the primary Python executions sum to only 67.351 ms.** The latter is an arithmetic sum of separate medians, not a measured pipeline. GEMM64 contributes about 0.546 s. One hundred GEMM32 executions would contribute about 6.73 s in Python versus 0.131 s in Rust by linear scenario arithmetic. Thus single small course examples remain fast; larger or repeated feedback may make native execution useful. The missing latency budget and workload mix prevent a universal “material”/“immaterial” verdict.

[judgment] **Post-measurement interpretation correction.** The original spike preregistration/report and this note's first draft said that a limited toy interpreter could not trigger D-26's reversal condition. That reading was incorrect: [[D-26#Reversal conditions]] explicitly accepts “precedent or spike evidence,” and angle 12 of [[2026-09-25-python-rust-architecture-research-design]] explicitly permits a toy-versus-toy spike of roughly 200 lines per implementation on one lab. The primary ratios 21.75×, 23.42× and 51.20× therefore trigger the registered speed-negative condition against the tested pure-CPython simulator route. k remains 10; no workload, code, result or threshold has changed. The archived original preregistration/report retain their initial wording for provenance; this paragraph corrects their rule interpretation. Small absolute times remain relevant to usability, but do not waive the registered ratio bound. The R-* loss conjunction is not met because this Python simulator is outside the required bound. A Python semantic core with a native/generated engine is a different, still-unmeasured candidate and receives no assumed pass from this experiment.

## Implications

### R-X

[judgment] Retaining a native interpreter is supported for repeated scalar simulation. The external surface receives no special support from these timings: input nodes bypass its parser and frontend.

### R-E

[judgment] A Rust semantic core with one restricted Python AST frontend can use the same native execution path. This evidence contributes to its runtime case, but does not select its surface, validate ingress/provenance or establish delivery cost. If [[D-26]] selects R-E, the rationale must also include semantic ownership and the surface decision, not this ratio alone.

### R-B

[judgment] Both frontends could share the same execution engine. The spike provides no evidence that maintaining two public surfaces is worthwhile and measures none of their parity obligations.

### P-X

[judgment] The registered simulator-loss condition applies to P-X using this pure-CPython node interpreter. A Python compiler core that generates simulation code or delegates a whole run to a native executor remains a distinct unmeasured route, not an established exception that passes the gate; its setup, boundary and execution costs would need measurement.

### P-E

[judgment] The same registered speed-negative applies to P-E using the tested runtime. Python core and Python student syntax are separate from the execution-engine choice. A proposed native executor would need one authoritative numeric/effect contract, shared conformance vectors and a coarse boundary, rather than two independently evolving simulators; this option has not passed the gate. No student or maintainer productivity result follows.

### P-B

[judgment] The tested interpreter route also triggers the speed-negative for P-B. Native execution could be shared as an unmeasured alternative, but two supported surfaces add obligations the timing cannot justify. Neither core language removes the need to preserve source provenance and the same acceptance contract.

## Evidence against

[judgment] **The registered decision consequence is narrower than a universal language claim.** The negative condition has fired for the tested pure-CPython route; the original design does not require a complete compiler first. That consequence is valid even though these hand-built programs do not cover full architectures or the whole mistake list. Conversely, a decision rule rejecting this runtime route is not proof that all possible Python compiler implementations are slow, that the Rust frontend is complete, or that X beats E. The unmeasured native-engine alternative must earn its own evidence.

[measured] One host, fixed language order, no affinity/frequency/thermal/background-load control, default Python GC, no empty-program/timer baseline and no confidence interval beyond observed sample spread. Assignment of a new Python result can release the previous output list inside its timer; Rust drops state outside its timer. Timer overhead is proportionally most relevant to sub-microsecond Rust fold32. These are implementation-pair ratios, not isolated universal language costs.

[measured] Widths other than 32, tails, empty domains, illegal effects, read-before-write diagnostics, FIFO/FSM, schedule checks, decimal ingress/output serialization and actual frontend/HLS pipelines are absent. The valid cases do not test a complete type/effect checker. Allocation reuse, generated simulation, NumPy and optimized Python representations were not measured; no post-result optimized variant was selected.

[judgment] The strongest practical counterargument is already in the absolute times: a 51× GEMM ratio coexists with about 67 ms single-kernel feedback. That may motivate a separately stated product-latency criterion, but it cannot retroactively replace k=10. Conversely, that small example cannot certify responsiveness for larger labs or hundreds of regression cases. Course usability still needs workload-specific end-to-end evidence.

## Open questions

- What is the actual latency target for an interactive run and for a grading/regression batch, including source processing and startup?
- How does the selected complete architecture perform on the required positive/negative corpus, including non-GEMM controllers and tails?
- Can allocation reuse or a coarse native/generated executor preserve the single semantic contract while meeting that target, with setup cost included?
- Does the restricted Python AST surface improve student writing/repair outcomes? No learner trial or timed maintenance exercise occurred here.

## Confidence

High in the recorded outputs and timings of these frozen programs on this host, supported by independent oracle checks and a repeat, and in the conclusion that they exceed the registered k=10 bound for this route. Moderate that unoptimized pure-CPython node dispatch creates a real scaling cost for repeated scalar work. Low in extrapolation to other execution architectures, course latency acceptance, implementation effort or teaching outcomes. The result supplies a registered negative for the tested runtime without choosing the student surface or proving a universal Python-core limitation.
