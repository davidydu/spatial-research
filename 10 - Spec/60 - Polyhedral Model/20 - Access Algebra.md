---
type: spec
concept: Access Algebra
source_files:
  - "poly/src/poly/SparseVector.scala:15-65"
  - "poly/src/poly/SparseVectorLike.scala:3-14"
  - "poly/src/poly/SparseConstraint.scala:13-26"
  - "poly/src/poly/SparseMatrix.scala:5-88"
  - "poly/src/poly/ConstraintMatrix.scala:5-54"
  - "poly/src/poly/ConstraintType.scala:3-7"
  - "poly/src/poly/DenseMatrix.scala:3-5"
source_notes:
  - "[[poly-models-dse]]"
hls_status: clean
depends_on:
  - "[[10 - ISL Binding]]"
status: draft
---

# Access Algebra

## Summary

The poly package defines a small affine integer algebra over symbolic keys `K`. `SparseVector[K]` represents an affine expression `a_1*k_1 + ... + a_n*k_n + c`, while `SparseMatrix[K]` represents a vector of affine expressions, usually one per memory dimension (`poly/src/poly/SparseVector.scala:5-16`, `poly/src/poly/SparseMatrix.scala:5-6`). `SparseConstraint[K]` wraps a sparse vector with a constraint type, and `ConstraintMatrix[K]` is the set-valued query object sent to ISL (`poly/src/poly/SparseConstraint.scala:3-14`, `poly/src/poly/ConstraintMatrix.scala:5-13`). The algebra is intentionally sparse until the ISL boundary, where it becomes a dense integer matrix (`poly/src/poly/ConstraintMatrix.scala:30-39`, `poly/src/poly/DenseMatrix.scala:3-5`).

## Syntax or API

All sparse vector-like objects expose `cols`, `c`, optional modulus `m`, `mod = m.getOrElse(0)`, `keys`, and zero-default lookup through `apply(x)` (`poly/src/poly/SparseVectorLike.scala:3-14`). `SparseVector[K]` adds affine operations `unary_-`, `+`, `-`, `map`, `empty`, and `zip`, always preserving or merging `allIters` metadata (`poly/src/poly/SparseVector.scala:30-52`). `asMinConstraint(x)` rewrites `this <= x` as `-this + x >= 0`, while `asMaxConstraint(x)` rewrites `this > x`-style upper bounding as `this - x + c - 1 >= 0`; the direct forms are `asConstraintEqlZero`, `asConstraintGeqZero`, `>==`, and `===` (`poly/src/poly/SparseVector.scala:22-29`).

`SparseConstraint[K]` is a `SparseVectorLike[K]` plus `tp: ConstraintType`, and it supports dense string and dense vector serialization for any chosen key order (`poly/src/poly/SparseConstraint.scala:13-20`). `ConstraintType` is a two-value enum: `GEQ_ZERO` has integer/string value `1`, and `EQL_ZERO` has integer/string value `0` (`poly/src/poly/ConstraintType.scala:3-6`). `ConstraintMatrix[K]` contains a `Set[SparseConstraint[K]]`, can prepend another constraint or another matrix with `::`, can collect domains for all keys through the implicit `ISL`, and can return `.isEmpty` or `.nonEmpty` through that solver (`poly/src/poly/ConstraintMatrix.scala:5-13`, `poly/src/poly/ConstraintMatrix.scala:25-43`).

## Semantics

The core algebra is pointwise affine arithmetic. A `SparseVector` lookup for a missing key is zero, so zipping two vectors computes over the union of their keys and applies the requested integer function to each coefficient and to the constant (`poly/src/poly/SparseVectorLike.scala:11-13`, `poly/src/poly/SparseVector.scala:40-44`). Negation is coefficient-wise negation; addition and subtraction are zips with `_ + _` and `_ - _` (`poly/src/poly/SparseVector.scala:46-48`). A `SparseMatrix` applies the same idea row-wise: `+` and `-` zip corresponding rows, `map` maps rows, and `increment(key, value)` advances the constant of each row by `value * coefficient(key)` without changing coefficients (`poly/src/poly/SparseMatrix.scala:23-39`).

