---
type: spec
concept: math-and-helpers
source_files:
  - "src/spatial/lang/api/MathAPI.scala:1-113"
  - "src/spatial/lang/api/MuxAPI.scala:1-34"
  - "src/spatial/lang/api/PriorityDeqAPI.scala:1-107"
  - "src/spatial/lang/api/MiscAPI.scala:1-34"
  - "src/spatial/lang/api/ShuffleAPI.scala:1-13"
  - "src/spatial/lang/Latency.scala:1-11"
  - "src/spatial/node/Mux.scala:1-57"
  - "src/spatial/node/DelayLine.scala:8-12"
  - "src/spatial/node/FIFO.scala:24"
  - "src/spatial/metadata/retiming/package.scala:30-35"
  - "src/spatial/metadata/access/AccessData.scala:43"
  - "src/spatial/metadata/access/package.scala:122-123"
  - "utils/src/utils/math/ReduceTree.scala:1-13"
  - "argon/src/argon/static/Staging.scala:185-192"
source_notes:
  - "[[language-surface]]"
hls_status: clean
depends_on:
  - "[[20 - Memories]]"
  - "[[30 - Primitives]]"
status: draft
---

# Math and Helpers

## Summary

This spec entry collects the per-topic API mixins included in `StaticAPI_Internal` (`src/spatial/lang/api/StaticAPI.scala:7-22`) that an application writer reaches as bare top-level functions: tree reductions, scalar numeric helpers, Taylor approximations, multiplexers, priority/round-robin FIFO dequeuers, and the retiming primitives `retimeGate`, `retime`, and `ForcedLatency`. Most of the surface dispatches 1-1 to argon's `Num` typeclass or to a small set of IR nodes (`Mux`, `OneHotMux`, `PriorityMux`, `FIFOPriorityDeq`, `DelayLine`, `RetimeGate`, `ShuffleCompress`); the Taylor approximations are pure DSL-level desugarings into fixed-point arithmetic.

## Syntax / API

```scala
sum(a, b, c); product(a, b, c)                        // MathAPI.scala:10, 13
reduce(a, b, c){ _+_ }                                // MathAPI.scala:16
xs.reduceTree(f); xs.sumTree; xs.prodTree             // MathAPI.scala:70-72
bits.andTree; bits.orTree                             // MathAPI.scala:76-77

min(a,b); max(a,b); pow(a,b)                          // MathAPI.scala:18-31
abs/ceil/floor/exp/ln/sqrt/sin/cos/tan/.../sigmoid    // MathAPI.scala:33-65

exp_taylor(x); log_taylor(x)                          // MathAPI.scala:81, 88
sin_taylor(x); cos_taylor(x); sqrt_approx(x)          // MathAPI.scala:94, 100, 104

mux(s, a, b)                                          // MuxAPI.scala:10
oneHotMux(sels, vals); priorityMux(sels, vals)        // MuxAPI.scala:26, 30

priorityDeq(f1, f2, f3)                               // PriorityDeqAPI.scala:10
priorityDeq(fifos, conds)                             // PriorityDeqAPI.scala:25
roundRobinDeq(fifos, ens, iter)                       // PriorityDeqAPI.scala:55

retimeGate()                                          // MiscAPI.scala:19
retime(d, payload)                                    // MiscAPI.scala:23
ForcedLatency(latency){ block }                       // src/spatial/lang/Latency.scala:8

val w = *; val v: Void = void                         // MiscAPI.scala:11, 9
compress(tup2)                                        // ShuffleAPI.scala:9
```

## Semantics

### Reductions

`reduce[T](xs: T*)(f)` (`MathAPI.scala:16`) calls `utils.math.ReduceTree(xs:_*)(f)`. `ReduceTree` (`utils/src/utils/math/ReduceTree.scala:5-12`) builds a balanced binary tree of `f` applied pairwise, recursing on halves and dragging an odd-leftover element forward. Tree depth is `ceil(log2(N))`, so the staged result maps to a hardware adder/comparator tree rather than a linear chain. `sum`/`product` (`MathAPI.scala:10-13`) are thin specializations: empty input yields `Num[T].zero`/`Num[T].one`, else delegate to `reduce` with `_+_` or `_*_`. `SeqMathOps` (`MathAPI.scala:69-73`) lifts these onto `Seq[A]` (`xs.reduceTree`/`sumTree`/`prodTree`). `SeqBitOps` (`MathAPI.scala:75-78`) gives `Seq[Bit]` `andTree` and `orTree` shortcuts.

### Scalar numeric helpers

`min`/`max`/`pow`/`abs`/`exp`/`ln`/`sqrt`/trig/`sigmoid` (`MathAPI.scala:18-65`) are a thin façade over `Num[A]`: each unboxes its argument and invokes the typeclass method (`Num[A].abs(a.unbox)`, etc.). The four-overload pattern for binary functions — `(Sym, Sym)`, `(Sym, Literal)`, `(Literal, Sym)`, `(Lift, Lift)` (`MathAPI.scala:18-31`) — lets app code mix staged and Scala literals without explicit lifts. Unary helpers duplicate over `Sym[A]` and `Lift[A]` (`MathAPI.scala:33-48` and `:50-65`).

