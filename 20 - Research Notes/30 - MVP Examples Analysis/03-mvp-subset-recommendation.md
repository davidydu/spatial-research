---
type: research-note
topic: mvp-subset-recommendation
date: 2026-05-12
status: draft
sources:
  - "[[01-spatial-user-examples]]"
  - "[[02-ee109-examples]]"
feeds_spec:
  - "[[A0 - MVP Subset]]"
---

# MVP Feature Subset — Synthesis & Recommendation

Distillation of [[01-spatial-user-examples]] (264 Scala files across `apps/`, Rosetta, `test/apps/`, feature tests, syntax tests) and [[02-ee109-examples]] (3 lab files, 203 LOC) into a recommended feature subset for the future Rust/Python+HLS rewrite.

## Why an MVP subset (not the full language)

The full Spatial surface is ~80 IR node types plus dozens of metadata/transform passes ([[Spec Index]] has 96 spec entries). A faithful reimplementation is enormous. But the **observed usage footprint** in real example programs is much smaller:

- Of ~30 user-facing language constructs, only ~10 appear in **every** Spatial program (`Accel`, basic arithmetic, etc.).
- Only ~15 appear in **majority** of programs.
- Several "documented" constructs appear in **zero** examples — they exist for compiler infrastructure or specialized hardware targets, not user code.

By scoping the rewrite to the actually-used subset, we cut implementation effort by an estimated **60–70%** while still compiling the majority of real applications. Specialized features can be added on demand once the MVP is solid.

## Methodology

### Re-weighting the catalog

The 264-file Spatial corpus mixes two populations:

| Population | What it is | Use for MVP scoping |
|---|---|---|
| **Production-style kernels** (~30 files) | Rosetta benchmarks, `apps/`, top-level apps. Real accelerators. | **Primary signal** — what real programs actually use |
| **Feature unit tests** (~234 files) | One file per language feature, in `test/spatial/tests/feature/`. Each tests one feature. | Used to detect "feature exists" but **dilutes frequency** — a vector-only unit test has no `SRAM` use |

Raw frequencies from the codex catalog include feature tests in the denominator. For MVP purposes, we re-weight by focusing on the **production-style subset** plus the **EE109 corpus**.

### EE109 as a pedagogical floor

The EE109 corpus is the absolute minimum: it's what Stanford's Digital Systems Design Lab teaches students who are new to Spatial. Any rewrite that doesn't compile EE109 examples is unusable for the course context. **EE109 features form a hard lower bound** on the MVP.

### MVP tiers

We define three tiers based on usage across both corpora:

- **Tier 0 — EE109 floor** (must work for student-written code; ~15 features)
- **Tier 1 — Spatial canonical** (must work for any user-facing app; Tier 0 + ~15 more)
- **Tier 2 — common patterns** (most user apps need this; Tier 1 + ~10 more)
- **Out of scope** — features no real example uses (drop from rewrite)

## Tier 0 — EE109 floor (hard minimum)

Every EE109 lab uses these. Without all of them, the rewrite can't compile a single student program.

| Feature | Category | EE109 use | Spec entry | HLS status |
|---|---|---|---|---|
| `@spatial object … extends SpatialApp` | Boilerplate | 3/3 | [[Spatial.scala]] / [[10 - Controllers]] | clean |
| `Accel { … }` | Controller | 3/3 | [[10 - Controllers]] | clean |
| `Sequential { … }` | Controller | 3/3 | [[10 - Controllers]] | clean |
| `Foreach(N by 1){ i => … }` | Controller | 3/3 | [[10 - Controllers]] | clean |
| `ArgIn[T]`, `ArgOut[T]` | Host I/O memory | 3/3 | [[20 - Memories]] | clean |
| `setArg`, `getArg` | Host transfer | 3/3 | [[60 - Host and IO]] | clean |
| `DRAM[T](size)` | Off-chip memory | 3/3 | [[20 - Memories]] | clean |
| `SRAM[T](size)` | On-chip memory | 2/3 (Lab2/3) | [[20 - Memories]] | rework (banking) |
| `load` / `store` | Tile transfer | 2/3 (Lab3) | [[10 - Language Surface]] | rework (HLS DMA) |
| `Reduce(Reg[T])(N by 1){ i => … }{_+_}` | Controller | 1/3 (Lab3) | [[10 - Controllers]] | clean |
| `Reg[T](init)` | Local register | 2/3 | [[20 - Memories]] | clean |
| `LUT[T](N)(values…)` | Lookup table | 1/3 (Lab2Part4 specifically) | [[20 - Memories]] | rework (HLS arrays) |
| `FSM` / `StateMachine` | Controller | 1/3 (Lab2Part3 specifically) | [[10 - Controllers]] | rework (HLS state) |
| `Int`, `FixPt[S,I,F]` | Types | 3/3 | [[30 - Primitives]], [[50 - Data Types]] | clean |
| `par` annotation on `Foreach`/`Reduce` | Parallelism | 1/3 (Lab3) | various | rework (HLS unroll) |
| Arithmetic + comparisons | Math | 3/3 | [[50 - Math and Helpers]] | clean |
| `printArray`, `println`, assertions | Host validation | 3/3 | [[70 - Debugging and Checking]] | clean |
| `setMem`, `getMem` | Host transfer | (used in app templates EE109 students extend) | [[60 - Host and IO]] | clean |

