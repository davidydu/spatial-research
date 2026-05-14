---
type: research-note
topic: ee109-examples-catalog
source_files:
  - "spatial/test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala"
  - "spatial/test/spatial/tests/ee109/Lab2Part4LUT.scala"
  - "spatial/test/spatial/tests/ee109/Lab3.scala"
sources_remote:
  - "(none cloned; gh CLI could not reach api.github.com from sandbox, and web search found no public EE109 Spatial Scala repositories)"
date: 2026-05-14
status: draft
---

# EE109 Spatial Examples Catalog

## Methodology

- Primary corpus: `find ~/Documents/David_code/spatial/test/spatial/tests/ee109 -name "*.scala" | wc -l` returned 3 files.
- Every `.scala` file in the mandatory local source was enumerated and read completely: `Lab2Part3BasicCondFSM.scala`, `Lab2Part4LUT.scala`, and `Lab3.scala`.
- LOC basis: `wc -l` returned 38 LOC for `Lab2Part3BasicCondFSM.scala`, 36 LOC for `Lab2Part4LUT.scala`, 129 LOC for `Lab3.scala`, 203 LOC total.
- Counting rule: frequency is per example, not per occurrence. For example, `Lab3.scala` uses four `Reduce` controllers (`Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`) but counts as one example using `Reduce`.
- Secondary remote search: requested `gh search repos` commands failed because the sandbox could not reach `api.github.com`; web search did not surface public EE109 Spatial Scala repositories. Remote corpus completeness is therefore [UNVERIFIED].
- Tertiary private source: `~/Documents/David_code/ee109-mla/` was used only to validate high-level EE109 project patterns. It is not quoted. Pattern summary only: the project emphasizes software reference models, numerical gates, precision choices, LUT approximations, and unit/integration tests.
- Full-Spatial comparison basis: the local Spatial Research spec was used qualitatively. The language index lists controllers, memories, primitives, streams/blackboxes, math helpers, host I/O, debugging, virtualization, aliases, macros, and standard libraries as the broader Spatial surface (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:15`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:16`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:17`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:18`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:19`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:20`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:21`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:22`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:23`).
- Denominator caveat: the corpus has 3 examples, so 1 example is 33.3%, 2 examples is 66.7%, and 3 examples is 100%. No positive-use feature can fall below 30%.

## Per-example Summary Table

| File | LOC | Top features | One-line note |
|---|---:|---|---|
| `Lab2Part3BasicCondFSM.scala` | 38 | `Accel`, `FSM`, `DRAM`, `SRAM`, `Reg`, `store`, `getMem`, conditionals, host `zip`/`reduce` | Conditional FSM writes a local SRAM, stores to DRAM, reads back with `getMem`, and checks a host gold array (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part3BasicCondFSM.scala:11`, `Lab2Part3BasicCondFSM.scala:12`, `Lab2Part3BasicCondFSM.scala:15`, `Lab2Part3BasicCondFSM.scala:28`, `Lab2Part3BasicCondFSM.scala:30`, `Lab2Part3BasicCondFSM.scala:35`). |
| `Lab2Part4LUT.scala` | 36 | `Accel`, `ArgIn`, `ArgOut`, `LUT`, `setArg`, `getArg`, args parsing, `Array.tabulate` | Scalar host/accelerator boundary example using three `ArgIn`s, one `ArgOut`, and a 3x3 lookup table (`Lab2Part4LUT.scala:10`, `Lab2Part4LUT.scala:11`, `Lab2Part4LUT.scala:15`, `Lab2Part4LUT.scala:19`, `Lab2Part4LUT.scala:25`, `Lab2Part4LUT.scala:29`, `Lab2Part4LUT.scala:30`). |
| `Lab3.scala` | 129 | `Accel`, `Foreach`, `Sequential.Foreach`, `Pipe`, `Reduce`, `DRAM`, `LineBuffer`, `RegFile`, `LUT`, `SRAM`, `par`, `load`, `store`, `mux`, `getMatrix` | Sobel-style 2-D convolution with line-buffered reuse, sliding window, nested reductions, boundary mux, dense output store, and host checksum (`Lab3.scala:20`, `Lab3.scala:25`, `Lab3.scala:26`, `Lab3.scala:35`, `Lab3.scala:38`, `Lab3.scala:41`, `Lab3.scala:42`, `Lab3.scala:56`, `Lab3.scala:72`, `Lab3.scala:74`, `Lab3.scala:78`). |

## Per-example Extraction

### `Lab2Part3BasicCondFSM.scala`

