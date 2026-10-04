---
type: design
title: "Course syntax and the compiler that checks it"
project: spatial-python
date: 2026-10-01
status: proposed
adoption_status: proposed
implementation_status: not-implemented
related:
  - "[[PY-E002 - Spatial to Python Syntax Atlas]]"
  - "[[10 - Source Checker and IR Blueprint]]"
  - "[[20 - Numeric Engine Blueprint]]"
  - "[[30 - State Simulator and HLS Blueprint]]"
  - "[[40 - Package and Conformance Blueprint]]"
---

# Course syntax and the compiler that checks it

The lab mappings revealed missing source-level details in the existing architecture. This supplement closes those details and traces the proposed examples into compiler records. It refines the five blueprints; it does not replace their numeric, lifetime or protocol rules. The architecture remains proposed under [[D-28]], and no production compiler is implemented here.

## Architecture derived from the examples

| Step | Concrete responsibility | Example that requires it |
|---|---|---|
| Acquire source | Freeze exact text, module IDs, dependency manifest and source spans; never import the kernel to execute decorators/annotations | Host/kernel separation in Lab 1 |
| Parse and bind | Recognize the closed AST grammar; bind each name to a definition, port, resource, helper or registered operation | `tile[i]`, `r.value`, `fsm(... action=write_state)` |
| Specialize | Substitute explicit Meta values, validate finite capacities, prebind signature shape dependencies | GEMM TM/TN/TK and runtime M/N/K shapes |
| Check meaning | Types, widths, domain bounds, effects, initialization, aliases, helper capture and resource lifetime | FIFO branch, GEMM tails, mapper-local SRAM and convolution history |
| Build checked IR | Immutable compiler-owned Python records with verified tokens, requirements and origin maps; xDSL is an optional derived adapter | Every example retains memories/controllers instead of becoming untyped Python calls |
| Run the reference model | Python numeric engine plus resource state and ordered/communicating continuations | Compare values, queue changes, memory initialization and faults |
| Build a hardware plan | Finite widths, storage, versions, ports, banking, task schedule, transfers, ABI and proof obligations | `.buffer`, `par`, II and streaming requests |
| Emit and validate | Checked implementation plan → HLS/interface code; independent tool and hardware evidence | The course's Part 2 tasks become later validation stages |

The reference simulator and HLS backend consume the same checked meaning. A vendor HLS tool may schedule supported generated code; it does not decide what a Python branch, fixed-point operation, FIFO consume or memory fold means.

## Closed common signatures

This is registration notation, not implementation code. `Index` slots accept structural Index values or the blueprint's checked projection from integral fixed data. `Meta` values are closed data. DefinitionRefs are source definitions, not host callbacks. Keyword expansion, unknown keywords and arbitrary dynamic member lookup reject. Declarative `from spatial.math import abs` and corresponding finite registered math/RNG namespace imports bind frozen intrinsic registrations; they never import or execute a host module. This explicitly extends the source blueprint's import allowlist.

| Registration | Accepted arguments and result |
|---|---|
| `foreach`, `sequential`, `pipe_range` | `(start, end, *, step=1, par=1, ii=None)`; one Index binder. Nonzero step; positive meta par and optional II. `ii` only admitted for pipe scheduling; `sequential` admits only par=1 |
| `pipe` | `(*, ii=None)` region; optional positive meta II |
| `sequential_region`, `parallel`, `stream` | `()` region. Parallel/stream contain only direct distinct named task children |
| `task`, `named` | `(literal_or_meta_name)` region; task must be a direct task-group child |
| `enabled` | `(predicate: Bool)`; only a selected body invokes its operations |
| `fsm` | `(start:S, *, test:(S)->Bool, action:(S)->Unit, next:(S)->S) -> Unit`; registered Bits-capable state |
| `load`, `store` | `(dst, src, *, par=1) -> Unit`; compatible registered memory/view/queue endpoints; memory-to-memory logical shapes agree, queue transfers take their token count from the memory view; positive meta par requests transfer lanes |
| `reg` | `(*, reset: T)` contextual initializer of `Reg[T]`; exact typed reset image |
| `lut` | `(values)` contextual initializer of `Lut[T,*shape]`; nested immutable literal tuples match every extent, leaves are exact contextual T constants, row-major order |
| `line_buffer` | `(*, width:Index)` contextual initializer of `LineBuffer[T,H,MAX_C]`; positive meta H/MAX_C, immutable invocation width with `0 < width <= MAX_C`; logical history shape H×width within bounded H×MAX_C capacity |
| `contribute` | `(fresh_local_memory) -> Contribution[M]`; only a memory mapper's terminal yield, no ordinary return/escape |
| `disjoint` | `(memory_or_view, memory_or_view) -> Bool` requirement predicate, admitted only inside `requires`; empty access regions are disjoint |

