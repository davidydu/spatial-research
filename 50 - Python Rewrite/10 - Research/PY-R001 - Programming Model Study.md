---
type: deep-dive
title: "PY-R001 — Python programming model comparison"
topic: python-programming-model
project: spatial-python
session: 2026-09-30
status: draft
source_files:
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43"
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-37"
  - "spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-31"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:37-62"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87"
  - "spatial@e7a8f2f:src/spatial/lang/Reg.scala:48-57"
feeds_spec: []
---

## Question and scope

Resolve PY-Q001 in [[02 - Python Open Questions]]: should the public programming model use captured Python source or an explicit Python builder? The compiler implementation remains Python under [[D-27]]. This study does not select a backend or begin compiler implementation.

Compare the three cases in [[PY-E001 - Initial Example Corpus]] in **both** forms. All six illustrative listings are below. Their common intended behavior is described, but semantic and diagnostic review remains open. The table is a work record, not an implementation-coverage report.

| Case | Source-capture form | Builder form | Meaning and effect review | Execution |
|---|---|---|---|---|
| E1 tiled scale | First sketch below | First sketch below | Original source contract checked; proposed APIs unvalidated | Not run |
| E2 scalar reduction | First sketch below | First sketch below | Identity and contribution meaning described; numeric and reduction policies need review | Not run |
| E3 branch/FIFO | First sketch below | First sketch below | Accumulator, lazy branches, and proposed functional trace described; controller/effect questions open | Not run |

## Evidence ledger

| Evidence class | What is known here | Limit |
|---|---|---|
| Original source | Three pinned source cases and their output references in [[PY-E001 - Initial Example Corpus]] | Source inspection is not a fresh compiler run |
| Earlier Rust design | Scope, assignment-order, literal, and FIFO policies in `35 - Python Surface Mapping/` | Re-evaluate each before adopting it for Python |
| Python proposal | Six spellings below, their proposed common interpretation, and the comparison protocol | Neither API exists in an implemented package; neither surface is adopted |
| Prior experiment | [[D-26-12-simulator-spike]] | Measures the earlier node interpreters, not these forms or their usability |
| Current decision | [[D-27]] | Settles Python and research order, not source capture or a builder |

## E1: two proposed spellings of tiled scale

These are **unimplemented design sketches**. Both preserve the source example's two SRAM buffers, 32 elements, 16-element tiles, and load/compute/store structure. The original source and host reference are `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:6-43`.

### Source capture

```python
@kernel
def tiled_scale(src: In[Dram[Int, 32]],
                scale: In[Int],
                dst: Out[Dram[Int, 32]]):
    for base in sequential(0, 32, step=16):
        tile_in: Sram[Int, 16]
        tile_out: Sram[Int, 16]
        load(tile_in, src[base:base + 16])
        for i in foreach(0, 16):
            tile_out[i] = tile_in[i] * scale
        store(dst[base:base + 16], tile_out)
```

Proposed interpretation: the compiler reads the source without executing the function, its decorator, or annotations. It recognizes the supported statements and constructs program objects. The displayed annotations declare ports or storage in this language; they are not ordinary Python allocations. File/cell capture and supported imports still need an explicit contract.

### Explicit builder

```python
k = Kernel("tiled_scale")
src = k.input_memory("src", Int, 32)
scale = k.input_scalar("scale", Int)
dst = k.output_memory("dst", Int, 32)

with k.sequential(0, 32, step=16) as base:
    tile_in = k.sram(Int, 16)
    tile_out = k.sram(Int, 16)
    k.load(tile_in, src[base:base + 16])
    with k.foreach(0, 16) as i:
        tile_out.at(i).write(tile_in[i] * scale)
    k.store(dst[base:base + 16], tile_out)
```

Proposed interpretation: Python executes the construction code once. Each context records a controller body using a symbolic index; it does not run the hardware trip count. Memory handles and arithmetic record operations. The local-storage declarations belong to the represented loop body; creating a Python handle once does not decide hardware allocation lifetime. Arbitrary Python side effects in construction code would occur during construction and need a clear policy.

Both sketches leave the exact `Int` and scheduling contracts open. The builder has more explicit construction machinery; the source form needs a documented distinction from ordinary Python execution. E1 alone does not establish a winner.