- Path: `spatial/test/spatial/tests/ee109/Lab2Part3BasicCondFSM.scala`.
- LOC: 38.
- Description: conditional finite-state machine over 32 states that writes an SRAM, stores to DRAM, reads the result on the host, and checks equality (`Lab2Part3BasicCondFSM.scala:15`, `Lab2Part3BasicCondFSM.scala:18`, `Lab2Part3BasicCondFSM.scala:24`, `Lab2Part3BasicCondFSM.scala:28`, `Lab2Part3BasicCondFSM.scala:30`, `Lab2Part3BasicCondFSM.scala:35`).
- Controllers: `Accel` (`Lab2Part3BasicCondFSM.scala:11`); `FSM` (`Lab2Part3BasicCondFSM.scala:15`).
- Memory primitives: `DRAM[Int]` (`Lab2Part3BasicCondFSM.scala:10`); `SRAM[Int]` (`Lab2Part3BasicCondFSM.scala:12`); `Reg[Int]` (`Lab2Part3BasicCondFSM.scala:13`).
- Types: explicit `Int` (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part3BasicCondFSM.scala:12`, `Lab2Part3BasicCondFSM.scala:13`); predicates/Boolean checks (`Lab2Part3BasicCondFSM.scala:15`, `Lab2Part3BasicCondFSM.scala:16`, `Lab2Part3BasicCondFSM.scala:17`, `Lab2Part3BasicCondFSM.scala:35`).
- Transfers: DRAM `store` (`Lab2Part3BasicCondFSM.scala:28`); `getMem` (`Lab2Part3BasicCondFSM.scala:30`).
- Functional combinators: host `zip` and `reduce` checksum (`Lab2Part3BasicCondFSM.scala:35`).
- Banking/parallelism: no `par`, explicit `.bank`/`.banking`, or `.bufferAmount`.
- Math: address arithmetic and integer arithmetic (`Lab2Part3BasicCondFSM.scala:18`, `Lab2Part3BasicCondFSM.scala:20`, `Lab2Part3BasicCondFSM.scala:24`, `Lab2Part3BasicCondFSM.scala:26`); comparisons (`Lab2Part3BasicCondFSM.scala:15`, `Lab2Part3BasicCondFSM.scala:16`, `Lab2Part3BasicCondFSM.scala:17`, `Lab2Part3BasicCondFSM.scala:24`).
- Host-side: `printArray`/`println` (`Lab2Part3BasicCondFSM.scala:33`, `Lab2Part3BasicCondFSM.scala:34`, `Lab2Part3BasicCondFSM.scala:36`); assertion (`Lab2Part3BasicCondFSM.scala:37`).
- Special: conditional `if`/`else` (`Lab2Part3BasicCondFSM.scala:16`, `Lab2Part3BasicCondFSM.scala:17`, `Lab2Part3BasicCondFSM.scala:24`). The comment at `Lab2Part3BasicCondFSM.scala:24` mentions a Mux1H test, but there is no explicit `mux` API call.

### `Lab2Part4LUT.scala`

- Path: `spatial/test/spatial/tests/ee109/Lab2Part4LUT.scala`.
- LOC: 36.
- Description: host arguments populate scalar ArgIns, accelerator adds an input to a 2-D LUT lookup, host reads an ArgOut, and checks gold (`Lab2Part4LUT.scala:10`, `Lab2Part4LUT.scala:11`, `Lab2Part4LUT.scala:15`, `Lab2Part4LUT.scala:19`, `Lab2Part4LUT.scala:25`, `Lab2Part4LUT.scala:26`, `Lab2Part4LUT.scala:29`, `Lab2Part4LUT.scala:31`).
- Controllers: `Accel` (`Lab2Part4LUT.scala:23`).
- Memory primitives: three `ArgIn[T]` scalars (`Lab2Part4LUT.scala:10`, `Lab2Part4LUT.scala:12`, `Lab2Part4LUT.scala:13`); one `ArgOut[T]` (`Lab2Part4LUT.scala:11`); `LUT[Int]` (`Lab2Part4LUT.scala:25`).
- Types: `type T = Int` (`Lab2Part4LUT.scala:6`); Boolean equality result (`Lab2Part4LUT.scala:32`).
- Transfers: `setArg` (`Lab2Part4LUT.scala:19`, `Lab2Part4LUT.scala:20`, `Lab2Part4LUT.scala:21`); `getArg` (`Lab2Part4LUT.scala:29`).
- Functional combinators: `Array.tabulate` (`Lab2Part4LUT.scala:30`).
- Banking/parallelism: no `par`, explicit `.bank`/`.banking`, or `.bufferAmount`.
- Math: accelerator addition (`Lab2Part4LUT.scala:26`); host index arithmetic (`Lab2Part4LUT.scala:31`); equality checks (`Lab2Part4LUT.scala:32`, `Lab2Part4LUT.scala:35`).
- Host-side: `runtimeArgs` override (`Lab2Part4LUT.scala:4`); `args(...).to[T]` parsing (`Lab2Part4LUT.scala:15`, `Lab2Part4LUT.scala:16`, `Lab2Part4LUT.scala:17`); print (`Lab2Part4LUT.scala:33`); assertion (`Lab2Part4LUT.scala:35`).
- Special: no explicit `mux`, no conditional, no blackbox.

### `Lab3.scala`

- Path: `spatial/test/spatial/tests/ee109/Lab3.scala`.
- LOC: 129.
- Description: Sobel-style 2-D convolution over a host `Matrix[T]`, using DRAM, LineBuffer, RegFile, LUT kernels, SRAM output staging, nested reductions, and host checksum (`Lab3.scala:11`, `Lab3.scala:20`, `Lab3.scala:23`, `Lab3.scala:26`, `Lab3.scala:28`, `Lab3.scala:31`, `Lab3.scala:35`, `Lab3.scala:39`, `Lab3.scala:56`, `Lab3.scala:63`, `Lab3.scala:72`, `Lab3.scala:74`, `Lab3.scala:78`, `Lab3.scala:121`, `Lab3.scala:122`).
- Controllers: `Accel` (`Lab3.scala:25`); outer `Foreach` (`Lab3.scala:38`); `Sequential.Foreach` (`Lab3.scala:41`); `Pipe` (`Lab3.scala:42`); inner `Foreach` controllers (`Lab3.scala:44`, `Lab3.scala:45`); nested `Reduce` (`Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`).
- Memory primitives: `ArgIn[Int]` (`Lab3.scala:14`, `Lab3.scala:15`); `DRAM[T]` (`Lab3.scala:20`, `Lab3.scala:21`); `LineBuffer[T]` (`Lab3.scala:26`); `LUT[T]` (`Lab3.scala:28`, `Lab3.scala:31`); `RegFile[T]` (`Lab3.scala:35`); `SRAM[T]` (`Lab3.scala:36`); `Reg[T]` accumulators (`Lab3.scala:53`, `Lab3.scala:54`).
- Types: generic `T:Num` and host `Matrix[T]` (`Lab3.scala:11`); explicit `Int` ArgIns (`Lab3.scala:14`, `Lab3.scala:15`); Boolean predicates (`Lab3.scala:72`, `Lab3.scala:85`, `Lab3.scala:86`, `Lab3.scala:104`, `Lab3.scala:124`).
- Transfers: `setArg` (`Lab3.scala:16`, `Lab3.scala:17`); `setMem` (`Lab3.scala:23`); line-buffer `load` from DRAM (`Lab3.scala:39`); DRAM `store` (`Lab3.scala:74`); `getMatrix` (`Lab3.scala:78`).
- Functional combinators: range tensor/matrix constructors (`Lab3.scala:85`, `Lab3.scala:86`, `Lab3.scala:104`); host `map` (`Lab3.scala:121`); host `zip` and `reduce` (`Lab3.scala:122`).
- Banking/parallelism: explicit `par` (`Lab3.scala:39`, `Lab3.scala:44`, `Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`, `Lab3.scala:74`).
- Math: multiply/add reductions (`Lab3.scala:59`, `Lab3.scala:60`, `Lab3.scala:66`, `Lab3.scala:67`); `abs` and addition (`Lab3.scala:72`); gold arithmetic (`Lab3.scala:114`); comparisons (`Lab3.scala:72`, `Lab3.scala:85`, `Lab3.scala:86`, `Lab3.scala:124`).
- Host-side: debug prints inside accelerator (`Lab3.scala:47`, `Lab3.scala:70`); host matrix prints (`Lab3.scala:117`, `Lab3.scala:118`, `Lab3.scala:119`); status prints (`Lab3.scala:123`, `Lab3.scala:125`); assertion (`Lab3.scala:126`).
- Special: explicit `mux` (`Lab3.scala:72`); conditionals in host matrix/gold construction (`Lab3.scala:85`, `Lab3.scala:86`, `Lab3.scala:104`); RegFile shift-in (`Lab3.scala:44`); local reset call (`Lab3.scala:42`).

## Feature Frequency Matrix

Percentages use denominator 3 examples.

### Controllers

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `Accel` | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:11`; `Lab2Part4LUT.scala:23`; `Lab3.scala:25` |
| `Sequential` | 1 | 33.3% | `Lab3.scala:41` |
| `Pipe` | 1 | 33.3% | `Lab3.scala:42` |
| `Foreach` | 1 | 33.3% | `Lab3.scala:38`; `Lab3.scala:44`; `Lab3.scala:45` |
| `Reduce` | 1 | 33.3% | `Lab3.scala:56`; `Lab3.scala:57`; `Lab3.scala:63`; `Lab3.scala:64` |
| `MemReduce` | 0 | 0.0% | not found in corpus |
| `FSM` / `StateMachine` | 1 | 33.3% | `Lab2Part3BasicCondFSM.scala:15` |
| `StreamForeach` / `Accel(*)` | 0 | 0.0% | not found in corpus |
| `ParallelPipe` / `Parallel` | 0 | 0.0% | not found in corpus |

### Memory Primitives

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `Reg` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:13`; `Lab3.scala:53`; `Lab3.scala:54` |
| `ArgIn` | 2 | 66.7% | `Lab2Part4LUT.scala:10`; `Lab2Part4LUT.scala:12`; `Lab2Part4LUT.scala:13`; `Lab3.scala:14`; `Lab3.scala:15` |
| `ArgOut` | 1 | 33.3% | `Lab2Part4LUT.scala:11` |
| `HostIO` | 0 | 0.0% | not found in corpus |
| `SRAM` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:12`; `Lab3.scala:36` |
| `DRAM` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:10`; `Lab3.scala:20`; `Lab3.scala:21` |
| `FIFO` | 0 | 0.0% | not found in corpus |
| `LIFO` | 0 | 0.0% | not found in corpus |
| `FIFOReg` | 0 | 0.0% | not found in corpus |
| `LineBuffer` | 1 | 33.3% | `Lab3.scala:26` |
| `RegFile` | 1 | 33.3% | `Lab3.scala:35` |
| `MergeBuffer` | 0 | 0.0% | not found in corpus |
| `StreamIn` | 0 | 0.0% | not found in corpus |
| `StreamOut` | 0 | 0.0% | not found in corpus |
| `LUT` | 2 | 66.7% | `Lab2Part4LUT.scala:25`; `Lab3.scala:28`; `Lab3.scala:31` |

### Types

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `Int` | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:10`; `Lab2Part4LUT.scala:6`; `Lab3.scala:14` |
| `FixPt[S,I,F]` | 0 | 0.0% | not found in corpus |
| `Float` | 0 | 0.0% | not found in corpus |
| `FltPt` / `Flt` | 0 | 0.0% | not found in corpus |
| `Bool` / predicate values | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:15`; `Lab2Part4LUT.scala:32`; `Lab3.scala:124` |
| `Tup2` / `Tup3` data values | 0 | 0.0% | not found in corpus; tuple-shaped lambdas such as `Lab3.scala:85` are not counted as Tup data values |
| user `Struct` | 0 | 0.0% | not found in corpus |
| host `Matrix[T]` | 1 | 33.3% | `Lab3.scala:11` |
| `Vec` | 0 | 0.0% | not found in corpus |
| generic `T:Num` | 1 | 33.3% | `Lab3.scala:11` |

### Transfers

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `load` | 1 | 33.3% | `Lab3.scala:39` |
| `store` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:28`; `Lab3.scala:74` |
| `gather` | 0 | 0.0% | not found in corpus |
| `scatter` | 0 | 0.0% | not found in corpus |
| `setMem` | 1 | 33.3% | `Lab3.scala:23` |
| `getMem` | 1 | 33.3% | `Lab2Part3BasicCondFSM.scala:30` |
| `setArg` | 2 | 66.7% | `Lab2Part4LUT.scala:19`; `Lab2Part4LUT.scala:20`; `Lab2Part4LUT.scala:21`; `Lab3.scala:16`; `Lab3.scala:17` |
| `getArg` | 1 | 33.3% | `Lab2Part4LUT.scala:29` |
| `getMatrix` | 1 | 33.3% | `Lab3.scala:78` |
| `getTensor*` | 0 | 0.0% | not found in corpus |

### Functional Combinators

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `tabulate` / range tensor constructor | 2 | 66.7% | `Lab2Part4LUT.scala:30`; `Lab3.scala:85`; `Lab3.scala:86`; `Lab3.scala:104` |
| `zip` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:35`; `Lab3.scala:122` |
| `reduce` | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:35`; `Lab3.scala:121`; `Lab3.scala:122` |
| `map` | 1 | 33.3% | `Lab3.scala:121` |
| lower-case `.foreach` | 0 | 0.0% | not found in corpus |
| `sum` | 0 | 0.0% | not found in corpus |
| `fold` | 0 | 0.0% | not found in corpus |

### Banking and Parallelism

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| `par` | 1 | 33.3% | `Lab3.scala:39`; `Lab3.scala:44`; `Lab3.scala:56`; `Lab3.scala:57`; `Lab3.scala:63`; `Lab3.scala:64`; `Lab3.scala:74` |
| explicit `.bank` / `.banking` | 0 | 0.0% | not found in corpus |
| `.bufferAmount` | 0 | 0.0% | not found in corpus |

### Math

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| arithmetic | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:18`; `Lab2Part4LUT.scala:26`; `Lab3.scala:59` |
| comparisons | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:15`; `Lab2Part4LUT.scala:32`; `Lab3.scala:124` |
| `abs` | 1 | 33.3% | `Lab3.scala:72`; `Lab3.scala:114` |
| `sin` | 0 | 0.0% | not found in corpus |
| `cos` | 0 | 0.0% | not found in corpus |
| `exp` | 0 | 0.0% | not found in corpus |
| `log` / `ln` | 0 | 0.0% | not found in corpus |
| `sqrt` | 0 | 0.0% | not found in corpus; comment mentions ideal `sqrt` at `Lab3.scala:72`, but there is no call |
| `tanh` | 0 | 0.0% | not found in corpus |

### Host-side Features

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| random | 0 | 0.0% | not found in corpus |
| args parsing | 1 | 33.3% | `Lab2Part4LUT.scala:15`; `Lab2Part4LUT.scala:16`; `Lab2Part4LUT.scala:17` |
| `print*` / `println` | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:33`; `Lab2Part4LUT.scala:33`; `Lab3.scala:117` |
| assertions | 3 | 100.0% | `Lab2Part3BasicCondFSM.scala:37`; `Lab2Part4LUT.scala:35`; `Lab3.scala:126` |
| `runtimeArgs` test harness override | 1 | 33.3% | `Lab2Part4LUT.scala:4` |

### Special Features

| Construct | Count | Percent | Example file names / citations |
|---|---:|---:|---|
| explicit `mux` | 1 | 33.3% | `Lab3.scala:72` |
| conditionals | 2 | 66.7% | `Lab2Part3BasicCondFSM.scala:16`; `Lab2Part3BasicCondFSM.scala:17`; `Lab2Part3BasicCondFSM.scala:24`; `Lab3.scala:85`; `Lab3.scala:86`; `Lab3.scala:104` |
| blackbox | 0 | 0.0% | not found in corpus |
| RegFile shift-in `<<=` | 1 | 33.3% | `Lab3.scala:44` |
| memory reset call | 1 | 33.3% | `Lab3.scala:42`; public surface status [UNVERIFIED] |

## Feature Tiers

### Tier 1: >=80%

- `Accel`: every example wraps accelerator code in `Accel` (`Lab2Part3BasicCondFSM.scala:11`, `Lab2Part4LUT.scala:23`, `Lab3.scala:25`).
- `Int`: every example uses explicit integer types or aliases (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part4LUT.scala:6`, `Lab3.scala:14`).
- Predicate/Boolean logic: every example has comparisons or Boolean checks (`Lab2Part3BasicCondFSM.scala:15`, `Lab2Part4LUT.scala:32`, `Lab3.scala:124`).
- Arithmetic: every example performs scalar arithmetic (`Lab2Part3BasicCondFSM.scala:18`, `Lab2Part4LUT.scala:26`, `Lab3.scala:59`).
- Host prints: every example emits result or pass diagnostics (`Lab2Part3BasicCondFSM.scala:33`, `Lab2Part4LUT.scala:33`, `Lab3.scala:117`).
- Host assertions: every example ends with an assertion (`Lab2Part3BasicCondFSM.scala:37`, `Lab2Part4LUT.scala:35`, `Lab3.scala:126`).

