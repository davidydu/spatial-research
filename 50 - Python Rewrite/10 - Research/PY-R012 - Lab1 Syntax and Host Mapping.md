---
type: deep-dive
title: "Lab 1 Spatial syntax, proposed Python spelling, and host workflow"
topic: course-lab1-python-syntax-mapping
scope: python-rewrite
source_files:
  - "digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:162-561"
  - "digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:160-350"
  - "digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:40-142"
  - "spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:9-97"
  - "spatial@c1979ce:src/spatial/lang/Reg.scala:9-107"
  - "spatial@c1979ce:src/spatial/lang/FIFO.scala:31-87"
session: 2026-10-01
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[10 - Source Checker and IR Blueprint]]"
  - "[[40 - Package and Conformance Blueprint]]"
  - "[[60 - Course Syntax and Compiler Trace]]"
verified:
  - "2026-10-01"
---

# Lab 1: from actual course syntax to a proposed Python program

## Scope, evidence, and stage boundary

[judgment] Lab 1 is a useful first acceptance workload because it already crosses the important boundaries: host inputs, a typed accelerator interface, on-chip state, ordered transfers, controllers, scalar reductions, and host checking. The proposed compiler must preserve those boundaries before selecting an IR framework or emitting HLS. A translated arithmetic expression alone does not cover the lab.

