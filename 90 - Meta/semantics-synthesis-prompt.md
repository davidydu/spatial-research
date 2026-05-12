---
type: design
project: spatial-spec
status: draft
approved_by: main-session-2026-04-23
date: 2026-04-23
---

# Semantics Synthesis — Subagent Prompt (for post-Round-2 dispatch)

Captured here so the main session can dispatch a synthesis subagent once Round 1 + Round 2 deep dives and spec entries are in place.

## When to dispatch

After all 4 Round 1 agents + at least Scalagen (Round 2) have returned. Scalagen-first because it is the reference semantics and the synthesis must cite it for formal behavior.

## Prompt template

```
Task: produce the cross-cutting formal-semantics spec for Spatial — the `20 - Semantics/` section — synthesized from the already-written spec entries under `10 - Spec/30 - IR/`, `10 - Spec/40 - Compiler Passes/`, `10 - Spec/10 - Language Surface/`, and `10 - Spec/50 - Code Generation/20 - Scalagen/`.

### Project context

- Vault root: ``
- Source: `/Users/david/Documents/David_code/spatial/`.
- This is a synthesis task: read the already-drafted spec entries and cross-reference them into a formal semantics document that a Rust+HLS reimplementer can match.
- Reference semantics anchor: `10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md`. When in doubt about numeric behavior, scalagen+emul wins.
- Conventions at `90 - Meta/conventions.md`.

### Deliverables

9 spec entries, each 800-1500 words, under `10 - Spec/20 - Semantics/`:

1. `10 - Effects and Aliasing.md` — synthesized from Argon Effects+Aliasing entry. State the complete effect lattice, the composition rules (andAlso/andThen/orElse/star), how `Impure` wraps symbol-level effects, the alias closure (Shallow/Deep/Nested), atomic-write propagation, and mutable-alias contract.
2. `20 - Scheduling Model.md` — synthesized from Argon Scopes+Scheduling + Spatial PipeInserter + UnrollingTransformer. Scope bundles, SimpleScheduler idempotent-only DCE, code motion constraints, BlockOptions, how schedules emerge from effect dependencies.
3. `30 - Control Semantics.md` — synthesized from Spatial Controllers nodes + SpatialFlowRules + RetimingAnalyzer. Each `CtrlSchedule` formally defined (`Sequenced`/`Pipelined`/`Streaming`/`ForkJoin`/`Fork`/`PrimitiveBox`). II semantics. Pipeline fill/drain behavior. Parallelization (par × lanes). Metapipelining.
4. `40 - Memory Semantics.md` — synthesized from Memories nodes + MemoryConfigurer + BankingStrategy + ScalaGenMemories (reference). Local vs remote memory invariants. Banking scheme (α, N, B, P). Duplicates and dispatch. N-buffering semantics. Port assignment. OOB behavior (from Scalagen).
5. `50 - Data Types.md` — synthesized from Argon DSL types + emul FixedPoint/FloatPoint. Fixed-point bit-exactness. Rounding modes (clamped/saturating/unbiased). Float mantissa/exponent packing. Bit-vector semantics. Saturation boundaries.
6. `60 - Reduction and Accumulation.md` — synthesized from OpReduce/OpMemReduce nodes + AccumTransformer + Scalagen accumulator emission. Detection of accumulator cycles. RegAccumOp/RegAccumFMA semantics. Fold vs Reduce distinction. AccumType lattice.
7. `70 - Timing Model.md` — synthesized from retiming pass + latency model + RuntimeModel. Latency computation (compiler vs target). Delay line injection. Retiming boundaries (RetimeGate). Pipeline timing.
8. `80 - Streaming.md` — synthesized from Streaming schedule + HierarchicalToStream + FIFO semantics. Streaming controllers. FIFO backpressure model. MetaPipe-to-Stream equivalence.
9. `90 - Host-Accel Boundary.md` — synthesized from AccelScope + ArgIn/Out/HostIO + DRAM transfers + Cppgen host emission. Host sets args → triggers accel → accel signals done → host reads results. DRAM allocation ownership transitions. Frame streaming semantics.

Each entry structure: Summary / Formal Semantics (with references to the authoritative spec entries under other sections) / Reference Implementation (point to Scalagen spec) / HLS Implications / Open questions.

### Critical rules

- Cite BOTH the Spatial source code (file:line) AND the spec entries being synthesized. Use `[[wikilinks]]` for cross-section references.
- Where behavior is defined by Scalagen, cite the Scalagen spec entry as the normative definition and note "reference semantics: match this".
- Do not introduce claims not already established by lower-level entries. Semantics entries consolidate, they don't invent.
- Block-style YAML; quote strings with `:` or `[[link]]`.
- Open questions → `20 - Research Notes/10 - Deep Dives/open-questions-semantics.md`.

### Final report

Inline: (1) files written with word counts, (2) open questions filed, (3) any places where lower-level spec entries contradicted each other (flag for main-session resolution), (4) gaps in lower-level spec entries that synthesis can't paper over.
```

## Timing

- Round 1 launched 2026-04-23 ~6 pm-ish. Expected completion: within several hours.
- Round 2 launched immediately after. Expected completion: within several hours.
- Semantics synthesis: dispatch after both rounds complete, with at least Round 1 (Argon, IR, passes, language) and Round 2 (Scalagen) results on disk.
