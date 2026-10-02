---
type: deep-dive
title: "Convolution windows and the Lab 3 Python mapping"
topic: python-lab3-convolution-window-syntax
scope: python-rewrite
session: 2026-10-01
status: research-conclusion
adoption_status: proposed
implementation_status: not-implemented
source_files:
  - "digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:42-173"
  - "digital-systems-design-lab@b4896ab:lab3_part2_f2_fpga.md:1-106"
  - "digital-systems-design-lab@b4896ab:spatial-cheatsheet.md:40-140"
  - "digital-systems-design-lab@b4896ab:spatial-design-flow.md:271-274"
  - "digital-systems-design-lab@b4896ab:CORDIC.md:17-56"
  - "spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:5-126"
  - "spatial@c1979ce:src/spatial/lang/LineBuffer.scala:16-38"
  - "spatial@c1979ce:src/spatial/lang/RegFile.scala:19-46"
  - "spatial@c1979ce:src/spatial/lang/RegFile.scala:131-205"
  - "spatial@c1979ce:src/spatial/lang/LUT.scala:40-58"
  - "spatial@c1979ce:emul/src/emul/LineBuffer.scala:14-59"
  - "spatial@c1979ce:emul/src/emul/ShiftableMemory.scala:15-31"
  - "spatial@c1979ce:test/spatial/tests/feature/memories/linebuf/LineBuffers.scala:22-128"
feeds_spec:
  - "[[10 - Python Language Contract]]"
  - "[[20 - Python Numeric Contract]]"
  - "[[30 - Python State and Protocol Contract]]"
  - "[[10 - Source Checker and IR Blueprint]]"
  - "[[20 - Numeric Engine Blueprint]]"
  - "[[30 - State Simulator and HLS Blueprint]]"
verified:
  - "2026-10-01"
---

## Result and evidence boundary

The useful Python translation is a typed row-streaming accelerator: publish one image row into a newest-first LineBuffer, shift one column into three RegFile rows, compute two nested 3×3 reductions, then store a completed output row. Python spelling alone does not specify publication, reset, arithmetic, or controller order. This note specifies those boundaries and the concrete registrations the existing blueprints still need. Everything below marked **proposed** is an unimplemented design; no Python Spatial compiler, simulator, HLS flow, RTL simulation, or board test was run.

The source pin was rechecked against the public CS217 checkout on 2026-10-01; the nine source files cited here were byte-identical to the earlier inspected local baseline. The public tutorial and the public Spatial test are separate evidence. The tutorial contains a `Your code here` hole; the public compiler repository contains completed nested reductions. No local student solution is used as a source. The representative complete kernel below translates the **public compiler test's concrete Int/16×16 invocation**, with the strict-initialization repair made explicit. It does not claim to recover the unavailable classroom skeleton exactly. Sources: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:139-173`; `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:53-85`.