`Unit` is added explicitly to the core type prelude. Bare terminal `return` supplies it. `Contribution[M]` is a special mapper result descriptor, not a Bits value, ordinary runtime handle, copyable aggregate or arbitrary public helper return type. `lut`, `contribute` and `disjoint` are explicit registrations; listing a method name in a table alone never authorizes arbitrary signatures.

The `line_buffer` width is captured once from immutable invocation shape ingress or meta data, not an effectful state read. Its generation begins at version zero with no valid history. Padding beyond logical width is inaccessible; backing capacity is distinct from live shape. H×MAX_C accounts for history only: staging, snapshots, initialization maps and admitted versions remain separately accounted by the state/plan blueprint. R014 gives exact replacements for a runtime R/C convolution using active line_out views.

Ordered `Fifo` registers `enq(value:T)->Unit`, `deq()->T`, `peek()->T`, `is_empty()->Bool`, `is_full()->Bool` and `occupancy()->Index`. Status/peek are ordered observations, not compile-time properties; peek checks availability without consuming. Each scalar enqueue/dequeue checks capacity/availability before its mutation. The analogous `Lifo` actions are `push(value:T)` and `pop()`. A memory-to-Fifo load produces one token per memory element in logical order; Fifo-to-memory store consumes that many tokens in order. These transfers use R008's per-item capture/validate/issue/commit protocol and retain a completed prefix on later fault, even for Ordered queues. For example, storing two items from queue `[7]` commits the first item before the second empty-dequeue fault. Whole-batch atomicity belongs only to explicitly registered vector/batch actions. Preflight metadata checks cannot change required effect/fault order. Neither endpoint is an indexed array by implication.

Scalar ports also have explicit access syntax: bare `x` reads an `InOut[T]` cell at its order-token point; `x = expression` writes it, and `x += expression` reads once then evaluates the RHS/operation/write. Bare `x` for `In[T]` reads its immutable ingress value. `Out[T]` permits assignment but not a read or augmented assignment. These rules depend on the resolved port category; they do not permit rebinding an ordinary immutable local. `Reg[T]` retains its explicit `.value` syntax.

For ordered synchronous transfers, evaluate explicit operands in source order and use the state blueprint's endpoint-specific validation, snapshot and commit rules. Equal memory-transfer shapes refer to selected source/destination views; the LineBuffer overload compares the source with its staging-frame shape, not the full H×W history. False method `enable` gates the transition, not effects already performed when evaluating call operands. An enclosing `with enabled(cond):` skips evaluation of the entire body when false. `par` annotates a plan request; it does not change the logical copied values or waive alias checks.

### Reductions

Common domain options are `step=1`, `par=1`, `schedule="foreach"`, `ii=None`. Schedules are the closed set `foreach`, `sequential`, `pipe`; sequential requires par=1 and II is only valid for pipe. A communicating stream wrapper is separate. There is no additional `policy` keyword: the named operation selects the numerical policy. Whole-call enable uses an enclosing `enabled` region.

| Operation | Required and optional arguments, in addition to common domain options | Meaning |
|---|---|---|
| `reduce(start,end,*,body,combine,identity=None,accumulator=None)` | body `(Index)->T`; combine `(T,T)->T` or registered ID; optional Reg[T] publication destination | Lawful typed reduction. Previous register value is not a seed. Empty domain returns the verified identity, otherwise faults before publication |
| `fold(start,end,*,body,combine,seed=...,accumulator=...)` | Exactly one of seed:T or initialized accumulator:Reg[T] | Ordered recurrence; seed included once, or snapshot existing accumulator once. Empty evaluates/snapshots and returns that seed, with no accumulator write/publication |
| `tree_reduce(start,end,*,body,combine,identity=None,empty_result=None,tree="adjacent_pairs")` | At most one identity or empty_result; only registered topology IDs | Ordered leaves, adjacent pairs and carried odd leaf; par cannot change topology. Empty faults if no result declared. Identity must be proved neutral; arbitrary empty_result is never padding permission |
| `mem_reduce(dst,start,end,*,body,combine,identity=None)` | body `(Index)->Contribution[M]`; destination matching element type and selected shape | Does not seed from old destination. Snapshots each mapper result; successful result publishes selected cells |
| `mem_fold(dst,start,end,*,body,combine)` | Same mapper type; selected destination cells must be initialized | Snapshot destination seeds once; map and fold in logical order; publish only on nonempty success. Empty map retains seed reads, with no writes/publication |
| `mem_tree_reduce(dst,start,end,*,body,combine,identity=None,empty_result=None,tree="adjacent_pairs")` | Same leased mapper shape; identity/empty_result exclusivity and topology as scalar tree_reduce | Collect mapper snapshots in logical order, then combine each selected cell using the fixed tree; publish only on success |