### Taylor and piecewise approximations

`exp_taylor`, `log_taylor`, `sin_taylor`, `cos_taylor`, `sqrt_approx` (`MathAPI.scala:80-111`) are pure DSL desugarings — no IR node, just expanded arithmetic stitched with `mux`.

- `exp_taylor` (`MathAPI.scala:81-85`) is *piecewise*: `0` below `-3.5`, linear between `-3.5` and `-1.2`, fifth-order Taylor of `e^x` above.
- `log_taylor` (`MathAPI.scala:88-91`) is a single fourth-order Taylor of `ln(x)` around `x=1`. No range guard, so accuracy degrades fast outside `(0, 2]` (Q-lang-02).
- `sin_taylor`/`cos_taylor` (`MathAPI.scala:94-102`) are odd/even truncated Taylor series for `[-π, π]`.
- `sqrt_approx` (`MathAPI.scala:104-111`) is a five-region piecewise fit (third-order Taylor for `x<2`, four linear regions for `[2, 10000]`, slope-only above). Author comment at `MathAPI.scala:105` flags this as a "placeholder for backprop until we implement floats" (Q-lang-03).

### Muxes

`mux(s, a, b)` (`MuxAPI.scala:10-24`) stages a `Mux` IR node (`src/spatial/node/Mux.scala:9`). Like the binary numeric helpers, four overloads handle Bits/Literal mixes; `selfType` recovers `Bits[A]` evidence at the call site (`MuxAPI.scala:11`). `Mux.rewrite` (`Mux.scala:11-16`) applies three peephole rules at staging: `Mux(true, a, _)=a`, `Mux(false, _, b)=b`, `Mux(_, a, a)=a`. This is critical because `mux` underlies `if`/`else` in `@virtualize` blocks — a constant-condition `if` collapses to its arm before any transformer runs.

`oneHotMux(sels, vals)` and `priorityMux(sels, vals)` (`MuxAPI.scala:26-32`) stage `OneHotMux` and `PriorityMux` (`Mux.scala:19, 39`). `OneHotMux.rewrite` warns when more than one literal-true selector is statically detected (`Mux.scala:25-28`); `PriorityMux` does not warn — multi-true is the expected case (lowest-index wins). Both apply `boxBits[A]` to each value.

### priorityDeq and roundRobinDeq

All three forms (`PriorityDeqAPI.scala:10-23, 25-53, 55-106`) share a structure: build per-fifo enable bits, stage one `FIFOPriorityDeq` per fifo (`src/spatial/node/FIFO.scala:24`), combine with `PriorityMux`. The whole thing runs inside `ForcedLatency(0.0){...}` (`PriorityDeqAPI.scala:12, 28, 56`) to pin retiming to zero — the dequeue semantics require all fifos to react to selectors in the same cycle.

The three forms differ in how the per-fifo enable is built:
1. **Variadic** (`PriorityDeqAPI.scala:13-18`). Enable for fifo[i] = AND of `isEmpty` of every prior fifo, so fifo[0] always wins if non-empty.
2. **List form with conds** (`PriorityDeqAPI.scala:31-46`). User provides `cond: List[Bit]` per fifo. Build `deqEnabled = !isEmpty && cond`, then `cumulativeEnabled = deqEnabled.scanLeft(false)(_||_)`, then `shouldDequeue = !cumulativeEnabled && cond` (`PriorityDeqAPI.scala:32-41`). The `scanLeft` builds the prefix-OR vector that gates the current fifo.
3. **`roundRobinDeq`** (`PriorityDeqAPI.scala:55-106`). Priority of fifo[i] = `(iter + i) % N` (`PriorityDeqAPI.scala:71-74`); fifo dequeues if its enable is high and no strictly-lower-priority fifo is enabled (computed lane-by-lane with `Mux(otherIdx<ourPriority, otherEn, false)` and OR-reduced, `PriorityDeqAPI.scala:78-89`).

In all forms, every staged `FIFOPriorityDeq` is tagged `prDeqGrp = fifo.head.toString.hashCode()` (`PriorityDeqAPI.scala:17, 47, 97`). `prDeqGrp` is `PriorityDeqGroup(grp: Int)` (`src/spatial/metadata/access/AccessData.scala:43`), accessed via `sym.prDeqGrp` (`src/spatial/metadata/access/package.scala:122-123`). The hash trick groups all dequeue nodes from one call so `MemoryUnrolling.scala:303-304` can fuse them into one hardware unit. Author's `// TODO: this is probably an unsafe way` (`PriorityDeqAPI.scala:11, 26`) flags the obvious collision risk (Q-lang-01).

### retimeGate, retime, and ForcedLatency

`retimeGate()` (`MiscAPI.scala:19-21`) stages `RetimeGate()` (`src/spatial/node/DelayLine.scala:12`) — a barrier that signals "do not move register stages across this point".

