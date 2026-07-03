---
type: log
project: spatial-spec
---

# Progress Log

Append-only, newest-first within day blocks. One line per discrete action when possible.

---

## 2026-07-03 — Rust rewrite HLS plan provenance

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