### Tier 2: 30-80%

- Controllers: `FSM`, `Sequential.Foreach`, `Pipe`, `Foreach`, and `Reduce` each appear in 1 of 3 examples (`Lab2Part3BasicCondFSM.scala:15`, `Lab3.scala:41`, `Lab3.scala:42`, `Lab3.scala:38`, `Lab3.scala:56`).
- Memories: `Reg`, `ArgIn`, `SRAM`, `DRAM`, and `LUT` appear in 2 of 3 examples (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part3BasicCondFSM.scala:12`, `Lab2Part3BasicCondFSM.scala:13`, `Lab2Part4LUT.scala:10`, `Lab2Part4LUT.scala:25`, `Lab3.scala:20`, `Lab3.scala:28`, `Lab3.scala:36`, `Lab3.scala:53`).
- Advanced local memories: `LineBuffer` and `RegFile` appear only in convolution (`Lab3.scala:26`, `Lab3.scala:35`).
- Transfers: `store` and `setArg` appear in 2 of 3 examples (`Lab2Part3BasicCondFSM.scala:28`, `Lab2Part4LUT.scala:19`, `Lab3.scala:16`, `Lab3.scala:74`); `load`, `setMem`, `getMem`, `getArg`, and `getMatrix` appear in 1 of 3 (`Lab3.scala:39`, `Lab3.scala:23`, `Lab2Part3BasicCondFSM.scala:30`, `Lab2Part4LUT.scala:29`, `Lab3.scala:78`).
- Host combinators: tabulation/range construction, `zip`, and `reduce` appear in 2 of 3 examples (`Lab2Part4LUT.scala:30`, `Lab3.scala:85`, `Lab2Part3BasicCondFSM.scala:35`, `Lab3.scala:122`); `map` appears in 1 of 3 (`Lab3.scala:121`).
- Parallelism: `par` appears in only the convolution example (`Lab3.scala:39`, `Lab3.scala:44`, `Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`, `Lab3.scala:74`).
- Special control/data selection: explicit `mux` appears only in convolution (`Lab3.scala:72`); conditionals appear in the FSM and convolution examples (`Lab2Part3BasicCondFSM.scala:16`, `Lab3.scala:85`).

### Tier 3: <30%

- No positive-use feature falls below 30% because the corpus has only 3 examples. Any feature used in one example is 33.3%.

### Unused

- Controllers not found in corpus: `MemReduce`, `StreamForeach`/`Accel(*)`, `ParallelPipe`/`Parallel`.
- Memories not found in corpus: `HostIO`, `FIFO`, `LIFO`, `FIFOReg`, `MergeBuffer`, `StreamIn`, `StreamOut`.
- Types not found in corpus: explicit `FixPt[S,I,F]`, `Float`, `FltPt`/`Flt`, `Tup2`/`Tup3` data values, user `Struct`, `Vec`.
- Transfers not found in corpus: `gather`, `scatter`, `getTensor*`.
- Functional combinators not found in corpus: lower-case `.foreach`, `sum`, `fold`.
- Banking/tuning not found in corpus: explicit `.bank`/`.banking`, `.bufferAmount`, and the broader memory hint family.
- Math not found in corpus: explicit `sin`, `cos`, `exp`, `log`/`ln`, `sqrt`, `tanh`.
- Host-side features not found in corpus: random data generation.
- Special features not found in corpus: blackboxes.

## Comparison: EE109 vs Full Spatial

### EE109-specific Idioms

- All three examples use `@spatial class ... extends SpatialTest` (`Lab2Part3BasicCondFSM.scala:7`, `Lab2Part4LUT.scala:3`, `Lab3.scala:5`). The full Language Surface Index lists `@spatial` macros, but not `SpatialTest` as a core user-facing construct (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:22`). Treat `SpatialTest` as course/test harness, not core DSL.
- All three examples use host prints and assertions as the standard pass/fail shape (`Lab2Part3BasicCondFSM.scala:33`, `Lab2Part3BasicCondFSM.scala:37`, `Lab2Part4LUT.scala:33`, `Lab2Part4LUT.scala:35`, `Lab3.scala:117`, `Lab3.scala:126`). The full language has debugging/checking support (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:19`), but EE109 uses it as lab scaffolding.
- All three examples put exactly one top-level `Accel` inside the test (`Lab2Part3BasicCondFSM.scala:11`, `Lab2Part4LUT.scala:23`, `Lab3.scala:25`). Full Spatial exposes many more controller forms: `Fold`, `MemReduce`, `MemFold`, `Stream`, `Parallel`, and `Named` (`10 - Spec/10 - Language Surface/10 - Controllers.md:29`, `10 - Spec/10 - Language Surface/10 - Controllers.md:40`, `10 - Spec/10 - Language Surface/10 - Controllers.md:42`, `10 - Spec/10 - Language Surface/10 - Controllers.md:45`, `10 - Spec/10 - Language Surface/10 - Controllers.md:47`, `10 - Spec/10 - Language Surface/10 - Controllers.md:49`).
- Every example has an in-file gold model or checksum (`Lab2Part3BasicCondFSM.scala:31`, `Lab2Part3BasicCondFSM.scala:35`, `Lab2Part4LUT.scala:30`, `Lab2Part4LUT.scala:32`, `Lab3.scala:104`, `Lab3.scala:121`, `Lab3.scala:124`). This is a course idiom; repo-wide rarity outside EE109 is [UNVERIFIED].

### Full Spatial Features Absent from EE109

- Stream and blackbox APIs are absent. Full Spatial exposes `StreamIn`, `StreamOut`, `StreamStruct`, `Blackbox.SpatialPrimitive`, `Blackbox.SpatialController`, `Blackbox.VerilogPrimitive`, and `Blackbox.VerilogController` (`10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:26`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:31`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:34`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:40`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:41`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:42`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:43`).
- Rich local memory types are mostly absent. Full Spatial lists `FIFO`, `LIFO`, `LineBuffer`, `MergeBuffer`, `LUT`, `LockSRAM`, `StreamIn`, `StreamOut`, and `StreamStruct` as local memories (`10 - Spec/10 - Language Surface/20 - Memories.md:32`), while EE109 uses only `SRAM`, `Reg`, `RegFile`, `LineBuffer`, and `LUT` (`Lab2Part3BasicCondFSM.scala:12`, `Lab2Part3BasicCondFSM.scala:13`, `Lab2Part4LUT.scala:25`, `Lab3.scala:26`, `Lab3.scala:35`, `Lab3.scala:36`).
- Explicit memory tuning is absent. The full memory spec mentions SRAM and RegFile tuning hints such as `.buffer`, `.bank`, `.forcebank`, and `.nBest` (`10 - Spec/10 - Language Surface/20 - Memories.md:32`); no EE109 file uses explicit `.bank`, `.forcebank`, `.buffer`, `.coalesce`, or `.bufferAmount`.
- Full host/file I/O is absent. The spec covers `CSVFile`, `BinaryFile`, `Tensor3-5`, CSV/binary/numpy file I/O, `setFrame`, and `getFrame` (`10 - Spec/10 - Language Surface/60 - Host and IO.md:32`, `10 - Spec/10 - Language Surface/60 - Host and IO.md:48`, `10 - Spec/10 - Language Surface/60 - Host and IO.md:49`, `10 - Spec/10 - Language Surface/60 - Host and IO.md:50`), while EE109 uses scalar args, DRAM set/get, and matrix get (`Lab2Part4LUT.scala:19`, `Lab2Part4LUT.scala:29`, `Lab3.scala:23`, `Lab3.scala:78`).
- Full numeric semantics are much richer than the examples. The data-types spec covers fixed-point formats, floating formats, three-valued Bool, vectors, and mux-family semantics (`10 - Spec/20 - Semantics/50 - Data Types.md:38`, `10 - Spec/20 - Semantics/50 - Data Types.md:42`, `10 - Spec/20 - Semantics/50 - Data Types.md:44`, `10 - Spec/20 - Semantics/50 - Data Types.md:48`, `10 - Spec/20 - Semantics/50 - Data Types.md:50`, `10 - Spec/20 - Semantics/50 - Data Types.md:56`, `10 - Spec/20 - Semantics/50 - Data Types.md:58`). EE109 examples use `Int`, generic `T:Num`, predicates, and no explicit fixed/floating/vector data types (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part4LUT.scala:6`, `Lab3.scala:11`, `Lab3.scala:14`).
- Advanced math helpers are absent. The full math surface includes reductions, `exp`, `ln`, `sqrt`, trig, Taylor approximations, `oneHotMux`, `priorityMux`, priority/round-robin dequeues, and retiming helpers (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:17`). EE109 uses arithmetic, comparisons, `abs`, and one explicit `mux` (`Lab3.scala:72`, `Lab3.scala:114`).
- Virtualization, aliasing/shadowing, macros beyond `@spatial`, and the standard library are absent except implicitly through normal DSL use. These are full-language areas in the index (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:20`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:21`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:22`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:23`).

### Pedagogical Simplifications

- EE109 examples prefer direct controller syntax over directive chains. Full Spatial supports `.II`, `.POM`, `.MOP`, `.NoBind`, and `.haltIfStarved` (`10 - Spec/10 - Language Surface/10 - Controllers.md:52`, `10 - Spec/10 - Language Surface/10 - Controllers.md:54`, `10 - Spec/10 - Language Surface/10 - Controllers.md:55`, `10 - Spec/10 - Language Surface/10 - Controllers.md:56`, `10 - Spec/10 - Language Surface/10 - Controllers.md:57`, `10 - Spec/10 - Language Surface/10 - Controllers.md:58`), but the EE109 examples use none of those modifiers.
- EE109 examples rely on compiler-managed banking by default. The only explicit parallelism annotation is `par` in `Lab3.scala` (`Lab3.scala:39`, `Lab3.scala:44`, `Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`, `Lab3.scala:74`).
- EE109 examples keep host I/O simple: scalar args and ArgIn/ArgOut in `Lab2Part4LUT.scala` (`Lab2Part4LUT.scala:15`, `Lab2Part4LUT.scala:19`, `Lab2Part4LUT.scala:29`), and `setMem`/`getMatrix` in `Lab3.scala` (`Lab3.scala:23`, `Lab3.scala:78`).
- EE109 examples avoid external interfaces: no streams, buses, or blackboxes appear, even though the full surface includes stream ports, stream structs, bus descriptors, Verilog blackboxes, and GEMM blackbox support (`10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:26`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:40`, `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:44`).
- EE109 examples avoid numeric-format complexity: no explicit fixed-point, floating-point, vector, or user-struct declarations, despite these being major Rust/HLS reference-semantics concerns (`10 - Spec/20 - Semantics/50 - Data Types.md:44`, `10 - Spec/20 - Semantics/50 - Data Types.md:50`, `10 - Spec/20 - Semantics/50 - Data Types.md:56`, `10 - Spec/20 - Semantics/50 - Data Types.md:66`).

