---
type: "research"
decision: "D-26"
angle: "3"
discriminates: surface-embedding
sources:
  - "spatial-rs@eb49d8b:docs/language-spec.md:987-1028"
  - "spatial-rs@eb49d8b:docs/language-spec.md:1069-1107"
  - "spatial-rs@eb49d8b:docs/language-spec.md:769-791"
  - "spatial-rs@eb49d8b:docs/language-spec.md:158-167"
  - "spatial-rs@eb49d8b:docs/language-spec.md:263-348"
  - "spatial-rs@eb49d8b:docs/language-spec.md:863-878"
  - "spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:88-118"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:34-67"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/tiled1d.rs:570-581"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/reductions.rs:142-162"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/scalar.rs:425-434"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/common.rs:78-91"
  - "spatial-rs@eb49d8b:examples/ee109/src/lib.rs:20-34"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29"
  - "spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-59"
  - "spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:11-33"
  - "spatial@e7a8f2f:test/spatial/tests/feature/dense/MatMult_systolic.scala:77-83"
  - "spatial@e7a8f2f:src/spatial/traversal/UserSanityChecks.scala:64-78"
  - "spatial@e7a8f2f:src/spatial/lang/api/SpatialVirtualization.scala:50-63"
  - "spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaTensor.scala:17-47"
  - "spatial@e7a8f2f:src/spatial/lang/DRAM.scala:90-104"
  - "spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87"
  - "spatial@e7a8f2f:src/spatial/traversal/CompilerSanityChecks.scala:54-65"
  - "exo@defe172:src/exo/rewrite/LoopIR_scheduling.py:286-301"
  - "exo@defe172:src/exo/API_scheduling.py:1696-1742"
  - "exo@defe172:src/exo/API.py:157-171"
  - "exo@defe172:src/exo/frontend/pyparser.py:1497-1511"
  - "exo@defe172:src/exo/frontend/boundscheck.py:818-840"
  - "exo@defe172:src/exo/libs/memories.py:85-112"
  - "allo@094ab41:allo/ir/builder.py:547-581"
  - "allo@094ab41:tests/test_types.py:65-81"
verified: ["2026-09-28"]
status: draft
---
## Scope

Eight registered mistakes, checked on 2026-09-28 (18:22 PDT), plus three canonical lab translations, five valid variants, and controls. Private-course confirmation remains pending; no private course repositories were accessed. This is a diagnostic reachability study, not a learner experiment or a core-language benchmark. Rust HEAD is `eb49d8b`; Scala HEAD is `e7a8f2f`, correcting the prompt's conflicting citation shorthand.

## Findings

### Measurement contract

[measured] Every external fixture ran through `cargo run -q -p spatial-rs-cli -- check` with SDKROOT set; accepted checks produced empty stdout/stderr. Full programs and exact fixture-relative binary transcripts appear below; binary results match Cargo results. The CLI calls `compile_source` and maps diagnostics to exit 1 (`spatial-rs@eb49d8b:crates/spatial-rs-cli/src/lib.rs:88-118`).

[designed] M1 uses full tiles without tail handling; M2 requests unmasked groups; M8 uses unconstrained input indices. M3 uses a nonliteral Int, avoiding contextual literal conversion. These qualifications make the intended obligations meaningful. Legacy spellings maximize reachability; supplementary canonical probes reveal syntax barriers. M7 models an untransferred host name as an undeclared identifier, not implemented Python capture.

[precedent-measured] Exo runs in an isolated Python 3.12.7 environment with PySMT 0.9.6, z3-solver 4.15.4.0 and `PYSMT_CYTHON=0`. P1/P2 exercise perfect loop division, P4 a Gemmini scratchpad, P5 DRAM assignment, P6 accumulation, P7 capture, and P8 a read-only table buffer. These are analogous obligations, not identical hardware constructs; Exo has no Spatial `par` or `requires` spelling (`exo@defe172:src/exo/API_scheduling.py:1696-1718`, `exo@defe172:src/exo/libs/memories.py:85-112`).

### Eight mistakes