## E2: two proposed spellings of scalar reduction

Original source: `spatial@e7a8f2f:test/spatial/tests/feature/control/ReduceTiny.scala:7-15`. Preserve its `1 × 16` SRAM, writes of indices `0` through `15`, scalar reduction with addition and identity `0`, and scalar output. The source-derived expected result is `120`.

The identity and accumulator are distinct concepts in the original implementation. `ReduceConstant` supplies the constant as the reduction identity when `isFold` is false; `ReduceAccum` separately records the contribution body, accumulator load/store, combination body, identity, and fold initialization. Sources: `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:37-62`. This inspection identifies the represented fields; it does not establish every reduction schedule or empty-domain behavior.

### Source capture

```python
@kernel
def scalar_reduce(result: Out[Int]):
    values: Sram[Int, 1, 16]
    for i in foreach(0, 16):
        values[0, i] = i

    def contribution(i: Int) -> Int:
        return values[0, i]

    total: Int = reduce(0, 16, identity=0, combine="add",
                        body=contribution)
    result = total
```

Proposed interpretation: the compiler captures the helper definition as a contribution region with a symbolic index. It does not call this helper as ordinary Python. Its `return` terminates that region with one contribution; it does not return from the kernel. `combine="add"` names a Spatial addition operation, not an arbitrary Python callback. The declaration of `total` binds the reduction result, while assignment to the declared output `result` writes a hardware output. This difference follows the proposed declaration/type rules, not Python rebinding semantics.

### Explicit builder

```python
k = Kernel("scalar_reduce")
result = k.output_scalar("result", Int)
values = k.sram(Int, 1, 16)

with k.foreach(0, 16) as i:
    values.at(0, i).write(i)

with k.reduce(0, 16, identity=0, combine="add") as reduction:
    reduction.contribute(values[0, reduction.index])

result.write(reduction.value)
```

Proposed interpretation: Python constructs each region once. `reduction.index` is symbolic; `contribute` records the value yielded by one represented iteration. Closing the context finishes construction of that region. It does not finish a numerical sum in the host. `reduction.value` is a handle to the eventual result, usable after the reduction in the represented program; `result.write` records the output write.

### Common meaning and remaining policy

For both forms, initialization precedes the reduction's SRAM reads. Each of the sixteen contributions is read once in the proposed functional model. The identity is a value of the selected Spatial numeric type; it is not a pre-existing accumulator value that should be added once more. The scalar result becomes available after the represented reduction completes. Neither sketch exposes partially accumulated values or chooses a hardware reduction tree.

The proposed common empty-domain rule would return the identity when one is supplied. That is a Python design proposal requiring original-behavior review; this fixed nonempty source example does not establish it. Exact `Int` width, overflow, reassociation, and the distinction between a reduction and a fold remain open. The value `120` cannot decide them. A later discriminating probe must use the numeric/effect policy being considered; choosing floating-point or saturating arithmetic now would add a new policy merely to make a test interesting.

## E3: two proposed spellings of a runtime branch with FIFO state

Original source: `spatial@e7a8f2f:test/spatial/tests/feature/control/FIFOBranch.scala:9-31`. Preserve two FIFOs of capacity `128`, runtime enqueue counts, a contribution chosen by the first FIFO's emptiness, and the scalar reduction output. The fixture counts are `13` and `25`, giving the source-derived expectation `78 + 300 = 378`.

The source uses `Reduce(Reg[Int])`, not `Reduce(0)`. The explicit-accumulator overload passes neither an identity nor a fold initialization; the default register constructor allocates a register with the type's zero reset value. Sources: `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87`; `spatial@e7a8f2f:src/spatial/lang/Reg.scala:48-57`. The sketches retain this distinction with an explicit accumulator and `identity=None`. A zero reset value must not silently become a reduction identity or a fold seed.

### Source capture

```python
@kernel
def fifo_branch(count1: In[Int], count2: In[Int], result: Out[Int]):
    fifo1: Fifo[Int, 128]
    fifo2: Fifo[Int, 128]
    accumulator: Reg[Int] = 0

    for i in foreach(0, count1):
        fifo1.enq(i)
    for i in foreach(0, count2):
        fifo2.enq(i)

    def contribution(i: Int) -> Int:
        if fifo1.is_empty():
            return fifo2.deq()
        else:
            return fifo1.deq()

    total: Int = reduce(0, count1 + count2, identity=None,
                        accumulator=accumulator, combine="add",
                        body=contribution)
    result = total
```

