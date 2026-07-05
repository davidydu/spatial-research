---
type: log
project: spatial-spec
---

# Progress Log

Append-only, newest-first within day blocks. One line per discrete action when possible.

---

## 2026-07-05 -- Rust rewrite FIFO resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `f9fd4ae1946d55d9089f2751514a28b5becdd75a`
  (`Resolve FIFO proof facts`).
- `Fifo1dTileScalarMul v0` now records resolver-backed input/scalar/output
  port symbols, local FIFO symbols, outer/lane loop domains, static
  length/depth facts, load/store tile ranges, FIFO dequeue/enqueue counts,
  parent blocks, lexical order, and effect loop ids before producing the same
  checked `FifoTileScalarMul` payload.
- New fail-closed coverage:
  the ordered FIFO effect proof now binds both dequeue and enqueue effects to
  the exact proven inner lane loop instead of accepting any loop-depth-two
  effect pair.
- Verification passed:
  `cargo test --locked -p spatial-rs-core fifo_tile_scalar_mul_proof -- --nocapture`;
  `cargo test --locked -p spatial-rs-core fifo -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen fifo -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo test --locked --workspace`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic FIFO/stream support,
  back-pressure modeling, arbitrary FIFO topology, or broad Scala source
  compatibility. The active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite Stencil2d resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `ce517499cdd9ffd6c6bf5553469b627d47460778`
  (`Resolve Stencil2d proof facts`).
- `Stencil2d v0` and the fixed Lab3 Sobel adapter now record resolver-backed
  input/output/local-memory symbols, row/column/shift loop domains, row-range
  load/store index facts, `RegFile` reset/shift effects, line-buffer shift
  reads, line-output writes, and horizontal/vertical reduce read groups before
  producing the same checked Stencil2d or exact Lab3 payloads. Accepted syntax
  is not broadened.
- New fail-closed coverage:
  the proof now pins Sobel window/LUT reduction reads to the exact
  horizontal/vertical reducer symbols, so swapped reduce-index facts such as
  `sr[yh, xh] * kh[yh, xh]` no longer satisfy the canonical local-window proof.
- Verification passed:
  `cargo test --locked -p spatial-rs-core stencil2d -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab3 -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen stencil -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_convolution -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo test --locked --workspace`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic `LineBuffer`/`RegFile`/
  `Reduce` lowering, broader Sobel variants, or broad Scala source
  compatibility. The active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite ControlFsm resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `c344521b`
  (`Resolve ControlFsm proof facts`).
- `ControlFsm v0` and the Lab2 FSM adapters now record resolver-backed
  output/scratch/reg/state symbols, the FSM loop domain, scratch write effects,
  reg-value read facts, and final output store-range facts before producing the
  same checked ControlFsm or exact Lab2 FSM payloads. Accepted syntax is not
  broadened.
- New fail-closed coverage:
  the proof asserts the canonical feature body has three state-indexed scratch
  writes, one reg-value read, and one final full-range store, while the alternate
  Lab2 FSM body has four state-indexed scratch writes, zero reg-value reads, and
  the same final full-range store. Resolver diagnostics are consumed only after
  the existing exact structural guard, preserving ControlFsm feature diagnostic
  priority for malformed names/shapes.
- Verification passed:
  `cargo test --locked -p spatial-rs-core control_fsm_proof -- --nocapture`;
  `cargo test --locked -p spatial-rs-core control_fsm -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen control_fsm -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo test --locked --workspace`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic FSM scheduling, arbitrary
  registers/conditionals/effects, or broad Scala source compatibility. The
  active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite ScalarExpr resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `879e8c21`
  (`Resolve ScalarExpr proof facts`).
- `ScalarExpr v0` now records resolver-backed scalar input/output roles,
  symbols, `Int` types, port ordinals, expression read symbols, integer
  expression counts, and zero memory access/effect facts before producing the
  same checked `ScalarExpr` payload. Accepted syntax is not broadened.
- New fail-closed coverage:
  the proof asserts the `ScalarAffine4` read symbols match the accepted scalar
  inputs in source order, that the scalar output is distinct, and that duplicate
  input/output names fail through resolver diagnostics with `spatial:E0302`.
- Verification passed:
  `cargo test --locked -p spatial-rs-core scalar_expr -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen scalar -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, broader scalar syntax, memory
  support inside `ScalarExpr`, or broad Scala source compatibility. The active
  vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite LUT resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `5b6d9d3c`
  (`Resolve LUT proof facts`).
- `LutLookup v0` and the Lab2 LUT adapters now record resolver-backed
  table/input/row/column/output symbols plus rank-2 table read index facts
  before producing the same checked LUT payload. Accepted syntax is not
  broadened.
- New fail-closed coverage:
  the proof asserts the rank-2 table read resolves to the accepted row/column
  scalar port symbols. Duplicate or shadowing LUT-related names are pinned at
  the resolver layer with `spatial:E0302`.
- Verification passed:
  `cargo test --locked -p spatial-rs-core lut -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lut -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, broader LUT syntax, dynamic
  indexing support, or broad Scala source compatibility. The active vendor-HLS
  anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite Dense1d resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `98d0d3fe`
  (`Resolve Dense1d proof facts`).
- `Dense1dScalarMul v0` now records resolver-backed outer/lane loop domains,
  loop-index symbols, input/scalar/output symbols, input/output tile symbols,
  rank-1 remote load/store range facts, and local lane read/write facts before
  producing the same checked `Dense1dScalarMul` payload. The parser/structural
  tiled-I/O shell remains the first accepted shape guard, so accepted syntax is
  not broadened.
- New fail-closed coverage:
  outer/lane loop names and local tile names that shadow accepted constants or
  ports fail through resolver diagnostics with `spatial:E0302`; output-lane
  drift fails with `spatial:E0403`; parser-bridge load/store range bound
  off-by-one variants fail before HIR with `spatial:E0002`. The dense adapter
  duplicate-constant near-miss now correctly reports the resolver duplicate
  declaration diagnostic `spatial:E0302`.
- Verification passed:
  `cargo test --locked -p spatial-rs-core dense1d -- --nocapture`;
  `cargo test --locked -p spatial-rs-core rank1 -- --nocapture`;
  `cargo test --locked -p spatial-rs-core rejects_extra_or_duplicate_consts_in_lut_and_dense_adapters -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen dense -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic rank-1 scheduling, tail
  support, arbitrary load/store endpoint support, or broad Scala source
  compatibility. The active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite Dram2d copy resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `fcdfed4c`
  (`Resolve DRAM2d copy proof facts`).
- `Dram2dCopy v0` now records resolver-backed row/column loop-domain facts,
  loop-index symbols, static row/column bounds, and a shared rank-2
  global-write/global-read copy access fact before producing the same checked
  `Dram2dCopy` payload. The original structural row-major shape guard remains
  in place, so accepted syntax is not broadened.
- New fail-closed coverage:
  row or column loop indices that shadow the `ROWS`/`COLS` shape constants fail
  through resolver diagnostics with `spatial:E0302` on both the private
  classifier proof and public `parse_accel` path.
- Verification passed:
  `cargo test --locked -p spatial-rs-core dram2d -- --nocapture`;
  `cargo test --locked -p spatial-rs-core rank2_row_major_copy -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_copy -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic rank-2 memory lowering,
  aliases/in-place semantics, or broad Scala source compatibility. The active
  vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite SRAM tile-fold resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `c6f2096d`
  (`Resolve SRAM tile fold proof facts`).
- `ScalarSramTileFold v0` now records resolver-backed fold/reduce loop facts,
  the unit-stride DRAM tile-load range, and the inner `tile[inner]` read before
  producing the same checked `ScalarSramTileFold` payload. The older structural
  source-shape guards remain in place, so accepted syntax is not broadened.
- New fail-closed coverage:
  outer loop names that shadow the length constant and inner reduce names that
  shadow the tile constant fail through resolver diagnostics with
  `spatial:E0302`; literal `outer + 16` tile-load bounds are rejected with
  `spatial:E0413` because the load range must use the resolved fold-step
  identifier.
- Verification passed:
  `cargo test --locked -p spatial-rs-core sram_tile_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-core resolved_hir_keeps_fold_load_and_reduce_body_loop_joins -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls render_tests`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline`;
  `cargo test --locked -p ee109-examples --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_validate_evidence_accepts_current_39_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a local compiler-interface/proof cleanup only. It does not add
  syntax, validation-roster members, generated HLS changes, manifest changes,
  fresh EC2/Vitis evidence, board execution, generic local-memory folds, or
  broad Scala source compatibility. The active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite scalar reduction/fold resolved-proof cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `7e221d11`
  (`Resolve scalar reduction proof facts`).
- `ScalarReduce v0` now records resolver-backed reduce loop-domain and
  schedule facts before producing the same checked `ScalarReduce` payload.
  Shadowing the reduce loop index against a constant now fails through the
  resolver with `spatial:E0302` instead of relying only on HIR identifier text.
- `ScalarFold v0` now records resolver-backed outer-fold and inner-reduce loop
  facts and validates the rank-1 `src[outer + inner]` read through a shared
  affine rank-1 read helper before producing the same checked `ScalarFold`
  payload. Shadowing the inner reduce index against the tile constant now fails
  through `spatial:E0302`.
- Verification passed:
  `cargo test --locked -p spatial-rs-core scalar_reduce -- --nocapture`;
  `cargo test --locked -p spatial-rs-core scalar_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-core rank1_indexed_read_sum_lanes -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls render_tests`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline`;
  `cargo test --locked -p ee109-examples --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_00797aed_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_validate_evidence_accepts_current_39_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a compiler-interface/proof cleanup only. It does not add syntax,
  validation-roster members, generated HLS changes, manifest changes, fresh
  EC2/Vitis evidence, board execution, generic reductions/folds, or broad
  Scala source compatibility. The active vendor-HLS anchor remains
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.

---

## 2026-07-05 -- Rust rewrite SRAM tile-fold alias-bound cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `038fae29`
  (`Accept SRAM tile fold alias bounds`).
- `ScalarSramTileFold v0` no longer requires the length/tile constants used by
  the accepted `SramTileFoldSum32` source to be literally named `N` and `TILE`.
  The classifier resolves the fold length, fold step, load range bound, and
  inner reduce bound from the source identifiers, accepting equivalent
  Rust-subset spellings such as `LEN`/`BLOCK` when they resolve to the same
  canonical `32`/`16` checked payload.
- Added parser and classifier proof accept tests for the alias-bound spelling,
  a fail-closed wrong-alias-tile test, and an HLS/manifest equality regression
  proving the alias spelling emits the same artifacts as the canonical canary.
- Verification passed:
  `cargo test --locked -p spatial-rs-core sram_tile_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen sram_tile_fold_alias_bounds -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a frontend/HIR classifier source-spelling cleanup only. It does not
  add generic local-memory folds, arbitrary fold-load effects, tail tiles,
  dynamic bounds, non-`Int`, new validation-roster members, fresh EC2/Vitis
  evidence, board execution, or broader Scala source compatibility.

---

## 2026-07-05 -- Rust rewrite hoisted-LHS row/column/K-tail Tile-K source shape

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `224d7a76`
  (`Accept hoisted Tile-K tail lhs load`).
- Accepted the Lab2-like row/column/K-tail Tile-K placement where `row_limit`
  and `tileA_sram load` are hoisted to tile-row scope before the column-tile
  loop, while `col_limit`, B/C tile loads, fold, and C store remain
  column-local.
- Added serial and Part6 scheduled parser/proof coverage. The accepted shape
  normalizes to the existing `Dense2dTileKMemFold` row/column/K-tail payloads,
  including `k_bound=numel_k`, `row_bound=row_limit`, `col_bound=col_limit`,
  and Part6 `partial_row_par=2` / `partial_col_par=16`.
- Added an HLS/manifest equality regression for the scheduled Part6
  row/column/K-tail hoisted-LHS source. Generated HLS and manifests match the
  existing scheduled row/column/K-tail canary exactly.
- Cleaned stale docs/evidence wording while in the area:
  README scalar alias-bound text now matches the resolved-name cleanup, retired
  raw Lab1 wrapper claims were corrected, selected 38-program evidence is
  marked historical beside the active 39-program anchor, and vault raw-wrapper
  ingress language now says raw wrappers are retired.
- Verification passed:
  `cargo test --locked -p spatial-rs-core hoisted_lhs_row_col_k_tail -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen hoisted_lhs -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a source-shape/proof cleanup only. It does not add new validation
  roster members, fresh EC2/Vitis evidence, one-sided tails, generic Tile-K
  phase discovery, raw Scala wrapper ingress, generic Spatial `MemFold`,
  inferred banking, board execution, or timing closure claims.

---

## 2026-07-05 -- Rust rewrite scalar reduction/fold alias-bound cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `9797d162`
  (`Accept scalar reduction alias bounds`).
- `ScalarReduce v0` no longer requires the loop bound constants to be literally
  named `N` and `P`. The classifier resolves the identifiers used by the
  reduce expression itself, so equivalent Rust-subset spellings such as
  `LEN`/`LANES` reach the same checked payload.
- `ScalarFold v0` similarly resolves the fold length, tile step, inner reduce
  tile bound, and `par` identifier from source facts, so equivalent spellings
  such as `LEN`/`BLOCK`/`LANES` are accepted when the resolved values match the
  existing narrow contract.
- Added accept tests for both alias-bound spellings and fail-closed tests for
  alias `LANES = 2`. Canonical `N`/`TILE`/`P` spellings still pass.
- Verification passed:
  `cargo test --locked -p spatial-rs-core resolved_alias_bounds -- --nocapture`;
  `cargo test --locked -p spatial-rs-core scalar_reduce -- --nocapture`;
  `cargo test --locked -p spatial-rs-core scalar_fold -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary:
  this is a frontend/HIR classifier cleanup only. It does not add generic
  reductions, arbitrary reduce/fold bodies, non-unit `par`, tail tiles, new
  validation-roster members, fresh EC2/Vitis evidence, board execution, or
  broader Scala source compatibility.

---

## 2026-07-05 -- Rust rewrite FixPt tail diagnostic evidence revalidation

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Registered `MatrixTileMemFoldTailFixPt5x7x5` as a diagnostic-only selected
  kernel for `run-vitis-validation --kernel`. This keeps the official
  validation roster at 39 programs while making the existing one-kernel
  EC2/Vitis proof locally revalidatable.
- Added a narrow evidence-validator compatibility path for single-kernel
  root-layout one-off evidence bundles. Standard selected/full bundles still use
  the newer `sidecars/`, `logs/`, and `reports/` layout.
- Revalidated
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-fixpt-tail-oneoff/`
  as selected diagnostic evidence:
  `resource_fit=1/1`, `over_budget=0`, and `ii_caveated=0`.
- Boundary:
  this is not a validation-roster promotion, not a new full current-head Vitis
  refresh, not board execution, and not generic FixPt tail support. A roster
  promotion for this canary still needs an explicit roster decision and a full
  current-head refresh.

---

## 2026-07-05 -- Rust rewrite generic scheduled row/column/K-tail Tile-K canary

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `5f684f2a`
  (`Add generic scheduled row-col Tile-K canary`).
- Added the local validation canary
  `MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34`.
  It keeps the existing Tile-K row/column/K-tail shape
  (`ROWS=33`, `COLS=35`, `K=34`, `row_limit`, `col_limit`, `numel_k`) and
  proves a non-Part6 partial schedule (`partial_row_par=4`,
  `partial_col_par=8`) through checked IR, HLS row-cyclic partitions,
  pipeline/unroll pragmas, and the native host-C++ harness.
- The EE109 local validation roster is now 39 programs. The previous
  38-program par4x16 EC2/Vitis bundle was the full vendor-stability anchor at
  this local-compiler checkpoint; later same-day EC2/Vitis evidence superseded
  it with the 39-program `746d9ec5` current-head refresh and selected par4x8
  evidence.
- Tightened fail-closed boundaries after GPT-5.5 xhigh review:
  non-dividing generic schedules such as `4x7` are rejected, the reserved
  Part6 `2x16` row/column/K-tail schedule is rejected under generic names, and
  row/column/K-tail payloads cannot use the old serial full-K or par4x16
  full-K kernel names.
- Updated CLI/evidence tests so local plan generation covers all 39 kernels,
  while default full-bundle evidence validation now rejects old 35-, 37-, and
  38-program bundles against the current 39-kernel local roster.
- Verification passed:
  `cargo test -p spatial-rs-core --locked generic_scheduled_tile_k_row_col_tail -- --nocapture`;
  `cargo test -p spatial-rs-core --locked checked_ir_rejects_generic_row_col_tail_payloads_under_full_k_profile_names -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k_par4x8_row_col_k_tail_emits_parametric_guarded_hls_and_harness -- --nocapture`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --kernel MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34 --out target/vitis-validation-plan-par4x8-row-col-tail-fresh`;
  `cargo test --locked --workspace`;
  `cargo fmt --all -- --check`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary:
  this is a local compiler/HLS canary, not a generic GEMM/schedule optimizer.
  It does not add raw Scala support, generic `MemFold`, schedule inference,
  arbitrary dimensions, generic fixed-point widths, board-fit claims, or a new
  full Vitis anchor.

## 2026-07-05 -- Rust rewrite rank-2 local-compute proof helper cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `3e7bb919`
  (`Share rank2 local compute lane proofs`).
- Added shared rank-2 local compute proof helpers in
  `crates/spatial-rs-core/src/classifier/rank2_access.rs`:
  `rank2_local_product_lanes` for
  `dst[row,col] := lhs[row,k] * rhs[k,col]`, and
  `rank2_local_accumulation_lanes` for
  `dst[row,col] := dst[row,col] + partial[row,col]`.
- Routed the Tile-K partial-product and C-accumulation resolved-fact checks
  through those helpers after the existing structural `*` / `+` syntax guards.
- Added helper-level acceptance coverage for both Tile-K and non-outer-K
  `Dense2dTileMemFold`, plus fail-closed negative tests for wrong RHS-K,
  wrong LHS-K, wrong RHS-column, and wrong partial-read lanes.
- A GPT-5.5 xhigh review subagent found no blocking issues and recommended the
  two added product-lane negative tests.
- Verification passed:
  `cargo test -p spatial-rs-core --locked rank2_local_product_lanes -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank2_local_accumulation_lanes -- --nocapture`;
  `cargo test -p spatial-rs-core --locked tile_k_partial_product_fact -- --nocapture`;
  `cargo test -p spatial-rs-core --locked tile_k_c_accumulation_fact -- --nocapture`;
  `cargo test -p spatial-rs-core --locked tile_k_fold_update -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank2_tile_memfold -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen tile_k -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo fmt --all -- --check`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary:
  this is a no-HLS-drift classifier reliability cleanup. It does not add new
  accepted syntax, checked payloads, validation-program members, generated HLS,
  imported Vitis evidence, or broader Spatial `MemFold` support.

## 2026-07-05 -- Rust rewrite selected par4x16 EC2/Vitis caveat proof

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust source commit under test:
  `6d461260`
  (`Record selected outer-k Vitis evidence`).
- Ran the selected-kernel Vitis lane for the known over-resource-budget
  `MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` canary on
  `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`) with Cargo 1.75.0 and Vitis 2025.1.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-05-selected-par4x16-6d461260`.
- Command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --kernel MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32 --out target/vitis-validation-selected-par4x16-6d461260-run`.
- Result:
  return code 0, `csim_design` passed, `csynth_design` passed,
  estimated Fmax 136.99 MHz, target device `xc7z020-clg400-1`, 10 ns clock
  target, 7.300 ns estimated clock, and HLS acceptance despite resource and II
  caveats.
- Exact one-kernel evidence validation passed:
  `VALIDATED ... kernels=1 resource_fit=0/1 over_budget=1 ii_caveated=1`.
- Imported compact evidence into the Rust repo at
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-par4x16-6d461260/`:
  generated kernel/harness/manifest, sidecar TCL, Vitis log, csynth report,
  one-row summary files, and README.
- The selected report records 10 BRAM_18K, 256 DSP, 24921 FF, 18634 LUT,
  0 URAM; DSP is over budget against 220 available. The selected log records
  six II-violation warnings and max final II 16 on the final C writeback loop.
- Added Rust evidence-regression coverage for both the HLS validator and CLI
  selected-evidence path.
- Boundary:
  this proves selected `--kernel` execution/validation and one-kernel caveat
  accounting for the exact `par4x16` canary. It is HLS acceptance evidence,
  not resource-fit implementation evidence, board execution, Vivado
  implementation, timing closure, or broader Spatial language support.

## 2026-07-05 -- Rust rewrite selected full-K Tile-K EC2/Vitis proof

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust source commit under test:
  `38ade9d2`
  (`Support selected Vitis validation kernels`).
- Ran the new selected-kernel Vitis lane for
  `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` on
  `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`) with Cargo 1.75.0 and Vitis 2025.1.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-05-selected-kernel-38ade9d2`.
- Command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --kernel MatrixTileMemFoldOuterKInPlaceFixPt32x32x32 --out target/vitis-validation-selected-outerk-38ade9d2-run`.
- Result:
  return code 0, `csim_design` passed, `csynth_design` passed,
  estimated Fmax 136.99 MHz, target device `xc7z020-clg400-1`, 10 ns clock
  target, 7.300 ns estimated clock, and resource fit true.
- Exact one-kernel evidence validation passed:
  `VALIDATED ... kernels=1 resource_fit=1/1 over_budget=0 ii_caveated=0`.
- Imported compact evidence into the Rust repo at
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-outerk-38ade9d2/`:
  generated kernel/harness/manifest, sidecar TCL, Vitis log, csynth report,
  one-row summary files, and README.
- Added a Rust evidence-regression test:
  `selected_outer_k_vitis_evidence_validator_accepts_one_kernel_checkpoint`.
- Verification passed:
  remote selected runner tests on EC2;
  remote selected Vitis execute;
  remote selected evidence validation;
  remote EC2 toolchain compatibility;
  local selected evidence CLI validation;
  local selected runner tests;
  local full `spatial-rs-hls --test vitis_validation`.
- Boundary:
  this is a selected one-kernel vendor-HLS proof and workflow validation for
  the resource-fit full-K Tile-K canary. It is not a replacement for the
  current 38-program vendor anchor, not board execution, not Vivado
  implementation, and not broader Spatial language support.

## 2026-07-05 -- Rust rewrite selected-kernel Vitis validation runner

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `38ade9d2`
  (`Support selected Vitis validation kernels`).
- Added an exact, case-sensitive `--kernel NAME` filter to
  `run-vitis-validation` so plan-only and execute runs can target a single
  EE109 validation member instead of always iterating the full 38-program
  roster.
- The no-filter default remains the full current validation roster.
- `--validate-evidence DIR --kernel NAME` now validates an exact one-kernel
  evidence bundle using the same selected-roster lookup. A selected validation
  against the full 38-program checkpoint fails closed with a kernel-count
  mismatch, preserving the stale-artifact guard.
- Updated the Rust README with selected-kernel plan, execute, and evidence
  validation commands for the EC2/Vitis workflow.
- Verification passed:
  `cargo test -p ee109-examples --locked --test run_vitis_validation selected_kernel -- --nocapture`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_par4x16_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `cargo fmt --all -- --check`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is validation-runner workflow hardening only. It is not a
  fresh EC2/Vitis execution, not a new validation-roster member, not board
  execution, and not a broader Spatial language feature.

## 2026-07-05 -- Rust rewrite captures one-off Vitis proof for exact FixPt tail canary

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust source commit under test:
  `2ed2ddecf1ec1af049b0ae41a544b93b0e1d75ea`
  (`Add exact FixPt MemFold tail canary`).
- Ran a one-kernel EC2/Vitis 2025.1 proof for
  `MatrixTileMemFoldTailFixPt5x7x5` on
  `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`) with Cargo 1.75.0 and
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`.
- Command:
  `cd /home/ubuntu/spatial-rs-runs/2026-07-05-fixpt-tail-oneoff/oneoff && cargo run --offline -- --mode both --out /home/ubuntu/spatial-rs-runs/2026-07-05-fixpt-tail-oneoff/vitis-oneoff`.
- Result:
  return code 0, `csim_design` passed, `csynth_design` passed,
  estimated Fmax 136.99 MHz, target device `xc7z020-clg400-1`, 10 ns clock
  target, 7.300 ns estimated clock, and resource fit true.
- Imported compact evidence into the Rust repo at
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-fixpt-tail-oneoff/`:
  generated kernel/harness/manifest, sidecar TCL, Vitis log, csynth report, and
  one-row summary files.
- Boundary:
  this is real vendor-HLS evidence for the exact non-roster
  `MatrixTileMemFoldTailFixPt5x7x5` canary, not a validation-roster promotion,
  not a full 39-program refresh, not board execution, not generic FixPt tail
  support, and not broader Spatial `MemFold` support.

## 2026-07-05 -- Rust rewrite Dense MemFold tail-bound role recovery

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `4834a9c8`
  (`Recover dense MemFold tail bounds by role`).
- Added a no-HLS-drift non-outer-K `Dense2dTileMemFold` classifier/proof
  cleanup for the local `MatrixTileMemFoldTail5x7x5` canary: the canonical
  `row_limit` and `col_limit` tail-bound lets are now recovered by role in
  either declaration order.
- The helper remains intentionally narrow: it inspects only the two leading
  tail-bound lets, requires canonical `row_limit/TILE_R` and
  `col_limit/TILE_C`, leaves the five compute phases ordered, and preserves the
  existing Int-only tail boundary.
- Added red/green canaries for proof-level role recovery, public classifier
  normalization, HLS/manifest equality, and fail-closed duplicate/renamed or
  formula-swapped bound-role near misses.
- Updated Rust repo docs and vault status notes to record that checked payloads,
  generated HLS, manifests, validation-roster membership, and imported Vitis
  evidence are unchanged.
- Verification passed:
  `cargo test --locked -p spatial-rs-core dense2d_memfold -- --nocapture`;
  `cargo test --locked -p spatial-rs-core classifies_rank2_tile_memfold_tail -- --nocapture`;
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold_tail_bound_role_near_misses_fail_closed -- --nocapture`;
  `cargo test --locked -p spatial-rs-core tile_k_contract -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_tile_memfold_tail -- --nocapture`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is not generic tail support, FixPt tail support, K tiling,
  `numel_k`, Part6 `par`, fold/store reordering, broad phase discovery, raw
  Scala Lab2 compatibility, a validation-roster change, or a fresh EC2/Vitis
  run.

## 2026-07-05 -- Rust rewrite Tile-K tail-bound role recovery

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `42167c03`
  (`Recover Tile-K tail bounds by role`).
- Added a no-HLS-drift Tile-K structural-recovery cleanup for the covered
  row/column/K-tail profiles: `row_limit` and `col_limit` tail-bound lets are
  now recovered by role in either declaration order before the pre-fold phases.
- The helper still requires exactly one canonical `row_limit/TILE_R` bound and
  one canonical `col_limit/TILE_C` bound, then leaves pre-fold role recovery and
  the fixed fold/store ordering unchanged.
- Added the red/green contract canary
  `tile_k_contract_accepts_role_identified_row_col_tail_bound_order`.
- Updated Rust repo docs and vault status notes to record that checked payloads,
  generated HLS, manifests, validation-roster membership, and imported Vitis
  evidence are unchanged.
- Verification passed:
  `cargo test --locked -p spatial-rs-core tile_k_contract -- --nocapture`;
  `cargo test --locked -p spatial-rs-core tile_k_phase_spine -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_part6_row_col_k_tail_reversed_min_preserves_exact_hls_and_manifest`;
  `cargo test --locked --workspace`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is not broader Tile-K phase discovery, fold/store reordering,
  arbitrary structural statement recovery, generic Spatial `MemFold`, arbitrary
  tails, broad Scala compatibility, a validation-roster change, or a fresh
  EC2/Vitis run.

## 2026-07-05 -- Rust rewrite Vitis evidence-quality classification

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `88c7df1a`
  (`Report Vitis resource quality caveats`).
- Extended the Vitis log/report parser to capture II-violation warning counts,
  max final II, resource totals, available resources, utilization percentages,
  and over-budget resource names from the stable copied evidence.
- Added a repo-local evidence-quality summary used by
  `run-vitis-validation --validate-evidence`; the active 38-program bundle now
  reports `resource_fit=37/38`, `over_budget=1`, and `ii_caveated=14`.
- Added focused tests proving the `par4x16` evidence records 256 DSP against
  220 available, is the only over-resource-budget kernel in the current
  roster, and remains an HLS-accepted but not board-fit canary.
- Verification passed:
  `cargo test --locked -p spatial-rs-hls --test vitis_validation par4x16 -- --nocapture`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_validate_evidence_accepts_current_38_checkpoint -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-par4x16-38-program --mode both`;
  `cargo fmt --all -- --check`;
  `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is local evidence parsing and quality classification over the
  existing 2026-07-05 Vitis evidence. It is not a fresh EC2/Vitis execution,
  Vivado implementation, board-fit proof, or performance optimization.

## 2026-07-05 -- Rust rewrite raw Lab3 Scala ingress retirement

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `22743e784955c8583e8694262f65b3af0a732a6d`
  (`Retire raw Lab3 Scala ingress`).
- Retired the local teaching raw
  `@spatial class Lab3Part1Convolution` Scala wrapper from quarantined source
  ingress, including the formerly accepted static-border spelling.
- Removed the now-dead `frontend::lab3_stencil_bridge` module and deleted the
  raw Lab3 shell/local-window proof island from `source_adapter.rs`; canonical
  Rust frontend/HIR `kernel Lab3Part1Convolution` remains accepted.
- Kept `Lab3Part1Convolution` reserved, kept the Lab3 classifier routed through
  the shared `Stencil2dSobelProof`, and preserved generated HLS, manifest,
  host-harness behavior, validation roster membership, and imported Vitis
  evidence.
- Red checks:
  `cargo test --locked -p spatial-rs-core retired_low_value_raw_scala_wrappers_stay_outside_quarantined_registry -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab3_part1_convolution -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_raw_part1_convolution_is_retired_from_quarantined_source_ingress -- --nocapture`
  first failed because raw Lab3 still canonicalized to the checked Lab3
  payload.
- Verification passed:
  `cargo test --locked -p spatial-rs-core retired_low_value_raw_scala_wrappers_stay_outside_quarantined_registry -- --nocapture`;
  `cargo test --locked -p spatial-rs-core retired_local_lab3_static_border_wrapper_stays_outside_quarantined_registry -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab3_part1_convolution -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab3_static_kernel_border_expression -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_raw_part1_convolution_is_retired_from_quarantined_source_ingress -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_raw_part1_convolution_static_border_is_retired_from_quarantined_source_ingress -- --nocapture`;
  `cargo test --locked -p spatial-rs-core source_adapter -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab3 -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3 -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part5_gemm_fixed_32 -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part5_fixed_32_preserves_outer_k_hls_and_manifest -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_fixed_32_emits_scheduled_hls_and_manifest -- --nocapture`;
  `cargo fmt --all -- --check`;
  `cargo test --locked --quiet`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is a Scala-ingress retirement and documentation update; it
  does not change accepted canonical Rust Lab3 syntax, generated HLS,
  manifests, validation roster membership, or fresh EC2/Vitis evidence. The
  active vendor anchor remains the imported `a62eb274` 37-program checkpoint
  pending future HLS testing.

## 2026-07-05 -- Rust rewrite reserved-label fallthrough audit

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `ad2ca35cda7afa59715e29e4deadbb4eb5a9bb23`
  (`Audit reserved label fallthrough guards`).
- Added table-independent parser coverage proving every hard-coded EE109 lab
  label rejects instead of falling through to a generic scalar feature if a
  future edit weakens the reserved-name table.
- Hardened checked-IR coverage so the hard-coded EE109 lab-label set rejects
  as generic `ScalarExpr`, Lab2 FSM labels reject as generic `ControlFsm`, and
  `Lab3Part1Convolution` rejects as generic `Stencil2d`.
- Red check:
  `cargo test --locked -p spatial-rs-core reserved_ee109_labels_cannot_fall_through_to_generic_scalar_expr -- --nocapture`
  first failed when the new parser test expected only `spatial:E0001`; the
  corrected test now accepts any fail-closed diagnostic and still panics on
  generic fallback.
- Verification passed:
  `cargo test --locked -p spatial-rs-core reserved_ee109_labels_cannot_fall_through_to_generic_scalar_expr -- --nocapture`;
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_reserved_lab_labels_as_generic_feature_names -- --nocapture`;
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_reserved_lab2_fsm_labels_for_control_fsm_feature_kind -- --nocapture`;
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_lab3_label_for_stencil2d_feature_kind -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parses_accepted_ee109_fixture_examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_fsm -- --nocapture`;
  `cargo test --locked -p spatial-rs-core stencil2d -- --nocapture`;
  `cargo test --locked -p spatial-rs-core registry_lists_current_raw_scala_course_adapters_with_retirement_targets -- --nocapture`;
  `cargo fmt --all -- --check`;
  `cargo test --locked --quiet`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: test-only hardening plus roadmap update; no accepted syntax, HLS
  output, manifest, validation roster, raw Scala adapter support, or fresh
  EC2/Vitis evidence changed. The active vendor anchor remains the imported
  `a62eb274` 37-program checkpoint pending future HLS testing.

## 2026-07-05 -- Rust rewrite Lab3 classifier proof inversion

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `da54bcd6e82ce961d6734185c8bc3cc757121e8e`
  (`Route Lab3 classifier through Stencil2d proof`).
- Routed the reserved `Lab3Part1Convolution` classifier adapter through the
  shared `Stencil2dSobelProof` semantic proof before applying a thin exact
  Lab3 surface guard.
- Extended the Stencil2d proof payload to record accumulator and reduce-loop
  surface names, then removed the duplicate Lab3 body-walk matcher helpers.
- Added a fail-closed regression showing a Sobel-shaped reserved Lab3 source
  with renamed accumulator names still rejects as `spatial:E0406`, preventing
  reserved-name broadening while sharing the semantic proof.
- Red check:
  `cargo test --locked -p spatial-rs-core lab3_convolution_adapter_proof_wraps_stencil2d_proof_and_pins_surface -- --nocapture`
  first failed on the missing `lab3_convolution_adapter_proof` wrapper.
- Verification passed:
  `cargo test --locked -p spatial-rs-core lab3_convolution_adapter_proof_wraps_stencil2d_proof_and_pins_surface -- --nocapture`;
  `cargo test -p spatial-rs-core --locked lab3_classifier -- --nocapture`;
  `cargo test -p spatial-rs-core --locked stencil2d_sobel -- --nocapture`;
  `cargo test -p spatial-rs-core --locked parse_accel_routes_lab3_convolution_comment_variant_through_frontend_hir -- --nocapture`;
  `cargo test -p spatial-rs-core --locked raw_lab3_part1_convolution_near_misses_fail_closed -- --nocapture`;
  `cargo test -p spatial-rs-core --locked lab3_convolution_adapter -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_convolution -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen stencil2d_sobel -- --nocapture`;
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_local_raw_lab3_convolution -- --nocapture`;
  `cargo test --locked --quiet`;
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: no generated HLS/manifest drift was observed, no validation-roster
  change, no new raw Lab3 spelling was accepted, and no fresh EC2/Vitis run.
  The active vendor anchor remains the imported `a62eb274` 37-program
  checkpoint pending future HLS testing.

## 2026-07-05 -- Rust rewrite Lab3 raw adapter bridge boundary

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `c36c6d9af59059db1ba1b74a986df6e8ecbb3637`
  (`Move Lab3 raw adapter frontend into bridge`).
- Moved the canonical Lab3 raw-adapter frontend source plus expected
  `ProgramKind::Lab3Part1Convolution` into
  `frontend::lab3_stencil_bridge`.
- Kept raw Scala token proofing quarantined in `source_adapter.rs`, while the
  parser now checks raw-adapter program-kind drift before accepting the
  bridge-owned checked frontend source. Lab2 GEMM keeps its stronger Tile-K
  profile guard.
- Red check:
  `cargo test --locked -p spatial-rs-core local_lab3_convolution_source_proof_carries_frontend_boundary -- --nocapture`
  first failed on the missing `frontend::lab3_stencil_bridge` module, missing
  Lab3 frontend proof field, and missing raw-adapter expected-kind accessor.
- Verification passed:
  `cargo test --locked -p spatial-rs-core local_lab3_convolution_source_proof_carries_frontend_boundary -- --nocapture`;
  `cargo test -p spatial-rs-core --locked local_lab3_convolution -- --nocapture`;
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_local_raw_lab3 -- --nocapture`;
  `cargo test -p spatial-rs-core --locked raw_lab3_part1_convolution_near_misses_fail_closed -- --nocapture`;
  `cargo test -p spatial-rs-core --locked lab2_fixed_gemm_source_proof_records_tile_k_hir_profile -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_local_raw_convolution_preserves_hls_and_manifest -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_local_raw_convolution_static_kernel_border_preserves_hls_and_manifest -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_convolution_frontend_variant_preserves_exact_hls_kernel -- --nocapture`;
  `cargo test --locked --quiet`;
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: no accepted raw Lab3 spelling changed, no generated HLS/manifest
  drift was observed, no validation-roster change, and no fresh EC2/Vitis run.
  The next natural slice is the separate Lab3 classifier-proof inversion around
  `Stencil2dSobelProof`, which should be guarded against reserved-name
  broadening.

## 2026-07-05 -- Rust rewrite shared HLS artifact rendering path

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `a29db3397a6ef598da3e004e42be033785419236`
  (`Share HLS artifact rendering path`).
- Added a shared `RenderedHlsArtifacts` / `HlsRenderPlan` orchestration path so
  host harness compilation and Vitis dry-run project emission write
  `manifest.json`, `kernel.cpp`, and `harness.cpp` from the same checked
  manifest and lowered HLS plan. Direct `emit_kernel` now shares the same
  body-plan dispatcher.
- Preserved explicit Lab3 versus reusable `Stencil2d` harness selection and
  removed the obsolete private program-level wrapper functions left behind by
  the refactor. Plan-level renderer helpers are now test-only.
- Red check:
  `cargo test --locked -p spatial-rs-hls render_hls_artifacts --lib -- --nocapture`
  first failed on missing `render_hls_artifacts` before the shared helper was
  implemented.
- Verification passed:
  `cargo test --locked -p spatial-rs-hls render_hls_artifacts --lib -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls emit::tests --lib -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_convolution_harness_compares_full_256_pixel_oracle -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen stencil2d_sobel_feature_harness_compares_full_oracle -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_copy_4x6_feature_emits_parameterized_rank2_copy_and_harness -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen vitis_dry_run_project_records_tool_profile_without_running_vendor_hls -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-plan-phase5-emit-artifacts`;
  `cargo test --locked --quiet`;
  `cargo fmt --all -- --check`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: no source-acceptance widening, no validation-roster change, no
  generated vendor-evidence promotion, and no fresh EC2/Vitis execution. The
  active vendor anchor remains the imported `a62eb274` 37-program checkpoint
  pending future HLS testing.

## 2026-07-04 -- Rust rewrite reversed tail-min HLS equality pin

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `5c8a10ea4dd511e08b3b7af08a3f4af9827e9a65`
  (`Pin reversed tail min HLS equality`).
- Added generated-HLS and manifest equality tests proving that reversed
  `min(...)` tail-bound spellings normalize to the same output as the
  canonical source for the non-outer-K MemFold tail, serial Tile-K K-tail,
  serial row/column/K-tail, and scheduled Part6 row/column/K-tail cases.
- Refreshed Rust-repo and vault docs so the accepted source surface is described
  as tile-size-first or remaining-first `min(...)`, not only the older exact
  `min(TILE_K, remaining)` order.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen reversed_min`;
  `cargo test --locked -p spatial-rs-core reversed`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check` in the Rust repo and the research vault.
- Boundary: no HLS generator change, no validation-roster change, and no new
  EC2/Vitis run. The active vendor evidence anchor remains the imported
  `a62eb274` 37-program checkpoint pending future HLS testing.

## 2026-07-04 -- Rust rewrite MemFold reversed tail-min source admission

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commits:
  `e4669d896470f73df589e130e0f8eb1576124582`
  (`Refresh raw GEMM proof docs`) and
  `ef07ea51e4e5c4f3da42f6d38cdd0a3aa10a7795`
  (`Accept reversed MemFold tail min bounds`).
- Corrected stale Rust-repo docs so the raw Lab2 GEMM adapter no longer claims
  ownership of duplicate tile-I/O role/window proof. The generated
  frontend/HIR Tile-K classifier remains the semantic authority.
- Confirmed the suspected Tile-K fold/update mismatch class is already a real
  fail-closed boundary: added fold/update-level negative tests for resolved
  partial-product lane drift and C-accumulation lane drift, both of which pass
  without production logic changes.
- Widened the shared MemFold tail-bound matcher to accept both
  `min(tile_size, total - tile_index * tile_size)` and
  `min(total - tile_index * tile_size, tile_size)` while preserving the same
  constant-value and affine-extent checks.
- New acceptance coverage pins reversed `min` argument order for non-outer-K
  `MatrixTileMemFoldTail5x7x5`, serial Tile-K K-tail, and scheduled Tile-K
  row/column/K-tail profiles. The payload profile, generated HLS, manifests,
  validation roster, and current Vitis evidence boundary remain unchanged.
- Red check:
  `cargo test --locked -p spatial-rs-core reversed` first failed on the three
  new reversed-tail classifier tests before the matcher normalization.
- Verification passed:
  `cargo test --locked -p spatial-rs-core reversed`;
  `cargo test --locked -p spatial-rs-core tile_k_fold_update`;
  `cargo test --locked -p spatial-rs-core tile_k_contract`;
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof`;
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k`;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_records_tile_k_hir_profile`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint`;
  `cargo test --locked`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo fmt --all`;
  `git diff --check`.
- Boundary: this is a no-HLS-drift source-admission and proof-coverage slice.
  It does not add generic Spatial `MemFold`, arbitrary dynamic tails, broader
  `par` scheduling, inferred banking, board execution, implementation, timing
  closure, or a new EC2/Vitis run.

## 2026-07-04 -- Rust rewrite raw Lab2 GEMM Tile-K proof authority cleanup

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `2a7fe3bb2798132b0aa506a1f059ed1e61844c88`
  (`Retire duplicate raw GEMM tile proof`).
- Removed the private raw-adapter `Lab2FixedGemmTileIoProof` /
  `Lab2FixedGemmTileCopyProof` / `Lab2FixedGemmTileWindow` proof family and the
  associated token-level tile-load/store role checker from
  `source_adapter.rs`.
- The quarantined raw Lab2 Part5/Part6 adapter now records only the matched raw
  scaffold, normalized `Accel` body, generated frontend source, and expected
  Tile-K profile; the frontend/HIR Tile-K classifier remains the semantic
  authority for rank-2 tile-copy/access-role proof.
- Regression coverage kept the accepted raw wrappers, K-tail and
  row/column/K-tail profiles, generated frontend boundary, expected Tile-K HIR
  profile check, and tile-I/O drift rejection green.
- Verification passed:
  `cargo test --locked -p spatial-rs-core source_adapter::tests::lab2_fixed_gemm -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: this is an internal proof-surface cleanup only. It does not change
  accepted raw syntax, generated frontend source, checked IR, generated HLS,
  manifests, validation membership, imported Vitis evidence, board execution,
  implementation, timing closure, or generic Spatial support. No fresh
  EC2/Vitis run was claimed.

## 2026-07-04 -- Rust rewrite Tile-K numel_k alias normalization

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `6830f9935dc99086587788d41255923d80a8a3e3`
  (`Accept normalized Tile-K numel_k aliases`).
- Widened the normal Rust frontend, not the raw Scala adapter, so Lab2-like
  Tile-K outer-K sources now accept equivalent `numel_k` min aliases:
  `min(TILE_K.to[Int], K - kk)`, `min(K - kk, TILE_K.to[Int])`, and plain
  `min(TILE_K, K - kk)`.
- The alias remains guarded by the active K-offset loop proof; wrong offsets,
  missing `TILE_K`, duplicate aliases, and surrounding invalid Lab2 shapes stay
  fail-closed.
- Red check:
  `cargo test --locked -p spatial-rs-core numel_k_min -- --nocapture` first
  failed on the reversed and plain-`TILE_K` tests.
- Verification passed:
  `cargo test --locked -p spatial-rs-core numel_k_min -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_outer_k_infix_tile_io_near_misses_fail_closed -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: this is a no-HLS-drift frontend source-admission slice. The new
  accepted spellings lower to existing checked Tile-K HIR/HLS payloads, and
  generated kernels, manifests, validation membership, imported Vitis evidence,
  board execution, implementation, timing closure, and generic Spatial support
  are unchanged. No fresh EC2/Vitis run was claimed.

## 2026-07-04 -- Rust rewrite evidence validation after plan-frame sweep

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at commit `871dd7de` (`Guard remaining HLS plan frames`).
- Ran the standalone evidence validator against the active current-head Vitis
  bundle:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-04-current-head-a62eb274-37-program`.
- Result: accepted
  `docs/vitis-validation/2026-07-04-current-head-a62eb274-37-program` with
  `mode=both`, `execution=execute`, and `kernels=37`.
- Boundary: this revalidated imported evidence under the current local code; it
  did not rerun EC2/Vitis or create new vendor artifacts.

## 2026-07-04 -- Rust rewrite remaining HLS plan-frame guard sweep

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `871dd7decaddcd86fe5ade32d4be9fa198be299d`
  (`Guard remaining HLS plan frames`).
- Moved the remaining simple HLS plan-to-frame validation into feature modules:
  `ControlFsm v0` requires exactly one output ABI param in
  `spatial_rs_hls::control_fsm`; `ScalarFold v0` and `ScalarSramTileFold v0`
  require exactly one input ABI param in `spatial_rs_hls::scalar`; and
  `ScalarExpr v0`, `ScalarReduce v0`, and `LutLookup v0` now require empty
  HLS param frames in `spatial_rs_hls::scalar` / `spatial_rs_hls::lut`.
- Removed the remaining ad hoc `find_plan_param` path from `emit.rs`; malformed
  internal plans now fail before kernel or harness rendering instead of
  accepting stale, missing, wrong, swapped, or extra ABI params where those
  shapes are invalid.
- Red tests:
  `cargo test --locked -p spatial-rs-hls emit_control_fsm_plans_reject_malformed_output_param_frames -- --nocapture`
  first failed because the Control FSM harness accepted an extra output param;
  `cargo test --locked -p spatial-rs-hls scalar_fold_plans_reject_malformed_input_param_frames -- --nocapture`
  and
  `cargo test --locked -p spatial-rs-hls scalar_sram_tile_fold_plans_reject_malformed_input_param_frames -- --nocapture`
  first failed because fold harnesses ignored malformed input param frames; and
  `cargo test --locked -p spatial-rs-hls scalar_assign_plans_reject_non_empty_param_frames -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls scalar_reduce_plans_reject_non_empty_param_frames -- --nocapture`,
  plus
  `cargo test --locked -p spatial-rs-hls lut_plans_reject_non_empty_param_frames -- --nocapture`
  first failed because zero-DRAM families rendered C++ while carrying stale
  params.
- Review coverage: `gpt-5.5 xhigh` subagent first ranked ControlFsm,
  Stencil/Lab3, and scalar-multiply families for the guard sequence; a later
  read-only `gpt-5.5 xhigh` audit found the remaining zero-param
  ScalarAssign/ScalarReduce/LUT hole after ControlFsm and fold guards were
  green.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls control_fsm -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls scalar_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls scalar_sram_tile_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls scalar_assign -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls scalar_reduce -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls lut -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  codegen/harness snapshots and Vitis evidence parser tests passed; generated
  kernels, manifests, validation-program membership, and imported Vitis
  evidence are unchanged, so no EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite scalar-multiply plan-frame guards

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `fd9c4de16f1e5a8d681d000828439dc168e61ad9`
  (`Guard scalar multiply plan frames`).
- Moved exact two-param plan-to-frame validation into
  `spatial_rs_hls::dense1d_tile_scalar_mul`,
  `spatial_rs_hls::tile_scalar_mul`, and `spatial_rs_hls::fifo`.
- New guard requires exact ordered ABI params `[input, output]` before Dense1d,
  rank-2 tile scalar, or FIFO kernel/harness rendering.
- Red tests:
  `cargo test --locked -p spatial-rs-hls emit_dense1d_plans_reject_malformed_param_frames -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls emit_dense2d_tile_scalar_mul_kernel_plan_rejects_malformed_param_frames -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls emit_fifo_tile_scalar_mul_kernel_plan_rejects_malformed_param_frames -- --nocapture`
  first failed because swapped params were accepted through unordered
  `find_plan_param` lookups.
- Review coverage: `gpt-5.5 xhigh` subagent ranked the Dense1d,
  Dense2dTileScalarMul, and FIFO two-param family as the next broad remaining
  ABI surface after DotAccum and Stencil/Lab3.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls "scalar_mul" -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  Dense1d, rank-2 tile scalar, and FIFO codegen/harness snapshots plus Vitis
  evidence tests passed; generated kernels, manifests, validation-program
  membership, and imported Vitis evidence are unchanged, so no EC2/Vitis rerun
  was needed.

## 2026-07-04 -- Rust rewrite Stencil/Lab3 plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `c158147627db818321596ac80666ce0153133d6f`
  (`Guard Stencil plan frames`).
- Moved `Stencil2d v0` / `Lab3Part1Convolution` plan-to-frame validation into
  `spatial_rs_hls::stencil2d`.
- New guard requires exact ordered ABI params `[input, output]` before Lab3 or
  generic Stencil2d kernel/harness rendering.
- Red test:
  `cargo test --locked -p spatial-rs-hls emit_lab3_convolution_kernel_plan_rejects_malformed_param_frames -- --nocapture`
  first failed because swapped Lab3 stencil params were accepted through
  unordered `find_plan_param` lookups.
- Review coverage: `gpt-5.5 xhigh` subagent ranked Stencil2d/Lab3 as the next
  highest-risk plan-frame guard after DotAccum because kernel and harness
  emission had split plan/ABI validation paths.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls stencil -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls emit_lab3_convolution_kernel_plan_rejects_malformed_param_frames -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  Stencil/Lab3 codegen/harness snapshots and Vitis evidence tests passed;
  generated kernels, manifests, validation-program membership, and imported
  Vitis evidence are unchanged, so no EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite DotAccum plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `851586fb96063373a35ff6749db93cb56a6d0408`
  (`Guard DotAccum plan frames`).
- Moved `Dense2dTileDotAccum v0` plan-to-frame validation into
  `spatial_rs_hls::dot_accum`.
- New guard requires exact ordered ABI params `[lhs, rhs, output]` before
  kernel or harness rendering.
- Red test:
  `cargo test --locked -p spatial-rs-hls emit_dense2d_tile_dot_accum_kernel_plan_rejects_malformed_param_frames -- --nocapture`
  first failed because swapped DotAccum params were accepted through unordered
  `find_plan_param` lookups.
- Review coverage: `gpt-5.5 xhigh` subagent ranked `Dense2dTileDotAccum` as
  the highest-risk remaining HLS plan-frame guard because it has three DRAM
  params, two same-typed inputs, and both kernel and harness had ad hoc lookup
  paths.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls dot_accum -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  DotAccum codegen/harness snapshots and Vitis evidence tests passed; generated
  kernels, manifests, validation-program membership, and imported Vitis
  evidence are unchanged, so no EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite MemReduce/MemFold fill plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `1810b21ea7be30fe0aafaa704d0756fd94561485`
  (`Guard mem reduction fill plan frames`).
- Moved `MemReduceFill v0` / `MemFoldFill v0` plan-to-frame validation into
  `spatial_rs_hls::mem_reduction_fill`.
- New guard requires exactly one output ABI param whose name matches the
  `MemReductionFillPlan` output before kernel or harness rendering.
- Red tests:
  `cargo test --locked -p spatial-rs-hls mem_reduction_fill_ -- --nocapture`
  first exposed that kernel rendering accepted an extra output param through
  unordered lookup and harness rendering ignored wrong output params entirely.
- Review coverage: `gpt-5.5 xhigh` subagent confirmed the missing
  `mem_reduction_fill_frame_from_plan` boundary, recommended missing/wrong/extra
  output-param cases, and confirmed no `plan.rs` or fresh Vitis work was needed
  if valid generated output stayed identical.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls mem_reduction_fill_ -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen mem_reduction -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen fill -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  fill codegen/harness snapshots and Vitis evidence tests passed; generated
  kernels, manifests, validation-program membership, and imported Vitis
  evidence are unchanged, so no EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite Dense2d MemFold plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `ff9a94a707b0be14c84c160d3a0122c1b2060207`
  (`Guard Dense2d MemFold plan frames`).
- Moved non-outer-K `Dense2dTileMemFold` plan-to-frame validation into
  `spatial_rs_hls::memfold`, matching the earlier rank-2 copy and Tile-K frame
  pattern.
- New guard requires exact ordered ABI params before kernel or harness
  rendering: split-output MemFold must be `[lhs, rhs, cin, out]`, and in-place
  mutable-C MemFold must be `[lhs, rhs, c]` with `c_input == output`.
- Red test:
  `cargo test --locked -p spatial-rs-hls emit_dense2d_tile_memfold_kernel_plan_rejects_malformed_param_frames -- --nocapture`
  first failed because swapped split-output params were accepted through
  unordered `find_plan_param` lookups.
- Review coverage: `gpt-5.5 xhigh` subagent confirmed the missing
  `memfold_frame_from_plan`-style boundary, recommended split-output and
  in-place malformed-plan cases, and called out the dangerous in-place
  `c_in_place = true` / `c_input != output` mismatch.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls memfold_frame_from_plan -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls emit_dense2d_tile_memfold_kernel_plan_rejects_malformed_param_frames -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls memfold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is internal HLS plan admissibility hardening only. Existing
  exact HLS/manifest snapshot tests and Vitis evidence tests passed; generated
  kernels, manifests, validation-program membership, and imported Vitis
  evidence are unchanged, so no EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite Vitis evidence stale-artifact guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `ba3880967858c908c180ee39a32dfbc08d7bd8e2`
  (`Reject stale Vitis evidence artifacts`).
- Hardened `spatial_rs_hls::validate_vitis_evidence_bundle`: after validating
  the summary roster and expected per-kernel paths, it now enumerates the stable
  `sidecars/`, `logs/`, and `reports/` artifact directories and rejects matching
  artifacts whose kernel name is outside the expected roster.
- Red test:
  `cargo test --locked -p spatial-rs-hls vitis_evidence_validator_rejects_unexpected_artifact_kernel -- --nocapture`
  first failed because a clean one-kernel synthetic bundle could silently carry
  `RetiredKernel` sidecar/log/report artifacts.
- Review coverage: two `gpt-5.5 xhigh` subagents checked the next bounded
  slice. One confirmed the older Tile-K fold/update memory was stale because
  the current checkout already has `TileKFoldUpdateProof` and resolved-fact
  tests; the other identified this exact Vitis evidence validator
  stale-artifact gap.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls vitis_evidence_validator_rejects_unexpected_artifact_kernel -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls vitis_evidence_validator -- --nocapture`;
  `cargo test --locked -p ee109-examples run_vitis_validation_validate_evidence_accepts_current_37_checkpoint -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-core -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is local evidence-validator reliability work only. It does not
  change generated HLS C++, manifests, validation-program membership, imported
  Vitis evidence, or the active `a62eb274` 37-program vendor checkpoint, so no
  EC2/Vitis rerun was needed.

## 2026-07-04 -- Rust rewrite raw Lab2 fixed GEMM ingress guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `89b637ede527c9ebedfab4312d926c32dce0daf9`
  (`Bind raw Lab2 GEMM ingress to matched class`).
- Fixed a second raw-adapter binding gap: the exact raw
  `Lab2Part5GEMM` / `Lab2Part6GEMM` adapter now proves runtime profile facts
  and the exact `Accel` island from the matched raw `@spatial class` body,
  rather than from whole-file tokens that could include a donor class or
  object.
- Red test:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_adapters_bind_accel_to_matched_spatial_class -- --nocapture`
  first failed because an empty raw Lab2 GEMM class marker could be paired with
  an exact Part5 donor class body.
- Review coverage: two `gpt-5.5 xhigh` subagents confirmed the fixed-GEMM gap,
  recommended binding the profile and `Accel` proof to the matched class body,
  and judged Lab3's current path suspicious but not exploitable by the same
  empty-marker donor shape because the matched class must already contain the
  unique direct `main`.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_adapters_bind_accel_to_matched_spatial_class -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`;
  `cargo test --locked -p spatial-rs-core local_lab3_convolution_adapter -- --nocapture`;
  `cargo test --locked -p spatial-rs-core source_adapter::tests -- --nocapture`;
  `cargo test --locked -p spatial-rs-core raw_lab2_part -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo clippy -p spatial-rs-core --all-targets --locked -- -D warnings`;
  `cargo clippy -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is local fail-closed raw-adapter hardening only. It does not
  change generated HLS C++, manifests, validation-program membership, or the
  imported 37-program Vitis evidence at `a62eb274`.

## 2026-07-04 -- Rust rewrite raw Lab2 memory-reduction ingress guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `5af91664c6ac7105dfb71971f136c7da662686c8`
  (`Guard raw Lab2 memory reduction ingress`).
- Added direct guard coverage proving the promoted normal-kernel profiles
  `MemReduceFives8` and `MemFoldSevens12` do not widen the quarantined raw
  Scala `Lab2Part1SimpleMemReduce` / `Lab2Part2SimpleMemFold` adapter path.
- Fixed a real raw-adapter binding gap found during review: the Lab2 simple
  `MemReduce` / `MemFold` raw ingress now extracts the direct `main` and
  direct `Accel` body from the matched raw `@spatial class`, instead of pairing
  a global class-name token with a `main`/`Accel` island from another class.
- Red test:
  `cargo test --locked -p spatial-rs-core lab2_memory_reduction_adapters_bind_accel_to_matched_class -- --nocapture`
  first failed because an empty old Lab2 class marker could be paired with an
  exact old accel in a renamed class.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-core raw_lab2_part -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_memory_reduction -- --nocapture`;
  `cargo test --locked -p spatial-rs-core promoted_mem_reduction_profiles_cannot_reuse_reserved_raw_lab2_names -- --nocapture`;
  `cargo test --locked -p spatial-rs-core static_len_and_general_literal_fill -- --nocapture`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo test --locked -p ee109-examples -- --nocapture`;
  `cargo clippy -p spatial-rs-core --all-targets --locked -- -D warnings`;
  `cargo clippy -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this is local fail-closed raw-adapter hardening only. It does not
  change generated HLS C++, manifests, validation-program membership, or the
  imported 37-program Vitis evidence at `a62eb274`.

## 2026-07-04 -- Rust rewrite a62eb274 37-program Vitis refresh

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Source checkpoint:
  `a62eb27443950ed431bfdc19de381c98560352f4`
  (`Promote MemReduce fill canaries to validation roster`).
- Promoted `MemReduceFives8` and `MemFoldSevens12` into
  `ee109_examples::validation_programs()`, growing the official roster from 35
  to 37 programs.
- EC2/Vitis proof:
  host `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`), Vitis 2025.1, Rust/Cargo 1.75.0, target
  `xc7z020-clg400-1`, 10 ns clock target.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-04-current-head-a62eb274/repo`.
- Imported evidence directory:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-04-current-head-a62eb274-37-program/`.
- Result: all 37 validation kernels reported `returncode=0`, `csim=true`, and
  `csynth=true`; the repo-local validator reported
  `VALIDATED ... mode=both execution=execute kernels=37`.
- Boundary: this proves vendor C simulation and HLS synthesis for the exact
  37-program roster only. It does not widen exact raw Lab2 source-adapter
  admission, generic Spatial `MemReduce`/`MemFold` bodies, dynamic bounds,
  rank-2 reductions, banking, scheduling, board execution, implementation,
  timing closure, or performance claims.

## 2026-07-04 -- Rust rewrite Tile-K plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `2841cc56ac3a081cae56e03f8b9a1ef04b39998a` (`Guard Tile-K plan frames`).
- Moved Tile-K HLS body/ABI-param adaptation into `spatial_rs_hls::tile_k`
  via `tile_k_frame_from_plan`.
- New fail-closed coverage rejects malformed internal Tile-K plans with
  swapped, missing, or extra ABI params unless they are exactly
  `[lhs, rhs, c_inout]` in order before either kernel or harness rendering.
- Red test:
  `cargo test --locked -p spatial-rs-hls tile_k_frame_from_plan_requires_exact_ordered_params -- --nocapture`
  first failed because `tile_k_frame_from_plan` did not exist.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_validate_evidence_accepts_current_checkpoint -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_7a350983_checkpoint -- --nocapture`;
  `cargo run --locked -p ee109-examples --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-04-current-head-7a350983-35-program --mode both`;
  `git diff --check` in the Rust repo.
- A `gpt-5.5`/`xhigh` reviewer subagent reported no blocking issues; one
  reviewer suggestion added the explicit missing-param assertion.
- Boundary: this is no-HLS-drift backend structure. It does not change accepted
  syntax, generated valid HLS, manifests, validation membership, imported Vitis
  evidence, or the active `7a350983` vendor-HLS anchor. No fresh EC2/Vitis run
  was needed.

## 2026-07-04 -- Rust rewrite Tile-K fold/update proof

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `52953ae0767bf6e94fec59171d6ce0d941b184b7` (`Name Tile-K fold update proof`).
- Replaced the Tile-K fold schedule-only helper with a named
  `TileKFoldUpdateProof`.
- The new proof records row/column/K update domains, effective bounds, local
  LHS/RHS/C/partial tile roles, and serial/scheduled partial-product par
  factors after the existing partial-product and C-accumulation resolved-fact
  checks pass.
- Red test:
  `cargo test -p spatial-rs-core --locked tile_k_fold_update_proof_records_domains_accesses_and_profile_schedule -- --nocapture`
  first failed because `TileKFoldUpdateProof` and `prove_tile_k_fold_update`
  did not exist.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-core -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen outer_k -- --nocapture`;
  `cargo clippy -p spatial-rs-core --all-targets --locked -- -D warnings`;
  `git diff --check` in the Rust repo.
- A `gpt-5.5`/`xhigh` reviewer subagent reported no blocking issues.
- Boundary: this is no-HLS-drift frontend/HIR proof structure. It does not
  change accepted syntax, checked payloads, generated HLS, manifests,
  validation membership, imported Vitis evidence, or the active `7a350983`
  vendor-HLS anchor. No fresh EC2/Vitis run was needed.

## 2026-07-04 -- Rust rewrite Dram2dCopy plan-frame guard

- Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial`.
- Rust commit:
  `88e33a0959478eba4bf1114517aa314fd5f11699` (`Guard Dram2dCopy plan frames`).
- Added a named `Dram2dCopyPlan` HLS body and moved rank-2 copy
  plan-to-renderer adaptation into `spatial_rs_hls::rank2_copy` via
  `rank2_copy_frame_from_plan`.
- New fail-closed coverage rejects malformed internal rank-2 copy plans with
  swapped or extra ABI params before either kernel or harness rendering.
- Red test:
  `cargo test --locked -p spatial-rs-hls emit::tests::dram2d_copy_harness_plan_rejects_swapped_param_order -- --nocapture`
  first failed because the swapped `[dst, src]` internal plan still rendered.
- Verification passed:
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-hls -- --nocapture`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `git diff --check` in the Rust repo.
- A `gpt-5.5`/`xhigh` reviewer subagent reported no blocking issues.
- Boundary: this is no-HLS-drift backend structure. It does not change accepted
  syntax, generated valid HLS, manifests, validation membership, imported Vitis
  evidence, or the active `7a350983` vendor-HLS anchor. No fresh EC2/Vitis run
  was needed.

## 2026-07-04 -- Rust rewrite 7a350983 current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- EC2/Vitis source snapshot:
  `7a350983c3a8b0bc6a8a6fcc4603fc507df7f95a` (`Fix EE109 documentation drift`).
- Rust evidence/import commit:
  `73032944727e3024fddd154d235c6217040ffbf1` (`Record 7a350983 Vitis evidence`).
- The imported evidence directory is
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-04-current-head-7a350983-35-program/`.
- This promotes the 35-program current-head vendor-HLS anchor after the raw
  Lab2 row/column/K-tail adapter, raw Lab3 static-border adapter, affine-index
  helper cleanup, MemReduce/MemFold literal-fill widening, and documentation
  cleanup.

EC2/Vitis proof:
- Host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`).
- Toolchain: `/tools/Xilinx/2025.1/Vitis/settings64.sh`, Vitis runner
  `vitis-run v2025.1`, HLS build `2025.1 6135595`, Rust/Cargo 1.75.0,
  target `xc7z020-clg400-1`, 10 ns clock target.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-04-current-head-7a350983/repo`.
- Remote command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-current-head-7a350983`.
- Result: all 35 validation kernels reported Vitis `csim_design` and
  `csynth_design` success. The remote and local evidence validators reported
  `VALIDATED ... mode=both execution=execute kernels=35`.

Proof:
- Remote EC2 compatibility gate passed:
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`.
- Local evidence anchor tests passed:
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_7a350983_checkpoint -- --nocapture`
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_7a350983_as_current_vendor_anchor -- --nocapture`.
- Local evidence CLI validation passed:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-04-current-head-7a350983-35-program --mode both`.
- Local hygiene passed: `cargo fmt --all -- --check`, `git diff --check` in the
  Rust repo, and `git diff --check` in the vault.

Boundary:
- This is a vendor-HLS stability refresh for the exact 35-program current-head
  validation roster.
- It proves Vitis C simulation and HLS synthesis only; it does not prove board
  execution, Vivado implementation, place-and-route, timing closure,
  performance optimality, arbitrary GEMM, broad Scala source compatibility, or
  completion of the full Spatial rewrite.
- The raw Lab2 GEMM and raw Lab3 teaching-wrapper adapters are still covered by
  parser/HLS/manifest equality against canonical Vitis-proven canaries, not by
  separate validation-roster members.

## 2026-07-04 — Rust rewrite affine HIR index predicate helper

- Added reusable `IndexUseFact` predicates for lane-symbol, constant-value, and
  tile-plus-lane affine index shapes in the Rust rewrite frontend/HIR layer.
- Migrated duplicated classifier-local predicates in rank-1 indexed writes,
  rank-2 Tile-K/MemFold access checks, shared rank-2 tile-copy role checks, and
  Stencil2d row/column/range checks to the shared HIR API.
- Red test:
  `cargo test -p spatial-rs-core --locked resolved_hir_exposes_reusable_affine_index_predicates -- --nocapture`
  first failed because the `IndexUseFact` methods did not exist.
- Focused verification passed:
  `cargo test -p spatial-rs-core --locked resolved_hir_exposes_reusable_affine_index_predicates -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank1_indexed_write_lane -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank2_tile_copy_role -- --nocapture`;
  `cargo test -p spatial-rs-core --locked stencil2d_local_window -- --nocapture`.
- Broader local verification passed:
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo fmt --all -- --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check` in the Rust repo and the vault.
- Boundary: this is no-HLS-drift compiler infrastructure. It does not change
  accepted syntax, checked payloads, generated HLS, validation roster, imported
  Vitis evidence, or the active `eb4f6236` vendor anchor.

## 2026-07-04 — Rust rewrite MemReduce/MemFold static literal widening

- Selected the first post-`eb4f6236` semantic widening slice after
  `gpt-5.5`/`xhigh` subagent review: broaden `MemReduceFill v0` /
  `MemFoldFill v0` constant-fill support without opening generic
  `MemReduce`/`MemFold`.
- Updated the Rust classifier and checked-IR validation so the supported
  rank-1 `Int` accumulator/temp/output shape may use any supported static
  length and any integer literal temp fill. New positive canaries:
  `MemReduceFives8` (`LEN=8`, `ROUNDS=3`, fill `5`) and `MemFoldSevens12`
  (`LEN=12`, `ROUNDS=4`, fill `7`).
- Added fail-closed coverage for nonliteral fills, unsupported lengths, extra
  local memories/effects, rank-2 reductions, missing stores, bad MemFold
  zero-initialization, and the existing narrow Spatial-ish Lab2 spelling.
- Added local HLS emission/host-harness coverage proving the carried array
  length, step count, lane name, and fill value. This does not add validation
  roster members or fresh EC2/Vitis evidence; the active vendor anchor remains
  `docs/vitis-validation/2026-07-04-current-head-eb4f6236-35-program/`.
- Local verification passed:
  `cargo test -p spatial-rs-core --locked mem_reduction -- --nocapture`;
  `cargo test -p spatial-rs-core --locked lab2_simple_memory_reduction_spatialish_sugar_near_misses_stay_fail_closed -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked mem_reduction -- --nocapture`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo fmt --all -- --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check` in the Rust repo and the vault.
- Boundary: exact raw Lab2 Part1/Part2 Scala adapters remain fixed to the
  all-ones 16-lane lab wrappers. This is still not generic Spatial
  `MemReduce`/`MemFold`, arbitrary reducer/fold bodies, dynamic bounds, rank-2
  reductions, banking, scheduling, broad Scala compatibility, board execution,
  Vivado implementation, or timing closure.

## 2026-07-04 — Rust rewrite eb4f6236 current-head Vitis refresh

- Re-ran the full 35-program EE109 validation roster on
  `[ec2-host — see private/ec2-lane.md]` using Vitis/Vivado 2025.1
  and Rust/Cargo 1.75. Source snapshot: Rust commit `eb4f6236` on branch
  `David/HLS-spatial`.
- Remote workspace:
  `/home/ubuntu/spatial-rs-runs/current-head-20260704-eb4f6236/spatial-rs`.
  Remote command used the existing runner:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out /home/ubuntu/spatial-rs-runs/current-head-20260704-eb4f6236/evidence`.
- EC2/Vitis result: all 35 kernels reported `returncode=0`,
  `csim=true`, and `csynth=true`. This covers Vitis C simulation and HLS
  synthesis for the exact EE109 MVP validation roster only.
- Imported evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-04-current-head-eb4f6236-35-program/`.
  The imported bundle is about 686 MB and contains per-kernel project
  directories plus `logs/`, `reports/`, `sidecars/`, `summary-both.md`, and
  `summary-both.json`.
- Repo-local validation passed:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-04-current-head-eb4f6236-35-program --mode both`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_eb4f6236_checkpoint -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_eb4f6236_as_current_vendor_anchor -- --nocapture`;
  `cargo test --locked -p ee109-examples --test run_vitis_validation run_vitis_validation_validate_evidence_accepts_current_checkpoint -- --nocapture`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo fmt --all -- --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `git diff --check`.
- Boundary: this refresh supersedes `c862e57a` as the active current-head
  vendor-HLS evidence anchor. It does not claim board execution, Vivado
  implementation, timing closure, generic Spatial compatibility, broad Scala
  source compatibility, performance optimality, or any roster expansion beyond
  the existing 35 validation programs.

## 2026-07-04 — Rust rewrite MemReduce/MemFold fill HLS harness helper

- Moved the `MemReduceFill v0` and `MemFoldFill v0` host-harness renderer
  behind `crates/spatial-rs-hls/src/mem_reduction_fill.rs`, beside the existing
  fill kernel frame. `emit.rs` now lowers to the HLS plan, builds a fill
  harness frame, and delegates to the fill helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked mem_reduction_fill_harness_uses_entry_output_expected_values_and_display_name -- --nocapture`
  first failed because the fill harness frame/function did not exist; focused
  rerun passed after moving the expected-array/oracle comparison into the
  helper;
  `cargo test -p spatial-rs-hls --locked mem_reduction_fill -- --nocapture`;
  `cargo fmt --all`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated fill kernel/harness text, manifests, validation roster,
  and imported Vitis evidence are unchanged. No EC2/Vitis run is needed for
  this helper extraction.

## 2026-07-04 — Rust rewrite scalar-family HLS harness helper

- Moved the `ScalarExpr v0`, `ScalarReduce v0`, `ScalarFold v0`, and
  `ScalarSramTileFold v0` host-harness renderers behind
  `crates/spatial-rs-hls/src/scalar.rs`, beside the existing scalar kernel
  frames. `emit.rs` now lowers to HLS plans, builds scalar harness frames, and
  delegates to the scalar helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked scalar_ -- --nocapture`
  first failed because the scalar harness frame/functions did not exist, then
  failed once more because the new fold-harness assertions used the wrong
  oracle input vector; focused rerun passed after correcting them to the
  deterministic `scalar_fold_inputs(8)` row;
  `cargo fmt --all`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated scalar-family kernel/harness text, manifests, validation
  roster, and imported Vitis evidence are unchanged. No EC2/Vitis run is
  needed for this helper extraction.

## 2026-07-04 — Rust rewrite LUT HLS harness helper

- Moved the square/non-square lab LUT and `LutBiasLookup`
  `LutLookup v0` host-harness renderer behind
  `crates/spatial-rs-hls/src/lut.rs`, beside the existing LUT kernel frame.
  `emit.rs` now lowers to the HLS plan, builds a LUT harness frame, and
  delegates to the LUT helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked lut_harness_uses_entry_symbol_ports_points_and_display_name -- --nocapture`
  first failed because the LUT harness frame/function did not exist, then
  failed once more because the new assertion used the wrong inherited
  sample-point expectation for a `2 x 4` table; focused rerun passed after
  correcting the assertion to the actual bottom-right/center row-major oracle
  cases;
  `cargo test -p spatial-rs-hls --locked lut -- --nocapture`;
  `cargo fmt --all`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated LUT kernel text, manifests, validation roster, and
  imported Vitis evidence are unchanged. No EC2/Vitis run is needed for this
  helper extraction.

## 2026-07-04 — Rust rewrite Dense1d HLS harness helper

- Moved the `Lab1Part2DramSramExample` / `DenseScale64`
  `Dense1dScalarMul v0` host-harness renderer behind
  `crates/spatial-rs-hls/src/dense1d_tile_scalar_mul.rs`, beside the existing
  rank-1 Dense1d kernel frame. `emit.rs` now lowers to the HLS plan, resolves
  ABI params, builds a Dense1d harness frame, and delegates to the Dense1d
  helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked dense1d_tile_scalar_mul_harness_uses_entry_symbol_ports_cases_and_display_name -- --nocapture`
  first failed because the Dense1d harness frame/function did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked dense1d -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen dense -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  vault `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated Dense1d kernel text, manifests, validation roster, and
  imported Vitis evidence are unchanged. No EC2/Vitis run is needed for this
  helper extraction.

## 2026-07-04 — Rust rewrite Dense2dTileMemFold HLS harness helper

- Moved the non-outer-K `Dense2dTileMemFold v0` host-harness renderer behind
  `crates/spatial-rs-hls/src/memfold.rs`, beside the existing MemFold kernel
  frame. `emit.rs` now lowers to the HLS plan, resolves ABI params, builds a
  MemFold harness frame, and delegates to the MemFold helper.
- The helper covers the existing split-C, tail, exact `FixPt[TRUE,_24,_8]`,
  and explicit in-place C harness paths. A parallel exploratory run of two
  overlapping MemFold harness filters produced one transient missing-harness
  executable error from shared output-path contention; the same MemFold filter
  passed when rerun sequentially.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked memfold_harness_ -- --nocapture`
  first failed because the MemFold harness frame/function did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked memfold -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  vault `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated non-outer-K MemFold kernel text, manifests, validation
  roster, and imported Vitis evidence are unchanged. No EC2/Vitis run is
  needed for this helper extraction.

## 2026-07-04 — Rust rewrite Dense2dTileDotAccum HLS harness helper

- Moved the `MatrixTileAccum4x6x5` host-harness renderer behind
  `crates/spatial-rs-hls/src/dot_accum.rs`, beside the existing rank-2
  dot-accum kernel frame. `emit.rs` now lowers to the HLS plan, resolves ABI
  params, builds a DotAccum harness frame, and delegates to the DotAccum
  helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked dot_accum_harness_uses_entry_symbol_ports_cases_and_display_name -- --nocapture`
  first failed because the DotAccum harness frame/function did not exist, then
  failed once more because the new assertion used the wrong oracle row; focused
  rerun passed after correcting the assertion to the actual row-major
  dot-product output;
  `cargo test -p spatial-rs-hls --locked dot_accum -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_accum -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  vault `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: generated `MatrixTileAccum4x6x5` kernel text, manifests,
  validation roster, and imported Vitis evidence are unchanged. No EC2/Vitis
  run is needed for this helper extraction.

## 2026-07-04 — Rust rewrite Dense2dTileDotAccum access-role fact gate

- Committed the previous no-HLS-drift Rust checkpoint as
  `5c21c485` (`Record no-HLS-drift helper checkpoints`) on
  `David/HLS-spatial`, and the matching research-vault record as `c8f4c4c`
  (`Record spatial-rs no-HLS-drift checkpoints`) on vault `main`.
- Hardened `Dense2dTileDotAccum v0` classifier admission by routing the lhs
  load, rhs load, and final accumulator store through resolver-backed rank-2
  access facts after the structural matchers succeed. The proof now checks
  local/global access grouping, same parent statement, loop-symbol identity,
  and const-backed stride provenance before reconstructing the existing checked
  payload.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-core --locked dense2d_dot_accum_lhs_load_fact_matcher_rejects_equal_valued_wrong_row_coefficient_symbol -- --nocapture`
  first failed because the DotAccum fact spec/helper did not exist; focused
  rerun passed;
  `cargo test -p spatial-rs-core --locked dense2d_dot_accum -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_accum -- --nocapture`.
- Boundary: generated `MatrixTileAccum4x6x5` HLS, manifests, validation
  roster, and imported Vitis evidence are unchanged. No EC2/Vitis run is
  needed for this proof-boundary cleanup.

## 2026-07-04 — Rust rewrite Dense2dTileScalarMul load/store fact gate

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Hardened `Dense2dTileScalarMul v0` classifier admission by routing the
  load/store tile-copy phases through the shared resolver-backed rank-2
  tile-copy fact helper after the structural matcher succeeds. The proof now
  checks local/global access grouping, same parent statement, loop-symbol
  identity, and const-backed stride provenance before reconstructing the
  existing checked payload.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-core --locked dense2d_tile_scalar_store_fact_matcher_rejects_equal_valued_wrong_row_coefficient_symbol -- --nocapture`
  first failed because the Dense2dTileScalar fact spec/helper did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-core --locked dense2d_tile_scalar -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_scale -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank2 -- --nocapture`.
- Boundary: generated `MatrixTileScale4x6` HLS, manifests, validation roster,
  and imported Vitis evidence are unchanged. No EC2/Vitis run is needed for
  this proof-boundary cleanup.

## 2026-07-04 — Rust rewrite Tile-K HLS harness helper

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Moved the `Dense2dTileKMemFold v0` host-harness renderer behind
  `crates/spatial-rs-hls/src/tile_k.rs`, beside the existing Tile-K kernel
  frame/body helpers. `emit.rs` now lowers to the HLS plan, resolves ABI params,
  builds a harness frame, and delegates to the Tile-K helper. The existing
  `PASS ..._kernel` display behavior is intentionally preserved.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked tile_k_harness_uses_entry_symbol_fixpt_inout_shape_and_oracle_cases -- --nocapture`
  first failed because the Tile-K harness frame/function did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked tile_k_harness -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6_fixed_32 -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation tile_k -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`.
- Boundary: generated Tile-K kernel text, manifests, validation roster, and
  imported Vitis evidence are unchanged. No EC2/Vitis run is needed for this
  helper extraction.

## 2026-07-04 — Rust rewrite TileScalarMul HLS harness helper

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Moved the `Dense2dTileScalarMul v0` / `MatrixTileScale4x6` host-harness
  renderer behind `crates/spatial-rs-hls/src/tile_scalar_mul.rs`, beside the
  existing rank-2 tile-scalar kernel frame. `emit.rs` now lowers to the HLS
  plan, resolves ABI params, builds a harness frame, and delegates to the
  tile-scalar helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked tile_scalar_mul_harness_uses_entry_symbol_ports_cases_and_display_name -- --nocapture`
  first failed because the tile-scalar harness frame/function did not exist;
  focused rerun passed through
  `cargo test -p spatial-rs-hls --locked tile_scalar_mul -- --nocapture`;
  integration rerun passed
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_scale -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`.
- Boundary: generated `MatrixTileScale4x6` kernel text, manifests, validation
  roster, and imported Vitis evidence are unchanged. No EC2/Vitis run is needed
  for this helper extraction.

## 2026-07-04 — Rust rewrite MemFold full-kernel snapshot guard

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Added an exact full emitted-kernel snapshot for
  `MatrixTileMemFoldInPlaceFixPt4x6x5`, the non-outer-K in-place
  `FixPt[TRUE,_24,_8]` MemFold path. This protects the full signature,
  mutable `c` pointer interface, AXI pragmas, local tile declarations, preload,
  partial-product, accumulation, and final store text before deeper ABI/frame
  helper work.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_inplace_c_memfold_matches_stable_full_hls_snapshot -- --nocapture`
  first failed because the full-kernel expected snapshot helper did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked memfold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`.
- Boundary: this is a test-coverage guard only. Generated MemFold HLS,
  manifests, validation roster, and imported Vitis evidence are unchanged. No
  EC2/Vitis run is needed.

## 2026-07-04 — Rust rewrite Stencil2d/Lab3 HLS harness helper

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Moved the Lab3 convolution and reusable `Stencil2d v0` Sobel host-harness
  renderers behind `crates/spatial-rs-hls/src/stencil2d.rs`, beside the
  existing Sobel kernel frame. `emit.rs` now lowers to the HLS plan, builds a
  harness frame, and delegates to the Stencil2d helper.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked stencil2d_sobel_harnesses_use_entry_symbol_display_name_and_full_cases -- --nocapture`
  first failed because the Stencil2d harness frame/functions did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3 -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen stencil2d -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked stencil2d -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`.
- Boundary: generated Lab3/Stencil2d kernel text, manifests, validation roster,
  and imported Vitis evidence are unchanged. The active vendor evidence anchor
  remains `c862e57a`; no EC2/Vitis run is needed for this helper extraction.
- Next recommended action after committing the pending Rust/vault checkpoints:
  add a full non-outer-K MemFold kernel snapshot before deeper ABI/frame work,
  then continue small helper-boundary or proof-boundary slices.

## 2026-07-04 — Rust rewrite FIFO HLS harness helper

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit remains pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- Moved the FIFO tile-scalar-multiply host harness renderer behind
  `crates/spatial-rs-hls/src/fifo.rs`, beside the existing FIFO kernel frame.
  `emit.rs` remains the dispatcher and plan-to-frame adapter. This is a
  backend helper-boundary cleanup only.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-hls --locked fifo_tile_scalar_mul_harness_uses_entry_symbol_ports_cases_and_display_name -- --nocapture`
  first failed because the FIFO harness frame/function did not exist;
  focused rerun passed;
  `cargo test -p spatial-rs-hls --locked fifo -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen fifo -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test --locked -p ee109-examples --quiet`.
- Boundary: no generated FIFO kernel text, manifest, validation roster, or
  imported Vitis evidence changed. The active vendor evidence anchor remains
  `c862e57a`; no EC2/Vitis run is needed for this helper extraction.
- Subagent review: two `gpt-5.5 xhigh` read-only scouts recommended finishing
  the FIFO harness extraction before starting a Stencil2d/Lab3 harness helper
  slice, and noted that future ABI/frame work should either extract the
  Stencil2d/Lab3 Sobel harness into `stencil2d.rs` or first add a full
  non-outer-K MemFold kernel snapshot.

## 2026-07-03 — Rust rewrite raw Lab3 direct-main Accel guard

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit is still pending because the Codex app approval/usage gate is
  blocking escalated Git index writes.
- The quarantined raw Scala scanner now requires the accepted raw Lab3
  `Accel` island to be a direct top-level statement in `main`, not identical
  accelerator text hidden inside a helper. This closes the direct-parent
  source-scope hole found after the Stencil2d proof/preflight cleanup.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-core --locked local_lab3_convolution_adapter_rejects_accel_hidden_inside_main_helper -- --nocapture`
  first failed because the hidden helper `Accel` was accepted;
  focused rerun passed;
  `cargo test -p spatial-rs-core --locked source_adapter::tests:: -- --nocapture`;
  `cargo test -p spatial-rs-core --locked raw_lab -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`.
- Boundary: this is source-scope hardening only. No accepted canonical payload,
  generated HLS C++, manifest, validation roster, or imported Vitis evidence
  changed. The active vendor evidence anchor remains `c862e57a`; no EC2/Vitis
  run is needed until generated HLS or validation membership changes.
- Next recommended action after committing the pending Rust/vault checkpoints:
  take a small HLS ABI/frame helper reliability slice before widening syntax.

## 2026-07-03 — Rust rewrite Stencil2d proof preflight

- Verified local working-tree checkpoint in
  `/Users/david/Documents/David_code/spatial-rs` on `David/HLS-spatial`.
  Rust commit is pending because the Codex app approval/usage gate rejected the
  escalated `git add` needed to write the Git index.
- `Stencil2d v0` now records the accepted Sobel source shape and resolved
  row/column/shift local-window facts in a private classifier proof object
  before rebuilding the same checked `Stmt::Stencil2d` payload. The proof
  covers loop-domain identity, row-range line-buffer loads/stores, `RegFile`
  reset/shift effects, shift/line-output accesses, and Sobel/window reduction
  reads.
- Checked IR now rejects flattened stencil extents whose `ROWS * COLS` product
  overflows or exceeds the supported HLS/harness `int` indexing range, before
  HLS planning.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-core --locked stencil2d_sobel_proof_records_shape_payload_and_resolved_domains -- --nocapture`
  first failed because the proof helpers did not exist;
  `cargo test -p spatial-rs-core --locked stencil2d_sobel_proof_records_shape_payload_and_resolved_domains -- --nocapture`;
  `cargo test -p spatial-rs-core --locked checked_ir_rejects_stencil2d_extent_product_overflow -- --nocapture`;
  `cargo test -p spatial-rs-core --locked stencil2d_local_window_proof_rejects_non_affine_line_buffer_read -- --nocapture`;
  `cargo test -p spatial-rs-core --locked stencil2d -- --nocapture`;
  `cargo test -p spatial-rs-core --locked lab3 -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`.
- Boundary: no accepted syntax, generated HLS C++, manifest, validation roster,
  or imported Vitis evidence changed. The active vendor evidence anchor remains
  `c862e57a`; no EC2/Vitis run is needed for this proof/preflight cleanup until
  the generated HLS or validation roster changes.
- Next recommended action after committing this checkpoint: either add one more
  stale-fact/source-scope negative around raw Lab3 direct-parent `Accel`
  handling, or take a small HLS ABI/frame helper reliability slice.

## 2026-07-03 — Rust rewrite raw Lab3 source proof

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit
  `0f16af3e7b042554369ce69972da580078651c6a` (`Record raw Lab3 source
  proof`). The known local `Lab3Part1Convolution` teaching wrapper now records
  a scoped source proof before canonical `Lab3Part1Convolution` emission,
  rather than relying on an exact raw wrapper match.
- The proof records direct class-level image facts before `main`, main setup
  facts before the single `Accel`, and local-window facts for `lb`, `sr`,
  `lineOut`, `kh`, `kv`, row/column/shift loops, two-row/two-column border
  handling, and the `par 16` store shape. Host print/oracle scaffolding may
  vary, but moved class/setup facts and changed accelerator/window shape are
  rejected fail-closed.
- `gpt-5.5 xhigh` review found two real scoping risks during the loop:
  shell facts were initially accepted outside `main`, and class image facts
  were initially accepted inside helper scope. Both were fixed and re-reviewed;
  the final spec and code-quality reviewers reported no remaining findings.
- Verification passed locally:
  RED
  `cargo test -p spatial-rs-core --locked source_adapter::tests:: -- --nocapture`
  first exposed shell facts accepted outside `main`;
  follow-up RED exposed class facts accepted inside helper scope;
  `cargo test -p spatial-rs-core --locked source_adapter::tests:: -- --nocapture`;
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_local_raw_lab3_convolution -- --nocapture`;
  `cargo test -p spatial-rs-core --locked raw_lab3_part1_convolution_near_misses_fail_closed -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_local_raw_convolution_preserves_hls_and_manifest -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_convolution_kernel_matches_stable_hls_snapshot -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_convolution_harness_compares_full_256_pixel_oracle -- --nocapture`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: no accepted HLS payload, generated C++, manifest, validation
  roster, or imported Vitis evidence changed. The active vendor evidence
  anchor remains `c862e57a`; no EC2/Vitis run was needed for this
  source-proof cleanup. Next recommended slice: promote the fixed
  `Stencil2d`/local-window path into HIR/fact proof form and add the stencil
  extent/product overflow guard found by review.

## 2026-07-03 — Rust rewrite raw Lab2 GEMM Tile-K profile bridge

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit
  `47f9baa43f455f6078a514098f25ad7815a58298` (`Bridge raw GEMM to Tile-K
  profiles`). The accepted raw Lab2 Part5/Part6 GEMM wrappers now validate
  their generated frontend source against the checked-IR Tile-K profile that
  the wrapper proof expects, instead of trusting only normalized source text.
- Added neutral `Dense2dTileKMemFoldProfile` vocabulary in checked IR while
  keeping `TileKMemFoldProof` private. `source_adapter` records the expected
  profile, `parser` checks the compiled checked program against that profile,
  and the classifier no longer owns the stable profile vocabulary.
- Covered the four accepted raw profile mappings: Part5 fixed32 ->
  `SerialFullK`, Part6 fixed32 -> `Part6ScheduledFullK`, Part5 K-tail34 ->
  `SerialKTail`, and Part6 K-tail34 -> `Part6ScheduledKTail`.
- `gpt-5.5 xhigh` reviewers found the intended compiler boundary sound after
  follow-up fixes: no `compile_source` call remains in `source_adapter`, the
  classifier tests no longer depend on the raw adapter, the profile marker is
  carried into the parser check, and the profile names no longer encode a
  specific dimension while the matcher still supports parameterized aliases.
- Verification passed locally:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`;
  `cargo test --locked -p spatial-rs-core tile_k_contract -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part5_gemm_fixed_32 -- --nocapture`;
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`;
  `cargo test --locked -p spatial-rs-core raw_lab2_part5_fixed_wrapper_near_misses_fail_closed -- --nocapture`;
  `cargo test --locked -p spatial-rs-core raw_lab2_part6_fixed_wrapper_near_misses_fail_closed -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part -- --nocapture`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation active_docs_name_c862e57a_as_current_vendor_anchor -- --nocapture`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: no accepted syntax, generated HLS, manifest, validation roster, or
  imported Vitis evidence changed. The active vendor evidence anchor remains
  `c862e57a`; no EC2/Vitis run was needed for this profile-bridge cleanup.

## 2026-07-03 — Rust rewrite raw Lab2 GEMM tile-I/O proof facts

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit
  `38c5ebfddcc984d4c1af5407824d0246cf11f3e0` (`Record raw GEMM tile IO
  proof`). The fixed raw Lab2 Part5/Part6 GEMM source proof now records exact
  rank-2 tile-I/O role/window facts for A/B/C preload and C store before the
  existing normalized `Accel`-body equality guard is trusted.
- Added direct proof coverage that both raw Part5 and raw Part6 expose the
  expected local/global roles and `(mm,kk)`, `(kk,nn)`, and `(mm,nn)` windows,
  plus fail-closed drift tests for C-store role drift, C-preload window drift,
  and B-load window drift. Updated README, the EE109 MVP plan, the fixture
  matrix, the Rust rewrite architecture note, and the full-roadmap plan to
  describe this as source-adapter proof tightening only.
- `gpt-5.5 xhigh` subagents reviewed the slice selection and final diff. The
  final review found no blocking correctness issue and identified one stale
  architecture-doc sentence about raw GEMM being only `32x32x32`; that wording
  is now corrected to include the exact named `K=34` tail profile.
- Verification passed locally:
  RED
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_records_rank2_tile_io_roles -- --nocapture`
  first failed on the missing proof fields;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_records_rank2_tile_io_roles -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_tile_io_proof_rejects_role_drift -- --nocapture`;
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`;
  `cargo test --locked -p spatial-rs-core --quiet`;
  `cargo test --locked -p ee109-examples --quiet`;
  `cargo test --locked -p spatial-rs-hls --quiet`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation active_docs_name_c862e57a_as_current_vendor_anchor -- --nocapture`;
  `cargo fmt --all -- --check`;
  `git diff --check`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`.
- Boundary: no accepted syntax, checked payload, generated HLS, manifest,
  validation roster, or imported Vitis evidence changed. The active vendor
  evidence anchor remains `c862e57a`. Next recommended compiler slice: bridge
  the accepted raw Part5/Part6 variants to the existing `TileKProfile` HIR
  proof vocabulary without widening raw Scala syntax.

---

## 2026-07-03 — Rust rewrite ScalarReduce/ScalarFold proof facts

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `3498213` (`Record scalar reduction proof
  facts`). The `ScalarReduce v0` and `ScalarFold v0` classifier paths now carry
  private proof objects before checked IR construction. The proofs record
  accepted output/input roles, reduction/fold indices, static length, tile, and
  `par` bounds.
- Added direct proof tests for `ScalarReduceSum16` and `ScalarFoldTileSum32`
  source shapes. Updated README, the EE109 MVP plan, and the Rust rewrite
  architecture note to describe the scalar proof boundary without claiming
  broader scalar reduction/fold syntax.
- Verification passed locally:
  RED
  `cargo test --locked -p spatial-rs-core scalar_reduce_proof_records_output_index_and_bounds -- --nocapture`
  first failed on missing proof functions;
  `cargo test --locked -p spatial-rs-core scalar_reduce -- --nocapture`;
  `cargo test --locked -p spatial-rs-core scalar_fold -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen scalar -- --nocapture`;
  `cargo test --locked -p spatial-rs-core`;
  `cargo test --locked -p ee109-examples`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: no accepted syntax, checked payload, generated HLS, manifest,
  validation roster, or vendor evidence changed. No fresh EC2/Vitis run was
  needed for this no-HLS-drift proof-factoring slice.

---

## 2026-07-03 — Rust rewrite MemReduce/MemFold proof facts

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `6eb9a25` (`Record MemReduce proof
  facts`). The `MemReduceFill v0` / `MemFoldFill v0` classifier now carries a
  private proof object for the accepted rank-1 memory-reduction shape before
  checked IR construction. The proof records accumulator/temp/output roles,
  reduction loop identity, fill loop identity, optional MemFold zero-init loop
  identity, literal fill, length, and resolved step bound.
- Added direct proof tests for static alias-bound `MemReduce` and `MemFold`
  sources, including the separation of the MemFold zero-init loop from the
  reduction/fill loops. Updated README, the EE109 MVP plan, the fixture matrix,
  and the Rust rewrite architecture note to describe the proof boundary without
  claiming broader Spatial `MemReduce` / `MemFold` support.
- Verification passed locally:
  RED
  `cargo test --locked -p spatial-rs-core memreduce_proof_records_roles_and_resolved_facts -- --nocapture`
  first failed on missing proof fields;
  `cargo test --locked -p spatial-rs-core classifier::reductions::tests -- --nocapture`;
  `cargo test --locked -p spatial-rs-core mem_reduction -- --nocapture`;
  `cargo test --locked -p spatial-rs-hls --test m1_codegen mem_reduction -- --nocapture`;
  `cargo test --locked -p spatial-rs-core`;
  `cargo test --locked -p ee109-examples`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: no accepted syntax, checked payload, generated HLS, manifest,
  validation roster, or vendor evidence changed. No fresh EC2/Vitis run was
  needed for this proof-factoring slice.

---

## 2026-07-03 — Rust rewrite current-head 6a4c4ae Vitis evidence refresh

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `d4e2fcb` (`Record current-head Vitis
  evidence`). The committed evidence refresh uses clean source snapshot
  `6a4c4ae` (`Share rank2 tile copy fact checks`) and makes
  `docs/vitis-validation/2026-07-03-current-head-6a4c4ae-35-program/` the
  active current-head vendor-stability anchor in README, architecture docs,
  the EE109 MVP plan, the fixture matrix, and the HLS evidence test.
- EC2 host `[ec2-host — see private/ec2-lane.md]` ran the full
  35-program EE109 validation roster under Vitis/Vivado 2025.1 using
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`. Remote preflight
  `cargo test -p ee109-examples --locked` passed under Rust/Cargo 1.75 before
  the vendor run.
- Remote Vitis command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-current-head-6a4c4ae`
  from
  `/home/ubuntu/spatial-rs-runs/current-head-6a4c4ae/spatial-rs`.
- Vitis result: all 35 kernels passed with `returncode=0`, `csim=true`, and
  `csynth=true`. The local evidence bundle contains `summary-both.md`,
  `summary-both.json`, logs, reports, sidecar Tcl, and Vitis project trees for
  the same 35 kernels.
- Verification passed locally:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-03-current-head-6a4c4ae-35-program --mode both`;
  `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`;
  `cargo fmt --all -- --check`;
  `cargo test --locked -p ee109-examples`;
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`;
  `cargo test --locked -p spatial-rs-core`;
  stale active-anchor `rg` check;
  `git diff --check`.
- Boundary: this refresh proves Vitis C simulation and HLS synthesis only for
  the exact current 35-program roster. It does not prove board execution,
  Vivado implementation/place-and-route, timing closure, generic Spatial source
  compatibility, arbitrary unsupported features, or performance optimality.

---

## 2026-07-03 — Rust rewrite raw Lab2 FSM-alt adapter retirement

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `1e564a79332d45103413cc4f3d1d9ae86a3bc0c0`
  (`Retire raw Lab2 FSM alt adapter`). The exact raw Scala
  `Lab2Part3BasicCondFSMAlt` source-adapter ingress is retired from the
  quarantined raw-EE109 registry. The canonical `Lab2Part3BasicCondFSMAlt`
  frontend/HIR payload remains accepted, keeps its reserved adapter name, and
  remains the 31st validation-program canary with distinct checked IR and HLS
  semantics.
- Added fail-closed proof that the retired raw Scala wrapper now rejects with
  unsupported-source diagnostic `spatial:E0200`, while a direct classifier
  test guards the canonical alternate FSM path through typed HIR. Updated
  active Rust docs to distinguish current source-ingress policy from
  historical Vitis evidence.
- Generated dry-run artifacts after the change and compared `kernel.cpp`,
  `harness.cpp`, and `manifest.json` against a clean detached `702d181`
  baseline for `Lab2Part3BasicCondFSM`, `Lab2Part3BasicCondFSMAlt`, and
  `ControlFsm32`; all compared files matched byte-for-byte.
- Verification passed locally:
  RED `cargo test -p spatial-rs-core --locked parse_accel_rejects_retired_raw_lab2_fsm_alt -- --nocapture`
  and
  `cargo test -p spatial-rs-core --locked retired_low_value_raw_scala_wrappers_stay_outside_quarantined_registry -- --nocapture`
  failed while the adapter still accepted the raw wrapper;
  `cargo test -p spatial-rs-core --locked lab2_fsm_alt -- --nocapture`;
  `cargo test -p spatial-rs-core --locked source_adapter -- --nocapture`;
  `cargo fmt --all`;
  `cargo test -p spatial-rs-core --locked`;
  `cargo test -p ee109-examples --locked`;
  `cargo test -p spatial-rs-hls --locked`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  the nine `cmp` byte checks listed above;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-plan-fsm-alt-raw-retire`;
  `cargo clippy --workspace --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: no fresh EC2/Vitis run, no validation-roster change, no generated
  HLS/manifest/harness change for canonical ControlFsm-family payloads, no
  generic Scala source compatibility, no generic FSM/control expansion, and no
  new vendor-HLS claim.

---

## 2026-07-03 — Rust rewrite raw Lab2 LUT adapter retirement

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `702d1819e833d856820ff83bc9d1adb262e52b8a`
  (`Retire raw Lab2 LUT adapters`). The exact raw Scala
  `Lab2Part4LUT` and `Lab2Part4LUTNonSquareExample` source-adapter ingress is
  retired from the quarantined raw-EE109 registry. The canonical
  `Lab2Part4LUT` and `Lab2Part4LUTNonSquareExample` frontend/HIR payloads
  remain accepted, their adapter names remain reserved, and `LutLookup v0`
  remains the reusable LUT representative.
- Added fail-closed proof that the retired raw Scala wrappers now reject with
  parser-stage `spatial:E0002`, while direct classifier and checked-IR tests
  guard the canonical square/non-square LUT adapter path and reserved-name
  boundary. Updated active Rust docs to describe raw Scala source ingress as
  retired without changing the canonical LUT support claim.
- Generated dry-run artifacts after the change and compared `kernel.cpp`,
  `harness.cpp`, and `manifest.json` against a clean detached `d0d6c0f`
  baseline for `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`, and
  `LutBiasLookup`; all compared files matched byte-for-byte.
- Verification passed locally:
  `cargo fmt --all`;
  `cargo test -p spatial-rs-core --locked`;
  `cargo test -p spatial-rs-hls --locked`;
  `cargo test -p ee109-examples --locked`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  the nine `cmp` byte checks listed above;
  `cargo clippy -p spatial-rs-core --all-targets --locked -- -D warnings`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.
- Boundary: no fresh EC2/Vitis run, no validation-roster change, no generated
  HLS/manifest/harness change for canonical LUT payloads, no generic Scala
  source compatibility, no generic LUT/table arithmetic expansion, and no new
  vendor-HLS claim.

---

## 2026-07-03 — Rust rewrite ControlFsm harness helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `d0d6c0f`
  (`Extract ControlFsm HLS harness renderer`). The
  `Lab2Part3BasicCondFSM`, `Lab2Part3BasicCondFSMAlt`, and `ControlFsm32`
  ControlFsm host-harness template, display-name handling, and oracle
  selection moved into the crate-private `spatial_rs_hls::control_fsm` helper
  module next to the existing ControlFsm kernel frame/body renderer. `emit.rs`
  still owns `ProgramKind` dispatch, `ControlFsmPlan` lowering,
  `HlsBodyPlan::ControlFsm` matching, HLS parameter lookup, dry-run project
  generation, and public harness compile/run orchestration.
- Generated dry-run artifacts for `Lab2Part3BasicCondFSM`,
  `Lab2Part3BasicCondFSMAlt`, and `ControlFsm32` were compared against the
  pre-change `bb83bce` baseline; `vitis-dry-run/kernel.cpp`,
  `vitis-dry-run/harness.cpp`, and `vitis-dry-run/manifest.json` matched
  exactly for all three programs. Boundary: local helper refactor only. No
  fresh EC2/Vitis execution, no validation-roster change, no manifest or HLS
  kernel change, no host-harness behavior change, no new source syntax, no
  frontend/HIR/classifier behavior change, no generic FSM/control support, and
  no new vendor-HLS claim.
- Verification passed locally:
  RED `cargo test -p spatial-rs-hls --locked control_fsm_harness_uses_entry_symbol_output_len_and_body_oracle -- --nocapture`
  failed first on missing `control_fsm_harness` / `ControlFsmHarnessFrame`;
  `cargo test -p spatial-rs-hls --locked control_fsm_harness_uses_entry_symbol_output_len_and_body_oracle -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked control_fsm -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --lib -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  `cmp` checks for the three ControlFsm programs' dry-run `kernel.cpp`,
  `harness.cpp`, and `manifest.json` artifacts against the `bb83bce` baseline;
  `cargo test -p spatial-rs-hls --locked`;
  `cargo test -p ee109-examples --locked`;
  `cargo clippy -p spatial-rs-hls --all-targets --locked -- -D warnings`;
  `cargo fmt --all -- --check`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite ControlFsm backend helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `bb83bce`
  (`Extract ControlFsm HLS renderer`). The `Lab2Part3BasicCondFSM`,
  `Lab2Part3BasicCondFSMAlt`, and `ControlFsm32` `ControlFsm` HLS kernel
  renderer moved behind the existing `ControlFsmPlan` and the new
  crate-private `spatial_rs_hls::control_fsm` helper module. `emit.rs` still
  owns `ProgramKind` dispatch, `HlsBodyPlan::ControlFsm` matching, HLS
  parameter lookup, dry-run project generation, and ControlFsm
  host-harness/oracle rendering; the helper owns extern signature rendering,
  DRAM/control AXI pragmas, scratch SRAM declaration, register initialization
  and update rendering, canonical and alt FSM body rendering, and the dense
  final store loop.
- Generated dry-run artifacts for `Lab2Part3BasicCondFSM`,
  `Lab2Part3BasicCondFSMAlt`, and `ControlFsm32` were compared against a clean
  detached baseline worktree at Rust commit `da1da8d`; `vitis-dry-run/kernel.cpp`
  and `vitis-dry-run/manifest.json` matched exactly for all three programs.
  Boundary: local Rust test coverage plus dry-run artifact byte comparison
  only. No fresh EC2/Vitis execution, no validation-roster change, no
  generated-HLS or manifest change, no new syntax, no frontend/HIR/classifier
  behavior change, no ControlFsm harness/oracle behavior change, no generic
  FSM/register/control support, no arbitrary conditionals or state updates, no
  scheduling/banking/performance/board-timing claim, and no new vendor-HLS
  claim.
- Verification passed locally:
  RED `cargo test -p spatial-rs-hls --locked control_fsm -- --nocapture`
  failed first on deliberate `todo!()` stubs;
  `cargo test -p spatial-rs-hls --locked --lib control_fsm -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen control_fsm -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_fsm_alt_emits_piecewise_scale_hls_and_harness -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen generated_positive_harnesses_compile_and_run -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_control_fsm_plan_seam_current_head_vitis_evidence_parses_for_thirty_three_program_validation_set -- --nocapture`;
  baseline/current `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  detached-baseline `cmp` checks for the three ControlFsm programs'
  dry-run `kernel.cpp` and `manifest.json` artifacts;
  `cargo test -p spatial-rs-hls --locked`;
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run -- --nocapture`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-control-fsm-renderer-plan`;
  `cargo run -p ee109-examples --locked`;
  `cargo test -p ee109-examples --locked --test ec2_toolchain_compat -- --nocapture`;
  `cargo test --locked`;
  `cargo clippy --workspace --all-targets --locked -- -D warnings`;
  `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`;
  `cargo fmt --all -- --check`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite Dense1d backend helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `da1da8d`
  (`Extract Dense1d HLS renderer`). The `Lab1Part2DramSramExample` and
  `DenseScale64` `Dense1dTileScalarMul` HLS kernel renderer moved behind the
  existing `Dense1dTilePlan` and the new crate-private
  `spatial_rs_hls::dense1d_tile_scalar_mul` helper module. `emit.rs` still owns
  `ProgramKind` dispatch, `HlsBodyPlan::Dense1dTileScalarMul` matching, HLS
  parameter lookup, dry-run project generation, and Dense1d host-harness/oracle
  rendering; the helper owns extern signature rendering, DRAM/scalar/control
  AXI pragmas, rank-1 local tile declarations, the outer tile loop, lane
  load/compute/store loops, `input_tile[lane] * scalar`, and rank-1 row-major
  access text.
- Generated local harness and dry-run artifacts for
  `Lab1Part2DramSramExample` and `DenseScale64` were compared against a clean
  detached baseline worktree at Rust commit `edbb73e`; `kernel.cpp`,
  `harness.cpp`, `manifest.json`, `run_hls.tcl`, and `vitis-project.json`
  matched exactly where those artifacts are generated. Boundary: no fresh
  EC2/Vitis execution, no validation-roster change, no generated-HLS or
  manifest change, no new syntax, no frontend/HIR/classifier behavior change,
  no Dense1d host-harness/oracle behavior change, no generic rank-1 memory
  lowering, no arbitrary tiled-loop scheduling, no dynamic bounds, no non-`Int`
  or FixPt Dense1d support, no performance/board-timing claim, and no new
  vendor-HLS claim.
- Verification passed locally:
  RED `cargo test -p spatial-rs-hls --locked dense1d_tile_scalar_mul -- --nocapture`
  failed first on deliberate `todo!()` stubs;
  `cargo test -p spatial-rs-hls --locked dense1d_tile_scalar_mul -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked dense1d_plan -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen dense -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_dense1d_vitis_evidence_parses_for_adapter_baseline_and_features -- --nocapture`;
  baseline/current `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  baseline/current `cargo test -p spatial-rs-hls --locked --test m1_codegen harness -- --nocapture`;
  detached-baseline `cmp` checks for both Dense1d programs' top-level harness
  artifacts and five dry-run artifacts;
  `cargo test -p spatial-rs-hls --locked`;
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run -- --nocapture`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-dense1d-renderer-plan`;
  `cargo test --locked`;
  `cargo clippy --workspace --all-targets --locked -- -D warnings`;
  `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`;
  `cargo fmt --all -- --check`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite FIFO backend helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `7f35974`
  (`Extract FIFO tile scalar renderer`). The `Fifo1dTileScalarMul` /
  `FifoTileScale32` HLS kernel renderer moved behind `FifoTileScalarMulPlan`
  and the new crate-private `spatial_rs_hls::fifo` helper module. `emit.rs`
  still owns `ProgramKind` dispatch, `HlsBodyPlan::FifoTileScalarMul`
  matching, HLS parameter lookup, and FIFO harness-oracle rendering; the helper
  owns kernel signature/interface rendering, `<hls_stream.h>`, local
  `hls::stream<int>` declarations, stream-depth pragmas, tile/lane loops, FIFO
  write/read ordering, `value * scale`, and final output store.
- Generated dry-run artifacts for `FifoTileScale32` were compared against a
  clean detached baseline worktree at commit `7eb6614`; `kernel.cpp`,
  `harness.cpp`, `manifest.json`, `run_hls.tcl`, and `vitis-project.json` all
  matched exactly. Boundary: no fresh EC2/Vitis execution, no validation-roster
  change, no generated-HLS or manifest change, no new syntax, no generic
  FIFO/stream support, no AXI stream/dataflow/back-pressure claim, and no new
  vendor-HLS claim.
- Verification passed locally:
  RED `cargo test -p spatial-rs-hls --locked fifo -- --nocapture` failed first
  on unresolved helper imports;
  `cargo test -p spatial-rs-hls --locked fifo_tile_scalar_mul_kernel_frame -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked fifo_tile_scalar_mul_plan_extracts_streams_ports_and_loop_shape -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen fifo_feature_emits_real_hls_streams -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen fifo_feature_compiles_with_host_only_stream_shim -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen fifo_staged_dequeue_feature_emits_same_stream_kernel -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen fifo_vitis_dry_run_uses_vendor_stream_header_not_host_shim -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked fifo -- --nocapture`;
  `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`;
  baseline/current `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  detached-baseline `cmp` checks for `FifoTileScale32`'s five dry-run
  artifacts;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-fifo-renderer-plan`;
  `cargo test --locked`;
  `cargo clippy --workspace --all-targets --locked -- -D warnings`;
  `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`;
  `cargo fmt --all -- --check`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite Stencil2d/Sobel backend helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `7eb6614`
  (`Extract Stencil2d Sobel renderer`). The `Stencil2d` / Sobel HLS kernel
  renderer moved behind `Stencil2dSobelPlan` and the new crate-private
  `spatial_rs_hls::stencil2d` helper module. `emit.rs` still owns
  `ProgramKind` dispatch, `HlsBodyPlan::Stencil2dSobel` matching, HLS
  parameter lookup, and Lab3/Sobel harness-oracle rendering; the helper owns
  kernel signature/interface rendering, Sobel table rendering, row-major
  `COLS` / `KW` access text, border-zero policy, absolute-gradient sum, final
  output store, and the row-major offset validator.
- Generated dry-run artifacts for `Lab3Part1Convolution` and
  `SobelStencil12x20` were compared against a clean detached baseline worktree
  at commit `19eeec1`; `kernel.cpp`, `harness.cpp`, `manifest.json`,
  `run_hls.tcl`, and `vitis-project.json` all matched exactly for both
  programs. Boundary: no fresh EC2/Vitis execution, no validation-roster
  change, no generated-HLS or manifest change, no new syntax, no generic
  local-window/stencil support, no arbitrary coefficient/parallelism/dimension
  support, and no new vendor-HLS claim.
- Verification passed locally:
  `cargo test -p spatial-rs-hls --locked stencil2d -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_convolution -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked plan::tests::lab3_stencil -- --nocapture`;
  baseline/current `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  detached-baseline `cmp` checks for both stencil programs' five dry-run
  artifacts;
  `cargo test -p spatial-rs-core --locked stencil2d`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_local_raw`;
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation current_head_vitis_evidence_validator_accepts_cc86ab5_checkpoint`;
  `cargo test --locked`;
  `cargo clippy --workspace --all-targets --locked -- -D warnings`;
  `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-stencil2d-renderer-plan`;
  `cargo fmt --all -- --check`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite rank-2 copy backend helper extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `19eeec1`
  (`Extract rank2 copy renderer`). The `Dram2dCopy` / rank-2 row-major copy
  HLS kernel and harness rendering moved behind the new crate-private
  `spatial_rs_hls::rank2_copy` helper module. `emit.rs` still owns
  `ProgramKind` dispatch, `HlsBodyPlan::Dram2dCopy` matching, and HLS parameter
  lookup; the helper owns signature/interface rendering, row-major copy loop
  text, harness cases, and row-major oracle wiring.
- Generated dry-run artifacts for `Lab3Part0MatrixCopyRowMajor` and
  `MatrixCopy4x6` were compared against a clean detached baseline worktree at
  commit `4c29758`; `kernel.cpp`, `harness.cpp`, `manifest.json`,
  `run_hls.tcl`, and `vitis-project.json` all matched exactly for both
  programs. Boundary: no fresh EC2/Vitis execution, no validation-roster change,
  no generated-HLS or manifest change, no new syntax, no broader rank-2 memory
  support claim, and no new vendor-HLS claim.
- Verification passed locally:
  `cargo fmt --all -- --check`;
  `cargo test -p spatial-rs-hls --locked rank2_copy -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_row_major_copy_kernel_uses_cols_as_rank2_flatten_stride -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_copy_4x6_feature_emits_parameterized_rank2_copy_and_harness -- --nocapture`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_dram2d_copy_vitis_evidence_parses_for_adapter_baseline_and_features -- --nocapture`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  detached-baseline `cmp` checks for both copy programs' five dry-run artifacts;
  `cargo test --locked`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-rank2-copy-renderer-plan`;
  `git diff --check`.

---

## 2026-07-03 — Rust rewrite Dense2d tile scalar classifier characterization

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `4c29758`
  (`Characterize Dense2d tile scalar classifier helpers`). Added helper-level
  characterization tests for `Dense2dTileScalarMul` `match_tile_load`,
  `match_tile_compute`, and `match_tile_store` in the core classifier.
- The new coverage pins canonical load/compute/store acceptance and
  fail-closed rejection for equal-valued wrong row/column coefficient symbols,
  swapped local lane symbols, commuted scalar multiply, wrong scalar symbol,
  wrong output tile, staged/split final store, and wrong output symbol.
- Verification passed locally:
  `cargo fmt --all -- --check`;
  `cargo test -p spatial-rs-core --locked dense2d_tile_scalar -- --nocapture`;
  `cargo test -p spatial-rs-core --locked rank2_tiled_int_scale -- --nocapture`;
  `cargo test -p spatial-rs-core --locked`;
  `cargo test --locked`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `git diff --check`.
  Boundary: test-only core classifier coverage, no production classifier
  behavior change, no generated-HLS or manifest change, no validation-roster
  change, no fresh EC2/Vitis execution, no new syntax, and no new vendor-HLS
  claim.

---

## 2026-07-03 — Rust rewrite Dense2d tile scalar backend-plan extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `08a3399`
  (`Extract Dense2d tile scalar renderer`). The `Dense2dTileScalarMul` HLS
  kernel renderer moved behind `Dense2dTileScalarMulPlan` and the new
  crate-private `spatial_rs_hls::tile_scalar_mul` helper path. `emit.rs` now
  keeps orchestration and parameter lookup, while the helper owns
  signature/interface pragma rendering, row/column tile loops, flattened
  input/output tile declarations, input load, scalar multiply, and final store.
- Generated `kernel.cpp`, `harness.cpp`, `manifest.json`, and `run_hls.tcl`
  bytes for `MatrixTileScale4x6` were compared against a clean detached
  baseline worktree at commit `0adde4d`; all matched exactly. Boundary: no
  fresh EC2/Vitis execution, no validation-roster change, no generated-HLS or
  manifest change, no new syntax, no generic rank-2 tiled lowering, and no new
  vendor-HLS claim.
- Verification passed locally:
  `cargo fmt --all -- --check`;
  `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin ee109-examples`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-tile-scalar-mul-renderer-plan`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation current_head`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles`;
  `cargo test -p ee109-examples --locked --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation rank2_tiled_int_scale_vitis_evidence_summary_is_twenty_program_checkpoint`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_rank2_tiled_int_scale_vitis_evidence_parses_for_twenty_program_validation_set`;
  `git diff --check`.
- Follow-up note: subagent review identified broader
  `Dense2dTileScalarMul` classifier-helper characterization gaps
  (`match_tile_load`, `match_tile_compute`, `match_tile_store`, equal-valued
  alias rejection, lane-swap rejection, staged/split-store rejection). Those
  are a separate frontend/classifier reliability slice, not part of this
  byte-stable backend-renderer extraction.

## 2026-07-03 — Rust rewrite Dense2d DotAccum backend-plan extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `0adde4d`
  (`Extract Dense2d DotAccum renderer`). The `Dense2dTileDotAccum` HLS kernel
  renderer moved behind `Dense2dTileDotAccumPlan` and the new crate-private
  `spatial_rs_hls::dot_accum` helper path. `emit.rs` now keeps orchestration
  and parameter lookup, while the helper owns signature/interface pragma
  rendering, row/column tile loops, flattened local tile declarations, LHS/RHS
  tile loads, accumulator zero/update, and final store.
- Generated `kernel.cpp` and `manifest.json` bytes for
  `MatrixTileAccum4x6x5` were compared against a clean detached baseline
  worktree at commit `ed10282`; both matched exactly. This was a
  no-HLS-drift backend cleanup: no validation-roster change, no generated-HLS
  or manifest change, no new syntax, no generic GEMM/MemFold/K-tiling support,
  and no fresh vendor-HLS claim.
- Verification passed locally:
  `cargo fmt --all -- --check`;
  `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin ee109-examples`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-dot-accum-renderer-plan`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation current_head`;
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`;
  `git diff --check`.

## 2026-07-03 — Rust rewrite Dense2d MemFold backend-plan extraction

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `ed10282`
  (`Extract Dense2d MemFold renderer`). The non-outer-K
  `Dense2dTileMemFold` HLS kernel renderer moved behind
  `Dense2dTileMemFoldPlan` and the new crate-private
  `spatial_rs_hls::memfold` helper path. `emit.rs` now keeps orchestration and
  parameter lookup, while the helper owns split-C/in-place signature rendering,
  AXI interface pragmas, paired row/column-tail bounds, local flattened tile
  declarations, and the preload / partial-product / fold / store loop body.
  Generated `kernel.cpp` and `manifest.json` bytes were compared against a
  clean baseline worktree at commit `493a3ab` for
  `MatrixTileMemFold4x6x5`, `MatrixTileMemFoldTail5x7x5`,
  `MatrixTileMemFoldFixPt4x6x5`, and
  `MatrixTileMemFoldInPlaceFixPt4x6x5`; all matched exactly.
- Verification passed locally:
  `cargo test -p spatial-rs-hls --locked memfold::tests`;
  `cargo test -p spatial-rs-hls --locked emit_dense2d_tile_memfold`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_shell_alias_buffer_preserves_exact_hls_and_manifest`;
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_infix_tile_io_preserves_exact_hls_and_manifest`;
  `cargo fmt --all -- --check`; `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin ee109-examples`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation --
  --plan-only --mode both --out target/vitis-validation-dense2d-memfold-renderer-plan`;
  `cargo test -p spatial-rs-hls --locked --test vitis_validation current_head`;
  and `git diff --check`.
  Boundary: no fresh EC2/Vitis execution, no validation-roster change, no
  generated-HLS or manifest change, no new syntax, no generic Spatial
  `MemFold` or GEMM support, and no new vendor-HLS claim.

## 2026-07-03 — Rust rewrite Tile-K support profile ledger

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `493a3ab`
  (`Add Tile-K support profile ledger`). The `Dense2dTileKMemFold` validation
  gate now records the current supported Lab2 Tile-K surface as a closed
  six-profile ledger: serial full-K, serial K-tail, serial row/column/K-tail,
  Part6 full-K, Part6 K-tail, and Part6 row/column/K-tail. The slice also adds
  a fail-closed regression for the previously over-permissive case where the
  scheduled row/column/K-tail kernel name could carry only a generic serial
  exact-coverage payload, and the classifier proof tests now pin all six
  profiles. Roadmap docs were updated to mark this proof/support ledger slice
  complete.
- Verification passed locally:
  `cargo test -p spatial-rs-core --locked --quiet tile_k_support_profile`;
  `cargo test -p spatial-rs-core --locked --quiet checked_ir_rejects_serial_payload_under_part6_row_col_tail_name`;
  `cargo test -p spatial-rs-core --locked --quiet tile_k_contract_accepts_all_current_profiles`;
  `cargo test -p spatial-rs-core --locked --quiet parse_accel_lab2_outer_k`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen lab2_outer_k`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen lab2_raw_part`;
  `cargo fmt --all -- --check`; `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin ee109-examples`;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation --
  --plan-only --mode both --out target/vitis-validation-tile-k-profile-ledger-plan`;
  and `git diff --check`.
  Boundary: no fresh EC2/Vitis execution, no generated-HLS evidence change, no
  validation-roster change, no broad Scala compatibility, and no new generic
  Spatial GEMM support. This is a local compiler-support and fail-closed
  validation slice.

## 2026-07-03 — Rust rewrite retired Lab1 raw Scala wrappers

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `c809b6b`
  (`Retire Lab1 raw Scala wrappers`). The quarantined raw Scala adapter no
  longer accepts the exact `Lab1Part4FIFOExample` or
  `Lab1Part6ReduceExample` wrappers. Their behavior remains covered by the
  Rust-subset representatives `FifoTileScale32` and `SramTileFoldSum32`, and
  the old lab names remain reserved so they cannot be mistaken for native Rust
  frontend support. Removed the obsolete raw-HLS equality tests for those two
  wrappers and updated README / fixture-matrix / architecture / roadmap docs
  to mark the wrappers retired rather than accepted.
- Verification passed locally:
  `cargo test -p spatial-rs-core --locked --quiet source_adapter::tests`;
  `cargo test -p spatial-rs-core --locked --quiet raw_lab1_part4`;
  `cargo test -p spatial-rs-core --locked --quiet raw_lab1_part6`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen fifo_feature`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen sram_tile_fold`;
  `cargo fmt --all -- --check`; `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin ee109-examples`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation --
  --plan-only --mode both --out target/vitis-validation-lab1-raw-retirement-plan`;
  and `git diff --check`.
  Boundary: no fresh EC2/Vitis execution, no validation-roster change, no
  generated-HLS evidence change, no broad Scala compatibility, and no
  retirement of Lab2 raw-island, Lab2 GEMM, Lab2 LUT/FSM, or Lab3 quarantine
  paths in this slice.

## 2026-07-03 — Rust rewrite raw Scala adapter quarantine provenance

- Committed `/Users/david/Documents/David_code/spatial-rs` on
  `David/HLS-spatial` at Rust commit `488cee9`
  (`Quarantine raw Scala adapter provenance`). The parser now routes raw EE109
  Scala only through `match_quarantined_raw_ee109_scala`, and each raw adapter
  path carries explicit provenance for how it matches today plus the intended
  retirement target. Low-value exact wrappers are marked as canonical-frontend
  equivalents, Lab2 Part1/Part2 raw-island proofs are marked as
  proof-driven-frontend/HIR work, and Lab2 GEMM plus Lab3 Sobel remain
  quarantined until stronger feature proofs exist. The redundant Lab2 Part5/6
  exact fallback table entries were removed because those sources already enter
  through the normalized GEMM proof path. Roadmap Phase 4 was updated to mark
  quarantine/provenance complete while leaving wrapper retirement and reserved
  adapter-name narrowing open.
- Verification passed locally:
  `cargo test -p spatial-rs-core --locked --quiet source_adapter::tests`;
  `cargo test -p spatial-rs-core --locked --quiet parse_accel_lab2_outer_k`;
  `cargo test -p spatial-rs-core --locked --quiet parse_accel_accepts_exact_raw_lab2`;
  `cargo test -p spatial-rs-core --locked --quiet raw_lab2_part`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen lab2_raw_part`;
  `cargo test -p spatial-rs-hls --locked --quiet --test m1_codegen lab2_outer_k_part6_structural_par_preserves_scheduled_hls_and_manifest`;
  `cargo fmt --all -- --check`; `cargo test --locked --quiet`;
  `cargo clippy --all-targets --locked -- -D warnings`;
  `cargo run -p ee109-examples --locked --bin run-vitis-validation --
  --plan-only --mode both --out target/vitis-validation-raw-quarantine-plan`;
  and `git diff --check`.
  Boundary: no fresh EC2/Vitis execution, no generated-HLS evidence change, no
  new accepted Spatial syntax, no broad Scala compatibility, and no wrapper
  retirement in this slice.

## 2026-07-03 — Rust rewrite full-roadmap audit and evidence-anchor cleanup

- Ran a six-lane GPT-5.5 xhigh read-only audit of the Rust Spatial rewrite
  direction after the current-head 35-program Vitis checkpoint. Consensus:
  the known EE109-shaped roster is stable enough to use
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-current-head-cc86ab5-35-program/`
  as the active vendor-stability anchor, while the full rewrite should now
  deepen `ResolvedHir -> feature proof -> Program`, raw-source quarantine, and
  `HlsKernelPlan` seams rather than adding more exact fixture adapters. Added
  `/Users/david/Documents/David_code/spatial-rs/docs/superpowers/plans/2026-07-03-full-rust-spatial-rewrite-roadmap.md`
  and updated repo docs so the latest current-head evidence is no longer
  confused with the earlier scheduled row/column/K-tail roster-expansion
  checkpoint. Boundary: documentation/roadmap only; no Rust code, HLS output,
  validation roster, or vendor-HLS evidence changed.

## 2026-07-03 — Rust rewrite current-head 35-program EC2/Vitis refresh

- Ran the full 35-program EE109 validation roster on EC2/Vitis for
  `/Users/david/Documents/David_code/spatial-rs` (`David/HLS-spatial`) at clean
  source commit `cc86ab5d2f62a335bd189fb7b1916990efc51ff2`. EC2 host
  `[ec2-host — see private/ec2-lane.md]` / `ip-172-31-37-7` ran
  Vitis 2025.1 with `/tools/Xilinx/2025.1/Vitis/settings64.sh`; all 35 kernels
  reported `returncode=0`, `csim=true`, and `csynth=true`. Imported evidence is
  in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-current-head-cc86ab5-35-program/`
  and validates locally with
  `run-vitis-validation --validate-evidence ... --mode both`. Boundary: Vitis C
  simulation and HLS synthesis only; no board execution, Vivado implementation,
  place-and-route, timing closure, generic Spatial compatibility, or performance
  optimality claim.

## 2026-07-03 — Rust rewrite Vitis evidence CLI validation

- Added a `run-vitis-validation --validate-evidence <dir>` mode in
  `/Users/david/Documents/David_code/spatial-rs` (`David/HLS-spatial`) so
  captured EC2/Vitis evidence can be validated through the same runner binary
  that plans and executes the roster. The CLI checks the current 35-program
  validation order against summary JSON, sidecar Tcl, logs, csynth reports,
  all-pass execution state, target device, and clock via the existing
  repo-local evidence validator. Boundary: this is local evidence ingestion and
  documentation hygiene only; it does not run Vitis, add new language support,
  or create fresh vendor-HLS evidence.

## 2026-07-03 — Rust rewrite Lab3 Stencil2d alias constants

- Widened the reusable Rust `Stencil2d v0` classifier on
  `/Users/david/Documents/David_code/spatial-rs` (`David/HLS-spatial`) so the
  Sobel subset no longer depends on exact Lab3-style constant names
  `ROWS/COLS/KH/KW/CMAX/LB_PAR`. Added `SobelStencilAlias12x20` as a local
  perturbation using `H/W/KROWS/KCOLS/LINE_COLS/LOAD_PAR` and `store ... par W`;
  it classifies to the same checked `Stencil2d` surface, emits the expected HLS
  shape, and passes the native host-C++ oracle harness. Boundary: this is local
  parser/classifier/HLS evidence only; generic local-window/stencil support,
  arbitrary kernels, arbitrary `par`, dynamic dimensions, and fresh
  EC2/Vitis-roster promotion remain future work.

## 2026-07-03 — Rust rewrite Lab2 GEMM parameterized raw aliases

- Widened the Rust Lab2 Tile-K GEMM frontend bridge on
  `/Users/david/Documents/David_code/spatial-rs` (`David/HLS-spatial`) so
  Lab2-like raw dimension/tile aliases are no longer restricted to literal
  `M/N=32` and `tileM/tileN/tileK=16` when the source is an exact-coverage
  serial Tile-K MemFold. Added a local parameter perturbation canary for
  `M/N/K=24/20/12` with `tileM/tileN/tileK=8/5/4`; it normalizes to the same
  checked `Dense2dTileKMemFold` payload as the expanded source, preserves
  generated HLS/manifest equality, and passes the native host-C++ harness.
  Boundary: this is parser/HIR/classifier/HLS local evidence only; no new
  Vitis validation-roster member or fresh vendor run.

## 2026-07-03 — Rust rewrite Vitis evidence hygiene gate

- Added a repo-local Vitis evidence validator and explicit EC2 Rust/Cargo 1.75
  compatibility gate for `/Users/david/Documents/David_code/spatial-rs`
  (`David/HLS-spatial`). The validator checks the captured 35-program
  scheduled row/column/K-tail evidence directory for summary mode/execution,
  exact kernel order, pass state, local sidecars/logs/reports, target device,
  and clock. Boundary: this is evidence hygiene only; no new HLS surface,
  validation member, or vendor run.

## 2026-07-03 — Rust rewrite Lab2 LUT reference-wrapper correction

- Corrected the raw `Lab2Part4LUT` fixture to match the actual reference-corpus
  EE109 source shape, including the `spatial.tests.ee109` package, `runtimeArgs
  = "0 0 0"`, reference `in/out/i/j` argument setup, `LUT[Int](3,3)`, and the
  original host oracle. Added the matching exact raw
  `Lab2Part4LUTNonSquareExample` reference wrapper. Both wrappers canonicalize
  to their existing checked LUT payloads, with parser equality,
  source-adapter near-miss rejection, and generated-HLS/manifest equality tests.
  Boundary: this is source-compatibility only; no generated-HLS change, no
  validation-roster change, and no fresh vendor-HLS claim.

## 2026-07-03 — Rust rewrite Lab2 Part4 raw LUT adapter

- Added the exact raw Scala `Lab2Part4LUT` wrapper to the Rust source-adapter
  path on `/Users/david/Documents/David_code/spatial-rs`
  (`David/HLS-spatial`). The wrapper canonicalizes to the existing checked
  square-LUT payload rather than adding a new HLS surface. Proof added:
  `parse_accel_accepts_exact_raw_lab2_part4_lut`,
  `registry_rejects_raw_lab2_part4_lut_near_misses`, and
  `lab2_raw_part4_lut_preserves_hls_and_manifest`. Focused tests passed for
  parser acceptance, source-adapter registry/near-miss rejection, and HLS /
  manifest equality. Full local gates also passed: Rust formatting, git diff
  whitespace checks in both repos, full workspace tests, clippy with warnings denied,
  the EE109 accepted-fixture binary, the 33-program plan-only Vitis roster, and
  Vitis dry-run emission. Boundary: no fresh EC2/Vitis run for this slice
  because
  generated HLS and manifest output are identical to the already-supported
  canonical LUT path; still no broad Scala LUT compatibility, arbitrary LUT
  dimensions/values, swapped indices, non-`Int` LUTs, board execution, Vivado
  implementation, or timing-closure claim.

## 2026-07-03 — Rust rewrite HLS plan provenance

- Promoted Rust commit `f1a229f` (`Finish HLS harness plan migration`) to a
  fresh EC2/Vitis checkpoint. I archived the clean `David/HLS-spatial` commit
  to `/home/ubuntu/spatial-rs-runs/harness-plan-20260703-f1a229f/spatial-rs`
  on `[ec2-host — see private/ec2-lane.md]`, used
  `/home/ubuntu/.cargo/bin/cargo` because `/usr/bin/cargo` was too old for the
  v4 lockfile, and ran `run-vitis-validation --execute --mode both` with
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`. All 33 validation programs
  passed `csim_design` and `csynth_design`, including all nine current raw
  EE109 fixture adapters and the Lab2 Part6 scheduled/tail canaries. The
  durable evidence is now in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-harness-plan-f1a229f/`.
  Boundary: Vitis C simulation and HLS synthesis only; still no board
  execution, Vivado implementation, place-and-route, post-implementation timing
  closure, broad Spatial compatibility, arbitrary MemFold/GEMM support,
  automatic banking inference, broader `par` inference, or performance
  optimality claim.
- Re-ran the local EE109/HLS-prep gate after Rust commit `f1a229f`
  (`Finish HLS harness plan migration`). Evidence: `cargo test --locked
  --quiet` passed across the workspace; `cargo run -p ee109-examples --locked
  --bin ee109-examples` accepted all nine current raw EE109 fixture adapters;
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run` emitted the
  current HLS dry-run roster; `cargo run -p ee109-examples --locked --bin
  run-vitis-validation -- --out target/vitis-validation-plan` produced 33
  Vitis plan sidecars; and the generated `kernel.cpp`/`host.cpp` leakage scan
  found no real Scala/Chisel/Spatial shell terms. Boundary: still local only;
  this does not add fresh Vitis `csim_design` / `csynth_design` evidence,
  board execution, Vivado implementation, timing closure, or broader Spatial
  source compatibility.
- Completed the remaining simple HLS host-harness plan migration in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: LUT, Dense1d, and Dram2d copy harness rendering now
  consumes `HlsKernelPlan` data, matching the prior ScalarReduce, ScalarFold,
  MemReduce/MemFold fill, and Control/FSM harness plan migration. The old
  `LutLayout`, `DenseLayout`, and `Dram2dCopyLayout` extractors were removed,
  leaving no legacy `*Layout` helpers in `crates/spatial-rs-hls/src/emit.rs`.
  Focused plan-harness tests and affected m1 codegen/harness tests passed,
  followed by `cargo test --locked -p spatial-rs-hls`, `cargo test --locked
  --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo fmt
  --all -- --check`, and `git diff --check`. Boundary: this is a local
  harness/oracle refactor only; generated kernels, manifests, validation
  membership, existing EC2/Vitis evidence, board execution, Vivado
  implementation, timing closure, and source language support are unchanged.
- Moved four HLS host-harness renderers onto explicit `HlsKernelPlan` data in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: ScalarReduce, ScalarFold, MemReduce/MemFold fill, and
  Control/FSM now lower through their plan objects before rendering the C++
  harness/oracle driver. This deletes the duplicate local layout extractors
  for those features and keeps validation anchored on the same checked plans as
  kernel emission. A `gpt-5.5 xhigh` explorer reviewed the remaining layout
  boundary; LUT, Dense1d, and Dram2d copy harness layouts remain as next cleanup
  targets. Focused plan-harness tests, affected m1 codegen/harness tests,
  `cargo test --locked -p spatial-rs-hls`, `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`, `cargo fmt --all -- --check`,
  and `git diff --check` passed. Boundary: generated kernels, manifests,
  validation membership, and existing EC2/Vitis evidence are unchanged; no new
  Vitis run, board execution, Vivado implementation, timing closure, new
  syntax, or broader Spatial language support is claimed by this harness
  refactor.
- Added a no-HLS-drift MemReduce/MemFold HLS plan-provenance slice in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: `MemReductionFillPlan` now preserves whether the
  checked payload came from `MemReduceFill` or `MemFoldFill` while also
  carrying the literal fill value. A test-first regression first failed because
  `MemReductionKindPlan` and `mem.kind` did not exist, then passed after adding
  the plan enum and lowering assignment. Focused verification passed
  `cargo test --locked -p spatial-rs-hls mem_reduction_fill_plan_preserves_kind_and_literal_fill`
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen mem_reduction_literal_two`.
  Boundary: generated HLS remains intentionally unchanged for the v0
  constant-fill MemReduce/MemFold renderers; no new syntax, validation-program
  member, EC2/Vitis rerun, board execution, Vivado implementation, timing
  closure, generic Spatial `MemReduce`/`MemFold`, arbitrary fold bodies,
  dynamic bounds, banking, scheduling, or performance claim is added by this
  slice.

## 2026-07-02 — Rust rewrite Lab2 Part6 and serial K-tail

- Hardened the Lab2 Part1/Part2 memory-reduction classifier in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: `MemReduceFill v0` / `MemFoldFill v0` now consume
  resolver-owned loop/symbol facts for the narrow rank-1 `Int` reduction
  shape, allowing equivalent Rust-subset static length/step aliases while
  keeping the exact raw Lab2 wrappers mapped only to `MemReduceOnes16` /
  `MemFoldOnes16`. Local verification passed the new alias and shadow
  fail-closed tests, `memreduce`, `memfold`, `memory_reduction`, raw Lab2
  wrapper tests, HLS m1 codegen/manifest tests, validation membership, and
  captured-evidence parser checks. Boundary: checked payloads, generated HLS,
  manifests, validation membership, and existing Vitis evidence are unchanged;
  no EC2/Vitis rerun was performed for this local classifier hardening slice,
  and this is still not generic Spatial `MemReduce`/`MemFold`, arbitrary
  bodies, dynamic bounds, rank-2 reductions, scheduling, banking, board
  execution, Vivado implementation, timing closure, or broad Scala source
  compatibility.
- Extracted the Lab2 GEMM bridge profile in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: parser-private `frontend/lab2_gemm_bridge.rs` now owns
  Lab2 GEMM shell-alias detection, in-place C state, offset-loop aliases,
  `numel_*` policy, and partial-par bridge state, while `parse.rs` keeps token
  consumption, diagnostics, and AST construction. This is behavior-preserving
  maintainability work over the fixed Part5/Part6 frontend-routing path:
  exact raw-wrapper admission, generated Lab2-like frontend source, checked
  payloads, generated HLS, manifests, validation membership, and Vitis evidence
  boundary remain unchanged. No EC2/Vitis rerun is required. Boundary: no new
  Scala source compatibility, generic `MemFold`, generic `par`, inferred
  banking, broad GEMM, dynamic dimensions, arbitrary K tails, emitted-HLS
  surface, validation member, board execution, timing closure, or performance
  claim.
- Routed fixed raw Lab2 GEMM wrappers through bounded frontend/HIR source in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: after exact token-stream quarantine,
  `Lab2Part5GEMM`/`Lab2Part6GEMM` now emit Lab2-like frontend source using
  `a/b/c`, tile SRAM aliases, static offset loops, infix tile IO,
  `numel_k = min(...)`, explicit-zero MemFold range, and Part6 literal
  `par 2`/`par 16` where applicable, then compile through the existing
  frontend/HIR/classifier bridge instead of returning expanded canonical kernel
  text directly. Local equality tests preserve checked payloads, generated HLS,
  manifests, validation membership, and the Vitis evidence boundary. No
  EC2/Vitis rerun is required. Boundary: not a broad Scala parser/source
  compatibility claim, no new GEMM shapes, dynamic dimensions, generic
  `MemFold`, generic `par`/banking, arbitrary K tails, board execution, timing
  closure, or HLS output change claim.
- Added a narrow explicit-zero raw Lab2 GEMM fold-range bridge in
  `/Users/david/Documents/David_code/spatial-rs` on branch
  `David/HLS-spatial`: fixed raw `Lab2Part5GEMM` and `Lab2Part6GEMM` wrappers
  now accept `MemFold(tileC_sram)(0 until numel_k by 1)` as an exact
  equivalent spelling of the fixture's implicit-zero
  `MemFold(tileC_sram)(numel_k by 1)` range. Nonzero starts such as
  `1 until numel_k by 1` remain rejected. This is source-adapter equality only:
  the checked payload, generated HLS, manifest output, validation membership,
  and vendor-HLS evidence boundary remain unchanged, so no EC2/Vitis rerun is
  required. Boundary: this is not generic Scala range parsing, generic Spatial
  `MemFold`, arbitrary K-tail support, dynamic dimensions, generic `par`,
  automatic banking, board execution, Vivado implementation, or timing
  closure.
- Captured 29-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `47743d055b7daa9f6b60def28b379aae7bb5b04a`, after promoting the serial K-tail canary. EC2 host `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-k-tail-20260702-47743d0` from `/home/ubuntu/spatial-rs-runs/k-tail-20260702-47743d0/spatial-rs` with return code 0 across all 29 validation programs. Each program reported `csim=true` and `csynth=true`; durable evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-k-tail-29-program/`. The K-tail canary reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 13363-61591 cycles, interval 13364-61592 cycles, and utilization estimate 41 BRAM_18K, 64 DSP, 8227 FF, and 6013 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the exact 29-program lane, not board execution, Vivado implementation/place-and-route, timing closure, broad Scala source compatibility, arbitrary K-tail shapes, dynamic dimensions, generic `MemFold`, generic `par`, automatic banking inference, generic GEMM, or performance optimality.
- Promoted `MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to the 29th local EE109 validation-program member. The existing 28-program order is preserved and the K-tail canary is appended after `FifoTileScale32`; `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`, `cargo test -p ee109-examples --locked dense2d_tile_k_memfold_tail_example_is_validation_canary -- --nocapture`, `cargo test -p spatial-rs-hls --locked lab2_outer_k_numel_k_tail_emits_runtime_k_bound_and_harness -- --nocapture`, `cargo test -p ee109-examples --locked emit_vitis_dry_run_binary_generates_m1_frontend_bundles -- --nocapture`, and `cargo test -p ee109-examples --locked run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture` passed. `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-k-tail-plan` emitted 29 planned sidecars, including `MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`. Boundary at promotion time: this was local validation membership and plan-only readiness, before the later EC2/Vitis evidence entry above.
- Added a local serial K-tail Tile-K MemFold canary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34` accepts the narrow Lab2-like offset-loop `val numel_k = min(TILE_K.to[Int], K - kk);` form when `K=34`, `K_TILES=3`, `TILE_K=16`, row/column tiling is exact, and the partial schedule is serial. The frontend now preserves `numel_k` as checked `Dense2dTileKMemFold.k_bound`, validation allows bounded ceil K coverage only for this named FixPt canary, and the HLS emitter computes a runtime `numel_k` loop bound while keeping local A/B SRAMs statically `TILE_K` wide. Focused local verification passed `cargo test -p spatial-rs-core --locked numel_k_tail -- --nocapture`, `cargo test -p spatial-rs-core --locked checked_ir_accepts_serial_tile_k_memfold_k_tail_bound -- --nocapture`, `cargo test -p spatial-rs-hls --locked lab2_outer_k_numel_k_tail_emits_runtime_k_bound_and_harness -- --nocapture`, `cargo test -p spatial-rs-core --locked lab2_outer_k -- --nocapture`, and `cargo test -p spatial-rs-hls --locked lab2_outer_k -- --nocapture`; full local hygiene passed `cargo fmt --all -- --check`, `cargo test --locked --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check` in both repos. Boundary at initial implementation time: this changed emitted HLS for a new local canary and still needed the later validation-program membership promotion plus EC2/Vitis execution; it is not generic Spatial `MemFold`, broad Scala source compatibility, raw Lab2 Part5/Part6 K tails, arbitrary K-tail shapes, dynamic dimensions, `par` scheduling, automatic banking, board execution, Vivado implementation, place-and-route, timing closure, or broad GEMM support.
- Added a narrow literal-fill expansion for `MemReduceFill v0` / `MemFoldFill v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the Rust-subset frontend/classifier and checked IR now accept fixed temp-SRAM fill literals `1` or `2`, carrying the selected fill into the existing HLS emitter and oracle-backed host harness. New local canaries `MemReduceTwos16` and `MemFoldTwos16` prove parser payloads, checked-IR validation, emitted `tmp[j] = 2;`, and local host-C++ harness PASS results. Focused local verification passed `cargo test -p spatial-rs-core --locked mem_reduction -- --nocapture`, `cargo test -p spatial-rs-hls --test m1_codegen --locked mem_reduction_literal_two_fill_features -- --nocapture`, `cargo test -p ee109-examples --locked supported_feature_near_misses_stay_fail_closed -- --nocapture`, and `cargo test -p spatial-rs-core --locked raw_lab2 -- --nocapture`. Boundary: no validation-program membership change and no EC2/Vitis rerun for this slice; the vendor-proven 28-program evidence remains `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-part6-structural-408e21c/`. The raw Scala Lab2 Part1/Part2 adapters remain pinned to the exact all-ones lab bodies, and generic Spatial `MemReduce`/`MemFold`, arbitrary reducer/fold bodies, other fill values, rank-2 reductions, dynamic bounds, scheduling, banking, board execution, Vivado implementation, timing closure, and broad Scala source compatibility remain unsupported.
- Captured exact-commit 28-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `408e21ca0be60b0fac7a81ae6abbba547a7be674`, after the structural Lab2-like Part6 bridge landed. EC2 host `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-part6-structural-408e21c` from `/home/ubuntu/spatial-rs-runs/part6-structural-20260702-408e21c/spatial-rs` with return code 0 across all 28 validation programs. Each program reported `csim=true` and `csynth=true`; compact evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-part6-structural-408e21c/`. The scheduled Part6 canary reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7885 cycles, interval 7886 cycles, and utilization estimate 8 BRAM_18K, 128 DSP, 15417 FF, and 12192 LUT. Boundary: this proves the exact structural bridge commit through Vitis C simulation and synthesis, but it still does not add a validation-program member or emitted-HLS surface and does not imply generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation/place-and-route, timing closure, generic GEMM, or broad Scala source compatibility.
- Added the structural Lab2-like Part6 scheduled bridge in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `408e21ca0be60b0fac7a81ae6abbba547a7be674`: the outer-K frontend now accepts infix tile IO, static offset-loop, and exact static `numel_k = min(TILE_K.to[Int], K - kk)` source shapes for `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` when only the partial-tile fill loops carry literal `par 2` / `par 16`. The bridge normalizes to the existing scheduled checked payload with `partial_row_par=2` and `partial_col_par=16`, while symbolic structural par factors, one-sided par, outer/fold/load/store par, generic/full-K MemFold par, serial-name/scheduled-name mismatches, and wrong/swapped factors remain fail-closed. Local verification passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked parse_accel_lab2_outer_k_ -- --nocapture`, `cargo test -p spatial-rs-core --locked lab2_outer_k_infix_tile_io_near_misses_fail_closed -- --nocapture`, `cargo test -p spatial-rs-core --locked spatialish_memfold_call_near_misses_fail_closed -- --nocapture`, `cargo test -p spatial-rs-core --locked raw_lab2_part6_fixed_wrapper_near_misses_fail_closed -- --nocapture`, `cargo test -p ee109-examples --locked validation_programs -- --nocapture`, `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`, `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6_fixed_32 -- --nocapture`, `cargo test -p spatial-rs-hls --locked --test vitis_validation lab2_part6_scheduled -- --nocapture`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-part6-structural-plan`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo test --locked --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check` in both repos. Boundary at local-commit time: frontend/HIR/classifier source-spelling bridge plus equality tests only; checked HLS surface, manifest, and validation-program membership were unchanged, with the later exact-commit EC2/Vitis refresh recorded above. This is still not generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, generic GEMM, broad Scala source compatibility, board execution, Vivado implementation, or timing closure.
- Added a resolver-backed fixed Tile-K phase-spine guard in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `61e91c6656e7c196637b90b437dd0e4f80a5771a`: `Dense2dTileKMemFold` classification now cross-checks the recovered `kk_tile -> tile_r -> tile_c` loop-domain chain, canonical `K_TILES`/`ROW_TILES`/`COL_TILES`/`TILE_K` schedule symbols, hoisted or non-hoisted LHS placement, and fold assignment ancestry through resolver-owned loop/effect facts while preserving structural statement recovery and the existing exact Tile-K phase access matchers. Added fail-closed coverage for equal-valued wrong schedule symbols, hoisted LHS layout, wrong fold-K bound symbol, and swapped RHS/C-preload phase order. Local verification passed `cargo test -p spatial-rs-core --locked tile_k_phase_spine_guard -- --nocapture`, `cargo test -p spatial-rs-core --locked rank2_tile_memfold_outer_k -- --nocapture`, `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k`, `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6_fixed_32`, `cargo test --locked --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-plan-phase-spine-final`, `cargo fmt --all -- --check`, and `git diff --check` in both repos. Boundary: local resolver/classifier hardening only; checked payloads, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence are unchanged, so no EC2/Vitis rerun was needed; this is still not generic GEMM, generic Spatial `MemFold`, broad Scala source compatibility, broader `par`/banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation, or timing closure.
- Relaxed the fixed Lab2 Part5/Part6 GEMM raw-wrapper source adapters in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `a66e88f9c8b9c94f12fde1d8e2ad967f1abc896b`: the accepted wrappers now require the fixed `runtimeArgs = "32 32 32"`, `FixPt[TRUE,_24,_8]`, exact `ArgIn`/`setArg`/`DRAM`/`setMem` setup, tile-16 declarations, and one exact Part5 or Part6 `Accel` body, while host-side oracle/logging scaffolding may vary. Local verification passed `cargo test --locked --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-plan-host-scaffold`, `cargo fmt --all -- --check`, and `git diff --check` in both repos. Boundary: checked payloads, generated HLS/manifest output, validation membership, and vendor-HLS evidence are unchanged; no EC2/Vitis rerun was needed for this local source-adapter cleanup, and this is still not generic Scala source compatibility, generic GEMM, generic `MemFold`, broader `par`, automatic banking, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation, or timing closure.
- Captured fresh current-head 28-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `954b6259f8e19c1eba5aa7c7f7694441cf98e5cf`, after the Tile-K C-accumulation resolved-facts migration and same-span loop-symbol resolver cleanup. EC2 host `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-tile-k-facts-954b625` from `/home/ubuntu/spatial-rs-runs/tile-k-facts-954b625/spatial-rs` with return code 0 across all 28 validation programs. Each program reported `csim=true` and `csynth=true`; durable evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-tile-k-facts-current-head/`, and code commit `2315863` records the imported evidence plus parser/manifest tests. The scheduled Part6 canary again reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7885 cycles, interval 7886 cycles, and utilization estimate 8 BRAM_18K, 128 DSP, 15417 FF, and 12192 LUT. Boundary: current-head evidence refresh only; no new validation-program member or emitted-HLS surface, and no generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation/place-and-route, timing closure, generic GEMM, or broad Scala source compatibility.
- Promoted the Tile-K same-span loop-symbol workaround into `ResolvedHir` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `ResolvedHir::loop_index_ident_matches_symbol` now answers whether a `HirIdent` can correspond to a specific loop `SymbolId`, covering Lab2 MemFold sugar where the parser synthesizes accumulation sibling loops by cloning the partial loop idents and spans. Added a focused resolver regression for same-name/same-span `ii` siblings and updated the C-accumulation matcher to consume the resolver API instead of inspecting `symbols_named`/`SymbolKind` locally. Boundary: local resolver/classifier API cleanup only; generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice.
- Migrated the Tile-K C-accumulation matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax/operator guard: the accepted `c_tile[ii, jj] := c_tile[ii, jj] + partial_tile[ii, jj]` shape now cross-checks the C-tile write, C-tile read, and partial-tile read as rank-2 access groups on the same parent statement, with row/column lane symbol identity. The matcher also accepts Lab2 MemFold sugar's same-span sibling loop symbols by checking all matching loop-index symbols instead of only the first same-name/same-span symbol. Swapped destination lanes, wrong C read lanes, and wrong partial read lanes remain fail-closed. Boundary: LHS/RHS loads, C preload, final store, and partial product are already fact-backed; broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Migrated the Tile-K partial-product matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax/operator guard: the accepted `partial_tile[ii, jj] := lhs_tile[ii, k_idx] * rhs_tile[k_idx, jj]` shape now cross-checks the partial SRAM write, LHS SRAM read, and RHS SRAM read as rank-2 access groups on the same parent statement, with row/column/K lane symbol identity. Swapped partial lanes, wrong LHS row lanes, and wrong RHS K lanes remain fail-closed. Boundary: LHS/RHS loads, C preload, and final store are already fact-backed; C accumulation/fold update, broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Migrated the Tile-K final-store matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax guard: the accepted `c[tile_r*TILE_R + ii, tile_c*TILE_C + jj] := c_tile[ii, jj]` shape now cross-checks global-write/local-read rank-2 access groups, same parent statement, row/column lane symbol identity, tile-row/tile-column loop symbol identity, and const-backed `TILE_R`/`TILE_C` coefficient-symbol provenance. Wrong equal-valued row/column tile constants, swapped local lanes, wrong tile-row/tile-column symbols, and split-parent staged reads remain fail-closed. Boundary: LHS/RHS loads and C preload are already fact-backed; fold/update, broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Migrated the Tile-K C-preload matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax guard: the accepted `c_tile[ii, jj] := c[tile_r*TILE_R + ii, tile_c*TILE_C + jj]` shape now cross-checks local/global rank-2 access groups, same parent statement, row/column lane symbol identity, tile-row/tile-column loop symbol identity, and const-backed `TILE_R`/`TILE_C` coefficient-symbol provenance. Wrong equal-valued row/column tile constants, swapped local lanes, and wrong tile-row/tile-column symbols remain fail-closed. Boundary: LHS/RHS loads are already fact-backed; fold/store, broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Migrated the Tile-K RHS-load matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax guard: the accepted `rhs_tile[k_idx, jj] := rhs[kk_tile*TILE_K + k_idx, tile_c*TILE_C + jj]` shape now cross-checks local/global rank-2 access groups, same parent statement, loop-index symbol identity, and const-backed coefficient-symbol provenance. Wrong equal-valued K/column tile constants, swapped local lanes, and wrong tile-column symbols remain fail-closed. Boundary: LHS load is already fact-backed; C preload, fold/store, broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Migrated the Tile-K LHS-load matcher in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` to consume resolver-owned `ResolvedHir` affine/index-use facts while retaining the existing syntax guard: the accepted `lhs_tile[ii, k_idx] := lhs[tile_r*TILE_R + ii, kk_tile*TILE_K + k_idx]` shape now cross-checks local/global rank-2 access groups, same parent statement, loop-index symbol identity, and const-backed coefficient-symbol provenance. Wrong equal-valued tile constants, commuted syntax, scalar-staged LHS reads, swapped local lanes, and wrong outer-K tile symbols remain fail-closed. Boundary: RHS load, C preload, fold/store, broader Tile-K phase recognition, generated HLS/manifest output, validation-program membership, and vendor-HLS evidence remain unchanged; Vitis was not executed for this slice, and this is not generic Spatial `MemFold`, GEMM, `par`, automatic banking, dynamic/tail `numel_k`, K tails, or broad Scala source compatibility.
- Added resolved-HIR affine/index-use facts in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `ResolvedHir` now records resolver-owned memory-access index facts joined to resolved symbols, access occurrence ids, parent statements, enclosing loop domains, conditional depth, and const-backed affine stride provenance. Coverage includes rank-1/rank-2 element indices, tile-lane and canonical tile-K load contracts, same-named sibling symbol identity, range start/end-exclusive facts, Lab3 line-buffer row/range and RegFile wildcard facts, expression-conditional depth, exact source spans, affine normalization, unsupported/non-affine markers, and oversized-`usize` overflow handling. Local verification passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked resolved_hir_ -- --nocapture` with 42 resolver tests, `cargo test --locked --quiet`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check` before commit. Six GPT-5.5 xhigh reviewers plus focused re-reviews cleared data-model, traversal, test, docs, Tile-K-readiness, and Rust edge-case concerns after adding access grouping, parent-statement joins, coefficient-symbol provenance, and the Tile-K contract test. Boundary: compiler-foundation metadata/query surface only; no new Spatial syntax, checked IR, generated HLS, validation-program membership, vendor-HLS evidence, generic `MemFold`/GEMM/`par`, automatic banking inference, or broad Scala source compatibility. Dense/tile-K classifiers still use private structural matching until a separate explicit migration consumes these resolver facts under parity tests.
- Added resolver-facing loop query helpers and access/effect loop joins in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `ResolvedHir` now exposes `loop_domain`, `root_loop_domains`, and `child_loop_domains`, and `AccessFact`/`EffectFact` carry the innermost enclosing `LoopDomainId`. Focused verification passed `cargo test -p spatial-rs-core --locked resolved_hir_ -- --nocapture` with 31 resolver tests, including FIFO access/effect kind pairing, `foreach par`, unit sequential foreach, FSM init/cond/step/body, fold-load, MemReduce/MemFold body/post-store, and loop-depth/loop-id invariant coverage; local verification also passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`. Boundary: still compiler-foundation metadata/query surface only; no syntax, checked-IR, HLS, validation-membership, or vendor-evidence change, and tile-K classifiers still need affine index-use facts plus an explicit migration before replacing private structural matching.
- Added resolved-HIR loop identity and nesting facts in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: each `LoopDomain` now has a stable resolver-local id, source span, parent block, optional parent loop, and nesting depth. MemReduce/MemFold domains are created before body traversal and backfilled with their accumulator/temp reduction pair afterward, so loops inside reduction bodies can point to the enclosing reduction domain. Local verification passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`; three GPT-5.5 xhigh reviewers cleared the traversal/order risk. Boundary: still compiler-foundation metadata only; no syntax, HLS, validation-membership, or vendor-evidence change, and tile-K still needs resolver-facing child/root queries plus effect/access loop joins before consuming these facts.
- Added a resolved-HIR loop schedule fact seed in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `ResolvedHir::LoopDomain` now records optional `LoopSchedule` metadata for foreach, sequential foreach, reduce/fold expressions, and MemReduce/MemFold statements, including resolved bound/step/par symbols, source text, const-backed bound/step values, and positive `par` factors. The resolver now records these facts observationally from the enclosing scope so self-bound malformed loops such as `foreach i in 0..i par i` do not resolve schedule bounds against their own loop index. Local verification passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked resolved_hir_ -- --nocapture`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`; GPT-5.5 xhigh reviewers cleared the original scope/test blocker after re-review. Boundary: compiler-foundation metadata only; no new Spatial syntax, no generated-HLS change, no validation-program membership change, no fresh EC2/Vitis evidence, and not yet enough to replace the tile-K classifier's private structural schedule matching because loop nesting/phase identity and affine index-use facts are still absent.
- Promoted the exact Lab2 Part1/Part2 memory-reduction source adapters in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known raw `Lab2Part1SimpleMemReduce` and `Lab2Part2SimpleMemFold` wrappers now emit generated Rust frontend source for `MemReduceOnes16` / `MemFoldOnes16` and compile through the existing frontend/HIR/classifier path instead of recursing through static canonical-source strings. Generated HLS and manifests remain equal to the existing canaries, validation-program membership remains 28, and no new EC2/Vitis run is required for this behavior-preserving compiler-structure slice. Boundary unchanged: still not generic Spatial `MemReduce`/`MemFold`, arbitrary reducer bodies, dynamic bounds, rank-2 reductions, scheduling, banking, board execution, Vivado implementation, timing closure, or broad Scala source compatibility.
- Pinned scheduled Part6 HLS guardrails in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: added an exact emitted-C++ snapshot for `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` and explicit partition-validator coverage for reordered, wrong-factor, and extra-entry Part6 recipes. Local verification passed before commit; this was test-only guard hardening after the 28-program current-head EC2/Vitis checkpoint, so it did not change generated HLS or require fresh vendor execution.
- Captured current-head 28-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `3e094611eca82a97a9e1af2bb90b1ddf423c5700`, after the scheduled tile-K MemFold partition-contract hardening and crate-private HLS partition-helper refactor. EC2 host `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-partition-helper-3e09461` from `/home/ubuntu/spatial-rs-runs/partition-helper-3e09461/spatial-rs` with return code 0 across all 28 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-partition-helper-current-head/`. The scheduled Part6 canary again reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7885 cycles, interval 7886 cycles, and utilization estimate 8 BRAM_18K, 128 DSP, 15417 FF, and 12192 LUT. Boundary: this refreshes vendor-HLS evidence for the current partition-helper foundation only; it does not add generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation/place-and-route, timing closure, or broad Scala source compatibility.
- Centralized the scheduled tile-K MemFold HLS partition recipe in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `spatial-rs-hls` now has a crate-private partition helper that both the HLS plan builder and emitter validation use for the exact Part6 ordered array-partition recipe, removing the duplicate hand-coded recipe from `plan.rs` and `emit.rs`. Added module-level tests for the serial empty recipe, the ordered `par 2x16` Part6 recipe, and incomplete-recipe rejection. Verification passed `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo fmt --all -- --check`, and `git diff --check`. Boundary: behavior-preserving maintainability refactor only; no new Spatial syntax, no broader scheduling or banking inference, no validation-program membership change, and no fresh EC2/Vitis execution beyond the current-head `2026-07-02-schedule-profile-current-head` evidence checkpoint.
- Hardened the scheduled tile-K MemFold HLS boundary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the HLS emitter now rejects scheduled Part6 plans unless they carry the exact ordered array-partition recipe used by the Vitis-proven canary, and the partition pragma renderer rejects zero dimensions, zero cyclic factors, and duplicate variable/dimension entries before producing C++ pragmas. Added core checked-IR boundary tests that reject `par 2x16` under the serial tile-K MemFold kernel name and reject serial `par 1x1` under the scheduled Part6 kernel name. Verification passed `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo fmt --all -- --check`, and `git diff --check`. Boundary: this is local robustness and regression coverage only; no new Spatial syntax, no broader `par`, no automatic banking inference, no validation-program membership change, and no fresh EC2/Vitis execution beyond the current-head `2026-07-02-schedule-profile-current-head` evidence checkpoint.
- Captured current-head 28-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `6667d0a35ccec2c601aff13fc91ac69bf3c967a5`, after the tile-K MemFold schedule-profile and HLS schedule/partition-plan refactors. EC2 host `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-schedule-profile-6667d0a` from `/home/ubuntu/spatial-rs-runs/schedule-profile-6667d0a/spatial-rs` with return code 0 across all 28 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-schedule-profile-current-head/`. The scheduled Part6 canary again reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7885 cycles, interval 7886 cycles, and utilization estimate 8 BRAM_18K, 128 DSP, 15417 FF, and 12192 LUT. Boundary: this refreshes vendor-HLS evidence for the current schedule-profile foundation only; it does not add generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, board execution, Vivado implementation/place-and-route, timing closure, or broad Scala source compatibility.
- Extracted the first reusable schedule-profile layer after the 28-program Part6 checkpoint in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `Dense2dTileKMemFold` checked IR now exposes `schedule_profile()` as `Serial` or `PartialTile { row_factor, col_factor }`, and the HLS plan maps that core profile into explicit schedule and ordered array-partition plans instead of treating raw `partial_row_par` / `partial_col_par` as the only semantic API. Local TDD evidence: the new core schedule-profile assertions failed before the API existed, then passed; focused core and HLS schedule-plan tests pass. Boundary: this is a maintainability/foundation slice only. It adds no new Spatial syntax, no new supported `par` pair, no new validation-program membership, no new generated-HLS behavior, and no new EC2/Vitis evidence beyond the existing `2026-07-02-lab2-part6-scheduled` checkpoint.
- Superseded the earlier serial Part6 compatibility boundary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: exact raw `Lab2Part6GEMM` now canonicalizes to a distinct scheduled canary, `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, rather than the serial Part5/outer-K payload. The checked IR carries `partial_row_par = 2` and `partial_col_par = 16`; the HLS emitter generates local-array partition pragmas, `PIPELINE II=1`, and `UNROLL factor=2` / `UNROLL factor=16` for the partial-tile multiply and fold-update loops. EC2 host `[ec2-host — see private/ec2-lane.md]` completed Vitis 2025.1 `csim_design` and `csynth_design` for all 28 validation programs with return code 0; durable evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-lab2-part6-scheduled/`. The scheduled Part6 canary reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7885 cycles, interval 7886 cycles, and utilization estimate 8 BRAM_18K, 128 DSP, 15417 FF, and 12192 LUT. Boundary: this is exact fixed Lab2 Part6 scheduling evidence, not generic Spatial `par`, automatic banking inference, dynamic/tail `numel_k`, K tails, dynamic dimensions, generic GEMM, board execution, Vivado implementation/place-and-route, timing closure, or broad Scala source compatibility.
- Added a narrow exact raw-wrapper adapter for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known local teaching `@spatial class Lab2Part6GEMM` source from `/Users/david/Documents/David_code/lab-2-accelerator-bandits-2/src/test/scala/Lab2GEMM.scala` now canonicalizes to the existing `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` / `Dense2dTileKMemFold v0` payload. The adapter accepts only the fixed `32x32x32`, tile-16, `FixPt[TRUE,_24,_8]`, single-`Accel` token stream with the exact Part6 `Foreach(numel_m by 1 par 2)` and `Foreach(numel_n by 1 par 16)` partial-tile loops. Local tests prove checked-program equality plus generated HLS/manifest equality against the Vitis-proven outer-K canary and assert no `UNROLL`, `PIPELINE`, or `ARRAY_PARTITION` pragmas are emitted. Verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-lab2-part6-plan`, and `git diff --check`. Boundary: no new validation-program membership or fresh EC2/Vitis execution evidence; this is source compatibility for the exact Part6 wrapper, not generic `par`, real HLS scheduling, unroll/banking policy, dynamic/tail `numel_k`, K tails, generic Spatial `MemFold`, broad fixed-point semantics, board execution, Vivado implementation, timing closure, or broad Scala source compatibility.

## 2026-07-01 — Rust rewrite Lab3 local teaching raw wrapper

- Captured current-head 27-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `f997672b55e5a729765eac31b6489c9536b823b7`, after adding the exact local teaching `Lab3Part1Convolution` raw source adapter: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-lab3-local-raw-f997672` from `/home/ubuntu/spatial-rs-runs/lab3-local-raw-f997672/spatial-rs` with return code 0 across all 27 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab3-local-raw-wrapper/`. `Lab3Part1Convolution` reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 2887 cycles, interval 2888 cycles, and utilization estimate 2 BRAM_18K, 0 DSP, 2561 FF, and 3085 LUT. Boundary: this proves the current head and canonical Lab3 payload still pass Vitis with the adapter code present; the raw local wrapper itself remains proven by parser equality plus generated HLS/manifest equality, not by a separate validation-program entry. Board execution, Vivado implementation/place-and-route, timing closure, generic Scala `LineBuffer`, `RegFile`, `Reduce`, generalized rotated-kernel support, dynamic dimensions, optimized line-buffer scheduling, and broad Spatial/Scala source compatibility remain unsupported.
- Added a narrow exact raw-wrapper adapter for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known local teaching `@spatial class Lab3Part1Convolution` source from `/Users/david/Documents/David_code/lab-3-accelerator-bandits/src/test/scala/Lab3.scala` now canonicalizes to the existing fixed `Lab3Part1Convolution` / `Stencil2d` payload. Local tests prove parser equality plus generated HLS/manifest equality against the canonical canary; near-misses for changed image dimensions, changed `LineBuffer` shape, removed `Pipe{sr.reset(c == 0)}`, and changed output-store `par` remain fail-closed. Boundary: no validation-program membership change or new EC2/Vitis evidence; generic Scala `LineBuffer`, `RegFile`, `Reduce`, generalized rotated-kernel support, dynamic dimensions, optimized line-buffer scheduling, board execution, Vivado implementation, timing closure, and broad Spatial/Scala source compatibility remain unsupported.

## 2026-07-01 — Rust rewrite Lab1 Part6 SRAM-tile fold canary

- Captured post-refactor 27-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `f0f3cb4ee03461fefacfeebc21dd8e4db38b8c51`, superseding the earlier "no fresh EC2/Vitis run" limitation for the SRAM-tile fold HIR/classifier refactor: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-lab1-part6-sram-hir-f0f3cb4` from `/home/ubuntu/spatial-rs-runs/lab1-part6-sram-hir-f0f3cb4/spatial-rs` with return code 0 across all 27 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab1-part6-sram-hir-refactor/`. `SramTileFoldSum32` reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 45 cycles, interval 59 cycles, and utilization estimate 2 BRAM_18K, 0 DSP, 1239 FF, and 1351 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the exact 27-program validation set after the non-lab SRAM canary moved through frontend/HIR/classifier; board execution, Vivado implementation/place-and-route, timing closure, generic Spatial `Fold`, arbitrary local-memory fold support, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, broad Scala source compatibility, and broader Spatial language coverage remain unsupported.
- Refactored `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` so raw Scala lab wrappers are quarantined in a `source_adapter` registry instead of living in `parse_accel`, and moved `SramTileFoldSum32` off the direct parser-built IR shortcut. The non-lab SRAM canary now parses through the frontend, lowers to HIR with a narrow fold-load prelude, classifies to checked `ScalarSramTileFold v0`, and preserves generated HLS/manifest equality for the exact raw `Lab1Part6ReduceExample` source adapter. Local evidence: focused core source-adapter/SRAM tests and HLS SRAM equality tests pass; no fresh EC2/Vitis run was added by this refactor, so the prior `2026-07-01-lab1-part6-sram` 27-program Vitis checkpoint remains the vendor-HLS evidence boundary. Boundary unchanged: no generic Spatial `Fold`, arbitrary nested folds, arbitrary local-memory folds/effects, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, board execution, Vivado implementation, timing closure, or broad Scala source compatibility.
- Captured 27-program EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `6a83cd2247258ec47f034f9b0f41bf0c131281b9`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-lab1-part6-sram-6a83cd2` from `/home/ubuntu/spatial-rs-runs/lab1-part6-sram-6a83cd2/spatial-rs` with return code 0 across all 27 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab1-part6-sram/`. `SramTileFoldSum32` reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 45 cycles, interval 59 cycles, and utilization estimate 2 BRAM_18K, 0 DSP, 1239 FF, and 1351 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the exact 27-program validation set only; board execution, Vivado implementation/place-and-route, timing closure, generic Spatial `Fold`, arbitrary local-memory fold support, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, broad Scala source compatibility, and broader Spatial language coverage remain unsupported.
- Added structural Lab1 Part6 coverage in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `ScalarSramTileFold v0` introduces a checked IR payload for one rank-1 `Dram<Int>[32]` input, one scalar `Int` output, one local `Sram<Int>[16]` tile, an explicit tile-load loop, an inner sum over the tile, and scalar accumulator writeback. The non-lab `SramTileFoldSum32` canary emits HLS with `int tile[16]`, a separate DRAM-to-tile load loop, a separate `partial += tile[inner]` loop, and no `PIPELINE`, `UNROLL`, or stream claim. The exact fixed raw `@spatial class Lab1Part6ReduceExample` source from the Lab 1 checkout now token-matches only the known `N=32`, `tileSize=16`, `Int`, single-`Accel`, `Reg(0)`, outer `Sequential.Fold`, local `SRAM` tile-load, inner `Fold`, and `ArgOut` writeback shape; it canonicalizes to `SramTileFoldSum32` with generated HLS/manifest equality. Local validation membership is now 27 programs, with host-C++ harness, Vitis dry-run, and plan-only coverage. Boundary: EC2/Vitis `csim_design`/`csynth_design` for the 27-program lane is still pending; generic Spatial `Fold`, arbitrary nested folds, arbitrary local-memory effects, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, board execution, Vivado implementation, timing closure, and broad Scala source compatibility remain unsupported.


## 2026-07-01 — Rust rewrite Lab2 mem-reduction raw wrappers

- Factored the Rust `MemReduceFill` / `MemFoldFill` classifier path in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` into one internal variant-driven shape extractor while preserving the separate public classifier entrypoints, checked IR kinds, diagnostics, and fail-closed boundaries. Focused memory-reduction and source-adapter tests passed locally. Boundary unchanged: no new accepted syntax, validation-program membership, generated-HLS change, or EC2/Vitis evidence.
- Tightened the Lab2 Part1/Part2 memory-reduction source-adapter boundary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known `@spatial class Lab2Part1SimpleMemReduce` and `@spatial class Lab2Part2SimpleMemFold` wrappers no longer require whole-file token equality. Instead, the adapter requires the exact class name, `out = DRAM[Int](16)` declaration, a single exact all-ones `Accel` memory-reduction/fold body, and explicit zero initialization for the MemFold case, while allowing host-side print/gold scaffolding to vary. The adapters still canonicalize to `MemReduceOnes16` / `MemFoldOnes16` with generated HLS/manifest equality. Boundary unchanged: no validation-program membership change or new EC2/Vitis evidence; changed output shape, changed accelerator body, generic Spatial `MemReduce`/`MemFold`, arbitrary reducer/fold bodies, dynamic bounds, rank-2 reductions, scheduling, banking, board execution, Vivado implementation, timing closure, and broad Spatial/Scala source compatibility remain unsupported.
- Added narrow exact raw-wrapper adapters for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known `@spatial class Lab2Part1SimpleMemReduce` and `@spatial class Lab2Part2SimpleMemFold` Lab 2 sources now token-match only the fixed all-ones memory-reduction/fold shapes and canonicalize to the existing `MemReduceOnes16` / `MemFoldOnes16` checked payloads. Local tests prove parser equality plus generated HLS/manifest equality against the canonical canaries; near-misses for wrong bounds, wrong fill values, missing or wrong zero initialization, wrong stores, extra `Accel`, comment spoofing, and token-split identifiers remain fail-closed. Boundary: no validation-program membership change or new EC2/Vitis evidence; generic Spatial `MemReduce`/`MemFold`, arbitrary reducer/fold bodies, dynamic bounds, rank-2 reductions, scheduling, banking, board execution, Vivado implementation, timing closure, and broad Spatial/Scala source compatibility remain unsupported.

## 2026-07-01 — Rust rewrite Lab2-like outer-K parser bridge

- Added a narrow exact raw-wrapper adapter for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the known `@spatial class Lab1Part4FIFOExample` Lab 1 source now token-matches only the fixed `N=32`, `tileSize=16`, `Int`, single-`Accel` FIFO tile-scale shape and canonicalizes to the existing `FifoTileScale32` / `Fifo1dTileScalarMul v0` checked payload. Local tests prove parser equality plus generated HLS/manifest equality against `FifoTileScale32`; near-misses for wrong length/runtime/tile/type, extra `Accel`, extra enqueue, changed `getMem`, commuted raw Scala multiply, comment spoofing, and token-split identifiers/operators remain fail-closed. Boundary: no validation-program membership change or new EC2/Vitis evidence; non-exact wrappers, generic `FIFO[Int](...)`, FIFO/stream ports, LIFO/StreamIn/StreamOut, dynamic or zero depths, tail tiles, arbitrary FIFO topologies/expressions, back-pressure/dataflow/throughput claims, board execution, Vivado implementation, timing closure, and broad Spatial source compatibility remain unsupported.
- Refreshed `a16401b9` EC2/Vitis evidence for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at source commit `a16401b9c1699d8f92d7ec0a93b04ae608d90617`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-block-comments-a16401b` from `/home/ubuntu/spatial-rs-runs/block-comments-a16401b/spatial-rs` with return code 0 across all 26 validation programs. Each program reported `csim=true` and `csynth=true`; evidence is captured under `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-block-comments-refresh/`. `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 41053 cycles, interval 41054 cycles, and utilization estimate 41 BRAM_18K, 64 DSP, 8120 FF, and 5896 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the exact `a16401b9` 26-program validation set only; board execution, Vivado implementation/place-and-route, timing closure, broad Scala source compatibility, structured Scala wrapper parsing, `Lab2Part6GEMM`, Part6 `par`, dynamic/tail K tiling, generic Spatial `MemFold`, banking, generic DMA, generic in-place alias analysis, FixPt tail tiles, and broader Spatial language coverage remain unsupported.
- Added shared frontend comment handling in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the Rust lexer now treats nested `/* ... */` block comments as whitespace, reports unterminated block comments with `spatial:E0002`, and keeps comment-split identifiers/operators as separate tokens rather than joining them. The unsupported-surface scanner now masks both line and block comments before looking for fail-closed constructs. Boundary unchanged: this is parser/frontend groundwork only; it does not add validation-program membership, EC2/Vitis evidence, Scala wrapper parsing, Part6 `par`, board execution, Vivado implementation, or timing closure.
- Tightened the raw `Lab2Part5GEMM` adapter in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the admission check now compares a comment-aware token stream rather than compacted source text, so comments and ordinary whitespace between tokens are accepted, but token-split identifiers/operators such as `ti/*x*/leK`, `tile N`, or `:/*x*/:` remain fail-closed. The exact fixed wrapper still canonicalizes to `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`, with HLS/manifest equality checked for exact and commented raw variants. Boundary unchanged: no validation-program membership or EC2/Vitis evidence change; non-exact wrappers, dynamic/tail `numel_k`, K tails, Part6 `par`, board execution, Vivado implementation, and timing closure remain unsupported.
- Added a narrow raw-wrapper adapter in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the exact fixed `@spatial class Lab2Part5GEMM` lab source now parses only when `runtimeArgs` prove `M=N=K=32`, `tileM/tileN/tileK` are all `16`, the type alias is `FixPt[TRUE,_24,_8]`, and there is one matching Part5 `Accel` body. The adapter canonicalizes to the existing `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` `Dense2dTileKMemFold v0` payload and preserves exact generated HLS/manifest equality. Boundary: no validation-program membership or EC2/Vitis evidence change; wrong dimensions, wrong tile sizes, wrong fixed-point type, extra `Accel` blocks, non-exact raw wrappers, dynamic/tail `numel_k`, K tails, Part6 `par`, board execution, Vivado implementation, and timing closure remain unsupported.
- Extended the parser-only Lab2-like outer-K bridge in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: exact static `val numel_k = min(TILE_K.to[Int], K - kk);` spelling is now accepted only under the static offset-loop proof and only for K tile ranges / `MemFold(...)(numel_k by 1)`. It emits no HIR statement, marks `numel_k` as the existing `TILE_K` alias, and preserves exact checked payload, generated HLS, and manifest equality against `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`. Boundary: no validation-program membership or EC2/Vitis evidence change; malformed or dynamic `numel_k = min(...)`, raw Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, Part6 `par`, board execution, Vivado implementation, and timing closure remain unsupported.
- Extended the parser-only Lab2-like outer-K bridge in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: exact static offset-loop spelling such as `Foreach(K by TILE_K)`, `Foreach(ROWS by TILE_R)`, and `Foreach(COLS by TILE_C)` now canonicalizes `kk/mm/nn` offset reads back to the existing tile-count `Dense2dTileKMemFold v0` payload. Local parser equality and HLS/manifest equality preserve `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` exactly. Boundary: no validation-program membership or EC2/Vitis evidence change; raw Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, dynamic/tail `numel_k`, non-exact offset steps, Part6 `par`, board execution, Vivado implementation, and timing closure remain unsupported.
- Extended the parser-only Lab2-like outer-K bridge in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `numel_k` is now accepted only as a declared static alias with the same value as `TILE_K`, and only in the static exact `Dense2dTileKMemFold v0` K load ranges and `MemFold(...)(numel_k by 1)` bound. The parser filters the alias before HIR/classification, preserving exact checked payload, generated HLS, and manifest equality against `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`. Boundary: no validation-program membership or EC2/Vitis evidence change; undeclared/mismatched `numel_k`, dynamic/tail K tiling, raw Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, Part6 `par`, board execution, Vivado implementation, and timing closure remain unsupported.
- Added the next parser-only source-spelling bridge for `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the static exact `Dense2dTileKMemFold v0` canary now accepts a Lab2-like outer-K shell/infix spelling with `inputs { a, b } inouts { c }`, `tileA_sram/tileB_sram/tileC_sram.buffer`, `kk/mm/nn`, a hoisted A-tile load before the column loop, infix rank-2 `::` tile loads/stores, and `MemFold(tileC_sram)(0 until TILE_K by 1) { k_idx => ... }{_+_}`. The bridge canonicalizes to the existing `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` checked payload, with exact generated HLS and manifest equality against the expanded static outer-K canary. Boundary: this is local parser/source-shape progress only and does not add validation-program membership or new EC2/Vitis evidence; raw Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, dynamic/tail K tiling, dynamic/tail `numel_k`, generic Spatial `MemFold`, Part6 `par`, banking, board execution, Vivado implementation, and timing closure remain unsupported.

## 2026-07-01 — Rust rewrite outer-K MemFold Vitis checkpoint

- Recorded EC2 Vitis 2025.1 execution evidence for the Rust `Dense2dTileKMemFold v0` canary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-outer-k-run` from `/home/ubuntu/spatial-rs-runs/outer-k-memfold-20260701-72aa062/spatial-rs` with return code 0 across all twenty-six validation programs. Each program reported `csim=true` and `csynth=true`, including `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`. Evidence is captured under `docs/vitis-validation/2026-07-01-outer-k-memfold/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. The new outer-K canary passed C simulation with `PASS MatrixTileMemFoldOuterKInPlaceFixPt32x32x32_kernel`, finished `csynth_design`, and reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 41053 cycles, interval 41054 cycles, and utilization estimate 41 BRAM_18K, 64 DSP, 8120 FF, and 5896 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the exact 26-program validation set including the static exact outer-K Rust-DSL canary; it does not prove original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, dynamic/tail K tiling, `numel_k`, generic Spatial `MemFold`, Part6 `par`, board execution, Vivado implementation/place-and-route, post-implementation timing closure, or broad Spatial language coverage. Next recommended slice: bridge the Vitis-proven outer-K canary toward the Lab2 source spelling while keeping raw Scala and dynamic K features fail-closed.

## 2026-06-30 — Rust rewrite source-spelling bridge

- Added the first static exact outer-K in-place C MemFold canary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` introduces a distinct `Dense2dTileKMemFold v0` checked IR payload instead of weakening the existing full-K `Dense2dTileMemFold v0` contract. The canary requires exact `K_TILES*TILE_K == K`, `TILE_K`-wide local A/B SRAMs, source-faithful `kk_tile -> tile_r -> tile_c` loop order, global K indexing as `kk_tile*TILE_K + k_idx`, and explicit inout `c` preload/store inside each K tile. It is now the 26th local validation program with parser/classifier tests, HLS codegen assertions, host-C++ harness coverage, and Vitis dry-run/plan-only sidecar coverage. Boundary: no EC2/Vitis `csim_design`/`csynth_design` evidence yet; raw Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, dynamic `ArgIn`, `numel_k`, K tails, generic Spatial `MemFold`, Part6 `par`, banking, board execution, Vivado implementation, and timing closure remain unsupported.
- Added a fourth parser-only MemFold source variation for the Rust `Dense2dTileMemFold v0` path in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: the Spatial-ish call form can now begin its lambda body with the canonical `let partial_tile = Sram<...>[...];`, which is hoisted into the existing checked payload before lowering. The exact `FixPt[TRUE,_24,_8]` fixture now exercises this body-local partial allocation spelling. This is frontend/source-shape progress only; renamed temps, raw Scala `SRAM[T](...)`, `val`, `MemFold(SRAM[T](...))`, original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, generic Spatial `MemFold`, `par`, banking, K tiling, FixPt tail tiles, and broader fixed-point semantics remain unsupported. No new vendor-HLS evidence is claimed because generated HLS and validation-program membership are unchanged.
- Added a third parser-only MemFold source variation for the Rust `Dense2dTileMemFold v0` path in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MemFold(c_tile)(0 until K by 1) { kk => ... partial_tile }{_+_};` now exposes a Spatial-ish lambda/range surface while normalizing to existing checked payloads; the bridge also accepts `(K by 1)` as an implicit-zero range. The exact `FixPt[TRUE,_24,_8]` fixture now exercises this spelling, with tail-canary equivalence regressions as well. This is frontend/source-shape progress only; original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, `MemFold(SRAM[T](...))`, generic Spatial `MemFold`, `par`, banking, K tiling, FixPt tail tiles, and broader fixed-point semantics remain unsupported. No new vendor-HLS evidence is claimed because generated HLS and validation-program membership are unchanged.
- Added a second parser-only MemFold source variation for the Rust `Dense2dTileMemFold v0` path in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `memfold c_tile with partial_tile over kk in 0..K { ... partial_tile }{_+_};` now exposes the returned temporary tile and plus combiner while normalizing to existing checked payloads. The exact `FixPt[TRUE,_24,_8]` fixture now exercises this spelling, with a tail-canary equivalence regression as well. This is frontend/source-shape progress only; original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM`, generic Spatial `MemFold`, `par`, banking, K tiling, FixPt tail tiles, and broader fixed-point semantics remain unsupported. No new vendor-HLS evidence is claimed because generated HLS and validation-program membership are unchanged.
- Added the first local source-spelling bridge for the Rust `Dense2dTileMemFold v0` tail/min path in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: parser-only sugar `memfold c_tile with partial_tile over kk in 0..K { ... };` now desugars to the same explicit K-loop, `partial_tile`, and `c_tile += partial_tile` checked payload as the Vitis-proven `MatrixTileMemFoldTail5x7x5` canary. This is local frontend/source-shape progress only: it does not accept original Scala `Lab2Part5GEMM` or `Lab2Part6GEMM`, generic Spatial `MemFold`, `par`, banking, K tiling, FixPt tail tiles, or broader fixed-point semantics, and it does not add new vendor-HLS evidence because generated HLS and validation-program membership remain unchanged.
- Refreshed the Rust rewrite evidence boundary after the 2026-06-29 tail/min MemFold run: EC2 Vitis 2025.1 on `[ec2-host — see private/ec2-lane.md]` passed all twenty-four validation programs through `csim_design` and `csynth_design`, including `MatrixTileMemFoldTail5x7x5`; durable evidence lives in `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-tail-min-memfold/`.

## 2026-06-29 — Rust rewrite rank-2 GEMM precursor

- Recorded EC2 Vitis 2025.1 execution evidence for `Dense2dTileMemFold v0` plus the exact `FixPt[TRUE,_24,_8]` canary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `[ec2-host — see private/ec2-lane.md]` completed `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/fixpt-memfold-20260629/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/fixpt-memfold-20260629/spatial-rs/target/vitis-validation-fixpt-memfold-20260629` with return code 0 across all twenty-three validation programs. Each program reported `csim=true` and `csynth=true`, including `MatrixTileMemFold4x6x5` and `MatrixTileMemFoldFixPt4x6x5`. Evidence is captured under `docs/vitis-validation/2026-06-29-fixpt-memfold/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. Fixed-point MemFold evidence: `MatrixTileMemFoldFixPt4x6x5` passed C simulation with `PASS MatrixTileMemFoldFixPt4x6x5`, finished `csynth_design`, and reported estimated Fmax 121.61 MHz, estimated clock 8.223 ns, latency 84 cycles, interval 60 cycles, and utilization estimate 6 BRAM_18K, 8 DSP, 6457 FF, and 5919 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the twenty-three-program validation set including the fixed-shape Rust-DSL `Int` and exact fixed-point MemFold GEMM canaries; it does not prove original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, generic Spatial `MemFold`, generic fixed-point widths, decimal fixed-point values, mixed element types, tail/min bounds, K tiling, `par`, board execution, Vivado implementation/place-and-route, post-implementation timing closure, or broad Spatial language coverage. Next recommended slice: start from this Vitis-proven checkpoint and add tail/min bounds before attempting a more source-compatible MemFold spelling.
- Added exact `FixPt[TRUE,_24,_8]` support for the fixed-shape `Dense2dTileMemFold v0` GEMM precursor in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MatrixTileMemFoldFixPt4x6x5` joins the validation list after the existing `MatrixTileMemFold4x6x5` `Int` canary; the Rust frontend/HIR/IR/manifest/HLS type spine carries one concrete fixed-point type for this path only, lowered as `ap_fixed<32, 24>`; the HLS host harness compiles locally through a host-only `ap_fixed` shim. Local verification covered `cargo test --locked -p ee109-examples`, `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_tile_memfold_fixpt -- --nocapture`, and `cargo test --locked -p spatial-rs-core fixpt -- --nocapture`. Boundary before the vendor run: no generic fixed-point widths, decimal fixed-point values, mixed `Int`/`FixPt` GEMM, Scala source compatibility, generic Spatial `MemFold`, tail/min bounds, K tiling, `par`, banking, performance scheduling, board execution, Vivado implementation, place-and-route, or timing closure.
- Added local Rust-DSL `Dense2dTileMemFold v0` support in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MatrixTileMemFold4x6x5` now parses through frontend/HIR, classifies into checked IR with three rank-2 input DRAMs (`lhs`, `rhs`, `cin`), one rank-2 output DRAM, four local SRAM tiles (`lhs_tile`, `rhs_tile`, `c_tile`, `partial_tile`), a C-preload phase, and one static K loop that computes a partial tile then folds it into `c_tile`. The HLS emitter now generates row-major C++ with four AXI pointer bundles, C preload, partial product tile, C-tile fold, and final store; the host harness compares against an independent `cin + lhs*rhs` Rust oracle. `MatrixTileMemFold4x6x5` joined the 22-program validation/dry-run set with local host-C++ and plan-only sidecar coverage before the fixed-point and 23-program Vitis entries recorded above. Boundary at this local checkpoint: this was not original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, generic Spatial `MemFold`, fixed-point arithmetic, tail/min bounds, K tiling, `par`, banking, performance scheduling, EC2 Vitis `csim_design`/`csynth_design`, board execution, Vivado implementation, or timing closure.
- Recorded EC2 Vitis 2025.1 execution evidence for `Dense2dTileDotAccum v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial` at commit `a96b4fb`: `[ec2-host — see private/ec2-lane.md]` completed `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/rank2-tile-dot-accum-20260629/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/rank2-tile-dot-accum-20260629/spatial-rs/target/vitis-validation-rank2-tile-dot-accum-20260629` with return code 0 across all twenty-one validation programs. Each program reported `csim=true` and `csynth=true`, including the new `MatrixTileAccum4x6x5` representative. Evidence is captured under `docs/vitis-validation/2026-06-29-rank2-tiled-dot-accum/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. Dot-accum evidence: `MatrixTileAccum4x6x5` passed C simulation with `PASS MatrixTileAccum4x6x5`, finished `csynth_design`, and reported estimated Fmax 121.61 MHz, estimated clock 8.223 ns, latency 84 cycles, and utilization estimate 4 BRAM_18K, 6 DSP, 5013 FF, 4537 LUT. Boundary: this proves Vitis C simulation and HLS synthesis for the twenty-one-program validation set including the fixed-shape Rust-DSL `Int` dot-accumulation canary; it does not prove original Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, fixed-point arithmetic, tail/min bounds, K tiling, buffered `MemFold`, `par`, generic GEMM, board execution, Vivado implementation/place-and-route, post-implementation timing closure, or broad Spatial language coverage. The EC2 noninteractive shell defaulted to old system Cargo 1.75.0, so the run explicitly used `/home/ubuntu/.cargo/bin/cargo` 1.96.0; no local or remote lockfile downgrade was needed.
- Added local Rust-DSL `Dense2dTileDotAccum v0` support in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MatrixTileAccum4x6x5` now parses through frontend/HIR, classifies into checked IR with two rank-2 input DRAMs, one rank-2 output DRAM, three local SRAM tiles, explicit zero-init, and one static K reduction loop, emits row-major HLS C++ with three AXI pointer bundles, and joins the twenty-one-program validation/dry-run set. Local verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and 21-program plan-only Vitis sidecar generation. Boundary before EC2 was local host-C++ and plan-only only; the follow-up EC2 Vitis evidence is recorded above.

## 2026-06-28 — Rust rewrite frontend/HIR foundation

- Replaced the classification-stage parser string candidate gates with HIR-recursive feature signals in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `CompileError` now carries boxed HIR on classification failures; `HirFacts` records source spans for control/FSM, FIFO, reduction/fold/mem-reduction, local-window, rank-2 DRAM, and parallel markers; `parse_accel` uses those facts for valid-HIR generic unsupported `spatial:E020x` diagnostics and keeps source scanning as the fallback for lexer/parser/HIR-construction failures. Tightened stencil and memory-reduction candidate markers so generic local-window and GEMM-like memory-fold surfaces stay `E020x` while true narrow feature near-misses keep `E040x`/`E041x`. Also fixed a `const_usize` eager-indexing panic on missing constants. GPT-5.5 xhigh review found and rechecked the local-window-pair blocker. Local verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-hir-signals-plan`, a 19-planned-kernel summary count, and `git diff --check`. Boundary: this adds compiler/fail-closed structure only; it claims no new syntax, no HLS output change, and no fresh EC2 Vitis execution evidence.
- Routed `parse_accel` through the stage-aware compiler spine in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: added crate-private `CompileStage::{Parse,Hir,Classify}`, `CompileError`, and `compile_source_detailed`, then made the parser entry call that spine while preserving the existing unsupported pre-scan policy and fail-closed diagnostic precedence. A follow-up cleanup made stage handling explicit and removed duplicated saved-diagnostic ladders with a small helper. GPT-5.5 xhigh fail-closed and code-quality reviewers found no required changes. Local verification passed `cargo fmt --all -- --check`, `cargo test -p spatial-rs-core --locked detailed_compile`, `cargo test -p spatial-rs-core --locked parser`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-parser-spine-plan`, a 19-planned-kernel summary count, and `git diff --check`. Boundary: this is compiler structure only; it claims no new syntax, no HLS output change, and no fresh EC2 Vitis execution evidence.
- Started the post-FIFO compiler-foundation phase in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: six GPT-5.5 xhigh reviewers audited frontend/HIR, classifier migration, typed-HIR gaps, HLS invariants, acceptance tests, and documentation. Added repo plan `docs/superpowers/plans/2026-06-28-post-fifo-compiler-foundation.md` and research-vault plan `[[2026-06-28-post-fifo-compiler-foundation-plan]]`. Implemented the first behavior-preserving slice: `compiler::compile_source(&SourceFile)` returns both `HirProgram` and checked `Program`; `hir::facts::HirFacts` indexes constants, ports, loop-local memories, and FIFO enqueue/dequeue effects; and the FIFO v0 classifier now consumes those facts for local FIFO/effect discovery while preserving the exact accepted shape. Local verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-post-fifo-foundation-plan`, a 19-planned-kernel summary count, and `git diff --check` in both the Rust repo and research vault. Boundary: this adds compiler structure only; it claims no new Spatial syntax, no generic FIFO/streams, no HLS output change, and no new EC2 Vitis execution evidence.
- Recorded EC2 Vitis 2025.1 execution evidence for `Fifo1dTileScalarMul v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run --manifest-path /home/ubuntu/spatial-rs-runs/fifo-v0-20260628/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/fifo-v0-20260628/spatial-rs/target/vitis-validation-fifo-v0-20260628` with return code 0 across all nineteen validation programs. Each program reported `csim=true` and `csynth=true`, including the new `FifoTileScale32` representative. Evidence is captured under `docs/vitis-validation/2026-06-28-fifo-v0/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. FIFO-specific evidence: `FifoTileScale32` passed C simulation with `PASS FifoTileScale32`, `CSim done with 0 errors`, Vitis generated RTL FIFOs for `tile_in` and `tile_out`, finished `csynth_design`, and reported estimated Fmax 127.15 MHz. Boundary: this proves Vitis C simulation and HLS synthesis for the nineteen-program validation set including narrow Rust-DSL FIFO tile scaling; it does not prove original Scala `Lab1Part4FIFOExample` source compatibility, generic Spatial FIFO/streams, AXI stream ports, back-pressure modeling, throughput optimization, board execution, Vivado implementation/place-and-route, post-implementation timing closure, or broad Spatial language coverage. EC2 used Rust/Cargo 1.75.0, so the copied remote workspace used a remote-only `Cargo.lock` v4-to-v3 compatibility downgrade; local `spatial-rs` remains unchanged.
- Added local Rust-DSL FIFO v0 support in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `FifoTileScale32` now parses through frontend/HIR, classifies as `Fifo1dTileScalarMul`, validates two checked FIFO memories, emits real local `hls::stream<int>` plus stream-depth pragmas, uses a host-only `hls_stream.h` shim only for local `c++` preflight, and joins the nineteen-program validation/dry-run set. GPT-5.5 xhigh review caught two boundary gaps before Vitis: a Rust mini-DSL kernel named `Lab1Part4FIFOExample` could classify as FIFO v0, and parseable FIFO-memory near misses without valid dequeue shape could still hit generic `spatial:E0201`. Added regressions and fixed both: the reserved Scala lab name now rejects with `spatial:E0412`, and FIFO-shaped near misses reach the targeted `spatial:E0412` diagnostic. Local verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-fifo-v0-plan-check`, a 19-planned-kernel summary count, and host-shim leakage scans. Boundary: original Scala `Lab1Part4FIFOExample` remains rejected, generic FIFO/LIFO/streams remain unsupported, and the host-only shim is not vendor evidence.
- Recorded the post-18 Vitis next-slice decision in `[[2026-06-28-post-18-vitis-next-slice-decision]]` and refreshed the Rust rewrite roadmap/stability matrix: the next sequence is documentation refresh, a behavior-preserving classifier/HIR guardrail slice, then a narrow FIFO v0 with real `hls::stream` emission and fresh 19-program Vitis evidence. GEMM/fixed-point remains deferred until FIFO and classifier/module boundaries are stable. Boundary remains explicit: the current 18-program evidence proves Vitis C simulation and HLS synthesis only for the listed adapters, supported-feature representatives, and memory-reduction canaries; it does not prove generic streams, generic memory reductions/folds, fixed-point GEMM, board execution, Vivado implementation/place-and-route, timing closure, or broad Spatial language coverage.
- Recorded EC2 Vitis 2025.1 execution evidence for the `MemReduceFill v0` / `MemFoldFill v0` Rust-DSL semantic representatives in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-mem-reductions-v0-20260628` with return code 0 across all eighteen validation programs. Each program reported `csim=true` and `csynth=true`: the seven EE109 reference-corpus adapters, the synthetic `Lab3Part0MatrixCopyRowMajor` groundwork adapter, plus `ScalarAffine4`, `ScalarReduceSum16`, `ScalarFoldTileSum32`, `MemReduceOnes16`, `MemFoldOnes16`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, `ControlFsm32`, and `SobelStencil12x20`. Evidence is captured under `docs/vitis-validation/2026-06-28-mem-reductions-v0/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. Boundary: this proves Vitis C simulation and HLS synthesis for the eighteen-program validation set including the simple Lab2 all-ones memory-reduction semantics in the Rust DSL, not original Scala source compatibility, generic Spatial `MemReduce`/`MemFold`, fixed-point GEMM, FIFO/streams, banking, scheduling/performance pragmas, board execution, Vivado implementation/place-and-route, post-implementation timing closure, or broader Spatial language coverage.
- Added local Rust-DSL semantic representatives for the simple Lab2 memory-reduction behaviors in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `MemReduceOnes16` and `MemFoldOnes16` now parse through the frontend, lower through HIR, classify into checked `MemReduceFill` / `MemFoldFill` payloads, emit simple HLS C++ array loops and full host harnesses, and are included in the eighteen-program validation/dry-run set. `895163d` added the HLS emission/harness slice after GPT-5.5 xhigh review; the follow-up Task 6 integration adds the EE109 examples, stale-count test updates, docs, and evidence-boundary guardrails. Local verification passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin ee109-examples`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-mem-reductions-plan`, and `git diff --check`. Boundary: this semantically covers the simple Lab2 all-ones MemReduce/MemFold behavior in the Rust DSL, not original Scala source compatibility, generic Spatial `MemReduce`/`MemFold`, GEMM, FIFO/streams, fixed-point arithmetic, scheduling/performance pragmas, board execution, or EC2 Vitis `csim_design`/`csynth_design`; the next vendor gate is an eighteen-program `run-vitis-validation --execute --mode both` run.
- Recorded EC2 Vitis 2025.1 execution evidence for `ScalarFold v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/HLS-spatial`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-scalar-fold-v0-20260628` with return code 0 across all sixteen validation programs. Each program reported `csim=true` and `csynth=true`: the eight EE109 accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`, `ScalarFoldTileSum32`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, `ControlFsm32`, and `SobelStencil12x20`. Evidence is captured under `docs/vitis-validation/2026-06-28-scalar-fold-v0/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports. Local verification before evidence import passed `cargo fmt --all -- --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked --bin ee109-examples`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-scalar-fold-plan`, `git diff --check`, and generated scalar-fold bundle leakage scan. Boundary: this proves Vitis C simulation and HLS synthesis for the sixteen-kernel validation set including narrow tiled rank-1 `ScalarFold v0`, not board execution, Vivado implementation/place-and-route, post-implementation timing closure, generic `Fold`, generic `Reduce`, `MemReduce`, `MemFold`, arbitrary bodies, tail tiles, non-unit `par`, unbounded `Int` accumulation, or broader Spatial language coverage.
- Recorded EC2 Vitis 2025.1 execution evidence for `ScalarReduce v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `9b11fdd`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-scalar-reduce-v0-20260628` with return code 0 across all fifteen validation programs. Each program reported `csim=true` and `csynth=true`: the eight EE109 accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, `ControlFsm32`, and `SobelStencil12x20`. Evidence is captured under `docs/vitis-validation/2026-06-28-scalar-reduce-v0/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports; generated Vitis project internals were intentionally left out of the durable artifact. The EC2 noninteractive shell defaulted to old system Cargo, so the run explicitly used `/home/ubuntu/.cargo/bin/cargo` 1.96.0; no local or remote lockfile downgrade was needed. Boundary: this proves Vitis C simulation and HLS synthesis for the fifteen-kernel validation set including narrow `ScalarReduce v0`, not board execution, Vivado implementation/place-and-route, post-implementation timing closure, generic reductions, `Fold`, `MemReduce`, `MemFold`, input-DRAM reductions, non-unit `par`, unbounded `Int` accumulation, or broader Spatial language coverage.
- Added and committed narrow `ScalarReduce v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `9b11fdd`: added checked `ProgramKind::ScalarReduce` / `Stmt::ScalarReduce(ScalarReduce)` payload support for exactly one scalar `Int` output assigned by `out := reduce i in 0..N par P { i }` with static `1 <= N <= 65536`, `P == 1`, no inputs, no DRAM ports, and no local memories. The HLS emitter generates a simple scalar output pointer kernel and host harness with an independent arithmetic-series oracle; `ScalarReduceSum16` is now the fifteenth validation-program representative. Review fixes rejected output-name collisions with generated HLS temporaries and overflow-sized `N` at both parser/classifier and checked-IR validation boundaries. Local verification before commit passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-scalar-reduce-v0-plan`, `git diff --check`, and generated-artifact leakage scan. GPT-5.5 xhigh spec and HLS/code-quality reviewers cleared the slice after blocker fixes. Boundary: this is not generic `Fold`, `Reduce`, `MemReduce`, `MemFold`, arbitrary reduce bodies, input-DRAM reductions, non-unit `par`, performance scheduling, or resource optimization support.
- Recorded EC2 Vitis 2025.1 execution evidence for the Lab3 convolution frontend/HIR route in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `56b166a`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-lab3-frontend-hir-20260628` with return code 0 across all thirteen validation programs. Each program reported `csim=true` and `csynth=true`: the eight EE109 accepted adapters plus `ScalarAffine4`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, and `ControlFsm32`. Evidence is captured under `docs/vitis-validation/2026-06-28-lab3-frontend-hir/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports; generated Vitis project internals were intentionally left out of the durable artifact. During the EC2 run, system Cargo was 1.75.0, so the copied remote bundle used a remote-only Cargo.lock v4-to-v3 downgrade; no local lockfile change was made. A full remote `cargo test --locked` preflight was not used as evidence because Cargo 1.75 did not provide the `CARGO_BIN_EXE_*` integration-test environment expected by one local binary test; local verification for the same source passed `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`. Boundary: this proves Vitis C simulation and HLS synthesis for the thirteen-kernel validation set after the Lab3 frontend/HIR route, not board execution, Vivado implementation/place-and-route, post-implementation timing closure, generic local-window/stencil support, or broad Spatial language coverage.
- Committed the Lab3 convolution frontend/HIR route in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `9dfce93`: removed the runtime compact-source equality path for `Lab3Part1Convolution`, added Lab3-only lexer/AST/HIR coverage for `LineBuffer`, `RegFile`, `reduce`, `par`, `||`, `<<=`, row load/store, shift, reset, `mux`, and `abs`, and added an exact classifier that rebuilds the existing fixed `ProgramKind::Lab3Part1Convolution` adapter only for the canonical EE109 shape. HLS output remains byte-exact against the existing Lab3 kernel snapshot and full 256-pixel host harness. Review fixes included preserving real frontend parse diagnostics for malformed Lab3 candidates and tightening the public-HIR classifier boundary with element-type and non-LUT payload checks. Local verification passed `cargo fmt --check`, `cargo test --locked` (including 111 core tests and 28 HLS codegen tests), `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-lab3-frontend-hir`, `git diff --check`, and generated-artifact leakage scan. GPT-5.5 xhigh spec and code-quality reviewers cleared the slice after two code-quality findings were fixed and re-reviewed. Boundary: this is a behavior-preserving frontend/HIR foundation for the fixed Lab3 adapter, not generic local-window/stencil support, not a new supported feature, and not new EC2 Vitis execution evidence.
- Recorded EC2 Vitis 2025.1 execution evidence for `ControlFsm v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `425e98e`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run --locked -p ee109-examples --bin run-vitis-validation -- --execute --mode both` with return code 0 across all thirteen validation programs. Each program reported `csim=true` and `csynth=true`: the eight EE109 accepted adapters plus `ScalarAffine4`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, and `ControlFsm32`. Evidence is captured under `docs/vitis-validation/2026-06-28-control-fsm-v0/` with README, summary JSON/Markdown, sidecar Tcl, Vitis logs, and csynth reports; generated Vitis project internals were trimmed from the durable artifact. During the EC2 run, system Cargo was 1.75.0, so the copied remote bundle used a remote-only Cargo.lock v4-to-v3 downgrade; no local lockfile change was made. Local verification after importing evidence passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`. Boundary: this proves Vitis C simulation and HLS synthesis for the thirteen-kernel validation set including narrow `ControlFsm v0`, not board execution, Vivado implementation/place-and-route, post-implementation timing closure, generic FSM/register/control support, or broad Spatial language coverage.
- Promoted narrow non-lab `ControlFsm v0` locally in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `5920aa2`: added checked `ProgramKind::ControlFsm` / `Stmt::ControlFsm(ControlFsm)` payload support for the exact fixed 32-step Lab2-style conditional FSM shape with renamed output, scratch SRAM, register, and state identifiers; added `ControlFsm32` as the thirteenth validation-program representative; emitted HLS C++/host harnesses from the checked payload; fixed host-harness shadowing by using a stable `actual` buffer; and kept malformed source shapes fail-closed with `spatial:E0405` while forged bad IR still fails at checked-IR validation. Local verification passed `cargo fmt --check`, `cargo test --locked` (including 106 core tests and 25 HLS codegen tests), `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-control-fsm-plan`, `git diff --check`, and generated-C++ leakage scan. Three GPT-5.5 xhigh reviewers checked spec/fail-closed behavior, HLS/harness name hygiene, and docs/evidence boundaries; two findings were fixed and re-reviewed clean. Boundary: `ControlFsm32` has local host-C++ plus Vitis dry-run/plan coverage only; fresh EC2 Vitis 2025.1 `csim_design`/`csynth_design` evidence for the thirteen-program set is still pending.
- Recorded EC2 Vitis 2025.1 execution evidence for the Lab2 FSM control-HIR route in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `dc7d6dc`: `[ec2-host — see private/ec2-lane.md]` completed `cargo run -p ee109-examples --bin run-vitis-validation -- --execute --mode both` with return code 0 across all twelve validation programs. Each program reported `csim=true` and `csynth=true`: the eight EE109 accepted adapters plus `ScalarAffine4`, `DenseScale64`, `LutBiasLookup`, and `MatrixCopy4x6`. Compact evidence is captured under `docs/vitis-validation/2026-06-28-lab2-fsm-hir/` with summary JSON/Markdown, Vitis logs, csynth reports, and TCL sidecars; generated Vitis project internals were intentionally left out of the durable repo artifact. During the EC2 run, system Cargo was 1.75.0, so the copied remote bundle used a remote-only Cargo.lock v4-to-v3 downgrade; no local lockfile change was made. Boundary: this proves Vitis C simulation and HLS synthesis for the current twelve validation kernels after the Lab2 control-HIR frontend route, not board execution, Vivado implementation, timing closure, generic `ControlFsm`, arbitrary registers, arbitrary conditionals, or broad Spatial language coverage.
- Committed the Lab2 FSM control-HIR route in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `93e39e8`: removed the Lab2 compact-source fast path from `parse_accel`, added Lab2 control tokens and AST/HIR nodes for `accel`, `Reg`, `fsm`, nested statement `if/else`, expression `if/else`, `reg.value`, subtraction, less-than, and equality, and added an exact HIR classifier that rebuilds the existing `ProgramKind::Lab2BasicCondFsm` / `Stmt::Lab2BasicCondFsm` adapter only for the canonical `Lab2Part3BasicCondFSM` shape. The generated HLS output and example status remain unchanged. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-lab2-fsm-hir`, `git diff --check`, and generated-C++ leakage scan. Three GPT-5.5 xhigh read-only reviewers found no spec/docs/blocking issues; one low span-underhighlighting issue in `IfElse` parsing was fixed with a red/green regression before commit. Boundary remains explicit: this is not reusable `ControlFsm v0`, generic registers, arbitrary conditionals, new HLS C++ behavior, or new EC2/Vitis execution evidence.
- Added and committed the Lab2 FSM control-HIR implementation plan in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `53a5bc7`. Six GPT-5.5 xhigh read-only planning agents compared frontend/HIR, Lab2 control, Lab3 stencil, HLS backend, validation, and roadmap lenses. Manager decision: after the supported-feature boundary hardening checkpoint, the next large implementation slice should route the exact canonical `Lab2Part3BasicCondFSM` adapter through real frontend AST, typed HIR, and exact classifier logic, while preserving `ProgramKind::Lab2BasicCondFsm`, `Stmt::Lab2BasicCondFsm`, and current HLS output. Boundary remains explicit: this is not `ControlFsm v0`, generic FSM support, generic register support, or a new vendor-HLS claim.
- Hardened the supported-feature boundary in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `ef021e4`: added dense generic-HIR near-miss regressions for computed lane indices, commuted multiply, wrong store ranges, and extra inner statements before checked IR collapse; added cross-feature fail-closed examples for `ScalarAffine4`, `DenseScale64`, `LutBiasLookup`, and `MatrixCopy4x6`; and made the Vitis dry-run/validation CLI tests derive expected kernel names from `validation_programs()` so all twelve current validation programs, including `MatrixCopy4x6`, stay covered. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-boundary-plan`, `git diff --check`, and generated-C++ leakage scan. No new EC2 Vitis run was required because this is a test-boundary hardening slice, not a generated-C++ or support-status change.
- Committed dense HIR unfusing in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `80c0bae`: the dense 1-D DRAM/SRAM path no longer lowers through fused AST/HIR whole-kernel markers. The accepted dense syntax now parses and lowers through generic `SequentialForeach`, loop-local `Sram<Int>[TILE]` declarations, load range, inner `Foreach`, indexed multiply assignment, and store range nodes; the dense classifier reconstructs the existing checked `Lab1Part2DramSramExample` adapter and `Dense1dScalarMul v0` feature from that generic HIR. The classifier now also checks local SRAM kind/type/dim at the HIR boundary, with a regression for local-memory shape drift. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-dense-hir-unfuse`, `git diff --check`, and generated-C++ leakage scan. A GPT-5.5 xhigh read-only reviewer found no commit-blocking issues; its non-blocking span, classifier-boundary, and docs consistency notes were addressed before commit. No new EC2 Vitis run was required because this is a behavior-preserving frontend/HIR foundation refactor, not a new feature or synthesis claim.

## 2026-06-27 — Rust EE109 MVP hardening

- Added the first crate-private HLS kernel-plan seam in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `12b5aee`: rank-2 copy now lowers through `spatial-rs-hls::plan::{HlsKernelPlan, HlsBodyPlan::Dram2dCopy}` before C++ rendering. The plan unifies the `Lab3Part0MatrixCopyRowMajor` adapter and `Dram2dCopy v0`/`MatrixCopy4x6` feature path, uses `Manifest::from_program` for entry symbol, parameter order, `cpp_param_type`, `m_axi_bundle`, and control bundle, and uses `spatial_rs_core::memory::Access` for row-major index rendering. Public `emit_kernel(&Program)` remains unchanged, harnesses and non-copy emitters remain direct templates, and no supported syntax was widened. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-rank2-plan`, `git diff --check`, and generated-C++ leakage scan. No new EC2 Vitis run was required because this is a behavior-preserving HLS architecture refactor, not a new feature or synthesis claim.
- Added the first shared checked row-major memory-access primitive in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `3a9f4ce`: `spatial_rs_core::memory::{MemoryObject, Access, AffineIndex}` now validates nonempty rank-1/rank-2 positive shapes, index-rank matching, and renders row-major C offsets from one source of truth. The rank-2 DRAM copy HLS emitter now uses this primitive for both `Lab3Part0MatrixCopyRowMajor` and `Dram2dCopy v0`/`MatrixCopy4x6`; generated behavior is unchanged, with only harmless extra parentheses in the emitted index expression. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-memory-effect-plan`, `git diff --check`, and generated-C++ leakage scan. No new EC2 Vitis run was required because this is a behavior-preserving foundation refactor, not a new support or synthesis claim; the prior twelve-kernel Vitis evidence remains current. Boundary: this is not yet generic effect scheduling, alias analysis, dense loop unfusing, FSM/control support, stencil lowering, or broad memory lowering.
- Promoted rank-2 row-major DRAM copy into the fourth Rust rewrite reusable supported feature: `Dram2dCopy v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp`. It accepts a non-lab kernel name, one rank-2 `Dram<Int>[ROWS, COLS]` input, one matching rank-2 output, nested static `foreach` row/column loops, and exactly `out[row, col] := in[row, col]`; it rejects swapped/computed indices, mismatched shapes, extra structure, generic rank-2 DRAM, `par`, reductions, stencils, alias/in-place claims, and non-`Int` element types. The original `Lab3Part0MatrixCopyRowMajor` adapter now routes through the frontend/HIR/classifier path instead of compact-source equality, while Lab3 convolution remains an explicit opaque adapter. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-dram2d-copy-plan`, `git diff --check`, and generated-C++ leakage scan. EC2 Vitis 2025.1 validation on `[ec2-host — see private/ec2-lane.md]` passed all twelve validation programs, the eight accepted adapters plus `ScalarAffine4`, `DenseScale64`, `LutBiasLookup`, and non-lab `MatrixCopy4x6`, with return code 0, `csim=true`, and `csynth=true`; evidence is captured under `docs/vitis-validation/2026-06-27-dram2d-copy/`. During the EC2 run, system Cargo was 1.75.0, so the copied remote bundle used a remote-only Cargo.lock v4-to-v3 downgrade; no local lockfile change was made. Boundary: this proves Vitis C simulation and HLS synthesis for the narrow rank-2 row-major copy feature, not generic memory/effect lowering, stencils, board execution, Vivado implementation, timing closure, or broad Spatial coverage.
- Promoted 2-D LUT lookup into the third Rust rewrite reusable supported feature: `LutLookup v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp`. It accepts a non-lab kernel name, one 2-D `Lut<Int>[R, C]`, three scalar `Int` inputs ordered as bias, row, and column, one scalar `Int` output, a rectangular row-major literal payload, and exactly `out := bias + table[row, col]`; it rejects reserved Lab2 adapter names as feature support, swapped/computed indices, extra LUT memories, and other out-of-scope expression forms. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, and `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/test-run-vitis-validation-lut-lookup-local` before the EC2 run. EC2 Vitis 2025.1 validation on `[ec2-host — see private/ec2-lane.md]` passed all eleven validation programs, the eight accepted adapters plus `ScalarAffine4`, `DenseScale64`, and non-lab `LutBiasLookup`, with return code 0, `csim=true`, and `csynth=true`; evidence is captured under `docs/vitis-validation/2026-06-27-lut-lookup/`. Boundary: this proves Vitis C simulation and HLS synthesis for the narrow LUT lookup feature, not generic table/memory indexing, runtime bounds safety, board execution, Vivado implementation, timing closure, or broad Spatial coverage.
- Promoted dense rank-1 memory behavior into the second Rust rewrite reusable supported feature: `Dense1dScalarMul v0` in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp`. It accepts a non-lab kernel name, one rank-1 `Dram<Int>[N]` input, one scalar `Int` multiplier, one rank-1 `Dram<Int>[N]` output, two rank-1 `Sram<Int>[TILE]` tiles, positive static `N`/`TILE` with `N % TILE == 0`, a unit-stride tiled load, an inner elementwise multiply, and a unit-stride store; it rejects the reserved Lab1 adapter name as feature support plus non-divisible tiles and other out-of-scope memory forms. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/test-run-vitis-validation-dense-final`, `git diff --check`, and generated-C++ leakage scan. EC2 Vitis 2025.1 validation on `[ec2-host — see private/ec2-lane.md]` passed all ten validation programs, the eight accepted adapters plus `ScalarAffine4` and non-lab `DenseScale64`, with return code 0, `csim=true`, and `csynth=true`; evidence is captured under `docs/vitis-validation/2026-06-27-dense1d/`. Boundary: this proves Vitis C simulation and HLS synthesis for the narrow dense scalar-multiply feature, not generic memory lowering, board execution, Vivado implementation, timing closure, or broad Spatial coverage.
- Promoted the Rust rewrite past exact adapters for the first time: `ScalarExpr v0` is now a reusable supported feature in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp`. It accepts a non-lab kernel name, 1-4 scalar `Int` inputs, one scalar `Int` output, one assignment, declared-input reads, nonnegative integer literals, `+`, `*`, and parentheses; it rejects reserved adapter names, unknown reads, excess inputs, DRAM/memories, and unsupported scalar language. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/test-run-vitis-validation-manual`, `git diff --check`, and generated-C++ leakage scan. EC2 Vitis 2025.1 validation on `[ec2-host — see private/ec2-lane.md]` passed all nine validation programs, the eight accepted adapters plus non-lab `ScalarAffine4`, with return code 0, `csim=true`, and `csynth=true`; evidence is captured under `docs/vitis-validation/2026-06-27-scalar-expr/`. Boundary: this proves Vitis C simulation and HLS synthesis for `ScalarExpr v0`, not board execution, Vivado implementation, timing closure, or broad Spatial coverage.
- Added and validated the durable Rust Vitis runner in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp`: `run-vitis-validation` now defaults to safe plan mode, emits per-kernel sidecar Tcl under `sidecars/`, writes Markdown and JSON summaries, optionally runs Vitis with `--execute --mode both`, parses `csim_design`/`csynth_design` log markers plus csynth reports, and copies stable logs/reports for documentation. Local verification passed `cargo fmt --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked`, `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/test-run-vitis-validation-manual`, `git diff --check`, and the generated-C++ leakage scan. EC2 replay on `[ec2-host — see private/ec2-lane.md]` completed all eight adapters with return code 0, `csim=true`, `csynth=true`, and parsed Fmax estimates; evidence is captured under `docs/vitis-validation/2026-06-27-runner/`. During EC2 replay, the system Rust/Cargo was 1.75.0 with no `rustup`, so the copied remote bundle used a remote-only Cargo.lock v4-to-v3 downgrade; no local lockfile change was made. Also fixed parser tolerance for old `stringify!` spacing of assignment as `: =`.
- Completed the first vendor Vitis validation pass for the Rust rewrite in `/Users/david/Documents/David_code/spatial-rs` using EC2 `[ec2-host — see private/ec2-lane.md]` with Ubuntu 22.04.5, Vitis/Vivado 2025.1, part `xc7z020-clg400-1`, and 10 ns clock. Added a locked `emit-vitis-dry-run` CLI that emits relocatable bundles for all eight current accepted adapters, reproduced `cargo test --locked`, `cargo run -p ee109-examples --locked --bin ee109-examples`, and `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run` on EC2 with Rust 1.96.0, then ran sidecar Vitis Tcl for all bundles. All eight completed `csim_design` and `csynth_design` with return code 0: `Lab1Part1RegExample`, `Lab1Part1RegThreeInputExample`, `Lab1Part2DramSramExample`, `Lab2Part3BasicCondFSM`, `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`, `Lab3Part0MatrixCopyRowMajor`, and `Lab3Part1Convolution`. Repo evidence is captured under `docs/vitis-validation/2026-06-27/` with `summary-both.json`, per-kernel Vitis logs, and csynth reports. Boundary: exact adapter Vitis `csim`/`csynth` is now validated; board execution, Vivado implementation/place-and-route, post-implementation timing closure, and generic Spatial feature support remain pending.
- Implemented and committed the Rust frontend/HIR classifier plus Vitis dry-run artifact slice in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `8249a60`: scalar, LUT, and dense accepted adapters now route through `frontend::{token, ast, parse}` to typed HIR and a first-class classifier while preserving exact HLS output; fail-closed guards now reject DRAM-shaped scalar/LUT ports, extra ignored ports, dense top-level memory drift, duplicate/extra constants, non-canonical ordinals, ragged LUTs, and unsupported tokens in comments; public manifests no longer expose a premature `supported_feature` status. The HLS crate can emit relocatable `vitis_project_dry_run` bundles with `kernel.cpp`, `harness.cpp`, `manifest.json`, `run_hls.tcl`, and `vitis-project.json`, with part/clock validation and vendor commands commented out. Fresh verification passed: `cargo fmt --check`, `cargo test --locked` (58 core tests + 17 HLS integration tests + 1 example test), `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked` with all eight examples printed as `accepted_fixture_adapter`, `git diff --check`, generated-output leakage scan with no Scala/Chisel/simulator/legacy backend matches, and stale overclaiming-term scan with no matches. Six GPT-5.5 xhigh final reviewers cleared the slice after two blocking findings were fixed and re-reviewed. Boundary remains accepted fixture adapters plus host-C++/dry-run project artifacts only; no Vitis/Vivado `csim_design`, `csynth_design`, timing, RTL, or board validation yet.
- Implemented and committed the first Rust rewrite frontend foundation slice in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `020a3b7`: six GPT-5.5 xhigh reviewers agreed the next safe step was source/span diagnostics plus fail-closed guardrails rather than a full parser/HIR rewrite; added `frontend::source` with `SourceId`, `ByteSpan`, `SourceSpan`, `LineCol`, and `SourceFile`; extended diagnostics with primary source labels; attached labels to parser unsupported/generic errors; added explicit fail-closed `par` diagnostic `spatial:E0206`; and renamed the public manifest/example status vocabulary from the overbroad `supported_ee109` to `accepted_fixture_adapter`. Fresh verification passed: `cargo fmt --check`, `cargo test --locked` (36 core tests + 10 HLS integration tests + 1 example test), `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked` with all eight accepted fixture adapters printed under `accepted_fixture_adapter`, `git diff --check`, stale `supported_ee109` search with no matches, and generated-output leakage scan with no Scala/Chisel/Vitis/Vivado/legacy backend matches. Boundary remains local host-C++ and structural checks only; vendor Vitis/Vivado HLS synthesis is still pending.
- Reframed the Rust direction after six GPT-5.5 xhigh architecture reviews and manager verification: `spatial-rs` is now documented as the first tracer slice of a full Rust rewrite of Spatial targeting HLS C++, not as a lab-only detour or a non-rewrite. Added `[[2026-06-27-rust-spatial-rewrite-roadmap]]`, updated the HLS mapping overview and workflow/conventions terminology, and added Lab3 architecture-debt guardrails. Repo-local docs now distinguish `accepted fixture adapter`, `supported feature`, `host_cpp_structural_gate`, `vitis_csim_validated`, and `vitis_csynth_validated`; current positives remain host-C++ fixture adapters until they graduate through reusable frontend/HIR/IR/lowering modules and vendor HLS evidence.
- Closed and committed the final Rust EE109 MVP audit-gap pass in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `86ce019`: scalar checked IR now requires canonical `argRegIn0`, `argRegIn1`, optional `argRegIn2`, and `argRegOut` names; scalar manifest inputs/outputs now sort by ordinal to match validation and HLS emission; local out-of-scope EE109 fixture sketches for FIFO, Fold/Reduce, MemReduce, MemFold, FSMAlt, and GEMM fail closed with stable diagnostics; and repo-local docs now include `docs/ee109-mvp-plan.md`, `docs/ee109-fixture-matrix.md`, and `docs/2026-06-27-final-audit.md`. Fresh verification passed after the final docs update: `cargo fmt --check`, `cargo test --locked` (32 core tests + 10 HLS integration tests), `cargo clippy --all-targets --locked -- -D warnings`, `cargo run -p ee109-examples --locked` with all eight accepted fixture adapters printed under the historical manifest label `supported_ee109`, `git diff --check`, and generated-output leakage scan with no Scala/Chisel/Vitis/Vivado/legacy backend matches. Six GPT-5.5 xhigh focused re-reviewers returned GO for scalar fail-closed validation, ABI/manifest ordering, fixture matrix coverage, documentation sufficiency, host-C++ gate hygiene, and final integration risk. Boundary remains local host-C++ only, with vendor Vitis/Vivado HLS synthesis still pending.
- Implemented and committed the Rust `Lab3Part1Convolution` direct semantic slice in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `0890782`: exact canonical parser island for the EE109 Lab3 convolution source despite internal `LineBuffer`, `RegFile`, nested `reduce`, `mux`, and `abs` tokens; opaque `ProgramKind::Lab3Part1Convolution` plus `Stmt::Lab3Part1Convolution`; fixed rank-2 `img: Dram<Int>[16,16]` input and `imgOut: Dram<Int>[16,16]` output; manifest records for `img`/`imgOut`, Sobel LUTs `kh`/`kv`, and `lineOut[16]`; direct HLS-style C++ with causal 3x3 row-major Sobel window, `COLS` stride, top/left border zeroing, integer abs, and full 16x16 host-C++ harness comparison against an independent Rust oracle. Generic/noncanonical `reduce`, `LineBuffer`, `RegFile`, and rank-2 DRAM remain fail-closed outside the exact accepted forms. Verification passed: RED `cargo test lab3` failed before implementation on missing Lab3 support, then `cargo test lab3`, `cargo test` (29 core tests + 10 HLS integration tests), `cargo clippy --all-targets -- -D warnings`, `cargo run -p ee109-examples` with eight accepted fixture adapters printed under the historical manifest label `supported_ee109`, `git diff --check`, direct generated `Lab3Part1Convolution` harness run, and generated C++ hygiene scan with no simulator/Chisel/VCS leakage matches. Six GPT-5.5 xhigh scouts converged on this opaque direct semantic slice, GPT-5.5 xhigh spec review found no blocking issues, and GPT-5.5 xhigh code-quality review found only a non-blocking generated-harness readability note. Boundary remains local host-C++ only, not Vitis/Vivado synthesis. Broad documentation-site work remains postponed; slice contract is recorded in `[[2026-06-27-rust-lab3-convolution-slice-contract]]`.
- Implemented and committed the Rust `Lab3Part0MatrixCopyRowMajor` groundwork slice in `/Users/david/Documents/David_code/spatial-rs` on branch `David/rust-ee109-mvp` at commit `1e9781e`: exact canonical parser support for a fixed non-square rank-2 DRAM copy, `ProgramKind::Dram2dRowMajorCopy`, `src: Dram<Int>[3,5]` input, `dst: Dram<Int>[3,5]` output, deterministic manifest rank-2 ABI with `src` on `gmem0` and `dst` on `gmem1`, row-major HLS-style C++ flattening with `(r * 5) + c`, independent Rust oracle and wrong-row-stride canary, host-C++ harness compile/run inclusion, and example-runner coverage. Generic/noncanonical rank-2 DRAM remains fail-closed, and `RegFile`/`LineBuffer` remain rejected pending the real Lab3 feature slice. Verification passed: `cargo test` (25 core tests + 9 HLS integration tests), `cargo clippy --all-targets -- -D warnings`, `cargo run -p ee109-examples`, `git diff --check`, and generated C++ hygiene scan with no simulator/Chisel/VCS leakage matches. GPT-5.5 xhigh spec review found a manifest bundle edge case for reversed raw DRAM port order; a failing regression was added, the role/ordinal manifest ordering fix was applied, focused re-review found no remaining spec findings, and GPT-5.5 xhigh code-quality review found no issues. Boundary remains local host-C++ only, not Vitis/Vivado synthesis. Next slice should move from rank-2 DRAM layout groundwork toward the first real Lab3 local-window feature.
- Implemented and committed the Rust `Lab2Part3BasicCondFSM` slice in `/Users/david/Documents/David_code/spatial-rs` at commit `ed24668`: exact canonical parser support for the EE109 FSM lab, `ProgramKind::Lab2BasicCondFsm`, one output `dram: Dram<Int>[32]`, local `bram: Sram<Int>[32]`, independent 32-element oracle matching the EE109 gold vector, manifest records for one output DRAM plus one local SRAM, HLS-style C++ state loop with nested conditionals and final dense store, and host-C++ harness compile/run inclusion. Generic and malformed FSM remains fail-closed. Verification passed: `cargo test` (22 core tests + 8 HLS integration tests), `cargo clippy --all-targets -- -D warnings`, `cargo run -p ee109-examples`, `git diff --check`, generated C++ hygiene scan with no simulator/Chisel/VCS leakage matches, and three GPT-5.5 xhigh read-only reviews with only test/wording tightenings applied. Boundary remains local host-C++ only, not Vitis/Vivado synthesis. Next slice is fixed non-square 2-D DRAM row-major copy for Lab3 groundwork.
- Hardened and committed the Rust EE109 M1 program construction API in `/Users/david/Documents/David_code/spatial-rs` at commit `cdd19d5`: `Program`, `Port`, and `Memory` now expose read-only accessors instead of public fields; `ProgramKind` classifies supported M1 shapes; checked construction rejects unsafe/C++ keyword identifiers, duplicate port/memory names, duplicate ordinals, malformed shapes, mismatched LUT payload sizes, mismatched kind/shape, mismatched canonical kernel name/shape, and extra/noncanonical IR before HLS emission. HLS integration tests now use public `parse_accel`/checked constructors instead of mutating raw IR. Verification passed: `cargo test` (20 core tests + 7 HLS integration tests), `cargo clippy --all-targets -- -D warnings`, `cargo run -p ee109-examples`, `git diff --check`, and generated C++ hygiene scan with no simulator/Chisel/VCS leakage matches. GPT-5.5 xhigh reviewers found the original kind/name/identifier gaps; focused re-review found no remaining blocking issue. Boundary remains local host-C++ only, not Vitis/Vivado synthesis. Next implementation slice remains `Lab2Part3BasicCondFSM`, followed by fixed non-square 2-D DRAM row-major copy for Lab3 groundwork.

---

## 2026-06-26 — Rust-first Spatial DSL framing

- Chose the post-M1 next action in `[[2026-06-26-rust-post-m1-next-slice]]` after three GPT-5.5 xhigh subagent recommendations. Decision: harden Rust `Program`/parser API first, then implement the next lab feature. Feature candidates remain `Lab2Part3BasicCondFSM` for real EE109 control-flow breadth and fixed non-square 2-D DRAM row-major copy for Lab3 groundwork; manager preference after hardening is Lab2 FSM, followed by Lab3 2-D DRAM.
- Implemented and committed the Rust EE109 M1 teaching tracer slice in `/Users/david/Documents/David_code/spatial-rs` at commit `75131f9`: Cargo workspace with `spatial-rs-core`, `spatial-rs-hls`, and `ee109-examples`; supports five M1 positives (`Lab1Part1RegExample`, `Lab1Part1RegThreeInputExample`, `Lab1Part2DramSramExample`, `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`) through `accel!`, manifest-first validation, independent Rust oracles, HLS-style C++ kernel/harness emission, and local `c++` compile/run. Verification passed: `cargo test` (14 core tests + 7 HLS integration tests), `cargo run -p ee109-examples`, `cargo clippy --all-targets -- -D warnings`, and generated C++ hygiene scan with no `FringeContext`/`TopHost`/`Chisel`/`Verilog`/`DRAMSim`/`vcs`/`instrument` matches. Three GPT-5.5 xhigh reviewers approved after fixes for manifest-first ordering, parser false accepts, and public IR validation holes. Boundary remains local host-C++ only, not Vitis/Vivado synthesis.
- Ran three GPT-5.5 xhigh read-only reviewers on the Rust M1 design/plan. All approved the direction but returned no-go-as-written on loose gates: overclaimed approval status, unresolved overlay decisions, missing manifest JSON tests, incomplete `accel!` coverage, oracle self-reference risk, broad hygiene scans, and post-M1 scope blur. Patched `[[2026-06-26-rust-ee109-mvp-design]]`, `[[2026-06-26-rust-ee109-mvp-implementation-plan]]`, and the overlay accordingly before implementation.
- Closed the Rust EE109 MVP implementation boundary in `[[2026-06-26-rust-ee109-mvp-design]]` and activated `[[2026-06-26-rust-ee109-mvp-implementation-plan]]`: create `/Users/david/Documents/David_code/spatial-rs` as a Rust Cargo workspace with core and HLS crates, expose a thin `accel!` DSL path for M1, keep Scala reference-only, require manifest-first validation, independent oracles, fail-closed diagnostics, and local host-C++ gates before claiming support.
- Completed a six-agent research wave on the Rust-first rewrite framing and recorded the approved synthesis in `[[2026-06-26-rust-first-spatial-dsl-overlay]]`: Rust should own the compiler core, typed IR, ABI manifest, diagnostics, and C++ HLS emitter; the student surface should remain a constrained Spatial-like DSL, with M1 scoped to scalar add, fixed dense DRAM/SRAM, LUT, local host-C++ harnesses, and explicit fail-closed diagnostics for FSM/FIFO/Reduce/RegFile/Lab3.

## 2026-06-25 — Citation cleanup after adversarial review

- Stabilized the selected EE109 local HLS lane in `[[84 - EE109 HLS Stability Matrix]]`: five positive examples now pass local host-C++ HLS generation and Scala parity (`Lab1Part1RegExample`, `Lab1Part1RegThreeInputExample`, `Lab1Part2DramSramExample`, `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`), while FSM, FIFO, Reduce/Fold, and RegFile-like Lab3 surfaces fail closed with `[hlsgen]` diagnostics. Vendor Vitis/Vivado HLS synthesis remains explicitly pending.
- Added `spatial.tests.ee109.Lab2Part4LUTNonSquareExample` as a stronger row-major LUT regression. It uses a `2x4` LUT with runtime args `10 1 2`; focused HLS output host-compiled and ran with `PASS: 17`, and the generated kernel indexes `lut[((i) * 4) + j]`, confirming the non-square stride is represented in emitted C++.
- Completed the Lab1Part2 DRAM/SRAM/Foreach scout in `[[82 - Lab1Part2 DRAM SRAM Scout]]`. The course checkout test passes under packaged CS217 Spatial Scala simulation, but its generated backend logs say `"Skipping Make"`/`"Skipping Run"`, and the checkout depends on `"edu.stanford.cs.dawn" %% "spatial" % "1.1-cs217"` rather than the local HLS branch. Treat the result as IR-shape reconnaissance only; next implementation action is a local fail-closed Lab1Part2-like HLS fixture plus narrow dense DRAM/SRAM lowering.
- Completed Wave 4 Lab2Part4LUT HLS support. Added conservative constant integer LUT lowering for `LUTNew` plus vector-width-one `LUTBankedRead`/`VecApply(..., 0)`, using row-major flat array indexing in the generated kernel and harness. Promoted `spatial.tests.ee109.Lab2Part4LUT` to a passing HLS target and replaced the stale LUT negative fixture with `spatial.tests.compiler.HLSRejectsUnsupportedFSM`, which verifies unsupported controllers still fail with explicit `[hlsgen]` diagnostics.
- Recorded HLS verification limitation: the current `--hls` backend test is a local host-C++ sanity gate only. It emits HLS-style C++ pragmas, compiles with the system `c++` using `-Wno-unknown-pragmas`, and runs a generated harness; it does not run Vitis/Vivado HLS, does not synthesize RTL, and does not validate that vendor HLS accepts the generated kernel.
- Completed Wave 3 HLS hardening and Stage 1 planning. Added a three-input EE109 scalar-add HLS regression, an HLS-specific expected-error regression lane, dynamic argv parsing in the generated C++ harness, expression-based scalar checking, unique HLS symbol names, `--sim` clearing `enableHLS`, and `[[80 - Stage1 EE109 HLS Expansion Plan]]`. Focused HLS verification passed for the two-input tracer, three-input tracer, and initial expected-error gate.
- Completed Wave 2 Lab1Part1 Stage 0 HLS tracer implementation. Six subagents produced focused notes on Stage 0 IR extraction, backend hook placement, emitter design, harness/build flow, test strategy, and risk review. Added a narrow `--hls` backend lane in Spatial, a standalone `spatial.codegen.hlsgen.HLSGen`, and `spatial.tests.ee109.Lab1Part1RegExample`; verified the generated HLS C++ harness compiles and prints `PASS: 8`, while unsupported non-Stage0 examples fail with explicit `[hlsgen]` diagnostics.
- Completed Wave 1 of the EE109 HLS MVP planning pass with six GPT-5.5 xhigh subagents; created `[[04-ee109-hls-target-corpus]]`, `[[50 - EE109 MVP Blocker Matrix]]`, `[[ee109-frontend-to-ir-path]]`, `[[55 - EE109 ABI Manifest v0]]`, `[[61 - EE109 Controller Primitive Lowering]]`, and `[[62 - EE109 Memory Partitioning Lowering]]`, then synthesized manager-owned `[[60 - EE109 HLS Lowering Map]]` and `[[70 - Lab1Part1 Tracer Bullet]]` for the next implementation cut.
- Verified the adversarial review's one-line-past-EOF citation findings with parallel Codex explorer subagents; most affected Banking, Retiming, Timing Model, and Streaming semantics entries were already corrected. Applied the 5 remaining active `10 - Spec/` fixes in `[[90 - Transformers]]` and `[[60 - Streams and Blackboxes]]`, then confirmed no stale off-by-one review ranges remain in `10 - Spec/` and `git diff --check` is clean.
- Reframed Phase 3 around an EE109-first HLS MVP instead of broad design-decision cleanup; wrote `[[2026-06-25-ee109-hls-mvp-plan]]` as the manager plan and future six-agent distribution model.

## 2026-04-21 — Phase 0 scaffold

- Brainstorming session: decisions recorded in [[2026-04-21-spatial-spec-design]].
- Approved approach: Approach B (10 parallel Opus 4.7 coverage subagents, serial deep-dives in main session).
- Scaffold written:
  - `00 - Index.md`
  - `90 - Meta/2026-04-21-spatial-spec-design.md`
  - `90 - Meta/workflow.md` — operational runbook for future sessions
  - `90 - Meta/conventions.md` — frontmatter, citation, linking rules
  - `90 - Meta/progress-log.md` — this file
  - `20 - Research Notes/20 - Open Questions.md` — empty template
  - `30 - HLS Mapping/00 - Overview.md` — categorization scheme
- Project memory added: pointer to [[workflow]] so future sessions auto-load.

**Next:** Phase 1 dispatch — 10 parallel Opus 4.7 Explore subagents per the plan in [[workflow]] §"Phase 1 — Coverage dispatch".

### Post-scaffold fixes (same day)

Codex adversarial review flagged three issues against the scaffold. Applied fixes:

1. **Added execution-harness note** to [[workflow]] — runbook now explicitly declares Claude Code as the assumed harness, disambiguating `Agent`/`TaskCreate`/`subagent_type: Explore`/`model: opus` references for readers on other harnesses.
2. **Rewrote YAML frontmatter templates** in [[workflow]] and [[conventions]] to use block-style lists with quoted string values. Root cause: bare `[[wikilink]]` inside flow sequences parses as a nested list, not a wikilink string; bare colons in flow sequences are ambiguous across parsers. Verified corrected templates parse cleanly in Python's PyYAML. Added a "YAML safety" blockquote to both files documenting the rule.
3. **Extended type schema** in [[conventions]] from 7 to 11 entries to match the file types actually shipped: added `conventions`, `log`, `open-questions`, `hls-mapping-index`. All shipped frontmatter now matches the declared schema.

## 2026-04-21 — Phase 1 pre-flight

- Vault scaffold OK: all expected folders (`20 - Research Notes`, `30 - HLS Mapping`, `90 - Meta`) + `00 - Index.md` present.
- `00 - Coverage/` **created** — was missing, now ready in `20 - Research Notes/`.
- Spatial source tree verified at `/Users/david/Documents/David_code/spatial` with all expected top-level directories.
- File count deviations: **2 bundles exceed ±15% threshold**: Bundle 2 (forge-runtime) at +40.0% (70 vs 50 expected), Bundle 10 (poly-models-dse) at +16.2% (93 vs 80 expected). All other bundles within tolerance. Recommend proceeding with dispatch — deviations likely due to submodule expansions or recent development. Monitor during deep-dive phase.
- Validator ready at `90 - Meta/scripts/validate_coverage_note.py`; passes good-stub, fails bad-stub (7 missing-section issues) as expected.
- Subagent prompt template at `90 - Meta/scripts/coverage-subagent-prompt.md`; full schema + YAML-safety rules + ground rules + no-write-outside-coverage-path invariant.

## 2026-04-21 — Phase 1 complete

- Dispatched 10 parallel Opus Explore subagents. All returned coverage-note content in chat (Explore subagents are read-only and cannot Write files, so each subagent emitted the full note markdown in its response).
- Main session wrote all 10 notes to `20 - Research Notes/00 - Coverage/` from chat returns: `argon`, `forge-runtime`, `spatial-lang`, `spatial-ir`, `spatial-passes`, `codegen-fpga-host`, `codegen-sim-alt`, `fringe`, `hardware-targets`, `poly-models-dse`. `fringe-coverage.md` was apparently written directly by its subagent (an exception).
- File counts returned by subagents: argon=95, forge-runtime=70, spatial-lang=62, spatial-ir=79, spatial-passes=78, codegen-fpga-host=38, codegen-sim-alt=76, fringe=149, hardware-targets=27, poly-models-dse=93. Total **765 Scala files** mapped.
- **Structural validation: 10/10 OK.** All notes pass the validator (frontmatter + 10 section headings in order).
- **Content spot-checks: 10/10 ACCEPT.** 8 subagents ran (Explore, sonnet); 2 rate-limited by Anthropic account usage. Main session did 3-claim manual spot-checks for the 2 rate-limited notes (codegen-sim-alt, poly-models-dse) — all 6 manual claims verified. Aggregate across the 8 subagent-run notes: 35✓ / 5✗ / 0? (minor fails: line-range imprecisions, off-by-2 counts, an inconsistent "29k" unit claim — all architectural claims supported).
- All 10 notes now carry `verified: [2026-04-21]` in frontmatter.
- 6 open questions filed (Q-001..Q-006) covering minor imprecisions flagged during spot-checks.

**Next:** Phase 2 deep dives. Per [[workflow]] §"Priority ordering": start with Argon framework → Spatial IR nodes + metadata → Pass pipeline → Language surface → Semantics → scalagen → chiselgen → other backends → poly/models/DSE/fringe/targets → testing/debugging/build. Each deep dive produces one or more spec entries under `10 - Spec/` with its source-cited algorithmic detail.

## 2026-04-23 — Phase 2 launch (unattended overnight)

Cleanup:
- Fixed Q-001..Q-005 in coverage notes (line ranges, counts, wording). All five marked resolved-2026-04-23 in 20 - Open Questions.md.

Scaffold:
- `10 - Spec/` top-level tree created with 9 sub-folders and an index MOC per folder: Language Surface / Semantics / IR (Argon Framework, Spatial Nodes, Metadata) / Compiler Passes / Code Generation (Chiselgen/Scalagen/Cppgen/Pirgen) / Polyhedral Model / Models and DSE / Runtime and Fringe.
- `20 - Research Notes/10 - Deep Dives/` created.

Round 1 dispatch (4 parallel general-purpose subagents, background):
- Argon framework (6 spec entries: Symbols+Types, Ops+Blocks, Effects+Aliasing, Staging Pipeline, Scopes+Scheduling, Transformers) + argon-framework deep-dive note.
- Spatial IR nodes (6 spec entries: Controllers, Memories, Memory Accesses, Counters, Primitives, Streams+Blackboxes) + spatial-ir-nodes deep-dive note.
- Pass pipeline (canonical-order cross-ref + 5 spec entries: Pipeline Order, Flows+Rewrites, Pipe Insertion, Unrolling, Banking) + pass-pipeline deep-dive note.
- Language surface (5 spec entries: Controllers, Memories, Primitives+Streams, Math+Helpers, Aliases+Shadowing) + language-surface deep-dive note.

Round 2 dispatch (5 parallel general-purpose subagents, background):
- Scalagen (6 spec entries under `10 - Spec/50 - Code Generation/20 - Scalagen/`): Overview, Numeric Reference Semantics, Memory Simulator, FIFO/LIFO/Stream Simulation, Controller Emission, Counters+Primitives.
- Chiselgen (6 spec entries under `10 - Spec/50 - Code Generation/10 - Chiselgen/`): Overview, Types+Ports, Memory Emission, Controller Emission, Streams+DRAM, Math+Primitives.
- Other codegens (5 spec entries): Cppgen, Pirgen, Other Codegens (rogue/tsth/dot/tree), Per-Target Files, Naming+Resource Reports.
- Poly+Models+DSE (6 spec entries): ISL Binding, Access Algebra, Banking Math, Area Model, Latency Model, DSE.
- Fringe+Targets (6 spec entries): Architecture, DRAM Arbiter+AXI, Ledger+Kernel, Hardware Templates, BigIP+Arithmetic, Target Hardware Specs.

Round 2 subagents write new open-questions to per-topic files (`20 - Research Notes/10 - Deep Dives/open-questions-<topic>.md`) — consolidation into main file is a later task.

Cross-reference scaffolding (done this session):
- `40 - Cross References/node-to-codegen-matrix.md` — per-IR-node × per-backend emission matrix (draft).
- `40 - Cross References/pass-pipeline-order.md` — placeholder; pass-pipeline subagent writes the full enumeration.
- `40 - Cross References/source-tree-map.md` — extended with Phase 2 priority mapping + deep-dive file roster.

Spec-tree MOCs scaffolded:
- Top-level: `10 - Spec/00 - Spec Index.md`.
- Per-section: Language Surface, Semantics, IR (+Argon, +Nodes, +Metadata), Compiler Passes, Code Generation, Polyhedral Model, Models+DSE, Runtime+Fringe — each with its own index and reading order.

## 2026-04-24 — Phase 2 mass dispatch resumed after usage-limit interruption

Pre-resumption state: Round 1 Claude agents had written 14 of 22 promised spec entries before hitting overnight usage limit. Round 2 Claude agents had written deep-dive notes for all 5 topics + 2 spec entries (Scalagen Overview, Chiselgen Overview); the remaining 24 spec entries were pending.

Round 3 Claude (focused completion, ran in foreground while user away):
- Argon: ✓ all 6 core entries verified done (Symbols+Types, Ops+Blocks, Effects+Aliasing, Staging Pipeline, Scopes+Scheduling, Transformers).
- Spatial IR remaining 3: ✓ Counters, Primitives, Streams+Blackboxes (avg ~2600 words; 27-51 citations).
- Pass pipeline remaining 2 + cross-ref: ✓ Banking (2512w/30c), Retiming (2327w/27c), pass-pipeline-order.md (89-entry full enumeration).
- Lang surface remaining 2: ✓ Math+Helpers (1351w/86c), Aliases+Shadowing (1381w/58c).
- Scalagen, Chiselgen Round 3 Claude completions still in flight at user-resumption.

User instruction at session resumption: "Use codex rescue for sub agents throughout, make sure using gpt 5.5 xhigh. Unlimited budget — ask aggressively (codex only)." From this point forward all subagent dispatches use `codex:codex-rescue` with `--model gpt-5.5-codex --effort xhigh --write`. **Note**: `gpt-5.5-codex` is not available on the user's ChatGPT account; Codex falls back to its default model. xhigh effort still applies. Output quality remains high (43-61 citations per spec entry observed).

Codex Round 4 (3 dispatches, parallel background):
- Other codegens 5 entries (Cppgen, Pirgen, Other Codegens, Per-Target Files, Naming+Resource Reports).
- Poly+Models+DSE 6 entries (ISL Binding, Access Algebra, Banking Math, Area Model, Latency Model, DSE).
- Fringe+Targets 6 entries (Architecture, DRAM Arbiter+AXI, Ledger+Kernel, Hardware Templates, BigIP+Arithmetic, Target Hardware Specs).

Codex Round 5 (3 dispatches):
- Metadata Big 4 (Control, Access, Memory, Retiming).
- Metadata Small 8 (Bounds, Math, Params, Types, Blackbox, Debug, Rewrites, Transform).
- Argon supplemental (40 - Metadata Model, 70 - Rewrites and Flows, B0 - Compiler Driver, C0 - Macro Annotations).

Codex Round 6 (3 dispatches):
- Argon wave 2 (80 - Passes, A0 - Codegen Skeleton, D0 - DSL Base Types).
- Pass entries Set A (Friendly+Sanity, Switch+Conditional, Blackbox Lowering, Use+Access Analysis).
- Pass entries Set B (Rewrite Transformer, Flattening+Binding, Accum Specialization, Streamify, Cleanup).

Codex Round 7 (2 dispatches):
- Lang Surface remaining 5 (Streams+Blackboxes DSL, Host+IO, Debugging+Checking, Virtualization, Macros).
- Models/DSE/Fringe gaps (50 - Memory Resources, 60 - CSV Model Format, 80/60 - Instantiation).

Per-topic open-questions files: each Codex dispatch writes new Q-NNN entries to `20 - Research Notes/10 - Deep Dives/open-questions-<topic>.md` to avoid concurrent-write collisions on the main `20 - Open Questions.md`. Main session consolidates after dispatches complete.

**Pending after current batch**: Semantics synthesis (9 entries, depends on lower-level complete); adversarial review of completed entries; Q-NN consolidation; final progress-log update with totals.

## 2026-04-25 — Mid-cycle status checkpoint

Spec entries complete and verified on disk (excluding indexes):
- Argon Framework: 13/13 ✓
- Spatial Nodes: 6/6 ✓
- Metadata: 12/12 ✓
- Compiler Passes: 14/14 ✓
- Language Surface: 10/10 ✓
- Code Generation: 17/17 ✓ (Chiselgen 6, Scalagen 7, Cppgen 2, Pirgen 1, Other 1)
- Polyhedral Model: 3/3 ✓
- Models and DSE: 5/6 (missing: 30 - Target Hardware Specs, in flight via Codex 3 Fringe+Targets)
- Runtime and Fringe: 1/6 (only 60 - Instantiation; 10/20/30/40/50 in flight via Codex 3)

**Total spec entries: 81/87 complete (93%)** plus 14 indexes = 95 markdown files in `10 - Spec/`.

Open-questions files (10 per-topic, 1497 lines total — to be consolidated into `20 - Open Questions.md` post-cycle):
- argon-supplemental: 42 lines
- chiselgen: 237 lines (Q-cgs-01..15)
- lang-surface: 230 lines (Q-lang-01..06+)
- metadata: 164 lines (Q-meta-01..21)
- models-dse-fringe-gaps: 62 lines
- other-codegens: 80 lines
- pass-pipeline: 181 lines (Q-pp-01..06+ plus pass A/B additions)
- poly-models-dse: 89 lines (Q-pmd-01..09)
- scalagen: 314 lines (Q-scal-01..18)
- spatial-ir: 98 lines (Q-irn-01..10)

Round 8 dispatch (Codex):
- Semantics synthesis (9 entries, dispatched 2026-04-25 after lower-level mostly complete; reads all argon/IR/passes/lang/scalagen entries and consolidates)

**Pending Codex jobs as of mid-cycle (7 still running, mostly in verification loops with files already on disk)**:
- Codex 3 Fringe+Targets — only one with files NOT yet on disk (6 entries pending)
- All others: rescue agents reported back; the Codex jobs may continue in detached-background mode

Critical findings (surfaced by Round 3 Claude agents):
- **Scalagen FixFMA emitted as unfused** multiply-then-add — diverges from Chisel hardware-FMA precision. Calls into question scalagen's "reference semantics" status for FMA-using programs. Filed Q-scal-NN.
- **OneHotMux uses bitwise OR** — semantically broken if multiple lanes true; fails to compile for floats.
- **FIFO/LIFO elastic** in scalagen (no back-pressure modeling) — diverges from Chisel.
- **FixedPoint.unbiased uses Random.nextFloat** — nondeterministic rounding.
- **RemapSignal (29 objects)** never used in chiselgen — dead-code candidate.
- **9 of 23 AppProperties** flags never registered — speculative or external readers.
- **MemoryAllocator has TODO "un-gut memory allocator"** at line 16 — half-finished pass.
- **MemoryConfigurer.requireConcurrentPortAccess** is 7 disjuncts (not 5 as deep-dive originally said).
- **`gpt-5.5-codex` not available** on user's account; default Codex model used with --effort xhigh.

## 2026-04-25 — Overnight completion and Phase 3 kickoff

Priority 1 complete:
- Wrote the 6 missing Fringe/Targets spec entries: Runtime and Fringe 10/20/30/40/50 plus Models and DSE 30 Target Hardware Specs.
- Added `20 - Research Notes/10 - Deep Dives/open-questions-fringe-targets.md` with Q-ft-01..Q-ft-12.
- Updated the Runtime and Fringe index to point at the final six entry names.

Priority 2 complete:
- Consolidated all per-topic open-question files into `20 - Research Notes/20 - Open Questions.md`.
- Final open-question count: 164 total questions, Q-001..Q-164, with 158 Phase 2 questions renumbered into the global sequence and cross-referenced to their original per-topic IDs.
- Per-topic files were left in place rather than archived so existing wikilinks remain valid.

Priority 3 complete:
- Wrote `20 - Research Notes/30 - Adversarial Review.md`.
- Reviewed 26 representative entries: all 13 Argon Framework entries, Banking, Retiming, Scalagen Numeric Reference Semantics, Scalagen Memory Simulator, and all 9 Semantics entries.
- Checked 303 `source_files` citations: 286 correct, 17 incorrect. All 17 were one-line-past-EOF range errors; no missing files were found. Corrections are listed but not auto-applied.

Priority 4 complete:
- Populated HLS mapping indexes from spec frontmatter.
- HLS classification tally: 96 entries total — 23 clean, 58 needs rework, 15 Chisel-specific.
- Added `30 - HLS Mapping/40 - Open HLS Questions.md` with the top 10 Phase 3 architecture questions.
- The only `unknown` entry, `[[70 - Naming and Resource Reports]]`, was suggested as needs-rework in the mapping index without changing its source frontmatter.

Final tally:
- `10 - Spec/`: 108 markdown files total, including 96 `type: spec` entries and 12 MOC/index files.
- Citation inventory: 933 frontmatter `source_files` references; 4,582 explicit Scala file:line mentions across spec entries.
- Open questions consolidated: 164 total; 158 Phase 2 questions appended and globally renumbered.
- HLS classifications: 96 total.

Phase status:
- Phase 0 ✓
- Phase 1 ✓
- Phase 2 ✓ substantially complete; adversarial review found citation corrections for human review
- Phase 3 kicked off ✓

Stopping point at handoff:
- All required Priority 1 through Priority 5 artifacts are on disk.
- Morning summary written to `90 - Meta/morning-summary-2026-04-25.md`.

Remaining work for next session:
- Apply or reject the 17 citation-range corrections listed in `[[30 - Adversarial Review]]`.
- Resolve top Phase 3 HLS questions, starting with FMA fused/unfused semantics, unbiased rounding determinism, FIFO/LIFO back-pressure, and host ABI replacement.
- Decide whether to archive per-topic open-question files after updating any links that still target them.

## 2026-06-28 — Rust rewrite Lab3 HLS stencil-plan foundation

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on `David/rust-ee109-mvp`.

Completed a narrow Lab3 backend foundation slice:
- Added `docs/superpowers/plans/2026-06-28-lab3-stencil-foundation.md`.
- Kept `Lab3Part1Convolution` as a fixed EE109 fixture adapter, not a generic stencil feature.
- Added crate-private `Stencil2dSobel` HLS body planning for Lab3: DRAM ports, dimensions, `lineOut`, `kh`/`kv` LUT names and values, and row-major index facts.
- Routed Lab3 HLS emission through the new plan while preserving the existing emitted C++ byte-for-byte.
- Added plan extraction, row-major canary, stable kernel snapshot, and full 256-pixel host harness/oracle tests.
- Updated Rust repo docs to call Lab3 a fixed stencil-plan fixture adapter and to keep generic `LineBuffer`, `RegFile`, `Reduce`, `par`, `mux`, and `abs` support fail-closed.

Local verification passed:
- `cargo fmt --check`
- `cargo test --locked`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-lab3-stencil-foundation`
- `git diff --check`
- generated C++ leakage scan for legacy Scala/Chisel/backend terms returned no matches.

Subagent review:
- Spec review: compliant, no gaps or overclaims.
- Code-quality review: approved. One P3 note remains: current Lab3 row-major expressions are validated as plan canaries while the byte-preserving renderer still emits symbolic `COLS`/`KW` expressions. Next slice should either rename them explicitly as canaries or add byte-preserving symbolic render expressions and consume those directly.

Recommended next slice:
- Replace the remaining Lab3 compact-source parser island with a narrow frontend/HIR/classifier route for the canonical Lab3 convolution.
- Do not promote generic `LineBuffer`, `RegFile`, `Reduce`, `par`, `mux`, or `abs` support until non-lab representatives and fresh HLS evidence exist.

## 2026-06-28 — Rust rewrite Stencil2d v0 local and Vitis evidence

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on `David/rust-ee109-mvp`.

Committed local checkpoint:
- Commit `2ec05e6` — `Promote narrow Stencil2d v0 locally`.
- Added `ProgramKind::Stencil2d` and checked semantic `Stmt::Stencil2d` payloads.
- Kept `Lab3Part1Convolution` as an accepted fixture adapter, but routed its body through the shared Stencil2d payload and HLS lowering path.
- Added non-lab representative `SobelStencil12x20` to the validation lane, bringing the Rust validation set to fourteen programs.
- Preserved fail-closed behavior for generic `LineBuffer`, `RegFile`, arbitrary reductions, arbitrary `par`, non-3x3 kernels, alternate coefficients, dynamic dimensions, and unsupported border policies.
- Documented the checked-IR boundary: source classification proves `LineBuffer`/`RegFile` shape before constructing the semantic stencil node, while checked IR v0 does not independently preserve frontend-only local-window memory declarations.

Local verification passed before vendor HLS:
- `cargo fmt --check`
- `cargo test --locked`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-stencil2d-v0-plan`
- `git diff --check`
- generated-artifact leakage scan for Scala/Chisel/FIRRTL/backend terms returned no matches.

Subagent review:
- HLS/code-quality review approved with no blocking findings.
- Spec/fail-closed review approved. Follow-up fixes applied: non-lab Stencil2d no longer requires source accumulator locals named exactly `horz`/`vert`; docs now explicitly describe the source-classifier vs checked-IR memory-provenance boundary; checked-IR tests pin tiny rank-2 copy acceptance and too-small stencil rejection.

EC2 Vitis evidence:
- Host: `[ec2-host — see private/ec2-lane.md]`
- Vitis/Vivado: 2025.1
- Target: `xc7z020-clg400-1`
- Clock target: 10 ns
- Remote run directory: `/home/ubuntu/spatial-rs-runs/stencil2d-v0-20260628-0648-2ec05e6/spatial-rs`
- Command: `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-stencil2d-v0-20260628-2ec05e6`
- Result: all fourteen validation programs completed with return code 0, `csim=true`, and `csynth=true`; `SobelStencil12x20` reported estimated Fmax 136.99 MHz.
- Durable repo evidence: `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-stencil2d-v0/`
- Remote-only compatibility note: EC2 Cargo is 1.75, so the remote copy used a Cargo.lock v4-to-v3 downgrade inside the run directory only. The local Rust repo lockfile was not changed.

Non-claims:
- This is Vitis C simulation and HLS synthesis evidence only.
- It does not prove board execution, Vivado implementation, place-and-route, post-implementation timing closure, generic stencil lowering, arbitrary `LineBuffer`/`RegFile`, arbitrary reductions, or optimized line-buffer scheduling.

Recommended next slice:
- Start the frontend/HIR foundation: factor shared loops, memory/effect shapes, scalar expressions, control, diagnostics, and source provenance out of the current feature-specific recognizers before expanding toward FIFO, reductions, generic FSM variants, or broader Spatial stencil support.

## 2026-06-28 — Rust rewrite frontend/HIR foundation seam

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on `David/rust-ee109-mvp`.

Committed local checkpoint:
- Commit `c6469ac` — `Add frontend HIR foundation seam`.
- Added crate-private `hir::query` helpers for exact-one `usize` constants,
  source-order const values, integer ports, scalar integer ports, memory lookup,
  and simple read/int expression predicates.
- Reworked top-level classifier dispatch through explicit local
  `ClassifierOutcome` values: accepted program, targeted near miss, or no-match
  fallthrough.
- Preserved existing diagnostic priority: scalar adapter `E0401` still wins
  early; scalar expression near misses still outrank later classifiers; LUT
  only promotes `E0402` as a targeted near miss.
- Added HIR regression coverage for Lab3 local-window/stencil lowering shape,
  query helper duplicate-const behavior, memory lookup, and expression
  predicates.
- Updated Rust docs and corrected the frontend/HIR foundation plan snippet so
  it matches the actual scalar-adapter near-miss behavior.

Subagent review:
- Spec/fail-closed review found no P0/P1 issues. It flagged the exact-one
  const helper invariant and plan-doc drift; both were fixed before commit.
- Code-quality review found no P0/P1 issues. It flagged broad query helper
  names, direct expression-helper coverage, and the untracked query module; all
  were fixed before commit.

Local verification passed after review fixes:
- `cargo fmt --check`
- `cargo test --locked`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --out target/vitis-validation-frontend-hir-foundation`
- `git diff --check`
- generated-artifact leakage scan for Scala/Chisel/FIRRTL/backend terms
  returned no matches.

Non-claims:
- This slice does not add a new Spatial syntax feature, supported-feature
  representative, or generated HLS C++ surface.
- It does not add new EC2/Vitis evidence; the Stencil2d v0 fourteen-program
  Vitis run remains the latest vendor-HLS evidence.
- `ClassifierOutcome` is transitional while individual classifiers still return
  diagnostics; future classifier splits should return outcome-like values
  directly instead of using diagnostic strings as no-match control flow.

Recommended next slice:
- Use this foundation to split classifier concerns into smaller modules or add
  the next EE109 feature gap with the new query helpers, keeping HLS emission
  anchored on checked `Program` values and preserving fail-closed behavior.

## 2026-06-28 — Rust rewrite post-ScalarFold classifier cleanup

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Local checkpoint verified:
- Rust commit `ed1e970` — `Add post-ScalarFold classifier guardrails`.
- Added guardrails for malformed ScalarReduce syntax, malformed ScalarFold
  syntax variants, generic fold/reduce/memreduce/memfold fail-closed behavior,
  fold/reduce lexer/parser shapes, ScalarReduce reserved HLS temporary-name
  collisions, ScalarFold manifest metadata, scalar-reduce oracle bounds, and
  completeness of the latest sixteen-kernel ScalarFold Vitis evidence summary.
- Verified the two behavior-changing guardrails against the old behavior:
  malformed ScalarReduce syntax failed with `spatial:E0202` before the parser
  fix and passes with `spatial:E0002` after it; ScalarReduce outputs named
  `expected`/`actual`/`test` failed with checked-IR `spatial:E0300` before the
  classifier fix and pass with targeted `spatial:E0408` after it.
- Moved only ScalarReduce/ScalarFold classification and their targeted
  diagnostics into private `classifier::reductions`, leaving
  `classifier.rs` as the public module root and leaving HLS emission untouched.
- Tightened the captured ScalarFold Vitis evidence test so the summary must
  include all sixteen `validation_programs()` kernels in order, each marked
  passed, with sidecar Tcl, Vitis log, and csynth report files present.

Subagent limitation:
- A GPT-5.5 xhigh implementation worker started Task 1 but hit the Codex usage
  limit before returning a final report. Its partial patch was reviewed in the
  main session, fixed where needed, and verified locally.

Local verification passed:
- `cargo fmt --all -- --check`
- `cargo test --locked`
- `cargo test -p spatial-rs-core --locked`
- `cargo test -p spatial-rs-hls --locked latest_scalar_fold_vitis_evidence_summary_is_complete`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked --bin ee109-examples`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-refactor-plan`
- `git diff --check`

Non-claims:
- This slice does not add a new Spatial feature, supported-feature
  representative, validation-program member, or Vitis run.
- It does not prove any new HLS behavior beyond the already captured
  ScalarFold v0 EC2 Vitis 2025.1 `csim_design`/`csynth_design` evidence.

Recommended next slice:
- Commit the Rust branch and vault note, then choose the next EE109 feature
  gap. The likely next feature decision is whether to unblock FIFO/stream
  surfaces or memory reductions first, while continuing to factor shared HIR
  facts out of the monolithic classifier.

## 2026-06-28 — Rust rewrite ResolvedHir design checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Design checkpoint prepared:
- Added `docs/superpowers/specs/2026-06-28-resolved-hir-design.md` as the next
  compiler-foundation artifact after the explicit compiler spine and HIR facts.
- The design keeps `ResolvedHir` crate-private and test-first. The first
  implementation must not call the resolver from `parse_accel`, change
  `compile_source_detailed`, change classifier dispatch, change HLS output, or
  change validation membership.
- The resolver owns semantic facts for symbols, scopes, `Int`/`Usize`/internal
  `Bool`, memory refs, register refs, loop domains, access/layout, ordered
  effects, built-in `mux`/`abs` calls, ABI/name hygiene, and direct resolver
  diagnostics.
- Diagnostics are deliberately bounded: `spatial:E0300` remains checked-IR
  validation; `ResolvedHir` reserves only `spatial:E0301` through
  `spatial:E0310`; public `parse_accel` and `compile_source_detailed`
  diagnostics must remain `E020x`/`E04xx` compatible until an explicit
  migration rebaselines tests.

Subagent review:
- GPT-5.5 xhigh architecture, diagnostics/fail-closed, and HLS-contract
  reviewers first requested changes.
- The design was revised to add resolver-local `DeclId`/`StmtId`/`ExprId`
  facts, sibling-scope reuse, non-indexed `MemReduce`/`MemFold` domains,
  `RegRef` typing, scope-based local memories, access/layout facts,
  ABI/name-hygiene facts, ordered effects, and built-in call typing.
- All three reviewers approved the second pass.

Non-claims:
- This is a design/documentation checkpoint only.
- It adds no new accepted syntax, generated HLS surface, validation-program
  member, Vitis evidence, board evidence, or public diagnostic migration.

Recommended next slice:
- Implement the first crate-private `hir::resolved` skeleton with focused unit
  tests only, then run the full behavior-preservation gate before any
  classifier migration.

## 2026-06-29 — Rust rewrite 20-program EC2 Vitis checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Vendor-HLS checkpoint completed:
- Rust commit under test: `7a16a23` — `Add rank-2 tiled int scale feature`.
- EC2 host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`), using Vitis/Vivado 2025.1 through
  `vitis-run --mode hls --tcl`.
- The current instance exposes `vitis-run`, not a standalone `vitis_hls`
  binary. This matches the repo runner and the prior smoke-check boundary.
- Synced the current Rust checkout to
  `/home/ubuntu/spatial-rs-runs/rank2-tiled-int-scale-20260629/spatial-rs`.
- Remote plan-only validation built on EC2 and emitted 20 sidecars, including
  `MatrixTileScale4x6`.
- Remote execute validation passed all 20 programs with return code 0,
  `csim=true`, and `csynth=true`.
- New durable repo evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-rank2-tiled-int-scale/`.

New feature evidence:
- `MatrixTileScale4x6` is now Vitis-proven as the first
  `Dense2dTileScalarMul v0` representative.
- Vitis log evidence: `PASS MatrixTileScale4x6`; estimated Fmax 122.68 MHz.
- Vitis report evidence: target `xc7z020-clg400-1`, 10 ns clock target,
  estimated clock 8.151 ns, latency 43 cycles.

Local repo evidence updates:
- Added README, summary, logs, reports, and sidecar Tcl files for the
  20-program checkpoint.
- Added captured-evidence parser/completeness tests for the new directory.
- Updated repo-local architecture, fixture-matrix, and MVP-plan docs.
- Updated this vault matrix:
  `30 - HLS Mapping/84 - EE109 HLS Stability Matrix.md`.

Verification run in this checkpoint:
- EC2: `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-rank2-tiled-int-scale-20260629-plan`
- EC2: `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-rank2-tiled-int-scale-20260629`
- Local: `cargo test --locked -p spatial-rs-hls rank2_tiled_int_scale`
- Local: `cargo fmt --all -- --check`
- Local: `cargo test --locked -p spatial-rs-hls --test vitis_validation`
- Local: `cargo test --locked`
- Local: `cargo clippy --all-targets --locked -- -D warnings`
- Local: `git diff --check`

Non-claims:
- This proves Vitis C simulation and HLS synthesis only for the exact
  20-program validation set.
- It does not claim board execution, Vivado implementation, place-and-route,
  timing closure, generic rank-2 tiling, GEMM, fixed-point arithmetic, tail
  tiles, or Scala source compatibility.

Recommended next slice:
- Build one fixed-shape rank-2 accumulation canary on top of
  `Dense2dTileScalarMul v0` before attempting fixed-point GEMM or tail-tile
  generalization.

## 2026-06-30 — Rust rewrite bulk rank-2 tile IO source-spelling bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend compatibility checkpoint:
- Added a parser-only source-spelling bridge for canonical GEMM rank-2 tile
  load/preload/store forms:
  `load lhs_tile <- lhs[row_base..row_base + row_limit, 0..K];`,
  `load rhs_tile <- rhs[0..K, col_base..col_base + col_limit];`,
  `load c_tile <- cin[row_base..row_base + row_limit, col_base..col_base + col_limit];`,
  and `store out[row_base..row_base + row_limit, col_base..col_base + col_limit] <- c_tile;`.
- The bridge desugars immediately to existing nested `foreach` plus
  indexed-assignment AST nodes. It adds no new AST/HIR/IR node, checked
  payload, generated HLS behavior, validation-program member, generic DMA
  model, or Vitis evidence claim.
- The existing exact `MatrixTileMemFoldFixPt4x6x5` EE109 validation example now
  exercises the bulk IO spelling together with the body-local
  `partial_tile` MemFold spelling, while preserving the same checked
  `Dense2dTileMemFold` payload.

Local proof added:
- Parser equivalence: expanded exact FixPt and Int-tail canaries equal the new
  bulk-IO source spellings after `parse_accel`.
- Fail-closed coverage: raw Scala/FixPt policy, missing C preload, wrong store
  source, swapped lhs role, nonzero K lower bound, `par`, reserved Lab2 names,
  and FIFO diagnostic priority.
- HLS/manifest equality: generated `kernel.cpp` and manifest JSON are bytewise
  identical between expanded and bulk-IO spellings for exact FixPt and Int-tail
  MemFold canaries.

Non-claims:
- This still does not accept original Scala Lab2 Part 5/6 source, raw Scala
  `::` ranges, `SRAM[T](...)`, `val`, generic Spatial `MemFold`, `par`,
  banking, K tiling, FixPt tail tiles, board execution, or new vendor-HLS
  evidence.

Recommended next slice:
- Choose whether to bridge the remaining real Lab2 body-shell spellings
  (`val partial_c = SRAM[T](...)`, tile aliases such as `tileA_sram`, and
  `.buffer`) or to introduce a new semantic slice for K tiling/Part6 `par`.

## 2026-06-30 — Rust rewrite Lab2 GEMM shell-alias/buffer parser bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend compatibility checkpoint:
- Added a parser-only bridge for exact Lab2-like GEMM shell spellings around
  the existing `Dense2dTileMemFold` FixPt canary:
  input aliases `a/b/c`, local aliases
  `tileA_sram/tileB_sram/tileC_sram`, `.buffer` only on `tileC_sram`,
  body-local `val partial_c = SRAM[T](...)`, Scala-call
  `Foreach(end by 1) { idx => ... }`, paren assignment/index reads, and loop
  aliases `ii/jj/k_idx`.
- These aliases canonicalize to `lhs/rhs/cin`,
  `lhs_tile/rhs_tile/c_tile`, `partial_tile`, and `r/c/kk` before
  HIR/classification. No new AST/HIR/IR node, checked payload, generated HLS
  behavior, validation-program member, allocation model, buffering semantics,
  or Vitis evidence claim was added.
- The exact `MatrixTileMemFoldFixPt4x6x5` validation example now exercises
  this shell spelling while preserving the existing validation list and
  generated-HLS identity.

Local proof added:
- Red/green parser equivalence test:
  `parse_accel_lab2_shell_alias_buffer_matches_expanded_fixpt_canary`.
- Fail-closed coverage for reserved `Lab2Part5GEMM`/`Lab2Part6GEMM`, Part6
  `par`, `.buffer` on the wrong tile, wrong body temp alias, and raw Scala
  `@spatial` class shell.
- HLS/manifest equality test:
  `lab2_shell_alias_buffer_preserves_exact_hls_and_manifest`.
- EE109 membership tests still show 24 validation programs and no
  `Lab2Part5GEMM`/`Lab2Part6GEMM` promotion.

Verification run in this checkpoint:
- `cargo test -p spatial-rs-core --locked lab2_shell_alias_buffer`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_shell_alias_buffer`
- `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline`
- `cargo test -p ee109-examples --locked dense2d_tile_memfold_fixpt_example_uses_spatialish_bridge_without_new_feature_kind`

Non-claims:
- This still does not accept original Scala Lab2 Part 5/6 source, raw Scala
  `::` ranges, in-place `c`, `ArgIn`/`setMem`, outer K tiling, `numel_k`
  MemFold bounds, Part6 `par`, banking, generic Spatial `MemFold`, generic
  DMA, broader fixed-point widths, FixPt tail tiles, board execution, or new
  vendor-HLS evidence.

## 2026-06-30 — Rust rewrite Lab2 GEMM infix tile IO parser bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend compatibility checkpoint:
- Added a parser-only bridge for exact Spatial-style infix rank-2 GEMM tile IO
  around the existing `Dense2dTileMemFold` payload:
  `tileA_sram load a(row_base :: row_base + row_limit, 0 :: K);`,
  `tileB_sram load b(0 :: K, col_base :: col_base + col_limit);`,
  `tileC_sram load c(row_base :: row_base + row_limit, col_base :: col_base + col_limit);`,
  and `out(row_base :: row_base + row_limit, col_base :: col_base + col_limit) store tileC_sram;`.
- The parser treats `::` as private to this infix tile IO bridge and
  immediately desugars the ranges to the same nested copy-loop AST used by the
  prefix bulk IO bridge.
- The exact `MatrixTileMemFoldFixPt4x6x5` validation example now exercises the
  infix tile IO spelling together with shell aliases/body-local `partial_c`,
  while preserving the existing checked payload and validation membership.
- Tightened the Lab2 shell-alias gate so comments or longer identifiers
  containing names like `partial_c` or `tileA_sram` do not accidentally enable
  alias canonicalization.

Local proof added so far:
- Lexer boundary test:
  `lexes_infix_range_without_breaking_assignment_colons`.
- Parser equivalence:
  `parse_accel_lab2_infix_tile_io_matches_shell_alias_fixpt_canary` and
  `parse_accel_lab2_infix_tile_io_matches_tail_bulk_canary`.
- Fail-closed coverage for reserved `Lab2Part5GEMM`/`Lab2Part6GEMM`, in-place
  `c(...) store`, Part6 `par`, wrong load target tile, nonzero K lower bound,
  and raw Scala `@spatial` class shell.
- HLS/manifest equality:
  `lab2_infix_tile_io_preserves_exact_hls_and_manifest`.
- EE109 fixture check:
  `dense2d_tile_memfold_fixpt_example_uses_spatialish_bridge_without_new_feature_kind`.

Non-claims:
- No new Vitis run is claimed for this bridge.
- This still does not accept original Scala Lab2 Part 5/6 source, raw Scala
  `@spatial` wrappers, host `ArgIn`/`setMem`, in-place `c`, outer K tiling,
  `numel_k` MemFold bounds, Part6 `par`, banking, generic Spatial `MemFold`,
  generic DMA, broader fixed-point widths, FixPt tail tiles, board execution,
  or timing-closure evidence.

## 2026-06-30 — EC2 Vitis validation for Lab2 GEMM infix tile IO checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial` at commit `1756d4d`.

Vendor-HLS evidence checkpoint:
- Ran EC2 Vitis 2025.1 on
  `[ec2-host — see private/ec2-lane.md]` using:
  `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/target/vitis-validation-infix-tile-io-20260630`.
- The command returned 0 and completed all 24 validation programs with
  `csim=true` and `csynth=true`.
- `MatrixTileMemFoldFixPt4x6x5`, whose source fixture now exercises the infix
  tile IO bridge, passed C simulation with `PASS MatrixTileMemFoldFixPt4x6x5`
  and completed `csynth_design`.
- The FixPt canary reported estimated Fmax 121.61 MHz, estimated clock
  8.223 ns, latency 84 cycles, interval 60 cycles, and utilization estimate
  6 BRAM_18K, 8 DSP, 6457 FF, and 5919 LUT.
- Compact evidence is captured in the Rust repo under
  `docs/vitis-validation/2026-06-30-infix-tile-io/` with README,
  `summary-both.{md,json}`, sidecar Tcl, Vitis logs, and csynth reports.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 24-program
  validation set at commit `1756d4d`, including the fixed-shape FixPt MemFold
  canary with parser-only infix tile IO spelling.
- This still does not accept original Scala Lab2 Part 5/6 source, raw Scala
  `@spatial` wrappers, host `ArgIn`/`setMem`, in-place `c(...) store`,
  outer K tiling, `numel_k` MemFold bounds, Part6 `par`, banking, generic
  Spatial `MemFold`, generic DMA, broader fixed-point widths, FixPt tail
  tiles, board execution, Vivado implementation/place-and-route, or
  timing-closure evidence.

## 2026-06-30 — EC2 Vitis validation for narrow in-place C MemFold canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial` at commit `79d1b67`.

Vendor-HLS evidence checkpoint:
- Ran EC2 Vitis 2025.1 on
  `[ec2-host — see private/ec2-lane.md]` using:
  `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/target/vitis-validation-inplace-c-memfold-20260630`.
- The command returned 0 and completed all 25 validation programs with
  `csim=true` and `csynth=true`.
- `MatrixTileMemFoldInPlaceFixPt4x6x5` passed C simulation with
  `PASS MatrixTileMemFoldInPlaceFixPt4x6x5` and completed `csynth_design`.
- The in-place FixPt canary reported estimated Fmax 123.77 MHz, estimated
  clock 8.080 ns, latency 111 cycles, interval 96 cycles, and utilization
  estimate 6 BRAM_18K, 8 DSP, 5496 FF, and 5072 LUT.
- Compact evidence is captured in the Rust repo under
  `docs/vitis-validation/2026-06-30-inplace-c-memfold/` with README,
  `summary-both.{md,json}`, sidecar Tcl, Vitis logs, and csynth reports.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 25-program
  validation set at commit `79d1b67`, including the explicit Rust-subset
  in-place C MemFold canary with `inputs { a, b } inouts { c }`.
- This still does not accept original Scala Lab2 Part 5/6 source, raw Scala
  `@spatial` wrappers, host `ArgIn`/`setMem`, source-level Part5/Part6 shell
  extraction, outer K tiling, `numel_k` MemFold bounds, Part6 `par`, banking,
  generic Spatial `MemFold`, generic DMA, broader fixed-point widths, FixPt
  tail tiles, board execution, Vivado implementation/place-and-route, or
  timing-closure evidence.

## 2026-06-30 — Rust rewrite narrow in-place C MemFold canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Code commit: `9025f5964e8781e271401d42000b185a362ba6f8`.
Evidence/docs commit: `febd1fbc8aa1c6eb10b465f7e378ecc2f162c16b`.

Frontend/IR/HLS checkpoint:
- Added first-class `inouts { c: Dram<...>[ROWS, COLS] }` support for the
  narrow rank-2 `Dense2dTileMemFold` canary.
- Added a separate validation example,
  `MatrixTileMemFoldInPlaceFixPt4x6x5`, rather than replacing the existing
  Vitis-proven `MatrixTileMemFoldFixPt4x6x5`.
- The new canary uses `inputs { a, b } inouts { c }`, preloads
  `tileC_sram` from `c(...)`, performs the existing fixed-shape
  `MemFold(tileC_sram)(0 until K by 1)` body, and stores back to the same
  `c(...)` DRAM.
- The manifest now emits a single mutable `host_kernel_inout` DRAM buffer for
  `c`, and the HLS emitter generates one mutable pointer parameter instead of
  split `cin`/`out` pointers.
- The parser keeps generated/shell column lanes as `jj` in this bridge so the
  HLS pointer named `c` is not shadowed by a C++ loop variable named `c`.
- Local validation membership is now 25 programs.

Local proof added so far:
- Focused HLS/codegen/harness test:
  `lab2_inplace_c_memfold_emits_single_mutable_c_pointer_and_harness`.
- Fixture/plan-only coverage:
  `cargo test -p ee109-examples --locked`.
- Focused MemFold HLS regression:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold`.

Boundary:
- At the initial local checkpoint, this was local host-C++ harness and Vitis
  plan-only evidence only; the follow-up EC2/Vitis evidence is recorded in the
  checkpoint above.
- `Lab2Part5GEMM` and `Lab2Part6GEMM` remain rejected. This still does not
  accept original Scala Lab2 Part 5/6 source, raw Scala `@spatial` wrappers,
  host `ArgIn`/`setMem`, source-level Part5/Part6 shell extraction, outer K
  tiling, `numel_k` MemFold bounds, Part6 `par`, banking, generic Spatial
  `MemFold`, generic DMA, broader fixed-point widths, FixPt tail tiles, board
  execution, Vivado implementation/place-and-route, or timing-closure evidence.

## 2026-06-30 — Rust rewrite Lab2 `numel_m`/`numel_n` parser bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Parser checkpoint:
- Added a narrow frontend bridge for Lab2 row/column extent aliases
  `numel_m` and `numel_n` inside the existing shell-alias/infix tile-IO
  MemFold path.
- Exact tile spellings canonicalize `numel_m`/`numel_n` to the existing
  `TILE_R`/`TILE_C` extents before HIR/classification.
- Tail spellings that declare `numel_m`/`numel_n` canonicalize to the existing
  `row_limit`/`col_limit` checked-payload names before HIR/classification.
- Added a fail-closed guard that keeps `numel_k` K-tiling syntax rejected.

Local proof added so far:
- Red/green focused parser test:
  `cargo test -p spatial-rs-core --locked parse_accel_lab2_infix_tile_io_accepts_numel_m_numel_n -- --nocapture`.
- Focused Lab2 infix regression:
  `cargo test -p spatial-rs-core --locked lab2_infix_tile_io -- --nocapture`.

Boundary:
- This is parser/source-spelling coverage only. It does not add a validation
  program, does not change generated HLS, and does not create new Vitis
  evidence.
- `Lab2Part5GEMM` and `Lab2Part6GEMM` remain rejected. This still does not
  accept original Scala Lab2 source, raw Scala `@spatial` wrappers, host
  `ArgIn`/`setMem`, source-level Part5/Part6 shell extraction, outer K tiling,
  `numel_k`, Part6 `par`, banking, generic Spatial `MemFold`, generic DMA,
  broader fixed-point widths, FixPt tail tiles, board execution, Vivado
  implementation/place-and-route, or timing-closure evidence.

## 2026-07-02 — Rust rewrite scheduled K-tail Part6 canary and validation promotion

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend/IR/HLS checkpoint:
- Added the local canary
  `MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34`.
- This combines the existing named serial K-tail shape (`K=34`,
  `K_TILES=3`, `TILE_K=16`, runtime `numel_k`) with the fixed Part6
  `partial_row_par=2` / `partial_col_par=16` schedule.
- Validation now admits this exact scheduled-tail shape only under the exact
  scheduled-tail kernel name; unlisted scheduled/tail combinations remain
  fail-closed.
- The manifest records a distinct source kind:
  `accel_macro_dense2d_tile_k_memfold_k_tail_part6_par2x16_v0`.
- HLS emission keeps static `TILE_K` local A/B arrays, uses the runtime
  `numel_k` bound for K load/fold loops, and preserves Part6 array partition,
  `PIPELINE II=1`, and row/column unroll pragmas.
- Promoted the canary into the local validation lane as the 30th validation
  program via `dense2d_tile_k_memfold_scheduled_tail_feature_examples()` and
  `validation_programs()`.

Local proof added so far:
- Red/green core IR test:
  `cargo test -p spatial-rs-core --locked checked_ir_accepts_part6_tile_k_memfold_k_tail_bound -- --nocapture`.
- Red/green parser test:
  `cargo test -p spatial-rs-core --locked parse_accel_lab2_outer_k_accepts_part6_numel_k_tail_bound -- --nocapture`.
- HLS/codegen/host-harness test:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k_part6_numel_k_tail_emits_runtime_k_bound_scheduled_hls_and_harness -- --nocapture`.
- Validation-lane membership and focused scheduled-tail tests:
  `cargo test -p ee109-examples --locked dense2d_tile_k_memfold -- --nocapture`
  and
  `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`.
- Vitis dry-run/plan coverage for the 30-program local validation lane:
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles -- --nocapture`
  and
  `cargo test -p ee109-examples --locked --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`.
- EC2/Vitis proof after promotion:
  `ssh -i [ssh-key — see private/ec2-lane.md] [ec2-user@host — see private/ec2-lane.md]`
  ran `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-scheduled-k-tail-30-program`
  from `/home/ubuntu/spatial-rs-runs/scheduled-k-tail-20260702-af8e307/spatial-rs`
  at source commit `af8e307955cc913085aabcd2763800563f6ecc44`. All 30
  validation programs reported `returncode=0`, `csim=true`, and `csynth=true`;
  durable evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-scheduled-k-tail-30-program/`.
- Scheduled-tail Vitis result:
  `MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34` reported
  estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7123-11839
  cycles, interval 7124-11840 cycles, and utilization estimate 8 BRAM_18K,
  128 DSP, 15524 FF, and 12309 LUT. Vitis emitted II-violation warnings while
  trying to pipeline the final C writeback loop; synthesis still completed.
- Focused regressions already green:
  `cargo test -p spatial-rs-core --locked rank2_tile_memfold_outer_k -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`,
  and
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6_fixed_32 -- --nocapture`.

Boundary:
- This now has local parser, checked-IR, manifest, generated-HLS, native
  host-C++ harness, validation-lane, Vitis dry-run/plan, and EC2/Vitis
  `csim_design`/`csynth_design` evidence for the exact 30-program lane.
- It does not accept generic Spatial `MemFold`, broad Scala source
  compatibility, arbitrary K-tail shapes beyond the two named K-tail canaries,
  generic `par`, inferred banking, board execution, Vivado implementation, or
  timing-closure evidence; it also does not claim II=1/performance optimality
  for the final C writeback loop.

## 2026-07-02 — Rust rewrite Lab2 raw-name GEMM alias bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend checkpoint:
- Extended the parser-only Lab2-like outer-K bridge to accept the exact fixed
  raw Lab2 dimension/tile aliases used by the lab sources:
  `M/N=32` and `tileM/tileN/tileK=16`.
- The bridge canonicalizes those declarations, DRAM/SRAM dimensions, offset
  loops (`K by tileK`, `M by tileM`, `N by tileN`), and
  `min(tileK.to[Int], K - kk)` back to the existing `ROWS/COLS` and
  `TILE_R/TILE_C/TILE_K` checked payload names before HIR.
- The same alias bridge applies to the exact scheduled Part6 structural core
  when the partial-tile loops still carry literal `par 2` / `par 16`.

Local proof added so far:
- Focused parser regression:
  `cargo test -p spatial-rs-core --locked lab2_outer_k -- --nocapture`.
- Focused HLS equality regression:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`.
- Focused Part6 parser regression:
  `cargo test -p spatial-rs-core --locked lab2_part6 -- --nocapture`.
- Focused Part6 HLS equality regression:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6 -- --nocapture`.
- Full local gates after formatting:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, and
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`.

Boundary:
- This is parser/source-spelling coverage only. It does not add a validation
  program, does not change generated HLS or manifest output, and does not
  require a new EC2/Vitis run.
- Wrong alias values, wrong offset-loop steps, malformed `numel_k` min forms,
  non-exact raw wrappers, arbitrary K tails beyond the named canaries, generic
  `par`, banking inference, board execution, Vivado implementation, and timing
  closure remain unsupported.

## 2026-07-02 — Rust rewrite Lab2 alternate FSM local canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend/IR/HLS checkpoint:
- Added exact local-course support for `Lab2Part3BasicCondFSMAlt`.
- The raw Scala fixture is token-quarantined in the source adapter and lowered
  to a bounded Rust-subset frontend source before HIR/classification.
- Added distinct checked `ProgramKind::Lab2BasicCondFsmAlt` /
  `Stmt::Lab2BasicCondFsmAlt` so the alternate FSM cannot silently reuse the
  canonical `Lab2Part3BasicCondFSM` HLS behavior.
- HLS emission now produces the exact alternate four-band state behavior:
  `state`, `state * 2`, `state * 3`, and `state * 4`, with a matching host
  harness oracle.
- The local validation roster is now 31 programs, with Alt as an accepted
  fixture adapter. EC2/Vitis `csim_design`/`csynth_design` evidence for this
  31-program lane is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-lab2-fsm-alt-31-program/`.

Proof added:
- Red tests first showed the canonical Alt source failing with `spatial:E0405`,
  the raw Scala fixture failing with `spatial:E0200`, and the HLS test failing
  before parser support existed.
- Focused green checks:
  `cargo test -p spatial-rs-core --locked lab2_fsm_alt -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_fsm_alt -- --nocapture`,
  `cargo test -p spatial-rs-core --locked control_fsm -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen control_fsm -- --nocapture`,
  `cargo test -p spatial-rs-core --locked registry_lists_current_exact_raw_scala_adapters -- --nocapture`,
  `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`,
  `cargo test -p ee109-examples --locked --test emit_vitis_dry_run emit_vitis_dry_run_binary_generates_m1_frontend_bundles -- --nocapture`, and
  `cargo test -p ee109-examples --locked --test run_vitis_validation run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`.
- Post-review local gates passed on commit
  `9025f5964e8781e271401d42000b185a362ba6f8`: `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`, Rust/vault `git diff --check`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, and
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`.
- EC2 host `[ec2-host — see private/ec2-lane.md]` completed
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-lab2-fsm-alt-9025f59`
  from `/home/ubuntu/spatial-rs-runs/lab2-fsm-alt-9025f59/spatial-rs` with
  return code 0 across all 31 validation programs. Each program reported
  `csim=true` and `csynth=true`. `Lab2Part3BasicCondFSMAlt` reported estimated
  Fmax 136.99 MHz, estimated clock 7.300 ns, latency 40 cycles, interval 32
  cycles, and utilization estimate 0 BRAM_18K, 0 DSP, 882 FF, and 983 LUT.

Boundary:
- This is exact local fixture support, not generic Spatial `FSM`, arbitrary
  condition/action lowering, arbitrary registers, dynamic lengths, scheduling,
  `par`, broad Scala source compatibility, board execution, Vivado
  implementation, or timing-closure evidence.

## 2026-07-03 — Rust rewrite raw Lab2 GEMM source proof extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit: `44cbbbbfa6fb06bbe980deac351ee26b3ca52c71`
(`Extract raw Lab2 GEMM source proof`).

Frontend/source-adapter checkpoint:
- Extracted a private `Lab2FixedGemmSourceProof` and
  `Lab2FixedGemmAccelProof` in
  `crates/spatial-rs-core/src/source_adapter.rs`.
- The fixed raw `Lab2Part5GEMM` and `Lab2Part6GEMM` source adapter now proves
  the accepted fixed shell profile (`32 32 32` or the exact named `32 32 34`
  K-tail profile), raw class target, and normalized single-`Accel` body before
  emitting generated Lab2-like frontend source.
- Existing fail-closed behavior is preserved: wrong dimensions, wrong tile
  sizes, wrong fixed-point type, nonzero explicit fold start, extra hardware
  setup, extra `Accel`, and wrong Part6 `par` factors remain unsupported.
- This is a compiler-structure checkpoint only. Accepted profiles, checked
  payloads, generated HLS, manifests, validation membership, and vendor-HLS
  evidence boundaries are unchanged.

Proof added:
- Red-first focused test initially failed because
  `prove_lab2_fixed_gemm_source` did not exist.
- Focused green checks:
  `cargo test --locked -p spatial-rs-core source_adapter::tests::lab2_fixed_gemm`,
  `cargo test --locked -p spatial-rs-core raw_lab2_part`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part`, and
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-raw-gemm-proof-plan`, and
  `git diff --check`.
- The plan-only validation roster remained 33 kernels and 33 sidecar
  `run_both.tcl` scripts.

Boundary:
- No EC2/Vitis rerun was needed for this slice because HLS/manifest output and
  validation-program membership stayed unchanged.
- This still does not add broad Scala source compatibility, generic GEMM,
  generic Spatial `MemFold`, arbitrary K tails, dynamic dimensions, schedule
  inference, banking inference, board execution, Vivado implementation, or
  timing closure.

## 2026-07-03 — Rust rewrite Tile-K HLS schedule preflight ledger

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit: `3bd86c13c5ffe99828b8cf6fa46f136d8746b6e9`
(`Extract Tile-K HLS schedule preflight`).

HLS backend checkpoint:
- Added crate-private `TileKScheduleLowering` and
  `tile_k_schedule_lowering` in `crates/spatial-rs-hls/src/tile_k.rs`.
- The Tile-K HLS ledger now owns schedule/payload factor agreement, ordered
  Part6 partition-recipe validation, and the serial no-partitions guard before
  the emitter renders pragmas.
- `emit_dense2d_tile_k_memfold_kernel_plan` now consumes this helper instead
  of carrying the Tile-K-specific preflight inline.
- Existing generated C++ byte shape, manifests, and validation membership are
  intended to remain unchanged; this is a backend reliability/refactoring
  checkpoint, not a new HLS surface.

Proof added:
- Red-first tests initially failed because `tile_k_schedule_lowering` and
  `TileKScheduleLowering` did not exist.
- Focused green checks:
  `cargo test --locked -p spatial-rs-hls tile_k_schedule_lowering`,
  `cargo test --locked -p spatial-rs-hls tile_k_`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_fixed_32_matches_stable_scheduled_hls_snapshot`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_k_tail_preserves_existing_scheduled_tail_hls_and_manifest`, and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_part6_structural_par_preserves_scheduled_hls_and_manifest`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-tile-k-schedule-preflight-plan`, and
  `git diff --check`.
- The plan-only validation roster remained 33 kernels and 33 sidecar
  `run_both.tcl` scripts.

Boundary:
- No EC2/Vitis rerun was needed because generated HLS, manifests, and
  validation-program membership stayed unchanged.
- This still does not add syntax, schedule support, banking inference,
  checked-IR changes, arbitrary K tails, dynamic dimensions, board execution,
  Vivado implementation, or timing closure.

## 2026-07-03 — Rust rewrite raw Lab2 GEMM K-tail source compatibility

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Frontend/HLS checkpoint:
- Extended the narrow raw Scala source adapter for `Lab2Part5GEMM` and
  `Lab2Part6GEMM` to accept only the exact named K-tail runtime profile
  `runtimeArgs = "32 32 34"` in addition to the previous fixed
  `runtimeArgs = "32 32 32"` profile.
- The adapter still requires the same fixed token-stream quarantine:
  `tileM/tileN/tileK = 16`, `FixPt[TRUE,_24,_8]`, exact
  `ArgIn`/`setArg`/`DRAM`/`setMem` setup, and one known Part5 or Part6
  `Accel` body.
- For `K=34`, raw Part5 now emits bounded Lab2-like frontend source that
  normalizes to `MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`.
- For `K=34`, raw Part6 now normalizes to
  `MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34`, preserving
  the existing checked `par 2` / `par 16` scheduled payload.
- Near-miss raw runtime profiles such as `32 32 33`, `32 32 35`, and
  `32 34 34` remain unsupported.
- Repo docs now describe this as source compatibility for the two already
  Vitis-proven K-tail canaries, not as generic K-tail or broad Scala support.

Proof added:
- Red-first adapter/HLS tests initially failed because the raw `32 32 34`
  wrappers fell through to unsupported generic reduction lowering.
- Focused green checks:
  `cargo test --locked -p spatial-rs-core source_adapter::tests::lab2_fixed_gemm`,
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check` in both the Rust repo and research vault.

Boundary:
- This slice does not add a validation-program member and does not require a
  new EC2/Vitis run because the accepted raw `32 32 34` wrappers preserve exact
  checked-program, generated HLS, and manifest equality with the existing
  serial/scheduled K-tail validation members.
- Arbitrary K values, dynamic dimensions, non-exact raw Scala wrappers,
  generic Spatial `MemFold`, broader fixed-point semantics, generic `par`,
  inferred banking, board execution, Vivado implementation, and timing closure
  remain unsupported.

## 2026-07-03 — Rust rewrite Tile-K proof contract foundation

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`ed32bfdb22db8688306dc5c0a948d8d752cf29f8` (`Start Tile-K proof contract`).

Compiler checkpoint:
- Added an initial private Tile-K MemFold proof facade inside
  `classifier/tiled2d.rs`: `TileKProfile`, `TileKMemFoldProof`, and
  `TileKProofResult`.
- Routed `classify_dense2d_tile_k_memfold` through `prove_tile_k_memfold` and
  `program_from_tile_k_memfold_proof`, so the caller now consumes a named proof
  result before reconstructing the same checked `Program`.
- Preserved classifier diagnostic priority with a cheap Tile-K candidate
  precheck before resolver work. This fixed a full-suite regression where an
  unrelated control-FSM near miss reported resolver duplicate-name
  `spatial:E0302` before the expected feature diagnostic `spatial:E0405`.
- Added direct proof tests for the serial full-K profile and generic no-match
  fallthrough.
- Updated repo docs to record this as compiler foundation only, not broader
  Tile-K/Scala/HLS support.

Proof added:
- Focused regression checks passed:
  `cargo test --locked -p spatial-rs-core parser::tests::control_fsm_feature_name_collisions_use_feature_diagnostic`
  and `cargo test --locked -p spatial-rs-core tile_k_contract`.
- Full local gates passed:
  `cargo test --locked`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- The proof constructor currently wraps the existing helper sequence. The next
  extraction step is to move loop-spine, access-role, phase, schedule, and
  payload checks directly into the proof object and pin all four accepted
  profiles with direct proof tests.

## 2026-07-03 — Rust rewrite Tile-K proof payload construction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`24eb75b9d3a33003e1806fab5ea55055817deebe` (`Build Tile-K proof payload directly`).

Compiler checkpoint:
- Extended the private Tile-K proof contract with `TileKScheduleProof`.
- Pinned all four current accepted Tile-K profiles with direct proof tests:
  serial full-K, Part6 scheduled full-K, serial `K=34` tail, and Part6
  scheduled `K=34` tail.
- Added proof-level near-miss tests for unsupported Part6 schedule factors and
  split-parent C-store grouping.
- Changed the proof path so `build_tile_k_memfold_proof` constructs the
  `Dense2dTileKMemFold` payload directly instead of first building a `Program`
  and extracting the payload back out.
- Preserved checked-IR validation and public diagnostic priority by
  rehydrating the payload through the same checked `Program` helper before
  accepting the proof. This fixed the transient regression where a wrong Part6
  row-par near miss surfaced `spatial:E0415` instead of the previous
  `spatial:E0300`.
- Updated repo docs to record this as compiler foundation only, not broader
  Tile-K, K-tail, schedule, Scala, or HLS support.

Proof added:
- Red-first proof-contract test initially failed at compile time because
  `TileKMemFoldProof` did not yet expose a schedule sub-proof.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-core parser::tests::lab2_outer_k_infix_tile_io_near_misses_fail_closed`,
  `cargo test --locked -p spatial-rs-core tile_k_contract`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo test --locked`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining Tile-K proof work is internal factoring: move loop-spine,
  access-role, phase, and schedule checks into smaller proof-owned helpers.

## 2026-07-03 — Rust rewrite Tile-K proof source-shape and phase-spine facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`ab1697d6067186df415e955e1034307b3186fafb` (`Enrich Tile-K proof facts`).

Compiler checkpoint:
- Extended the private Tile-K proof contract with `TileKSourceShapeProof` and
  `TileKPhaseSpineProof`.
- `TileKSourceShapeProof` records the accepted DRAM roles, SRAM tile roles,
  matrix dimensions, and tile dimensions. Tile counts are loop-bound facts, not
  source-shape facts.
- `TileKPhaseSpineProof` records the accepted outer/tile/lane index names,
  canonical loop-bound symbols (`K_TILES`, `ROW_TILES`, `COL_TILES`,
  `TILE_R`, `TILE_C`, and `TILE_K` or `numel_k`), K-tail bound, and
  hoisted-LHS source placement.
- Kept `Program` as the HLS contract: `program_from_tile_k_memfold_proof`
  still rebuilds from `proof.element_type` and `proof.payload`, not from the
  source-shape or phase-spine facts.
- Updated repo docs and the Tile-K contract plan to record this as
  compiler-foundation progress only.

Proof added:
- Red-first proof-contract assertions initially failed at compile time because
  `TileKMemFoldProof` did not expose source-shape/phase-spine sub-proofs, then
  again because the phase-spine bound fields did not exist.
- A GPT-5.5 xhigh read-only reviewer recommended adding explicit phase bound
  fields; those fields were added before commit.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k_contract`,
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining Tile-K proof work is still internal factoring: move loop-spine,
  access-role, phase, and schedule checks into smaller proof-owned helpers.

## 2026-07-03 — Rust rewrite Tile-K phase-spine proof extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`787510498f0fcca269db571b0418c4f6c4d6f773` (`Extract Tile-K phase-spine proof`).

Compiler checkpoint:
- Extracted the second proof-owned helper from the monolithic Tile-K recognizer:
  `prove_tile_k_phase_spine`.
- The helper owns outer-K loop recovery, optional `numel_k` recovery, tile-row
  and tile-column loop recovery, canonical `K_TILES`/`ROW_TILES`/`COL_TILES`
  tile-count validation, exact row/column coverage, exact-or-bounded-ceil K
  coverage, non-degenerate static K-split validation, hoisted/non-hoisted LHS
  phase layout, phase statement recovery, and the resolver-backed phase-spine
  ancestry guard.
- Access-role matching, fold/update semantics, schedule extraction, payload
  construction, and checked `Program` rehydration remain separate proof-path
  responsibilities.
- Updated repo docs and the Tile-K contract plan to clarify that tile counts
  now belong to phase-spine proof extraction, not source-shape matching.

Proof added:
- Red-first helper test initially failed at compile time because
  `prove_tile_k_phase_spine` did not exist.
- A GPT-5.5 xhigh read-only reviewer confirmed the helper boundary and warned
  to preserve diagnostic priority and keep access-role parsing out of the
  phase helper.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k_phase_spine_helper_records_loop_bounds_and_phase_refs`,
  `cargo test --locked -p spatial-rs-core tile_k_phase_spine_helper`,
  `cargo test --locked -p spatial-rs-core tile_k_phase_spine`,
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining Tile-K proof work is still internal factoring: move access-role
  and schedule checks into smaller proof-owned helpers.

## 2026-07-03 — Rust rewrite Tile-K access-role proof extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`61d24eea248d73a4c46718bd278e3dae8fdc58ed` (`Extract Tile-K access-role proof`).

Compiler checkpoint:
- Extracted the third proof-owned helper from the monolithic Tile-K recognizer:
  `prove_tile_k_access_roles`.
- The helper owns LHS and RHS load role matching, shared inner-K lane/bound
  agreement, canonical `TILE_R`/`TILE_C`/`TILE_K` or `numel_k` access bounds,
  C preload role matching, C preload lane coherence with the fold lanes, and
  final C-store proof.
- The helper returns owned lane names and bounds (`row`, `col`, `inner_k`,
  `row_end`, `col_end`, `inner_k_end`) so the remaining fold/update schedule
  matcher and payload construction stay separate.
- Updated repo docs and the Tile-K contract plan to record this as
  no-HLS-drift compiler factoring; fold/update schedule extraction remains the
  next internal proof-owned helper slice.

Proof added:
- Red-first helper test initially failed at compile time because
  `prove_tile_k_access_roles` did not exist.
- A GPT-5.5 xhigh read-only reviewer confirmed the helper boundary and warned
  to keep C-store validation inside the helper; a split-parent final-store
  regression now asserts the helper itself rejects that case.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k_access_roles_helper`,
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining Tile-K proof work is still internal factoring: move fold/update
  schedule checks into a smaller proof-owned helper.

## 2026-07-03 — Rust rewrite Tile-K fold schedule proof extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`ee9132795951336bdd95225077efd7b5d4ee8763` (`Extract Tile-K fold schedule proof`).

Reviewer follow-up commit:
`962fbcec1ae979f02e7bfbf232f27dbb817ff20c` (`Tighten Tile-K fold schedule helper`).

Compiler checkpoint:
- Extracted the fourth proof-owned helper from the monolithic Tile-K recognizer:
  `prove_tile_k_fold_schedule`.
- The helper owns the existing partial-product and C-accumulation fold matcher,
  including resolver-backed partial tile write/LHS read/RHS read facts,
  resolver-backed `c_tile := c_tile + partial_tile` facts, and serial/Part6
  `partial_row_par` / `partial_col_par` recovery.
- The main proof path is now staged as source-shape proof, phase-spine proof,
  access-role proof, fold-schedule proof, payload construction, and checked
  `Program` rehydration.
- Updated repo docs and the Tile-K contract plan to record this as the final
  obvious internal Tile-K proof factoring checkpoint in the current file.
- Follow-up review cleanup made the helper return a Tile-K-specific
  `TileKFoldSchedule` instead of the generic `MemFoldSchedule`, loosened the
  `SourceFile` lifetime, and expanded the direct helper test across all four
  current Tile-K profiles.

Proof added:
- Red-first helper test initially failed at compile time because
  `prove_tile_k_fold_schedule` did not exist.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k_fold_schedule_helper`,
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.
- The same full local gates passed again after the reviewer cleanup commit.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining work is not another obvious Tile-K helper split; the next useful
  manager action is to decide whether to run a current-head EC2/Vitis refresh
  for the accumulated no-HLS-drift proof factoring or move to the next EE109
  feature gap.

## 2026-07-03 — Rust rewrite Tile-K source-shape proof extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`dd8fafbcbcd045d92acb94c7d7ee17f41319253a` (`Extract Tile-K source-shape proof`).

Compiler checkpoint:
- Extracted the first proof-owned helper from the monolithic Tile-K recognizer:
  `prove_tile_k_source_shape`.
- The helper owns DRAM/SRAM role recovery, element-type agreement,
  matrix-dimension checks, local tile-dimension checks, and the generic
  no-match boundary for non-candidates.
- The helper returns borrowed HIR ports/memories plus copied dimensions so the
  rest of `build_tile_k_memfold_proof` can continue validating loop bounds,
  phase spine, access roles, fold schedule, payload construction, and checked
  `Program` rehydration.
- Tightened the durable wording: `TileKSourceShapeProof` records roles and
  matrix/tile dimensions only. `ROW_TILES`, `COL_TILES`, and `K_TILES` remain
  validated from recovered canonical loop bounds.

Proof added:
- Red-first helper test initially failed at compile time because
  `prove_tile_k_source_shape` did not exist.
- A GPT-5.5 xhigh read-only reviewer caught the tile-count ownership boundary;
  the helper was adjusted before commit.
- Focused checks passed:
  `cargo test --locked -p spatial-rs-core tile_k_source_shape`,
  `cargo test --locked -p spatial-rs-core tile_k_contract_uses_source_shape_helper_proof`,
  `cargo test --locked -p spatial-rs-core tile_k`,
  `cargo test --locked -p spatial-rs-hls lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls lab2_raw_part`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`,
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-plan`, and
  `git diff --check`.

Boundary:
- This slice does not change accepted syntax, checked payloads, manifests,
  generated HLS, or the 31-program validation roster.
- EC2/Vitis was skipped because emitted artifacts and validation membership did
  not change.
- Remaining Tile-K proof work is still internal factoring: move loop-spine,
  access-role, phase, and schedule checks into smaller proof-owned helpers.

## 2026-07-03 — Rust rewrite Tile-K proof current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`962fbcec1ae979f02e7bfbf232f27dbb817ff20c` (`Tighten Tile-K fold schedule helper`).

Compiler checkpoint:
- Staged the exact clean local commit on the EC2 Vitis host using a Git bundle
  rather than a remote branch, then ran the full 31-program Vitis validation
  roster.
- The EC2 default `/usr/bin/cargo` was too old for the current lockfile, so the
  run pinned the rustup-managed toolchain directly:
  `/home/ubuntu/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo`
  with matching `RUSTC`.
- The full `--execute --mode both` run passed for all 31 kernels:
  every row in `summary-both.md` reports `returncode=0`, `csim=true`, and
  `csynth=true`.

Evidence added:
- Rust repo evidence folder:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-tile-k-proof-current-head/`.
- Captured artifacts: `summary-both.md`, `summary-both.json`, 31 Vitis logs,
  31 csynth reports, and 31 sidecar Tcl scripts.
- The scheduled K-tail Tile-K canary
  `MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34` passed with
  estimated clock 7.300 ns, estimated Fmax 136.99 MHz, top-level latency
  7123 to 11839 cycles, and utilization estimate 8 BRAM_18K, 128 DSP,
  15524 FF, 12309 LUT, and 0 URAM.

Boundary:
- This is a current-head vendor-HLS stability refresh for the accumulated
  Tile-K proof factoring. It does not claim a new accepted syntax surface,
  changed checked payload, changed generated HLS, changed manifest, or changed
  validation-program membership.
- The next manager move is to choose the next EE109 feature gap or broaden one
  of the narrow lab adapters into a reusable supported feature.

## 2026-07-03 — Rust rewrite literal-two MemReduce/MemFold 33-program Vitis checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commits:
- `30d338e00b76c071622468c94edf6c6866d44180`
  (`Promote literal-two mem reductions to validation`).

Compiler checkpoint:
- Promoted the already-supported `MemReduceTwos16` and `MemFoldTwos16`
  literal-`2` canaries into `validation_programs()`, increasing the local EE109
  validation roster from 31 to 33 programs.
- The change did not add a new HLS emitter path. It exercises the existing
  narrow `MemReduceFill v0` / `MemFoldFill v0` constant-fill memory-reduction
  path with fill value `2`.
- Local gates passed before EC2: `cargo fmt --all -- --check`,
  `git diff --check`, `cargo test --locked`, `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, and
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-33-plan`.

Evidence added:
- EC2 run directory:
  `/home/ubuntu/spatial-rs-runs/memreduce-twos-33-20260703-30d338e/spatial-rs`.
- Rust repo evidence folder:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-memreduce-twos-33-program/`.
- The full `--execute --mode both` Vitis run passed for all 33 kernels:
  every row in `summary-both.md` reports `returncode=0`, `csim=true`, and
  `csynth=true`.
- Captured artifacts: `summary-both.md`, `summary-both.json`, 33 Vitis logs,
  33 csynth reports, and 33 sidecar Tcl scripts.
- `MemReduceTwos16` and `MemFoldTwos16` each passed with estimated clock
  7.300 ns, estimated Fmax 136.99 MHz, top-level latency 61 cycles,
  interval 62 cycles, and utilization estimate 0 BRAM_18K, 0 DSP, 1367 FF,
  2011 LUT, and 0 URAM.

Boundary:
- This proves vendor `csim_design` and `csynth_design` for the exact
  33-program validation set at commit `30d338e`.
- It does not claim generic Spatial `MemReduce` / `MemFold`, arbitrary reducer
  bodies, dynamic memory-reduction bounds, board execution, Vivado
  implementation, timing closure, or performance optimality.

## 2026-07-03 — Rust rewrite Tile-K HLS lowering ledger start

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`3137a8b` (`Start Tile-K HLS lowering ledger`).

Compiler checkpoint:
- Added crate-private `crates/spatial-rs-hls/src/tile_k.rs` as the first
  Tile-K HLS backend-ledger module.
- Moved runtime/static K-loop-bound rendering out of the large HLS emitter into
  `tile_k_loop_bound`.
- The helper now owns both current cases:
  full-K profiles use the static `TILE_K` loop bound, while K-tail profiles
  emit the runtime `numel_k = min(TILE_K, K - kk*TILE_K)` declaration.
- The emitter now consumes this helper; generated HLS and manifests are intended
  to stay byte-stable.

Proof added:
- Red-first `tile_k_loop_bound` tests failed on the intentional `todo!`, then
  passed after implementation.
- Focused HLS stability tests passed:
  `cargo test --locked -p spatial-rs-hls tile_k_loop_bound`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`, and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_k_tail_preserves_existing_scheduled_tail_hls_and_manifest`.
- Full local gates passed:
  `cargo fmt --all -- --check`, `git diff --check`, `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`, and
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-tile-k-ledger-plan`.
- The plan-only validation summary still contains 33 kernels and 33 sidecar
  Tcl files.

Boundary:
- This is a no-HLS-drift backend reliability slice. It does not change accepted
  syntax, checked IR, manifests, generated HLS, validation membership, or vendor
  evidence.
- Fresh EC2/Vitis was not needed because the generated HLS/manifest stability
  tests and plan-only roster stayed unchanged.

## 2026-07-03 — Rust rewrite Tile-K HLS local storage ledger

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`100c18fa970dc4826a5a8c7ede96c6a701c376ab`
(`Extract Tile-K HLS local storage layout`).

Compiler checkpoint:
- Extended crate-private `crates/spatial-rs-hls/src/tile_k.rs` with
  `TileKLocalStorage` and `tile_k_local_storage`.
- The helper now owns the current Tile-K local array layout split:
  scheduled Part6 profiles emit 2-D `lhs_tile`, `rhs_tile`, `c_tile`, and
  `partial_tile` arrays; serial profiles emit flattened arrays with the same
  overflow-checked sizes previously computed in `emit.rs`.
- The main Tile-K emitter now splices in the helper's declaration block while
  keeping schedule validation, partition validation, pipeline/unroll pragmas,
  and loop bodies unchanged.

Proof added:
- Red-first storage tests first failed on the intentional `todo!`, then passed:
  scheduled 2-D declarations, serial flattened declarations, and serial
  flattened overflow rejection.
- Focused stability tests passed:
  `cargo test --locked -p spatial-rs-hls tile_k_`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part5_k_tail_preserves_existing_tail_hls_and_manifest`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_k_tail_preserves_existing_scheduled_tail_hls_and_manifest`, and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_fixed_32_matches_stable_scheduled_hls_snapshot`.
- Full local gates passed:
  `cargo fmt --all -- --check`, `git diff --check`, `cargo test --locked`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`, and
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-tile-k-local-storage-plan`.
- The plan-only validation summary still contains 33 kernels and 33 sidecar
  Tcl files.

Boundary:
- This is a no-HLS-drift backend reliability slice. It does not change accepted
  syntax, checked IR, manifests, generated HLS, validation membership, or vendor
  evidence.
- Fresh EC2/Vitis was skipped because the HLS byte-stability tests, dry-run
  generation, and plan-only validation roster stayed unchanged.

## 2026-07-03 — Rust rewrite serial Tile-K row/column/K tail canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commit:
`fa33d55` (`Add serial Tile-K row-col tail canary`).

Compiler checkpoint:
- Added the named serial Tile-K GEMM tail canary
  `MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34`.
- The checked payload carries `ROWS=33`, `COLS=35`, `K=34`,
  `ROW_TILES=3`, `COL_TILES=3`, `K_TILES=3`, `TILE_R/TILE_C/TILE_K=16`,
  plus `row_bound=row_limit`, `col_bound=col_limit`, and
  `k_bound=numel_k`.
- Extended Tile-K HIR proof, checked IR, manifest labeling, HLS planning, and
  serial HLS emission so dynamic `row_limit`, `col_limit`, and `numel_k` bound
  the local loops while global DRAM addresses still stride by static
  `TILE_R`, `TILE_C`, and `TILE_K`.
- Added the canary to the `ee109-examples` validation roster, increasing the
  local plan-only roster from 33 to 34 programs.
- Kept scheduled Part6 row/column tails fail-closed; the checked IR rejects
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34` until
  lane guards/predicate semantics are designed.

Proof added:
- Focused tests passed for parser acceptance, checked-IR acceptance/rejection,
  HLS emission, and the local host-C++ harness:
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k_accepts_serial_row_col_k_tail_bounds --lib`,
  `cargo test --locked -p spatial-rs-core checked_ir_accepts_serial_tile_k_memfold_row_col_k_tail_bounds --lib`,
  `cargo test --locked -p spatial-rs-core row_col_tail --lib`, and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_row_col_k_tail_emits_runtime_bounds_and_harness`.
- Surrounding Tile-K tests passed:
  `cargo test --locked -p spatial-rs-core tile_k --lib`,
  `cargo test --locked -p spatial-rs-hls tile_k --lib`, and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k`.
- The `ee109-examples` validation-roster tests passed, including dry-run and
  plan-only sidecar generation.
- Full local gates passed:
  `cargo fmt --all -- --check`, `cargo test --locked --quiet`,
  `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`.
- Generated explicit 34-program plan-only sidecars at
  `/Users/david/Documents/David_code/spatial-rs/target/vitis-validation-row-col-k-tail-34-plan/`.

Boundary:
- This proves local parser/checker/HLS emission/host-harness behavior for the
  serial non-square Tile-K tail canary and prepared it for the EC2/Vitis
  checkpoint recorded below.
- This does not claim generic M/N tails, scheduled Part6 row/column tails,
  arbitrary GEMM shapes, generic `par`, performance optimality, timing closure,
  Vivado implementation, or board execution.

## 2026-07-03 — Rust rewrite row/column/K tail 34-program Vitis checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust evidence commit:
`2087625` (`Keep core compatible with Rust 1.75`).

Checkpoint:
- Re-ran the full 34-program EE109 validation roster on EC2/Vitis after the
  serial row/column/K-tail canary landed. The source snapshot was clean commit
  `2087625`, which adds only a Rust 1.75 compatibility shim over the previous
  canary commit `fa33d55`.
- EC2 host `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`) ran Vitis 2025.1 from
  `/home/ubuntu/spatial-rs-runs/row-col-k-tail-34-2087625/spatial-rs`.
- Command:
  `cargo run --manifest-path /home/ubuntu/spatial-rs-runs/row-col-k-tail-34-2087625/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out /home/ubuntu/spatial-rs-runs/row-col-k-tail-34-2087625/spatial-rs/target/vitis-validation-row-col-k-tail-34-2087625`
  with `/tools/Xilinx/2025.1/Vitis/settings64.sh` sourced first.
- Remote-only setup note: the copied `Cargo.lock` was rewritten from lockfile
  version 4 to version 3 so remote Cargo 1.75 could read it; the local repo
  lockfile was unchanged.
- Result: all 34 kernels reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- Durable Rust evidence is captured under
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-row-col-k-tail-34-program/`.

Canary evidence:
- `MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`: estimated Fmax
  136.99 MHz, estimated clock 7.300 ns, latency 13363-61591 cycles, interval
  13364-61592 cycles, utilization estimate 41 BRAM_18K, 64 DSP, 8227 FF,
  6013 LUT, and 0 URAM.
- `MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34`: estimated Fmax
  136.99 MHz, estimated clock 7.300 ns, latency 2329-274840 cycles, interval
  2330-274841 cycles, utilization estimate 11 BRAM_18K, 7 DSP, 4389 FF,
  4917 LUT, and 0 URAM.
- `MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34`: estimated
  Fmax 136.99 MHz, estimated clock 7.300 ns, latency 7123-11839 cycles,
  interval 7124-11840 cycles, utilization estimate 8 BRAM_18K, 128 DSP,
  15524 FF, 12309 LUT, and 0 URAM.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 34-program
  validation set on `xc7z020-clg400-1`, including the serial Tile-K
  row/column/K-tail runtime-bound canary.
- This does not claim board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM support, automatic banking inference, broader `par` inference,
  scheduled row/column tails, II=1 for every loop, or performance optimality.

## 2026-07-03 — Rust rewrite scheduled row/column/K tail 35-program Vitis checkpoint

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Rust commits:
- `d521a0f` (`Add scheduled row-col K-tail canary`)
- `d5816ad` (`Record scheduled row-col K-tail Vitis evidence`)

Checkpoint:
- Added the exact scheduled Part6 row/column/K-tail Tile-K canary
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`.
- The canary uses `ROWS=33`, `COLS=35`, `K=34`, 16-wide tiles, runtime
  `row_limit`, `col_limit`, and `numel_k`, with fixed Part6
  `partial_row_par=2` and `partial_col_par=16`.
- HLS lowering keeps load/store loops runtime-bounded, keeps scheduled compute
  loops static at the 16-wide tile bounds, and guards inactive lanes before
  writing `partial_tile` or accumulating into `c_tile`.
- Re-ran the full 35-program EE109 validation roster on EC2/Vitis. The source
  snapshot was clean commit `d521a0f`, with evidence recorded at `d5816ad`.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/scheduled-row-col-k-tail-35-d521a0f/spatial-rs`.
- Remote-only setup note: the copied `Cargo.lock` was rewritten from lockfile
  version 4 to version 3 so remote Cargo 1.75 could read it; the local repo
  lockfile was unchanged.
- Result: all 35 kernels reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- Durable Rust evidence is captured under
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-scheduled-row-col-k-tail-35-program/`.

Proof added:
- Full local gates before the EC2 run passed:
  `cargo fmt --all -- --check`, `cargo test --locked --quiet`,
  `cargo clippy --all-targets --locked -- -D warnings`, and `git diff --check`.
- EC2/Vitis 2025.1 `--execute --mode both` passed all 35 programs.
- Evidence bundle includes 35 logs, 35 synthesis reports, 35 sidecar TCL files,
  `summary-both.json`, `summary-both.md`, `README.md`, and
  `evidence-manifest.json`.

Canary evidence:
- `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`:
  estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency 2707-26872
  cycles, interval 2708-26873 cycles, utilization estimate 58 BRAM_18K,
  131 DSP, 19307 FF, 13628 LUT, and 0 URAM.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 35-program
  validation set on `xc7z020-clg400-1`, including the scheduled Tile-K
  row/column/K-tail runtime-bound canary with guarded inactive lanes.
- This does not claim board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM support, automatic banking inference, broader `par` inference, II=1 for
  every loop, or performance optimality.

## 2026-07-03 — Rust rewrite rank-2 access proof helper extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Started Phase 2 of the full Rust Spatial rewrite roadmap by extracting the
  rank-2 access fact matcher from the Tile-K classifier into
  `classifier/rank2_access.rs`.
- Reused the shared helper in the non-outer-K `Dense2dTileMemFold` path for
  lhs tile load, rhs tile load, C preload, partial/accumulation fold, and final
  C tile store checks.
- Kept the existing structural recognizers in place first, then added
  resolver-backed rank-2 fact checks as an additional fail-closed guard.
- Added a non-outer-K `MatrixTileMemFold4x6x5` behavioral test that exercises
  the new fold fact matcher on parsed/resolved HIR.
- Updated the full Rust rewrite roadmap to mark the first helper-extraction
  increment complete while leaving the broader negative-test matrix open.

Proof added:
- `cargo fmt --all -- --check`
- `cargo test --locked`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-rank2-access-plan`

Boundary:
- This proves the local Rust parser/checker/HLS-emission test suite and the
  35-program Vitis sidecar plan still pass after the proof-helper refactor.
- This does not claim fresh EC2/Vitis execution, board execution, generic
  Spatial compatibility, arbitrary rank-2 local-memory lowering, or completion
  of the remaining fail-closed negative tests for swapped lanes, wrong K lanes,
  wrong const provenance, and split-parent facts.

## 2026-07-03 — Rust rewrite Dense2d MemFold fact-negative coverage

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Added direct `Dense2dTileMemFold` fact-gate negative tests for the first
  reusable rank-2 access helper increment.
- Covered swapped local lane symbols, a wrong RHS K lane in the fold product,
  equal-valued wrong row-coefficient const provenance, and split-parent store
  access facts.
- The tests passed without production-code changes, confirming that the helper
  extraction was already fail-closed for these named residual risks.
- Updated the full Rust rewrite roadmap so Phase 2's first proof-helper slice
  now points toward Phase 3 Lab2 memory reductions next.

Proof added:
- `cargo test --locked -p spatial-rs-core dense2d_memfold_ -- --nocapture`

Boundary:
- This is local Rust test coverage only. It does not add new accepted Spatial
  syntax, alter generated HLS, run fresh EC2/Vitis, or prove broad generic
  rank-2 memory lowering beyond the current `Dense2dTileMemFold` slice.

## 2026-07-03 — Rust rewrite Lab2 memory-reduction raw-island proof

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Started Phase 3 by moving raw `Lab2Part1SimpleMemReduce` and
  `Lab2Part2SimpleMemFold` away from exact `Accel` token equality.
- Added a narrow raw-island proof for the Lab2 memory-reduction shape:
  fixed class names, one `DRAM[Int](16)` output, one `Accel`, exact
  `-5 until 5 by 1` reduction/fold range, literal-one temp fill, plus
  combiner, Part2 zero-init, and full `out store accum`.
- The proof now accepts shape-equivalent raw variants with renamed
  accumulator, temp, and loop/lambda identifiers, then canonicalizes to the
  same frontend/HIR programs `MemReduceOnes16` and `MemFoldOnes16`.
- Removed the generic exact-fixture fallback for those two raw adapters so the
  raw-island proof is the only Lab2 Part1/Part2 raw ingress.
- Tightened the raw proof identifier guard so `_` and core Scala reserved words
  cannot be treated as user-defined accumulator, temp, or lane names.
- Preserved HLS kernel text and manifest JSON equality against the canonical
  frontend programs for original, host-scaffold-edited, and renamed-local raw
  variants.

Proof added:
- `cargo test --locked -p spatial-rs-core parse_accel_accepts_shape_equivalent_raw_lab2_memory_reduction_names -- --nocapture`
- `cargo test --locked -p spatial-rs-core memreduce -- --nocapture`
- `cargo test --locked -p spatial-rs-core memfold -- --nocapture`
- `cargo test --locked -p spatial-rs-core lab2_memory_reduction_adapters -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part1_simple_memreduce_preserves_hls_and_manifest -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part2_simple_memfold_preserves_hls_and_manifest -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_mem_reductions -- --nocapture`

Boundary:
- This does not accept arbitrary Scala, arbitrary reducer bodies, generic
  `MemReduce` / `MemFold`, dynamic bounds, raw fill values beyond the EE109
  literal-one Part1/Part2 shape, banking, scheduling, or fresh EC2/Vitis
  evidence.
- The next Phase 3 compiler-internal slice is to extract rank-1 resolved
  indexed-write proof helpers for temp fill and zero-init checks.

## 2026-07-03 — Rust rewrite rank-1 memory-reduction write facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Continued Phase 3 by adding a reusable rank-1 indexed-write proof helper in
  the classifier layer.
- Wired `MemReduceFill` / `MemFoldFill` classification so temp fills and
  MemFold zero-init are now checked against resolved HIR index-use facts, not
  only textual `target[lane] := literal` shape.
- The helper requires a single rank-1 write to the resolved target symbol, the
  exact source index expression span, a direct lane read, no conditional or
  unsupported index fact, and an affine unit lane symbol.
- Kept generated Lab2 HLS/manifest behavior stable for renamed raw
  Part1/Part2 sources.

Proof added:
- `cargo test --locked -p spatial-rs-core rank1_indexed_write -- --nocapture`
- `cargo test --locked -p spatial-rs-core memreduce -- --nocapture`
- `cargo test --locked -p spatial-rs-core memfold -- --nocapture`
- `cargo test --locked -p spatial-rs-core mem_reduction_fill_near_misses_stay_fail_closed -- --nocapture`
- `cargo test --locked -p spatial-rs-core parse_accel_accepts_shape_equivalent_raw_lab2_memory_reduction_names -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_mem_reductions_renamed_locals_preserve_hls_and_manifest -- --nocapture`
- `cargo fmt --all -- --check`
- `cargo test --locked --quiet`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-rank1-write-plan`
- `git diff --check`

Boundary:
- This is a compiler-internal proof-helper extraction. It does not add new
  accepted Spatial syntax, alter generated HLS intentionally, retire the raw
  token-cursor adapter, or provide fresh EC2/Vitis evidence.

## 2026-07-03 -- Rust rewrite MemReduce/MemFold fill renderer extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Committed Rust repo change `138e86e` (`Extract MemReduce/MemFold fill
  renderer`).
- Moved the `MemReduceFill` / `MemFoldFill` HLS kernel renderer behind
  `MemReductionFillPlan` and the crate-private
  `spatial_rs_hls::mem_reduction_fill` helper module.
- Kept `emit.rs` responsible for `ProgramKind` dispatch,
  `HlsBodyPlan::MemReductionFill` matching, HLS parameter lookup, and
  host-harness/oracle rendering.
- The new helper owns signature/interface pragma rendering,
  accumulator/tmp local arrays, zero-fill, fill/accumulate, and final-store
  loop rendering.
- Generated dry-run artifacts for `MemReduceOnes16`, `MemReduceTwos16`,
  `MemFoldOnes16`, and `MemFoldTwos16` were compared against a clean detached
  baseline worktree at Rust commit `7f35974`; `kernel.cpp`, `harness.cpp`,
  `manifest.json`, `run_hls.tcl`, and `vitis-project.json` all matched exactly
  for all four programs.

Proof added:
- `cargo test -p spatial-rs-hls --locked mem_reduction_fill_kernel_frame -- --nocapture`
- `cargo test -p spatial-rs-hls --locked mem_reduction_fill_plan_preserves_kind_and_literal_fill -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen memreduce_fill_feature_emits_array_sum_loop_and_harness -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold_fill_feature_emits_array_sum_loop_and_harness -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen mem_reduction_literal_two_fill_features_emit_fill_value_and_pass_harness -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen mem_reduction_checked_ir_hls_keeps_length_parameterized -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part1_simple_memreduce_preserves_hls_and_manifest -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part2_simple_memfold_preserves_hls_and_manifest -- --nocapture`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-mem-reduction-fill-renderer-plan`
- `cargo test -p ee109-examples --locked --test emit_vitis_dry_run -- --nocapture`
- `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`
- `cargo fmt --all -- --check`
- `git diff --check`
- `cargo test --locked`
- `cargo clippy --workspace --all-targets --locked -- -D warnings`
- `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`

Boundary:
- This is local Rust test coverage plus dry-run artifact byte comparison. It
  does not run fresh EC2/Vitis, change the validation roster, change generated
  HLS or manifests, add new syntax, add generic `MemReduce` / `MemFold`, accept
  arbitrary reducer/fold bodies, prove dynamic bounds, banking, scheduling,
  performance, board timing, or make a new vendor-HLS claim.

## 2026-07-03 -- Rust rewrite scalar-family renderer extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Committed Rust repo change `7ddf17b` (`Extract scalar-family HLS
  renderers`).
- Moved the `ScalarAssign`, `ScalarReduce`, `ScalarFold`, and
  `ScalarSramTileFold` HLS kernel renderers behind the crate-private
  `spatial_rs_hls::scalar` helper module.
- Kept `emit.rs` responsible for `ProgramKind` dispatch, lowering
  orchestration, `HlsBodyPlan` matching, HLS parameter lookup for DRAM-input
  folds, dry-run project generation, and host-harness/oracle rendering.
- The new helper owns scalar kernel signature/interface pragma rendering,
  scalar-expression C++ rendering, arithmetic-series reduce loop rendering,
  direct rank-1 DRAM fold rendering, and SRAM tile-load fold loop rendering.
- Generated dry-run artifacts for `Lab1Part1RegExample`,
  `Lab1Part1RegThreeInputExample`, `ScalarAffine4`, `ScalarReduceSum16`,
  `ScalarFoldTileSum32`, and `SramTileFoldSum32` were compared against a clean
  detached baseline worktree at Rust commit `138e86e`; `kernel.cpp`,
  `harness.cpp`, `manifest.json`, `run_hls.tcl`, and `vitis-project.json` all
  matched exactly for all six programs. `ScalarMixedPrecedence` is not in the
  dry-run registry, so its expression-precedence canary remains covered by the
  exact m1 codegen/harness tests.

Proof added:
- `cargo test -p spatial-rs-hls --lib --locked scalar::tests -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen scalar -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen sram_tile_fold -- --nocapture`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-scalar-renderer-plan`
- `cargo test -p spatial-rs-hls --locked`
- `cargo test -p ee109-examples --locked --test emit_vitis_dry_run -- --nocapture`
- `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`
- `cargo fmt --all -- --check`
- `git diff --check`
- `cargo test --locked`
- `cargo clippy --workspace --all-targets --locked -- -D warnings`
- `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`

Boundary:
- This is local Rust test coverage plus dry-run artifact byte comparison only.
  It does not run fresh EC2/Vitis, change the validation roster, change
  generated HLS or manifests, add new accepted syntax, add new scalar/reduction
  or fold semantics, add generic `Reduce` / `Fold` / `MemReduce` / `MemFold`,
  accept arbitrary bodies, tail tiles, dynamic bounds, non-unit parallelism,
  scheduling, banking, performance, board timing, or make a new vendor-HLS
  claim.

## 2026-07-03 -- Rust rewrite LUT renderer extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Committed Rust repo change `edbb73e` (`Extract LUT HLS renderer`).
- Moved `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`, and
  `LutBiasLookup` kernel rendering behind the existing `Lut2dLookupPlan` and
  the new crate-private `spatial_rs_hls::lut` helper module.
- Kept `emit.rs` responsible for `ProgramKind` dispatch,
  `HlsBodyPlan::Lut2dLookup` matching, lowering orchestration, dry-run project
  generation, and LUT host-harness/oracle rendering.
- The helper owns extern signature rendering, scalar/control AXI-lite pragma
  rendering, static row-major `int` LUT literal rendering, `(row * cols) + col`
  lookup text, and scalar output store rendering.
- Generated dry-run artifacts for `Lab2Part4LUT`,
  `Lab2Part4LUTNonSquareExample`, and `LutBiasLookup` were compared against a
  clean detached baseline worktree at Rust commit `7ddf17b`; `kernel.cpp`,
  `harness.cpp`, `manifest.json`, `run_hls.tcl`, and `vitis-project.json` all
  matched exactly for all three programs.

Proof added:
- `cargo test -p spatial-rs-hls --locked --lib lut_kernel_frame -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen lut -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test vitis_validation captured_lut_lookup_vitis_evidence_parses_for_adapter_baseline_and_features -- --nocapture`
- `cargo run -p ee109-examples --locked --bin emit-vitis-dry-run`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-lut-renderer-plan`
- `cargo test -p spatial-rs-hls --locked`
- `cargo test -p ee109-examples --locked --test emit_vitis_dry_run -- --nocapture`
- `cargo test -p ee109-examples --locked --test run_vitis_validation -- --nocapture`
- `cargo fmt --all -- --check`
- `git diff --check`
- `cargo test --locked`
- `cargo clippy --workspace --all-targets --locked -- -D warnings`
- `RUSTDOCFLAGS='-D warnings' cargo doc --workspace --locked --no-deps --document-private-items`

Boundary:
- This is local Rust test coverage plus dry-run artifact byte comparison only.
  It does not run fresh EC2/Vitis, change the validation roster, change
  generated HLS or manifests, add new syntax, change frontend/HIR/classifier
  behavior, retire raw Lab2 LUT wrappers, add generic LUT/table indexing,
  support multiple LUTs, computed/swapped indices, arbitrary scalar
  expressions, dynamic dimensions/bounds, rank-1/rank-3 LUTs, non-`Int` or
  FixPt LUTs, performance, board timing, or make a new vendor-HLS claim.

## 2026-07-03 -- Rust rewrite raw-adapter retirement current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Vitis source snapshot is clean Rust commit `a30ec96` (`Support Cargo 1.75
  CLI integration tests`); the imported evidence/docs were later committed in
  the Rust repo as `efca04c`.
- The preceding raw-ingress cleanup retired the raw Lab2 LUT wrappers at
  `702d181` and the raw Lab2 FSM-alt wrapper at `1e564a7`, while preserving the
  canonical LUT/FSM payloads, validation roster, generated HLS, manifests, and
  host harnesses.
- The CLI integration tests now work on the EC2 Rust/Cargo 1.75 toolchain by
  falling back from missing `CARGO_BIN_EXE_*` env vars to `cargo run -p
  ee109-examples --locked --bin <tool> --`.
- Re-ran the full 35-program EE109 validation roster on EC2/Vitis 2025.1 from
  `/home/ubuntu/spatial-rs-runs/raw-ingress-retire-35-a30ec96/spatial-rs`.
- Durable evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-raw-ingress-retire-a30ec96-35-program/`.
- The copied evidence validates locally with
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-03-raw-ingress-retire-a30ec96-35-program --mode both`.

Proof:
- Remote `cargo test -p ee109-examples --locked` passed under
  `cargo 1.75.0` / `rustc 1.75.0`.
- Remote Vitis command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-raw-ingress-retire-35-a30ec96`
- Vitis summary result: all 35 kernels passed with `returncode=0`,
  `csim=true`, and `csynth=true`.
- Captured artifacts: `summary-both.md`, `summary-both.json`, 35 Vitis logs,
  35 csynth reports, and 35 sidecar Tcl files.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 35-program
  Rust rewrite roster at commit `a30ec96`.
- It does not prove board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM/stencil support, automatic banking inference, broader `par` inference,
  II=1 for every loop, or performance optimality.

## 2026-07-03 -- Rust rewrite Tile-K partial schedule facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `29e6b52` (`Check Tile-K partial schedule facts`) makes the
  Tile-K fold-schedule proof consume resolver-owned `ResolvedHir::LoopDomain`
  facts for the partial-product loops.
- The classifier still keeps the existing structural MemFold shape guard first,
  but the accepted partial schedule now walks from the partial product
  assignment effect to its enclosing column loop, parent row loop, and parent
  fold-K loop, then checks the resolved loop-index symbols, canonical end-bound
  symbols, serial fold schedule, and fixed serial or Part6 `par 2` / `par 16`
  factors.
- Added fail-closed coverage for crossed resolver facts where the source syntax
  still says `par 2` but the supplied resolved loop-domain facts say `par 4`.
- Extended the helper coverage to include the serial and scheduled
  row/column/K-tail Tile-K profiles.
- Updated repo docs and the fixture matrix to record this as local
  fact-consumption hardening, not a new HLS feature.

Proof:
- Red/green focused test:
  `cargo test --locked -p spatial-rs-core tile_k_fold_schedule_helper_rejects_resolved_partial_par_mismatch -- --nocapture`.
- Focused schedule/profile checks:
  `cargo test --locked -p spatial-rs-core tile_k_fold_schedule_helper -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tile_k_contract_accepts_all_current_profiles -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-core checked_ir_accepts_exact_part6_tile_k_memfold_schedule -- --nocapture`.
- Full local verification:
  `cargo fmt --all -- --check`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k -- --nocapture`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  and `git diff --check`.

Boundary:
- This is local compiler/classifier trust reduction only.
- It does not change accepted syntax, checked IR payloads, validation roster,
  generated HLS C++, manifests, host harnesses, imported Vitis evidence, or the
  35-program vendor-HLS claim from source snapshot `a30ec96`.
- It does not imply generic Spatial `MemFold`, generic GEMM, generic `par`,
  automatic banking inference, arbitrary K/row/column tails, broad Scala source
  compatibility, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Lab3 local-window facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c44be2a` (`Check Lab3 local-window facts`) makes the
  Lab3/Stencil2d classifier consume resolver-owned facts before admitting the
  existing narrow Sobel local-window payload.
- The accepted Lab3 and `Stencil2d v0` surfaces are unchanged, but admission now
  checks the resolved row/column/shift loop-domain tree, row-range
  line-buffer-load and row-store facts, `RegFile` reset/shift effects,
  line-buffer shift reads, line-output writes, Sobel/window reduction read
  groups, and const-backed range ends.
- The root cause during implementation was that valid range ends such as `COLS`
  resolve to constant value `16` with a backing constant symbol; the gate now
  accepts resolved constant values whether they came from literals or named
  constants.
- Updated the Rust docs and fixture matrix to describe this as local
  fact-consumption hardening, not generic stencil support or new vendor
  evidence.

Proof:
- Focused red/green checks:
  `cargo test --locked -p spatial-rs-core stencil2d_local_window_fact_gate -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_alias_named_stencil2d_sobel_feature -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_local_raw_lab3_convolution -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-core raw_lab3_part1_convolution_near_misses_fail_closed -- --nocapture`.
- Full local verification:
  `cargo fmt --all -- --check`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3 -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  and `git diff --check`.

Boundary:
- This is local compiler/classifier trust reduction only.
- It does not change accepted syntax, checked IR payloads, validation roster,
  generated HLS C++, manifests, host harnesses, imported Vitis evidence, or the
  35-program vendor-HLS claim from source snapshot `a30ec96`.
- It does not imply generic Spatial `LineBuffer`, `RegFile`, `Reduce`, generic
  stencil scheduling, arbitrary `par`, dynamic dimensions, broad Scala source
  compatibility, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite raw GEMM class-island guard

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `d8c8879` (`Reject ambiguous raw GEMM class islands`) tightens
  the quarantined raw Lab2 Part5/Part6 GEMM ingress.
- The raw fixed GEMM source proof now requires exactly one raw `@spatial class`
  declaration before trusting the normalized single-`Accel` island. Duplicate
  `Lab2Part5GEMM` class declarations, or mixed Part5/Part6 class declarations
  in one raw file, are rejected even if one accel body still matches the known
  fixture.
- Accepted Part5/Part6 profiles, generated Lab2-like frontend source, checked
  payloads, generated HLS C++, manifests, validation membership, and vendor
  evidence are unchanged.
- Updated the Rust planning docs and fixture matrix to record the single-class
  raw-island boundary.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_adapters_reject_ambiguous_raw_class_islands -- --nocapture`.
- Focused fixed-GEMM checks:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`,
  `cargo test --locked -p spatial-rs-core raw_lab2_part5_fixed_wrapper_near_misses_fail_closed -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part5_gemm_fixed_32 -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-core raw_lab2_part6_fixed_wrapper_near_misses_fail_closed -- --nocapture`.
- Broader local verification:
  `cargo fmt --all -- --check`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  and `git diff --check`.

Boundary:
- This is local raw-ingress hardening only.
- It does not add accepted Scala syntax, change Rust-subset syntax, change
  checked IR, change emitted HLS/manifests/harnesses, add validation-program
  membership, or make a fresh vendor-HLS claim.
- It does not imply broad Scala source compatibility, generic Spatial `MemFold`,
  arbitrary GEMM shapes, generic `par`, inferred banking, board execution,
  Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite shared rank-2 tile-copy facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `6a4c4ae` (`Share rank2 tile copy fact checks`) removes duplicate
  Tile-K C preload/store affine fact checks by routing them through the existing
  `rank2_tile_copy_facts_match` helper.
- The helper is now shared by the non-outer-K MemFold tile-copy path and the
  Tile-K C preload/store path. It still proves local row/column lanes,
  global `tile*TILE + lane` affine forms, resolved loop-symbol identity, and
  const-backed tile-stride provenance.
- Updated the Rust plan/architecture docs to record this as helper reuse, not a
  new feature.

Proof:
- Focused checks:
  `cargo test --locked -p spatial-rs-core tile_k_c_preload_fact_matcher -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tile_k_c_store_fact_matcher -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-core dense2d_memfold_preload_fact_matcher -- --nocapture`.
- Broader local verification:
  `cargo fmt --all -- --check`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k -- --nocapture`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  and `git diff --check`.

Boundary:
- This is local classifier refactoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program vendor-HLS claim from source snapshot `a30ec96`.
- It does not imply generic rank-2 memory effects, alias analysis, generic
  GEMM, automatic banking, broad `par` semantics, board execution, Vivado
  implementation, or timing closure.

## 2026-07-03 -- Rust rewrite LUT proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `7aa1cca` (`Record LUT proof facts`) factors the LUT
  adapter/feature classifiers through a private proof object before checked IR
  construction.
- The proof records the accepted program kind, LUT table, scalar output, scalar
  input, row/column index roles, table dimensions, and row-major literal
  values for both the reserved Lab2 square/non-square adapters and the reusable
  non-lab `LutLookup v0` feature path.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift frontend/classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core lut_feature_proof_records_roles_dims_and_values -- --nocapture`.
- Focused LUT checks:
  `cargo test --locked -p spatial-rs-core lut_feature_proof_records_roles_dims_and_values -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lut_adapter_proof_records_reserved_lab2_shape -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lut -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen lut -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic LUT support, arbitrary table expressions, runtime
  bounds checks, dynamic dimensions, non-`Int` LUTs, board execution, Vivado
  implementation, or timing closure.

## 2026-07-03 -- Rust rewrite SRAM tile-fold proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `6309745` (`Record SRAM tile fold proof facts`) factors the
  `ScalarSramTileFold v0` classifier through a private proof object before
  checked IR construction.
- The proof records the accepted rank-1 DRAM input, scalar output, local SRAM
  tile, outer/inner indices, fixed length, and tile size for the narrow
  `SramTileFoldSum32` canary.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift frontend/classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core scalar_sram_tile_fold_proof_records_roles_indices_and_bounds -- --nocapture`.
- Focused SRAM tile-fold checks:
  `cargo test --locked -p spatial-rs-core scalar_sram_tile_fold_proof_records_roles_indices_and_bounds -- --nocapture`,
  `cargo test --locked -p spatial-rs-core sram_tile_fold -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen sram_tile_fold -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic Spatial `Fold`, arbitrary local-memory effects,
  tail tiles, dynamic bounds, non-`Int` data, board execution, Vivado
  implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Control/FSM proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `3706bd8` (`Record control FSM proof facts`) renames the internal
  Control/FSM classifier shape object into an explicit private proof object and
  adds direct proof tests.
- The proof records the accepted output DRAM, scratch SRAM, local register,
  FSM state variable, and body kind before the classifier chooses either the
  checked Lab2 fixture adapter or reusable `ControlFsm v0` IR.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift frontend/classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core control_fsm_proof_records_feature_roles_and_body_kind -- --nocapture`.
- Focused Control/FSM checks:
  `cargo test --locked -p spatial-rs-core control_fsm_proof_records_feature_roles_and_body_kind -- --nocapture`,
  `cargo test --locked -p spatial-rs-core control_fsm_proof_records_alt_lab2_body_kind -- --nocapture`,
  `cargo test --locked -p spatial-rs-core control_fsm -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen control_fsm -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic FSM support, arbitrary control effects, dynamic
  state-machine bounds, broader Scala source compatibility, board execution,
  Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite fixed GEMM frontend proof boundary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `5a8b1e6` (`Record fixed GEMM frontend proof facts`) extends the
  private fixed Lab2 GEMM source proof so it carries the emitted quarantined
  frontend source, instead of recomputing that source at the raw-adapter match
  boundary.
- The proof now owns all three adapter facts for the accepted raw Part5/Part6
  fixed GEMM wrappers: static shell/profile, normalized single-`Accel` island,
  and generated Lab2-like frontend source.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift source-adapter foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_carries_frontend_boundary -- --nocapture`.
- Focused fixed GEMM/raw Lab2 checks:
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_carries_frontend_boundary -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_records_profile_target_and_accel_island -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part5_gemm_fixed_32 -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core raw_lab2_part5_fixed_wrapper_near_misses_fail_closed -- --nocapture`,
  `cargo test --locked -p spatial-rs-core raw_lab2_part6_fixed_wrapper_near_misses_fail_closed -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local source-adapter proof factoring only.
- It does not change accepted syntax, normalized frontend text, checked IR
  payloads, generated HLS C++, manifests, host harnesses, validation membership,
  imported Vitis evidence, or the 35-program current-head vendor-HLS claim from
  source snapshot `6a4c4ae`.
- It does not imply generic Spatial GEMM support, arbitrary `runtimeArgs`,
  arbitrary K tails beyond the named canaries, broad Scala source compatibility,
  board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite non-outer-K Dense2d MemFold proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `fb47d9b` (`Record dense MemFold proof facts`) wraps the
  non-outer-K `Dense2dTileMemFold v0` classifier path in a private proof object
  before reconstructing the same checked IR.
- The proof records accepted source-shape facts, optional row/column bounds,
  the shared element type, split-C vs in-place-C mode, and the checked MemFold
  payload.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof_records_source_shape_bounds_and_payload -- --nocapture`.
- Focused Dense2d MemFold checks:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof_records_source_shape_bounds_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic Spatial `MemFold`, arbitrary GEMM schedules,
  banking inference, arbitrary fixed-point widths, K tiling on this
  non-outer-K path, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Dense2d DotAccum proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `f38738a` (`Record dense DotAccum proof facts`) wraps the
  `Dense2dTileDotAccum v0` classifier path in a private proof object before
  reconstructing the same checked IR.
- The proof records accepted source-shape facts and the checked DotAccum
  payload for the fixed `MatrixTileAccum4x6x5` family.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core dense2d_dot_accum_proof_records_source_shape_and_payload -- --nocapture`.
- Focused DotAccum checks:
  `cargo test --locked -p spatial-rs-core dense2d_dot_accum_proof_records_source_shape_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dot_accum -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_dot_accum -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen dot_accum -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic GEMM support, fixed-point DotAccum, tail tiles,
  K tiling, `MemFold`, `par`, banking inference, board execution, Vivado
  implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Dense2d scalar-scale proof facts

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c411362` (`Record dense scale proof facts`) wraps the
  `Dense2dTileScalarMul v0` classifier path in a private proof object before
  reconstructing the same checked IR.
- The proof records accepted source-shape facts and the checked scalar-scale
  payload for the fixed `MatrixTileScale4x6` family.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift classifier foundation slice.

Proof:
- Red/green focused check:
  `cargo test --locked -p spatial-rs-core dense2d_tile_scalar_mul_proof_records_source_shape_and_payload -- --nocapture`.
- Focused scalar-scale checks:
  `cargo test --locked -p spatial-rs-core dense2d_tile_scalar_mul_proof_records_source_shape_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_tile_scalar -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tiled_int_scale -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen scale -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic rank-2 local-memory lowering, tail tiles,
  fixed-point scalar scale, GEMM semantics, `MemFold`, `par`, banking inference,
  board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Dense2d MemFold source-shape proof split

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `8e8bffc` (`Split dense MemFold source proof`) factors the
  non-outer-K `Dense2dTileMemFold v0` source-shape admission into a dedicated
  helper before the existing phase/bounds matcher consumes the proof context.
- The helper records the accepted DRAM/SRAM roles, dimensions, shared element
  type, and split-C vs in-place-C mode while preserving the same checked IR
  reconstruction path.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_source_shape_helper_records_roles_dims_and_c_mode -- --nocapture`
  failed first because `prove_dense2d_tile_memfold_source_shape` did not exist.
- Focused Dense2d MemFold checks:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_source_shape_helper_records_roles_dims_and_c_mode -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof_records_source_shape_bounds_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`.
- Broader local verification:
  `cargo fmt --all`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic Spatial `MemFold`, arbitrary GEMM schedules,
  banking inference, arbitrary fixed-point widths, K tiling on this
  non-outer-K path, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Dense2d MemFold phase proof split

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `9363677` (`Split dense MemFold phase proof`) factors the
  non-outer-K `Dense2dTileMemFold v0` tile-row/tile-column phase spine and
  exact/tail bound admission into a dedicated helper.
- The source-shape helper and phase/bounds helper now run before the existing
  resolved access matching, keeping the checked IR reconstruction path the
  same.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_phase_spine_helper_records_loops_phases_and_bounds -- --nocapture`
  failed first because `prove_dense2d_tile_memfold_phase_spine` did not exist.
- Focused Dense2d MemFold checks:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_phase_spine_helper_records_loops_phases_and_bounds -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof_records_source_shape_bounds_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`.
- Broader local verification:
  `cargo fmt --all`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic Spatial `MemFold`, arbitrary GEMM schedules,
  banking inference, arbitrary fixed-point widths, K tiling on this
  non-outer-K path, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite Dense2d MemFold access proof split

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c3e3be5` (`Split dense MemFold access proof`) factors the
  non-outer-K `Dense2dTileMemFold v0` resolved access-role matching into a
  dedicated helper after the source-shape and phase/bounds helpers.
- The helper owns LHS/RHS/C preload, fold, and store matching in the original
  syntax-first/facts-second order, preserves fold-before-store diagnostics, and
  returns only row/column/K lane roles plus their bounds for payload
  construction.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Subagent review:
- A `gpt-5.5` `xhigh` explorer reviewed the proposed helper boundary and
  highlighted diagnostic-order risk around fold-before-store ordering.
- The implementation preserves the original order inside the helper and keeps
  split-C preload versus output-store ports distinct.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_access_roles_helper_records_shared_lanes_and_bounds -- --nocapture`
  failed first because `prove_dense2d_tile_memfold_access_roles` did not exist.
- Focused Dense2d MemFold checks:
  `cargo test --locked -p spatial-rs-core dense2d_memfold_access_roles_helper_records_shared_lanes_and_bounds -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold_proof_records_source_shape_bounds_and_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense2d_memfold -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold -- --nocapture`,
  `cargo test -p spatial-rs-core --locked classifies_rank2_tile_memfold -- --nocapture`,
  `cargo test -p spatial-rs-core --locked rank2_tile_memfold_near_misses_fail_closed -- --nocapture`,
  `cargo test -p spatial-rs-core --locked rank2_tile_memfold_tail_near_misses_fail_closed -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_memfold_4x6x5_feature_emits_c_preload_partial_fold_and_harness -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_memfold_tail_5x7x5_feature_compiles_harness -- --nocapture`,
  and `cargo test -p spatial-rs-hls --locked --test m1_codegen rank2_tile_memfold_bulk_io_preserves_exact_hls_and_manifest -- --nocapture`.
- Broader local verification:
  `cargo fmt --all`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, imported Vitis evidence, or
  the 35-program current-head vendor-HLS claim from source snapshot `6a4c4ae`.
- It does not imply generic Spatial `MemFold`, arbitrary GEMM schedules,
  banking inference, arbitrary fixed-point widths, K tiling on this
  non-outer-K path, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite c3e3be5 current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `c3e3be5` (`Split dense MemFold access proof`) was copied to
  the EC2 Vitis host and rerun through the full current 35-program validation
  roster with Vitis 2025.1.
- Rust commit `231e072` (`Record c3e3be5 Vitis evidence`) imports the captured
  evidence under
  `docs/vitis-validation/2026-07-03-current-head-c3e3be5-35-program/`,
  updates README/architecture/MVP/fixture docs to name that folder as the
  active vendor-stability anchor, and updates the repo-local evidence-validator
  test to cover the new checkpoint.

EC2/Vitis proof:
- Host: `[ec2-host — see private/ec2-lane.md]`, with
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`, `rustc 1.75.0`, and
  `cargo 1.75.0`.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/current-head-c3e3be5/spatial-rs`.
- Remote command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-current-head-c3e3be5 --settings /tools/Xilinx/2025.1/Vitis/settings64.sh`.
- Remote summary: mode `both`, execution `execute`, 35 kernels, 0 failures;
  every kernel reported Vitis `csim_design` and `csynth_design` success.

Local proof after import:
- `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_c3e3be5_checkpoint -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_c3e3be5_as_current_vendor_anchor -- --nocapture`
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-03-current-head-c3e3be5-35-program --mode both`
- `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`
- `cargo test --locked -p ee109-examples`
- `cargo test --locked -p spatial-rs-core`
- `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`
- `cargo fmt --all -- --check`
- `git diff --check`

Boundary:
- This is a vendor-HLS stability refresh for the existing 35-program roster
  after compiler-foundation proof factoring.
- It proves Vitis C simulation and HLS synthesis for those exact kernels only.
- It does not claim board execution, Vivado implementation/place-and-route,
  timing closure, performance optimality, generic Spatial compatibility,
  generic `MemFold`, arbitrary GEMM schedules, dynamic dimensions, or automatic
  banking/scheduling inference.

## 2026-07-03 -- Rust rewrite Dram2d copy proof boundary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `b546033` (`Record Dram2d copy proof boundary`) renames the
  accepted `Dram2dCopy v0` shape record into a private proof boundary and adds
  a direct unit test for the accepted input/output roles, row/column loop
  indices, and static row/column bounds.
- The checked IR payload and HLS-facing feature remain the same: one rank-2
  DRAM input, one matching rank-2 DRAM output, nested static row/column loops,
  and direct row-major copy assignment.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core dram2d_copy_proof_records_ports_indices_and_bounds -- --nocapture`
  failed first because `dram2d_copy_proof` did not exist.
- Focused checks:
  `cargo test --locked -p spatial-rs-core dram2d_copy_proof_records_ports_indices_and_bounds -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_copy -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_copy_4x6_feature_emits_parameterized_rank2_copy_and_harness -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_row_major_copy_kernel_uses_cols_as_rank2_flatten_stride -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls rank2_copy -- --nocapture`.
- Broader local verification:
  `cargo fmt --all`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  `git diff --check`,
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_c3e3be5_as_current_vendor_anchor -- --nocapture`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, or imported Vitis evidence.
- The active vendor-HLS evidence anchor remains
  `docs/vitis-validation/2026-07-03-current-head-c3e3be5-35-program/`;
  commit `b546033` itself has not been rerun on EC2/Vitis yet.
- It does not imply generic rank-2 memory lowering, arbitrary affine index
  analysis, dynamic dimensions, board execution, Vivado implementation, or
  timing closure.

## 2026-07-03 -- Rust rewrite b5460335 current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `b546033` (`Record Dram2d copy proof boundary`) was copied to
  the EC2 Vitis host and rerun through the full current 35-program validation
  roster with Vitis 2025.1.
- Rust commit `6918e94` (`Record b5460335 Vitis evidence`) imports the captured
  evidence under
  `docs/vitis-validation/2026-07-03-current-head-b5460335-35-program/`,
  updates README/architecture/MVP/fixture docs to name that folder as the
  active vendor-stability anchor, and updates the repo-local evidence-validator
  test to cover the new checkpoint.

EC2/Vitis proof:
- Host: `[ec2-host — see private/ec2-lane.md]`, with
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`, `rustc 1.75.0`, and
  `cargo 1.75.0`.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/current-head-b5460335/spatial-rs`.
- Remote command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-current-head-b5460335 --settings /tools/Xilinx/2025.1/Vitis/settings64.sh`.
- Remote result: every emitted kernel line reported `returncode=0`,
  `csim=true`, and `csynth=true`; the imported local validator confirmed
  mode `both`, execution `execute`, and 35 kernels.

Local proof after import:
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-03-current-head-b5460335-35-program --mode both`
- `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_b5460335_checkpoint -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_b5460335_as_current_vendor_anchor -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`
- `cargo test --locked -p ee109-examples`
- `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`
- `cargo fmt --all -- --check`
- `git diff --check`

Boundary:
- This supersedes the prior local-only `b546033` note: that exact head now has
  imported EC2/Vitis `csim_design` and `csynth_design` evidence for the same
  35-program roster.
- It proves vendor C simulation and HLS synthesis for those exact kernels only.
- It does not claim board execution, Vivado implementation/place-and-route,
  timing closure, performance optimality, generic Spatial compatibility,
  arbitrary rank-2 memory lowering, dynamic dimensions, or automatic
  banking/scheduling inference.

## 2026-07-03 -- Rust rewrite Dense1d proof boundary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `ee145d4` (`Record Dense1d proof boundary`) factors
  `Dense1dScalarMul v0` classifier admission through a private
  `Dense1dScalarMulProof` before checked IR construction.
- The proof records the accepted input/scalar/output roles, input/output tile
  roles, source loop indices, static length evidence when it resolves, and the
  resolved tile size.
- A regression test keeps the old behavior that the canonical Lab1 dense
  adapter may use noncanonical source loop names; the proof records those names
  without requiring them to be `i` and `ii`.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Subagent review:
- A `gpt-5.5` `xhigh` explorer reviewed the Dense1d boundary and caught the
  initial loop-name narrowing risk before broad verification.
- The final implementation removes that narrowing and preserves the old
  adapter acceptance boundary.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core dense1d_scalar_mul_proof_records_roles_indices_and_tile_bound -- --nocapture`
  failed first because `dense1d_scalar_mul_proof` did not exist.
- Follow-up red check after subagent review:
  `cargo test --locked -p spatial-rs-core dense1d_ -- --nocapture`
  failed because `Dense1dScalarMulProof` did not yet carry optional `len`.
- Focused checks:
  `cargo test --locked -p spatial-rs-core dense1d_ -- --nocapture`,
  `cargo test --locked -p spatial-rs-core dense -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen dense -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls dense -- --nocapture`.
- Broader local verification:
  `cargo fmt --all`,
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  `git diff --check`,
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_b5460335_as_current_vendor_anchor -- --nocapture`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, or imported Vitis evidence.
- The active vendor-HLS evidence anchor remains
  `docs/vitis-validation/2026-07-03-current-head-b5460335-35-program/`;
  commit `ee145d4` itself has not been rerun on EC2/Vitis yet.
- It does not imply generic rank-1 scheduling, tail tiles, dynamic bounds,
  commuted multiply support, broader Dense1d lowering, board execution, Vivado
  implementation, or timing closure.

## 2026-07-03 -- Rust rewrite FIFO proof boundary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c862e57` (`Record FIFO proof boundary`) factors
  `Fifo1dTileScalarMul v0` classifier admission through a private
  `FifoTileScalarMulProof` before checked IR construction.
- The proof records accepted input/scalar/output roles, input/output FIFO
  memories, source loop indices, static length/depth facts, and ordered
  dequeue/enqueue resolver evidence.
- The implementation preserves the cheap `HirFacts` structural FIFO gate and
  the existing resolver effect rules: exactly one input dequeue before one
  output enqueue, same parent block, loop depth two, and no conditionals.
- Updated the Rust README and architecture/MVP notes to record this as a
  no-HLS-drift compiler-foundation slice.

Subagent review:
- A `gpt-5.5` `xhigh` explorer recommended FIFO proof factoring over
  `MemReductionShape` factoring because memory reductions already had a
  shape/proof object and FIFO still mixed admission, resolver facts, port
  checks, and checked IR construction in one classifier.
- The final implementation follows that recommendation and keeps HLS lowering
  untouched.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core fifo_tile_scalar_mul_proof_records_roles_indices_bounds_and_effects -- --nocapture`
  failed first because `fifo_tile_scalar_mul_proof` did not exist.
- Focused checks:
  `cargo test --locked -p spatial-rs-core fifo_tile_scalar_mul_proof -- --nocapture`,
  `cargo test --locked -p spatial-rs-core fifo -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen fifo -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_b5460335_as_current_vendor_anchor -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  and `git diff --check`.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, or imported Vitis evidence.
- The active vendor-HLS evidence anchor remains
  `docs/vitis-validation/2026-07-03-current-head-b5460335-35-program/`;
  commit `c862e57` itself has not been rerun on EC2/Vitis yet.
- It does not imply generic FIFO support, AXI streams, stream ports,
  back-pressure modeling, arbitrary producer/consumer scheduling, tail tiles,
  dynamic depths, board execution, Vivado implementation, or timing closure.

## 2026-07-03 -- Rust rewrite c862e57a current-head Vitis refresh

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c862e57a` was rerun on EC2/Vitis after the accumulated
  non-outer-K `Dense2dTileMemFold` proof-helper cleanup, the `Dram2dCopy`
  proof-boundary cleanup, and the follow-up Dense1d/FIFO proof-boundary
  cleanups.
- Imported evidence is captured in
  `docs/vitis-validation/2026-07-03-current-head-c862e57a-35-program/`.
- Rust docs/tests now promote this directory as the active current-head
  vendor-stability anchor, while the scheduled row/column/K-tail run remains
  the latest roster-expansion anchor.

Remote proof:
- EC2 host: `[ec2-host — see private/ec2-lane.md]`.
- Remote source directory:
  `/home/ubuntu/spatial-rs-runs/current-head-c862e57/spatial-rs`.
- Command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-current-head-c862e57`.
- Result: the runner exited with code 0; all 35 kernels in
  `summary-both.json` report `status=passed`, `returncode=0`,
  `csim_passed=true`, and `csynth_finished=true`.

Local verification:
- `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-03-current-head-c862e57a-35-program --mode both`
- `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_c862e57a_checkpoint -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_c862e57a_as_current_vendor_anchor -- --nocapture`
- `cargo test --locked -p spatial-rs-hls --test vitis_validation -- --nocapture`
- `cargo test --locked -p spatial-rs-core`
- `cargo test --locked -p ee109-examples`
- `cargo test --locked -p spatial-rs-hls`
- `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`
- `cargo fmt --all -- --check`
- `git diff --check`

Boundary:
- This refresh proves Vitis 2025.1 C simulation and HLS synthesis for the exact
  35-program EE109 MVP roster only.
- It does not add validation-program membership or claim new emitted-HLS
  behavior beyond the current source snapshot.
- It does not claim board execution, Vivado implementation/place-and-route,
  timing closure, performance optimality, generic Spatial compatibility,
  arbitrary FIFO/stream support, broad rank-1/rank-2 lowering, automatic
  banking/scheduling inference, or completion of the full Spatial rewrite.

## 2026-07-03 -- Rust rewrite shared rank-1 proof shell

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `2f527aa4` (`Share rank-1 classifier proof shell`) records a
  local no-HLS-drift rank-1 classifier cleanup.
- `Dense1dScalarMul v0` and `Fifo1dTileScalarMul v0` now share a
  `rank1_dram_scalar_ports` helper for the common rank-1 DRAM input, scalar
  input, and rank-1 DRAM output ABI.
- They also share a private `Rank1TiledIoProof` in `tiled1d.rs` for the common
  local-memory, unit-stride load, inner-loop bound, and unit-stride store
  shell.
- Dense1d still owns its indexed scalar-multiply compute proof. FIFO still
  owns its staged/direct enqueue-dequeue compute proof and resolver-backed
  ordered effect proof.
- Updated the Rust README, EE109 MVP plan, architecture note, superpowers
  roadmap, and this vault roadmap/progress log.

Subagent review:
- Three `gpt-5.5` `xhigh` subagents reviewed the next compiler-foundation
  direction before implementation.
- Consensus was to do the shared rank-1 Dense/FIFO proof shell first, keep it
  private to `tiled1d.rs`, and postpone the rank-2 tile-copy role helper as the
  next natural slice.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core rank1_tiled_io_proof -- --nocapture`
  failed first because `rank1_tiled_io_proof` did not exist.
- Focused checks:
  `cargo test --locked -p spatial-rs-core rank1_tiled_io_proof -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tiled1d -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank1_dram_scalar_ports -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen dense -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen fifo -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_c862e57a_as_current_vendor_anchor -- --nocapture`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, checked IR payloads, generated HLS C++,
  manifests, host harnesses, validation membership, or imported Vitis evidence.
- The active vendor-HLS evidence anchor remains
  `docs/vitis-validation/2026-07-03-current-head-c862e57a-35-program/`;
  this rank-1 helper slice has not been rerun on EC2/Vitis yet.
- It does not imply generic rank-1 scheduling, tail tiles, dynamic bounds,
  generic FIFO/stream support, board execution, Vivado implementation, timing
  closure, or completion of the full Spatial rewrite.

## 2026-07-03 -- Rust rewrite shared rank-2 tile-copy role proof

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `1ac50545f11332acf06d4887ad791fa1d44ac906` (`Share rank-2
  tile-copy role proof`) records a local no-HLS-drift rank-2 classifier cleanup.
- `Dense2dTileMemFold v0` and `Dense2dTileKMemFold v0` now share a private
  `Rank2TileCopyRole` / `Rank2TileCopyRoleSpec` helper for the common
  local-write/global-read and global-write/local-read tile-copy fact roles.
- The helper is wired only into the non-outer-K MemFold C preload/store path and
  the Tile-K C preload/store path. Feature-local syntax gates, phase-spine
  checks, source-shape proofs, fold/update proofs, and payload construction stay
  outside the helper.
- Updated the Rust README, EE109 MVP plan, architecture note, superpowers
  roadmap, and this vault roadmap/progress log.

Subagent review:
- A `gpt-5.5` `xhigh` read-only review subagent found no blocking issues.
- The review confirmed that feature-local syntax gates still run before the
  shared helper, docs keep `c862e57a` as the active vendor-HLS evidence anchor,
  and `.codex/` remains private/untracked.

Proof:
- Red check:
  `cargo test --locked -p spatial-rs-core rank2_tile_copy_role -- --nocapture`
  failed first because the helper did not exist.
- Focused checks:
  `cargo test --locked -p spatial-rs-core rank2_tile_copy_role -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tiled2d -- --nocapture`,
  `cargo test --locked -p spatial-rs-core rank2_tile_memfold -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tile_k_contract -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen tile_memfold -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core`,
  `cargo test --locked -p ee109-examples`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_c862e57a_as_current_vendor_anchor -- --nocapture`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `cargo fmt --all -- --check`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is local classifier proof factoring only.
- It does not change accepted syntax, diagnostics intent, checked IR payloads,
  generated HLS C++, manifests, host harnesses, validation membership, or
  imported Vitis evidence.
- The active vendor-HLS evidence anchor remains
  `docs/vitis-validation/2026-07-03-current-head-c862e57a-35-program/`;
  this rank-2 helper slice has not been rerun on EC2/Vitis yet.
- It does not imply generic rank-2 memory lowering, alias analysis, broader
  GEMM/MemFold support, board execution, Vivado implementation, timing closure,
  or completion of the full Spatial rewrite.

## 2026-07-04 -- Rust rewrite raw Lab2 GEMM row/column/K-tail adapter

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `c4f8eea6a8c9ef9c9e20c9bf7f92526568859ec9` (`Accept raw Lab2
  row-col K-tail GEMM`) extends the quarantined raw `Lab2Part5GEMM` and
  `Lab2Part6GEMM` source adapter to the exact lab runtime profile
  `runtimeArgs = "33 35 34"`.
- Part5 now maps to the existing
  `MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34` checked payload and
  neutral Tile-K profile `SerialRowColKTail`.
- Part6 now maps to the existing
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`
  checked payload and neutral Tile-K profile `Part6ScheduledRowColKTail`.
- The adapter remains token-stream quarantined and exact: near-miss dimensions,
  wrong Part6 par factors, dynamic dimensions, broader K/row/column tails,
  generic `par`, inferred banking, and broad Scala source compatibility remain
  fail-closed.
- Updated the Rust README, fixture matrix, EE109 MVP plan, architecture note,
  superpowers roadmap, vault stability matrix, vault roadmap, and this progress
  log.

Subagent review:
- A `gpt-5.5` `xhigh` read-only review subagent found no blocking, important,
  or minor issues.
- The reviewer confirmed that exact `runtimeArgs` matching is still limited to
  the named strings, the new profile maps only to the existing row/column/K-tail
  Tile-K profiles, and no validation roster or Vitis evidence files changed.

Proof:
- Red check:
  `cargo test -p spatial-rs-core --locked lab2_fixed_gemm_adapters_accept_exact_row_col_k_tail_runtime_args -- --nocapture`
  failed first because the adapter did not match `33 35 34`.
- Focused checks:
  `cargo test -p spatial-rs-core --locked lab2_fixed_gemm_adapters_accept_exact_row_col_k_tail_runtime_args -- --nocapture`,
  `cargo test -p spatial-rs-core --locked lab2_fixed_gemm_source_proof_records_row_col_k_tail_profile -- --nocapture`,
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_raw_lab2_part5_row_col_k_tail -- --nocapture`,
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_raw_lab2_part6_row_col_k_tail_as_scheduled_payload -- --nocapture`,
  `cargo test -p spatial-rs-core --locked raw_lab2_gemm_row_col_k_tail_near_misses_fail_closed -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part5_row_col_k_tail -- --nocapture`,
  and
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part6_row_col_k_tail -- --nocapture`.
- Broader local verification:
  `cargo test -p spatial-rs-core --locked lab2_fixed_gemm -- --nocapture`,
  `cargo test -p spatial-rs-core --locked parse_accel_lab2_outer_k -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test vitis_validation scheduled_row_col_k_tail -- --nocapture`,
  `cargo test --locked -p spatial-rs-core --quiet`,
  `cargo test --locked -p spatial-rs-hls --quiet`,
  `cargo test --locked -p ee109-examples --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is a bounded source-adapter compatibility slice.
- It does not add validation-program membership, generated-HLS surface area, or
  fresh EC2/Vitis evidence; it maps exact raw lab sources to existing
  Vitis-proven row/column/K-tail canaries.
- It does not imply arbitrary GEMM dimensions, generic row/column tails, broad
  Scala source compatibility, board execution, Vivado implementation, timing
  closure, or completion of the full Spatial rewrite.

## 2026-07-04 -- Rust rewrite raw Lab3 convolution static-border adapter

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `07a55ba88cb517ce528722367d507869d600dce8` (`Accept raw Lab3
  static border predicate`) extends the quarantined raw
  `Lab3Part1Convolution` source adapter to accept the exact teaching spelling
  `r < Kh - 1 || c < Kw - 1`.
- The adapter normalizes only that full paired predicate to the existing
  checked `pad_r`/`pad_c` proof form, then compares against the canonical
  local-window fixture before emitting the canonical Lab3 convolution payload.
- Swapped and mixed near-misses such as `r < Kw - 1 || c < Kh - 1`,
  `r < Kh - 1 || c < pad_c`, and `r < pad_r || c < Kw - 1` remain rejected.
- Updated the Rust README, fixture matrix, EE109 MVP plan, architecture note,
  superpowers roadmap, vault stability matrix, vault roadmap, and this progress
  log.

Subagent review:
- A `gpt-5.5` `xhigh` read-only exploration subagent confirmed this was the
  next bounded Lab3 source-compatibility slice.
- A `gpt-5.5` `xhigh` review subagent caught that the first implementation
  normalized each side independently and could have accepted mixed predicates.
  The implementation was tightened to whole-predicate normalization and covered
  by a failing-then-passing mixed-form rejection test.

Proof:
- Red check:
  `cargo test -p spatial-rs-core --locked local_lab3_convolution_adapter_accepts_static_kernel_border_expression -- --nocapture`
  failed first because exact fixture equality rejected the static kernel-border
  spelling.
- Review red check:
  `cargo test -p spatial-rs-core --locked local_lab3_convolution_adapter_rejects_mixed_static_kernel_border_expression -- --nocapture`
  failed against the initial independent-token normalizer before the
  whole-predicate fix.
- Focused checks:
  `cargo test -p spatial-rs-core --locked local_lab3_convolution_adapter_accepts_static_kernel_border_expression -- --nocapture`,
  `cargo test -p spatial-rs-core --locked local_lab3_convolution_adapter_rejects_mixed_static_kernel_border_expression -- --nocapture`,
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_local_raw_lab3_static_kernel_border_expression -- --nocapture`,
  `cargo test -p spatial-rs-core --locked raw_lab3_part1_convolution_near_misses_fail_closed -- --nocapture`,
  and
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab3_local_raw_convolution_static_kernel_border_preserves_hls_and_manifest -- --nocapture`.
- Broader local verification:
  `cargo test --locked -p spatial-rs-core --quiet`,
  `cargo test --locked -p spatial-rs-hls --quiet`,
  `cargo test --locked -p ee109-examples --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy -p spatial-rs-core -p spatial-rs-hls -p ee109-examples --all-targets --locked -- -D warnings`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is a bounded source-adapter compatibility slice.
- It does not add generic Scala `LineBuffer`, `RegFile`, `Reduce`,
  arbitrary local-window syntax, rotated kernels, dynamic dimensions, renamed
  row/column identifiers, generated-HLS surface area, or validation-program
  membership.
- It has not been rerun on EC2/Vitis yet; the result is stable under local
  Rust, HLS-codegen equality, and manifest equality tests, pending fresh vendor
  HLS validation.
- It does not imply board execution, Vivado implementation, timing closure, or
  completion of the full Spatial rewrite.

## 2026-07-05 -- Rust rewrite retired raw Lab2 memory-reduction wrappers

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `a645e6133ba1e593ed973fdb1b0a5757f050d72a` (`Retire raw Lab2
  mem reductions`) removes the quarantined raw Scala ingress for
  `Lab2Part1SimpleMemReduce` and `Lab2Part2SimpleMemFold`.
- The supported behavior remains available through the Rust-subset
  `MemReduceOnes16` / `MemFoldOnes16` all-ones canaries and the promoted
  `MemReduceFill v0` / `MemFoldFill v0` static-length/integer-fill family.
- The old raw lab class names remain reserved: parser and checked-IR tests now
  prove they fail closed instead of silently re-entering through raw source
  compatibility.
- Updated the Rust README, fixture matrix, EE109 MVP plan, architecture note,
  superpowers roadmap, vault HLS stability matrix, vault roadmap, and this
  progress log to reflect the current retired-wrapper boundary.

Proof:
- Red checks were run first for the retired-wrapper expectations:
  `cargo test --locked -p spatial-rs-core retired_lab2_memory_reduction_wrappers -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab2_part -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part1_simple_memreduce_is_retired -- --nocapture`
  all failed before the production adapter removal.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core source_adapter -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab2_part -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_lab2_simple_memory_reduction_spatialish_sugar_without_raw_adapter -- --nocapture`,
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_retired_raw_lab2_mem_reduction_adapter_names -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen memreduce_fill -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen memfold_fill -- --nocapture`,
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`.
- Broader local verification passed:
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `cargo test --locked`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is a raw-adapter retirement and compiler-boundary cleanup slice.
- It does not add validation-program membership, change generated validation
  HLS, or create fresh EC2/Vitis evidence; the imported
  `a62eb274` 37-program checkpoint remains the active vendor-HLS anchor.
- It does not imply generic Spatial `MemReduce`/`MemFold`, arbitrary reducer
  bodies, dynamic bounds, rank-2 reductions, scheduling, banking, broad Scala
  source compatibility, board execution, Vivado implementation, timing closure,
  or completion of the full Spatial rewrite.

## 2026-07-05 -- Rust rewrite accepts const-backed Part6 par aliases

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `da2fa5905fa336bef5f62481b629a7c0387754ec` (`Accept
  const-backed Part6 par aliases`) lets the narrow Lab2-like structural Part6
  outer-K bridge accept parser-only `ROW_PAR` and `COL_PAR` constants for the
  partial-tile MemFold `par` factors.
- These aliases normalize to the existing checked schedule values,
  `partial_row_par = 2` and `partial_col_par = 16`, before checked payload,
  HLS generation, manifest comparison, and validation-roster handling.
- The alias constants are filtered only when used by that bridge, preserving
  the exact Tile-K classifier shape and preventing unused alias constants from
  widening the accepted source surface.
- Generic symbolic `par` factors such as `ROW_TILES` or `TILE_C`, unknown
  aliases, unused alias constants, wrong alias values, one-sided partial par,
  and outer-loop par remain fail-closed.
- Updated the Rust README, fixture matrix, EE109 MVP plan, architecture note,
  Tile-K contract design note, vault HLS lowering map, vault stability matrix,
  vault roadmap, and this progress log.

Proof:
- Red checks first showed the old boundary was real:
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k_infix_tile_io_accepts_const_backed_part6_partial_par -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k_offset_loops_accept_const_backed_part6_partial_par -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_part6_structural_par_preserves_scheduled_hls_and_manifest -- --nocapture`
  initially failed on the literal-only parser guard, then exposed the exact
  nine-constant classifier gate before the alias filtering was added.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core raw_lab2_part6_fixed_wrapper_near_misses_fail_closed -- --nocapture`,
  `cargo test --locked -p spatial-rs-core tile_k_fold_update -- --nocapture`,
  `cargo test --locked -p spatial-rs-core resolved_hir_records_foreach_schedule_facts -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls tile_k_memfold_plan_exposes -- --nocapture`,
  `cargo test --locked -p ee109-examples validation_programs -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_a62eb274_as_current_vendor_anchor -- --nocapture`.
- Broader local verification passed:
  `cargo test --locked --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This is a parser/HIR compatibility slice for the already-supported Lab2
  Part6 HLS schedule; it does not add generic symbolic `par`, generalized
  scheduling, banking, arbitrary reduction bodies, new validation examples, or
  any generated-HLS surface-area change.
- No fresh EC2/Vitis run was needed for this slice because the accepted alias
  source normalizes to the same checked payload and HLS/manifest as the
  existing literal `par 2` / `par 16` Part6 program, and the validation roster
  did not change.
- The imported `a62eb274` 37-program current-head checkpoint remains the active
  vendor-HLS anchor.

## 2026-07-05 -- Rust rewrite guards reserved lab labels in checked IR

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `6738960456650327c2d76206246f1858a1815294` (`Guard reserved
  lab labels in checked IR`) adds a central checked-IR preflight that rejects
  reserved EE109 adapter labels when the checked `ProgramKind` does not match
  that label's canonical checked-IR kind.
- Canonical adapter paths remain accepted when the kind and shape are correct;
  broad or generic feature reuse of lab labels now fails early with
  `spatial:E0104`.
- A hard-coded Lab2 Part5/Part6 Tile-K checked-IR fallthrough guard now proves
  those GEMM labels cannot be reused as generic Tile-K feature names. The
  parser already had matching Lab2 GEMM reserved-name near-miss coverage.
- Updated the Rust rewrite roadmap to mark this sub-slice complete while
  leaving the broader reserved-label removal audit open.

Proof:
- The red check
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_reserved_lab_labels_as_generic_feature_names -- --nocapture`
  initially failed because reserved labels reached the older
  `spatial:E0300` unsupported-kind path instead of the new reserved-name
  boundary.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_reserved_lab_labels_as_generic_feature_names -- --nocapture`,
  `cargo test --locked -p spatial-rs-core validate::tests -- --nocapture`,
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_lab2_gemm_reserved_labels_for_tile_k_memfold_feature_kind -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_outer_k_infix_tile_io_near_misses_fail_closed -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part5_gemm_fixed_32 -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_accepts_exact_raw_lab2_part6_gemm_as_scheduled_payload -- --nocapture`,
  `cargo test --locked -p spatial-rs-core source_adapter -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part5_fixed_32_preserves_outer_k_hls_and_manifest -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part6_fixed_32_emits_scheduled_hls_and_manifest -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_part6_structural_par_preserves_scheduled_hls_and_manifest -- --nocapture`.
- Broader local verification passed:
  `cargo test --locked --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check` in the Rust repo.

Boundary:
- This is a compiler-boundary and diagnostic hardening slice. It does not
  change the HLS or manifest output, validation roster, raw adapter surface, or
  supported EE109 examples.
- It does not remove any reserved labels; the parent candidate-specific
  fallthrough audit remains open for future label removals.
- No fresh EC2/Vitis run was needed for this slice because generated HLS and
  validation membership did not change.
- The imported `a62eb274` 37-program current-head checkpoint remains the active
  vendor-HLS anchor.

## 2026-07-05 -- Rust rewrite moves Lab2 GEMM frontend profiles into bridge

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `edb27825c93e1057f9c3c788c7350bd499e08cbf` (`Move Lab2 GEMM
  frontend bridge profiles`) moves the quarantined Lab2 GEMM raw-adapter
  frontend source/profile construction into `frontend::lab2_gemm_bridge`.
- `source_adapter` now proves the exact raw Scala wrapper/scaffold/body,
  selects the Lab2 Part5/Part6 bridge target and fixed/K-tail/row-col-K-tail
  profile, and delegates generated frontend source plus expected Tile-K
  profile construction to the bridge.
- Added a bridge-local test that parses all six Part5/Part6 raw-adapter
  frontend profiles and checks the expected Tile-K profile for each.
- Updated the Rust rewrite roadmap to record that Lab2 GEMM raw-adapter
  frontend source/profile construction now belongs to the bridge boundary.

Proof:
- The red check
  `cargo test --locked -p spatial-rs-core lab2_gemm_bridge_builds_raw_adapter_frontend_profiles -- --nocapture`
  initially failed at compile time because the bridge-owned target/profile API
  and frontend-profile builder did not exist.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core lab2_gemm_bridge_builds_raw_adapter_frontend_profiles -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm_source_proof_carries_frontend_boundary -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_fixed_gemm -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_gemm_bridge -- --nocapture`,
  `cargo test --locked -p spatial-rs-core source_adapter -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_lab2_outer_k -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_part6_structural_par -- --nocapture`.
- Broader local verification passed:
  `cargo test --locked --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check` in the Rust repo.

Boundary:
- This is a compiler-boundary cleanup for the already-supported Lab2 GEMM
  profiles. It does not add new raw Scala spellings, new validated programs,
  or new HLS features.
- It preserves the existing Lab2 Part5/Part6 generated HLS and manifest
  behavior under the local HLS regression tests.
- No fresh EC2/Vitis run was needed because HLS output and validation
  membership did not change.
- The imported `a62eb274` 37-program current-head checkpoint remains the active
  vendor-HLS anchor.

## 2026-07-05 -- Rust rewrite moves rank2 copy from-plan wrappers

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `0a1a0269ec8ac7c8ca004634febede30d323eb5e` (`Move rank2 copy
  from-plan wrappers`) adds `rank2_copy_kernel_from_plan` and
  `rank2_copy_harness_from_plan` to `spatial_rs_hls::rank2_copy`.
- `emit.rs` now dispatches rank-2 copy kernel and harness generation through
  those wrappers instead of performing `rank2_copy_frame_from_plan` plus render
  calls itself.
- The wrappers preserve the existing exact `[input, output]` param-order guard
  and keep malformed swapped/extra-param internal plans fail-closed.
- Updated the Rust rewrite roadmap to record the rank-2 copy `emit.rs`
  orchestration cleanup.

Proof:
- The red check
  `cargo test --locked -p spatial-rs-hls rank2_copy_from_plan --lib -- --nocapture`
  initially failed at compile time because `rank2_copy_kernel_from_plan` and
  `rank2_copy_harness_from_plan` did not exist.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-hls rank2_copy_from_plan --lib -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls rank2_copy --lib -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_copy_4x6_feature_emits_parameterized_rank2_copy_and_harness -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab3_row_major_copy_kernel_uses_cols_as_rank2_flatten_stride -- --nocapture`,
  and `cargo test --locked -p spatial-rs-hls --quiet`.
- Broader local verification passed:
  `cargo test --locked --quiet`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check` in the Rust repo.

Boundary:
- This is a backend helper-boundary cleanup for already-supported rank-2 copy
  lowering. It does not add features, change validation membership, or widen
  source acceptance.
- MatrixCopy and Lab3 row-major copy HLS/harness guards preserved the generated
  rank-2 copy output locally.
- No fresh EC2/Vitis run was needed because HLS output and validation
  membership did not change.
- The imported `a62eb274` 37-program current-head checkpoint remains the active
  vendor-HLS anchor.

## 2026-07-05 -- Rust rewrite retires raw Lab2 GEMM Scala ingress

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `b91118f756d16edf610f890542c2684da6b74acb` (`Retire raw Lab2
  GEMM Scala ingress`) closes the quarantined raw Scala adapter registry for
  `Lab2Part5GEMM` and `Lab2Part6GEMM`.
- Raw fixed32, K-tail34, and row/column/K-tail33x35x34 Scala wrappers now fail
  closed in parser and HLS tests.
- Canonical Rust-subset Tile-K support remains intact for serial/scheduled
  full-K, K-tail, and row/column/K-tail GEMM canaries.
- Removed the stale raw-adapter frontend-profile builder from
  `frontend/lab2_gemm_bridge.rs`; the bridge still owns the Rust-subset shell,
  offset-loop, `numel_*`, in-place C, and Part6 partial-par state.
- Updated README, fixture matrix, MVP plan, architecture notes, and roadmap to
  describe Lab2 GEMM support as Rust-subset Tile-K canaries rather than raw
  Scala wrapper compatibility.

Proof:
- Red checks first failed because raw Lab2 GEMM wrappers still compiled:
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab2 -- --nocapture`
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core source_adapter -- --nocapture`,
  `cargo test --locked -p spatial-rs-core parse_accel_rejects_retired_raw_lab2 -- --nocapture`,
  `cargo test --locked -p spatial-rs-core lab2_outer_k -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_raw_part -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k -- --nocapture`.
- Broader local verification passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked --quiet`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`,
  `cargo test --locked -p ee109-examples validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check` in the Rust repo.

Boundary:
- This intentionally removes source compatibility for the old Scala
  `Lab2Part5GEMM` / `Lab2Part6GEMM` wrappers. The supported path is now the
  Rust-subset frontend/HIR Tile-K surface.
- Generated HLS and validation membership are expected to remain anchored by
  existing canonical canaries; no fresh EC2/Vitis run was performed in this
  slice.
- The imported `a62eb274` 37-program current-head checkpoint remains the active
  vendor-HLS anchor pending the next real Vitis refresh.

## 2026-07-05 -- Rust rewrite refreshes current-head EC2/Vitis evidence

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `0a21d52e` (`Refresh current-head Vitis evidence`) imports a new
  current-head 37-program EC2/Vitis bundle at
  `docs/vitis-validation/2026-07-05-current-head-b91118f7-37-program/`.
- The run executed from source commit `b91118f7` after the raw Lab2 Part5/Part6
  GEMM Scala-ingress retirement.
- All 37 validation programs passed Vitis 2025.1 `csim_design` and
  `csynth_design` on the EC2 instance.
- README, fixture matrix, MVP plan, architecture notes, roadmap, and evidence
  validator tests now name `b91118f7` as the active vendor-HLS anchor while
  keeping `a62eb274` as a historical checkpoint.

Proof:
- EC2 plan gate passed with Rust/Cargo 1.75 and `PLAN_COUNT=37`.
- Full EC2 command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-current-head-b91118f7`.
- Last EC2 kernel completed successfully:
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`
  with `returncode=0 csim=true csynth=true`.
- Repo-local evidence validation passed on EC2 and locally:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-b91118f7-37-program --mode both`.
- Focused local gates passed:
  `cargo test --locked -p spatial-rs-hls --test vitis_validation current_head_vitis_evidence_validator_accepts_b91118f7_checkpoint -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation historical_current_head_vitis_evidence_validator_accepts_a62eb274_checkpoint -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test vitis_validation active_docs_name_b91118f7_as_current_vendor_anchor -- --nocapture`,
  and
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`.
- Broader local verification passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked --quiet`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check` in the Rust repo.

Boundary:
- This is vendor-HLS evidence for Vitis `csim_design` and `csynth_design` only.
  It does not prove board execution, Vivado implementation, timing closure, or
  performance optimality.
- It does not reintroduce broad Scala source compatibility. Raw
  `Lab2Part5GEMM` / `Lab2Part6GEMM` wrappers remain retired; the supported
  GEMM path is still the Rust-subset Tile-K canary set.

## 2026-07-05 -- Rust rewrite locks the FixPt HLS policy and refreshes Vitis

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- The supported `FixPt[TRUE,_24,_8]` type now has an explicit policy in core
  metadata: signed, 32 total bits, 24 integer bits, 8 fractional bits,
  `AP_TRN` rounding, and `AP_WRAP` overflow.
- HLS generation now emits
  `ap_fixed<32, 24, AP_TRN, AP_WRAP>` for
  `spatial_fixpt_true_24_8_t`; the host-only `ap_fixed` shim accepts the same
  rounding/overflow template form for local harness tests.
- Manifest conversion policy for fixed-point DRAM buffers now records
  `raw_ap_fixed_true_24_8_trn_wrap_v1`.
- A fresh 37-program EC2/Vitis bundle is imported at
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-fixpt-policy-current-head-37-program/`.
- README, fixture matrix, MVP plan, architecture notes, roadmap, and evidence
  validator tests now treat the fixed-point-policy run as the active
  vendor-HLS anchor; `b91118f7` remains historical.

Proof:
- Red checks first failed on the missing `fixpt_policy()` API, old two-argument
  HLS alias, and old fixed-point manifest conversion-policy string.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core fixpt_true_24_8_exposes_explicit_hls_numeric_policy -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls --test m1_codegen matrix_tile_memfold_fixpt_4x6x5_feature_emits_ap_fixed_types_and_harness -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls tile_k -- --nocapture`.
- Full local gates passed:
  `cargo fmt --all -- --check`,
  `cargo test --locked --quiet`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check`.
- EC2 plan-only gate produced 37 planned validation programs.
- EC2 Vitis 2025.1 execute run completed all 37 validation programs with
  `returncode=0 csim=true csynth=true`; the fixed-point MemFold, in-place
  MemFold, serial Tile-K, scheduled Tile-K, K-tail, and row/column/K-tail GEMM
  canaries all passed with the explicit alias.
- Repo-local evidence validation passed on EC2 and locally:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-fixpt-policy-current-head-37-program`.

Boundary:
- This locks the lowering policy for the single supported fixed-point canary
  type only. It does not add decimal fixed-point literals, arbitrary
  fixed-point widths, mixed `Int`/`FixPt` GEMM, generic fixed-point arithmetic,
  or board/timing evidence.
- Non-outer-K FixPt tail tiles remain fail-closed; the existing Tile-K tail
  canaries remain the fixed-point tail coverage path.

## 2026-07-05 -- Rust rewrite lands the Tile-K par4x16 local canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Added the exact full-K schedule canary
  `MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32`.
- The frontend/checker now accepts positive exact full-K Tile-K schedule
  factors that divide the static tile dimensions, while preserving the strict
  named Part6 and tail profiles.
- HLS lowering now carries `partial_row_par=4` / `partial_col_par=16` into
  `TileKMemFoldSchedule::PartialTile`, row-cyclic array partitions, row/column
  unroll pragmas, and the generated host harness.
- A non-dividing `3x16` exact full-K schedule remains fail-closed.

Proof:
- Red canary first failed with `spatial:E0300` on the unsupported `4x16`
  schedule.
- Focused green checks passed:
  `cargo test --locked -p spatial-rs-core checked_ir_accepts_generic_exact_tile_k_par4x16_schedule -- --nocapture`,
  `cargo test --locked -p spatial-rs-core checked_ir_rejects_generic_exact_tile_k_nondividing_schedule -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls tile_k_memfold_plan_exposes_generic_par4x16_schedule_and_partitions -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen lab2_outer_k_par4x16_schedule_emits_parametric_hls_and_manifest -- --nocapture`.
- Broader focused gates passed:
  `cargo test --locked -p spatial-rs-core tile_k -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls tile_k -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen -- --nocapture`.
- Full local gates passed after docs:
  `cargo fmt --all -- --check`,
  `cargo test --locked --quiet`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  `git diff --check` in the Rust repo,
  and `git diff --check` in the vault.

Boundary:
- This entry recorded the local-only state before the follow-up EC2/Vitis
  promotion below.
- This does not add generic Spatial scheduling, inferred banking, arbitrary
  K-tail schedules, broad Scala source compatibility, board execution, or
  timing evidence.

## 2026-07-05 -- Rust rewrite promotes Tile-K par4x16 through EC2/Vitis

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Promoted `MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` into the
  EE109 validation roster as the 38th program.
- The active vendor-HLS evidence anchor is now
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-current-head-par4x16-38-program/`.
- The old 37-program fixed-point-policy bundle remains historical evidence,
  but is no longer the active current-head roster.

Proof:
- Remote EC2 host:
  `[ec2-host — see private/ec2-lane.md]`.
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-05-par4x16-38-program/repo`.
- EC2 preflight passed with `cargo 1.75.0`, `rustc 1.75.0`, Vitis settings at
  `/tools/Xilinx/2025.1/Vitis/settings64.sh`, the 38-program roster unit test,
  and 38 sidecar plans.
- EC2 Vitis command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-current-head-par4x16-38-program`.
- All 38 kernels passed Vitis 2025.1 `csim_design` and `csynth_design`,
  including `MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32`.
- The par4x16 Vitis log reports II=1 for the scheduled compute/update loops,
  but the final C writeback loop emits II-violation warnings and settles at
  final II=16. The csynth report estimates 256 DSP against 220 available on
  `xc7z020-clg400-1`.
- Local evidence validation passed:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-par4x16-38-program --mode both`.

Boundary:
- This proves Vitis C simulation and HLS synthesis for the exact 38-program
  roster only.
- It does not claim board execution, Vivado implementation, timing closure,
  performance optimality, resource fit, generic Spatial scheduling, inferred
  banking, arbitrary K-tail schedules, or broad Scala source compatibility.

## 2026-07-05 -- Rust rewrite records parameterized Tile-K proof gate

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `3a4d753f354eb20dfa4218ea38b2e954d699c783` (`Record
  parameterized Tile-K proof gate`).
- Promoted the existing local non-roster
  `MatrixTileMemFoldOuterKInPlaceFixPt24x20x12Tile8x5x4` canary into an
  explicit proof/equality gate.
- Added private `TileKMemFoldProof` coverage for the 24x20x12 / 8x5x4 exact
  full-K shape, including source-shape, loop-bound, tile-size, and serial
  schedule facts.
- Added fail-closed parser/classifier coverage for inconsistent parameterized
  raw-alias coverage and wrong stride-symbol provenance.
- Updated the repo fixture matrix, vault roadmap, and stability matrix to
  record this as local non-roster proof coverage rather than a Vitis-roster
  change.

Proof:
- `cargo test -p spatial-rs-core --locked parse_accel_lab2_outer_k_accepts_parameterized_raw_dimension_tile_aliases -- --nocapture`
- `cargo test -p spatial-rs-core --locked lab2_outer_k_infix_tile_io_near_misses_fail_closed -- --nocapture`
- `cargo test -p spatial-rs-core --locked tile_k_contract -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_outer_k -- --nocapture`
- `git diff --check`

Boundary:
- Generated HLS, manifests, validation roster membership, and imported Vitis
  evidence are unchanged, so no fresh EC2/Vitis run is claimed.
- This is not raw Scala compatibility, generic Spatial `MemFold`, arbitrary
  K-tail support, inferred banking, dynamic dimensions, board execution, or
  timing/resource evidence.
- Subagent review ranked the next substantive semantic slice as a named FixPt
  tail `Dense2dTileMemFold` canary; that can start locally, but needs fresh
  EC2/Vitis evidence before any vendor-HLS readiness or roster-promotion claim.

## 2026-07-05 -- Rust rewrite adds exact FixPt MemFold tail canary

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `2ed2ddecf1ec1af049b0ae41a544b93b0e1d75ea` (`Add exact FixPt
  MemFold tail canary`).
- Added the exact local `MatrixTileMemFoldTailFixPt5x7x5` canary as the
  `FixPt[TRUE,_24,_8]` counterpart to the Int
  `MatrixTileMemFoldTail5x7x5` non-outer-K tail/min-bound canary.
- Parser, classifier proof, checked IR, generated HLS, manifest, and host
  compile/run now accept the exact 5x7x5 / 2x3 split-C tail shape.
- HLS emits `ap_fixed<32, 24, AP_TRN, AP_WRAP>` storage plus runtime
  `row_limit` / `col_limit` loops for this shape.
- Wrong FixPt tail names/shapes remain fail-closed, along with raw Scala
  wrappers, generic Spatial `MemFold`, `par`, banking, K tiling, and arbitrary
  FixPt tails.

Proof:
- Focused gates passed:
  `cargo test -p spatial-rs-core --locked parse_accel_accepts_rank2_tile_memfold_tail_fixpt_feature -- --nocapture`,
  `cargo test -p spatial-rs-core --locked dense2d_memfold_proof_accepts_exact_fixpt_tail_canary -- --nocapture`,
  `cargo test -p spatial-rs-core --locked checked_ir_accepts_exact_dense2d_tile_memfold_tail_fixpt_feature -- --nocapture`,
  and
  `cargo test -p spatial-rs-hls --locked --test m1_codegen matrix_tile_memfold_tail_fixpt_5x7x5_feature_emits_ap_fixed_bounds_and_harness -- --nocapture`.
- Negative gates passed:
  `cargo test -p spatial-rs-core --locked spatialish_memfold_call_near_misses_fail_closed -- --nocapture`,
  `cargo test -p spatial-rs-core --locked memfold_return_combiner_sugar_near_misses_fail_closed -- --nocapture`,
  `cargo test -p spatial-rs-core --locked dense2d_memfold_proof_rejects_non_exact_fixpt_tail_canaries -- --nocapture`,
  and
  `cargo test -p spatial-rs-core --locked checked_ir_rejects_non_exact_dense2d_tile_memfold_tail_fixpt_features -- --nocapture`.
- Broader gates passed:
  `cargo test -p spatial-rs-core --locked rank2_tile_memfold -- --nocapture`,
  `cargo test --locked --workspace`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`,
  and `git diff --check`.

Boundary:
- This changes the local generated-HLS surface for one new named canary, but it
  does not add validation-roster membership or EC2/Vitis evidence yet.
- Do not claim vendor-HLS readiness for `MatrixTileMemFoldTailFixPt5x7x5`
  until a fresh EC2/Vitis run is captured and validated.
- This is not raw Scala compatibility, generic Spatial `MemFold`, arbitrary
  tail support, arbitrary fixed-point widths, inferred banking, scheduling,
  board execution, resource fit, or timing evidence.

## 2026-07-05 -- Rust rewrite refreshes 00797aed current-head Vitis evidence

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `00797aedfb2c9af7d2b25848dfa409e2569be72e` (`Accept scheduled
  Tile-K bulk IO`) now has a fresh full-roster EC2/Vitis evidence bundle:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.
- This supersedes
  `docs/vitis-validation/2026-07-05-current-head-746d9ec5-39-program/` as the
  active vendor-HLS anchor; `746d9ec5` remains historical evidence.
- The roster remains 39 validation programs. All 39 passed Vitis 2025.1
  `csim_design` and `csynth_design`.
- The repo-local evidence validator reports
  `kernels=39 resource_fit=37/39 over_budget=2 ii_caveated=14`.
- The exact scheduled Part6 full-K Tile-K canary
  `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` passed in the
  full-roster run after the canonical arrow bulk IO source cleanup.

Proof:
- EC2 source checkout staged from local git bundle at
  `/home/ubuntu/spatial-rs-runs/2026-07-05-current-head-00797aed-39-program/repo`.
- Remote command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-current-head-00797aed-39-program-run`.
- Remote and local validator command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-00797aed-39-program --mode both`.
- Focused local pins passed:
  `run_vitis_validation_validate_evidence_accepts_current_39_checkpoint`,
  `current_head_vitis_evidence_validator_accepts_00797aed_checkpoint`,
  `current_head_39_checkpoint_distinguishes_hls_acceptance_from_resource_fit`,
  `active_docs_name_39_program_checkpoint_as_current_vendor_anchor`, and
  `ec2_toolchain_compat`.

Boundary:
- This is Vitis C simulation and HLS synthesis evidence for the exact
  39-program roster only.
- It is not board execution, Vivado implementation, timing closure,
  resource-fit implementation evidence for the two over-DSP Tile-K schedules,
  arbitrary tails, inferred banking/scheduling, generic Spatial `MemFold`, raw
  Scala compatibility, or broad Spatial source compatibility.

## 2026-07-05 -- Rust rewrite accepts scheduled canonical Tile-K bulk IO

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `00797aedfb2c9af7d2b25848dfa409e2569be72e` (`Accept scheduled
  Tile-K bulk IO`).
- The canonical Rust-subset arrow bulk tile IO source form now accepts the
  exact scheduled Part6 full-K Tile-K profile when the partial-product loops
  carry literal `par 2` / `par 16`.
- That source normalizes to
  `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, preserving the
  same checked payload, generated HLS C++, and manifest JSON as the existing
  scheduled structural canary.
- Generic `par`, symbolic canonical `par`, non-partial-loop `par`, `numel_k`,
  tails, raw Scala wrappers, and broad Spatial scheduling remain fail-closed
  outside the already documented bridge paths.
- Updated Rust README, fixture matrix, MVP plan, architecture notes, vault
  roadmap, stability matrix, and this progress log.

Proof:
- `cargo fmt --all -- --check`
- `git diff --check`
- `cargo test --locked --workspace`
- `cargo clippy --all-targets --locked -- -D warnings`

Limit:
- No fresh EC2/Vitis run was performed for this slice.
- At the time of this local source cleanup, validation-roster membership,
  imported Vitis evidence, and vendor-HLS claims were unchanged. The active
  vendor-HLS anchor remained
  `docs/vitis-validation/2026-07-05-current-head-746d9ec5-39-program/`.

## 2026-07-05 -- Rust rewrite accepts canonical Tile-K bulk IO

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Rust commit `5b428158cbe12b0d6a30c993c64bbfc709cfb3db` (`Accept canonical
  Tile-K bulk IO`).
- Added canonical Rust-subset arrow bulk tile IO for the exact full-K
  `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` Tile-K canary:
  `load lhs_tile <- lhs[...]`, `load rhs_tile <- rhs[...]`,
  `load c_tile <- c[...]`, canonical `memfold c_tile with partial_tile over
  k_idx in 0..TILE_K`, and `store c[...] <- c_tile`.
- The frontend now distinguishes Tile-K bulk-index normalization from the older
  Lab2 shell-alias bridge. Canonical Tile-K arrow bulk IO stays on canonical
  names, while the existing non-outer-K Lab2 shell-alias arrow bridge and the
  Lab2 outer-K infix bridge remain intact.
- Local tests prove the new source spelling lowers to the same checked
  Tile-K payload as the expanded loop canary and preserves exact HLS/manifest
  equality.
- Updated Rust README, fixture matrix, MVP plan, architecture notes, vault
  roadmap, stability matrix, and this progress log.

Proof:
- `cargo test -p spatial-rs-core --locked tile_k_canonical_bulk_io -- --nocapture`
- `cargo test -p spatial-rs-hls --locked --test m1_codegen tile_k_canonical_bulk_io -- --nocapture`
- `cargo test -p spatial-rs-core --locked parse_accel_lab2_shell_alias_buffer_matches_expanded_fixpt_canary -- --nocapture`
- `cargo test -p spatial-rs-core --locked lab2_shell_alias_buffer_near_misses_fail_closed -- --nocapture`
- `cargo test --locked --workspace`
- `cargo clippy --all-targets --locked -- -D warnings`
- `cargo fmt --all -- --check`
- `git diff --check`

Boundary:
- No validation-roster member was added, and no fresh EC2/Vitis run was needed:
  the generated HLS and manifest are exactly equal to the existing expanded
  full-K Tile-K canary.
- This is not raw Scala compatibility, generic Spatial `MemFold`, `numel_k`
  tail semantics, Part6 `par`, inferred banking, dynamic dimensions, board
  execution, resource fit, or timing evidence.

## 2026-07-05 -- Selected scheduled row/column/K-tail Vitis proof

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `f2833216` (`Record selected par4x16 Vitis caveats`) was used
  to run
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`
  through the selected-kernel EC2/Vitis lane.
- The run used the exact `run-vitis-validation --kernel` path and passed
  `csim_design` plus `csynth_design` on Vitis 2025.1 for `xc7z020-clg400-1`.
- Durable compact evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-scheduled-row-col-k-tail-f2833216/`.

Proof:
- EC2 selected plan-only:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --kernel MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34 --out target/vitis-validation-selected-row-col-k-tail-part6-f2833216-plan`
- EC2 selected execute:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --kernel MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34 --out target/vitis-validation-selected-row-col-k-tail-part6-f2833216-run`
- EC2 selected validator:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence target/vitis-validation-selected-row-col-k-tail-part6-f2833216-run --kernel MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34 --mode both`
- Validator result:
  `kernels=1 resource_fit=1/1 over_budget=0 ii_caveated=0`.
- EC2 compatibility smoke:
  `cargo test --locked -p ee109-examples --test ec2_toolchain_compat -- --nocapture`

Measured HLS result:
- Return code 0.
- `csim_design` passed with `CSim done with 0 errors`.
- `csynth_design` finished.
- Estimated Fmax 136.99 MHz.
- Estimated clock 7.300 ns against a 10.00 ns target.
- Resource summary: 58 BRAM_18K, 131 DSP, 19307 FF, 13628 LUT, 0 URAM.
- No selected-run II caveats were reported.

Boundary:
- This proves the selected-run Vitis lane and evidence-quality accounting for
  the fixed `33x35x34`, `partial_row_par=2` / `partial_col_par=16` scheduled
  row/column/K-tail Tile-K profile with runtime `row_limit`, `col_limit`, and
  `numel_k` guards.
- It is not a full-roster refresh, board execution, Vivado implementation,
  timing closure, arbitrary row/column/K-tail support, inferred banking or
  schedule policy, generic Spatial `MemFold`, or broad Scala source
  compatibility.

## 2026-07-05 -- Rust HLS render-plan lowering extraction

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Moved the `ProgramKind -> HlsRenderPlan` lowering ledger and harness-kind
  selection out of `crates/spatial-rs-hls/src/emit.rs` into a crate-private
  `spatial_rs_hls::render` module.
- Kept `emit.rs` responsible for public artifact IO, kernel/harness body-plan
  dispatch, host HLS shims, and Vitis dry-run project writing.
- Added an architecture regression that fails if `emit.rs` grows a local
  `lower_hls_render_plan` function again.

Proof:
- Red test first:
  `cargo test --locked -p spatial-rs-hls emit_module_delegates_render_plan_lowering -- --nocapture`
  failed while `emit.rs` still owned `lower_hls_render_plan`.
- Green/focused gates passed:
  `cargo test --locked -p spatial-rs-hls emit_module_delegates_render_plan_lowering -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls render_hls_artifacts_matches_public_kernel_harness_and_manifest -- --nocapture`,
  `cargo test --locked -p spatial-rs-hls render_hls_artifacts_preserves_lab3_vs_stencil_harness_selection -- --nocapture`,
  and
  `cargo test --locked -p spatial-rs-hls --test m1_codegen vitis_dry_run_project_records_tool_profile_without_running_vendor_hls -- --nocapture`.

Boundary:
- This is a no-HLS-drift backend structure cleanup. It does not change source
  syntax, checked IR, generated HLS C++, manifests, validation-program
  membership, imported Vitis evidence, or any Spatial language support claim.
- The next stronger implementation candidates identified by subagent review
  are a shared rank-2 local product/accumulation proof helper, or a bounded
  non-EE109 Tile-K shape-parameterization slice around the existing
  `24x20x12 / tile8x5x4` canary.

## 2026-07-05 -- Rust HLS render ownership cleanup

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `a45019ee` (`Move HLS render ownership out of emit`).
- Moved HLS artifact rendering, manifest checking, and kernel/harness
  body-plan dispatch out of `crates/spatial-rs-hls/src/emit.rs` into
  `crates/spatial-rs-hls/src/render.rs`.
- Kept `emit.rs` focused on public artifact entry points, filesystem writes,
  host HLS shims, and Vitis dry-run project generation.
- Moved renderer-coupled unit tests into `crates/spatial-rs-hls/src/render_tests.rs`.
- Added an architecture regression that fails if `emit.rs` re-imports backend
  renderer modules.
- Subagent review found no production behavior blocker and flagged the old
  test-only renderer coupling; this cleanup addresses that finding.

Proof:
- Red test first:
  `cargo test -p spatial-rs-hls --locked render_module_renders_public_artifact_bundle -- --nocapture`
  failed while `render_hls_artifacts` did not exist in `render.rs`.
- Focused green gates passed:
  `cargo test -p spatial-rs-hls --locked render_module_renders_public_artifact_bundle -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked render_hls_artifacts -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked emit_module_delegates_artifact_and_plan_rendering -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked emit_dense2d_tile_memfold_kernel_plan_rejects_malformed_param_frames -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --lib`,
  `cargo test -p spatial-rs-hls --locked --test m1_codegen tile_k -- --nocapture`, and
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold -- --nocapture`.
- Full local gates passed after docs/log updates:
  `cargo test --locked --workspace`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`, and
  `git diff --check`.

Boundary:
- This is a no-HLS-drift backend structure cleanup. It does not change source
  syntax, checked IR, generated HLS C++, manifests, validation-program
  membership, imported Vitis evidence, or any Spatial language support claim.
- No fresh EC2/Vitis run was needed because generated validation HLS and roster
  membership did not change.
- The stale next-candidate note from the previous render-plan checkpoint is now
  superseded: the rank-2 local-compute helper and non-EE109 Tile-K
  `24x20x12 / tile8x5x4` canary are already covered locally.

## 2026-07-05 -- Selected Par4x8 row/column/K-tail Vitis proof

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `5f684f2a` (`Add generic scheduled row-col Tile-K canary`) was
  copied to the EC2 Vitis host and used to run
  `MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34` through the
  selected-kernel Vitis lane.
- The selected run passed Vitis 2025.1 `csim_design` and `csynth_design` for
  `xc7z020-clg400-1`.
- Durable compact evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-par4x8-row-col-tail-5f684f2a/`.
- The result proves HLS acceptance for the new 39th local validation-program
  member, but not resource-fit implementation on the recorded Zynq-7020 part.

Proof:
- EC2 selected execute:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --kernel MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34 --out target/vitis-validation-selected-par4x8-row-col-tail-5f684f2a-run`
- Local imported evidence validator:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-selected-par4x8-row-col-tail-5f684f2a --kernel MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34 --mode both`
- Validator result:
  `kernels=1 resource_fit=0/1 over_budget=1 ii_caveated=0`.
- Focused local tests passed:
  `cargo test -p ee109-examples --locked --test run_vitis_validation run_vitis_validation_validate_evidence_reports_selected_par4x8_tail_resource_caveat -- --nocapture`,
  `cargo test -p spatial-rs-hls --locked --test vitis_validation selected_par4x8_row_col_k_tail_vitis_evidence_records_dsp_caveat -- --nocapture`, and
  `cargo test -p spatial-rs-hls --locked --test vitis_validation active_docs_name_par4x16_as_current_vendor_anchor -- --nocapture`.
- Full local gates passed after evidence/docs updates:
  `cargo test --locked --workspace`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`, and
  `git diff --check`.

Measured HLS result:
- Return code 0.
- `csim_design` passed with `CSim done with 0 errors`.
- `csynth_design` finished.
- Estimated Fmax 136.99 MHz.
- Estimated clock 7.300 ns against a 10.00 ns target.
- Resource summary: 110 BRAM_18K, 259 DSP, 32513 FF, 21666 LUT, 0 URAM.
- DSP over budget: 259 used against 220 available.
- No selected-run II caveats were reported.

Boundary:
- This proves the selected-run Vitis lane for the exact fixed `33x35x34`,
  `partial_row_par=4` / `partial_col_par=8` scheduled row/column/K-tail Tile-K
  profile with runtime `row_limit`, `col_limit`, and `numel_k` guards.
- It is not a full-roster refresh, board execution, Vivado implementation,
  timing closure, resource-fit implementation evidence, arbitrary
  row/column/K-tail support, inferred banking or schedule policy, generic
  Spatial `MemFold`, or broad Scala source compatibility.

## 2026-07-05 -- Current-head 39-program Vitis proof

Rust repo branch: `/Users/david/Documents/David_code/spatial-rs` on
`David/HLS-spatial`.

Checkpoint:
- Source commit `746d9ec5` (`Record selected Par4x8 Tile-K Vitis evidence`)
  was copied to the EC2 Vitis host and used for a full current-head validation
  run.
- Remote EC2 run directory:
  `/home/ubuntu/spatial-rs-runs/2026-07-05-current-head-746d9ec5-39-program/`.
- Durable compact evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-current-head-746d9ec5-39-program/`.
- The previous 38-program bundle remains useful history; the 39-program bundle
  is now the active vendor-stability anchor.

Proof:
- EC2 plan-only:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --plan-only --mode both --out target/vitis-validation-current-head-746d9ec5-39-program-plan`
- EC2 full execute:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --out target/vitis-validation-current-head-746d9ec5-39-program-run`
- Local imported evidence validator:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/2026-07-05-current-head-746d9ec5-39-program --mode both`
- Validator result:
  `kernels=39 resource_fit=37/39 over_budget=2 ii_caveated=14`.
- Full local gates passed after evidence/docs updates:
  `cargo test --locked --workspace`,
  `cargo fmt --all -- --check`,
  `cargo clippy --all-targets --locked -- -D warnings`, and
  `git diff --check`.

Measured HLS result:
- All 39 validation programs returned code 0.
- All 39 passed `csim_design`.
- All 39 completed `csynth_design`.
- The final Par4x8 row/column/K-tail canary reported estimated Fmax
  136.99 MHz.
- Two kernels are DSP over budget on the recorded Zynq-7020 target:
  `MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` and
  `MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34`.
- Fourteen kernels have reported II caveats.

Boundary:
- This proves current-head HLS acceptance for the 39-program EE109-oriented
  validation roster under Vitis 2025.1.
- It is not board execution, Vivado implementation, timing closure,
  resource-fit implementation evidence, arbitrary Spatial source
  compatibility, or a final scheduling/banking policy.
- The important limitation is explicit: Vitis can compile and synthesize the
  current roster, but two Tile-K schedules still exceed the selected part's DSP
  budget and fourteen kernels still need II-quality follow-up.
