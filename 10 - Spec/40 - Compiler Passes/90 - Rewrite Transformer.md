---
type: spec
concept: rewrite-transformer
source_files:
  - "src/spatial/transform/RewriteTransformer.scala:25-316"
  - "src/spatial/traversal/RewriteAnalyzer.scala:11-63"
  - "src/spatial/Spatial.scala:215-218"
  - "src/spatial/Spatial.scala:394-398"
  - "src/spatial/Spatial.scala:455-464"
source_notes:
  - "[[pass-pipeline]]"
hls_status: rework
depends_on:
  - "[[60 - Use and Access Analysis]]"
  - "[[B0 - Accum Specialization]]"
status: draft
---

# Rewrite Transformer

## Summary

`RewriteTransformer` is the post-unroll hardware strength-reduction pass: Spatial runs `rewriteAnalyzer`, optional `accumAnalyzer`, `rewriteTransformer`, and then `memoryCleanup` after the post-unroll DCE/retiming-analysis refresh (`src/spatial/Spatial.scala:211-218`). Its late position means it sees unrolled memory/register structure before flattening and binding reshape controllers (`src/spatial/Spatial.scala:209-220`). The pass is hardware-scoped through `AccelTraversal`, enters accelerators and blackboxes specially, and otherwise pattern-matches arithmetic, register writes, reciprocal-square-root, shifts, FMA candidates, and residual metadata patterns in `transform` (`src/spatial/transform/RewriteTransformer.scala:25-26`, `src/spatial/transform/RewriteTransformer.scala:163-167`, `src/spatial/transform/RewriteTransformer.scala:169-313`). The important cross-pass dependency is [[60 - Use and Access Analysis|use/access analysis]] via `RewriteAnalyzer`: it sets `canFuseAsFMA` before mutation because consumers/effects are not reliable while the mutating transformer is rewriting the graph (`src/spatial/traversal/RewriteAnalyzer.scala:11-16`, `src/spatial/traversal/RewriteAnalyzer.scala:39-60`).

## Pass list and roles

`RewriteAnalyzer` recognizes add-of-multiply patterns for fixed and floating point, checks whether the multiply has either a single forward consumer or a specific reduce-consumer pattern, requires `lhs.isInnerReduceOp == mul.isInnerReduceOp`, and writes `lhs.canFuseAsFMA` only when `spatialConfig.fuseAsFMA` and `inHw` are true (`src/spatial/traversal/RewriteAnalyzer.scala:29-37`, `src/spatial/traversal/RewriteAnalyzer.scala:42-58`). The reduce-consumer pattern permits the multiply's other consumer to be a `Mux` that selects between the add result and multiply result, then requires that the mux consumers write the same register, allowing duplicated registers by comparing `originalSym` (`src/spatial/traversal/RewriteAnalyzer.scala:18-24`, `src/spatial/traversal/RewriteAnalyzer.scala:29-36`). `RewriteTransformer` then uses that metadata as a gate for `FixAdd(FixMul(...), add)` and `FltAdd(FltMul(...), add)` rewrites into `FixFMA` and `FltFMA`, with an additional `specializationFuse` guard that allows same-cycle fusion, accumulator-specialization fusion, or explicit `forceFuseFMA` (`src/spatial/transform/RewriteTransformer.scala:28-40`, `src/spatial/transform/RewriteTransformer.scala:263-274`). CLI flags can disable FMA fusion or force it, and can disable mul/mod optimizations or enable Crandall division/modulo (`src/spatial/Spatial.scala:455-464`).

## Algorithms

Constant fixed-point multiplication is rewritten when `inHw`, `optimizeMul`, integral constant `q`, and `isSumOfPow2(abs(q))` hold; `asSumOfPow2` returns two powers and an add/sub direction, and `rewriteMul` emits two smaller `FixMul`s plus a `FixAdd` or `FixSub`, preserving sign by negating both pieces when `q < 0` (`src/spatial/transform/RewriteTransformer.scala:42-53`, `src/spatial/transform/RewriteTransformer.scala:169-171`). Division and modulo by constants use Mersenne/pseudo-Mersenne gates: `FixDiv` requires `optimizeDiv`, integral `q`, `pseudoMersenneC(q) == 1`, and `q < 2^15`, then calls `rewriteDivWithMersenne`, which returns the quotient from `crandallDivMod` (`src/spatial/transform/RewriteTransformer.scala:55-84`, `src/spatial/transform/RewriteTransformer.scala:173-174`). `FixMod` has three paths: Crandall modulo for the same pseudo-Mersenne gate when `useCrandallMod` is on, direct Mersenne modulo when `isMersenne(q)`, and a near-Mersenne `PriorityMux` correction when `withinNOfMersenne(mersenneRadius, q)` succeeds (`src/spatial/transform/RewriteTransformer.scala:86-117`, `src/spatial/transform/RewriteTransformer.scala:176-184`, `src/spatial/Spatial.scala:394-398`). Static counter modulo has a separate path: the pass extracts linear iterator forms from add/sub/mul/FMA expressions, turns statically known modulo into constants or vector constants, and otherwise records `modulus`/`residual` metadata for pow2 and non-pow2 modulo cases (`src/spatial/transform/RewriteTransformer.scala:214-245`). The source implements the staged algorithm as `crandallDivMod`; the software helper `modifiedCrandallSW` is not called by `RewriteTransformer` and is tracked as Q-pp-12 (`src/spatial/transform/RewriteTransformer.scala:55-80`, `src/spatial/transform/RewriteTransformer.scala:82-88`).

