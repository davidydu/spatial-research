---
type: deep-dive
title: "Controllers, reductions, and Lab 2: Spatial to Python"
topic: python-course-controller-and-reduction-syntax
scope: python-rewrite
session: 2026-10-01
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
source_files:
  - "digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:1-504"
  - "digital-systems-design-lab@b4896ab:lab2_part2_f2_fpga.md:1-98"
  - "digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:107-142"
  - "spatial@c1979ce:src/spatial/lang/control/Control.scala:9-72"
  - "spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:9-97"
  - "spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:11-104"
  - "spatial@c1979ce:src/spatial/lang/control/FSM.scala:8-24"
  - "spatial@c1979ce:test/spatial/tests/ee109/Lab2Part4LUT.scala:6-26"
verified:
  - "2026-10-01"
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[20 - Python Numeric Contract]]"
  - "[[60 - Course Syntax and Compiler Trace]]"
---

# Controllers, reductions, and Lab 2: Spatial to Python

## Evidence boundary and reading route

[designed] This is a concrete proposed syntax map, with stable `L2-xx` coverage IDs, typed kernels, and checker/lowering obligations. None of the Python Spatial APIs below is implemented or executed here. Python AST acceptance is a small syntax check, not a Spatial compilation result. [[60 - Course Syntax and Compiler Trace]] owns the shared source registrations; [[10 - Source Checker and IR Blueprint]], [[20 - Numeric Engine Blueprint]], and [[30 - State Simulator and HLS Blueprint]] own the meanings summarized here.