**Tier 0 footprint:** ~15 distinct constructs + standard arithmetic/comparison ops. Implementable as a v0.1 of the rewrite.

## Tier 1 — Spatial canonical (broader real-app usage)

These are common in Rosetta benchmarks and `test/spatial/tests/apps/` but not necessarily in EE109. Required for a rewrite that targets the broader Spatial ecosystem, not just course assignments.

| Feature | Category | Canonical use | Spec entry | HLS status |
|---|---|---|---|---|
| `Pipe { … }` (pipelined controller) | Controller | ~25% canonical | [[10 - Controllers]] | clean |
| `Tup2[A,B]`, `Tup3[A,B,C]` | Types | ~85% (universal — codex flagged Tier 1) | [[50 - Data Types]] | clean |
| `tabulate { i => … }` | Functional | ~60% | [[60 - Host and IO]] | clean (host-side) |
| `slice` (range indexing) | Functional | ~60% | [[30 - Primitives]] | clean |
| `zip`, `reduce` on `Array` | Functional | ~50% | [[A0 - Standard Library]] | clean (host-side) |
| `cond.to[T]` (cast operator) | Special | ~68% (**spec gap — no entry**) | ⚠ none | rework |
| Conditional `if`/`else` in Accel | Special | ~37% | [[30 - Control Semantics]] | clean |
| 2D `DRAM[T](rows, cols)`, 2D `SRAM` | Memory | ~50% | [[40 - Memory Semantics]] | rework (HLS pragma) |
| `getMatrix` (2D readback) | Transfer | ~20% (Rosetta) | [[60 - Host and IO]] | clean |
| `bound(arg) = N` (DSE bounds) | DSE | GEMM example | [[30 - HLS Mapping]] | unknown |
| Multi-level parallelism (`par tileM_par, par M_par`) | Parallelism | GEMM example | various | rework |
| DSE parameter syntax `(16 → 8 → 64)`, `(1,2,4,8)` | DSE | GEMM example | [[70 - Models and DSE]] | unknown |

**Tier 1 footprint:** Tier 0 + ~12 more. Implementable as a v0.5.

### Spec gap flag

`cond.to[T]` (the type-cast operator like `someBit.to[Int]`) has **68% usage in canonical apps** but **no corresponding spec entry**. This is a concrete miss that the spec needs to address — file as Q-new under [[20 - Open Questions]].

## Tier 2 — common but not universal

Features that real apps occasionally use but a v0.5 rewrite can omit if needed.

| Feature | Category | Canonical use | Notes |
|---|---|---|---|
| `MemReduce` | Controller | ~8% | High value when used (collective reductions across memory) |
| `RegFile[T](dims…)` | Memory | ~7% | Small fast memory, often used for filter coefficients |
| `Struct` (user-defined) | Types | ~7% | DigitRecognition, BNN use this |
| `FIFO[T](depth)` | Memory | ~17% | Common for inter-stage flow |
| `FltPt`, `Float` | Types | ~14% combined | Floating-point apps |
| Transcendental math (`sin`, `cos`, `exp`, `log`, `sqrt`, `tanh`) | Math | ~5% | Float-using kernels only |
| `gather`, `scatter` | Transfer | ~3% | Sparse access patterns |
| `HostIO` | Memory | ~4% (HelloSpatial canonical) | Host↔Accel bidirectional |
| `Bool`, `Bit` | Types | ~32% / ~13% | Predicates, masks |
| `args.length` parsing | Host | ~0.4% | Variable argument handling |
| `LineBuffer` | Memory | ~2% | Stencil/convolution windows |
| `flatten` | Functional | ~12% | Multi-D → 1-D iteration |

## Out of scope — drop from MVP rewrite

These appear in **zero** user-facing examples in our 264-file corpus. They likely exist for compiler infrastructure, internal IR plumbing, or specialized backends (PIR, Plasticine, etc.).