`retime(delay: scala.Int, payload)` (`MiscAPI.scala:23-33`) has three branches: `delay < 0` throws `IllegalArgumentException("Attempted to create a delayline with delay < 0")` at staging time; `delay == 0` returns `payload.unbox` directly with no IR; `delay > 0` stages `DelayLine(delay, payload)` (`DelayLine.scala:8`) and tags the result `userInjectedDelay = true` (`src/spatial/metadata/retiming/package.scala:30-31`) so the retimer cannot rebalance it away.

`ForcedLatency(latency)(block)` (`src/spatial/lang/Latency.scala:7-11`) calls `argon.withFlow("ForcedLatency", x => x.forcedLatency = latency){block}` (`Latency.scala:9`). `withFlow` (`argon/src/argon/static/Staging.scala:185-192`) installs a flow rule that runs every time a symbol is staged inside the block; the rule writes `forcedLatency` metadata onto the resulting Sym (`src/spatial/metadata/retiming/package.scala:33-34`). Save/restore at `Staging.scala:187, 190` makes nesting safe. `fullDelay` (`retiming/package.scala:17-20`) prefers `forcedLatency` over the analyzed `FullDelay`, so `ForcedLatency(0.0){...}` is the standard idiom for "do not retime anything inside this scope" — used by `priorityDeq`/`roundRobinDeq` for exactly this purpose.

### Wildcard, void, TextOps, compress

`MiscAPI` also provides: `void: Void = Void.c` (`MiscAPI.scala:9`); `def * = new Wildcard` (`MiscAPI.scala:11`) — sentinel for `Foreach(*)` and `mem(i, *)` (see `[[30 - Primitives]]`); `implicit class TextOps` (`MiscAPI.scala:13-17`) — adds `t.map(f)` (yields `Tensor1[R]`) and `t.toCharArray` (identity-map yielding `Tensor1[U8]`) onto argon's `Text`. `ShuffleAPI.compress` (`src/spatial/lang/api/ShuffleAPI.scala:9-11`) stages `ShuffleCompress` — vectorized "compact a `(value, valid)` vector by removing entries with `valid=false`".

## Implementation

### Trait dependencies

All traits live under `spatial.lang.api` and are mixed into `StaticAPI_Internal` (`src/spatial/lang/api/StaticAPI.scala:7-22`). `MathAPI` requires `this: Implicits with MuxAPI` (`MathAPI.scala:7`) — needs `mux` for the Taylor expansions plus `boxBits`/`unbox` from `Implicits`. `MuxAPI`/`PriorityDeqAPI`/`ShuffleAPI` require `this: Implicits` only. `MiscAPI` has no self-type — it doesn't depend on the rest of the stack.

### IR-node footprint

Only six families of helpers in this entry produce IR nodes: `mux`/`oneHotMux`/`priorityMux` → `Mux`/`OneHotMux`/`PriorityMux`; `retimeGate` → `RetimeGate`; `retime` → `DelayLine`; `compress` → `ShuffleCompress`; `priorityDeq`/`roundRobinDeq` → `FIFOPriorityDeq` plus `PriorityMux`. Everything else (`sum`, `reduceTree`, `pow`, `exp_taylor`, `void`, `*`, `TextOps.map`) expands into staged primitives via typeclass dispatch or local arithmetic.

## Interactions

- `[[30 - Primitives]]` — `Wildcard` lives there; `MiscAPI.def *` yields one.
- `[[20 - Memories]]` — `priorityDeq`/`roundRobinDeq` operate on `FIFO[T]`; `prDeqGrp` is consumed by `MemoryUnrolling`.
- `[[10 - Controllers]]` — `ForcedLatency` is exposed at `spatial.lang.ForcedLatency` (`src/spatial/lang/Aliases.scala:152`); used to pin retiming inside arbitrary scopes.
- **Retimer pass** — reads `userInjectedDelay`, `forcedLatency`, `prDeqGrp` to decide which delay lines to insert/move and which dequeue nodes to fuse.
- **Codegens** — `Mux`/`OneHotMux`/`PriorityMux` lower to ternary or `Mux(...)` constructors; `DelayLine` becomes a shift register; `RetimeGate` is a no-op outside the retimer; `ShuffleCompress` lowers to a vector compaction primitive.

## HLS notes

`hls_status: clean` for almost everything: tree reductions and scalar typeclass calls map directly to HLS arithmetic; muxes become `?:`; `DelayLine` becomes a shift-register array; Taylor approximations are pure C++. Two corner cases. (1) `priorityDeq`/`roundRobinDeq` use `prDeqGrp` via `String.hashCode()` to fuse dequeue ports — the Rust port should make this an explicit `PriorityDeqGroup(fifos, conds)` IR construct (Q-lang-01). (2) `ForcedLatency` semantics depend on the retimer; the HLS equivalent (`#pragma HLS LATENCY min=N max=N`) is per-construct rather than scoped, but per-construct hints likely suffice since most uses are localized.

## Open questions

- See `[[open-questions-lang-surface]]` Q-lang-01 (`prDeqGrp` hash collision risk), Q-lang-02 (`log_taylor` lacks domain guard), Q-lang-03 (`sqrt_approx` "placeholder until floats" — what is the planned replacement?).