| Mistake | External-DSL code + exit | Python precedent + message | Scala message | Earliest catch | Actionable? |
| --- | --- | --- | --- | --- | --- |
| 1. Tile bound not dividing extent | [designed] M1: N=30, TILE=16, full load/store. [measured] Exit 1, E0403: `N=30 is not a multiple of TILE=16`. | [precedent-measured] P1: `divide_loop(...,16,perfect=True)` raises `cannot perfectly divide '30' by 16`. | [precedent-measured] S1 source: `M must be divisible by $outerTile`; explicit application assertion, not automatic compiler checking. | [judgment] External check; Exo schedule check; Scala assertion runs only if written. | [judgment] Both measured messages name incompatible sizes. External help unnecessarily prescribes the old fixed adapter. |
| 2. Par not dividing range | [designed] M2: N=16, P=3. [measured] Exit 1, E0408: `parallelism equal to 1`. | [precedent-measured] P2 perfect split into three lanes before unrolling: `cannot perfectly divide '16' by 3`. | [precedent-measured] S2 has only a warning when par exceeds length; no matching divisibility diagnostic located. | [judgment] External check is incidental subset rejection; Exo schedule check reaches divisibility; Scala unknown. | [judgment] Exo explains the obligation; external teaches P=1 instead. |
| 3. Int used where FixPt required | [designed] M3: Int inputs assigned to fixed output. [measured] Legacy type: exit 1 E0001 `unsupported source form`; canonical type: E0002 `expected [` . | [precedent-measured] Allo source supports Int-to-Fixed conversion; no mismatch message established. P3 runtime unavailable: `No module named 'allo._mlir'`. | [precedent-measured] S3 template: `Type mismatch: Cannot assign ${data.tp} to var of type ${v.A}`; source-only, variable assignment path. | [judgment] External classifier/parser masks typing; Allo conversion policy differs; Scala template is a staged check, exact fixture untested. | [judgment] Scala template explains both types. External advice to add a parser case is unsuitable for a first-year student. |
| 4. SRAM read before load | [designed] M4 removes the dense control's load. [measured] Exit 1 E0002 `expected load`. | [precedent-measured] P4: `scratch: i8[16,16] @ GEMM_SCRATCH; out[0]=scratch[0,0]` accepts at `@proc`, empty stderr. | [precedent-measured] S4 executor initializes cells to `None`; no matching first-read message located. | [judgment] External parse, not definite-assignment proof; Exo silent through frontend checking; later backend unknown. | [judgment] External suggests a useful repair here, but gives no missing-initialization explanation. |
| 5. DRAM written directly inside loop instead of store | [designed] M5: `dst[r,c] := src[r,c]`. [measured] Exit 0, empty stderr. | [precedent-measured] P5 direct DRAM loop assignment accepts, empty stderr. | [precedent-measured] S5 exposes `store`; no exact scalar-assignment diagnostic located. | [judgment] No intended error exists under the external specification; Python also accepts this representation. | [judgment] Acceptance is appropriate; imposing the registered prohibition would reject legal external code. |
| 6. Reduce without init | [designed] M6: `reduce i in 0..N par P { i }`. [measured] Legacy form accepts; canonical `using +` without init rejects E0002 `expected {`; corrected init also rejects. | [precedent-measured] P6 uninitialized `total += a[i]` accepts at `@proc`, empty stderr; accumulator analogue, not identical reduce syntax. | [precedent-measured] S6 `ReduceClass` explicitly permits an implicit accumulator with absent identity/init. | [judgment] External canonical parse cannot distinguish correction; legacy acceptance is intentional compatibility. Exo frontend silent; Scala omission is supported. | [judgment] No useful missing-init diagnostic measured; do not classify Scala's supported construct as an error. |
| 7. Host/Python value used inside accelerator body | [designed] M7: `out := a + python_x`. [measured] Exit 1 E0401 `scalar expression reads an unknown value`. | [precedent-measured] P7 string capture: `Unquote received input that couldn't be unquoted`; integer capture control accepts. | [precedent-measured] S7: `One or more values were defined on the host but used in Accel without explicit transfer.` | [judgment] External name-like classifier check; Exo decorator parse; Scala compiler sanity check. | [judgment] External names the site; Scala explains transfer. Exo's “Unquote” requires terminology help. Host constants are not universally mistakes. |
| 8. LUT index without requires bound | [designed] M8: `lut[i,j]`, unconstrained input indices. [measured] Exit 0; added requires control rejects E0002. | [precedent-measured] P8 table read rejects: `lut is read out-of-bounds when: ... index_value = -1`; bounded control accepts. | [precedent-measured] S8 tensor executor template: `Index $index was out of bounds, shape was $shape`; no static requires diagnostic located. | [judgment] Exo checks at decoration; external silent at check; Scala cited path is run-time bounds defense. | [judgment] Exo's concrete counterexample gives a repair target; runtime bounds text helps only after execution. |

[precedent-measured] S1–S8 exact source anchors and limitations are recorded below; all Scala evidence is source inspection, never an sbt run. Allo's cast map is `allo@094ab41:allo/ir/builder.py:547-581`; its index/fixed conversion test is `allo@094ab41:tests/test_types.py:65-81`.

### Reachability and false rejections

[precedent-measured] The specification permits indexed writable DRAM (`spatial-rs@eb49d8b:docs/language-spec.md:777-791`), explicitly requires reduction init (`spatial-rs@eb49d8b:docs/language-spec.md:164-167`), and distinguishes legacy diagnostics from canonical E0311–E0315 (`spatial-rs@eb49d8b:docs/language-spec.md:1010-1023`). Its implementation-status table already marks canonical FixPt, reductions and requires incomplete (`spatial-rs@eb49d8b:docs/language-spec.md:1076-1107`).

[measured] None of E0311, E0312, E0313, E0314 or E0315 appeared. M1 reaches divisibility; M7 reaches unknown-name rejection. M2 does not isolate divisibility: dividing P=2 also receives E0408. M3 masks typing and M4 enforces parser shape. M5 is a valid control, M6 legacy acceptance follows a different grammar, and M8 remains an unchecked-bound acceptance. This does not yield an honest single “errors caught” percentage.