| Source identity | Pinned public location | Role and limit |
|---|---|---|
| Lab guide, `b4896abffd19bcc3f319a49d7a919e1cf70d5221` | [Lab 3 Spatial](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab3_part1_spatial.md#L42-L173) | Padded image, rotated filters, load/shift/compute/store topology; arithmetic exercise remains blank |
| Lab HLS guide, same pin | [Lab 3 HLS](https://github.com/kelayamatoz/Digital-Systems-Design-Lab/blob/b4896abffd19bcc3f319a49d7a919e1cf70d5221/lab3_part2_f2_fpga.md#L1-L106) | Separate GEMM/vector-add exercise and staged validation, not another Spatial convolution implementation |
| Spatial, `c1979ceb715cec239b6de36408a365aba5b7c709` | [Public completed Lab3 test](https://github.com/stanford-ppl/spatial/blob/c1979ceb715cec239b6de36408a365aba5b7c709/test/spatial/tests/ee109/Lab3.scala#L5-L126) | Complete older convolution fixture and host checksum |
| Spatial, same pin | [LineBuffer API](https://github.com/stanford-ppl/spatial/blob/c1979ceb715cec239b6de36408a365aba5b7c709/src/spatial/lang/LineBuffer.scala#L16-L38), [RegFile API](https://github.com/stanford-ppl/spatial/blob/c1979ceb715cec239b6de36408a365aba5b7c709/src/spatial/lang/RegFile.scala#L131-L205) | Source semantics and syntax, with simulator/RTL discrepancies kept separate |
| Existing Python proposal | [[10 - Python Language Contract]], [[10 - Source Checker and IR Blueprint]], [[20 - Numeric Engine Blueprint]], [[30 - State Simulator and HLS Blueprint]], [[PY-R008 - Advanced State and Communication Protocols]] | Authority for the proposed capture/type/effect/lifetime model; this note proposes missing surface instances rather than silently redefining them |

## L3 inventory: original spelling, proposed meaning, compiler obligation

IDs are stable acceptance/migration identifiers. “Host” means ordinary Python outside the captured source unit; “meta” means immutable compiler input; “runtime” means typed accelerator values/effects. The proposed IR names refer to the closed operation families in [[10 - Source Checker and IR Blueprint]]. A row's source citation establishes the original construct, not implementation support for its Python mapping.

| ID | Actual source construct and evidence | Concrete proposed Python mapping | Type, effect, or rejection obligation |
|---|---|---|---|
| L3-01 | `convolve[T:Num](image: Matrix[T])`, `main`, `Accel`; `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:11-25,78-91` | Host creates typed buffers and specializes a captured `@kernel`; algorithm body lives in a dedicated source unit | Capture reads source, never calls the function or evaluates decorators/annotations; host matrix is not a kernel Python list |
| L3-02 | `Kh=3`, `Kw=3`, `Cmax=16`, `B=16`; same source `:7-18` | Immutable meta extents; no runtime allocation from an unconstrained integer | `B` is unused in this public fixture and has no semantic operation; positive storage extents and finite target bounds check independently |
| L3-03 | Tutorial `type T=Int`, image/padding dimensions; `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:83-106` | `Int` is signed wrapping 32-bit data; image/pad dimensions are host/meta integers | Literal coefficients are contextual Int; a host `int` used as geometry is not automatically Int data |
| L3-04 | Generic `T:Num`, coefficients `1.to[T]`; `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:11,28-33` | A later generic helper binds a registered immutable numeric descriptor and checks each arithmetic operation and reduction policy | Do not claim arbitrary Python classes satisfy `Num`; floating/fractional/checked types require their own reduction topology/law |
| L3-05 | `ArgIn[Int]`, `setArg(R,image.rows)`/C; same source `:14-17` | Runtime variant uses `rows:In[Index]`, `cols:In[Index]` plus declared capacities, or retains `In[Int]` with exact integral projection in index slots | The complete listing uses explicit meta specialization for the concrete fixture; it does not pretend those parameters remain runtime ingress |
| L3-06 | `DRAM[T](R,C)`, `setMem`, `getMatrix`; same source `:20-23,78` | `src:In[Dram[Int,ROWS,COLS]]`, `dst:Out[...]`; host typed-buffer initialization/readback | Snapshot/alias validation at launch; output is incomplete on fault; distinct formal names alone do not prove no alias |
| L3-07 | Padded host matrix `(0::R,0::C){...if...}`; guide `:100-111` | Ordinary host comprehensions/loops prepare zeros and interior pixels, then typed ingress validates them | Host comprehension is legal host work, not permission for comprehensions inside captured kernels |
| L3-08 | `LineBuffer[T](Kh,C)`; guide `:114-119`; `LineBuffer[T](Kh,Cmax)` in public test `:26` | `lb:LineBuffer[Int,3,COLS]`; 1-row staging for dense row load | Allocation has fresh uninitialized history; ordered load publishes a new logical version; row 0 is newest |
| L3-09 | `LUT[T](3,3)(...)`; guide `:121-130`, public test `:28-33` | `kh:Lut[Int,3,3]=lut(((...),(...),(...)))`, likewise kv | Proposed initializer registration below; exactly nine contextual typed constants; read-only allocation; mutation rejects |
| L3-10 | `RegFile[T](Kh,Kw)`; guide `:118` | `sr:RegFile[Int,3,3]` with typed-zero reset image | Invocation-local object, retained across pixels until explicit row reset; not a fresh object per pixel |
| L3-11 | `lineOut=SRAM[T](C)`; guide `:119` | `line_out:Sram[Int,COLS]` | Initially uninitialized; each column writes exactly once before the row store, including warmup columns |
| L3-12 | Outer `Foreach(0 until R)`; guide `:140` | `for r in foreach(0,ROWS)` | `control.loop`, Index binder; LineBuffer and output-row dependencies survive any pipeline schedule |
| L3-13 | `lb load img(r,0::C par lb_par)`; public test `:38-39`; guide `:141` | `load(lb,src[r,0:COLS],par=8)` for the public test; omit/1 for guide | Dropped row axis leaves rank-1 view; destination-first call; load completion includes publication; par is a schedule request |
| L3-14 | `Sequential.Foreach(0 until C)`; guide `:143` | `for c in sequential(0,COLS)` | Pixel recurrence must finish shift→read→compute before next pixel shift; Index loop arithmetic is exact |
| L3-15 | `Pipe{sr.reset(c==0)}`; guide `:144` | `with pipe(): sr.reset(enable=(c==0))` | Registered ordered reset; false enable commits no reset; true initializes all nine cells before shift |
| L3-16 | `Foreach(0 until Kh par Kh){i=>sr(i,*) <<= lb(i,c)}`; guide `:146` | `for i in foreach(0,3,par=3): sr[i,:].shift(sample)` | Row view retains axis 1 and backing identity; three distinct rows can commute; each shift snapshots old row |
| L3-17 | Pixel-local `Reg[T](0)` horz/vert; public test `:53-54` | `horz:Reg[Int]=reg(reset=0)`, `vert:Reg[Int]=reg(reset=0)` inside pixel body | Fresh pixel-activation generation/reset; write `.value` after successful reduction; no Python local mutation masquerading as recurrence |
| L3-18 | Inner `Reduce(0.to[T])(0 until Kw par Kw)`; public test `:56-68` | Typed nested helper `(j:Index)->Int`, `reduce(0,3,identity=0,combine="add",body=...,par=3)` | Three typed multiply contributions, exact zero identity; lawful wrapping-Int addition; contribution reads ordered |
| L3-19 | Outer `Reduce(horz)`/`Reduce(vert)`; public test `:56-68` | Inner-row helper `(i:Index)->Int`, outer reduce, then `horz.value=...`/vert | `reduction.scalar` result publication then Reg write; preserve two levels rather than assuming flattened floating reassociation |
| L3-20 | `mux(r<2 || c<2,0.to[T],abs(horz.value)+abs(vert.value))`; public test `:72` | Runtime `if r<2 or c<2: ... else: ...` | Bool short circuit and selected regions; full reductions already occurred, so this branch does not erase prior faults |
| L3-21 | `imgOut(r,0::C par 16) store lineOut`; guide `:154`, public test `:74` | `store(dst[r,0:COLS],line_out,par=16)` | Destination-first `transfer.copy`, per-axis view bounds, complete initialized row, no physical padding access |
| L3-22 | Nested `println` of shift values and gradients; public test `:45-48,70`; guide `:226-229` | `debug_print` records typed events; hardware debug uses a declared trace/DRAM adapter | Public guide explicitly asks VCS debugging through DRAM/host; no universal device Python `print` guarantee |
| L3-23 | Host gold, `map`, `zip`, `reduce`, checksum, `assert`; public test `:104-126` | Ordinary host reference plus elementwise typed comparison | Preserve checksum as historical test, add full-matrix comparison because equal sums can hide errors; host `assert` is not accelerator control |
| L3-24 | Helper/local/source condition boundaries: host image `if`, runtime output `mux`; public test `:72,85` | Host `if` executes immediately; captured `if` becomes regions; optional explicit meta `static` specializes branches | No implicit host truth test of DSL values, `int(DSLValue)`, arbitrary closure lookup, or runtime recursion |
| L3-25 | One row buffer, then two independent row buffers; `spatial@c1979ce:test/spatial/tests/feature/memories/linebuf/LineBuffers.scala:22-51` | Separate `LineBuffer` identities and publications; pointwise sum of matching versions | Supplemental API coverage, not a second Lab3 algorithm; commented `Parallel` is not evidence of active task parallelism |
| L3-26 | `LineBuffer.strided(3,24,2)` and `enqAt(r,...)`; same source `:53-66` | Explicit two-row begin/fill/publish frame; data expression uses `embed(Int,index_expr)` | Per-staging-row cursor and active-lane compaction; row 1 arrives after row 0 and becomes newest at publication |
| L3-27 | Strided two-row dense load, read seven rows/25 columns from 8×26 window; same source `:69-90,122-128` | Rank-2 row-batch view into a frame; slice of published rows 1..7 and columns 0..24 | Retained/dropped axes must remain explicit; this is a supplemental window test, not permission to tile Lab3 columns without halos |
| L3-28 | GEMM 4×4 with 2×2 tiles and vector-add HLS unroll factors; `digital-systems-design-lab@b4896ab:lab3_part2_f2_fpga.md:13-35,94-106` | Separate tiled-reduction/vector mapping and target schedule requests | Source par does not prove bandwidth benefit; C++ test, RTL simulation, and board execution are distinct evidence stages |
| L3-29 | Approximate `abs(h)+abs(v)` versus mentioned sqrt; guide `:56`; supplemental CORDIC link in design flow `:271-274` | Keep the original L1 expression; an optional true magnitude uses explicitly typed math operations and a declared profile | No silent sqrt substitution, host `math.sqrt`, or adoption of the linked pseudocode as a numerical oracle |

## Which convolution is being translated?

The guide generates a padded input with `R=img_r+4`, `C=img_c+4`, interior value `(i-pad_r+1)*16`, and assumes padded dimensions divisible by 16. It allocates the LineBuffer/output row to that C, and stores coefficient tables with signs opposite to the older public test. The public test fixes `Cmax=16`, supplies R=C=16, uses `border=3` with strict inequalities, and completes the two reductions. Those differences are source facts, not corrections to one source by the other. Sources: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:83-130`; `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:7-36,81-91`.

For either table pair, the streaming window after row r and column c has the coordinate meaning

$$W[i,j]=I[r-i,c-j],\qquad 0\le i,j<3,$$

once the indicated history exists. New data enters RegFile column 0, and the newest LineBuffer row is row 0. Consequently both row and column coordinates run backwards relative to an ordinary oldest/top-left-first image patch. This equation is a source-derived consequence of the explicit newest-row assertion and shift implementation, not an assumption based on the `<<=` arrow. Sources: `spatial@c1979ce:test/spatial/tests/feature/memories/linebuf/LineBuffers.scala:24-32`; `spatial@c1979ce:emul/src/emul/ShiftableMemory.scala:15-25`. The tutorial explicitly explains its 180-degree table rotation at `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:159-169`.

The two filters are combined as `abs(h)+abs(v)`. Negating both coefficient tables preserves that final expression under the proposed wrapping Int semantics, including the minimum signed value's wrapping abs behavior, but it changes signed gradient/debug observations. Therefore output agreement alone cannot establish table orientation. A migration test must inspect at least one asymmetric 3×3 window and signed h/v, in addition to the final magnitude. This is a proposed test requirement derived from the two cited table versions.

### Warmup is a real semantic repair

The original loop reads `lb(i,c)` for all i before its later output mux suppresses the first two rows/columns. The guide describes uninitialized shift-register values and relies on muxing those outputs to zero. In the proposed state model, an **active uninitialized read faults when it executes**. A subsequent zero output cannot undo it. Source: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:143-152,168-169`; proposed authority: [[30 - Python State and Protocol Contract]] and [[PY-R008 - Advanced State and Communication Protocols]].

The complete listing below reads `lb[i,c]` only when `i<=r`; otherwise it shifts an explicit zero. RegFile construction/reset initializes all cells to zero. At every unmasked output (`r>=2 and c>=2`), all nine values are actual input history. Thus the repair preserves the defined output matrix while defining previously invalid warmup/debug values. It is a deliberate migration difference, not bit-for-bit agreement with unspecified simulator sentinels.

Do not replace the guarded expression with an eager `select(i<=r,lb[i,c],0)`: its read has already occurred. A source conditional expression creates a lazy region. An explicit full history-fill constructor is another possible policy, but it is not the default adopted by R008 and is unnecessary for this example.

## Complete proposed captured kernel

**Design listing, not executable package code.** A dedicated source file is read as data through the acquisition contract. `ROWS` and `COLS` are immutable meta bindings; bind both to 16 for the exact concrete public fixture. Capacity specialization is deliberate: this listing does not preserve the original helper's runtime R/C or generic T interface. Those extensions are specified separately below. The initialized-LUT helper, transfer `par` keyword and RegFile shift/reset method instances are concrete proposed registrations in the next section; their appearance here is not an existing-API claim.

```python
from spatial import (
    kernel, Meta, Size, Int, Index, In, Out, Dram,
    LineBuffer, RegFile, Lut, Sram, Reg, reg, lut,
    requires, disjoint, foreach, sequential, pipe, load, store,
    reduce, debug_print,
)
from spatial.math import abs

@kernel
def lab3_public_int(
    ROWS: Meta[Size],
    COLS: Meta[Size],
    src: In[Dram[Int, ROWS, COLS]],
    dst: Out[Dram[Int, ROWS, COLS]],
):
    requires(ROWS > 0)
    requires(0 < COLS <= 16)
    requires(disjoint(src, dst))

    lb: LineBuffer[Int, 3, COLS]
    sr: RegFile[Int, 3, 3]
    line_out: Sram[Int, COLS]
    kh: Lut[Int, 3, 3] = lut((
        (1, 0, -1),
        (2, 0, -2),
        (1, 0, -1),
    ))
    kv: Lut[Int, 3, 3] = lut((
        (1, 2, 1),
        (0, 0, 0),
        (-1, -2, -1),
    ))

    for r in foreach(0, ROWS):
        load(lb, src[r, 0:COLS], par=8)
        for c in sequential(0, COLS):
            with pipe():
                sr.reset(enable=(c == 0))

            for i in foreach(0, 3, par=3):
                sample: Int = lb[i, c] if i <= r else 0
                sr[i, :].shift(sample)

            for i in foreach(0, 3):
                for j in foreach(0, 3):
                    debug_print("sr({0:int}, {1:int}) = {2:int}",
                                i, j, sr[i, j])

            horz: Reg[Int] = reg(reset=0)
            vert: Reg[Int] = reg(reset=0)

            def horizontal_row(i: Index) -> Int:
                def horizontal_term(j: Index) -> Int:
                    return sr[i, j] * kh[i, j]
                return reduce(0, 3, identity=0, combine="add",
                              body=horizontal_term, par=3)

            def vertical_row(i: Index) -> Int:
                def vertical_term(j: Index) -> Int:
                    return sr[i, j] * kv[i, j]
                return reduce(0, 3, identity=0, combine="add",
                              body=vertical_term, par=3)

            horz.value = reduce(0, 3, identity=0, combine="add",
                                body=horizontal_row, par=3)
            vert.value = reduce(0, 3, identity=0, combine="add",
                                body=vertical_row, par=3)
            debug_print("{0:int},{1:int} Horiz = {2:int}, Vert = {3:int}",
                        r, c, horz.value, vert.value)

            if r < 2 or c < 2:
                line_out[c] = 0
            else:
                line_out[c] = abs(horz.value) + abs(vert.value)
        store(dst[r, 0:COLS], line_out, par=16)
```

The complete arithmetic/topology comes from `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:25-75`. The proposed diagnostic operations record the selected integer information in the proposed ordered iteration trace. Byte-identical legacy logs and identical legacy backend event timing are not claimed; the newly defined warmup values also differ from invalid sentinels. `debug_print` requires a target trace capability; a no-debug variant explicitly removes observation operations before checking. No hidden host `print` is called by the captured body.

All loop binders are Index. Comparisons and domain/slice expressions use exact structural arithmetic. Image/filter/Reg values are Int. No Index is stored as pixel data here; the synthetic host prepares those integers. If the synthetic expression `(r-pad_r+1)*16` moves into the kernel, use `embed(Int,(r-pad_r+1)*16,overflow="checked")` explicitly, or choose `wrap` deliberately. Do not use `Int(r)` or Python `int(r)` as an unspecified conversion. [[10 - Source Checker and IR Blueprint]] registers `num.embed_index` only for integral fixed targets and exact integral projection into index slots.

Every Int multiply/add/abs in the listing normalizes according to the numeric contract. The accumulator does not secretly widen. Wrapping addition has a registered associativity/identity law, so parallel reduction is legal; reads and possible faults still preserve contribution order. Substituting F32 or checked/saturating arithmetic is not a token-level generic rewrite: choose an explicit ordered fold or recorded fixed tree unless the admitted operation/domain has a checker-owned law. Sources for the proposed arithmetic: [[20 - Python Numeric Contract]], [[20 - Numeric Engine Blueprint]], [[PY-R002 - Numeric and Reduction Semantics]].

### Host workflow, completely separated from capture

The host may perform the following ordinary Python preparation, matching the public fixture's image generator. This small block is executable Python data preparation, but it is not a launch script and does not claim an implemented Spatial host library.

```python
rows = cols = 16
border = 3
image = [
    [i * 16 if (j > border and j < cols - border
               and i > border and i < cols - border) else 0
     for j in range(cols)]
    for i in range(rows)
]
meta_bindings = {"ROWS": rows, "COLS": cols}
```

The host then supplies the dedicated kernel source and closed meta bindings to capture/specialization, resolves declarative imports, checks the program, creates an Int32 16×16 backing initialized from `image`, and provides a writable output backing. Input/output alias identity, element encoding, shape/strides and ownership are validated at invocation. `requires(disjoint(src,dst))` matches the original separate DRAM allocations: overlapping shifted host views could otherwise overwrite rows before their later input load. The registered predicate uses backing/address domains and view intersections; preparation rejects unresolved disjointness rather than assuming it from In/Out names. After successful reference/target completion, read back all 256 cells and compare with an independently structured typed reference. Capture/check/simulate/compile API call spellings belong to [[40 - Package and Conformance Blueprint]]; inventing `compile_and_run(...)` here would conceal that boundary.

The original host generator uses `i < C-border` as its second row test, even though rows are denoted R; preserve that exact expression for this square 16×16 fixture. A general rectangular generator should use the row extent, documented as a correction rather than quoted as the original. The original host `kh`/`kv` List declarations are unused by the generated gold expression and do not become accelerator memories. The original checksum masks the first two output rows and compares sums; retain it as historical evidence but also compare elements. Sources: `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:81-89,104-126`.

## Proposed exact registrations needed for this mapping

These entries refine existing closed families. The shared registry integration lives in [[60 - Course Syntax and Compiler Trace]]; its complete signatures govern calls, and this note supplies the Lab3 instances and window contracts. They are proposals for the owners of [[10 - Source Checker and IR Blueprint]] and [[30 - State Simulator and HLS Blueprint]]; this note does not claim that generic family-name lists already define the following complete signatures. Each entry needs a versioned SourceRegistration/TransitionSpec and matching builder operation before acceptance.

| Registration proposal | Signature and exact rule | Normalized operation |
|---|---|---|
| `source.line_buffer_init.v1` | Contextual `line_buffer(*,width:Index) -> initializer[LineBuffer[T,H,MAX_C]]`; annotation H/MAX_C are positive meta extents. Capture an immutable invocation Index width once; require `0 < width <= MAX_C` before allocation. No implicit numeric cast, width mutation, history fill or publication. Declaration without initializer uses logical width MAX_C | `storage.allocate(kind=LineBuffer,logical_shape=(H,width),max_shape=(H,MAX_C),init=none,version=0)` with captured shape operand, generation/owner and token; history capacity H×MAX_C, separate staging/snapshot cost |
| `source.lut_init.v1` | Contextual `lut(values:nested_literal_tuple) -> initializer[Lut[T,*shape]]`; no runtime inputs. Nesting depth equals rank, each tuple length equals the corresponding extent, and exactly product(shape) leaves appear in row-major last-axis-fast order. Each leaf is a captured exact numeric literal tree accepted in T context. No ragged tuple, runtime read, callback, host list conversion or inferred reshape | `storage.allocate(kind=Lut,full_image=typed_bits,capability=Read)`; writes/reset-as-mutation reject. Aligns source LUT constructor and mutation rejection at `spatial@c1979ce:src/spatial/lang/LUT.scala:40-58` |
| `source.regfile_reset.v1` | `rf.reset(*,enable:Bool=true)->Unit`, evaluated receiver then enable once. True replaces the complete logical RegFile with its declared image; false does no bounds/init/write action. Image belongs to construction, not to reset's caller | `storage.reset`, Ordered token, write domain entire RF; preserves generation and owner |
| `source.regfile_shift_scalar.v1` | `row_view.shift(data:T,*,enable:Bool=true)->Unit`. Receiver must identify one full contiguous axis of a RegFile, other coordinates captured Index; receiver→data→enable evaluation once. False gates transition checks/commit but cannot erase already evaluated operand effects; true bounds-checks all fixed axes and requires read/write capability | `storage.shift(profile=regfile.chronological.v1)`, row snapshot, atomic publish, token |
| `source.regfile_shift_vec.v1` | Same receiver, `data:Vec[N,T]`, optional `mask:Vec[N,Bool]` all-true default. Active lanes are chronological oldest-to-newest in ascending lane order; k active values requires k<=axis length. Active count 0 is no-op; oversized batch faults before mutation | Same transition, vector/mask operands. `new[j]=active[k-1-j]` for j<k; `new[j]=old[j-k]` otherwise. Whole old slice captured before writes |
| `source.load_line_row.v1` | `load(dst:LineBuffer[T,H,MAX_C],src:ReadView[T,W],*,par:Meta[Size]=1)->Unit`, where W is the receiver's captured logical width, equal to MAX_C only for a declaration without a width initializer. H,MAX_C,W and par positive; exact element type/row width. A rank-1 source is one staging row. Ordered exclusive receiver; preflight source bounds/init/generation, snapshot row, begin/fill/publish, complete | `transfer.copy` with `endpoint=line_frame`, then specified LineBuffer state transitions; no separate call-site publish required |
| `source.load_line_rows.v1` | Rank-2 overload `src:ReadView[T,S,W]`, S>0 bound to frame row count. Default S=1 for rank-1; S may exceed H. Source row order is chronological; after commit published row 0 is source row S-1 | Same transfer/publication profile, exact S-row staging; newest H rows survive |
| `source.store_dense_schedule.v1` | Existing destination-first `store(dst:WriteView[T,*shape],src:ReadStorageOrView[T,*shape],*,par:Meta[Size]=1)->Unit`. Shapes/types match exactly; no implicit element cast. par affects candidate schedule, not snapshot or write order | `transfer.copy` with explicit snapshot/alias/completion policy and soft schedule request |
| `source.reduce_lawful_schedule.v1` | Shared `reduce(start,end,*,step=1,par=1,body,combine,identity=None,accumulator=None,schedule="foreach",ii=None)`. This listing instantiates Index start/end/step, positive meta par, body `Def[(Index)->Int]`, identity Int zero, no destination accumulator and no II request. step is nonzero; schedule is registered controller intent; `"add"` resolves under exact T to a numeric ID with a lawful descriptor | `reduction.scalar(policy=lawful,identity=typed_zero)`; identity used on empty domain, default enabled; no destination argument required in this listing |

The scalar shift is **not** Python augmented left-shift assignment: it is a state transition. For old row `[10,20,30]`, `.shift(40)` produces `[40,10,20]`. Vector input `[40,50]` produces `[50,40,10]`. Repeating writes from low to high without a snapshot would yield `[40,40,40]`, violating the contract. The original scalar/vector APIs and emulator establish this direction: `spatial@c1979ce:src/spatial/lang/RegFile.scala:131-137,172-175,203-205`; `spatial@c1979ce:emul/src/emul/ShiftableMemory.scala:15-25`. Slice creation borrows the existing RF; it never allocates a separate row copy.

RegFile default initialization is an intentional Python policy. The original API promises initial values or zeros, while the Scalagen allocation path without an image fills invalid values and records `saveInit=false`; the shiftable emulator resets such a memory to invalid. RTL's RegInit path instead uses zero when inits are absent. Do not assert identical source/simulator/hardware reset defaults. Sources: `spatial@c1979ce:src/spatial/lang/RegFile.scala:27-31`; `spatial@c1979ce:src/spatial/codegen/scalagen/ScalaGenMemories.scala:144-158`; `spatial@c1979ce:emul/src/emul/ShiftableMemory.scala:27-31`; `spatial@c1979ce:fringe/src/fringe/templates/memory/MemPrimitives.scala:561-564`.

### Constructor state is resource-specific

`Sram[T,*shape]` begins with no initialized cells. `RegFile[T,*shape]` begins with every cell initialized to its full reset image (typed zero by default), and `.reset` restores that same image. `Lut[T,*shape]=lut(nested_tuple)` begins completely initialized and read-only. `LineBuffer[T,H,W]` begins with version zero and no valid published history cells; a first publication initializes only its newly inserted rows. These are explicit differences: declaration syntax does not imply a universal uninitialized-memory rule. They preserve the existing R008 construction/reset policy.

### Manual/strided frames require additional registrations

The supplemental `LineBuffers.scala` tests justify covering manual enqueue and two-row loads; the single-row Lab3 kernel does not require user-visible frame handles. Proposed manual form uses a linear `Frame[LineBufferSchema]` action result: `frame=lb.begin_frame(rows=S)`, `frame.fill(row,data,mask=...)`, `frame.publish()`. The exact `Frame` descriptor and these method names are **new registration proposals**, absent from the current source spelling list. A Frame is generation/owner/base-version-bound; no aggregate packing, arbitrary copying, nested open frame on the same exclusive receiver, or escape past invocation is permitted. It is not an existing publication Lease.

`fill(row:Index,data:T|Vec[N,T],mask)` writes accepted lanes at that staging row's cursor in ascending active-lane order. It validates row, capacity and initialized input values before committing the batch. Each row has its own cursor. Default publish requires exactly W accepted cells in every row. An explicit partial-fill image may fill missing cells; an undeclared partial row faults and publishes nothing. No cursor wraps modulo width. These are the concrete surface consequences of the semantics already proposed in [[PY-R008 - Advanced State and Communication Protocols]].

For old window P and chronological incoming rows F0..F(S-1), publication is

$$P' = \operatorname{take}_{H}([F_{S-1},\ldots,F_0] + P).$$

It increments the version exactly once and leaves old uninitialized cells invalid. A failed preflight/full-frame check changes no published version. Dense array-backed row load can preflight/snapshot before exposing staging effects; a manual frame may already contain accepted cells when a later fill faults, and cleanup discards that unpublished frame. Communicating publication additionally needs credit slots, acquire-next-version/read/release operations and immutable leases; they cannot be replaced by “read latest” under a concurrent producer. The ordered Lab3 instance requires no task group or lease syntax.

## Typed compiler path and lifetime proof for one pixel

1. **Acquire and bind.** Read source/tokens/origins, resolve only registered imports and markers, bind ROWS/COLS before dependent port shapes, validate immutable meta values and `requires`. No Python `exec`, annotation call, decorator invocation, dynamic method search, host float arithmetic or recursive host callback occurs in the compiler. A host generator may independently generate a finite source graph; this example needs none. Authority: [[10 - Python Language Contract]] and [[10 - Source Checker and IR Blueprint]].
2. **Allocate enclosing state.** `storage.allocate` creates LineBuffer, RegFile, row SRAM and read-only LUT resources owned by this kernel invocation. Each records logical identity, generation, shape, type, reset/init bitmap and capabilities. The enclosing allocations survive row/pixel iterations. Physical reuse cannot reinterpret this as fresh per-pixel memory.
3. **Form the row view and publish.** `storage.view(src,r,0:COLS)` drops axis 0 and retains axis 1. The checker keeps logical row and column bounds separately before flattening. `transfer.copy` preflights/snapshots, fills staging, and commits a single published window version. Its token precedes all reads for this row. A row store must finish before the next reuse of `line_out`, unless an equivalent versioned schedule proves preservation.
4. **Enter pixel and reset.** `control.loop(mode=Sequential)` gives c:Index. The reset region consumes the current token; when c=0, all RF cells become initialized typed zero. `control.if` for the warmup sample executes exactly one branch. Reads only use initialized published rows. The three row-shift operations have disjoint write domains but their completion precedes all convolution/debug reads.
5. **Capture helper environments.** The checker closure-converts `horizontal_row`/`vertical_row` with borrowed sr/kh/kv, and their term helpers additionally capture i:Index. Calls are acyclic and use typed DefinitionRefs. No mutable Python closure remains. Each helper's possible bounds/init faults and formal read regions stay in its effect summary; unchecked alias or lifetime assumptions cannot be hidden inside a helper.
6. **Reduce and publish.** Each inner reduction reads three initialized cells, computes Int multiplications, combines according to the lawful descriptor, and yields one Int. The outer reduction combines the three row results and only then publishes its result to the Reg. The second reduction follows in source order. Pixel-local Reg resources receive fresh activation generations each pixel; their values do not carry to the next pixel.
7. **Mask output and finish.** Runtime Bool regions select the output assignment. At least one assignment initializes exactly `line_out[c]`; zero warmup writes count as initialization. After all COLS iterations, the row store reads a fully initialized rank-1 array and writes the matching output view. On a fault, preserve earlier committed rows/effects and mark invocation outputs incomplete. Do not quietly export a successful partially filled matrix.

The concrete typed nodes are `control.loop`, `control.region`, `control.if`, `storage.allocate/view/read/write/reset/shift`, `transfer.copy`, LineBuffer `state.action`, `numeric.eval(fix.mul/add/abs)`, `reduction.scalar`, and debug events. They already fit the closed semantic IR families; missing work is registration/profile instantiation and implementation, not a special `Lab3Convolution` whole-program recognizer. The continuations, captured request operands, state transitions and cleanup procedures are owned by [[30 - State Simulator and HLS Blueprint]].

No overlapping controller is authorized merely by `par=3` or `par=16`. Those requests do not create communicating tasks, alter semantic capacity, reorder a reset after its reads, or let the next pixel overwrite the current window. HLS planning may bank/replicate LUTs and RF rows, create a line-ring layout and burst transfers, but must preserve logical initialization, complete row publication, typed arithmetic and the source event projection. A portable sequential realization is meaningful before an optimized pipelined realization is proven. Target resource/II/clock and actual bus transaction width remain separate validation results.

## Extensions, alternatives, and source contradictions

### Runtime-width kernel: bounded capacity, invocation-sized rows

The runtime-width source form is now specified; it is no longer an unresolved source-design gap. It remains proposed and unimplemented. It fits the existing descriptor algebra's separation of `logical_shape` from static capacity in [[10 - Source Checker and IR Blueprint]]. The source motivation is the original `ArgIn` R/C and Cmax allocation at `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:9-21,26-39,74`.

Start with the complete `lab3_public_int` body above and apply **all** replacements below. This is a precise source variant, not a call that executes the captured function from ordinary Python. Replace its entire signature and requirements with:

```python
@kernel
def lab3_runtime_int(
    MAX_C: Meta[Size],
    R: In[Index],
    C: In[Index],
    src: In[Dram[Int, R, C]],
    dst: Out[Dram[Int, R, C]],
):
    requires(0 < MAX_C <= 2147483647)
    requires(0 < R <= 2147483647)
    requires(0 < C <= MAX_C)
    requires(disjoint(src, dst))
```

The Index ports carry exact signed coordinates. The explicit 32-bit-positive bounds keep this variant within the original integral-ArgIn extent range and let a target derive finite counter/address widths; they do not promise the required buffers fit any device. Prebind all signature names before resolving R/C-dependent DRAM annotations, validate host buffer shapes against the supplied runtime extents, and retain the accepted ranges in the invocation/target contract. MAX_C is specialization data; R/C are values supplied for each invocation and do not enter specialization identity as accidental constants.

| Exact location in the complete listing | Replace with |
|---|---|
| Imported names from `spatial` | Add `line_buffer`; keep every other imported operation |
| `lb: LineBuffer[Int, 3, COLS]` | `lb: LineBuffer[Int, 3, MAX_C] = line_buffer(width=C)` |
| `line_out: Sram[Int, COLS]` | `line_out: Sram[Int, MAX_C]` |
| `for r in foreach(0, ROWS):` | `for r in foreach(0, R):` |
| `load(lb, src[r, 0:COLS], par=8)` | `load(lb, src[r, 0:C], par=8)` |
| `for c in sequential(0, COLS):` | `for c in sequential(0, C):` |
| `store(dst[r, 0:COLS], line_out, par=16)` | `store(dst[r, 0:C], line_out[0:C], par=16)` |

Keep the two literal LUTs, RegFile declaration, c==0 reset, guarded history sample, row shifts, typed helpers, nested Int reductions, debug observations, and output mask exactly as shown. No ROWS/COLS name remains after the replacements. For the original concrete case, specialize MAX_C=16 and invoke R=C=16; invoke another legal R/C without reacquiring or specializing the source. These replacements also define narrow rows such as C=5 under MAX_C=16: a frame completes after five cells, line_out[0:5] is initialized/stored, and no sixth input/output cell is touched.

**Initializer schema and immutability.** `LineBuffer[T,H,MAX_C] = line_buffer(width=C)` uses H and MAX_C as capacity bounds and captures C from immutable invocation ingress. It constructs a handle with `logical_shape=(H,C)`, `max_shape=(H,MAX_C)`, element descriptor T, owner/generation, version zero and no valid history cells. The width is fixed for that handle generation: no setter, mid-frame resize, assignment to C, or reset that reinterprets old cells under another width. A subsequent invocation allocates a fresh generation and may supply a different legal C. A general checked initializer may accept a total-pure structural Index expression derived from immutable invocation ports/meta constants; mutable Reg reads, queue consumes, effectful calls and undeclared host data are not shape operands.

**Loads, reads and publication.** A rank-one load must have exactly C logical elements of exactly T. It preflights and snapshots those C cells, begins one staging row, fills its C positions, then publishes through the same R008 protocol. Manual fill/full-row checks likewise use C, not MAX_C. Reads require both `0<=history_row<H` and `0<=column<C`, plus that cell's published-version initialization. No transfer, full-row test, read or publication acquires authority over padding `[C,MAX_C)`. Loading a C-element source into an uninitialized declaration that still has logical width MAX_C remains a shape error; the initializer is what supplies the narrower logical shape.

**Capacity and row scratch.** The history capacity is H×MAX_C elements; separate staging rows, snapshots, initialization maps and live version storage must still be counted by [[30 - State Simulator and HLS Blueprint]]. This is not a promise that the entire physical implementation occupies only H×MAX_C cells. The SRAM scratch has logical capacity MAX_C and remains partially uninitialized above C. Only its active view `[0:C]` may be stored by this kernel; storing the full scratch after C writes must fault or reject. A burst implementation may allocate or transport private padding under its target protocol only while preserving the source's exact C-cell access/visibility footprint.

**Generic numeric specialization.** Replacing Int by a frozen registered T descriptor requires Bits/storage representation, exact representability of every signed filter coefficient, `mul`/`abs`/`add` registrations with explicit rounding/overflow, a typed zero, and a checker-owned total associative addition law for the complete admitted reduction domain. Signed wrapping integral types can satisfy these obligations. Ordinary floating addition cannot use this lawful `reduce` merely because the original Scala helper required `Num`; use explicit ordered folds or a recorded fixed tree and document its numerical order instead. Unsigned types that cannot represent -1/-2 also fail this literal-image instance unless an explicitly different coefficient encoding is supplied. There is no generic Python float callback, silent widening, or arbitrary host class implementation of Num.

**Guide-sized convolution.** Specialize the guide's padded R/C (16,32,48,...) instead of the older fixture, allocate width C, replace the two coefficient tuples with the guide's values, and supply its padded host image. Drop the older C<=16 restriction. Preserve the first-two-row/column mask and exact alignment. This is a separate input/profile, not another test of the original 16×16 generator. Source: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:83-155`.

**Column tiling is not free.** A row-streaming line buffer advances image history at a publication boundary; loading a piece of a row as if it were a complete next row changes the vertical history. The guide's commented explanation warns exactly about this split. A tiled convolution needs an explicit width/halo/origin model and row-boundary schedule, or a separate line buffer per column tile with overlap/reload, with output ownership for the halos. Simply replacing C with TILE in this kernel is not justified. Source: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:71`.

**Strided/history variants.** The feature tests cover one buffer, two buffers, a two-row manual frame and a two-row dense frame. They are supporting API evidence only. Their host gold formulas assert newest-first ordering, including the seven-row slice that deliberately omits row 0 in the 8-row case. They do not establish arbitrary stride/mask overlap equivalence or a full convolution for every topology. Source: `spatial@c1979ce:test/spatial/tests/feature/memories/linebuf/LineBuffers.scala:22-128`. Original `enqAt` and emulator cursor semantics remain separate from the proposed compact-active-lane frame policy: `spatial@c1979ce:src/spatial/lang/LineBuffer.scala:23-38`; `spatial@c1979ce:emul/src/emul/LineBuffer.scala:43-59`.

**Part 2 is a backend lesson.** The HLS guide's C++ GEMM TODO, vector-add TODO, unroll experiment, memory-width questions, native testbench, RTL test and board test motivate separate frontend/reference, code-generation, synthesis and protocol gates. They do not define a new Python convolution API or show this proposed compiler can produce FPGA hardware. The guide labels the interface/runtime questions as exercises; no private answer or uncited port-width number is inserted here. Source: `digital-systems-design-lab@b4896ab:lab3_part2_f2_fpga.md:13-48,63-106`.

**CORDIC is a caution, not a replacement kernel.** Lab 3 links to the design-flow page, which links the CORDIC document as a collection of ChatGPT-generated introductory material. The supplied `cordic_sqrt` initializes `(x,y)=(value,0)` and applies a homogeneous linear recurrence; for positive scaling of value, direction decisions remain the same and its result scales linearly. A square root scales by the square root of that factor, so this routine cannot implement general sqrt. The document also writes a reciprocal product for K while describing the value near 1.64676. These are direct source/derivation discrepancies; do not import its native float/list-comprehension loop as an exact numeric primitive. Sources: `digital-systems-design-lab@b4896ab:lab3_part1_spatial.md:175-176`; `digital-systems-design-lab@b4896ab:spatial-design-flow.md:271-274`; `digital-systems-design-lab@b4896ab:CORDIC.md:19-50,148-154`. A real optional sqrt must use the owned numeric contract/recipe with a declared accuracy and operation order.

## Validation required, and checks actually performed

The following are **acceptance requirements**, not passing compiler tests:

| Case | Required discriminating observation |
|---|---|
| L3-V01 orientation | Publish distinct rows/columns, inspect all nine RF cells and signed h/v; detect either reversed dimension and globally flipped gradients |
| L3-V02 warmup | R,C in 1..3: no uninitialized read, correctly initialized zero outputs; replacing lazy sample guard with eager select must fail or fault |
| L3-V03 reset | Distinct last column of row r and first column of row r+1: no horizontal history leaks after c=0 reset |
| L3-V04 shift snapshot | Old `[10,20,30]`, scalar40→`[40,10,20]`; chronological Vec[40,50]→`[50,40,10]`; zero mask no-op, oversized batch faults atomically |
| L3-V05 publication | Two staging rows A then B yield `[B,A,old0]`; incomplete frame cannot publish; interleaved row fills retain separate cursors |
| L3-V06 view/init | A scalar row index drops one axis; shape mismatch, out-of-range column, uninitialized SRAM read and stale Frame/view generation diagnose at the active operation |
| L3-V07 arithmetic | Extreme Int bits verify multiplication/addition/abs wrapping and nested lawful reduction; F32 substitution requires fixed order or a rejected law request |
| L3-V08 lifetime | Two invocations begin with fresh LB/RF state; pixel Reg reset each pixel; outer RF persists until explicit reset; helper borrow cannot outlive owner |
| L3-V09 scheduling | Change physical lanes/banking while matching bits/events; `par` cannot change next-row visibility or turn ordered calls into tasks |
| L3-V10 aliases and tails | Reject overlapping src/dst under this kernel's disjointness requirement, including shifted views; separately verify generic alias-preserving transfers; partial physical burst consumes/writes no extra logical cells |
| L3-V11 source boundary | Reject kernel comprehension/native `math`/dynamic callback/host truth conversion, unknown `.shift` receiver, LUT mutation and unregistered frame methods |
| L3-V12 real backend | Separate reference results, generated C behavior, synthesis capability/resources, RTL stalled-interface trace, and board evidence; no passing label inferred from another stage |
| L3-V13 runtime width | MAX_C=16, C=5: publish/read/store exactly five columns; reject C=0, C=17, changed width, mismatched row length and full scratch store; a second invocation with C=7 gets a fresh history generation |

A bounded **standalone design probe** was run on 2026-10-01 using Python integer arithmetic, independently of any proposed compiler. One model used explicit newest-first history and snapshot row shifts; another directly indexed the input at `(r-i,c-j)`. Both used signed-32 wrapping arithmetic. They agreed for 72 generated matrices covering R=1..8, C=1..9 with values drawn from `{Int.min,Int.max,-17,0,1,321}`, plus the public 16×16 image. The concrete fixture produced 256 outputs, total 44,928, maximum 1,088. This checks the proposed repaired window equation/arithmetic for these finite cases; it does not run the listing or validate parser, effect checker, generic numeric support, hardware scheduling, or the original compiler. The historical checksum source is `spatial@c1979ce:test/spatial/tests/ee109/Lab3.scala:121-126`.

The decisive research conclusion is narrow: this convolution has a complete, reviewable Python-shaped mapping once the listed resource signatures are registered, and its typed operations fit the existing architecture. The warmup, reset, runtime-capacity and frame-publication rules must remain visible in that contract; hiding them inside an apparently ordinary Python loop would lose the behavior being translated.
