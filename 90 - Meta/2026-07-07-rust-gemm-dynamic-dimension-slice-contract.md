# Rust GEMM Dynamic-Dimension Slice Contract

Date: 2026-07-07

Rust repo: `/Users/david/Documents/David_code/spatial-rs`

Rust branch: `David/HLS-spatial`

Baseline Rust commit: `639f2de9` (`Add lab-functionality MVP checklist`).

Vendor-stability anchor:
`docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`
(`resource_fit=37/39`, `over_budget=2`, `ii_caveated=14`).

Checklist item: G8, "Dynamic dimensions (the lab's actual interface)" in
`docs/lab-functionality-mvp-checklist.md`. This is the single highest-value,
non-speculative MVP-B gap: the lab GEMM reads its dimensions at runtime, and
spatial-rs supports only static shapes.

## Why This Is The Flagship Slice

`lab-2-accelerator-bandits-2/src/test/scala/Lab2GEMM.scala:12-17` declares
`M`, `N`, `K` as `ArgIn[Int]` and sets them from `runtimeArgs = "32 32 32"`:

```scala
val M = ArgIn[Int]; val N = ArgIn[Int]; val K = ArgIn[Int]
setArg(M, args(0).to[Int]); setArg(N, args(1).to[Int]); setArg(K, args(2).to[Int])
```

The current `Dense2dTileKMemFold` payload
(`crates/spatial-rs-core/src/ir.rs`, struct `Dense2dTileKMemFold`) stores
`rows: usize`, `cols: usize`, `k: usize`, `row_tiles`, `col_tiles`, `k_tiles`
as **static** values, and only the tail bounds `row_bound` / `col_bound` /
`k_bound: Option<String>` are runtime strings (`numel_k`, `row_limit`,
`col_limit`). So spatial-rs matches the lab's *shape and body* at fixed
`32x32x32` / `33x35x34`, but cannot accept the lab's *interface* where M/N/K
arrive as runtime scalars. This slice closes that gap.

Every other MVP-B gap (par freedom, reducer bodies, LUT/stencil constants) is
a knob a student *could* turn; dynamic dimensions is the one thing the checked
lab source *actually does* that has no representative. It is also the sharpest
test of whether the proof-fact infrastructure generalizes from "recognize this
exact shape" to "lower any shape satisfying these facts."

## Accepted Slice (Staged)

Do not attempt all of this in one commit. The ladder below is three separable,
independently committable increments; each keeps the workspace green and each
HLS-changing increment gets its own selected EC2/Vitis run before its box is
ticked.

### Stage A — Static shape freedom (no dynamic dims yet)

Generalize the enumerated Tile-K profiles into a checked static parameter
family: arbitrary static `ROWS`/`COLS`/`K` and `TILE_R`/`TILE_C`/`TILE_K` with
the existing tail machinery, not only `32x32x32` and `33x35x34`. The local
non-roster `MatrixTileMemFoldOuterKInPlaceFixPt24x20x12Tile8x5x4` canary
already proves the shape works off the enumerated profiles; this stage promotes
that approach to a parameter family with a small perturbation matrix.

- Accept N shapes (e.g. `40x24x16 / tile 8x8x8`, `48x32x32 / tile 16x16x16`)
  as one checked family, serial schedule first.
- Keep `FixPt[TRUE,_24,_8]` and `Int` element types; keep the locked
  truncation/wrap policy.
- Host harness sweeps each shape against the Rust oracle.

This stage changes generated HLS (new dims → new bounds/arrays), so it needs a
selected `run-vitis-validation --kernel` run per representative before the G8
static-shape box may be ticked.

### Stage B — Dynamic dimensions (the lab interface)

- Accept `M`/`N`/`K` as runtime scalar inputs (`inputs { M: Int, N: Int,
  K: Int }` in the Rust-subset surface) that drive DRAM extents and runtime
  tile counts, while local SRAM tiles stay statically `TILE_*`-wide.
- Extend the payload: add runtime-dimension fields (or reuse the
  `Option<String>` bound pattern already proven for `numel_k`) so `rows`,
  `cols`, `k`, and the three tile counts can be runtime symbols. Prefer
  extending the existing bound machinery over inventing a parallel one.
- ABI manifest records the runtime-dimension scalar ports in ordinal order.
- HLS emits `ceil`-style runtime tile-count loops and reuses the existing
  runtime tail guards (`row_limit` / `col_limit` / `numel_k`) for the partial
  final tiles.
- Host harness sweeps several `(M, N, K)` triples (including a non-multiple-of-
  tile case) against the Rust oracle.

After a selected EC2/Vitis run, promote one dynamic-dim representative into the
validation roster and run a full-roster refresh.

### Stage C — Par legality over the parametric family

- Extend the `ParRxC` name/factor coherence guard
  (`crates/spatial-rs-core/src/adapter_names.rs`,
  `dense2d_tile_k_named_schedule_factors`) so row/col partial-loop factors from
  `{1,2,4,8,16}` are accepted iff they divide the static tile dims, across the
  parametric family rather than the enumerated profiles.
