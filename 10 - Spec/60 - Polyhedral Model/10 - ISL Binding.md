---
type: spec
concept: ISL Binding
source_files:
  - "poly/src/poly/ISL.scala:13-175"
  - "poly/src/poly/ConstraintMatrix.scala:30-39"
  - "poly/src/poly/SparseConstraint.scala:18-23"
  - "src/spatial/metadata/access/AffineData.scala:38-48"
source_notes:
  - "[[poly-models-dse]]"
hls_status: clean
depends_on:
  - "[[20 - Access Algebra]]"
status: draft
---

# ISL Binding

## Summary

`poly.ISL` is Spatial's minimal binding to ISL emptiness queries. It does not expose a general ISL API inside Scala; instead it lazily compiles and launches a small external executable named `emptiness`, sends dense integer constraint matrices over stdin, and reads a one-character result from stdout (`poly/src/poly/ISL.scala:13-18`, `poly/src/poly/ISL.scala:82-103`, `poly/src/poly/ISL.scala:143-152`). The binding is used by banking and access reasoning for "is this integer constraint system empty?" and for address-overlap checks built by equating two sparse affine matrices (`poly/src/poly/ISL.scala:155-162`, `src/spatial/metadata/access/AffineData.scala:38-48`). For a Rust+HLS rewrite, the behavior to preserve is the query boundary and matrix semantics, not the exact subprocess implementation.

## Syntax or API

The trait requires an implementer-provided `domain[K](key: K): ConstraintMatrix[K]`; `ConstraintMatrix.andDomain` calls this for every key before emitting the final query (`poly/src/poly/ISL.scala:134-135`, `poly/src/poly/ConstraintMatrix.scala:11-28`). It exposes `startup()` and `shutdown(wait)` as explicit lifecycle hooks around a private lazy `BackgroundProcess` (`poly/src/poly/ISL.scala:117-131`). The implemented query methods are `isEmpty(SparseConstraint)`, `isEmpty(ConstraintMatrix)`, `nonEmpty(SparseConstraint)`, and `nonEmpty(ConstraintMatrix)`; the single-constraint variants wrap the constraint in a one-row `ConstraintMatrix` (`poly/src/poly/ISL.scala:137-143`).

`overlapsAddress(a, b)` is implemented by subtracting two `SparseMatrix` values, constraining the result to equality with zero, conjoining all symbolic domains, and checking that the resulting set is non-empty (`poly/src/poly/ISL.scala:155-162`). `isSuperset(a, b)` and `intersects(a, b)` are not implemented: `isSuperset` returns `false`, while `intersects` returns `true`, and both carry TODO comments that say they are used for reaching write calculation (`poly/src/poly/ISL.scala:164-174`). `AccessMatrix.overlapsAddress`, `AccessMatrix.isSuperset`, and `AccessMatrix.intersects` are thin delegations to these trait methods (`src/spatial/metadata/access/AffineData.scala:38-48`).

## Semantics

The wire format is a dense integer matrix. `ConstraintMatrix.toDenseString` chooses the current key order, serializes every row through `SparseConstraint.toDenseString(keys)`, and prefixes the payload with `"<nRows> <nCols>\n"` where `nCols = keys.size + 3` for constraint type, key coefficients, modulus, and constant (`poly/src/poly/ConstraintMatrix.scala:30-34`, `poly/src/poly/SparseConstraint.scala:18-19`). A serialized row is `"$tp <coefficients> $mod $c"`; the only supported constraint types serialize as `GEQ_ZERO -> "1"` and `EQL_ZERO -> "0"` (`poly/src/poly/SparseConstraint.scala:18-19`, `poly/src/poly/ConstraintType.scala:3-6`). The matrix form deliberately includes `mod`, but both `SparseConstraint` and `SparseVector` currently expose `m = None`, so their `mod` field is zero unless another subtype is introduced (`poly/src/poly/SparseConstraint.scala:13-18`, `poly/src/poly/SparseVectorLike.scala:7-10`).