### MVP Rewrite Implications

- Minimum EE109 subset: `@spatial` app/test entry, `Accel`, `FSM`, `Foreach`, `Sequential.Foreach`, `Pipe`, `Reduce`, `DRAM`, `SRAM`, `Reg`, `ArgIn`, `ArgOut`, `LUT`, `LineBuffer`, `RegFile`, dense `load`/`store`, `setArg`/`getArg`, `setMem`/`getMem`/`getMatrix`, `par`, integer arithmetic/comparisons, `abs`, explicit `mux`, conditionals, host tensor/matrix construction, `map`/`zip`/`reduce`, prints, and assertions.
- Defer for an EE109-only MVP: `MemReduce`, streams, blackboxes, FIFO/LIFO/MergeBuffer, LockMem/Frame, file I/O, explicit banking hints, custom fixed/floating formats, vector bit semantics, priority dequeue, retiming helpers, virtualization, and standard library templates.
- HLS mapping priority: controllers, memories, primitives, and math/helpers are marked clean at the surface level (`30 - HLS Mapping/10 - Clean Mappings.md:14`, `30 - HLS Mapping/10 - Clean Mappings.md:15`, `30 - HLS Mapping/10 - Clean Mappings.md:16`, `30 - HLS Mapping/10 - Clean Mappings.md:17`); streams, host I/O, debugging, data types, scheduling, memory semantics, reductions, and host-accelerator boundary need rework (`30 - HLS Mapping/20 - Needs Rework.md:14`, `30 - HLS Mapping/20 - Needs Rework.md:15`, `30 - HLS Mapping/20 - Needs Rework.md:16`, `30 - HLS Mapping/20 - Needs Rework.md:20`, `30 - HLS Mapping/20 - Needs Rework.md:22`, `30 - HLS Mapping/20 - Needs Rework.md:23`, `30 - HLS Mapping/20 - Needs Rework.md:24`, `30 - HLS Mapping/20 - Needs Rework.md:26`).