- Non-dividing or non-partial-loop `par` stays fail-closed with stable
  diagnostics.

## Code Touchpoints (verify before editing; cite file:line in the log)

- Payload: `crates/spatial-rs-core/src/ir.rs` — struct `Dense2dTileKMemFold`
  and `Dense2dTileKMemFoldProfile` (the `(row_bound, col_bound, k_bound,
  row_par, col_par)` match that selects the profile).
- Classifier: `crates/spatial-rs-core/src/classifier/tiled2d/tile_k.rs` —
  `classify_dense2d_tile_k_memfold`, `tile_k_memfold_candidate_precheck`, and
  the staged proof helpers (`prove_tile_k_source_shape`,
  `prove_tile_k_phase_spine`, `prove_tile_k_access_roles`,
  `prove_tile_k_fold_schedule`). Tile counts are already validated from loop
  bounds rather than source-shape matching, which is the hook dynamic dims
  builds on.
- Frontend surface for runtime scalar dims: `crates/spatial-rs-core/src/frontend/`
  and the Lab2 bridge `frontend/lab2_gemm_bridge.rs`.
- HLS lowering: `crates/spatial-rs-hls/src/tile_k.rs` (kernel frame, loop
  bounds, local storage, partitions) and `crates/spatial-rs-hls/src/plan.rs`.
- Oracle for the harness: `crates/spatial-rs-core/src/oracle.rs`.
- Roster + runners: `examples/ee109/src/lib.rs` (`validation_programs()`),
  `examples/ee109/src/bin/run-vitis-validation.rs`.

## Fail-Closed Boundary

- No generic Spatial `MemFold`, no inferred banking, no schedule inference
  beyond the explicit par legality model.
- No `Float`; only `Int` and exactly `FixPt[TRUE,_24,_8]`.
- No raw Scala ingress (retired and staying retired).
- Dynamic tile *sizes* stay out of scope; only dynamic *dimensions* with
  static tile sizes are admitted.
- Non-multiple dimensions are handled by the runtime tail guards, not by
  silently rounding; a dimension smaller than one tile must still be correct
  or fail closed with a stable diagnostic.

## TDD Plan (red first)

Stage A:
- RED `cargo test -p spatial-rs-core --locked classifies_tile_k_static_shape_family -- --nocapture`
  (a new shape off the enumerated profiles).
- RED `cargo test -p spatial-rs-hls --locked --test m1_codegen tile_k_static_shape_family_harness_matches_oracle -- --nocapture`.
- Fail-closed: non-dividing tile, wrong element type, reserved lab name.

Stage B:
- RED `cargo test -p spatial-rs-core --locked classifies_tile_k_dynamic_dimensions -- --nocapture`.
- RED manifest test: runtime-dim scalar ports appear in ordinal order.
- RED `cargo test -p spatial-rs-hls --locked --test m1_codegen tile_k_dynamic_dims_harness_sweeps_sizes_vs_oracle -- --nocapture`.
- Fail-closed: dynamic tile size, missing dim port, dim/port ordinal mismatch.

Stage C:
- RED par-legality tests: dividing factor accepted, non-dividing rejected with
  stable `ParRxC` diagnostic, across two shapes.

## EC2 / Vitis Evidence Steps

The EC2 host `[ec2-alias]` (see `~/.ssh/config`) was **unreachable on
2026-07-07** (SSH to `[old-ec2-host — see private/ec2-lane.md]:22` timed out —
instance likely stopped). Before claiming any G8 vendor tick:

1. Confirm the instance is running and reachable:
   `ssh [ec2-alias] "source /tools/Xilinx/2025.1/Vitis/settings64.sh; vitis-run --version"`.
   If the hostname changed, update `~/.ssh/config` (the IP is dynamic on
   stop/start unless an Elastic IP is attached).
2. Selected run for one new representative:
   `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --kernel <NewKernel> --out target/vitis-validation-<slug>-run`
   on the EC2 host.
3. Import the trimmed evidence dir under `docs/vitis-validation/`, then
   validate locally:
   `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --validate-evidence docs/vitis-validation/<dir> --mode both`.
4. Roster promotion (Stage B): full-roster
   `--execute --mode both` refresh, then update the current-head anchor in
   README, this contract, the checklist, and the progress log together.

## Resume State (2026-07-07)

- Checklist and this contract are committed; no G8 code exists yet.
- Start at Stage A. It is the smallest increment that generalizes real
  machinery and is independently valuable even before dynamic dims.
- The workspace is green at `639f2de9` plus the diagnostic-stability slice
  committed the same day (see [[progress-log]] `2026-07-07`).
- Keep gpt-5.5 xhigh reviewers in the loop per the project rule if executing
  under a subagent workflow; this session ran solo on Claude Fable 5 at the
  user's direction.
