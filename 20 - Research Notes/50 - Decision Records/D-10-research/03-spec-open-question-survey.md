---
title: D-10 Spec and Open-Question Survey
tags:
  - spatial/research
  - decision-record
---

## Scope

D-10 is framed as the choice of Rust reference precision for transcendental functions: match Scalagen `f64` transcendentals, use per-format MPFR/exact math, or match synthesized hardware units (`20 - Research Notes/40 - Decision Queue.md:47-49`). The corresponding open question, Q-130, identifies the immediate source of ambiguity: `Number.scala` routes transcendental helpers through JVM `Math.*` on `Double`, which is exact enough for `FltFormat(52, 11)`, usually-but-not-formally equivalent for single precision, and lossy for wider formats such as quad (`20 - Research Notes/20 - Open Questions.md:1818-1836`).

## Current Normative Semantics

The strongest existing normative statement is still simulator-first: the Numeric Reference Semantics spec says Scalagen plus `emul` is the bit-level meaning of numeric IR nodes, and that one-line lowerings delegate to the emulator runtime (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:25-29`). Data Types repeats the rule more broadly: when Scalagen disagrees with native Scala, JVM, or hardware expectations, Scalagen wins for simulator behavior and Rust reference parity (`10 - Spec/20 - Semantics/50 - Data Types.md:36-39`).

For D-10 specifically, the implemented reference is `Double` then rewrap/reclamp. Fixed-point `sqrt`, `exp`, `ln`, `log2`, `pow`, trig, hyperbolic, and inverse-trig helpers call `Math.*(x.toDouble)` before constructing a `FixedPoint` in the original format (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:96-114`). Float versions do the same through `FloatPoint(Math.*(x.toDouble), x.fmt).withValid(x.valid)` (`/Users/david/Documents/David_code/spatial/emul/src/emul/Number.scala:139-155`). The Scalagen spec records this directly: every `Number` transcendental routes through `Double`, so accuracy is bounded by IEEE double regardless of source format, and `sigmoid` is defined by composition over `exp` (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:80-84`).

## Open Policy Surface

The open issue is not whether current Scalagen is ambiguous; it is not. The ambiguity is whether Rust+HLS wants Scalagen parity, mathematically stronger format parity, or hardware parity. Q-130 asks for exactly that canonical choice (`20 - Research Notes/20 - Open Questions.md:1831-1836`). The language-surface Math spec adds that public helpers such as `pow`, `abs`, `exp`, `ln`, `sqrt`, trig, and `sigmoid` are only a thin facade over the `Num[A]` typeclass, while Taylor helpers are separate DSL desugarings and should not be conflated with the `Number.*` reference path (`10 - Spec/10 - Language Surface/50 - Math and Helpers.md:69-80`).

## Overlaps

D-01 overlaps because hardware arithmetic is mediated by `BigIP`, whose default contract throws for many optional arithmetic operations including integer `sqrt`, trig/hyperbolics, `log2`, floating `exp`, `tanh`, `sigmoid`, `ln`, reciprocal, `sqrt`, reciprocal-sqrt, FMA, and conversions (`10 - Spec/80 - Runtime and Fringe/50 - BigIP and Arithmetic.md:35-39`). BigIPSim is not a precision reference for all of these: its fixed `sin`, `cos`, `atan`, `sinh`, and `cosh` return the input unchanged with TODOs (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/targets/BigIPSim.scala:82-96`). D-01’s recommendation moves toward HLS-native lowering for many functions, but that answers availability, not whether HLS library numerics define the Rust oracle (`20 - Research Notes/50 - Decision Records/D-01.md:67-76`).

D-18 overlaps downstream: after D-10 produces a real-valued result for `FloatPoint`, `FloatPoint.clamp` performs packing, including the unresolved `x > 1.9` subnormal heuristic (`/Users/david/Documents/David_code/spatial/emul/src/emul/FloatPoint.scala:335-398`). Q-145 asks whether Rust must reproduce that heuristic bit-for-bit or adopt a cleaner algorithm (`20 - Research Notes/20 - Open Questions.md:2065-2075`). D-19 is the sibling precision-policy problem: Scalagen emits FMA as multiply-then-add, while hardware may fuse and preserve extra precision (`20 - Research Notes/20 - Open Questions.md:2078-2088`; `10 - Spec/20 - Semantics/60 - Reduction and Accumulation.md:50-52`).

## Recommendation Implication

Treat D-10 as a reference-oracle decision, not just an implementation detail. If the project prioritizes simulator compatibility, choose Scalagen `f64` plus existing `FloatPoint.clamp`/`FixedPoint` wrapping as the v1 Rust reference, and test that explicitly. MPFR can remain an audit or optional high-precision mode, but making it normative would intentionally diverge from current Scalagen. Hardware-unit parity should only win if D-01 and D-19 also choose hardware/library results as canonical; otherwise it will produce a split-brain simulator where ordinary numeric ops mean Scalagen but transcendentals mean HLS.