`None` denotes compile-time absence here; ellipses in the fold signature denote omitted optional alternatives, not admitted source expressions. A disabled enclosing region evaluates no domain, seed, mapper or combine. A nonempty map over an empty destination still runs mapper effects exactly once per active map index, with no cell accesses/combines/publications. Empty map and disabled operation are different. [[PY-R002 - Numeric and Reduction Semantics]] and the numeric blueprint remain authoritative for fault order, lawful reassociation and destination ownership.

`mem_tree_reduce` supplies a source name for the memory fixed-tree semantics already specified by the numeric blueprint; it is a course-review registry completion, not an original tutorial spelling. Without it, the named-operation policy would leave an existing semantic family inexpressible. Empty-map domain validity is checked even when the destination has zero cells: no identity/empty_result still faults; with an admitted empty result there are no destination cells to publish.

The combine checker admits the numeric blueprint's registered laws: wrapping fixed addition, F=0 wrapping multiplication, fixed min/max, raw bitwise AND/OR/XOR, and Bool all/any/xor. It matches a registered operation certificate or a recognized typed expression; wrapping addition is one example, not the whole law registry. A helper merely named `add`, a flag claiming associativity or a successful sample cannot establish the law. Floating addition and fractional multiplication cannot use the same generic lawful-reduction certificate. An ordered fold or explicit tree can express those computations with its specified evaluation order.

### Windows and initialization

| Resource/operation | Proposed rule |
|---|---|
| `Reg[T]` declaration | Explicit reset image, or registered ZeroImage(T); missing default requires explicit supported reset or a diagnostic |
| `Sram[T,*shape]` declaration | Allocate uninitialized cells in the owning activation; writes/transfers establish initialized regions |
| `RegFile[T,*shape]` declaration | Allocate and initialize the declared reset image, default typed zero, as already specified by R008 |
| `Lut[T,*shape] = lut(...)` | Immutable fully initialized literal image; missing/extra cells or writes reject |
| `LineBuffer[T,H,MAX_W]` declaration | Allocate finite row capacity MAX_W with no published valid row; invocation logical width w satisfies 0 < w <= MAX_W; a bare declaration uses w=MAX_W |
| `load(lb,row)` | Rank-one source is one chronological row of the invocation's logical width w; preflight/snapshot, begin/fill/publish through R008 protocol |
| `load(lb,rows)` | Registered rank-two source S×W is a chronological batch; new history is `take_H(reverse(rows)+old_history)`; publish one new version |
| `sr.reset(*,enable=True)` | Restore the full declared reset image only when enabled |
| `sr[i,:].shift(value,*,enable=True)` | Select one full contiguous row; snapshot the old row, put value at column 0, set column j>0 from old j−1; preserve other rows |

Window operations retain owner generation, capabilities, bounds, initialization and order tokens. In the Lab 3 proposal `0 if i > r else lb[i,c]` selects zero **before** unavailable history is read. Computing `lb[i,c]` eagerly and masking the output later would already have faulted. This is a documented repair of the tutorial's under-specified warm-up behavior, not a claim of exact old simulator parity.

## Trace 1: a tile through the compiler

Take the complete E1 source in [[PY-R012 - Lab1 Syntax and Host Mapping]]. The following are explanatory records, not output from an implemented compiler:

1. Bind `src` and `dst` as separate formal handles with declared read/write capabilities; noalias is not inferred from their names. Bind `scale` as Int. Specialize tile size 16 and shape 32.
2. Build an outer sequential loop over `[0,32)` with step 16 and Index binder `base`. Its two activations own distinct logical `tile_in` and `tile_out` allocations.
3. Build the src view with root identity, offset `base`, length 16 and stride 1. Record `0 ≤ base` and `base+16 ≤ 32`. The induction domain proves both iterations satisfy them.
4. Normalize `load(tile_in, view)` to a typed transfer. Its completion establishes all sixteen input cells initialized. The reference simulator waits for this visibility before proceeding.
5. Build the inner foreach over `[0,16)`. For each active i, read tile_in[i], perform wrapping Int multiplication, then write tile_out[i]. The full-coverage write establishes all output cells initialized. The planner may overlap independent iterations only while preserving required behavior.
6. Normalize store to a transfer from the initialized output tile into the selected dst view. Region exit releases both local backing generations after all dependent work completes.
7. The checked graph carries the loop domains, two memory identities, transfer effects, numeric operation type, initialization certificates and original spans. A pass that changes a domain or view must invalidate the affected proofs.

Reference fixtures use all 32 results and state, not an animation or checksum. Exact src/dst overlap can be safe for this particular tiled algorithm, while some shifted overlap can corrupt later input tiles. The source checker cannot infer universal safety merely from one same-buffer test. Runtime bindings and any requested overlap plan are checked against the actual access regions; unsafe overlap for a promised out-of-place algorithm must be rejected by an explicit requirement or reflected in the stated semantics.

## Trace 2: the GEMM mapper owns a temporary

The outer-product proposal in R013 makes the abstract lifetime problem concrete:

1. Prebind the entire signature before resolving `Dram[...,M,K]`. M/N/K are bounded runtime Index ports; TM/TN/TK/P are explicit meta inputs. Validate nonnegative dimensions, positive finite tile sizes and C disjoint from A/B at prepare time.
2. Derive active extents `nm`, `nn_valid`, `nk`. Full local capacities are fixed; load only active A/B/C rectangles. Initialize inactive destination and contribution cells explicitly to zero. Do not read an off-chip padding cell to manufacture that zero.
3. Closure-convert `outer(k)` into a typed map region capturing A/B tile read capabilities and active extents. It cannot capture the owned C recurrence for arbitrary reads/writes.
4. Each map activation allocates `product`. `contribute(product)` moves its backing root into a ContributionLease. Require compatible shape and initialized selected cells; snapshot the result and retain ownership through its read/combine obligations before release and generation retirement. Early release after a complete snapshot is an optimization requiring equivalent lifetime/effect/fault behavior. Returning raw local SRAM is a lifetime error.
5. `mem_fold` snapshots tile_c's old initialized cells once. It performs contribution k and ordered cell combines before moving to k+1, then publishes only after successful completion. Earlier mapper effects are retained if a later fault occurs.
6. A physical implementation may reuse memory only after the lifetime/visibility proof permits reuse. Introducing three rotating banks without tracking which version a consumer owns is insufficient.

`disjoint` lowers to existing AccessRegion obligations, not numerical pointer comparison. Prepare uses buffer owner/storage identity, byte ranges, strides, dtype and logical views. A proved empty intersection passes, including zero-size views; logical emptiness means a zero extent, not merely a zero-byte element encoding. An unknown overlap result cannot be treated as true. Read-only A and B may alias one another. InOut permission on C does not establish its independence from A/B.

## Trace 3: convolution state survives between iterations

LineBuffer belongs to the kernel activation, not to the row loop body, so history survives across rows. RegFile belongs to that same activation and its reset condition starts a fresh horizontal window for each row. The source converter must preserve those allocation scopes when it outlines helpers or lowers loops.

The row load publishes a new newest-first history version. The column loop resets when c=0, shifts a guarded value into each register row, computes nested scalar reductions from the current window and immutable LUTs, then writes line_out[c]. Store reads line_out only after every selected cell is written. Reordering reset after shift, changing newest-first interpretation, or hoisting a history read out of its guard changes the algorithm even if the shapes still match.

The independent fixture must compare this stateful traversal with direct padded 2-D convolution under the same filter orientation and exact arithmetic. The guide and older CS217 fixture use different image/filter data; they must not be silently combined into a single source claim. R014 records the chosen input and orientation.

## Schedule and storage requests

Use a closed external plan-input record for richer tuning; the source spelling `par=P` or `ii=I` produces the same request records. A separate record avoids inventing unverified receiver methods such as `.buffer()` during semantic capture.

These external records occupy the `plan_requests` field of the closed target descriptor passed to the existing `plan(program, target, binding_contract)` API. They are part of target-plan/cache identity. They do not alter the checked semantic program's hash or bypass the binding contract. The plan resolves and verifies every subject against the specified program identity before using a request.