[measured] This inventory reads the pinned Markdown sources of [Lab 1 Spatial](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part1_spatial.md), [Lab 1 FPGA flow](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab1_part2_f2_fpga.md), and the [cheatsheet](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/spatial-cheatsheet.md). The live [course page](https://kelayamatoz.github.io/Digital-Systems-Design-Lab/lab1_part1_spatial.html) was also opened on 2026-10-01; pinned source line numbers below, rather than rendered-page line numbers, define the evidence. The course selects the CS217 branch (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:117-129`). Ambiguous library behavior is checked against public CS217 commit `c1979ceb715cec239b6de36408a365aba5b7c709`; its upstream is [stanford-ppl/spatial](https://github.com/stanford-ppl/spatial/tree/c1979ceb715cec239b6de36408a365aba5b7c709). [[reference-clones]] records the source manifests. The earlier local `spatial@e7a8f2f` snapshot remains historical evidence, not an assumed public GitHub blob.

[designed] Every Python spelling below is **unimplemented proposed syntax**, including spellings already reviewed in the contracts. The authority is [[10 - Python Language Contract]], [[10 - Source Checker and IR Blueprint]], [[40 - Package and Conformance Blueprint]], and the explicit course refinements in [[60 - Course Syntax and Compiler Trace]]. This note does not change those documents. The inventory's old spelling and citation are source facts; its Python spelling, obligations, and proposed compiler records are design. This column boundary supplies that distinction throughout the tables.

[designed] Stage labels:

- **H — host:** ordinary Python executes argument parsing, input creation, source acquisition, compiler calls, output decoding, and assertions.
- **K — captured kernel:** the compiler reads source text. It does not execute decorators, annotations, function bodies, imports, or callbacks as Python. A `for` creates a controller region, not a host loop.
- **M — meta:** exact immutable compile-time values and type/shape descriptors are interpreted by the bounded meta evaluator.
- **T — target/tool:** a plan, emitted project, vendor simulation, or device run; this stage is separate from reference simulation.

[designed] The Scala page's surrounding code is staged host code in its Spatial application. Mapping that responsibility to ordinary Python is a deliberate redesign. In particular, `simpleLoadStore` contains host transfers and an `Accel` block; translating it into a captured Python helper containing host API calls would cross the proposed boundary illegally.

## Construct inventory

The row IDs are stable references for examples and acceptance cases. Quoted names such as `storage.read` are proposed semantic operation families from the source blueprint, not claims that those classes already exist.

### Application, scalar I/O, and host data

| ID | Original spelling | Proposed Python spelling | Stage | Semantic obligation | Compiler record or check | Pinned source |
|---|---|---|---|---|---|---|
| L1-01 | `import spatial.dsl._`; `@spatial class ... extends SpatialTest`; `main(args: Array[String]): Unit` | Dedicated source unit containing `@kernel def scalar_add(...)`; separate ordinary Python host driver | H acquisition; K declaration | Freeze source and dependencies without executing them; host test class is not accelerator state | `CaptureBundle`, source/prelude digest, entry Definition ID, typed port signature | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:164-173` |
| L1-02 | `type T = Int` | Use `Int` directly in this mapping; a generic version would bind a registered type descriptor through meta | M | Proposed `Int` is signed wrapping 32-bit data; Python `int` is not its runtime semantics | Exact numeric descriptor and profile ID; no arbitrary type alias assignment in captured module | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:178-189` |
| L1-03 | `override def runtimeArgs = "3 5"` | Host test input `argv = ["3", "5"]` or command-line arguments | H | Defaults are host fixture data, not hidden captured defaults or kernel constants | Invocation provenance records chosen values; captured signature has no Python default expressions | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:182-189` |
| L1-04 | `args(0).to[T]`, `args(1).to[T]` | Host `n = int(argv[0]); m = int(argv[1])`, then checked Int32 encoding | H | Parse text before launch; check ingress range or select an explicit conversion policy; never call host `int` inside K | Typed scalar bits in port bindings; host conversion diagnostic before `prepare` succeeds | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:185-197` |
| L1-05 | `val x = ...` | H: `x = ...`; K value: `x: Int = ...`; K resource: annotated descriptor declaration | H or K according to location | A captured scalar is immutable; a resource name denotes a handle. The same Scala keyword cannot determine Python stage | Symbol category, declaration owner/order, SSA value or storage handle; reject reassignment of immutable value | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:188-200` |
| L1-06 | `ArgIn[T]` and `setArg(arg, value)` | Signature `a: In[Int]`; host binding for `a` passed to `prepare` | K interface; H binding | Ingress is immutable for invocation; an input is not writable accelerator Reg storage | Port direction/type, exact typed ingress bits, invocation ownership | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:191-197` |
| L1-07 | `ArgOut[T]` | Signature `result: Out[Int]` | K | Output begins uninitialized; successful completion requires initialization; ordered repeated writes publish the last successful value | Writable result-cell descriptor, output initialization analysis and active checks | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:199-200` |
| L1-08 | `Accel { ... }` | Body of selected `@kernel` definition | K | Separate interface and accelerator region from host launch; merely capturing the definition does not launch anything | Kernel entry region, explicit captures/ports, order domain; host calls only after checking | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:205-215` |
| L1-09 | `argRegIn0.value`; implicit read in `b1(ii) * x` | Input value `a`; true local register read `r.value` | K | Scalar ingress is already a typed immutable value; Reg reads remain explicit state observations | Distinguish port value from storage handle; no generic implicit handle-to-number cast | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:207-213`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:341-354` |
| L1-10 | `argRegOut := a + b` | `result = a + b`; local register `r.value = value` | K | `=` mutates only an existing writable output/Reg/storage lvalue; RHS effects precede target evaluation | `LValuePlan`, capability check, `numeric.eval` then `storage.write`; initialized-output fact | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:212-214` |
| L1-11 | `+`, `*`, `1.to[T]` | Typed `+`, `*`; context-checked literal `1` | K; separate H gold arithmetic | Wrap at declared Int32 operation boundaries; preserve expression tree and exact literal ingestion | Numeric op ID/format/overflow policy; no NumPy/Python width inference | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:213-214`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:302-304`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:352-355` |
| L1-12 | `getArg(argRegOut)` | Decode named scalar in `RunResult.complete_outputs` after successful completion | H | Fault/budget/wait partial state is not a completed output; decode signed bits explicitly | Run outcome and output completeness; typed output descriptor | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:217-234` |
| L1-13 | `println`, `print`, `cksum`, `assert(cksum == 1)` | Host `print(...)` and `assert got == gold` | H | Host test remains outside captured grammar; ordinary Python assertions are not registered kernel assertions | No accelerator node; test evidence associates run identity with independent oracle | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:220-234`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:381-393` |
| L1-14 | `def simpleLoadStore(srcHost: Array[T], value: T) = {... Accel {...}; getMem(...)}` | Host orchestration function plus independent captured `tiled_scale` | H and K split | Preserve explicit copy-in, computation, copy-out responsibilities; do not capture Python arrays or launch API calls inside K | Host function composes the five workflow calls; kernel Definition contains only typed ports/regions | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:329-364` |
| L1-15 | `Array.tabulate[Int](arraySize) { i => i % 256 }` | Host `[i % 256 for i in range(32)]`, then Int32 array encoding | H | Host comprehension is allowed here but excluded in captured source; fixture is exactly `0..31` | Typed backing, shape `(32,)`, stride `(4,)`, 128 encoded bytes | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:366-374` |
| L1-16 | `src.map { _ * value }`; `dst.zip(gold){_ == _}.reduce{_&&_}` | Host `[wrap_i32(v * scale) for v in src]`; shape equality and `all(a == b for a,b in zip(...))` | H | Match numeric profile and compare all cells; check equal lengths because host `zip` truncates | Independent oracle; no captured reduction node for this host check | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:376-393` |
| L1-17 | Host `(0 until arraySize) foreach ...`; `src.reduce{_+_}` | Host `for i in range(32)` and `wrap_i32(sum(src))` | H | Do not confuse host iteration/collection reduction with accelerator Foreach/Reduce. Modular addition makes final wrapping sufficient for this sum | No K controller; preserve host input/output association | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:381-390`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:518-527` |

### Storage, transfers, queues, and controllers

| ID | Original spelling | Proposed Python spelling | Stage | Semantic obligation | Compiler record or check | Pinned source |
|---|---|---|---|---|---|---|
| L1-18 | `DRAM[T](N)`; general `DRAM[data_type](n0,n1,...)` | `src: In[Dram[Int,32]]`, `dst: Out[Dram[Int,32]]`; higher ranks use an explicitly registered shape form | K port descriptor; H backing | Same logical extents do not imply disjoint backing; fixed Lab1 shape is 32, not host data-dependent allocation inside K | Borrowed memory Handle, shape/capability and backing/generation bindings; reject rank/size/type mismatch | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:293-298`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:326-339` |
| L1-19 | `setMem(srcFPGA, srcHost)` | Host input backing/view with encoded data in `bindings`; default reference preparation snapshots it | H | Copy each backing once and reconstruct aliases; do not separately copy aliased ports and change meaning | Backing ID, byte layout, initialized cells, alias-preserving preparation | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:335-339` |
| L1-20 | `getMem(dstFPGA)` | Decode completed `dst` view after simulation or matched device adapter | H | Outputs carry shape/type and completeness; target copy-back belongs to adapter, not a kernel read | `RunResult.complete_outputs`, view decoding; no implicit successful output on fault | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:357-363` |
| L1-21 | `SRAM[T](tileSize)`; `b1`, `b2` | `tile_in: Sram[Int,16]`; `tile_out: Sram[Int,16]` | K | Two logical resources, each scoped to the represented tile activation; no source merge into one scratch buffer | Two `storage.allocate` sites with lifetime/generation/capacity; SRAM initialization tracking | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:343-358` |
| L1-22 | `sram(i)` | `tile_in[i]` | K | Index is a structural Index; active per-axis bounds and initialized-cell checks precede read | `storage.read`, Handle and Index operand, guard/token where required | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:302-304`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:352-355` |
| L1-23 | `sram(i) = ...` | `tile_out[i] = ...` | K | Check writable capability and address bounds; preserve RHS-before-target order; mark exactly the written cell initialized | `LValuePlan`, ordered `storage.write`, logical coordinate/init update | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:302-304`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:352-355` |
| L1-24 | `dram(i::i+tileSize)` | `src[base:base + 16]` | K | Half-open view with captured endpoints; no Python slice clipping or negative-index adjustment; preserve original backing identity | `storage.view`, affine coordinate map and logical extent16; active backing bounds before flattening | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:305-306`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:345-358` |
| L1-25 | `b1 load srcFPGA(...)` | `load(tile_in, src[base:base + 16])` | K | Destination first; array transfer snapshots/preflights selected source, then completes before dependent computation | `transfer.copy`, shape/type compatibility, read/write capability and completion token | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:345-348` |
| L1-26 | `dstFPGA(...) store b2` | `store(dst[base:base + 16], tile_out)` | K | Destination first; every active stored cell must be initialized; output view extents match transfer | `transfer.copy` with reversed resource roles from load; publication/completion ordering | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:351-358` |
| L1-27 | `Foreach(N by n) { i => ... }` | `for i in foreach(0,N,step=n): ...` | K; bounds M/Index | Default zero start, exclusive end, nonzero step; single Index binder; no implicit host iterable | `control.loop` Foreach domain, binder, captures, active-tail mask and scheduling preferences | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:313-319` |
| L1-28 | `Sequential.Foreach(N by tileSize)` | `for base in sequential(0,32,step=16): ...` | K | Two outer tile activations; preserve sequential controller intent and load/compute/store dependencies | `control.loop` Sequential; two iteration ordinals and distinct per-activation local lifetimes | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:326-359` |
| L1-29 | `Foreach(tileSize by 1)` | `for i in foreach(0,16): ...` | K | Sixteen valid cells; Foreach is not an assertion that hardware realizes 16 lanes or II1 | Domain/trip-count facts; dependencies and target schedule feasibility kept separately | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:350-355` |
| L1-30 | `FIFO[T](tileSize)` | `q: Fifo[Int,16]` | K | Bounded queue, initially empty; Ordered mode in proposed descriptor; no automatic communicating behavior | Queue resource kind/capacity/reset/occupancy and mode; storage handle is not an array | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:411-427` |
| L1-31 | `f1 load dram(i::i+tileSize)` | `load(q, src[base:base + 16])` | K | Produce 16 tokens in increasing source coordinate order; capacity must accommodate the transfer | Transfer endpoint roles and queue transition sequence; counts, occupancy and completion | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:416-419` |
| L1-32 | `f1.enq(data)` | `q.enq(value)` | K | Exactly one production, after operand evaluation; full Ordered queue faults, not silently drops data | `state.action` enqueue, input token, payload type, capacity check, next token | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:420-421` |
| L1-33 | `val data = f1.deq()` | `value: Int = q.deq()` | K | Exactly one destructive consume; empty Ordered queue faults; repeated uses of `value` do not consume again | Queue dequeue transition produces typed value + next order token | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:422-423` |
| L1-34 | `f1.peek()` | `q.peek()` or `head: Int = q.peek()` | K | Non-destructive observation; it still checks availability and cannot be freely reordered across mutations | Queue peek transition; observation/may-fault token; occupancy unchanged | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:424-425` |
| L1-35 | `Reg[T](0)`; `accum.value` | `accum: Reg[Int] = reg(reset=0)`; `accum.value` | K | Reset image and mutable cell identity are explicit; zero reset is distinct from reduction identity | `storage.allocate` Reg, reset image; ordered reads/writes; reduction ownership checks | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:477-483`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:501-515` |
| L1-36 | `Reduce(accum)(N by n){...}{_+_}` | `reduce(0,N,step=n,body=contribution,combine=add,accumulator=accum)` | K | Existing accumulator is destination, not seed; helper combines two Int values; lawful regrouping requires checked algebraic evidence | `reduction.scalar`, explicit accumulator ownership, contribution region/DefinitionRef, combine/law descriptor | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:477-483`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:78-87` |
| L1-37 | `Reduce(0)(tileSize by 1){ii => b1(ii)}{_+_}` | `reduce(0,16,identity=0,body=element,combine=add)` | K | Literal 0 is supplied identity, not “start adding the old accumulator value”; helper result is explicit scalar | Typed identity and empty behavior, `Index -> Int` contribution signature; no untyped lambda/string guessing | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:505-512`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:55-62` |
| L1-38 | `Sequential.Reduce(accum)`; nested Reduce is last expression of mapper | `reduce(...,accumulator=accum,schedule="sequential")`; helper ends `return subtotal` | K | Retain nested contributions and ordered tile loads; local SRAM may not escape; Python helper needs explicit typed return | Outer/inner `reduction.scalar`, nested helper captures/lifetimes, `region.return` and completion token | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:503-515` |
| L1-39 | `Fold(a)(N by n){...}{...}`, with `a=Reg[T](1)` | `fold(0,N,step=n,accumulator=a,body=contribution,combine=add)` | K | Snapshot current accumulator once as seed; seed contributes, including zero-trip case; preserve ordered fold semantics | Seed/cell snapshot, ordered-fold policy, typed contribution/combine, completion publication | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:532-541`; `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:101-103` |
| L1-40 | `MemFold`, `MemReduce` named but deferred | Registered `mem_fold`, `mem_reduce` family; no Lab1 translation claimed | K family, no Lab1 concrete call | A mention does not supply shapes, contribution lifetime, identity or algorithm; route exact examples to later lab study | Coverage disposition only; memory reduction records require both map and destination domains | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:449-450`; `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:544-547` |

### FPGA host workflow and evidence

| ID | Original spelling/responsibility | Proposed Python spelling/responsibility | Stage | Semantic obligation | Compiler or evidence record | Pinned source |
|---|---|---|---|---|---|---|
| L1-41 | `ddr_wr32(pcis_handle,in_ptr+i*4,val)` | A selected device adapter uploads the typed input backing | H/T | Source cells are Int32 here; physical byte offsets, device allocation/address response and host/device copy are explicit | ABI, device allocation/transfer evidence, binding address table; Python object IDs are never device addresses | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:264-273` |
| L1-42 | `ocl_wr32(... ADDR_IN_LO/HI, ADDR_OUT_LO/HI, ADDR_X, ADDR_SIZE ...)` | Adapter applies checked plan's pointer/scalar control-register map | H/T | Low/high pointer words, parameter width/layout and address spaces come from the target interface manifest | `ComponentPlan`/ABI register map, pointer width, exact encoded values | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:275-288` |
| L1-43 | `ocl_wr32(...ADDR_CTRL,AP_START)`; wait before reads | Adapter starts invocation and obtains completion evidence before publishing outputs | H/T | The page uses a wait; elapsed wall time alone must not become the proposed completion proof | Launch/status protocol and completion trace; timeout yields incomplete result | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:290-303` |
| L1-44 | `ddr_rd32(...out_ptr+i*4,&got_val)` and gold comparison | Download completed output backing, decode typed cells, compare host oracle | H/T | Require completed invocation and matched ABI; preserve partial effects separately on failure | Run/device evidence linked to project and invocation identities | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:305-325` |
| L1-45 | HLS `m_axi`/`s_axilite`, `vadd`, `design_top.sv`, DDR arbiter | `plan(checked,target,binding_contract)` then `emit(plan)` and `validate(project,toolchain)` | T | Logical port count is not physical bus count; wrapper/interface compatibility and arbitration need target evidence | Implementation plan, interface bundles/widths, source map and wrapper/model hashes | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:174-182`; `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:200-215` |
| L1-46 | Scala simulation, `PostExecution.html`, cycle/latency/II questions; RTL and FPGA tests | Reference `simulate` plus separately identified schedule/vendor/device evidence | H/T | Reference functional success establishes no FPGA cycles, achieved II, RTL correctness or device success | `RunResult` versus schedule/report evidence; requested/estimated/measured metrics remain distinct | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:398-409`; `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:216-251` |

## Complete proposed kernels

[designed] These definitions are source text to capture. They may be parsed for Python syntax; none has been imported, compiled by a Python Spatial compiler, simulated, or synthesized. The fixed core prelude supplies registered names. Explicit declarative imports are also possible; `from spatial import *` is excluded by the proposed grammar even though the Scala example imports `spatial.dsl._`.

### Scalar addition: printed demo and assigned three-input extension

[measured] The printed demo binds 3 and 5 and computes their sum; the assignment asks for three integers and names the result `Lab1Part1RegExample3` in its summary. These are distinct cases (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:238-273`, `286-287`, `549-553`).

```python
@kernel
def scalar_add(a: In[Int], b: In[Int], result: Out[Int]):
    result = a + b


@kernel
def scalar_add3(a: In[Int], b: In[Int], c: In[Int], result: Out[Int]):
    result = a + b + c
```

[designed] The first definition accounts for L1-01–13. The second is a proposed completion of the assignment, not a recovered omitted listing. The two-input fixture expects 8; a selected three-input fixture `(3,5,7)` expects 15. A boundary fixture `(2147483647,1)` expects `-2147483648` under the proposed Int32 profile, so an ordinary unbounded Python addition cannot serve as its oracle without wrapping.

### Tiled scale: exact E1, 32 elements and two 16-element SRAMs

[measured] The source fixes `N=32`, `tileSize=16`, two different local memories, a sequential outer controller and an ordinary inner Foreach (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:324-359`). The following source block is the E1 spelling in [[PY-R001 - Programming Model Study]], preserved exactly.

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

[designed] For host values `src=[i % 256 for i in range(32)]` and `scale=2`, output is `[0,2,...,62]`. Tiles cover source/destination intervals `[0,16)` and `[16,32)`; each input load precedes 16 reads/multiplies/writes and the corresponding output store. There is no tail in this fixed case. Replacing `32` with arbitrary runtime `N` would require a separate bound/tail design, not merely changing the host array length. L1-14–29 explain the complete boundary.

[measured] The FPGA walkthrough uses a different host fixture `i+1` and describes a `NUM_WORDS` transfer width (`digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:253-272`). Its expected values with scale2 are `[2,4,...,64]`. This is a labeled input variant, not evidence that the Spatial E1 input was `1..32` or that a 512-bit bus is its semantic type.

### FIFO scale: explicit proposed answer to the exercise

[measured] The page gives allocation/load/enqueue/dequeue/peek snippets and asks the student to reimplement Part 2 with FIFO, but does not print the completed FIFO app (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:411-447`).

```python
@kernel
def fifo_scale(src: In[Dram[Int, 32]],
               scale: In[Int],
               dst: Out[Dram[Int, 32]]):
    for base in sequential(0, 32, step=16):
        input_q: Fifo[Int, 16]
        output_q: Fifo[Int, 16]
        load(input_q, src[base:base + 16])
        for i in foreach(0, 16):
            value: Int = input_q.deq()
            output_q.enq(value * scale)
        store(dst[base:base + 16], output_q)
```

[designed] This proposed completion replaces both SRAMs by queues; using a FIFO source plus SRAM destination is another possible exercise answer, but is not this fixture. `store(...,output_q)` is the proposed registered queue-transfer endpoint case, supported by the compiler's transfer family rather than a printed Lab1 store example. Before each inner iteration `j`, input occupancy is `16-j` and output occupancy is `j`; after all 16, the output store consumes exactly 16 tokens. No queue exceeds capacity or underflows. Ordinary Ordered queue semantics are sufficient; there is no implicit producer task, stream group, backpressure or parallel enqueue/dequeue batch. A backend that overlaps operations must preserve the admitted effect order and capacity behavior. `peek` remains inventoried but is not artificially added to an algorithm that does not need it.

### Nested reduction: explicit typed helpers and accumulator destination

[measured] The printed Reduce example has an explicit outer accumulator, a sequential outer tile reduction, a local 16-cell SRAM, an inner identity-zero reduction, then an output read of the accumulator (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:488-528`). The overload implementation separates an explicit accumulator from identity/init fields (`spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:17-52`, `55-62`, `78-87`).

[designed] The exact keyword convention is the course refinement in [[60 - Course Syntax and Compiler Trace]]. `body` and `combine` below resolve typed source definitions, not live Python callables. The admitted default reduction is lawful only after the compiler verifies the Int32 modular-add law for `add`; a function name alone is insufficient proof. The mapper may perform ordered reads/transfers, whose order is retained independently of lawful regrouping of the resulting values.

```python
@helper(effects="pure")
def add(left: Int, right: Int) -> Int:
    return left + right


@kernel
def tiled_sum(src: In[Dram[Int, 32]], result: Out[Int]):
    accum: Reg[Int] = reg(reset=0)

    def tile_sum(base: Index) -> Int:
        tile: Sram[Int, 16]
        load(tile, src[base:base + 16])

        def element(i: Index) -> Int:
            return tile[i]

        subtotal: Int = reduce(0, 16, identity=0,
                               body=element, combine=add)
        return subtotal

    reduce(0, 32, step=16, accumulator=accum,
           body=tile_sum, combine=add, schedule="sequential")
    result = accum.value
```

[designed] The value of the outer `accum` before reduction is not an input contribution. Changing only its reset from0 to7 must still produce496 for `src=0..31`. The inner reductions produce120 and376; the outer combines them to496. Both helper returns are scalar Int, so no local SRAM handle escapes. `Index` parameters preserve the source checker's loop-binder rule; no Index-to-Int conversion is needed merely to address `tile[i]`.

### Fold: proposed completion with a discriminating seed

[measured] The page's Fold snippet explicitly reads its register's existing value as the starting value; the assignment asks for a Fold sum but supplies no complete program (`digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:532-545`).

```python
@kernel
def tiled_fold(src: In[Dram[Int, 32]], result: Out[Int]):
    accum: Reg[Int] = reg(reset=1)

    def tile_sum(base: Index) -> Int:
        tile: Sram[Int, 16]
        load(tile, src[base:base + 16])

        def element(i: Index) -> Int:
            return tile[i]

        subtotal: Int = reduce(0, 16, identity=0,
                               body=element, combine=add)
        return subtotal

    fold(0, 32, step=16, accumulator=accum,
         body=tile_sum, combine=add, schedule="sequential")
    result = accum.value
```

[designed] This definition belongs to the same source module as `add` above. The explicit seed1 fixture produces497 and demonstrates that Fold reads the seed while Reduce ignores the destination's previous value. To answer an assignment interpreted as the unseeded sum, the proposed exercise variant changes the reset to0 and expects496; that variant is not sufficient by itself to distinguish Fold from Reduce. The words “sum of an element” in the assignment are underspecified; the chosen interpretation is a sum of the example's 32-element input array, with the seed behavior tested separately. No unprinted course answer is claimed.

[designed] Empty-domain variations are separate fixtures, not silent changes to the fixed32 examples. Under [[20 - Python Numeric Contract]], an enabled identity-zero reduction over an empty domain returns0; an enabled identity-free reduction faults unless nonemptiness is established; an empty Fold returns its captured seed. A disabled controller evaluates no seed or contribution and performs no destination write. These cases require distinct IR fields even though the printed nonempty addition examples cannot distinguish them all.

## Complete proposed host workflows

[designed] The 2026-10-03 refinement in [[PY-R016 - Source and Host Workflow Refinement]] closes the constructor gaps previously recorded here. [[40 - Package and Conformance Blueprint]] owns the exact public SourceUnit/CaptureBundle, typed input/backing, environment/budget and completed-output interfaces. The following driver is **syntactically valid proposed ordinary Python**. The Spatial package/API is unimplemented; this is not a working compiler demonstration. Save the unchanged complete tiled_scale kernel above as `lab1.py`. The driver reads it as text and never imports it.

### One complete tiled-scale driver

```python
from pathlib import Path
from spatial import (
    Int, SourceUnit, CaptureBundle, core_prelude, capture, specialize,
    check, prepare, simulate, Error, ScalarInput, Backing, Environment, Budget,
)

unit = SourceUnit(
    module_id="lab1", text=Path("lab1.py").read_text(encoding="utf-8"),
    label="lab1.py",
)
bundle = CaptureBundle(
    entry=("lab1", "tiled_scale"), sources=(unit,), dependencies=(),
    prelude=core_prelude(),
)
template = capture(bundle)
program = specialize(template, {})
checked_result = check(program, profile="reference.guarded.v1")
if isinstance(checked_result, Error):
    raise RuntimeError(checked_result.diagnostics)
checked = checked_result.value

values = tuple(i % 256 for i in range(32))
src = Backing.from_ints(name="input", dtype=Int, shape=(32,), values=values)
dst = Backing.empty(name="output", dtype=Int, shape=(32,))
bindings = {
    "src": src.view(access="read"),
    "scale": ScalarInput.from_int(dtype=Int, value=2),
    "dst": dst.view(access="write"),
}
prepared_result = prepare(checked, bindings, session=None)
if isinstance(prepared_result, Error):
    raise RuntimeError(prepared_result.diagnostics)
run = simulate(
    prepared_result.value, environment=Environment.closed_memory(),
    budget=Budget(steps=100_000, numeric_work=100_000, trace_bytes=1_048_576),
)
if run.outcome != "Completed":
    raise RuntimeError((run.outcome, run.diagnostics, run.run_identity))
output = run.complete_outputs["dst"]
assert output.dtype == Int and output.shape == (32,)
got = output.to_ints()
gold = tuple(((x * 2 + (1 << 31)) % (1 << 32)) - (1 << 31) for x in values)
assert got == gold
print("PASS", run.run_identity)
```

[designed] `capture` and `specialize` return a Template and UncheckedProgram directly; expected failures raise `DiagnosticError` with immutable diagnostics and terminate this script. `check`/`prepare` retain their specified Ok/Error alternatives. The difference preserves the existing stage signatures and is explicit in the package contract; no invented `.unwrap()` is needed. These budgets are proposed observation limits, not evidence of interpreter completion within them.

[designed] Backing factories freeze typed portable ABI input bytes. Default reference preparation snapshots each backing once, retaining all shared views; output extraction reads the completed invocation snapshot, not the original `dst` object. The output backing's physical zero-fill is not source-visible initialization. Each of its 32 logical cells must be initialized before Completed can publish the buffer. Any fault, stop, cancellation or budget outcome has `complete_outputs=None`, with committed partial state inspectable separately. Completed is the state blueprint's existing success tag, not an FPGA/cycle-accuracy claim.

### Scalar input and scalar output through the same stages

[designed] Save the complete scalar module above as `scalar.py`. This block uses the same imports as the complete driver and demonstrates the scalar binding and public decoder without changing the launch contract:

```python
scalar_unit = SourceUnit(
    module_id="scalar", text=Path("scalar.py").read_text(encoding="utf-8"),
    label="scalar.py",
)
scalar_bundle = CaptureBundle(
    entry=("scalar", "scalar_add"), sources=(scalar_unit,), dependencies=(),
    prelude=core_prelude(),
)
scalar_program = specialize(capture(scalar_bundle), {})
scalar_checked = check(scalar_program, profile="reference.guarded.v1")
if isinstance(scalar_checked, Error):
    raise RuntimeError(scalar_checked.diagnostics)
scalar_prepared = prepare(scalar_checked.value, {
    "a": ScalarInput.from_int(dtype=Int, value=3),
    "b": ScalarInput.from_int(dtype=Int, value=5),
}, session=None)
if isinstance(scalar_prepared, Error):
    raise RuntimeError(scalar_prepared.diagnostics)
scalar_run = simulate(
    scalar_prepared.value, environment=Environment.closed_memory(),
    budget=Budget(steps=100_000, numeric_work=100_000, trace_bytes=1_048_576),
)
if scalar_run.outcome != "Completed":
    raise RuntimeError((scalar_run.outcome, scalar_run.diagnostics))
assert scalar_run.complete_outputs["result"].to_int() == 8
print("PASS", scalar_run.run_identity)
```

[designed] Scalar `result: Out[Int]` has no host seed or binding entry; it is an uninitialized output cell until the kernel writes it. Binding a scalar Out is an error. For `scalar_add3`, select that export and add `"c": ScalarInput.from_int(dtype=Int,value=7)`; the independent expected result is 15.

### A wrong binding must stop before execution

[designed] A 31-cell output allocation is valid host data, but incompatible with E1's fixed 32-cell dst. With the tile driver's checked program and bindings, the proposed distinguishing failure is:

```python
bad_bindings = dict(bindings)
bad_bindings["dst"] = Backing.empty(
    name="wrong_output", dtype=Int, shape=(31,),
).view(access="write")
rejected = prepare(checked, bad_bindings, session=None)
assert isinstance(rejected, Error)
assert any(d.code == "HOST.SHAPE_MISMATCH" for d in rejected.diagnostics)
```

[designed] The diagnostic identifies port dst, expected `(32,)`, actual `(31,)`, and its source declaration. No invocation is created. Separately, `ScalarInput.from_int(dtype=Int,value=1 << 31)` raises `DiagnosticError(HOST.INVALID_ARGUMENT)` before preparation; the constructor does not silently wrap. Wrong dtype, extra/missing port names, and unsupported read/write capabilities also reject. A negative `IndexInput(value=...)` used as a runtime extent fails the declared shape precondition during prepare.

### Concrete binding records and outputs

[designed] These record descriptions instantiate the package ABI: little-endian scalar slots, exact types, explicit backing identity and initialization. Each array fixture uses distinct input and output backing IDs. Output bytes may be physically zeroed, but their source-visible initialized-cell map begins empty; allocation zero-fill is not logical initialization evidence. `Out[Int]` requires no host seed.

| Fixture / entry | Scalar bindings | Buffer bindings | Completed output and independent oracle |
|---|---|---|---|
| L1-SCALAR / `scalar_add` | `a` signed Int32 bits `00000003`; `b` bits `00000005` | None | `result` bits `00000008`, signed value8 |
| L1-SCALAR3 / `scalar_add3` | `a=3`, `b=5`, `c=7`, each encoded Int32 | None | `result=15`; extension of the exercise, not printed demo |
| L1-SRAM / `tiled_scale` | `scale=2`, Int32 bits `00000002` | `src`: backing `input`, 128 bytes with cell i=`i`, shape `(32,)`, offset0, strides `(4,)`, Int32, read capability, all32 cells initialized. `dst`: distinct backing `output`, 128 bytes, same layout, write capability, initially no initialized cells | `dst[i]=wrap_i32(i*2)` for every i in `[0,32)`; exact shape `(32,)` |
| L1-FIFO / `fifo_scale` | Same `scale` | Same two distinct host backings and views as L1-SRAM; queues are invocation-local resources declared by K, never host arrays disguised as queues | Same32 expected values as L1-SRAM; trace additionally accounts for32 source queue productions,32 explicit dequeues,32 explicit output enqueues and32 store consumes |
| L1-REDUCE / `tiled_sum` | No scalar ingress | Only `src` as above; scalar result is declared by K | `result=496`, from `32*31/2`; tile subtotals120 and376 |
| L1-FOLD / `tiled_fold` | No scalar ingress | Only `src` as above | `result=497`, from seed1 plus496; reset0 exercise variant yields496 |

[designed] Hex values in the table denote canonical raw scalar bits, not already ordered byte strings. Thus Int32 bits `00000003` encode the four host ABI bytes `03 00 00 00`. The array's first two cells encode `00 00 00 00 01 00 00 00`; its last cell encodes `1f 00 00 00`. The input length and byte count are checked before launch. Buffer views share backing IDs only when the fixture explicitly intends aliasing; variable names never prove disjointness.

[designed] Ordinary Python can build independent host oracle data without any Spatial API:

```python
def wrap_i32(value):
    return ((value + (1 << 31)) % (1 << 32)) - (1 << 31)


argv = ["3", "5"]
n, m = (int(text) for text in argv)
assert -(1 << 31) <= n < (1 << 31)
assert -(1 << 31) <= m < (1 << 31)
scalar_gold = wrap_i32(n + m)

src = [i % 256 for i in range(32)]
scale = 2
src_bytes = b"".join(value.to_bytes(4, "little", signed=True) for value in src)
scale_gold = [wrap_i32(value * scale) for value in src]
reduce_gold = wrap_i32(sum(src))
fold_gold = wrap_i32(1 + sum(src))
assert len(src_bytes) == 128
assert (scalar_gold, reduce_gold, fold_gold) == (8, 496, 497)
```

[designed] For each fixture, use its full kernel module and construct the typed bindings above in the same five-stage sequence. In particular, scalar addition still runs capture/specialize/check/prepare/simulate; FIFO does not acquire a separate shortcut simulator; nested Reduce/Fold do not execute their helpers as host callbacks. The same checked program can later feed `plan(checked,target,binding_contract)`, but successful reference execution grants no target capability or FPGA deployment evidence.

## Source problems and explicit proposed repairs

| Finding | Evidence | Disposition |
|---|---|---|
| Cheatsheet says `dm(...) tore sm` | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:86-89`; main page correctly says `store` at `lab1_part1_spatial.md:305-306` | [designed] Treat as typo. Proposed `store(dst,src)` does not register `tore`. |
| Cheatsheet says `f1.deq(data)` | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:91-96`; source overloads `deq()` and `deq(en:Bit)` at `spatial@c1979ce:src/spatial/lang/FIFO.scala:52-56` | [measured] A Bit argument can be an enable; it is not a dequeued payload passed into deq. [designed] Follow the main page's `data = f1.deq()`; do not translate the cheatsheet spelling as an output parameter. |
| “Fold, sequential” example spells `Sequential.Reduce` | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:136-140` | [designed] Flag the mislabeled example. Map a real Fold to proposed `fold(...,schedule="sequential")`, retaining seed semantics. |
| Cheatsheet shows `@virtualize`/`SpatialApp` while Lab1 uses `@spatial`/`SpatialTest` | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:40-68`; `lab1_part1_spatial.md:164-173` | [measured] Different scaffolds are printed. [designed] Do not combine them into a new assumed Scala syntax; both migrate to source acquisition and separate host orchestration. |
| FILO appears only in commented Lab1 text and a supplemental cheatsheet | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:429-441`; `spatial-cheatsheet.md:98-103` | [designed] Record supplemental LIFO family, not an executed Lab1 exercise. The commented snippet's enqueue/dequeue spellings are not authority for a new Python Lifo API. |
| Lab1 says Reduce begins with first element, but also calls `Reduce(0)` | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:483-511`, `532-534`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:55-62`, `78-87` | [measured] Overloads distinguish explicit destination/no identity from constant identity. [designed] Preserve that distinction; neither destination reset nor identity is a Fold seed. |
| Public CS217's scalar Fold overloads disagree in constructor flag | `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:90-96`; explicit register route at `src/spatial/lang/control/MemReduceClass.scala:101-103` | [measured] Lift seed passes `isFold=true`; Sym seed passes `false`; explicit Reg delegates to MemFold with `fold=true`. [judgment] This is an upstream overload anomaly, not a reason to copy ambiguous behavior into Python. The mapped Lab1 form uses explicit Reg; proposed Python seed/accumulator rules are stated independently. |
| `b1(ii) * x` omits `.value` | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:354`; implicit conversion at `spatial@c1979ce:src/spatial/lang/api/Implicits.scala:61-69` | [measured] Spatial admits implicit Reg read. [designed] Python scalar `scale:In[Int]` is already a value; true Reg remains explicit `.value`. Do not allow arbitrary handles in numeric slots. |
| R001 examples use `combine="add"`; source blueprint rejects arbitrary string-op guessing; exact keyword schema was incomplete | [[PY-R001 - Programming Model Study]], [[10 - Source Checker and IR Blueprint]] | [designed] Retain a closed registered `"add"` alias and typed DefinitionRef alternative in [[60 - Course Syntax and Compiler Trace]]. This note uses named typed helper `add`; neither an arbitrary string nor its name proves a law. |
| Earlier package records lacked exact Python constructors/decoders | [[40 - Package and Conformance Blueprint]]; [[PY-R016 - Source and Host Workflow Refinement]] | [designed] The 2026-10-03 refinement supplies typed constructors, exact failure behavior and public completed-output decoders. The five stages and raw-source boundary remain; syntactic validity is not implemented compiler support. |
| Page labels `gold` printing as “Sent in” | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:379-384` | [measured] Printed expression is gold, not src. [designed] Host examples label source, expected and actual separately; no algorithm change is inferred. |
| Controller introduction labels schematic fragments as Python, but contains C-style loop notation | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:454-470` | [measured] The page itself calls these fragments pseudo code. [designed] Do not treat `for (i; ...)`, `list.len` or its `accum + i` illustration as an accepted Python/Spatial program or an exact sum oracle. The complete Reduce listing supplies the mapped algorithm. |

## Every course request has a disposition

[measured] Setup, simulation, physical integration and submission are all part of the pages, but they are not all language constructs. The mapping preserves their role without claiming those tools or private skeleton files were executed/read.

| Course request | Evidence | Research disposition |
|---|---|---|
| Install OS packages, SDKMAN, Java/Scala/sbt; configure memory; build CS217 Spatial | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:27-136` | Host/toolchain setup for the original route. No Python syntax translation or installation performed. Proposed Python package baseline is separately specified. |
| Accept Classroom skeleton; run `testOnly` or `run.sh` | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:139-160`, `276-281` | Original execution route, accounted for by L1-46. No private Classroom acceptance or course-app execution. |
| Implement three-input sum | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:286-287`, `549-550` | Complete proposed `scalar_add3` plus `(3,5,7)->15` host fixture above. |
| Run DRAM/SRAM simulation; fill total cycles, inner latency and II | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:398-409`, `551` | Full semantic mapping and fixture provided. Measurements remain unperformed; no values fabricated from loop counts. |
| Reimplement Part2 with FIFO and simulate | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:443-447`, `552` | Complete proposed `fifo_scale` and host fixture; page's omitted implementation is not claimed recovered. |
| Implement Fold sum | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:544-545`, `553` | Explicit proposed completion above; unseeded exercise variant and seed discriminator are separate. |
| Learn MemReduce/MemFold later | `digital-systems-design-lab@b4896ab:lab1_part1_spatial.md:547` | Recorded as deferred mention L1-40; no fake complete Lab1 example. |
| Set up instance access, credentials/S3, aws-fpga release/environment | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:1-158` | Original infrastructure workflow, outside captured language. No credentials, account operations, uploads or running instance required for this research. |
| Explain HLS pragmas, selected protocols and physical interface count | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:200-204` | Compiler requirement L1-45. Exact instance count requires the identified skeleton `vadd.cpp`; the page does not supply those pragma calls, so no count is inferred. |
| Inspect generated module and explain the DDR MUX | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:205-215` | Wrapper/ABI/ownership analysis requirement. The page names the arbiter but omits the wrapper implementation; do not invent its clients or arbitration policy. |
| Run RTL simulation; report transfer/compute cycles and explain overhead | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:216-224` | Requires actual matched RTL testbench/report evidence; no cycle claim from reference simulator. |
| Build FPGA, generate/check AFI, program/run test; compare transfer and compute time | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:225-251` | Separate vendor/device gates; not performed. Page's repeated “RTL Sim” labels in its FPGA questions do not make those observations RTL evidence. |
| Understand host upload/configure/start/wait/read/compare flow | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:253-325` | Explicit L1-41–44 mapping; supplied C fragments analyzed, without claiming full `vadd.cpp` or host C translation. |
| Repeat flow for remaining parts; answer `lab1_submit.md`; submit code, logs and commit/repo | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:329-340`; `lab1_part1_spatial.md:556-561` | Submission/evidence checklist belongs to the course, not a compiler feature. No completed lab submission, logs or nonexistent run evidence generated. |
| Explore dataflow pragma and linked Vitis examples | `digital-systems-design-lab@b4896ab:lab1_part2_f2_fpga.md:343-350` | Optional HLS research leads. No source-level task parallelism is inferred merely from a mention of a pragma. |

## Compiler requirements derived from these programs

[judgment] The concrete mappings above require the following architecture independently of which IR library stores its objects. They fit the existing source/checker/state/package blueprints, but are a source-to-requirement argument rather than an appeal to those blueprints' authority.

| Evidence in the mapping | Required compiler boundary | Distinguishing failure if omitted |
|---|---|---|
| Host `int`, comprehension, print and oracle versus captured markers/controllers (L1-01–17) | Frozen source acquisition, explicit stages and declarative imports | Executing a kernel file runs definition-time host code; blindly capturing host helpers admits arrays and launch calls into K. |
| Scalar ingress, writable output, Reg and SRAM use similar surface names (L1-06–11,21–23,35) | Symbol category/type/capability checking and initialization state | A register handle enters arithmetic; assigning immutable local silently creates recurrence; uninitialized result appears as zero. |
| Fixed tile counts and views (L1-18–29) | Exact structural Index arithmetic, logical coordinate maps and storage identity | Python clipping silently truncates a transfer; aliasing changes meaning; an out-of-bounds tile reads padding. |
| Two SRAMs and queue replacements (L1-21,30–34) | Resource kind/lifetime/generation descriptors, reusable transfer endpoint protocols | Treating FIFO as indexed SRAM repeats a consumed value or erases queue capacity semantics. |
| Queue consume, memory loads and output writes (L1-25–38) | Ordered regions and explicit effect tokens across helpers/controllers | CSE merges two consumes; optimizer hoists store before completion; repeated callback evaluation reloads data. |
| Nested Reduce, destination reset and Fold seed (L1-35–39) | Dedicated reduction records with contributions, typed combine, law/topology, identity/seed/destination and completion | Reduce accidentally adds the old destination; Fold loses its seed; lawful regrouping reorders mapper effects. |
| Completion-gated host result and separate FPGA flow (L1-12,19–20,41–46) | Checked-program/invocation/run/plan/project/evidence separation | Partially written memory is reported as PASS; emitted C++ is presented as measured FPGA success. |

[designed] For exact E1, the normalized graph should show a kernel entry with three port descriptors; one Sequential loop over `0,16`; two local SRAM allocation sites; source-view/load; an inner Foreach with one read, multiply and write per active ordinal; destination-view/store; and explicit completion. It must not become an opaque `tiled_scale` node or require a name-based recognizer. FIFO scale changes resource descriptors and transfer/action endpoints, while retaining the same host interface and controller structure. Nested reduction adds two reduction regions and helper captures without requiring a different frontend architecture. The detailed trace and shared source signatures live in [[60 - Course Syntax and Compiler Trace]].

## Acceptance obligations and verification limits

[designed] Future conformance fixtures should cover the following paired cases; each oracle is independent of a future simulator implementation.

| Fixture | Positive discriminator | Matched negative/boundary |
|---|---|---|
| Scalar ports | `(3,5)->8`, three-input extension15, Int32 wrap boundary | Writing `In[Int]`; missing result write; incompatible host scalar encoding; treating a fault's partial output as complete |
| Exact E1 | Two SRAMs, two16-cell transfers each direction, all32 results, exact E1 text | 31/33-cell binding, wrong stride/byte span, wrong element format; unresolved alias contract; reading tile_out before write |
| FIFO scale | Occupancy proof and ordered consume/produce trace;32 output values | 17-token load into capacity16; empty dequeue; replacing `deq` by `peek`; duplicated consume by expression rewriting |
| Nested Reduce |120+376=496; outer accumulator reset7 still yields496; explicit identity-zero empty case returns0 | Treat reset as seed; identity-free empty case publishes a result; body signature `Int` instead of Index; escaping tile handle; unproved user combine accepted as lawful |
| Fold | Seed1 produces497; seed0 produces496 | Simultaneously supplying `seed` and `accumulator`; losing seed on zero-trip domain; reordering faulting combines |
| Host workflow | Frozen source/prelude and independent typed oracle through the five calls | Modified source reuses stale artifact; raw unchecked program sent to prepare; Error unwrapped; budget outcome printed as PASS |
| Target evidence | Same checked meaning plans/emits with explicit ABI then independently validates | Functional simulation labeled cycle-accurate; interface count guessed from logical ports; AFI/device success inferred from emit |

[measured] This research directly read the pinned course files and the cited public CS217 source ranges. The source examples and host-oracle block were checked for Python parseability without importing captured modules. E1 was compared with the source block in [[PY-R001 - Programming Model Study]]. The ordinary host oracle was independently evaluated for `(8,496,497)` and128-byte input encoding. These checks establish documentation syntax and arithmetic only. There is no Python Spatial compiler acceptance, reference simulation, HLS generation, RTL simulation, device run, or measured cycle/II result in this note.
