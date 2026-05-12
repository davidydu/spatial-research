---
title: D-09 Spec and Open-Question Survey
tags:
  - spatial/research
  - decision-record
---

## Scope

D-09 is currently framed as a Rust simulator choice: unbiased rounding should match JVM RNG nondeterminism, use a seedable deterministic RNG, or become deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:43-45`). D-17 repeats the same policy at the canonical-semantics level, asking whether unbiased rounding matches nondeterministic Spatial behavior, becomes seedable, or is replaced by deterministic rounding (`20 - Research Notes/40 - Decision Queue.md:75-77`). The survey below treats D-09 as downstream of D-17, not as a second place to choose the same numeric rule.

## Current Reference Semantics

The spec's strongest reference-semantics statement is that Scalagen plus the `emul` runtime defines the bit-level meaning of Spatial numeric primitives; one-line lowerings such as `FixAdd` delegate to `emul`, so the IR node's meaning is the operator implementation's meaning (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:27`). The data-types spec repeats that Scalagen wins over native Scala, JVM, or hardware expectations for simulator behavior and Rust reference parity (`10 - Spec/20 - Semantics/50 - Data Types.md:38`). That includes three-valued `Bool`, `BigInt` fixed point, `BigDecimal` float storage, and fixed-point rounding modes rather than native machine arithmetic (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:29`).

For ordinary fixed-point arithmetic, the reference is already settled. `+`, `-`, `*`, `/`, `%`, bitwise ops, and comparisons use raw integer payloads and rewrap through `clamped`; multiplication shifts by `fmt.fbits`, division shifts the numerator, and divide-by-zero returns an invalid X value through `valueOrX` (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:51-53`; `10 - Spec/20 - Semantics/50 - Data Types.md:46`). Saturating operators clip through `FixedPoint.saturating`, and ordinary operators wrap through `clamped` (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:41-45`).

## Unbiased Rounding Sites

The unresolved area is specifically `FixedPoint.unbiased`. The implementation expects four extra fractional bits, computes `biased = bits >> 4`, computes a 1/16-granularity remainder, draws `scala.util.Random.nextFloat()`, then rounds away from zero when `rand + remainder >= 1` before clamping or saturating (`/Users/david/Documents/David_code/spatial/emul/src/emul/FixedPoint.scala:232-240`). Scalagen reaches that path through `UnbMul`, `UnbDiv`, `UnbSatMul`, `UnbSatDiv`, `FixToFixUnb`, and `FixToFixUnbSat` (`/Users/david/Documents/David_code/spatial/src/spatial/codegen/scalagen/ScalaGenFixPt.scala:96-114`). The spec records the consequence plainly: unbiased rounding is nondeterministic across runs and can change bit-exact LSBs (`10 - Spec/50 - Code Generation/20 - Scalagen/20 - Numeric Reference Semantics.md:45-47`).

## Open Policy and BigIP Context

Q-118 and Q-144 are the same live policy question in two ledgers. Q-118 asks whether nondeterminism is load-bearing hardware dither or an implementation accident, and offers JVM RNG parity, seedable deterministic RNG, or round-to-nearest-even as candidates (`20 - Research Notes/20 - Open Questions.md:1595-1602`). Q-144 compresses that to the canonical question: match nondeterminism, seed it, or replace it (`20 - Research Notes/20 - Open Questions.md:2057-2062`). The data-types HLS implication also says the Rust simulator must decide whether unbiased rounding remains nondeterministic, becomes seeded, or becomes exact/deterministic; until then, Scalagen matching means nondeterministic random rounding (`10 - Spec/20 - Semantics/50 - Data Types.md:64-70`).

The BigIP/Chisel arithmetic path makes this broader than Rust alone. Chiselgen maps unbiased variants to `Math.mul`/`Math.div`/`Math.fix2fix` with `Unbiased` rounding and either wrapping or saturation (`10 - Spec/50 - Code Generation/10 - Chiselgen/60 - Math and Primitives.md:42-47`). The math template defines `Unbiased` as LFSR-based stochastic rounding, while `fix2fixBox` instantiates a PRNG with a host-random seed when shrinking fractional bits (`/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/RoundingMode.scala:3-8`; `/Users/david/Documents/David_code/spatial/fringe/src/fringe/templates/math/Converter.scala:37-43`). So D-17 should own the cross-backend semantic policy; D-09 should only record simulator implementation consequences after that choice.

## Recommendation Implication

D-09 should avoid duplicating D-17 by becoming a dependent implementation decision: "given D-17's canonical unbiased-rounding policy, how should the Rust simulator expose seeds, reproducibility controls, and conformance tests?" If the queue allows consolidation, mark D-09 as duplicate/blocked-by D-17. If it remains separate, scope it to Rust API/test ergonomics and explicitly defer the normative numeric rule to D-17.
