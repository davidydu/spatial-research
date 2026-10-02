---
type: reference
title: "Spatial to Python: the course examples"
project: spatial-python
date: 2026-10-01
status: proposed
adoption_status: proposed
implementation_status: not-implemented
related:
  - "[[PY-R012 - Lab1 Syntax and Host Mapping]]"
  - "[[PY-R013 - Controllers Reductions and Lab2 Mapping]]"
  - "[[PY-R014 - Convolution Windows and Lab3 Mapping]]"
  - "[[60 - Course Syntax and Compiler Trace]]"
---

# Spatial to Python: the course examples

**The proposed Python language keeps Spatial's memories, controllers and reductions visible.** A register becomes `Reg[Int]`, a local memory becomes `Sram[Int, 16]`, and a Spatial loop becomes `for i in foreach(0, 16):`. The compiler reads that source, checks its meaning and builds a program that the Python reference simulator can run. HLS lowering comes after that.

These are proposed language spellings, not a working package. This atlas answers what a rewrite looks like using the [Digital Systems Design Lab](https://kelayamatoz.github.io/Digital-Systems-Design-Lab/) examples. The linked studies contain complete proposed kernels, source evidence, deliberate changes and compiler obligations. [[60 - Course Syntax and Compiler Trace]] fixes the shared signatures and follows the examples through the compiler.

## Start with the familiar constructs

All Python in this table is **captured kernel source**, except rows explicitly marked host. Names come from a fixed Spatial prelude. An annotation declaring storage is a language operation; ordinary Python would not allocate that memory merely by seeing the annotation.

| Spatial spelling | Proposed Python spelling | What carries over |
|---|---|---|
| `@spatial class ...; Accel { ... }` | `@kernel` on a typed function | One captured accelerator entry; ordinary host setup is separate |
| `ArgIn[Int]` | Parameter `x: In[Int]` | Input value, fixed type; use `x` in the kernel |
| `ArgOut[Int]` | Parameter `y: Out[Int]`; `y = expression` | Writable output port, checked before publishing complete outputs |
| `HostIO[Int]` | Parameter `x: InOut[Int]` | Initialized readable and writable scalar port |
| `Reg[Int](0)` | `r: Reg[Int] = reg(reset=0)` | Stateful register and explicit reset image |
| `r.value`; `r := x`; `r :+= x` | `r.value`; `r.value = x`; `r.value += x` | Ordered read/write; augmented assignment reads once |
| `val x = expression` | `x: Int = expression` | Immutable typed local value; no arbitrary Python object |
| `type T = FixPt[TRUE,_24,_8]` | `Fix[True, 24, 8]` | Signed 32-bit fixed point: 24 integer/sign bits and 8 fractional bits |
| `DRAM[T](N)` | Parameter `a: In[Dram[T, N]]` or `Out`/`InOut` | External memory handle with shape and access direction |
| `SRAM[T](16)` | `a: Sram[T, 16]` | Fresh local storage; reads require initialization |
| `a(i,j)`; `a(i,j)=x` | `a[i,j]`; `a[i,j] = x` | Per-axis bounds, resource identity and ordered access |
| `a(i::j)`; `a(i,*)` | `a[i:j]`; `a[i,:]` | Aliasing view, not an implicit copy |
| `tile load a(base::base+16)` | `load(tile, a[base:base+16])` | Destination first, checked shape, transfer then visibility |
| `a(base::base+16) store tile` | `store(a[base:base+16], tile)` | Destination first here too |
| `FIFO[Int](16)` | `q: Fifo[Int, 16]` | Bounded ordered queue |
| `q.enq(x)`; `q.deq()`; `q.isEmpty` | `q.enq(x)`; `q.deq()`; `q.is_empty()` | State-changing actions and observed status; no implicit blocking |
| `FILO` / `LIFO` | `q: Lifo[Int, 16]`; `push` / `pop` | Stack order; old cheatsheet names/errors are recorded in R012 |
| `Foreach(0 until N)` | `for i in foreach(0, N):` | Structural Index loop; preserves the controller |
| `Sequential.Foreach(N by B)` | `for base in sequential(0, N, step=B):` | Each iteration completes before the next |
| `Pipe.Foreach(... par P)` | `for i in pipe_range(0, N, par=P):` | Pipelined schedule request with a checked domain |
| `Pipe { ... }`; `Pipe.II(2)` | `with pipe():`; `with pipe(ii=2):` | Explicit region and requested initiation interval |
| `if (c) a else b` | `a if c else b` or a statement `if` | Only the selected runtime branch performs effects |
| `mux(c,a,b)` | `select(c, a, b)` on already evaluated values | Preserve operand effects before selecting; moving effectful operands into lazy branches is a deliberate semantic change |
| `Reduce(0)(N by 1){...}{_+_}` | `reduce(0, N, identity=0, body=term, combine="add")` | Typed contribution helper, verified addition law, explicit identity |
| `Fold(acc)(...){...}{...}` | `fold(0, N, accumulator=acc, body=term, combine=combine)` | Existing initialized accumulator is the seed; ordered fold is a deliberate redesign |
| `MemReduce(dst)(...){tile}{_+_}` | `mem_reduce(dst, 0, N, body=tile, combine="add")` | One memory contribution per map index, combined elementwise |
| Returning mapper-local SRAM | `return contribute(tile)` with `Contribution[Sram[...]]` result | Explicit lifetime transfer into the memory reduction |
| `MemFold(dst)(...){tile}{_+_}` | `mem_fold(dst, 0, N, body=tile, combine="add")` | Existing initialized destination cells supply seeds |
| `FSM(start)(test){action}{next}` | `fsm(start, test=test, action=action, next=next_state)` | Three typed helpers; test → action completion → next |
| `LUT[Int](2,2)(1,2,3,4)` | `w: Lut[Int,2,2] = lut(((1,2),(3,4)))` | Immutable, shape-checked literal image |
| `LineBuffer[Int](3,C)` | `lb: LineBuffer[Int,3,C]` | Published row history; unavailable history cannot be read |
| Runtime C with bounded line capacity | `lb: LineBuffer[Int,3,MAX_C] = line_buffer(width=C)` | Immutable logical width C, finite meta capacity MAX_C; active views use C |
| `RegFile[Int](3,3)` | `sr: RegFile[Int,3,3]` | Register window initialized with its default typed-zero reset image |
| `sr.reset(c==0)` | `sr.reset(enable=c == 0)` | Conditional reset to the declared image |
| `sr(i,*) <<= value` | `sr[i,:].shift(value)` | Insert at column zero; move the old row toward larger columns |
| `abs(x)` | `spatial.math.abs(x)` | Registered numeric rule, including overflow behavior |
| `setArg`, `setMem`, `getArg`, `getMem` | Host bindings passed to `prepare`; outputs from successful `simulate` | Explicit typed ingress, completion check and output decoding; see R012 |
| Host `Array.tabulate`, files, gold, `assert` | Ordinary Python lists/arrays, file I/O and assertions | Host executes these; captured kernel source is never imported to run it |

Source basis and exact ranges: R012 covers the Lab 1 rows; R013 covers controllers, reductions, FSM and GEMM; R014 covers windows and convolution. The HostIO extension comes from `spatial-apps@2185958:src/UnitTests.scala:390-433`. This table summarizes proposed choices, not a claim of source-to-source or cycle-for-cycle compatibility.

## Read complete programs

| Question | Worked proposal |
|---|---|
| How do I add two inputs, then move a tile through SRAM? | [[PY-R012 - Lab1 Syntax and Host Mapping|Scalar add, two-buffer tiled scale, scalar reduction and host invocation]] |
| How do state and a branch interact? | [[PY-R001 - Programming Model Study|The existing E3 FIFO-branch example]]; [[PY-R012 - Lab1 Syntax and Host Mapping|the course FIFO-scale exercise completion]] |
| How does a whole SRAM contribute to a reduction? | [[PY-R013 - Controllers Reductions and Lab2 Mapping#L2-04/05: complete memory reduction and fold proposals|Memory reduction and memory fold]] |
| How does the FSM become Python? | [[PY-R013 - Controllers Reductions and Lab2 Mapping#L2-06: complete FSM proposal|Typed FSM test, action and next-state helpers]] |
| What does a larger tiled algorithm look like? | [[PY-R013 - Controllers Reductions and Lab2 Mapping#L2-09/10/11: complete proposed tiled outer-product GEMM|Runtime-size GEMM with tails and leased memory contributions]] |
| What changes if each output is a dot product? | [[PY-R013 - Controllers Reductions and Lab2 Mapping#Dot-product GEMM as a distinct designed comparison|Separate scalar-reduction decomposition]] |
| What does convolution look like? | [[PY-R014 - Convolution Windows and Lab3 Mapping|LineBuffer, RegFile, LUT and nested reductions]] |

The course leaves some bodies for students. Our completed MemFold, FIFO exercise and inner GEMM proposals are labeled as new designs. The convolution proposal translates a separate completed public CS217 fixture with an explicit warm-up repair; it is not proof that the current tutorial contains that solution.

## Three kinds of Python value

| Place | Example | Who handles it |
|---|---|---|
| Ordinary host | `inputs = list(range(32))` | Python executes it to prepare a run |
| Specialization input | `B: Meta[Size]` | Compiler evaluates admitted structural data before allocating finite storage |
| Accelerator runtime | `x: In[Int]`; loop `i: Index` | Checked program evaluates it during the invocation |

`Int` has wrapping 32-bit arithmetic. `Index` is an exact structural coordinate with bounds obligations. Writing an Index into Int storage uses `embed(Int, i)`. Reading an integral fixed value in an index slot preserves the arithmetic that produced it before interpreting its signed/unsigned value as a coordinate. Shape parameters and dynamic input values must not become arbitrary Python objects or implicit specialization decisions.

Typed local declarations are the current explicit design. Inferring obvious immutable value types could be added later without changing the semantic IR; it is not required to make the examples expressible. Memory identity, capacity, numeric widths and controller structure remain explicit even if such inference is adopted.

## Parallelism and buffering are still part of the design

The homepage-linked Products example loads two independent tiles inside `Parallel` (`spatial-apps@2185958:src/Products.scala:33-55`). The proposed form names the two tasks:

```python
@kernel
def paired_load(a: In[Dram[Int,16]], b: In[Dram[Int,16]],
                dst: Out[Dram[Int,16]]):
    tile_a: Sram[Int,16]
    tile_b: Sram[Int,16]
    result: Sram[Int,16]
    with parallel():
        with task("load_a"):
            load(tile_a, a)
        with task("load_b"):
            load(tile_b, b)
    for i in foreach(0,16):
        result[i] = tile_a[i] * tile_b[i]
    store(dst, result)
```

This is a new small illustration of the same fork/join requirement, not a translation of the entire outer-product application. Both loads complete before the multiply loop. Overlapping writes or incompatible shared resources require a legal protocol or a diagnostic.

`par`, `ii` and versioned buffering requests live in a checked implementation plan. The course's `.buffer` on GEMM C becomes a request for separate live tile versions with proven reuse, rather than permission to ignore dependencies. The compiler must preserve the load/compute/store behavior when it overlaps stages. [[60 - Course Syntax and Compiler Trace#Schedule and storage requests|The exact plan record]] ties every request to a stable controller or resource identity and distinguishes a preference from a hard requirement.

## What the source set covers

All source pins, upstreams and licenses or missing-license observations are recorded in [[reference-clones]]. The course homepage names the six lab pages and three reference files at `digital-systems-design-lab@b4896ab:index.md:12-31`.

| Source | Review coverage | Result |
|---|---|---|
| Lab 1 Part 1 + Part 2 | Whole pages: program/host examples and hardware workflow | R012 stable L1 IDs; complete proposed kernels and explicit host records |
| Lab 2 Part 1 + Part 2 | Whole pages: controllers, memory fold, FSM, LUT, GEMM and hardware workflow | R013 L2-01…L2-16; source TODOs and corrections retained |
| Lab 3 Part 1 + Part 2 | Whole pages: convolution, windows, GEMM/HLS tasks | R014 stable L3 IDs; explicit initialization and fixture differences |
| Cheatsheet | Language forms and known inconsistent spellings | Cross-checked against public compiler source; typos are not language requirements |
| Public CS217 language/EE109 source | Targeted declarations and completed public fixtures | Public pin c1979ce, distinct from local e7a8f2f |
| Products.scala | Whole 141-line file; outer and dot product control/memory forms | Parallel loads, nested reductions, host gold and parameter requests mapped |
| UnitTests.scala, MachSuite.scala | Construct inventory plus selected spans, not every algorithm/body | Extended forms below route to the existing full-language studies |
| Project milestones, prior student reports, vendor setup | Context and later validation workflow | Not treated as additional completed kernel translations |

The historical reference files total 7,729 lines. This review does **not** claim 7,729 translated or executed lines. Full language-family design is separately accounted in [[01 - Python Coverage Ledger]]; exact source-version compatibility needs explicit fixtures.

## Extended forms from the linked reference designs

| Source form and inspected evidence | Python design route | Required distinction |
|---|---|---|
| Tunable tile/par values and `bound`, Products 16–22, 93–99 | `Meta[Size]`, `requires` and finite plan search domains | Structural specialization choices versus runtime bounds; historical range shorthand is not a runtime Python range |
| `StreamIn`, `StreamOut`, `Accel(*)`, UnitTests 39–49 | Typed stream ports, explicit communicating task and forever policy | Arrival/close/stop/back-pressure is part of the environment contract, not an ordered FIFO side effect |
| `HostIO` and arrays of argument ports, UnitTests 390–433 | `InOut[T]`; finite schema-expanded port bundle | Preserve alias/ownership and ABI identity; host list construction is outside the captured kernel |
| Sparse gather/scatter, UnitTests 2221–2248, 2290–2327 | Registered transfer with index-memory operand and bounds/collision policy | Repeated scatter indices need specified order/conflict handling; not NumPy advanced indexing by accident |
| `Stream` with stage FIFOs, UnitTests 2561–2596 | Explicit `stream()`/named tasks and declared channel protocol | Task context alone does not convert `Fifo` into a blocking channel |
| Tensor ranks 3/4/5, UnitTests 199–329 | Same ranked memory descriptor and per-axis views | Rank is not fixed at two; flattening must not hide per-axis bounds |
| Saturating and stochastic operators, UnitTests 3148–3254 | Explicit overflow and RNG profiles in the numeric engine | Random consumption/order and intermediate saturation cannot be inherited from host arithmetic |
| Stencil and untiled dot-product GEMM, MachSuite 571–652, 1399–1454 | Window protocol and scalar-reduction studies | Exact intermediate rounding and input/output edges belong to semantics |

References in this table are all `spatial-apps@2185958:src/<named file>:<range>`. [[50 - Library and Migration Recipes]] covers library expansion and [[30 - State Simulator and HLS Blueprint]] covers the protocols. These are design routes, not newly implemented support claims. Do not substitute an old example's target identifier or original compiler bug for an adopted Python contract.

## What this establishes

The concrete programs now drive the architecture: source acquisition, typed names/shapes, exact numbers, explicit state/effects, temporary-memory lifetimes, controller regions and checked plan metadata. The next research layer is no longer a generic “Python → HLS” arrow. It is [[60 - Course Syntax and Compiler Trace|a compiler trace with acceptance and rejection cases]], checked against these examples. [[08 - Course Syntax and Architecture Audit]] records the review and its limits.