| Feature | Why drop | Confidence |
|---|---|---|
| `.banking(…)` explicit annotation | Banking inferred automatically — no user explicitly sets it | High |
| `.bufferAmount(…)` | Same — buffer depth inferred from access patterns | High |
| `ParallelPipe` | Controller variant; superseded by `par` on `Foreach` | High |
| `StreamForeach` | Stream variant; `StreamIn`/`StreamOut` themselves are <3% used | Medium (could be intentional sparsity) |
| `Switch`/`Mux` controllers | Compiler-internal — users write `if`/`else` | High |
| `Bus` / `StreamStruct` | Bus/protocol types; only `HostIO` and `Stream*` users see them | Medium |
| `MergeBuffer` | Sparse-data merge primitive; only specialized apps | High |
| `getTensor3D/4D/5D` | Multi-D readback; HelloSpatial mentions them but no example uses | Medium |

## Recommended implementation order

1. **Bring up Tier 0 boilerplate first**: `@spatial object … extends SpatialApp`, `Accel`, basic `Foreach(N by 1)`, `Int`/`FixPt` types, host I/O (`ArgIn`/`ArgOut`/`setArg`/`getArg`), and assertions/print. This compiles trivially small EE109 examples without `SRAM`/`DRAM`.

2. **Add memory primitives next**: `DRAM`, `SRAM`, `Reg`, `load`/`store`. Now most of Lab3 compiles. This is the major HLS challenge — banking decisions become HLS `#pragma HLS ARRAY_PARTITION` directives.

3. **Add reductions and control variants**: `Reduce(Reg[T])`, `Sequential`, `Pipe`. Plus `par` annotation handling (HLS `#pragma HLS UNROLL` and `#pragma HLS PIPELINE II=N`).

4. **Add Tier 0 specialty constructs**: `LUT` (HLS read-only arrays), `FSM` (HLS state machines). These unlock the dedicated EE109 labs.

5. **Tier 1 expansion**: `Tup2/Tup3`, `cond.to[T]`, `tabulate`/`zip`/`reduce` on host-side `Array`, 2D memories, `getMatrix`, conditional `if`/`else` in `Accel`.

6. **DSE parameters**: `(16 → 8 → 64)` syntax, `bound()`. Initially these can be no-ops (use defaults); full DSE is a v1.0 feature.

7. **Tier 2 on demand**: As real applications need them.

Milestone gates:

- **v0.1**: compiles Lab2Part3, Lab2Part4, Lab3 (the three EE109 labs)
- **v0.5**: compiles HelloSpatial.scala + GEMM.scala (the spatial-quickstart canonical examples)
- **v1.0**: compiles 80% of Rosetta benchmarks

## Coverage gaps in the existing spec

Features used by user code but lacking dedicated spec entries:

| Feature | Frequency | Why no entry? |
|---|---|---|
| `cond.to[T]` (cast op) | 68% canonical | Likely covered indirectly under type promotion; no standalone entry |
| `bound(arg) = N` (DSE bounds) | GEMM | DSE is documented but the user-facing syntax isn't surfaced |
| DSE parameter ranges `(min → step → max)` and discrete `(a,b,c,d)` | GEMM, many Rosetta | Same — DSE design is documented but parameter syntax isn't a first-class spec entry |
| Multi-dim `(0::M, 0::N){(i,j) => …}` tabulation | ~50% canonical | Likely covered under standard library Array ops but worth a standalone entry |

File these as items in [[20 - Open Questions]].

## Open questions for the professor

The most productive 30 minutes with someone who built Spatial would resolve:

1. **Is the EE109 floor stable?** Have the labs changed recently? Will the rewrite need to track upcoming course revisions?
2. **DSE syntax canonical or aspirational?** The `(min → step → max)` parameter ranges and `bound()` annotations appear in GEMM and many Rosetta apps — are these expected to be part of the long-term language, or are they design-space tooling that could be replaced?
3. **`cond.to[T]` semantics.** Is this just type coercion or does it have meaning beyond "cast"? The spec gap is real — what is the canonical definition?
4. **Streaming features at 1–3% usage.** `StreamIn`/`StreamOut`, `MergeBuffer`, `LineBuffer` are vanishingly rare in our corpus. Is this representative, or do real production deployments use them more? Should the MVP skip them entirely, or are there reference apps we're missing?
5. **Banking annotations at 0%.** Banking is critical for performance, but no user sets it explicitly. Confirmation: is banking always inferred? If so, the explicit annotation is dead syntax we can drop.
6. **HLS as the target.** Is the user planning to target Vitis HLS specifically, Catapult, or a vendor-neutral path? This decides several rewrite questions (e.g., `#pragma HLS` syntax flavor).

## What to read next

- [[01-spatial-user-examples]] — full 264-file catalog with file:line citations
- [[02-ee109-examples]] — EE109 3-file catalog
- [[10 - Clean Mappings]] — HLS mapping status for each construct
- [[20 - Open Questions]] — running list of unresolved issues
- [[Spec Index]] — full spec entry point