Proposed interpretation: source capture retains the condition and both return regions. During represented execution, the condition observes FIFO state and exactly one selected `deq` consumes one value. The untaken branch consumes nothing. The helper is captured without executing its `if`, its dequeues, or the surrounding loops in host Python. Its unused index records that the controller has a counted contribution domain even though the FIFO choice depends on state.

### Explicit builder

```python
k = Kernel("fifo_branch")
count1 = k.input_scalar("count1", Int)
count2 = k.input_scalar("count2", Int)
result = k.output_scalar("result", Int)
fifo1 = k.fifo(Int, 128)
fifo2 = k.fifo(Int, 128)
accumulator = k.reg(Int, reset=0)

with k.foreach(0, count1) as i:
    fifo1.enq(i)
with k.foreach(0, count2) as i:
    fifo2.enq(i)

with k.reduce(0, count1 + count2, identity=None,
              accumulator=accumulator, combine="add") as reduction:
    with k.if_else(fifo1.is_empty()) as choice:
        with choice.then_():
            reduction.contribute(fifo2.deq())
        with choice.else_():
            reduction.contribute(fifo1.deq())

result.write(reduction.value)
```

Proposed interpretation: Python enters both branch contexts during construction, but each `deq` records an effect in its own branch region; neither pops a host queue. Each branch records one contribution to the enclosing reduction. The checker would require exactly one contribution on every reachable runtime path. `is_empty` builds a state observation rather than returning a host Boolean. Ordinary `if fifo1.is_empty()` in builder code must not silently select a construction-time path; a symbolic truth conversion should report the unsupported use. This is a proposed builder guard, not observed package behavior.

### Common functional model for discussion

Both forms use the following **proposed reference-execution policy** for this illustration: finish the first fill region, finish the second, then evaluate contribution bodies in increasing index order, completing a body's selected FIFO effect before evaluating the next body. FIFO allocation starts with empty queues. For this nonempty reduction without an identity, the first contribution seeds the accumulator and later contributions combine with it; the register reset is not added as another contribution. These are explicit candidate semantics to compare, not a verified description of every original Spatial controller or generated schedule.

The review domain is the supplied positive counts within capacity. Extending it to zero or negative counts, empty identity-free reductions, capacity faults, blocking behavior, or parallel contribution bodies requires a separate decision. A possible common rule is to reject an empty identity-free reduction; deciding when the compiler can prove nonemptiness versus require a runtime guard remains open.

Under that candidate model, the small trace is derived by hand:

| Point | FIFO state or selected effect | Accumulation |
|---|---|---|
| Before fills | Both queues empty | Accumulator reset value is `0`, with no reduction contribution yet |
| After fills | FIFO 1 contains `0…12`; FIFO 2 contains `0…24` | No contribution yet |
| Contributions `0…12` | Condition false; dequeue FIFO 1 values `0…12` in order; FIFO 2 unchanged | First contribution seeds the reduction; cumulative sum after this group is `78` |
| Contribution `13` | FIFO 1 empty; condition true; dequeue `0` from FIFO 2 | Sum stays `78` |
| Contributions `14…37` | Condition true; dequeue FIFO 2 values `1…24` in order | Final sum is `378`; both queues are empty |

The trace states the candidate's behavior more strongly than its final sum. It has not been observed in a Python compiler or checked against an original Spatial execution. Getting `378` alone would not demonstrate correct branch laziness, queue order, occupancy, or controller semantics. Review of original reduction/effect handling and a later branch-sensitive probe remain necessary before claiming preservation.

## Comparison after the first six sketches

