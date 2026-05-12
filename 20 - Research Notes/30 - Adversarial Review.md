---
type: research-note
project: spatial-spec
status: draft
date: 2026-04-25
---

# Adversarial Review

Scope: representative Phase 2 citation audit, focused on the high-leverage entries requested in the handoff:

- all 13 Argon Framework spec entries
- Banking and Retiming
- Scalagen Numeric Reference Semantics and Memory Simulator
- all 9 Semantics synthesis entries

Method: checked every `source_files` file:line citation in the selected entries against the source tree at `/Users/david/Documents/David_code/spatial/`. This validates that each cited file exists and each cited line range is in-bounds. I also spot-checked several load-bearing behavioral claims in Banking, Retiming, and Scalagen against the cited source. No spec text was auto-corrected.

## Summary

- Entries reviewed: 26
- `source_files` citations checked: 303
- Correct citations: 286
- Incorrect citations: 17
- Pattern of incorrect citations: all 17 are line-range boundary errors, usually one line past EOF on whole-file citations. No missing source files were found.

## Per-entry Counts

| Entry | Citations checked | Correct | Incorrect |
|---|---:|---:|---:|
| `[[10 - Symbols and Types]]` | 7 | 7 | 0 |
| `[[20 - Ops and Blocks]]` | 6 | 6 | 0 |
| `[[30 - Effects and Aliasing]]` | 10 | 10 | 0 |
| `[[40 - Metadata Model]]` | 14 | 14 | 0 |
| `[[50 - Staging Pipeline]]` | 13 | 13 | 0 |
| `[[60 - Scopes and Scheduling]]` | 7 | 7 | 0 |
| `[[70 - Rewrites and Flows]]` | 12 | 12 | 0 |
| `[[80 - Passes]]` | 12 | 12 | 0 |
| `[[90 - Transformers]]` | 9 | 6 | 3 |
| `[[A0 - Codegen Skeleton]]` | 5 | 5 | 0 |
| `[[B0 - Compiler Driver]]` | 9 | 9 | 0 |
| `[[C0 - Macro Annotations]]` | 24 | 24 | 0 |
| `[[D0 - DSL Base Types]]` | 27 | 27 | 0 |
| `[[70 - Banking]]` | 12 | 10 | 2 |
| `[[C0 - Retiming]]` | 12 | 5 | 7 |
| `[[20 - Numeric Reference Semantics]]` | 9 | 9 | 0 |
| `[[30 - Memory Simulator]]` | 14 | 14 | 0 |
| `[[10 - Effects and Aliasing]]` | 10 | 10 | 0 |
| `[[20 - Scheduling Model]]` | 10 | 10 | 0 |
| `[[30 - Control Semantics]]` | 10 | 10 | 0 |
| `[[40 - Memory Semantics]]` | 13 | 13 | 0 |
| `[[50 - Data Types]]` | 12 | 12 | 0 |
| `[[60 - Reduction and Accumulation]]` | 10 | 10 | 0 |
| `[[70 - Timing Model]]` | 11 | 8 | 3 |
| `[[80 - Streaming]]` | 14 | 12 | 2 |
| `[[90 - Host-Accel Boundary]]` | 11 | 11 | 0 |

## Citation Errors Found

`[[90 - Transformers]]`:

- `argon/src/argon/transform/SubstTransformer.scala:6-177` is one line past EOF. Correction: `argon/src/argon/transform/SubstTransformer.scala:6-176`.
- `argon/src/argon/node/Enabled.scala:6-22` is one line past EOF. Correction: `argon/src/argon/node/Enabled.scala:6-21`.
- `argon/src/argon/Mirrorable.scala:1-9` is one line past EOF. Correction: `argon/src/argon/Mirrorable.scala:1-8`.

`[[70 - Banking]]`:

- `src/spatial/traversal/AccessAnalyzer.scala:1-323` is one line past EOF. Correction: `src/spatial/traversal/AccessAnalyzer.scala:1-322`.
- `src/spatial/traversal/banking/FIFOConfigurer.scala:1-103` is one line past EOF. Correction: `src/spatial/traversal/banking/FIFOConfigurer.scala:1-102`.

`[[C0 - Retiming]]`:

- `src/spatial/traversal/RetimingAnalyzer.scala:1-122` is one line past EOF. Correction: `src/spatial/traversal/RetimingAnalyzer.scala:1-121`.
- `src/spatial/transform/RetimingTransformer.scala:1-272` is one line past EOF. Correction: `src/spatial/transform/RetimingTransformer.scala:1-271`.
- `src/spatial/transform/DuplicateRetimeStripper.scala:1-37` is one line past EOF. Correction: `src/spatial/transform/DuplicateRetimeStripper.scala:1-36`.
- `src/spatial/traversal/IterationDiffAnalyzer.scala:1-218` is one line past EOF. Correction: `src/spatial/traversal/IterationDiffAnalyzer.scala:1-217`.
- `src/spatial/traversal/InitiationAnalyzer.scala:1-102` is one line past EOF. Correction: `src/spatial/traversal/InitiationAnalyzer.scala:1-101`.
- `src/spatial/traversal/BroadcastCleanup.scala:1-133` is one line past EOF. Correction: `src/spatial/traversal/BroadcastCleanup.scala:1-132`.
- `src/spatial/traversal/BufferRecompute.scala:1-55` is one line past EOF. Correction: `src/spatial/traversal/BufferRecompute.scala:1-54`.

`[[70 - Timing Model]]`:

- `src/spatial/traversal/RetimingAnalyzer.scala:1-122` is one line past EOF. Correction: `src/spatial/traversal/RetimingAnalyzer.scala:1-121`.
- `src/spatial/transform/RetimingTransformer.scala:1-272` is one line past EOF. Correction: `src/spatial/transform/RetimingTransformer.scala:1-271`.
- `src/spatial/transform/DuplicateRetimeStripper.scala:1-37` is one line past EOF. Correction: `src/spatial/transform/DuplicateRetimeStripper.scala:1-36`.

`[[80 - Streaming]]`:

- `src/spatial/node/StreamIn.scala:1-21` is one line past EOF. Correction: `src/spatial/node/StreamIn.scala:1-20`.
- `src/spatial/node/StreamOut.scala:1-28` is one line past EOF. Correction: `src/spatial/node/StreamOut.scala:1-27`.

## Targeted Claim Spot-checks

- `[[70 - Banking]]`: the pipeline claim is correct: `bankingAnalysis` is `retimeAnalysisPasses ++ Seq(accessAnalyzer, iterationDiffAnalyzer, printer, memoryAnalyzer, memoryAllocator, printer)` at `src/spatial/Spatial.scala:140-143, 203`. The `MemoryAllocator` first-fit style allocation is also present at `src/spatial/traversal/MemoryAllocator.scala:56-103`. Human-review note: `MemoryAllocator.process` prints `TODO: un-gut memory allocator` at `src/spatial/traversal/MemoryAllocator.scala:15-17`, so any prose that presents allocation as fully finished should be caveated.
- `[[C0 - Retiming]]`: the repeated-analysis schedule is correct. Source shows `retimeAnalysisPasses` at `src/spatial/Spatial.scala:140`, optional runtime-model use at `:180`, banking use at `:142,203`, post-DCE analyzer at `:213`, and final analyzer/transformer at `:227-228`.
- `[[20 - Numeric Reference Semantics]]`: the Scalagen FMA divergence is real. `FixFMA` emits `($m1 * $m2) + $add` at `src/spatial/codegen/scalagen/ScalaGenFixPt.scala:150`; fixed-point unbiased rounding draws `scala.util.Random.nextFloat()` at `emul/src/emul/FixedPoint.scala:232-241`.
- `[[30 - Memory Simulator]]`: OOB behavior is correctly described as non-aborting: `OOB.readOrElse` returns the caller-provided invalid value and `writeOrElse` drops the write after logging at `emul/src/emul/OOB.scala:19-38`. The Scalagen wrapper also catches `ArrayIndexOutOfBoundsException` and emits invalid values on reads at `src/spatial/codegen/scalagen/ScalaGenMemories.scala:36-50`.

## Recommendations

- Fix the 17 off-by-one line ranges above before using the spec as a citation-grade reference.
- Add an explicit caveat in `[[70 - Banking]]` or its downstream HLS notes that `MemoryAllocator` contains a visible TODO even though the current code does execute a concrete allocation pass.
- Treat the Scalagen FMA and unbiased-rounding findings as Phase 3 architecture questions, not documentation typos.