[designed] The three fixed translations are L1 dense DRAM/SRAM scaling, L2 tiled scalar folding, and L3 fixed-point GEMM with memfold. L3 specializes dimensions to 32 and tiles to 16, preserving the fixed fixture's full-tile case. Before running, variants were fixed as: V1 L1 kernel rename; V2 L2 local rename; V3 L1 tile 16→8; V4 L3 independent constant reordering; V5 L2 comment insertion. Full constructions and source anchors follow.

| Canonical input | Result |
| --- | --- |
| L1; V1; V3 | [measured] 3/3 reject E0002, `expected :=` at unsupported `seq foreach`. |
| L2; V2; V5 | [measured] 3/3 reject E0002, `expected {` at `init`. |
| L3; V4 | [measured] 2/2 reject E0002, `expected [` at canonical FixPt syntax. |
| Separate legacy controls C1/C2/C3 | [measured] 3/3 accept; they are not substitutes for the canonical labs. |

[judgment] These eight valid canonical inputs are false rejections against the specification, not evidence that tile arithmetic, proof rules, or Python embedding inherently fail. Repeating known parser barriers across variants establishes current reachability, not broad semantic robustness. The compiler sequence confirms parse precedes classification (`spatial-rs@eb49d8b:crates/spatial-rs-core/src/compiler.rs:34-67`).

## Implications

### R-X

Current external diagnostics need canonical syntax and general obligation checks before educational superiority can be claimed. Retain explicit preconditions and source spans as a design target.

### R-E

A Python surface can check before execution, as Exo demonstrates. Bindings do not automatically reproduce those checks or their messages; define capture and conversion rules explicitly.

### R-B

Use one obligation suite for both surfaces, including valid controls and retained source locations. Surface parity cannot be assessed from the existing adapter acceptance alone.

### P-X

This study offers no evidence that Python implementation language prevents precise diagnostics. The parser/classifier gaps are implementation gaps, not a measured Rust-versus-Python result.

### P-E

Early Python AST checks are credible, but initialization and host-value boundaries need explicit semantics. A familiar syntax does not ensure familiar diagnostic vocabulary.

### P-B

The same parity requirement applies. No measured result here chooses a core language or integration depth I0/I1/I1′/I2/In.

## Evidence against

My modest leaning is toward an external surface's explicit accelerator boundary and precondition vocabulary. The strongest counterevidence is Exo's successful missing-bound rejection with a counterexample while the current external checker accepts the unbounded LUT and rejects its repair. All eight valid canonical lab/variant inputs also reject. Conversely, Exo accepts the uninitialized examples at its frontend; those observations do not establish safety through code generation. Surface choice alone explains neither result.

## Open questions

Private-course confirmation of the fixed mistake list is still pending. Resolve row 5's conflict without retroactively relabeling this run. Clarify whether row 7 means runtime host data or permitted elaboration constants. Repeat after canonical parsing/checking lands; obtain actual Scala compile messages where source inspection was inconclusive, and test Allo when its native module is available. Measure novice repair success and time independently; actionability here is judgment.

## Confidence

medium — high confidence in recorded external/Exo frontend results and opened source text; limited cross-language equivalence, no Scala execution, unavailable Allo runtime, and no learner observations.

## Transcripts

### Reproduction and path convention

Measured 2026-09-28. Rust checks ran from the pinned spatial-rs checkout with SDKROOT pointing to the Command Line Tools macOS SDK; reproduce this setting with `SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"`. Every fixture first used `cargo run -q -p spatial-rs-cli -- check <relative-fixture-path>`. For exact short relative-path stderr below, every fixture was also checked from its fixture directory with the identical Cargo-built `spatial-rs/target/debug/spatial-rs` binary (SHA-256 `73cabf0e77937a2b4294316010b9c457b6a01cc4f74a4d0a71add42c542c883a`). `$SPATIAL_RS` denotes that binary. All exit codes, stdout and stderr match after replacing only the input-path prefix. `(empty)` is a transcript annotation for zero output bytes, not emitted text.

The complete canonical translations were constructed from `spatial@e7a8f2f:test/spatial/tests/ee109/Lab1Part2DramSramExample.scala:11-33`, `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab1_part6_reduce.scala:15-29`, and `spatial-rs@eb49d8b:crates/spatial-rs-core/testdata/ee109/lab2_part6_gemm_fixed_32.scala:29-59`, using the opened canonical syntax examples in `spatial-rs@eb49d8b:docs/language-spec.md:263-348`. These are constructed translations, not files asserted to compile in the current implementation. Legacy dense control syntax follows `spatial-rs@eb49d8b:examples/ee109/src/lib.rs:20-34`.

The emitting source for M1 is `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/tiled1d.rs:570-581`; M2 is `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/reductions.rs:142-162`; M3 fallback is `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/common.rs:78-91`; M7 is `spatial-rs@eb49d8b:crates/spatial-rs-core/src/classifier/scalar.rs:425-434`.

### C1-scalar

[designed] Complete external fixture.