`isEmpty` sends the matrix string to the subprocess and blocks for a character. The response character `'0'` means the system is empty, `'1'` means it is non-empty, and any other character throws `"Failed isEmpty check"` (`poly/src/poly/ISL.scala:143-152`). `nonEmpty` is purely logical negation of `isEmpty`, not a separate protocol command (`poly/src/poly/ISL.scala:137-142`). This means all higher-level emptiness behavior depends on preserving the exact dense matrix convention, the domain-conjoining convention, and the `'0'`/`'1'` polarity.

## Implementation

The first access to `proc` creates `$HOME/bin` if needed, derives `$HOME/bin/emptiness` and `$HOME/bin/emptiness.lock`, and warns if `whereis libisl` appears not to find libisl (`poly/src/poly/ISL.scala:14-34`). Compilation is guarded by a Java `FileLock` on the lock path; the code opens or creates the lock file, then spin-waits until `channel.lock()` succeeds, swallowing `OverlappingFileLockException` during the spin (`poly/src/poly/ISL.scala:36-53`). The lock only protects compilation of the binary, not calls to the running subprocess (`poly/src/poly/ISL.scala:45-53`, `poly/src/poly/ISL.scala:106-117`).

The source for the executable is loaded as a classpath resource named `emptiness.c`; failure to load that resource throws `"Could not get emptiness.c source code"` (`poly/src/poly/ISL.scala:55-62`). If an executable already exists, Spatial runs `$HOME/bin/emptiness -version`, extracts `Version: d.f`, extracts `float version = d.f` from the C source, and recompiles whenever those numbers differ (`poly/src/poly/ISL.scala:64-79`). Recompilation shells out to `pkg-config --cflags --libs isl`, splits the returned flags, and starts `${CC:-gcc} -xc -o $HOME/bin/emptiness -`, sending the C source on stdin (`poly/src/poly/ISL.scala:82-103`). After successful compile or version check, the file lock and channel are released and the lazy value returns `BackgroundProcess("", emptiness_bin)` (`poly/src/poly/ISL.scala:106-117`).

Within one `ISL` instance, the subprocess is a singleton because `proc` is a private lazy value and `init()` starts it only while `needsInit` is true (`poly/src/poly/ISL.scala:14-15`, `poly/src/poly/ISL.scala:119-126`). This is a process-level caveat rather than an OS-wide service: multiple JVMs synchronize binary compilation through the lock, but each `ISL` instance can own its own `BackgroundProcess` after the binary exists (`poly/src/poly/ISL.scala:23-27`, `poly/src/poly/ISL.scala:117-126`). The query protocol itself is also serialized through that one process because `isEmpty` writes to `proc` and immediately blocks for one response char (`poly/src/poly/ISL.scala:143-152`).

## Interactions

The principal visible caller is `AccessMatrix`, which routes overlap, superset, and intersection questions to the implicit `ISL` instance (`src/spatial/metadata/access/AffineData.scala:38-48`). The banking search creates equality or inequality `ConstraintMatrix` objects and calls `.andDomain.isEmpty`, so query correctness depends on domains attached to every symbolic key and on `ConstraintMatrix.domain` folding all per-key domains into the matrix (`poly/src/poly/ConstraintMatrix.scala:11-28`). Because `isSuperset` and `intersects` are stubbed, any caller expecting precise set containment or precise set intersection does not get it today (`poly/src/poly/ISL.scala:164-174`). The spec should therefore treat only `isEmpty`, `nonEmpty`, and `overlapsAddress` as implemented behavior.

## HLS notes

The binding design is clean for HLS if the rewrite keeps a polyhedral solver boundary and dense integer matrix contract. A Rust implementation could embed ISL, call another solver, or retain an external worker, as long as `ConstraintMatrix.toDenseString` semantics, domain conjoining, and the `'0'`/`'1'` interpretation are preserved (`poly/src/poly/ConstraintMatrix.scala:30-34`, `poly/src/poly/ISL.scala:143-152`). The subprocess lifecycle and `$HOME/bin` cache are not conceptually required for HLS; they are Scala/JVM packaging choices (`poly/src/poly/ISL.scala:14-27`, `poly/src/poly/ISL.scala:82-117`).

## Open questions

- [[open-questions-poly-models-dse#Q-pmd-01 - 2026-04-24 ISL set-containment semantics|Q-pmd-01]]
- [[open-questions-poly-models-dse#Q-pmd-02 - 2026-04-24 External solver packaging boundary|Q-pmd-02]]