## Notable EE109 Patterns

- Course examples are lab-shaped rather than library-shaped: each file defines one `@spatial class`, one `main`, one top-level `Accel`, and one pass/fail assertion (`Lab2Part3BasicCondFSM.scala:7`, `Lab2Part3BasicCondFSM.scala:9`, `Lab2Part3BasicCondFSM.scala:11`, `Lab2Part3BasicCondFSM.scala:37`, `Lab2Part4LUT.scala:3`, `Lab2Part4LUT.scala:5`, `Lab2Part4LUT.scala:23`, `Lab2Part4LUT.scala:35`, `Lab3.scala:5`, `Lab3.scala:81`, `Lab3.scala:126`).
- Gold models are in the same file as the accelerator: literal array in the FSM lab (`Lab2Part3BasicCondFSM.scala:31`), tabulated LUT gold in the LUT lab (`Lab2Part4LUT.scala:30`), and full expected matrix in the convolution lab (`Lab3.scala:104`).
- Accelerator code is embedded in a host-scaffolded test, not separated as reusable kernels (`Lab3.scala:81`, `Lab3.scala:85`, `Lab3.scala:91`, `Lab3.scala:104`, `Lab3.scala:117`, `Lab3.scala:121`, `Lab3.scala:126`).
- Memory hierarchy is introduced incrementally: scalar ArgIn/ArgOut (`Lab2Part4LUT.scala:10`, `Lab2Part4LUT.scala:11`), SRAM/DRAM (`Lab2Part3BasicCondFSM.scala:10`, `Lab2Part3BasicCondFSM.scala:12`), then DRAM plus LineBuffer plus RegFile plus SRAM (`Lab3.scala:20`, `Lab3.scala:26`, `Lab3.scala:35`, `Lab3.scala:36`).
- The only example with explicit parallelism is also the only example with nested control and local-memory data reuse (`Lab3.scala:38`, `Lab3.scala:39`, `Lab3.scala:41`, `Lab3.scala:44`, `Lab3.scala:56`, `Lab3.scala:57`, `Lab3.scala:63`, `Lab3.scala:64`, `Lab3.scala:74`).
- The convolution example captures the standard image-processing teaching idiom: line-buffer load, shift-register window, kernel LUTs, local reductions, muxed boundary handling, dense store (`Lab3.scala:26`, `Lab3.scala:28`, `Lab3.scala:31`, `Lab3.scala:35`, `Lab3.scala:39`, `Lab3.scala:44`, `Lab3.scala:56`, `Lab3.scala:63`, `Lab3.scala:72`, `Lab3.scala:74`).
- Debug prints occur even inside accelerator code (`Lab3.scala:47`, `Lab3.scala:70`), so an EE109-compatible simulator should tolerate staged prints even if an HLS backend later strips or restricts them.
- Private project pattern validation, summarized without code quotations: the user project uses a Python reference simulator, precision policy choices, LUT approximation options, numerical validation thresholds, and unit/integration tests. This supports prioritizing host-side model/test ergonomics in an EE109 rewrite, but it does not add counted Spatial DSL features.