```spatial
kernel ScalarControl {
  inputs { a: Int, b: Int }
  outputs { out: Int }
  out := a + b;
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C1-scalar.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### C2-dense

[designed] Complete external fixture.

```spatial
kernel DenseControl {
  const N: usize = 32;
  const TILE: usize = 16;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  sequential_foreach base in 0..N step TILE {
    let a = Sram<Int>[TILE];
    load a <- src[base..base + TILE];
    let b = Sram<Int>[TILE];
    foreach lane in 0..TILE { b[lane] := a[lane] * x; }
    store dst[base..base + TILE] <- b;
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C2-dense.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### M1-tile

[designed] Complete external fixture.

```spatial
kernel DenseControl {
  const N: usize = 30;
  const TILE: usize = 16;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  sequential_foreach base in 0..N step TILE {
    let a = Sram<Int>[TILE];
    load a <- src[base..base + TILE];
    let b = Sram<Int>[TILE];
    foreach lane in 0..TILE { b[lane] := a[lane] * x; }
    store dst[base..base + TILE] <- b;
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M1-tile.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0403]: dense DRAM/SRAM program is outside the accepted adapter shape
  --> M1-tile.spatial:1:1
   = dense feature requires a positive N that is a multiple of TILE, but N=30 is not a multiple of TILE=16
   = help: use the fixed N=32, TILE=16 dense adapter until dense memory lowering is generalized
```

### M2-par

[designed] Complete external fixture.

```spatial
kernel ParMistake {
  const N: usize = 16;
  const P: usize = 3;
  outputs { out: Int }
  out := reduce i in 0..N par P { i };
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M2-par.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0408]: scalar reduction is outside the supported ScalarReduce v0 subset
  --> M2-par.spatial:1:1
   = scalar reduce v0 requires 1 <= length <= 65536 and parallelism equal to 1
   = help: use one scalar Int output and `out := reduce i in 0..N par P { i }` with 1 <= N <= 65536 and P equal to 1
```

### C3-par

[designed] Complete external fixture.

```spatial
kernel ParMistake {
  const N: usize = 16;
  const P: usize = 1;
  outputs { out: Int }
  out := reduce i in 0..N par P { i };
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C3-par.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### M3-type

[designed] Complete external fixture.

```spatial
kernel TypeMistake {
  inputs { a: Int, b: Int }
  outputs { out: FixPt[TRUE,_24,_8] }
  out := a + b;
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M3-type.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0001]: program is outside the accepted EE109 adapter grammar
  --> M3-type.spatial:1:1
   = unsupported source form
   = help: use one of the accepted canonical EE109 forms or add a new parser case intentionally
```

### M3-canonical

[designed] Complete external fixture.

```spatial
kernel TypeMistake {
  inputs { a: Int, b: Int }
  outputs { out: FixPt<Signed,24,8> }
  out := a + b;
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M3-canonical.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> M3-canonical.spatial:3:23
   = expected `[`
   = help: use the currently accepted scalar or LUT subset syntax
```

### M4-uninit

[designed] Complete external fixture.

```spatial
kernel DenseControl {
  const N: usize = 32;
  const TILE: usize = 16;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  sequential_foreach base in 0..N step TILE {
    let a = Sram<Int>[TILE];
    let b = Sram<Int>[TILE];
    foreach lane in 0..TILE { b[lane] := a[lane] * x; }
    store dst[base..base + TILE] <- b;
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M4-uninit.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> M4-uninit.spatial:8:5
   = expected `load`
   = help: use the currently accepted scalar or LUT subset syntax
```

### M5-dram

[designed] Complete external fixture.

```spatial
kernel DirectDram {
  const ROWS: usize = 2;
  const COLS: usize = 2;
  inputs { src: Dram<Int>[ROWS, COLS] }
  outputs { dst: Dram<Int>[ROWS, COLS] }
  foreach r in 0..ROWS {
    foreach c in 0..COLS { dst[r,c] := src[r,c]; }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M5-dram.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### M6-no-init

[designed] Complete external fixture.

```spatial
kernel ParMistake {
  const N: usize = 16;
  const P: usize = 1;
  outputs { out: Int }
  out := reduce i in 0..N par P { i };
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M6-no-init.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### M6-canonical

[designed] Complete external fixture.

```spatial
kernel MissingInit {
  const N: Size = 16;
  const P: Size = 1;
  outputs { out: Int }
  accel { out := reduce i in 0..N par P using + { yield i; }; }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M6-canonical.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> M6-canonical.spatial:5:41
   = expected `{`
   = help: use the currently accepted scalar or LUT subset syntax
```

### C4-init

[designed] Complete external fixture.

```spatial
kernel MissingInit {
  const N: Size = 16;
  const P: Size = 1;
  outputs { out: Int }
  accel { out := reduce i in 0..N par P init 0 using + { yield i; }; }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C4-init.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> C4-init.spatial:5:41
   = expected `{`
   = help: use the currently accepted scalar or LUT subset syntax
```

### M7-host

[designed] Complete external fixture.

```spatial
kernel ScalarControl {
  inputs { a: Int, b: Int }
  outputs { out: Int }
  out := a + python_x;
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M7-host.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0401]: scalar expression reads an unknown value
  --> M7-host.spatial:4:14
   = unknown scalar read
   = help: read only declared scalar inputs in the scalar expression subset
```

### M8-lut

[designed] Complete external fixture.

```spatial
kernel UnboundedLut {
  const ROWS: usize = 2;
  const COLS: usize = 2;
  inputs { input: Int, i: Int, j: Int }
  outputs { out: Int }
  let lut = Lut<Int>[ROWS, COLS] = [[1,2],[3,4]];
  out := input + lut[i,j];
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check M8-lut.spatial
exit: 0
stdout: (empty)
stderr:
(empty)
```

### C5-requires

[designed] Complete external fixture.

```spatial
kernel UnboundedLut {
  const ROWS: usize = 2;
  const COLS: usize = 2;
  inputs { input: Int, i: Int, j: Int }
  outputs { out: Int }
  requires { 0 <= i && i < ROWS; 0 <= j && j < COLS; }
  let lut = Lut<Int>[ROWS, COLS] = [[1,2],[3,4]];
  out := input + lut[i,j];
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C5-requires.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source contains an unsupported character
  --> C5-requires.spatial:6:21
   = unsupported character
   = help: use the currently accepted Spatial subset syntax

error[spatial:E0002]: source contains an unsupported character
  --> C5-requires.spatial:6:22
   = unsupported character
   = help: use the currently accepted Spatial subset syntax

error[spatial:E0002]: source contains an unsupported character
  --> C5-requires.spatial:6:41
   = unsupported character
   = help: use the currently accepted Spatial subset syntax

error[spatial:E0002]: source contains an unsupported character
  --> C5-requires.spatial:6:42
   = unsupported character
   = help: use the currently accepted Spatial subset syntax
```

### L1-dense

[designed] Complete external fixture.

```spatial
kernel DenseLab {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  accel {
    seq foreach base in 0..N step TILE {
      let a = Sram<Int>[TILE];
      load a <- src[base..base + TILE];
      let b = Sram<Int>[TILE];
      foreach lane in 0..TILE { b[lane] := a[lane] * x; }
      store dst[base..base + TILE] <- b;
    }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check L1-dense.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> L1-dense.spatial:7:9
   = expected `:=`
   = help: use the currently accepted scalar or LUT subset syntax
```

### L2-fold

[designed] Complete external fixture.

```spatial
kernel FoldLab {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N] }
  outputs { out: Int }
  accel {
    let tile = Sram<Int>[TILE];
    out := fold base in 0..N step TILE init 0 using + {
      load tile <- src[base..base + TILE];
      let subtotal = fold lane in 0..TILE init 0 using + {
        yield tile[lane];
      };
      yield subtotal;
    };
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check L2-fold.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> L2-fold.spatial:8:40
   = expected `{`
   = help: use the currently accepted scalar or LUT subset syntax
```

### L3-gemm

[designed] Complete external fixture.

```spatial
kernel GemmLab {
  const M: Size = 32;
  const N: Size = 32;
  const K: Size = 32;
  const TM: Size = 16;
  const TN: Size = 16;
  const TK: Size = 16;
  inputs { a: Dram<FixPt<Signed,24,8>>[M,K], b: Dram<FixPt<Signed,24,8>>[K,N] }
  inouts { c: Dram<FixPt<Signed,24,8>>[M,N] }
  accel {
    foreach kk in 0..K step TK {
      foreach mm in 0..M step TM {
        let ta = Sram<FixPt<Signed,24,8>>[TM,TK];
        load ta <- a[mm..mm+TM,kk..kk+TK];
        foreach nn in 0..N step TN {
          let tb = Sram<FixPt<Signed,24,8>>[TK,TN];
          let tc = Sram<FixPt<Signed,24,8>>[TM,TN];
          let partial = Sram<FixPt<Signed,24,8>>[TM,TN];
          load tb <- b[kk..kk+TK,nn..nn+TN];
          load tc <- c[mm..mm+TM,nn..nn+TN];
          memfold tc with partial over k_idx in 0..TK using + {
            foreach ii in 0..TM par 2 {
              foreach jj in 0..TN par 16 {
                partial[ii,jj] := ta[ii,k_idx] * tb[k_idx,jj];
              }
            }
          }
          store c[mm..mm+TM,nn..nn+TN] <- tc;
        }
      }
    }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check L3-gemm.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> L3-gemm.spatial:8:25
   = expected `[`
   = help: use the currently accepted scalar or LUT subset syntax
```

### V1-name

[designed] Complete external fixture.

```spatial
kernel DenseRenamed {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  accel {
    seq foreach base in 0..N step TILE {
      let a = Sram<Int>[TILE];
      load a <- src[base..base + TILE];
      let b = Sram<Int>[TILE];
      foreach lane in 0..TILE { b[lane] := a[lane] * x; }
      store dst[base..base + TILE] <- b;
    }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check V1-name.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> V1-name.spatial:7:9
   = expected `:=`
   = help: use the currently accepted scalar or LUT subset syntax
```

### V2-local

[designed] Complete external fixture.

```spatial
kernel FoldLab {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N] }
  outputs { out: Int }
  accel {
    let tile = Sram<Int>[TILE];
    out := fold base in 0..N step TILE init 0 using + {
      load tile <- src[base..base + TILE];
      let sum_tile = fold lane in 0..TILE init 0 using + {
        yield tile[lane];
      };
      yield sum_tile;
    };
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check V2-local.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> V2-local.spatial:8:40
   = expected `{`
   = help: use the currently accepted scalar or LUT subset syntax
```

### V3-tile

[designed] Complete external fixture.

```spatial
kernel DenseLab {
  const N: Size = 32;
  const TILE: Size = 8;
  inputs { src: Dram<Int>[N], x: Int }
  outputs { dst: Dram<Int>[N] }
  accel {
    seq foreach base in 0..N step TILE {
      let a = Sram<Int>[TILE];
      load a <- src[base..base + TILE];
      let b = Sram<Int>[TILE];
      foreach lane in 0..TILE { b[lane] := a[lane] * x; }
      store dst[base..base + TILE] <- b;
    }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check V3-tile.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> V3-tile.spatial:7:9
   = expected `:=`
   = help: use the currently accepted scalar or LUT subset syntax
```

### V4-const-order

[designed] Complete external fixture.

```spatial
kernel GemmLab {
  const N: Size = 32;
  const M: Size = 32;
  const K: Size = 32;
  const TM: Size = 16;
  const TN: Size = 16;
  const TK: Size = 16;
  inputs { a: Dram<FixPt<Signed,24,8>>[M,K], b: Dram<FixPt<Signed,24,8>>[K,N] }
  inouts { c: Dram<FixPt<Signed,24,8>>[M,N] }
  accel {
    foreach kk in 0..K step TK {
      foreach mm in 0..M step TM {
        let ta = Sram<FixPt<Signed,24,8>>[TM,TK];
        load ta <- a[mm..mm+TM,kk..kk+TK];
        foreach nn in 0..N step TN {
          let tb = Sram<FixPt<Signed,24,8>>[TK,TN];
          let tc = Sram<FixPt<Signed,24,8>>[TM,TN];
          let partial = Sram<FixPt<Signed,24,8>>[TM,TN];
          load tb <- b[kk..kk+TK,nn..nn+TN];
          load tc <- c[mm..mm+TM,nn..nn+TN];
          memfold tc with partial over k_idx in 0..TK using + {
            foreach ii in 0..TM par 2 {
              foreach jj in 0..TN par 16 {
                partial[ii,jj] := ta[ii,k_idx] * tb[k_idx,jj];
              }
            }
          }
          store c[mm..mm+TM,nn..nn+TN] <- tc;
        }
      }
    }
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check V4-const-order.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> V4-const-order.spatial:8:25
   = expected `[`
   = help: use the currently accepted scalar or LUT subset syntax
```

### V5-comment

[designed] Complete external fixture.

```spatial
kernel FoldLab {
  const N: Size = 32;
  const TILE: Size = 16;
  inputs { src: Dram<Int>[N] }
  outputs { out: Int }
  // a complete sum over 32 elements
  accel {
    let tile = Sram<Int>[TILE];
    out := fold base in 0..N step TILE init 0 using + {
      load tile <- src[base..base + TILE];
      let subtotal = fold lane in 0..TILE init 0 using + {
        yield tile[lane];
      };
      yield subtotal;
    };
  }
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check V5-comment.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0002]: source does not match the accepted Spatial adapter syntax
  --> V5-comment.spatial:9:40
   = expected `{`
   = help: use the currently accepted scalar or LUT subset syntax
```

### C6-par-divides

[designed] Complete external fixture.

```spatial
kernel ParMistake {
  const N: usize = 16;
  const P: usize = 2;
  outputs { out: Int }
  out := reduce i in 0..N par P { i };
}
```

[measured] Transcript.

```text
$ "$SPATIAL_RS" check C6-par-divides.spatial
exit: 1
stdout: (empty)
stderr:
error[spatial:E0408]: scalar reduction is outside the supported ScalarReduce v0 subset
  --> C6-par-divides.spatial:1:1
   = scalar reduce v0 requires 1 <= length <= 65536 and parallelism equal to 1
   = help: use one scalar Int output and `out := reduce i in 0..N par P { i }` with 1 <= N <= 65536 and P equal to 1
```

### Python execution environment

Exo's seven cases and three controls below ran against the pinned clone through `PYTHONPATH` in an isolated venv; source and dependency paths in stack traces are relocated to `reference/exo/`, `venv/`, `fixtures/`, and `python-stdlib/`. Exception text, source line numbers, stack frames, exit codes, and output otherwise remain as captured. All cases stop after `@proc` construction or schedule transformation: no generated hardware/C execution is claimed. The front-end calls type checking, bounds checking and alias checking (`exo@defe172:src/exo/API.py:157-171`). Scratchpad backend code separately disallows ordinary reads (`exo@defe172:src/exo/libs/memories.py:110-112`); frontend acceptance does not predict its eventual diagnostic or successful execution.

Initial import probes found missing `asdl_adt` and, after installing dependencies inside the venv, optional PySMT Cython compilation attempted an unwritable default `.pyxbld` directory. Selecting supported `PYSMT_CYTHON=0` enabled the following actual runs. No sandbox escalation or source modification was used. Allo remained unavailable due to its missing native module; Scala was inspected only, without sbt.

### P1-tile

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(a: i8[30]):
    for i in seq(0, 30):
        a[i] = 0
divide_loop(kernel, "i", 16, ["tile", "lane"], perfect=True)
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P1-tile.py
exit: 1
stdout: (empty)
stderr:
Traceback (most recent call last):
  File "fixtures/P1-tile.py", line 9, in <module>
    divide_loop(kernel, "i", 16, ["tile", "lane"], perfect=True)
  File "reference/exo/src/exo/API_scheduling.py", line 100, in __call__
    return self.func(*bound_args.args, **bound_args.kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/API_scheduling.py", line 1734, in divide_loop
    ir, fwd = scheduling.DoDivideLoop(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/rewrite/LoopIR_scheduling.py", line 790, in DoDivideLoop
    Check_IsDivisible(ir, [loop], N, quot)
  File "reference/exo/src/exo/rewrite/LoopIR_scheduling.py", line 301, in Check_IsDivisible
    raise SchedulingError(f"cannot perfectly divide '{expr}' by {quot}")
exo.rewrite.new_eff.SchedulingError: <<<unknown directive>>>: cannot perfectly divide '30' by 16
```

### P2-par

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(a: i8[16]):
    for i in seq(0, 16):
        a[i] = 0
kernel = divide_loop(kernel, "i", 3, ["group", "lane"], perfect=True)
unroll_loop(kernel, "lane")
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P2-par.py
exit: 1
stdout: (empty)
stderr:
Traceback (most recent call last):
  File "fixtures/P2-par.py", line 9, in <module>
    kernel = divide_loop(kernel, "i", 3, ["group", "lane"], perfect=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/API_scheduling.py", line 100, in __call__
    return self.func(*bound_args.args, **bound_args.kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/API_scheduling.py", line 1734, in divide_loop
    ir, fwd = scheduling.DoDivideLoop(
              ^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/rewrite/LoopIR_scheduling.py", line 790, in DoDivideLoop
    Check_IsDivisible(ir, [loop], N, quot)
  File "reference/exo/src/exo/rewrite/LoopIR_scheduling.py", line 301, in Check_IsDivisible
    raise SchedulingError(f"cannot perfectly divide '{expr}' by {quot}")
exo.rewrite.new_eff.SchedulingError: <<<unknown directive>>>: cannot perfectly divide '16' by 3
```

### P4-uninit

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(out: i8[1]):
    scratch: i8[16,16] @ GEMM_SCRATCH
    out[0] = scratch[0,0]
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P4-uninit.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### P5-dram

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(a: i8[16]):
    for i in seq(0, 16):
        a[i] = 0
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P5-dram.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### P6-no-init

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(a: i8[16], out: i8[1]):
    total: i8
    for i in seq(0, 16):
        total += a[i]
    out[0] = total
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P6-no-init.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### P7-host

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
host_value = "sixteen"
@proc
def kernel(a: i8[16]):
    for i in seq(0, host_value):
        a[i] = 0
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P7-host.py
exit: 1
stdout: (empty)
stderr:
Traceback (most recent call last):
  File "fixtures/P7-host.py", line 6, in <module>
    @proc
     ^^^^
  File "reference/exo/src/exo/API.py", line 42, in proc
    parser = Parser(
             ^^^^^^^
  File "reference/exo/src/exo/frontend/pyparser.py", line 647, in __init__
    self._cached_result = self.parse_fdef(module_ast, instr=instr)
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/frontend/pyparser.py", line 813, in parse_fdef
    body = self.parse_stmt_block(pyast_body)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/frontend/pyparser.py", line 1230, in parse_stmt_block
    cond = self.parse_loop_cond(s.iter)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/frontend/pyparser.py", line 1346, in parse_loop_cond
    hi = self.parse_expr(cond.args[1])
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/frontend/pyparser.py", line 1511, in parse_expr
    self.err(e, "Unquote received input that couldn't be unquoted")
  File "reference/exo/src/exo/frontend/pyparser.py", line 688, in err
    raise ParseError(f"{self.getsrcinfo(node)}: {errstr}") from origin
exo.frontend.pyparser.ParseError: fixtures/P7-host.py:8:20: Unquote received input that couldn't be unquoted
```

### P8-lut

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(index_value: index, lut: i8[4], out: i8[1]):
    out[0] = lut[index_value]
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python P8-lut.py
exit: 1
stdout: (empty)
stderr:
Traceback (most recent call last):
  File "fixtures/P8-lut.py", line 5, in <module>
    @proc
     ^^^^
  File "reference/exo/src/exo/API.py", line 49, in proc
    return Procedure(parser.result())
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "reference/exo/src/exo/API.py", line 170, in __init__
    CheckBounds(proc)
  File "reference/exo/src/exo/frontend/boundscheck.py", line 582, in __init__
    raise TypeError(
TypeError: Errors occurred during effect checking:
fixtures/P8-lut.py:7:13: lut is read out-of-bounds when:
   lut_stride_0 = 1, out_stride_0 = 1, index_value = -1.
```

### PC-tile

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(a: i8[32]):
    for i in seq(0, 32):
        a[i] = 0
divide_loop(kernel, "i", 16, ["tile", "lane"], perfect=True)
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python PC-tile.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### PC-lut

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
@proc
def kernel(index_value: index, lut: i8[4], out: i8[1]):
    assert index_value >= 0
    assert index_value < 4
    out[0] = lut[index_value]
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python PC-lut.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### PC-host

[designed] Complete Exo fixture.

```python
from __future__ import annotations
from exo import proc
from exo.stdlib.scheduling import divide_loop, unroll_loop
from exo.libs.memories import GEMM_SCRATCH
host_value = 16
@proc
def kernel(a: i8[16]):
    for i in seq(0, host_value):
        a[i] = 0
```

[precedent-measured] Actual execution; no source-only substitute.

```text
$ PYSMT_CYTHON=0 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/exo/src venv/bin/python PC-host.py
exit: 0
stdout: (empty)
stderr:
(empty)
```

### P3 — Allo source-only comparison

[designed] Nonliteral integer-to-fixed counterpart; not run past import and not a Spatial Python implementation:

```python
import allo
from allo.ir.types import int32, Fixed
T = Fixed(32, 8)
def kernel(a: int32) -> T:
    b: T = a
    return b
allo.customize(kernel)
```

[precedent-measured] Complete actual import probe; the unavailable import blocks this fixture. Source paths use the relocation convention above.

```text
$ PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=reference/allo venv/bin/python -c 'import allo'
exit: 1
stdout: (empty)
stderr:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "reference/allo/allo/__init__.py", line 5, in <module>
    from . import frontend, backend, ir, passes, library, _mlir
  File "reference/allo/allo/frontend/__init__.py", line 4, in <module>
    from .pytorch import from_pytorch
  File "reference/allo/allo/frontend/pytorch.py", line 18, in <module>
    from .library import CoreAttention_lib, KVCache_lib, SliceClsToken_lib
  File "reference/allo/allo/frontend/library.py", line 6, in <module>
    from ..ir.types import float32, int32
  File "reference/allo/allo/ir/__init__.py", line 5, in <module>
    from .types import *
  File "reference/allo/allo/ir/types.py", line 9, in <module>
    from .._mlir.ir import (
ModuleNotFoundError: No module named 'allo._mlir'
```

[precedent-measured] Source evidence instead of a runtime diagnostic: `allo@094ab41:allo/ir/builder.py:564-581` maps `(Int, Fixed)` to `allo_d.IntToFixedOp`; `allo@094ab41:tests/test_types.py:65-81` explicitly exercises index/fixed conversion. Thus a type error cannot honestly be quoted for this counterpart. The constructed complete function remains unverified.

### S1–S8 — Scala source messages and unavailable matches

[precedent-measured] All entries are inspected source, not Scala runs; interpolation placeholders are quoted literally.

| ID | Opened source | Exact message or unavailable evidence |
| --- | --- | --- |
| S1 | `spatial@e7a8f2f:test/spatial/tests/feature/dense/MatMult_systolic.scala:77-83` | `M must be divisible by $outerTile`; explicit assertion in this application. No automatic tile-divisibility message established. |
| S2 | `spatial@e7a8f2f:src/spatial/traversal/UserSanityChecks.scala:64-78` | `Counter parallelization ($par) is greater than total number of iterations ($len)` is only the nearby warning; it does not diagnose 16 mod 3. Exact requested message unavailable. |
| S3 | `spatial@e7a8f2f:src/spatial/lang/api/SpatialVirtualization.scala:50-63` | `Type mismatch: Cannot assign ${data.tp} to var of type ${v.A}`. A generic staged-variable path, not a measured scalar-port or SRAM assignment. |
| S4 | `spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaTensor.scala:17-47` | Uninitialized values are `None` and reads return `Option[T]`; a matching read-before-load error string was not located. Do not infer that all Scala backends silently accept it. |
| S5 | `spatial@e7a8f2f:src/spatial/lang/DRAM.scala:90-104` | Bulk store API located; exact attempted indexed-assignment compiler message unavailable. No fabricated “update is not a member” transcript. |
| S6 | `spatial@e7a8f2f:src/spatial/lang/control/ReduceClass.scala:78-87` | `ReduceClass` inherits `ReduceAccum(None, None, None, ...)`; no missing-init error is claimed for this supported overload. |
| S7 | `spatial@e7a8f2f:src/spatial/traversal/CompilerSanityChecks.scala:54-65` | `One or more values were defined on the host but used in Accel without explicit transfer.` Follow-up: `First use in Accel occurs here.` This is an internal sanity-check diagnostic, not evidence that every host capture takes this path. |
| S8 | `spatial@e7a8f2f:src/spatial/executor/scala/memories/ScalaTensor.scala:26-46` | `Index $index was out of bounds, shape was $shape`. Generic tensor execution defense; no static missing-requires diagnostic established. |

The Exo message implementations were opened at `exo@defe172:src/exo/rewrite/LoopIR_scheduling.py:286-301` (division), `exo@defe172:src/exo/frontend/pyparser.py:1497-1511` (capture), and `exo@defe172:src/exo/frontend/boundscheck.py:818-840` (bounds counterexample).