`SparseVector.span(N, B)` computes the residual set of banks an affine expression can address under bank count `N` and block factor `B` (`poly/src/poly/SparseVector.scala:54-64`). For every nonzero coefficient value `v`, it maps `v` into positive mod-`N` space and computes `P_raw = N*B/gcd(N,posV)`, except that a zero coefficient with `B == 1` contributes period `1` (`poly/src/poly/SparseVector.scala:54-58`). It then enumerates all loop combinations through `utils.math.allLoops`, adds the vector constant, reduces modulo `N`, and normalizes negative residues into `[0,N)` (`poly/src/poly/SparseVector.scala:58-60`). If the set covers all banks, the result is `ResidualGenerator(1,0,N)`; if the residues have a modular step size, the result is a strided residual; otherwise it returns an explicit residual set with stride `0` (`poly/src/poly/SparseVector.scala:61-64`).

## Implementation

`SparseMatrix.replaceKeys` rewrites row keys through a map from old key to `(newKey, offset)` and adds the sum of replacement offsets for keys present in that row to the row constant (`poly/src/poly/SparseMatrix.scala:7-14`). `ConstraintMatrix.replaceKeys` performs the same operation over constraints but carries a source TODO that says the author was not sure the offset adjustment is correct for constraints (`poly/src/poly/ConstraintMatrix.scala:15-23`). `SparseMatrix.prependBlankRow` inserts an all-zero vector as the first row; `sliceDims(dims)` selects rows by dimension index (`poly/src/poly/SparseMatrix.scala:16-22`). `SparseMatrix.asConstraintEqlZero` and `asConstraintGeqZero` lift each row to a constraint and gather the set into a `ConstraintMatrix` (`poly/src/poly/SparseMatrix.scala:72-77`).

`SparseMatrix.expand` specializes rows with a nonzero modulus into concrete residual alternatives (`poly/src/poly/SparseMatrix.scala:56-71`). For each modular row, it collects nonzero coefficients, computes a per-coefficient period `row.mod / gcd(row.mod, coeff)`, and either enumerates every residue from `0 until row.mod` if any period equals the modulus or recursively enumerates loop sums with the private `allLoops` helper and reduces them modulo `row.mod` (`poly/src/poly/SparseMatrix.scala:50-63`). Each possible residual becomes `row.empty(i)`, and the private `combs` helper forms the Cartesian product across row options, returning one expanded `SparseMatrix` per concrete row combination (`poly/src/poly/SparseMatrix.scala:46-49`, `poly/src/poly/SparseMatrix.scala:62-71`).

Dense serialization is key-order dependent. `ConstraintMatrix.toDenseString` chooses `this.keys.toSeq`, serializes each row with that key sequence, and emits a header with row count and `keys.size + 3` columns (`poly/src/poly/ConstraintMatrix.scala:30-34`). `ConstraintMatrix.toDenseMatrix` returns `DenseMatrix(denseRows.length, keys.length, denseRows)` even though each row vector includes type, coefficients, modulus, and constant; this mirrors the current code and should be treated as an implementation fact, not a corrected schema (`poly/src/poly/ConstraintMatrix.scala:35-39`, `poly/src/poly/SparseConstraint.scala:18-19`). `DenseMatrix.toString` emits its own header and rows joined by spaces (`poly/src/poly/DenseMatrix.scala:3-5`).

## Interactions

The ISL binding consumes only `ConstraintMatrix.toDenseString` in the implemented path (`poly/src/poly/ISL.scala:143-146`). Access overlap builds matrices by subtracting two `SparseMatrix` values and constraining every row to equality with zero (`poly/src/poly/ISL.scala:159-162`, `poly/src/poly/SparseMatrix.scala:76-77`). Banking uses `SparseVector.span` through `AccessMatrix.bankMuxWidth`, so the residual generator semantics are part of bank conflict and mux-width estimation (`src/spatial/metadata/access/AffineData.scala:73-89`, `poly/src/poly/SparseVector.scala:54-64`).

## HLS notes

This layer transfers cleanly to HLS because it is integer affine algebra and solver serialization, not Chisel-specific hardware emission. The Rust rewrite should preserve sparse storage, zero-default lookup, constraint-type numeric encoding, and key-order dense serialization (`poly/src/poly/SparseVectorLike.scala:11-13`, `poly/src/poly/ConstraintType.scala:3-6`, `poly/src/poly/ConstraintMatrix.scala:30-34`). The only rework candidate is `replaceKeys` offset handling for constraints because the current source carries an explicit uncertainty TODO (`poly/src/poly/ConstraintMatrix.scala:15-20`).

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-03 - 2026-04-24 Constraint replaceKeys offset rule|Q-pmd-03]]