| Question | Source-capture proposal | Builder proposal | Evidence still needed |
|---|---|---|---|
| Program regions | Function, loop, helper, and branch syntax are interpreted as Spatial regions | Contexts explicitly construct the same region structure | Closed supported subset and region/scope rules |
| Capture versus execution | No shown kernel/helper body executes in host Python | Host runs construction once; symbolic operations record represented work | File/notebook capture contract and policy for arbitrary host actions |
| Contributions and lazy effects | Helper returns yield contributions; statement `if` retains both paths | `contribute` and branch contexts retain path-specific effects | Path completeness, effect legality, and error examples |
| Identity and state | Annotations and intrinsic arguments distinguish result, register reset, identity, and output writes | Typed handles and explicit calls express those same distinctions | Numeric rules, empty domains, mutation/rebinding, and result lifetime |
| Diagnostics | Source syntax can retain expression locations and literal spelling | Constructors need a defined location/literal provenance mechanism | Matched invalid examples with primary and related-source labels |

This is an inspection of designed spellings. Six written examples establish neither implementation coverage nor diagnostic quality, usability, semantic equivalence, or a preferred surface. Both proposals still need a fair treatment of composition and generated kernels. A framework choice or a line-count comparison would not close those questions.

## Fair comparison protocol

Before comparing a case, list its common intended behavior and unresolved rules. Use the same data movement, numeric policy, initialization, reduction behavior, and state effects for both designs. Give both enough design effort to express the case clearly; do not compare an ideal source form with a deliberately cumbersome builder.

For each complete listing, explain:

1. What executes while capturing or constructing the program, and what the represented accelerator does later.
2. How declarations, updates, memory identity, loop regions, and result lifetime are represented.
3. How both runtime branch bodies survive capture while only the selected stateful operation takes effect during execution.
4. What literal spelling and source locations reach diagnostics, including file and notebook input.
5. How a reusable or generated kernel is expressed without silently executing hardware control during construction.

Report line/concept counts only as descriptive observations. They are not evidence of learning difficulty. No learner study is currently planned or claimed by this small source comparison.

## Diagnostic and semantic probes

Draft one uninitialized read, one incompatible numeric use, one unsupported construct, and one branch/effect-order case. State the proposed policy, the responsible check, and the intended source label. Do not report a proposed error as output from a compiler.

The simple E2 sum can hide differences between a reduction and a fold; add a written case that exposes the candidate's chosen numeric or effect policy. The E3 final sum can hide an incorrect order of FIFO consumption; review the candidate trace above and add a case whose output or remaining state changes when an untaken branch consumes. Verify original controller and simulator behavior before claiming that model preserves Spatial.

## Completion and decision

The packet now contains six illustrative listings, their intended statement-level meaning, source-derived expected values, a candidate FIFO trace, the evidence ledger, and an initial comparison. Python syntax checks do not validate the invented APIs or their semantics. Diagnostic sketches and the semantic review below remain necessary before proposing a surface decision in the shared decision queue.

Remaining research, in order:

1. Verify original reduction/fold, accumulator, branch, and FIFO behavior against the relevant implementation paths. Separate original behavior from each proposed policy above and from the earlier Rust redesign.
2. Review the common numeric, effect, scope, result-lifetime, and empty-domain rules; retain both surface alternatives while those rules change. Add the discriminating reduction and branch probes rather than relying only on `120` or `378`.
3. Complete matched error examples, construction/capture contracts, source provenance, and a small reusable/generated-kernel case. Identify any expression the current sketches cannot represent cleanly.
4. Record a reasoned surface recommendation and its strongest objection. After review, design the unchecked and checked program objects, Python checker, and reference simulator. Investigate HLS mapping from that meaning afterward; writing these examples is not approval to implement either frontend.

The earlier source-capture preference is a hypothesis. Neither alternative is selected here. The conclusion must not depend on the implementation language, maintenance scarcity, or HLS tuning; those would answer different questions.

## Review checks on 30 September 2026

All six Python blocks passed `ast.parse` as separate source snippets. No snippet was imported or executed, and the check does not establish that any named API exists. The cited original example, reduction-constructor, and register-constructor ranges were checked directly at `spatial@e7a8f2f`. The E1 listings and their stated constraints were preserved. No simulator, HLS tool, learner study, or end-to-end diagnostic was run for this study.

## Distillation plan

After the relevant decision is adopted, distill its contract into the Python specification. Preserve this study and its rejected alternatives. Research on source semantics stays linked to the original Spatial specification and pinned sources; the future Python specification must say which behavior it preserves or deliberately changes.
