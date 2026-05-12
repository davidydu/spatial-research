---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# Polyhedral Model — Index

Integer-set-library (ISL) binding and polyhedral-analysis primitives used by Spatial's access analysis and banking.

## Sections

- `10 - ISL Binding.md` — `ISL` wrapper, context lifecycle, set/map operations, JNI/native-library plumbing.
- `20 - Access Algebra.md` — `SparseMatrix`, `SparseVector`, `SparseConstraint`, `ConstraintMatrix`, `AffineComponent`, the affine-unapply mechanism.
- `30 - Banking Math.md` — How polyhedral matrices feed banking: `AccessMatrix` construction, banking view enumeration, viable `(α, N, B)` tuple search.

## Source

- `poly/src/` (8 files)
- [[poly-models-dse-coverage]] — Phase 1 coverage note