## Features Seen That Are Not Central in the Current Spec Surface

- `SpatialTest` appears in all three examples (`Lab2Part3BasicCondFSM.scala:7`, `Lab2Part4LUT.scala:3`, `Lab3.scala:5`), while the language index names `@spatial` macros rather than `SpatialTest` (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:22`). Treat as harness.
- `runtimeArgs` appears in the LUT lab (`Lab2Part4LUT.scala:4`) but is not called out in the Host and IO or Debugging index entries (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:18`, `10 - Spec/10 - Language Surface/00 - Language Surface Index.md:19`). Treat as harness support unless the source-level spec says otherwise. [UNVERIFIED]
- `sr.reset(c == 0)` appears as user code in convolution (`Lab3.scala:42`). The memory spec describes shared reset hooks and read/write idioms, but the public user-facing `reset` call is not prominent in the syntax block (`10 - Spec/10 - Language Surface/20 - Memories.md:64`, `10 - Spec/10 - Language Surface/20 - Memories.md:66`, `10 - Spec/10 - Language Surface/20 - Memories.md:72`). Confirm MVP status. [UNVERIFIED]
- `Matrix[T]` is used directly in the convolution helper signature (`Lab3.scala:11`). The Host and IO spec covers host `Matrix` (`10 - Spec/10 - Language Surface/60 - Host and IO.md:32`, `10 - Spec/10 - Language Surface/60 - Host and IO.md:45`), but the extraction schema did not list Matrix as a type category. Include it in the MVP subset.
- The raw string interpolator `r"..."` appears in debug prints (`Lab3.scala:47`, `Lab3.scala:70`), and the Language Surface Index lists the `r"..."` interpolator under debugging (`10 - Spec/10 - Language Surface/00 - Language Surface Index.md:19`).