Register write-of-mux lowering is exact and local: `RegWrite(reg, Mux(sel, RegRead(reg), b), en)` becomes a `RegWrite(reg, b, en + !sel)`, while `RegWrite(reg, Mux(sel, a, RegRead(reg)), en)` becomes `RegWrite(reg, a, en + sel)` (`src/spatial/transform/RewriteTransformer.scala:187-209`). The helper `writeReg` stages the replacement with flow and transfers data metadata from the original write (`src/spatial/transform/RewriteTransformer.scala:119-122`). Reciprocal-square-root fusion recognizes `FltRecip(FltSqrt(b))` and `FixRecip(FixSqrt(b))`, replacing them with `FltRecipSqrt` or `FixRecipSqrt` (`src/spatial/transform/RewriteTransformer.scala:137-148`, `src/spatial/transform/RewriteTransformer.scala:248-251`). Shift combining folds same-direction fixed shifts but intentionally leaves `SRA` followed by `SLA`, and `SLA` followed by `SRA`, to `super.transform` because the intermediate right shift may have discarded bits (`src/spatial/transform/RewriteTransformer.scala:150-161`, `src/spatial/transform/RewriteTransformer.scala:253-261`).

## Metadata produced/consumed

`RewriteTransformer` consumes `CanFuseFMA` metadata from `RewriteAnalyzer` through `lhs.canFuseAsFMA`, and it consumes `reduceCycle.marker`/`inCycle` when `specializationFuse` decides whether fusion is compatible with accumulator specialization (`src/spatial/transform/RewriteTransformer.scala:33-40`, `src/spatial/traversal/RewriteAnalyzer.scala:42-58`). The pass writes residual metadata on lowered or mirrored arithmetic: static/pow2 modulo results get `modulus` and `residual`, and fixed add/sub/mul/FMA linear forms receive `residual(lin, iter, ofs, mod)` (`src/spatial/transform/RewriteTransformer.scala:214-245`, `src/spatial/transform/RewriteTransformer.scala:276-310`). `transferDataToAllNew` and `transferData` are used on many replacements, so rewritten nodes inherit source metadata where the transformer intentionally creates new hardware nodes (`src/spatial/transform/RewriteTransformer.scala:119-122`, `src/spatial/transform/RewriteTransformer.scala:169-184`, `src/spatial/transform/RewriteTransformer.scala:263-274`).

## Invariants established

After this pass, qualifying constant multiply/divide/modulo arithmetic has been expressed as shifts, adds, masks, and muxes rather than generic multiply/divide/modulo nodes (`src/spatial/transform/RewriteTransformer.scala:42-117`, `src/spatial/transform/RewriteTransformer.scala:169-184`). Register self-mux writes no longer write the previous register value as data; they use the mux select as an enable term (`src/spatial/transform/RewriteTransformer.scala:187-209`). FMA-eligible add/multiply pairs are fused only after the analyzer has proved the local consumer pattern and the transformer has checked cycle/special-accumulator compatibility (`src/spatial/traversal/RewriteAnalyzer.scala:42-58`, `src/spatial/transform/RewriteTransformer.scala:263-274`).

## HLS notes

HLS can usually express pow2 multiply lowering, reciprocal-square-root selection, and write-enable extraction directly, but the exact Crandall/Mersenne lowering and residual metadata flow need an HLS-specific design because Spatial's version is a staged IR rewrite coupled to banking/address residual metadata (`src/spatial/transform/RewriteTransformer.scala:55-117`, `src/spatial/transform/RewriteTransformer.scala:214-245`, `src/spatial/transform/RewriteTransformer.scala:276-310`). Treat FMA fusion as rework rather than a direct pragma pass, because Spatial's legality gate depends on `consumers`, `isInnerReduceOp`, `reduceCycle.marker`, and `inCycle` metadata rather than only expression shape (`src/spatial/traversal/RewriteAnalyzer.scala:29-58`, `src/spatial/transform/RewriteTransformer.scala:28-40`).

## Open questions

Q-pp-12 asks whether the intended spec should describe `modifiedCrandallSW` as a reference model or only `crandallDivMod` as the implemented hardware rewrite, because the transformer source does not call the software helper (`src/spatial/transform/RewriteTransformer.scala:55-88`).