| Field | Required value |
|---|---|
| `schema` | Registered immutable record tag/version `plan_request/1` |
| `program_identity` | Exact checked program revision/hash |
| `subject` | Stable controller/transfer/resource ID plus original source origin; never a line number alone |
| `kind` | Closed enum `lanes`, `initiation_interval`, `storage_versions`, `bank_layout`, `search_domain` |
| `value` | Kind-specific positive integer, finite candidate tuple, or already defined typed bank-layout descriptor |
| `strength` | `prefer` or `require`; explicit in external records |
| `origin` | Source annotation span or plan-record origin for diagnostics |

Source numeric `par` and `ii` requests default to `prefer`; external records can make them `require`. Explicit task concurrency/protocol obligations remain semantic requirements and cannot be weakened by preference status. A preference may be realized with a different reported resource/schedule value while preserving meaning; an unmet requirement returns a failed plan with reasons. Neither value establishes measured throughput. No silent conflicting duplicate overrides: different values for the same subject/kind require a declared search domain or produce a conflict diagnostic.

For a stop-sensitive effectful loop with semantic admission window W=1, `par=4` cannot authorize four visible iterations in flight. The plan must report any unrealized preference while preserving the same committed effects as `par=1`. A larger explicit admission window is a separate semantic policy and changes semantic identity; it is not inferred from par or II. The advanced-controller slice must register its source form before presenting an extra keyword as accepted syntax.

For the course's buffered C, request `kind=storage_versions`, `value=3`, with its chosen strength. This counts physical version slots; it cannot increase semantic publication credits or alter controller admission. Extra physical slots retain the declared protocol limits. The planner derives live intervals and producer/consumer version dependencies, checks capacity and safe recycling, and records the realized count and any unmet preference. The course's triple-buffer explanation motivates the candidate, not a proof for every transformed loop. Plan changes invalidate affected banking/alias/visibility/schedule certificates and require rechecking before emission.

## Diagnostics that determine the implementation

| Source mistake or unsafe transformation | Required result |
|---|---|
| Execute a kernel function to capture only the branch taken for a sample input | Acquisition design violation; both runtime branches must be represented |
| Treat `x: Sram[...]` as a Python type hint with no allocation | Missing semantic operation; capture must create an owned resource |
| Plain integer truth conversion of Int, mutable Python list, unregistered callback or lambda in a kernel | Surface/type diagnostic with the responsible span |
| Uninitialized SRAM read, early LineBuffer history read | Prove safety or retain an active checked fault; never replace with arbitrary zero |
| Domain step zero; par zero/runtime; incompatible transfer extents | Specialization/check/prepare diagnostic at the relevant boundary |
| Assign structural Index into Int storage without `embed` | Type diagnostic, preserving the distinction between coordinates and hardware arithmetic |
| Use a register's reset as an unstated reduction identity | Rejected normalization; reset, identity and seed are distinct |
| Return temporary memory from an ordinary helper | Lifetime diagnostic; use the admitted contribution ownership transfer only in a mapper |
| Treat different formal memory names as distinct backing storage | Alias checker failure; prepare must use the actual bindings |
| Parallelize effectful FIFO contributions by duplicating or reordering consumes | Reject transformation without a preservation proof; correct sum alone is insufficient |
| Merge float multiply and add without an adopted contraction rule | Numeric-preservation failure |
| A plan cannot meet required II or lacks a valid version-reuse schedule | Failed target plan with constraints; no emitted success artifact |

## Package boundaries and first implementation path

Keep the existing module responsibilities in [[40 - Package and Conformance Blueprint]]: source acquisition/conversion, descriptors, checker, owned IR, numeric engine, state/protocol engine, reference executor, hardware planner, backend and artifacts. The new source registrations belong to the source/type registry; their numeric and state transitions remain in the respective engines. Do not duplicate arithmetic or queue behavior in the AST converter.

The first implementation path is still one complete scalar/tiled program through capture → specialize → check → prepare → simulate, with negative cases and independently derived outputs. Then extend that same representation through FIFO/branch, reductions, memory contributions, FSM and windows. This sequence validates the difficult boundaries before adding an HLS backend. The full-language design and later families remain in scope; the first path is an implementation order, not a redefinition of Spatial as only array arithmetic.

The course studies and [[08 - Course Syntax and Architecture Audit]] provide research acceptance cases. AST parsing, hand calculations, independent host arithmetic and a published document establish limited research evidence. Only an implemented checker/simulator passing those fixtures can establish working Python Spatial support.