## Open Questions

- GitHub completeness: public EE109 Spatial repositories could not be cloned because the local `gh` CLI could not reach GitHub, and web search did not surface relevant repos. Recheck in a network-enabled environment. [UNVERIFIED]
- Full-Spatial rarity: this note compares EE109 examples against the full spec surface, but it does not compute repo-wide feature frequencies over all Spatial examples. Claims about "rare in full Spatial" are qualitative, not quantitative. [UNVERIFIED]
- `runtimeArgs`: decide whether the rewrite should emulate `SpatialTest.runtimeArgs` or replace it with a normal Python/Rust test harness (`Lab2Part4LUT.scala:4`).
- `RegFile.reset`: decide whether user-facing `reset` is an MVP feature or an internal memory hook exposed through Scala (`Lab3.scala:42`).
- Tensor-constructor syntax: `Lab3.scala` uses `(0::R, 0::C){...}` for host matrices (`Lab3.scala:85`, `Lab3.scala:86`, `Lab3.scala:104`), while the extraction schema names `tabulate`. The rewrite should either preserve this syntax or map it cleanly to host `Matrix.tabulate`.
- Type naming: the user schema says `Bool`, while the Spatial spec uses `Bit` and Scalagen has three-valued `Bool` semantics (`10 - Spec/20 - Semantics/50 - Data Types.md:42`). The rewrite should standardize staged predicate and host Boolean naming.
- Comments versus constructs: `Lab3.scala:72` comments that `sqrt` would be technically correct, but no `sqrt` call appears; this note counts `sqrt` as not found. `Lab2Part3BasicCondFSM.scala:24` comments on a Mux1H test, but no explicit `mux` call appears; this note counts explicit `mux` only in `Lab3.scala:72`.

## Sample Verification Log

- `Lab2Part3BasicCondFSM.scala:15` verified the counted `FSM` controller and state predicate.
- `Lab2Part4LUT.scala:25` verified the counted 3x3 `LUT`.
- `Lab3.scala:39` verified the counted DRAM-to-LineBuffer `load` with `par`.
- `Lab3.scala:56` and `Lab3.scala:57` verified nested `Reduce` use.
- `Lab3.scala:72` verified explicit `mux`, `abs`, arithmetic, and boundary predicate use.
- `Lab3.scala:78` verified `getMatrix`.
- `10 - Spec/10 - Language Surface/40 - Streams and Blackboxes.md:40` verified that blackbox APIs exist in full Spatial even though not found in the EE109 corpus.