[measured] Read all of the pinned Lab 2 Part 1, Part 2, and cheatsheet Markdown, including commented historical instructions. The public [Lab 2 Part 1 page](https://kelayamatoz.github.io/Digital-Systems-Design-Lab/lab2_part1_spatial.html) and [Part 2 page](https://kelayamatoz.github.io/Digital-Systems-Design-Lab/lab2_part2_f2_fpga.html) were also opened on 2026-10-01. Exact source authority for quotations and line ranges is [the course repository at b4896abffd19bcc3f319a49d7a919e1cf70d5221](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/tree/b4896abffd19bcc3f319a49d7a919e1cf70d5221), not a mutable rendered page.

[measured] The public compiler source pin used below is [stanford-ppl/spatial at c1979ceb715cec239b6de36408a365aba5b7c709](https://github.com/stanford-ppl/spatial/tree/c1979ceb715cec239b6de36408a365aba5b7c709). `Control.scala`, `CtrlOpt.scala`, `ReduceClass.scala`, `MemReduceClass.scala`, `ForeachClass.scala`, `FSM.scala`, `Parallel.scala`, `Counter.scala`, and `Lab2Part3BasicCondFSM.scala` were byte-compared with the previously inspected local Spatial pin `e7a8f2f7f776dd0c5ac7fc03f16b3ed4d97021f0`; all nine matched. This establishes the public citation lane for these files, not identity of the two entire repositories.

[measured] The actual page teaches blocked **outer-product GEMM**, with six conceptual loops and the inner computation intentionally left for the student. Its host gold computes each output as a dot product. It does not give two completed accelerator implementations. Part 2 covers FSM/LUT HLS work and explicitly defers GEMM hardware work to Lab 3. Sources: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:308-368`, `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:387-436`, `digital-systems-design-lab@b4896ab:lab2_part2_f2_fpga.md:1-3`.

## Source coverage and corrections

| ID | Actual source material | Treatment in this map | Pinned citation |
|---|---|---|---|
| L2-01 | `Foreach(N by n)` and `Sequential.Foreach` | One Index binder; signed half-open domain; separate scheduling mode | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:107-116` |
| L2-02 | `Reduce` and `Sequential.Reduce` with a Reg | Typed scalar contribution/combine, explicit optional result destination | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:118-128` |
| L2-03 | `Fold`; “Fold, sequential” example actually spells `Sequential.Reduce` | Correct the spelling in the proposed mapping, retain the source error as evidence | `digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:130-140` |
| L2-04 | Complete `MemReduce` of ten all-one SRAMs of length 16 | Complete proposed kernel below; expected sixteen values of 10 | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:44-87` |
| L2-05 | `MemFold` exercise and explicit initialization instruction | Complete proposed translation labeled a designed completion | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:185-190` |
| L2-06 | Complete conditional FSM with start/test/action/next | Complete typed-helper translation; exact original gold vector retained | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:192-263` |
| L2-07 | Alternative FSM rules, implementation left TODO | Complete proposed typed-FSM kernel, explicitly a designed exercise completion | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:265-280` |
| L2-08 | LUT rank/row-major syntax and 3×3 exercise | Complete proposed LUT-add kernel using the shared nested-tuple initializer | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:282-302` |
| L2-09 | Runtime M/N/K, fixed-point type, host initialization and dot-product gold | Runtime shape ports, explicit host zero image, numeric format and reference boundary | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:314-368` |
| L2-10 | Tile sizes 16; K/M/N tiled loops with partial-tile extents | Complete proposed outer-product kernel below preserves this tiling order | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:371-419` |
| L2-11 | Inner outer-product computation left TODO | Typed memory contribution and fold are a designed completion of the exercise | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:427-436` |
| L2-12 | `.buffer`, load/compute/store stages, triple-buffer explanation | Logical memory/version lifetime first; physical versioning requires a verified plan | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:438-461` |
| L2-13 | `par 16`; controller cycle reports and a parallelization exercise | Positive meta par, active-tail mask, verified schedule request | `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:464-485` |
| L2-14 | FSM/LUT Vitis tasks and build/simulation/deployment instructions | Backend evidence requirements, not captured Python syntax or measured results | `digital-systems-design-lab@b4896ab:lab2_part2_f2_fpga.md:21-78` |
| L2-15 | `Pipe`, `Parallel`, `Stream`, directive combinations | Source-language supplement below; these are not worked Lab 2 page examples | `spatial@c1979ce:src/spatial/lang/control/Control.scala:9-72`; `spatial@c1979ce:src/spatial/lang/control/Parallel.scala:9-13` |
| L2-16 | Multiple counters in one controller | Proposed nested single-binder loops or nested reductions; no tuple-unpacking loop syntax | `spatial@c1979ce:src/spatial/lang/control/ForeachClass.scala:10-31`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:19-49` |

[measured] Two additional source blemishes must not silently become language facts: the Part 2 directory command says `Lab1Part3BasicCondFSMAlt`, whereas its submission list says `Lab2Part3BasicCondFSMAlt`; the page's final parallelization sketch lacks a closing brace for `Accel`. Neither sketch is an executed compile fixture. Sources: `digital-systems-design-lab@b4896ab:lab2_part2_f2_fpga.md:21-25`, `digital-systems-design-lab@b4896ab:lab2_part2_f2_fpga.md:91-95`, `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:472-482`.

## Concrete controller syntax map

[designed] All proposed forms in the following tables are captured source; none invokes a Python iterator, context manager, or callback at acquisition time. `start`, `end`, and `step` are structural Index operands. A Python `for` binds exactly one Index; destructuring remains outside the grammar. A sequence of statements within a task stays ordered.

| Original Spatial | Proposed Python spelling | Meaning, compiler representation, and checks | Evidence |
|---|---|---|---|
| `Foreach(N by n){i => body}` | `for i in foreach(0, N, step=n):` | `control.loop(mode=Foreach)` with captured bounds; n≠0; no implicit host range | L2-01; `spatial@c1979ce:src/spatial/lang/control/ForeachClass.scala:9-32` |
| `Sequential.Foreach(a until b by s)` | `for i in sequential(a, b, step=s):` | Ordered completed iterations; not merely `par=1` on a different controller | L2-01; `spatial@c1979ce:src/spatial/lang/control/Control.scala:49-56` |
| `Pipe.Foreach(a until b par p)` | `for i in pipe_range(a, b, par=p):` | Pipe scheduling intent on counted loop; same logical indices and effects | L2-15; `spatial@c1979ce:src/spatial/lang/control/Control.scala:9-14`; `spatial@c1979ce:src/spatial/lang/control/Control.scala:22-33` |
| `Pipe { body }`, `Pipe.II(2) { body }` | `with pipe():` / `with pipe(ii=2):` | `control.region`; body order preserved; II positive meta request, not measured latency | `spatial@c1979ce:src/spatial/lang/control/Control.scala:22-33`; `spatial@c1979ce:src/spatial/lang/control/CtrlOpt.scala:18-25` |
| `Sequential { body }` | `with sequential_region():` | Ordered `control.region`; calls do not become implicit concurrent actors | `spatial@c1979ce:src/spatial/lang/control/Control.scala:49-56` |
| `Parallel { child1; child2 }` | `with parallel():` containing named `with task("..."):` children | `control.task_group` with explicit child ownership, joins, and distinct task tokens; declarations precede group; alias/race checks | `spatial@c1979ce:src/spatial/lang/control/Parallel.scala:9-13` |
| `Stream { stages }` | `with stream():` containing explicit named task children | Streaming task group; typed channel/protocol semantics determine communication. A FIFO's empty ordered dequeue does not become blocking because of this wrapper | `spatial@c1979ce:src/spatial/lang/control/Control.scala:35-47` |
| `Stream.Foreach(domain){body}` | Explicit `stream()` task with a counted `foreach` body | Exposes the task graph instead of inferring stages from arbitrary statements; reference effect order retained, overlap plan separately checked | `spatial@c1979ce:src/spatial/lang/control/Control.scala:9-14`; `spatial@c1979ce:src/spatial/lang/control/Control.scala:35-47` |
| `Stream(*) { body }` | Explicit task with `with forever(...):` and an admitted stop/environment policy | `control.forever`; no fake large range. Source stop/reset-on-exit behavior needs an explicit migration policy, not an inferred Python break | `spatial@c1979ce:src/spatial/lang/control/Control.scala:39-46` |
| `FSM(start)(test){action}{next}` | `fsm(start, test=keep_running, action=step_action, next=next_state)` | `control.fsm`; S Bits-capable; test S→Bool, action S→Unit, next S→S; action completion precedes next, test/next cannot mutate/consume/suspend | L2-06; `spatial@c1979ce:src/spatial/lang/control/FSM.scala:8-24` |
| `Foreach(I by 1, J by 1){(i,j)=>...}` | `for i in foreach(0, I):` then nested `for j in foreach(0, J):` | Two owned loops, two Index binders; exposes hierarchy and per-axis par. Does not promise identical original counter-chain schedule | L2-16; `spatial@c1979ce:src/spatial/lang/control/ForeachClass.scala:14-31` |
| `0 until N by S par P` / `N by S` | `foreach(0, N, step=S, par=P)` or same bounds in reduction call | Counter domain plus separate schedule request. P positive meta; partial last group masks by ordinal, not by executing an invalid lane | L2-13; `spatial@c1979ce:src/spatial/lang/Counter.scala:15-27` |

[designed] The source API makes `Foreach`, `Reduce`, `Fold`, `MemReduce`, and `MemFold` available under each of `Pipe`, `Sequential`, and `Stream`; `Parallel` is a separate block constructor. Python does not invent unsupported expressions such as `parallel.reduce(...)`. Counted scalar/memory reductions accept `schedule="foreach"`, `"sequential"`, or `"pipe"`; an original streaming directive is elaborated into an explicit stream task containing the chosen reduction. `Pipe.II(k)` contributes `ii=k` to the request. These are surface translations of scheduling intent, not claims that a new task decomposition is cycle-identical to the original. Source basis: `spatial@c1979ce:src/spatial/lang/control/Control.scala:9-14`, `spatial@c1979ce:src/spatial/lang/control/Control.scala:22-65`, `spatial@c1979ce:src/spatial/lang/control/Parallel.scala:9-13`.

## Exact scalar and memory reduction calls

[designed] The following signature notation is the proposed registration contract, not Python implementation stubs. Common options are `step:Index=1`, `par:Meta[Size]=1`, `schedule:Meta[String]="foreach"`, and `ii:Meta[Size]|None=None`. Positive par/II and nonzero step are checked. Use the registered `enabled` context to guard the whole invocation; disabled invocation performs no bound, seed, contribution, combine, or publication effects. Unspecified identity is a compile-time absence marker, not a runtime Python object.

| Operation | Exact argument shape | Result and initialization |
|---|---|---|
| `reduce` | `reduce(start, end, *, body, combine, identity=None, accumulator=None, step=1, par=1, schedule="foreach", ii=None)` | T result; optional Reg[T] gets that result on success. Old Reg value/reset is not a contribution. Typed lawful combine required; supplied identity validated |
| `fold` | `fold(start, end, *, body, combine, seed=..., accumulator=..., step=1, par=1, schedule="foreach", ii=None)` | Exactly one of seed:T or initialized accumulator:Reg[T]. Seed included once; accumulator variant snapshots then publishes. Ordered combine recurrence |
| `tree_reduce` | `tree_reduce(start, end, *, body, combine, identity=None, empty_result=None, tree="adjacent_pairs", step=1, par=1, schedule="foreach", ii=None)` | T; identity and empty_result mutually exclusive. Identity must be verified neutral; arbitrary empty_result grants no padding law. Both absent means empty-domain fault. Explicit adjacent-pair/carry-odd topology independent of par |
| `mem_reduce` | `mem_reduce(dst, start, end, *, body, combine, identity=None, step=1, par=1, schedule="foreach", ii=None)` | Unit; dst writable local memory/view. Does not read old destination cells as seeds; publishes selected cells only on successful completion |
| `mem_fold` | `mem_fold(dst, start, end, *, body, combine, step=1, par=1, schedule="foreach", ii=None)` | Unit; dst readable/writable and selected cells initialized. Each old cell is snapshotted once as its seed; ordered map/cell combination |
| `mem_tree_reduce` | `mem_tree_reduce(dst, start, end, *, body, combine, identity=None, empty_result=None, tree="adjacent_pairs", step=1, par=1, schedule="foreach", ii=None)` | Unit; leased memory contributions are collected in map order, then each selected cell uses the fixed tree. Identity/empty_result are mutually exclusive; only verified identity permits neutral padding. Success publishes destination cells |

[designed] `mem_tree_reduce` is a new source registration supplied by [[60 - Course Syntax and Compiler Trace#Reductions]], not an original Lab 2 tutorial name. Its meaning is the memory fixed-tree case already specified in [[PY-R002 - Numeric and Reduction Semantics#Proposed reduction contract]] and [[20 - Numeric Engine Blueprint#Reduction laws and reference interpreter]]. It admits typed state-free arbitrary combines without falsely granting associativity. Empty-map validity is checked even for an empty destination: absent identity/empty_result faults; an admitted empty result permits completion with zero cells published.

[designed] Scalar `body` resolves a source DefinitionRef `(Index)->T`; memory `body` resolves `(Index)->Contribution[M]`, with a compatible destination/contribution element type and logical shape. `combine` resolves a source DefinitionRef `(T,T)->T` with no storage/RNG/communication/observable effects, or a closed admitted combine ID such as the existing `"add"`. It never accepts an arbitrary Python callback. The kernels below use explicit typed combine helpers. A helper returning exactly wrapping fixed addition can normalize to the built-in proven addition law; its spelling alone never supplies that proof. Faulting combines are allowed for ordered fold/fixed tree with specified fault order, not freely reassociable reduction. See [[PY-R002 - Numeric and Reduction Semantics#Proposed reduction contract]] and [[20 - Numeric Engine Blueprint#Reduction laws and reference interpreter]].

[designed] `Contribution[M]` and `contribute(fresh_local_memory)` are the source spelling of the existing `ContributionLease` state rule. They are legal only as a memory mapper's terminal yield to its owning reduction. The checker transfers the mapper-local backing root into the reduction lease, validates selected-cell initialization, retains it through reads/snapshots, then releases its generation. An ordinary helper cannot return this object, save it in an aggregate, or return a view of its dying local SRAM. The contribution cannot alias the owned destination. This registration closes the lifecycle gap that `def make_tile(...) -> Sram: return tmp` would otherwise hide. See [[30 - State Simulator and HLS Blueprint#Region-to-continuation construction]].

| Original Spatial | Proposed Python | Meaning/checks | Source |
|---|---|---|---|
| `Reduce(acc)(N by n){map}{op}` | `total:T = reduce(0,N,step=n,body=map,combine=op,accumulator=acc)` | No implicit identity from reset; nonempty proof or empty fault; completion writes acc | `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:37-52`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:78-87` |
| `Reduce(0)(N by n){map}{_+_}` | `total:T = reduce(0,N,step=n,body=map,combine=add,identity=0)` | 0 contextual T and verified addition identity; enabled empty returns 0 | `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:55-74` |
| `Fold(5)(N by n){map}{op}` | `total:T = fold(0,N,step=n,seed=5,body=map,combine=op)` | Seed=5 once; proposed ordered recurrence deliberately differs from arbitrary original unroll-dependent Fold | `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:55-74`; `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:90-96` |
| `Fold(acc)(N by n){map}{op}` | `total:T = fold(0,N,step=n,accumulator=acc,body=map,combine=op)` | Requires initialized acc, owns recurrence, publishes after success | `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:95-96` |
| `MemReduce(dst)(N by n){tile}{op}` | `mem_reduce(dst,0,N,step=n,body=tile,combine=op)` | Separate map domain and destination-cell domain, leased tile, shape/init checks | `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:34-92`; `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:96-99` |
| `MemReduce(dst,zero)(...)` | Same call with `identity=zero` | Neutral element checked in element type; no old destination inclusion | `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:96-99` |
| `MemFold(dst)(...)` | `mem_fold(dst,0,N,step=n,body=tile,combine=op)` | Existing selected destination cells are seeds; an empty map leaves those values | `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:101-104`; `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:185-190` |
| `MemFold(dst,zero)(...)` | `mem_fold` after explicit destination initialization only if that matches the application's intended seed | Original constructor stores both `ident` and `fold=true`; do not reinterpret `zero` as an automatic replacement of existing seeds. Legacy invalid-lane/topology fidelity needs the R002 compatibility policy | `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:11-16`; `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:74-88`; `spatial@c1979ce:src/spatial/lang/control/MemReduceClass.scala:101-104` |

[measured] A concrete original overload discrepancy reinforces that caution: `FoldClass.apply(zero: Lift[A])` sets `isFold=true`, while `apply(zero: Sym[A])` sets `isFold=false`. This map records it and selects an explicit Python seed contract; it does not claim faithful reproduction of both overload paths. Source: `spatial@c1979ce:src/spatial/lang/control/ReduceClass.scala:90-96`.

[designed] Multi-counter reductions need no new tuple binder. A lawful scalar sum can nest typed scalar reduction helpers, each accepting one Index, with explicit identity for an empty inner domain. A general nonassociative Cartesian fold uses nested sequential loops and an explicit Reg recurrence; nesting independent folds with arbitrary seeds is not generally equivalent to one flat fold. If exact original counter-chain topology matters, import an explicit legacy topology or define a separate multidimensional-domain registration before accepting it. `for i, j in foreach(...)` remains rejected.

## L2-04/05: complete memory reduction and fold proposals

[designed] Each block is a complete proposed kernel under the fixed DSL prelude. The first mirrors the completed page example. The second is our completion of its MemFold exercise; no original completed MemFold body is asserted. Both produce sixteen Int values of 10. The identity is explicit in the first; the second initializes every destination element as its seed. Original example and exercise: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:60-87`, `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:185-190`.

```python
@kernel
def lab2_mem_reduce(dst: Out[Dram[Int, 16]]):
    acc: Sram[Int, 16]

    @helper(effects="pure")
    def add_int(left: Int, right: Int) -> Int:
        return left + right

    def ones(i: Index) -> Contribution[Sram[Int, 16]]:
        tmp: Sram[Int, 16]
        for j in foreach(0, 16):
            tmp[j] = 1
        return contribute(tmp)

    mem_reduce(acc, -5, 5, body=ones, combine=add_int, identity=0)
    store(dst, acc)
```

```python
@kernel
def lab2_mem_fold(dst: Out[Dram[Int, 16]]):
    acc: Sram[Int, 16]
    for j in foreach(0, 16):
        acc[j] = 0

    @helper(effects="pure")
    def add_int(left: Int, right: Int) -> Int:
        return left + right

    def ones(i: Index) -> Contribution[Sram[Int, 16]]:
        tmp: Sram[Int, 16]
        for j in foreach(0, 16):
            tmp[j] = 1
        return contribute(tmp)

    mem_fold(acc, -5, 5, body=ones, combine=add_int)
    store(dst, acc)
```

[designed] The negative map indices are structural coordinates; the mapper does not store them as Int. An example that stores i must use `embed(Int, i)` with checked or explicit wrapping policy. `Reg[Int] = reg(reset=0)`, `identity=0`, `seed=0`, and writing zeros into SRAM are four different source operations with different lifecycle points. A disabled invocation and an enabled zero-trip invocation must not be collapsed.

## L2-06: complete FSM proposal

[measured] The page uses an Int state, register reset 0, a separate write of 16, and a 32-element SRAM. Its final transfer requests par=16; the public EE109 fixture has the same FSM/gold but an unannotated final transfer. Sources: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:229-260`; `spatial@c1979ce:test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala:9-37`.

[designed] This kernel preserves the FSM computation. The final store's transfer parallelism is target-plan metadata, separate from the FSM semantics. `Unit` is the owned no-value result type; bare `return` yields Unit. State is Int numeric data, not Index, so its SRAM address expressions use the existing integral-data-to-index-slot rule; no data conversion is silently inserted at writes.

```python
@kernel
def lab2_fsm(dst: Out[Dram[Int, 32]]):
    bram: Sram[Int, 32]
    reg_value: Reg[Int] = reg(reset=0)
    reg_value.value = 16

    @helper(effects="pure")
    def keep_running(state: Int) -> Bool:
        return state < 32

    def write_state(state: Int) -> Unit:
        if state < 16:
            if state < 8:
                bram[31 - state] = state
            else:
                bram[31 - state] = state + 1
        else:
            bram[state - 16] = (
                17 if state == 16 else
                reg_value.value if state == 17 else state
            )
        return

    @helper(effects="pure")
    def advance(state: Int) -> Int:
        return state + 1

    fsm(0, test=keep_running, action=write_state, next=advance)
    store(dst, bram)
```

[designed] Hand-checkable output is `[17,16,18,19,20,21,22,23,24,25,26,27,28,29,30,31,16,15,14,13,12,11,10,9,7,6,5,4,3,2,1,0]`. The output initialization proof must show that the state sequence visits 0 through 31 and that the two address mappings cover all cells exactly once; finite-state execution can discharge this small constant case. A generic checker may instead retain active read/init guards, but cannot assume all memory is initialized just because an FSM exists.

## L2-07: complete proposed alternative FSM exercise

[designed] This is a new proposed completion of the page's explicit 32-element piecewise exercise; the page leaves its accelerator body TODO. State i visits 0 through 31 and writes cell i with i, 2i, 3i, or 4i according to the four consecutive eight-element intervals. It uses typed Test/Action/Next helpers under the shared FSM signature. State remains Int numeric data, with exact integral projection only when used as an address. Source requirements: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:268-280`.

```python
@kernel
def lab2_fsm_alt(dst: Out[Dram[Int, 32]]):
    bram: Sram[Int, 32]

    @helper(effects="pure")
    def keep_running(state: Int) -> Bool:
        return state < 32

    def write_state(state: Int) -> Unit:
        if state < 8:
            bram[state] = state
        elif state < 16:
            bram[state] = state * 2
        elif state < 24:
            bram[state] = state * 3
        else:
            bram[state] = state * 4
        return

    @helper(effects="pure")
    def advance(state: Int) -> Int:
        return state + 1

    fsm(0, test=keep_running, action=write_state, next=advance)
    store(dst, bram)
```

[designed] The complete expected output is `[0,1,2,3,4,5,6,7,16,18,20,22,24,26,28,30,48,51,54,57,60,63,66,69,96,100,104,108,112,116,120,124]`. Equivalently cell i equals `i*(1+i//8)` on this bounded nonnegative domain. All 32 cells are initialized before the store; the terminal state 32 performs no write. The finite-state initialization check must establish those facts, not merely infer them from the existence of an FSM.

## L2-08: complete proposed 3×3 LUT-add exercise

[designed] This is a new proposed completion of the page's LUT exercise: the user supplies a base value and indices i,j; result is base plus the selected entry of the row-major table 1 through 9. The nested immutable tuple follows [[60 - Course Syntax and Compiler Trace#Closed common signatures]], which checks each tuple extent and exact contextual Int leaf. The course requirement remains a 3×3 LUT, not an inferred reshape of a dynamic Python list. Sources: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:282-302`. The public completed Spatial fixture separately confirms Int ports and the same computation at `spatial@c1979ce:test/spatial/tests/ee109/Lab2Part4LUT.scala:6-26`; it does not make the page's exercise body complete.

```python
@kernel
def lab2_lut_add(
    base: In[Int], i: In[Int], j: In[Int], result: Out[Int]
):
    requires(0 <= i < 3)
    requires(0 <= j < 3)
    table: Lut[Int, 3, 3] = lut((
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
    ))
    result = base + table[i, j]
```

[designed] Inputs i,j remain typed Int ports, as in the public fixture; their use in address slots projects the already computed integral values. They do not become meta parameters. For base=11, the nine results in row-major index order are `[12,13,14,15,16,17,18,19,20]`. General expected result is `wrap32(base + 3*i + j + 1)`. Out-of-range indices fail the invocation precondition; missing/ragged LUT image cells or LUT mutation reject. Numeric addition keeps the declared Int wrapping behavior rather than silently widening the output.


## L2-09/10/11: complete proposed tiled outer-product GEMM

[measured] The source uses signed `FixPt[TRUE,_24,_8]`, runtime matrix dimensions, host-initialized zero C, tile sizes 16, and tile-loop order K→M→N. For each K tile it loads existing C and accumulates more outer products. These are distinct from computing each dot product independently. Sources: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:324-344`, `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:365-415`, `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:427-434`.

[designed] The code below is a complete **new proposed completion** of that exercise, not a quoted course solution. `Fix[True,24,8]` is the signed 32-bit format (24 integer bits including sign, 8 fractional bits). M/N/K use bounded runtime `In[Index]` ports so shape arithmetic is exact; that is an explicit ABI redesign from the course's `ArgIn[Int]`. Tile sizes and par are `Meta[Size]`, specialized before allocating finite SRAM capacities. Binding TM=TN=TK=16 and P=1 recovers the tutorial's sizes; changing P changes a request, not numeric meaning. Host initializes C to typed zero to request C=A×B; otherwise this kernel computes C_initial+A×B. C must be disjoint from both input regions; A and B may alias each other because both are read-only. Read-only input annotations alone do not imply disjointness.

[designed] `disjoint(left_memory_or_view,right_memory_or_view)` is a closed requirement predicate used by `requires`, not an arbitrary runtime callback. It lowers to the existing `disjoint(AccessRegion,AccessRegion)` requirement. Invocation preparation resolves common backing/owner identity, offsets, logical cell maps and reachable regions; known-empty regions have empty intersection even on the same backing, and Unknown cannot count as true. A coarse interval test may prove disjointness but cannot always establish the exact result for strided views. This explicit source registration is shared with [[60 - Course Syntax and Compiler Trace]].

[designed] Destination and contribution scratchpad tiles are zero-filled outside the active rectangle. Input A/B scratchpads remain initialized only where loaded, and guarded reads stay within those regions. That deliberate normalization lets every memory contribution and destination have a fixed, fully initialized logical shape. Bulk transfers still touch only active source/destination views. K-tail values are never read: the memory mapper domain is `0:nk`. The explicit sequential K-tile loop preserves accumulation across repeated C tiles; inner foreach schedules remain requests subject to dependence and ownership checks. No `.buffer` safety waiver is introduced.

```python
@kernel
def lab2_outer_gemm(
    a: In[Dram[Fix[True, 24, 8], M, K]],
    b: In[Dram[Fix[True, 24, 8], K, N]],
    c: InOut[Dram[Fix[True, 24, 8], M, N]],
    M: In[Index], N: In[Index], K: In[Index],
    TM: Meta[Size], TN: Meta[Size], TK: Meta[Size], P: Meta[Size]
):
    requires(0 <= M <= 4096)
    requires(0 <= N <= 4096)
    requires(0 <= K <= 4096)
    requires(1 <= TM <= 64)
    requires(1 <= TN <= 64)
    requires(1 <= TK <= 64)
    requires(1 <= P <= TN)
    requires(disjoint(a, c))
    requires(disjoint(b, c))

    @helper(effects="pure")
    def add_fixed(
        left: Fix[True, 24, 8], right: Fix[True, 24, 8]
    ) -> Fix[True, 24, 8]:
        return left + right

    for kk in sequential(0, K, step=TK):
        nk: Index = TK if TK < K - kk else K - kk
        for mm in foreach(0, M, step=TM):
            nm: Index = TM if TM < M - mm else M - mm
            tile_a: Sram[Fix[True, 24, 8], TM, TK]
            load(tile_a[0:nm, 0:nk], a[mm:mm + nm, kk:kk + nk])
            for nn in foreach(0, N, step=TN):
                nn_valid: Index = TN if TN < N - nn else N - nn
                tile_b: Sram[Fix[True, 24, 8], TK, TN]
                tile_c: Sram[Fix[True, 24, 8], TM, TN]
                load(tile_b[0:nk, 0:nn_valid], b[kk:kk + nk, nn:nn + nn_valid])
                for i in foreach(0, TM):
                    for j in foreach(0, TN, par=P):
                        tile_c[i, j] = 0
                load(tile_c[0:nm, 0:nn_valid], c[mm:mm + nm, nn:nn + nn_valid])

                def outer(k: Index) -> Contribution[Sram[Fix[True, 24, 8], TM, TN]]:
                    product: Sram[Fix[True, 24, 8], TM, TN]
                    for i in foreach(0, TM):
                        for j in foreach(0, TN, par=P):
                            if i < nm and j < nn_valid:
                                product[i, j] = tile_a[i, k] * tile_b[k, j]
                            else:
                                product[i, j] = 0
                    return contribute(product)

                mem_fold(tile_c, 0, nk, body=outer, combine=add_fixed)
                store(c[mm:mm + nm, nn:nn + nn_valid], tile_c[0:nm, 0:nn_valid])
```

[designed] This one code block covers runtime shape ports, static SRAM dimensions, nondivisible tails, captured nested helpers, numeric arithmetic, distinct map/cell domains, contribution ownership, explicit seed memory, and transfers. For M=0 or N=0 no output cells exist; for K=0 no tile is read/written and initialized C is retained. Negative dimensions and dimensions above the stated ABI bounds reject before launch. The bounds 4096 and tile limits 64 are explicit example interface choices, not measured hardware limits or course requirements.

[designed] In the checked graph, `outer` captures borrowed tile_a/tile_b, nm and nn_valid, with lifetimes that enclose its invocation. Its local product allocation belongs to each map activation, and `contribute` transfers that root before returning. `mem_fold` snapshots tile_c once; invokes outer(k); snapshots product cells in destination-index order; combines privately; releases the contribution lease; then advances k. It publishes tile_c after successful completion. The mapper may not capture/read/write tile_c, which would bypass the owned recurrence. HLS storage reuse needs a version/credit plan that keeps both input tiles and every admitted live contribution valid. These are the shared numeric/state blueprint rules, not inferred Python lifetime behavior.

## Dot-product GEMM as a distinct designed comparison

[measured] The course host reference uses a per-output K reduction, but supplies no corresponding complete dot-product accelerator body. Source: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:350-355`.

[designed] This complete proposed comparison maps that mathematical decomposition to scalar `reduce`, using typed contribution/combine helpers and fixed-size input tiles. It illustrates what scalar reduction means without pretending that the course provided this accelerator. Unlike the outer-product version, it writes C from scratch and does not read an initial C. Each result is a scalar sum of full-precision-as-declared products in the same fixed format; multiplication normalizes before addition. Modular fixed addition is lawful. Substituting F32 requires ordered fold or an explicit fixed tree, not the same lawful-reduce claim.

```python
@kernel
def dot_product_gemm(
    a: In[Dram[Fix[True, 24, 8], M, K]],
    b: In[Dram[Fix[True, 24, 8], K, N]],
    c: Out[Dram[Fix[True, 24, 8], M, N]],
    M: Meta[Size], N: Meta[Size], K: Meta[Size]
):
    requires(1 <= M <= 16)
    requires(1 <= N <= 16)
    requires(1 <= K <= 16)
    local_a: Sram[Fix[True, 24, 8], M, K]
    local_b: Sram[Fix[True, 24, 8], K, N]
    local_c: Sram[Fix[True, 24, 8], M, N]
    load(local_a, a)
    load(local_b, b)

    @helper(effects="pure")
    def add_fixed(
        left: Fix[True, 24, 8], right: Fix[True, 24, 8]
    ) -> Fix[True, 24, 8]:
        return left + right

    for i in foreach(0, M):
        for j in foreach(0, N):
            def term(k: Index) -> Fix[True, 24, 8]:
                return local_a[i, k] * local_b[k, j]

            total: Fix[True, 24, 8] = reduce(
                0, K, body=term, combine=add_fixed, identity=0
            )
            local_c[i, j] = total
    store(c, local_c)
```

[designed] This comparison intentionally restricts dimensions to positive compile-time sizes ≤16 to expose scalar reduction without introducing another tiling algorithm. It is not a replacement for the preceding runtime-dimension blocked kernel. Multidimensional data is indexed with `mem[i,j]`; only loop-variable destructuring is disallowed. That distinction is part of the source checker, not a limitation to one-dimensional memories.

## Buffering, scheduling, and the compiler path

[measured] The tutorial calls tileC a triple buffer and explains load, compute and store stages. The original SRAM `.buffer` setter sets `isWriteBuffer=true`; its own comment warns that sequential and pipelined results may differ. It is therefore not evidence that adding a source flag proves a dependency safe. Sources: `digital-systems-design-lab@b4896ab:lab2_part1_spatial.md:438-452`; `spatial@c1979ce:src/spatial/lang/SRAM.scala:54-60`.

[designed] Proposed Python preserves a fresh logical tile per controller activation. A named controller/resource plan may request versioned buffering; the lowering must prove ownership, initialization, producer/consumer visibility, and version recycling for the actual task graph. A triple-buffer realization is one candidate, not a magic interpretation of `Sram` or a guarantee that exactly three physical banks suffice. The complete kernel above has well-defined ordered reference meaning without an unsafe buffer waiver. Any pipelined realization must preserve it.

| Source choice | Checked semantic record | Lowering obligation |
|---|---|---|
| `foreach`, `sequential`, `pipe_range` | `control.loop` with Index domain, region captures, ordered token, requested schedule | Build finite hardware counters from proven bounds; preserve zero-trip behavior and active masks |
| `par=P`, `ii=I` | Positive meta request attached to controller/domain | Banking, recurrence/resource limits and realization may prevent requested performance; report requested and achieved schedule separately |
| Scalar reduction | `reduction.scalar`, map region, combine definition/law, identity/seed, optional destination | Preserve arithmetic rounding points, contribution effects, selected topology, disabled/empty behavior, and success-only publication |
| Memory reduction | `reduction.memory`, map domain plus destination coordinate map and ContributionLease | Distinct map and cell parallelism; retain temporary/backing lifetimes and initialized cell images |
| FSM | `control.fsm` and three typed regions | Reference continuations Test→Action→Next→Test; derive finite state encoding; never execute next before suspended action completes |
| Parallel/stream group | `control.task_group` with explicit task domains | Safe fork/join, communication protocol, capacity/alias/race/stop checks; ordered FIFO actions remain ordered |
| Named buffering request | Logical resource identity plus checked implementation storage/version plan | Do not erase semantic init/bounds/lifetime/capacity checks when banking or rotating physical storage |

[designed] Implementation sequence is acquire exact source → parse registered AST forms → prebind meta and shape-port signature dependencies → specialize meta values → type/effect/bounds/init/lease checking → owned semantic graph → exact reference simulation → target resource/schedule plan → implementation dialect/HLS emission → independent C simulation/synthesis/RTL/board evidence. Parsing a decorator never executes it. A valid graph, a Python AST parse, a host arithmetic oracle, and a successful FPGA test are four different evidence levels. L2-14's build commands are instructions for obtaining later evidence, not such evidence themselves.

## Validation obligations and executed checks

[designed] Required compiler conformance cases are:

| Case | Expected check or result |
|---|---|
| Domain `(-5,5,step=1)` | Ten ordered map activations; no conversion of map Index to data unless requested |
| `step=0`, `par=0`, runtime par, two-variable for target | Reject at appropriate domain/meta/grammar boundary |
| Two axes with par and a nondivisible tail | All and only valid coordinates execute; invalid lanes perform no memory access or numeric fault |
| Reg reset 7; reduction of `[1,2]` | Result 3; reset not added. Fold with accumulator seeded 7 returns 10 |
| Empty enabled reduction with identity 0 | Return/publish 0; without identity fault before publication |
| Empty enabled fold | Return existing seed once; disabled fold evaluates no seed or body |
| Empty destination domain, nonempty map | Mapper still invoked once per active map index; zero cell combines/publications; contribution lease released |
| Mapper returns local SRAM without contribution marker, escapes lease, returns wrong shape, or aliases owned destination | Reject with mapper/destination/allocation origins |
| Float add passed to lawful reduce, or arbitrary helper asserted associative by a flag | Reject law request; ordered fold/fixed tree remains expressible |
| Combine reads a Reg, consumes FIFO, performs random draw, or writes storage | Reject combine effect bound; contribution effects follow their declared contract |
| FSM test or next dequeues/writes | Reject phase effect bound; action may contain checked state effects |
| GEMM M=17,N=19,K=18 with 16-sized tiles | Correct tails on all axes; inactive scratchpad cells are zero and never cause off-chip access |
| GEMM K=0 with initialized C | C unchanged for outer-product accumulate interface; no absent product contribution fabricated |
| GEMM C overlaps A or B; strided overlap not proven absent | Reject the disjointness precondition during preparation; allow A/B overlap and empty-region disjointness |
| GEMM negative/runtime oversize shape or zero tile size | Reject launch/specialization requirement before allocation/access |
| Requested par or II lacks a legal physical realization | Capability/schedule result with reasons; no changed reduction order or unproved memory overlap |

[measured] All seven complete Python kernel blocks passed CPython `ast.parse`; every helper argument/result is annotated and every loop has one name binder. All 61 unique pinned citation ranges exist. The nine source-file pin comparisons stated above passed. A direct host calculation of the FSM rules matched all 32 cells of the published gold vector. These checks do not execute the captured kernels. The alternative FSM's piecewise host model matched the explicit 32-cell vector and independent formula `i*(1+i//8)`. The LUT tuple was read from its parsed literal AST and checked against `((1,2,3),(4,5,6),(7,8,9))`; all nine index pairs at five base values (`Int.min`, -7, 0, 11, `Int.max`) matched the independent `wrap32(base+3*i+j+1)` expectation, for 45 LUT checks.

[measured] A separate integer-only design probe compared the blocked outer-product algorithm with an independently structured per-output dot-product reference in 36 cases: dimensions `(0,0,0)`, `(0,3,2)`, `(3,0,2)`, `(2,3,0)`, `(1,1,1)`, `(2,3,5)`, `(17,19,18)`, `(16,16,16)`, `(3,2,1)`, each with tiles `(1,1,1)`, `(2,3,2)`, `(16,16,16)`, `(3,2,5)`. All matched, including initial nonzero C. Both used signed-32 raw wrapping, product `wrap32((a_raw*b_raw)//256)`, and wrapped addition, independently of Python Spatial APIs. Raw test values were `[-2**31,2**31-1,-257,-1,0,1,255,256,769]`; A selected entry `(7*i+3*k)%9`, B `(5*k+2*j+1)%9`, and initial C `(i+3*j+2)%9`. The dot reference computed each output from original A/B/C; the blocked version used padded private tiles and published each K-tile result. This bounded arithmetic/indexing check is not proof of frontend typing, lease/effect checks, HLS scheduling, or general compiler correctness. No Python Spatial compile, simulation timing, synthesis, or board run is claimed.
