---
type: hls-mapping
construct: ee109-hls-stability-matrix
category: rework
status: current
date: 2026-07-02
stage: 1D
depends_on:
  - "[[80 - Stage1 EE109 HLS Expansion Plan]]"
  - "[[82 - Lab1Part2 DRAM SRAM Scout]]"
---

# EE109 HLS Stability Matrix

## Scope

This note records the local stability state after the first EE109 HLS expansion pass on the Spatial branch `David/HLS-spatial`.

The supported claim is deliberately narrow: the selected EE109 examples compile
through the local Spatial `--hls` lane into HLS-style C++, host-compile with
the system `c++`, pass their generated harnesses, and for the current Rust
rewrite 39-program roster pass EC2/Vitis `csim_design` and `csynth_design`.
This is still not board execution, Vivado implementation, timing closure, or a
generic Spatial compatibility claim.

Current Rust rewrite delta, 2026-07-05: the 39-program current-head refresh at
Rust commit `00797aed` is now the active vendor-HLS checkpoint. The full
39-program roster passed EC2/Vitis 2025.1 `csim_design` and `csynth_design`
after locking `FixPt[TRUE,_24,_8]` lowering to signed truncation/wrap,
promoting the exact full-K
`MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` schedule canary,
promoting the non-Part6
`MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34`
row/column/K-tail schedule canary, and refreshing the scheduled canonical
Tile-K bulk IO cleanup.
Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`.
This supersedes older notes below that say the active anchor remains
`a62eb274`, `7a350983`, `eb4f6236`, `c862e57a`, `b91118f7`, or the
fixed-point-policy 37-program checkpoint, and also supersedes the earlier
`746d9ec5` 39-program current-head bundle. The bundle validates as
`resource_fit=37/39`, `over_budget=2`, and `ii_caveated=14`, so this is HLS
acceptance evidence, not board/resource-fit implementation evidence for the
two over-DSP Tile-K schedules.

Current local frontend/HIR cleanup, 2026-07-05: Rust commit `ce517499`
(`Resolve Stencil2d proof facts`) moves `Stencil2d v0` and the exact Lab3
Sobel adapter onto resolver-backed input/output/local-memory symbols,
row/column/shift loop domains, row-range load/store index facts, `RegFile`
reset/shift effects, line-buffer shift reads, line-output writes, and exact
horizontal/vertical reducer-symbol identities before checked IR emission. It
preserves the same checked payloads and HLS contract. The resolver now
explicitly rejects swapped Sobel reduce-index facts such as
`sr[yh, xh] * kh[yh, xh]` against the canonical local-window proof. Local
core Stencil2d/Lab3, HLS Stencil2d/Lab3 equality, evidence-validator, full
workspace, clippy, fmt, and diff checks pass.
This does not add a validation roster member, fresh EC2/Vitis evidence,
generated HLS changes, manifest changes, generic `LineBuffer`/`RegFile`/
`Reduce` lowering, broader Sobel variants, board execution, or broader Scala
source compatibility.

Previous local frontend/HIR cleanup, 2026-07-05: Rust commit `c344521b`
(`Resolve ControlFsm proof facts`) moved `ControlFsm v0` and the exact Lab2
FSM adapters onto resolver-backed output/scratch/reg/state symbols, FSM loop
domain, scratch write effects, reg-value read facts, and final output
store-range facts before checked IR emission without changing generated HLS,
manifests, validation-roster membership, or vendor-HLS evidence.

Earlier local frontend/HIR cleanup, 2026-07-05: Rust commit `879e8c21`
(`Resolve ScalarExpr proof facts`) moved `ScalarExpr v0` onto resolver-backed
scalar input/output roles, symbols, `Int` types, port ordinals, expression read
symbols, integer expression counts, and zero memory access/effect facts before
checked IR emission without changing generated HLS, manifests,
validation-roster membership, or vendor-HLS evidence.

Earlier local frontend/HIR cleanup, 2026-07-05: Rust commit `5b6d9d3c`
(`Resolve LUT proof facts`) moved `LutLookup v0` and the Lab2 LUT adapters onto
resolver-backed table/input/row/column/output symbols plus rank-2 table read
index facts before checked IR emission without changing generated HLS,
manifests, validation-roster membership, or vendor-HLS evidence.

Earlier local frontend/HIR cleanup, 2026-07-05: Rust commit `98d0d3fe`
(`Resolve Dense1d proof facts`) moved `Dense1dTileScalarMul v0` and the Lab1
DRAM/SRAM adapter onto resolver-backed input/output/scalar/tile/lane symbols
and unit-stride tile load/store range facts before checked IR emission without
changing generated HLS, manifests, validation-roster membership, or vendor-HLS
evidence.

Current promoted Vitis update, 2026-07-05: the Rust rewrite now accepts
and validates the exact full-K Tile-K schedule canary
`MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32`. The checked payload
preserves `partial_row_par=4` and `partial_col_par=16`; HLS lowering emits the
matching row-cyclic array partitions, row/column unroll pragmas, and host
harness. Non-dividing schedule factors such as `3x16` remain fail-closed.
Local core Tile-K, HLS Tile-K, full `m1_codegen`, validation-roster, and
EC2/Vitis `csim_design` / `csynth_design` checks pass. The Vitis report reaches
II=1 for the scheduled compute/update loops, but the final C writeback loop
emits II-violation warnings and the report estimates 256 DSP against 220
available, so this is HLS-acceptance evidence rather than resource-fit
implementation evidence.

Current evidence-quality update, 2026-07-05: Rust commit `88c7df1a`
(`Report Vitis resource quality caveats`) extends the local Vitis evidence
parser and validator to read resource totals, available resources,
utilization, II-violation warning counts, and max final II from the stable
reports/logs. That 38-program bundle validates with
`resource_fit=37/38`, `over_budget=1`, and `ii_caveated=14`; the later active
39-program bundle validates with `resource_fit=37/39`, `over_budget=2`, and
`ii_caveated=14`. This is a machine-readable quality boundary over the
existing evidence, not a board-fit claim.

Current one-off Vitis update, 2026-07-05: the exact non-roster
`MatrixTileMemFoldTailFixPt5x7x5` canary now has compact EC2/Vitis 2025.1
evidence in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-fixpt-tail-oneoff/`.
The single-kernel run passed `csim_design` and `csynth_design` with return code
0, estimated Fmax 136.99 MHz, 10 ns target clock, 7.300 ns estimated clock, and
resource fit true for `xc7z020-clg400-1`. The Rust evidence validator now
revalidates this as selected diagnostic evidence with `resource_fit=1/1`,
`over_budget=0`, and `ii_caveated=0`. This is not a validation-roster
promotion, full roster refresh, board execution, or generic FixPt tail support.

Current validation-tooling update, 2026-07-05: Rust commit `38ade9d2`
(`Support selected Vitis validation kernels`) adds an exact `--kernel NAME`
filter to `run-vitis-validation`. Selected plan-only and execute runs now use
the same validation-program lookup as the full roster, and
`--validate-evidence DIR --kernel NAME` validates exact one-kernel evidence
bundles while rejecting a full 38-program checkpoint for selected validation.
This is EC2/Vitis workflow hardening only; it adds no new HLS semantics, no
new validation member, and no fresh vendor run by itself.

Current selected-run Vitis update, 2026-07-05: the first selected-kernel
EC2/Vitis run using commit `38ade9d2` validates
`MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` as an exact one-kernel evidence
bundle. The selected run passed `csim_design` and `csynth_design` with return
code 0, estimated Fmax 136.99 MHz, 10 ns target clock, 7.300 ns estimated
clock, and resource fit true on `xc7z020-clg400-1`. The local selected
validator reports `kernels=1 resource_fit=1/1 over_budget=0 ii_caveated=0`.
Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-outerk-38ade9d2/`.
This is supplemental selected-run evidence and does not replace the current
39-program vendor anchor; it was captured beside the then-current 38-program
checkpoint and remains historical selected evidence.

Current selected-run caveat update, 2026-07-05: Rust commit `6d461260`
(`Record selected outer-k Vitis evidence`) was used to run the known
over-resource-budget
`MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` canary through the
selected-kernel EC2/Vitis lane. The selected run passed `csim_design` and
`csynth_design` with return code 0 and estimated Fmax 136.99 MHz, but the
selected evidence validator reports
`kernels=1 resource_fit=0/1 over_budget=1 ii_caveated=1`. The report records
256 DSP against 220 available, and the log records six II-violation warnings
with max final II 16 on the final C writeback loop. Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-par4x16-6d461260/`.
This proves selected-run caveat accounting; it is still HLS-acceptance
evidence, not board-fit implementation evidence.

Current selected-run scheduled-tail update, 2026-07-05: source commit
`f2833216` was used to run
`MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34` through
the selected-kernel EC2/Vitis lane. The selected run passed `csim_design` and
`csynth_design` with return code 0, estimated Fmax 136.99 MHz, 10 ns target
clock, 7.300 ns estimated clock, and resource fit true on `xc7z020-clg400-1`.
The local selected validator reports
`kernels=1 resource_fit=1/1 over_budget=0 ii_caveated=0`. Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-selected-scheduled-row-col-k-tail-f2833216/`.
This proves selected-run evidence quality for the exact fixed `33x35x34`
scheduled row/column/K-tail canary; it is not arbitrary tail support, a
full-roster refresh, board execution, Vivado implementation, or timing closure.

Current local no-fresh-Vitis update, 2026-07-05: Rust commit `4834a9c8`
(`Recover dense MemFold tail bounds by role`) hardens the non-outer-K
`Dense2dTileMemFold` classifier/proof boundary for the local
`MatrixTileMemFoldTail5x7x5` canary. The canonical `row_limit` and `col_limit`
tail-bound lets are recovered by role in either declaration order while the
five compute phases remain ordered and the checked payload, generated HLS,
manifest, validation roster, and imported Vitis evidence remain unchanged.
This is local fail-closed guard work only, not a new Vitis execution or broader
tail-support claim.

Current vendor-HLS refresh, 2026-07-05: Rust commit `00797aed` (`Accept
scheduled Tile-K bulk IO`) now has a full 39-program current-head EC2/Vitis
checkpoint at
`docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`. The
earlier local-only source cleanup accepted exact scheduled Part6 canonical
arrow bulk tile IO for the full-K
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` Tile-K canary when
only the partial-product loops carry literal `par 2` / `par 16`; this fresh
bundle proves the unchanged 39-program roster through Vitis `csim_design` and
`csynth_design` after that cleanup. Generic `par`, symbolic canonical `par`,
non-partial-loop `par`, `numel_k`, tails, raw Scala wrappers, board execution,
timing closure, and resource-fit implementation claims remain unsupported.

Current local no-fresh-Vitis update, 2026-07-05: Rust commit `5b428158`
(`Accept canonical Tile-K bulk IO`) accepts canonical Rust-subset arrow bulk
tile IO for the exact full-K
`MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` Tile-K canary. The accepted
source lowers to the same checked payload and exact generated HLS/manifest as
the expanded loop canary. The old Lab2 shell aliases remain confined to the
Lab2 bridge paths, and `numel_k`, Part6 `par`, and tail semantics remain
outside this canonical full-K source spelling. Validation roster membership,
imported Vitis evidence, and vendor-HLS claims are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `89b637ed`
hardens the raw Lab2 fixed GEMM ingress. The `Lab2Part5GEMM` /
`Lab2Part6GEMM` adapter now proves runtime profile facts and the exact `Accel`
island from the matched raw `@spatial class`, rejecting donor class/object
bodies elsewhere in the same source. This is local fail-closed guard work only;
generated HLS C++, manifests, validation-program membership, imported Vitis
evidence, and the then-active `a62eb274` vendor-HLS anchor are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `5af91664`
hardens the raw Lab2 simple `MemReduce` / `MemFold` ingress. The adapter now
binds the accepted `Accel` island to the matched raw `@spatial class`, and
direct tests prove the promoted `MemReduceFives8` / `MemFoldSevens12` profiles
do not widen raw Scala adapter admission or reuse reserved raw Lab2 names.
This is local fail-closed guard work only; generated HLS C++, manifests,
validation-program membership, imported Vitis evidence, and the active
`a62eb274` vendor-HLS anchor are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `88e33a09`
adds a named `Dram2dCopyPlan` body and moves rank-2 copy plan-to-renderer
validation into `spatial_rs_hls::rank2_copy`. The shared
`rank2_copy_frame_from_plan` helper now rejects malformed internal copy plans
unless ABI params are exactly `[input, output]` in order before kernel or
harness rendering. This is backend structure only; accepted syntax, generated
valid HLS, manifests, validation membership, imported Vitis evidence, and the
active `7a350983` vendor-HLS anchor are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `52953ae0`
replaces the Tile-K fold schedule-only helper with
`TileKFoldUpdateProof`. The proof records update domains, effective bounds,
local tile roles, and serial/scheduled partial-product par factors after the
existing partial-product and C-accumulation resolved-fact checks pass. This is
frontend/HIR proof structure only; accepted syntax, checked payloads,
generated HLS, manifests, validation membership, imported Vitis evidence, and
the active `7a350983` vendor-HLS anchor are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `2841cc56`
moves Tile-K body/ABI-param adaptation into `spatial_rs_hls::tile_k`. The
shared `tile_k_frame_from_plan` helper now rejects malformed internal Tile-K
plans unless ABI params are exactly `[lhs, rhs, c_inout]` in order before
kernel or harness rendering. This is backend structure only; accepted syntax,
generated valid HLS, manifests, validation membership, imported Vitis evidence,
and the active `7a350983` vendor-HLS anchor are unchanged.

Current local no-fresh-Vitis update, 2026-07-04: `MemReduceFill v0` /
`MemFoldFill v0` now accept supported static rank-1 lengths beyond the 16-lane
lab representative and arbitrary integer literal temp fills in the bounded
Rust/Spatial-ish frontend path. Local canaries `MemReduceFives8` and
`MemFoldSevens12` prove parser/classifier payloads plus HLS emission and
host-harness execution. Fail-closed tests still reject nonliteral fills,
unsupported lengths, extra local memories/effects, rank-2 reductions, missing
stores, and bad MemFold zero-initialization. At the time, this did not change
the 35-program validation roster or raw Lab2 adapter admission; exact raw Lab2
Part1/Part2 Scala adapters remain all-ones 16-lane compatibility wrappers. The later
`a62eb274` run promotes `MemReduceFives8` and `MemFoldSevens12` into the
37-program vendor-proven roster.

Current local no-fresh-Vitis update, 2026-07-04: Rust commit `c4f8eea6`
extends the quarantined raw `Lab2Part5GEMM` and `Lab2Part6GEMM` adapters to
admit the exact lab
row/column/K-tail runtime tuple `runtimeArgs = "33 35 34"`. Part5 maps to the
existing `MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34` payload and
Part6 maps to
`MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`, with
parser, generated HLS, and manifest equality against those existing
Vitis-proven canaries. Near-miss dimensions and wrong Part6 par factors remain
fail-closed. This does not change the 35-program validation roster or imported
Vitis evidence.

Current Rust rewrite delta, 2026-07-03: commit `d521a0f` added
`MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34` as the
35th local validation-program member. The canary proves scheduled Part6
Tile-K row/column/K tail bounds locally and through EC2/Vitis: load/store loops
stay runtime-bounded by `row_limit`/`col_limit`, scheduled compute loops stay
static at the 16-wide tile bounds, and inactive lanes are guarded. The full
35-program roster now passes Vitis `csim_design` and `csynth_design` on
`xc7z020-clg400-1`. Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-scheduled-row-col-k-tail-35-program/`.

Later no-fresh-Vitis policy update, 2026-07-03: Rust commit
`702d1819e833d856820ff83bc9d1adb262e52b8a` retired the raw Scala source
ingress for `Lab2Part4LUT` and `Lab2Part4LUTNonSquareExample` while keeping
the canonical square/non-square LUT payloads, generated HLS, manifests,
harnesses, validation roster, and historical Vitis evidence unchanged. Local
dry-run byte comparisons against the pre-retirement `d0d6c0f` baseline matched
for `Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`, and `LutBiasLookup`
`kernel.cpp`, `harness.cpp`, and `manifest.json`. This is a source-ingress
retirement only, not new vendor-HLS evidence.

Later no-fresh-Vitis policy update, 2026-07-03: Rust commit
`1e564a79332d45103413cc4f3d1d9ae86a3bc0c0` retired the raw Scala source
ingress for `Lab2Part3BasicCondFSMAlt` while keeping the canonical alternate
FSM payload, generated HLS, manifests, harnesses, validation roster, and
historical Vitis evidence unchanged. Local dry-run byte comparisons against
the pre-retirement `702d181` baseline matched for `Lab2Part3BasicCondFSM`,
`Lab2Part3BasicCondFSMAlt`, and `ControlFsm32` `kernel.cpp`, `harness.cpp`,
and `manifest.json`. This is a source-ingress retirement only, not new
vendor-HLS evidence.

Current Rust rewrite delta, 2026-07-03: commit `a30ec96` is now the active
current-head vendor-HLS checkpoint. The full 35-program roster passed
EC2/Vitis 2025.1 `csim_design` and `csynth_design` after raw Lab2 LUT/FSM-alt
ingress retirement and Rust/Cargo 1.75 CLI test hardening. Durable evidence:
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-raw-ingress-retire-a30ec96-35-program/`.

Later no-fresh-Vitis policy update, 2026-07-03: Rust commit
`47f9baa43f455f6078a514098f25ad7815a58298` bridged the accepted raw Lab2 GEMM
Part5/Part6 wrappers to neutral checked-IR Tile-K profiles. The parser now
checks the generated frontend program against the expected profile, while
accepted raw syntax, generated HLS, manifests, validation membership, and
imported Vitis evidence are unchanged. No fresh EC2/Vitis run was needed for
this profile bridge at the time; its then-active current-head vendor-HLS anchor
was `eb4f6236`, now superseded by the `7a350983` refresh.

Rust commit `0f16af3e7b042554369ce69972da580078651c6a` tightened the known
local Lab3 teaching wrapper from exact raw-wrapper equality to a scoped source
proof. The adapter now records direct class image facts before `main`, main
setup facts before the single `Accel`, and local-window facts for
`lb`/`sr`/`lineOut`, `kh`/`kv`, row/column/shift loops, border handling, and
the `par 16` store before canonical `Lab3Part1Convolution` payload emission.
Generated HLS, manifests, validation membership, and imported Vitis evidence
are unchanged, so no fresh EC2/Vitis run was needed for this source-proof
cleanup at the time; its then-active current-head vendor-HLS anchor was
`eb4f6236`, now superseded by the `7a350983` refresh.

Current local no-fresh-Vitis update, 2026-07-04: the same quarantined raw
Lab3 teaching adapter now accepts the exact static-kernel border predicate
`r < Kh - 1 || c < Kw - 1` as equivalent to the existing
`r < pad_r || c < pad_c` proof form. Parser, generated HLS, and manifest
equality against the canonical `Lab3Part1Convolution` payload are preserved;
swapped `Kh`/`Kw` border expressions remain fail-closed. This does not change
the 35-program validation roster or imported Vitis evidence.

A landed Rust follow-up, commit `5c21c48520b96425ee4303185ce262c699e02ac5`,
records the accepted `Stencil2d v0` Sobel source shape plus resolved
row/column/shift local-window facts in a private classifier proof object, and
checked IR rejects flattened stencil extents beyond the supported HLS/harness
`int` indexing range before HLS planning. Accepted syntax, generated HLS,
manifests, validation membership, and imported Vitis evidence are unchanged, so
no fresh EC2/Vitis run was needed for this proof/preflight cleanup at the time;
its then-active current-head vendor-HLS anchor was `eb4f6236`, now superseded
by the `7a350983` refresh.

A second verified working-tree cleanup tightens the same raw Lab3 ingress:
the accepted raw `Accel` island must be a direct top-level statement in `main`,
so identical accelerator text hidden inside a helper is rejected fail-closed.
This is source-scope hardening only. Local source-adapter, raw-lab, fmt, diff
hygiene, clippy, core, EE109 examples, and HLS package tests passed; generated
HLS, manifests, validation membership, and imported Vitis evidence are
unchanged. This checkpoint also landed in Rust commit
`5c21c48520b96425ee4303185ce262c699e02ac5`.

A third verified working-tree cleanup moves the `Fifo1dTileScalarMul`
host-harness renderer into `spatial_rs_hls::fifo`, beside the FIFO kernel
frame. This is a backend helper-boundary cleanup only: `emit.rs` remains the
plan dispatcher and ABI adapter, generated FIFO kernel text, manifests,
validation membership, and imported Vitis evidence are unchanged, and no fresh
EC2/Vitis run is needed. This checkpoint also landed in Rust commit
`5c21c48520b96425ee4303185ce262c699e02ac5`.

A fourth verified working-tree cleanup moves the Lab3 convolution and reusable
`Stencil2d v0` Sobel host-harness renderers into `spatial_rs_hls::stencil2d`,
beside the Sobel kernel frame. This is also a backend helper-boundary cleanup:
`emit.rs` remains the plan dispatcher and ABI adapter, generated Lab3/Stencil2d
kernel text, manifests, validation membership, and imported Vitis evidence are
unchanged, and no fresh EC2/Vitis run is needed. This checkpoint also landed in
Rust commit `5c21c48520b96425ee4303185ce262c699e02ac5`.

A fifth verified working-tree cleanup adds a full exact emitted-kernel snapshot
for `MatrixTileMemFoldInPlaceFixPt4x6x5`, the non-outer-K in-place
fixed-point MemFold canary. This is a local test-coverage guard only: generated
HLS, manifests, validation membership, and imported Vitis evidence are
unchanged, and no fresh EC2/Vitis run is needed.

A sixth verified working-tree cleanup moves the rank-2 tile-scalar
`MatrixTileScale4x6` host-harness renderer into
`spatial_rs_hls::tile_scalar_mul`, beside the existing kernel frame. This is a
backend helper-boundary cleanup only: generated kernel text, manifests,
validation membership, and imported Vitis evidence are unchanged, and no fresh
EC2/Vitis run is needed.

A seventh verified working-tree cleanup moves `Dense2dTileKMemFold v0`
host-harness rendering into `spatial_rs_hls::tile_k`, beside the existing
Tile-K kernel frame/body helpers. This is a backend helper-boundary cleanup
only: generated kernel text, manifests, validation membership, and imported
Vitis evidence are unchanged, and no fresh EC2/Vitis run is needed.

An eighth verified working-tree cleanup hardens `Dense2dTileScalarMul v0`
classifier admission: the load and store tile-copy phases now pass through the
shared resolver-backed rank-2 tile-copy fact helper after structural matching.
This checks same access grouping, same parent statement, loop-symbol identity,
and const-backed stride provenance before reconstructing the existing checked
payload. Generated kernel text, manifests, validation membership, and imported
Vitis evidence are unchanged, and no fresh EC2/Vitis run is needed.

A ninth verified working-tree cleanup hardens `Dense2dTileDotAccum v0`
classifier admission: the lhs load, rhs load, and final accumulator store now
pass through resolver-backed rank-2 access facts after structural matching.
This checks same access grouping, same parent statement, loop-symbol identity,
and const-backed stride provenance before reconstructing the existing checked
payload. Generated kernel text, manifests, validation membership, and imported
Vitis evidence are unchanged, and no fresh EC2/Vitis run is needed.

A tenth verified working-tree cleanup moves the `MatrixTileAccum4x6x5`
host-harness renderer into `spatial_rs_hls::dot_accum`, beside the existing
rank-2 dot-accum kernel frame. This is a backend helper-boundary cleanup only:
generated kernel text, manifests, validation membership, and imported Vitis
evidence are unchanged, and no fresh EC2/Vitis run is needed.

An eleventh verified working-tree cleanup moves the non-outer-K
`Dense2dTileMemFold v0` host-harness renderer into `spatial_rs_hls::memfold`,
beside the existing MemFold kernel frame. Split-C, tail, exact fixed-point, and
explicit in-place C harness paths still route through `emit.rs` as the plan
dispatcher and ABI adapter. This is a backend helper-boundary cleanup only:
generated kernel text, manifests, validation membership, and imported Vitis
evidence are unchanged, and no fresh EC2/Vitis run is needed.

A twelfth verified working-tree cleanup moves the
`Lab1Part2DramSramExample` / `DenseScale64` host-harness renderer into
`spatial_rs_hls::dense1d_tile_scalar_mul`, beside the existing rank-1 Dense1d
kernel frame. This is a backend helper-boundary cleanup only: generated kernel
text, manifests, validation membership, and imported Vitis evidence are
unchanged, and no fresh EC2/Vitis run is needed.

A thirteenth verified working-tree cleanup moves square/non-square lab LUT and
`LutBiasLookup` host-harness rendering into `spatial_rs_hls::lut`, beside the
existing LUT kernel frame. This is a backend helper-boundary cleanup only:
generated kernel text, manifests, validation membership, and imported Vitis
evidence are unchanged, and no fresh EC2/Vitis run is needed.

A fourteenth verified working-tree cleanup moves `ScalarExpr v0`,
`ScalarReduce v0`, `ScalarFold v0`, and `ScalarSramTileFold v0` host-harness
rendering into `spatial_rs_hls::scalar`, beside the existing scalar kernel
frames. This is a backend helper-boundary cleanup only: generated kernel text,
manifests, validation membership, and imported Vitis evidence are unchanged,
and no fresh EC2/Vitis run is needed.

A fifteenth verified working-tree cleanup moves `MemReduceFill v0` and
`MemFoldFill v0` host-harness rendering into
`spatial_rs_hls::mem_reduction_fill`, beside the existing fill kernel frame.
This is a backend helper-boundary cleanup only: generated kernel text,
manifests, validation membership, and imported Vitis evidence are unchanged,
and no fresh EC2/Vitis run is needed.

## 2026-07-03 Rust Rewrite Raw-Adapter Retirement 35-Program Vitis Checkpoint

The Rust rewrite branch `David/HLS-spatial` passed the full 35-program EE109
validation roster through EC2/Vitis at source commit `a30ec96`.

Evidence:
- Remote host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`)
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/raw-ingress-retire-35-a30ec96/spatial-rs`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-raw-ingress-retire-a30ec96-35-program/`
- Result: all 35 programs reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- Evidence validator: passed for
  `2026-07-03-raw-ingress-retire-a30ec96-35-program/`.
- EC2 Rust/Cargo gate: passed under `cargo 1.75.0` / `rustc 1.75.0`.
- This refresh covers the raw Lab2 LUT/FSM-alt ingress retirement head and the
  Cargo 1.75-compatible CLI integration-test harness.

Evidence boundary:
- This validates Vitis C simulation and HLS synthesis for the exact 35-program
  Rust rewrite roster at `a30ec96`.
- It does not validate board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM support, automatic banking inference, broader `par` inference, II=1 for
  every loop, or performance optimality.

## 2026-07-03 Rust Rewrite Scheduled Row/Column/K-Tail Vitis Checkpoint

The Rust rewrite branch `David/HLS-spatial` passed the full 35-program EE109
validation roster through EC2/Vitis at source commit `d521a0f`.

Evidence:
- Remote host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`)
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/scheduled-row-col-k-tail-35-d521a0f/spatial-rs`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-scheduled-row-col-k-tail-35-program/`
- Result: all 35 programs reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- Evidence validator: passed for
  `2026-07-03-scheduled-row-col-k-tail-35-program/`.
- EC2 Rust/Cargo gate: passed with a Rust/Cargo 1.75-compatible local
  lockfile and package `rust-version = "1.75"` declarations. The historical
  35-program run still used a remote-only lockfile rewrite; this working tree
  carries the compatible lockfile locally for future captures.
- New scheduled row/column/K-tail canary
  `MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34`
  reported estimated Fmax 136.99 MHz, estimated clock 7.300 ns, latency
  2707-26872 cycles, interval 2708-26873 cycles, and utilization estimate
  58 BRAM_18K, 131 DSP, 19307 FF, 13628 LUT, and 0 URAM.

Evidence boundary:
- This validates Vitis C simulation and HLS synthesis for the exact 35-program
  Rust rewrite roster, including the scheduled Tile-K row/column/K-tail canary
  with guarded inactive lanes.
- It does not validate board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM support, automatic banking inference, broader `par` inference, II=1 for
  every loop, or performance optimality.

## 2026-07-03 Rust Rewrite Row/Column/K-Tail Vitis Checkpoint

The Rust rewrite branch `David/HLS-spatial` passed the full 34-program EE109
validation roster through EC2/Vitis at source commit `2087625`.

Evidence:
- Remote host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`)
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/row-col-k-tail-34-2087625/spatial-rs`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-row-col-k-tail-34-program/`
- Result: all 34 programs reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- New serial row/column/K-tail canary
  `MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34` reported estimated
  Fmax 136.99 MHz, estimated clock 7.300 ns, latency 2329-274840 cycles,
  interval 2330-274841 cycles, and utilization estimate 11 BRAM_18K, 7 DSP,
  4389 FF, 4917 LUT, and 0 URAM.

Evidence boundary:
- This validates Vitis C simulation and HLS synthesis for the exact 34-program
  Rust rewrite roster, including the serial Tile-K row/column/K-tail
  runtime-bound canary.
- It does not validate board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, generic Spatial compatibility, arbitrary
  GEMM support, automatic banking inference, broader `par` inference,
  scheduled row/column tails, II=1 for every loop, or performance optimality.

## Rust Rewrite Vendor HLS Update

On 2026-06-27, the Rust rewrite workspace
`/Users/david/Documents/David_code/spatial-rs` completed a separate Vitis
validation pass for the current accepted adapter set. This is not a Scala
Spatial branch result; it is the Rust rewrite's HLS C++ emitter output.

Environment:

- EC2 host: `[ec2-host — see private/ec2-lane.md]`
- OS: Ubuntu 22.04.5 LTS
- Vitis/Vivado: 2025.1
- Target part: `xc7z020-clg400-1`
- Clock target: 10 ns
- Rust source bundle on EC2:
  `/home/ubuntu/spatial-validation/vitis-20260627-1519/spatial-rs`
- Durable repo evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27/`
- Durable runner replay:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-runner/`

Rust adapters validated by Vitis `csim_design` and `csynth_design`:

| Adapter | Rust Vitis status | Fmax estimate |
|---|---|---|
| `Lab1Part1RegExample` | Pass | 219.68 MHz |
| `Lab1Part1RegThreeInputExample` | Pass | 156.96 MHz |
| `Lab1Part2DramSramExample` | Pass | 127.15 MHz |
| `Lab2Part3BasicCondFSM` | Pass | 136.99 MHz |
| `Lab2Part4LUT` | Pass | 150.65 MHz |
| `Lab2Part4LUTNonSquareExample` | Pass | 170.24 MHz |
| `Lab3Part0MatrixCopyRowMajor` | Pass | 136.99 MHz |
| `Lab3Part1Convolution` | Pass | 136.99 MHz |

Boundary: this validates exact Rust adapter bundles through Vitis C simulation
and HLS synthesis. It does not validate board execution, Vivado
implementation/place-and-route, post-implementation timing closure, or generic
Spatial feature support beyond these adapter shapes.

Follow-up supported-feature run:

On 2026-06-27, the Rust rewrite added `ScalarExpr v0` as the first reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, a non-lab representative
for scalar integer expressions. All nine completed with return code 0,
`csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-scalar-expr/`

`ScalarExpr v0` covers a narrow scalar language: 1-4 scalar `Int` inputs, one
scalar `Int` output, one assignment, declared-input reads, nonnegative integer
literals, `+`, `*`, and parentheses. It still excludes DRAM, memories, control
flow, comparisons, muxes, negative literals, subtraction, division, function
calls, multiple outputs, and multiple statements.

Follow-up dense-memory supported-feature run:

On 2026-06-27, the Rust rewrite added `Dense1dScalarMul v0` as the second
reusable supported feature and re-ran the Vitis lane. The validation list now
contains the same eight accepted adapters plus `ScalarAffine4` and
`DenseScale64`, a non-lab representative for rank-1 tiled DRAM/SRAM
scalar-multiply. All ten completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-dense1d/`

`Dense1dScalarMul v0` covers one rank-1 `Dram<Int>[N]` input, one scalar `Int`
multiplier, one rank-1 `Dram<Int>[N]` output, two rank-1 `Sram<Int>[TILE]`
tiles, positive static `N`/`TILE` with `N % TILE == 0`, unit-stride load,
elementwise multiply, and unit-stride store. It still excludes generic memory
lowering, rank-2 DRAM, dynamic/tail tiles, non-unit strides, extra memories,
arbitrary expressions, FIFO/streams, reductions, aliasing/in-place claims, and
non-`Int` element types.

Follow-up LUT supported-feature run:

On 2026-06-27, the Rust rewrite added `LutLookup v0` as the third reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `DenseScale64`, and
`LutBiasLookup`, a non-lab representative for 2-D row-major LUT lookup. All
eleven completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-lut-lookup/`

`LutLookup v0` covers one 2-D `Lut<Int>[R, C]`, three scalar `Int` inputs
ordered as bias, row, and column, one scalar `Int` output, a rectangular
row-major literal payload, and exactly `out := bias + table[row, col]`. It
still excludes generic table/memory indexing, DRAM, multiple LUTs, computed
indices, swapped row/column roles, arbitrary scalar expressions around the
lookup, runtime bounds checks, dynamic dimensions, and non-`Int` element types.

Follow-up rank-2 copy supported-feature run:

On 2026-06-27, the Rust rewrite added `Dram2dCopy v0` as the fourth reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `DenseScale64`,
`LutBiasLookup`, and `MatrixCopy4x6`, a non-lab representative for rank-2
row-major DRAM copy. All twelve completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-27-dram2d-copy/`

`Dram2dCopy v0` covers one rank-2 `Dram<Int>[ROWS, COLS]` input, one matching
rank-2 output, nested static `foreach` row/column loops, and exactly
`out[row, col] := in[row, col]`. It still excludes generic memory/effect
lowering, rank polymorphism, swapped or computed indices, mismatched shapes,
extra ports/statements, aliasing/in-place claims, stencils, reductions, `par`,
dynamic dimensions, and non-`Int` element types. The original
`Lab3Part0MatrixCopyRowMajor` adapter now routes through the
frontend/HIR/classifier path; `Lab3Part1Convolution` remains an explicit
opaque adapter.

The `2026-06-27-runner` replay used the repo-local `run-vitis-validation`
command. It defaults to plan-only sidecar generation and requires `--execute`
to run Vitis. The EC2 host's system Cargo was 1.75.0, so the copied remote
bundle used a remote-only lockfile v4-to-v3 downgrade; the local Rust repo
lockfile was not changed. The `2026-06-27-dram2d-copy` run used the same
remote-only lockfile adjustment.

Follow-up control, Lab3 frontend/HIR, and Stencil2d runs:

By 2026-06-28, the Rust rewrite had added three more relevant milestones:

- `ControlFsm v0`, represented by `ControlFsm32`, with evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-control-fsm-v0/`.
- Lab3 convolution frontend/HIR routing for the fixed adapter, with evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-lab3-frontend-hir/`.
- `Stencil2d v0`, represented by `SobelStencil12x20`, with fourteen-program
  Vitis `csim_design` and `csynth_design` evidence in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-stencil2d-v0/`.

The `Stencil2d v0` run was executed from Rust commit `2ec05e6` on branch
`David/rust-ee109-mvp`, using EC2 host
`[ec2-host — see private/ec2-lane.md]`, Vitis/Vivado 2025.1, target
`xc7z020-clg400-1`, and 10 ns clock target. All fourteen validation programs
completed with return code 0, `csim=true`, and `csynth=true`; the new
`SobelStencil12x20` representative reported an estimated Fmax of 136.99 MHz.
The remote run again used a remote-only Cargo.lock v4-to-v3 compatibility
adjustment for Cargo 1.75; the local Rust repo lockfile was not changed.

`Stencil2d v0` covers a narrow Sobel-like rank-2 `Int` stencil: one input DRAM,
one matching output DRAM, two static 3x3 Sobel LUTs, one row scratch SRAM,
Lab3-style local-window source classification, top-left zero border, and
`abs(first) + abs(second)` arithmetic. It still does not claim generic
`LineBuffer`, `RegFile`, arbitrary `Reduce`, arbitrary `par`, arbitrary
coefficients, dynamic dimensions, optimized line-buffer scheduling, board
execution, Vivado implementation, place-and-route, or timing closure.

Follow-up scalar-reduction supported-feature run:

On 2026-06-28, the Rust rewrite added `ScalarReduce v0` as the seventh reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`,
`DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`, `ControlFsm32`, and
`SobelStencil12x20`. All fifteen completed with return code 0, `csim=true`,
and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-scalar-reduce-v0/`

`ScalarReduce v0` covers exactly one scalar `Int` output assigned by
`out := reduce i in 0..<len> par <par> { i }` with resolved static constant
values `1 <= len <= 65536` and `par == 1`, no inputs, no DRAM ports, and no
local memories. The validation representative still spells those constants
`N` and `P`, but Rust commit `9797d162` now accepts equivalent Rust-subset
constant names such as `LEN` and `LANES` by resolving the identifiers used in
the reduce syntax. It rejects output-name collisions with generated HLS
temporaries and overflow-sized lengths. It still does not claim generic
`Reduce`, `Fold`, `MemReduce`, `MemFold`, arbitrary reduce bodies, input-DRAM
reductions, non-unit `par`, unbounded `Int` accumulation, board execution,
Vivado implementation, place-and-route, or timing closure.

Follow-up scalar-fold supported-feature run:

On 2026-06-28, the Rust rewrite added `ScalarFold v0` as the eighth reusable
supported feature and re-ran the Vitis lane. The validation list now contains
the same eight accepted adapters plus `ScalarAffine4`, `ScalarReduceSum16`,
`ScalarFoldTileSum32`, `DenseScale64`, `LutBiasLookup`, `MatrixCopy4x6`,
`ControlFsm32`, and `SobelStencil12x20`. All sixteen completed with return
code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-scalar-fold-v0/`

`ScalarFold v0` covers exactly one rank-1 `Dram<Int>[len]` input and one scalar
`Int` output assigned by a tiled fold around a rank-1 indexed reduction:
`out := fold outer in 0..<len> step <tile> { reduce inner in 0..<tile> par <par> { src[outer + inner] } }`.
It requires resolved static constant values `1 <= len <= 65536`, `tile > 0`,
`len % tile == 0`, a matching inner reduce tile bound, and `par == 1`. The
validation representative still spells those constants `N`, `TILE`, and `P`,
but Rust commit `9797d162` now accepts equivalent Rust-subset names such as
`LEN`, `BLOCK`, and `LANES` by resolving the identifiers used in the
fold/reduce syntax. It still does not claim generic `Fold`, generic `Reduce`,
`MemReduce`, `MemFold`, arbitrary bodies, tail tiles, rank-2 inputs, non-unit
`par`, unbounded `Int` accumulation, board execution, Vivado implementation,
place-and-route, or timing closure.

Follow-up memory-reduction semantic-canary run:

On 2026-06-28, the Rust rewrite added the local all-ones `MemReduceFill v0` and
`MemFoldFill v0` semantic canaries and re-ran the Vitis lane. The validation
list now contains 18 programs, adding `MemReduceOnes16` and `MemFoldOnes16` to
the prior sixteen-program ScalarFold checkpoint. All eighteen completed with
return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-mem-reductions-v0/`

`MemReduceFill v0` and `MemFoldFill v0` cover narrow Rust-DSL all-ones local
SRAM accumulation shapes for the simple Lab2 memory-reduction behaviors. They
do not claim original Scala source compatibility, arbitrary reducer/fold
bodies, rank-2 memory reductions, GEMM, fixed-point arithmetic, banking,
streams, scheduling, board execution, Vivado implementation, place-and-route,
or timing closure.

Later raw-wrapper source-adapter updates:

On 2026-07-02, the Rust rewrite promoted the known local `Lab2Part6GEMM` lab
class from source-compatibility-only to a distinct scheduled HLS canary. The
exact fixed `32x32x32`, tile-16, `FixPt[TRUE,_24,_8]`, single-`Accel` token
stream with `par 2` / `par 16` partial-tile loops now canonicalizes to
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, carrying checked
`partial_row_par = 2` and `partial_col_par = 16` schedule metadata. The HLS
branch emits local-array partition pragmas, `PIPELINE II=1`, and row/column
unroll pragmas for the partial-tile multiply and fold-update loops. A fresh
28-program EC2/Vitis 2025.1 run completed with return code 0 for every
validation program; evidence is captured under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-lab2-part6-scheduled/`.
This proves the exact Part6 scheduled canary through `csim_design` and
`csynth_design`, but it does not claim generic Spatial `par`, automatic banking
inference, generic Spatial `MemFold`, dynamic/tail K, K tails, or broad Scala
source compatibility.

Later on 2026-07-02, the Rust rewrite added a local structural source bridge
for that same scheduled Part6 payload. The Lab2-like outer-K frontend/HIR path
now accepts infix tile IO, static offset-loop spelling, and tile-size-first or
remaining-first static `numel_k = min(...)` spelling when the kernel name is the
scheduled Part6 canary and the partial-tile fill loops carry literal `par 2`
and `par 16`, or parser-only `ROW_PAR` / `COL_PAR` aliases resolving to those
same values. Local parser/HIR/classifier tests prove equality with the raw
Part6 scheduled payload, and HLS tests prove generated C++ and manifest
identity. The alias widening is a no-HLS-drift source-admission slice: it does
not add validation-program membership, change generated HLS/manifest output, or
create fresh EC2/Vitis evidence. The earlier exact structural bridge commit was
rerun through the full 28-program EC2/Vitis lane; compact evidence is captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-part6-structural-408e21c/`.

On 2026-07-01, the Rust rewrite added temporary source adapters for the
known local `Lab2Part1SimpleMemReduce` and `Lab2Part2SimpleMemFold` lab
classes, canonicalizing those wrappers to the existing `MemReduceOnes16` and
`MemFoldOnes16` payloads with generated HLS/manifest equality tests. That path
has since been superseded: the raw Scala Lab2 Part1/Part2 memory-reduction
wrappers are retired from quarantined ingress, the old class names remain
reserved, and `MemReduceOnes16` / `MemFoldOnes16` remain the Rust-subset
all-ones representatives. This is not new Vitis evidence and does not broaden
the historical MemReduce/MemFold Vitis checkpoint. Changed output shape,
changed accelerator body, generic Spatial `MemReduce`/`MemFold`, arbitrary
reducer/fold bodies, dynamic bounds, rank-2 reductions, scheduling, banking,
broad Scala source compatibility, board execution, Vivado implementation,
place-and-route, and timing closure remain unsupported.

On 2026-07-02, the Rust-subset `MemReduceFill v0` / `MemFoldFill v0`
classifier was hardened to consume resolved HIR loop/symbol facts for the same
narrow rank-1 `Int` shape. Equivalent static length/step aliases are now
accepted in the Rust-subset source, while the retired raw Lab2 wrapper names
remain reserved and the all-ones semantics stay represented by
`MemReduceOnes16` / `MemFoldOnes16`. This is a local classifier/frontend-HIR
foundation cleanup only: checked payloads, generated HLS, manifests,
validation membership, and existing Vitis evidence are unchanged.

On 2026-07-01, the Rust rewrite also added an exact raw source adapter for the
known local teaching `Lab3Part1Convolution` wrapper from
`/Users/david/Documents/David_code/lab-3-accelerator-bandits/src/test/scala/Lab3.scala`.
It canonicalizes to the existing fixed `Lab3Part1Convolution` / `Stencil2d`
payload and local tests prove parser equality plus generated HLS/manifest
equality. A then-current-head 27-program EC2/Vitis run also proved the
canonical Lab3 payload still passes `csim_design` and `csynth_design` with this
adapter code present; evidence is captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab3-local-raw-wrapper/`.
This does not add a separate raw-wrapper validation program or broaden the
historical Lab3 payload claim. Changed dimensions, changed accelerator shape,
generic Scala `LineBuffer`, `RegFile`, `Reduce`, generalized rotated-kernel
handling, dynamic dimensions, optimized line-buffer scheduling, broad source
compatibility, board execution, Vivado implementation, place-and-route, and
timing closure remain unsupported.

Follow-up FIFO semantic-canary run:

On 2026-06-28, the Rust rewrite added `Fifo1dTileScalarMul v0` and re-ran the
Vitis lane. The validation list now contains 19 programs, adding
`FifoTileScale32` to the prior eighteen-program MemReduce/MemFold checkpoint.
All nineteen completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-28-fifo-v0/`

`Fifo1dTileScalarMul v0` covers a narrow Rust-DSL Lab1 Part4-style tile-scale
shape: one rank-1 DRAM input, one scalar multiplier, one rank-1 DRAM output,
two loop-local `FIFO<Int>[TILE]` memories, ordered enqueue/dequeue tile
scaling, and generated `hls::stream<int>` plus stream-depth pragmas. It does
not claim generic Scala FIFO source compatibility, generic FIFO/streams, AXI
stream ports, LIFO, back-pressure modeling, throughput optimization, board
execution, Vivado implementation, place-and-route, or timing closure. A later
exact raw `Lab1Part4FIFOExample` wrapper now token-matches only the known fixed
Lab1 Part4 source and canonicalizes to this same `FifoTileScale32` payload with
HLS/manifest equality; it is not new Vitis evidence and does not broaden the
historical FIFO Vitis checkpoint. The Scala HLS negative row below remains true
for the legacy Scala backend/source path.

Follow-up rank-2 tiled int scale run:

On 2026-06-29, the Rust rewrite added `Dense2dTileScalarMul v0` and re-ran
the Vitis lane. The validation list now contains 20 programs, adding
`MatrixTileScale4x6` to the prior nineteen-program FIFO checkpoint. All twenty
completed with return code 0, `csim=true`, and `csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-rank2-tiled-int-scale/`

`Dense2dTileScalarMul v0` covers a narrow Rust-DSL rank-2 tiled local-SRAM
integer scale shape: one rank-2 input DRAM, one scalar multiplier, one matching
rank-2 output DRAM, two rank-2 SRAM tiles, exact row/column tile loops, and
load/compute/store phases. The `MatrixTileScale4x6` representative reported
`PASS MatrixTileScale4x6`, an estimated Fmax of 122.68 MHz, and an estimated
clock of 8.151 ns. This evidence does not claim GEMM, fixed-point arithmetic,
tail tiles, generic rank-2 tiling, arbitrary local-memory programs, Scala
source compatibility, board execution, Vivado implementation, place-and-route,
or timing closure.

Follow-up rank-2 tiled dot-accum run:

On 2026-06-29, the Rust rewrite added `Dense2dTileDotAccum v0` and re-ran the
Vitis lane. The validation list now contains 21 programs, adding
`MatrixTileAccum4x6x5` to the prior twenty-program rank-2 tile-scale
checkpoint. All twenty-one completed with return code 0, `csim=true`, and
`csynth=true`.

Additional repo evidence:

- `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-rank2-tiled-dot-accum/`

`Dense2dTileDotAccum v0` covers a fixed-shape Rust-DSL rank-2 tiled `Int`
dot-accumulation canary: two rank-2 input DRAMs `lhs[ROWS,K]` and
`rhs[K,COLS]`, one matching rank-2 output DRAM `out[ROWS,COLS]`, three SRAM
tiles, explicit accumulator zero-init, one static K reduction loop, and
row-major flattened HLS offsets. The `MatrixTileAccum4x6x5` representative
reported `PASS MatrixTileAccum4x6x5`, an estimated Fmax of 121.61 MHz, an
estimated clock of 8.223 ns, latency 84 cycles, and utilization estimate 4
BRAM_18K, 6 DSP, 5013 FF, and 4537 LUT. This evidence does not claim original
Scala `Lab2Part5GEMM`/`Lab2Part6GEMM` source compatibility, fixed-point
arithmetic, tail/min bounds, K tiling, buffered `MemFold`, `par`, generic
GEMM, board execution, Vivado implementation, place-and-route, or timing
closure.

Follow-up rank-2 tiled MemFold-style checkpoint:

On 2026-06-29, the Rust rewrite added `Dense2dTileMemFold v0` as a fixed-shape
Rust-DSL `Int` source-shape GEMM precursor. The validation list now contains
22 programs, adding `MatrixTileMemFold4x6x5` to the prior twenty-one-program
rank-2 dot-accum checkpoint. This checkpoint has local host-C++ harness
coverage and was later included in the 23-program EC2 Vitis execution run
recorded under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-06-29-fixpt-memfold/`.

`Dense2dTileMemFold v0` covers three rank-2 input DRAMs `lhs[ROWS,K]`,
`rhs[K,COLS]`, and `cin[ROWS,COLS]`, one output DRAM `out[ROWS,COLS]`, four
SRAM tiles, C preload into `c_tile`, a `partial_tile = lhs_tile * rhs_tile`
phase, `c_tile += partial_tile` over one static K loop, and row-major flattened
HLS offsets. This moves closer to the EE109 Lab2 GEMM `tileC_sram.buffer` /
`MemFold` lifecycle, but it does not claim original Scala `Lab2Part5GEMM` or
`Lab2Part6GEMM` source compatibility, generic Spatial `MemFold`, fixed-point
arithmetic beyond the exact canary below, tail/min bounds, K tiling, `par`,
banking, performance scheduling, board execution, Vivado implementation,
place-and-route, or timing closure.

Follow-up exact fixed-point MemFold canary checkpoint:

On 2026-06-29, the Rust rewrite added exact `FixPt[TRUE,_24,_8]` support for
the same fixed-shape `Dense2dTileMemFold v0` GEMM precursor. The validation
list now contains 23 programs, adding `MatrixTileMemFoldFixPt4x6x5` after the
`Int` MemFold representative. This checkpoint has local Rust tests, local
host-C++ harness coverage through a host-only `ap_fixed` shim, Vitis
dry-run/plan-only sidecar coverage, and EC2 Vitis 2025.1 `csim_design` plus
`csynth_design` evidence.

The 23-program EC2 run completed with return code 0 on
`[ec2-host — see private/ec2-lane.md]` using
`/tools/Xilinx/2025.1/Vitis/settings64.sh`; every validation program reported
`csim=true` and `csynth=true`. `MatrixTileMemFoldFixPt4x6x5` passed C
simulation with `PASS MatrixTileMemFoldFixPt4x6x5`, finished synthesis, and
reported estimated Fmax 121.61 MHz, estimated clock 8.223 ns, latency 84
cycles, interval 60 cycles, and utilization estimate 6 BRAM_18K, 8 DSP, 6457
FF, and 5919 LUT.

The fixed-point slice widens the Rust frontend/HIR/IR/manifest/HLS type spine
by one concrete type only. All DRAM ports and local SRAM tiles in the accepted
MemFold GEMM canary must use the same element type, either `Int` or exact
`FixPt[TRUE,_24,_8]`; the HLS emitter lowers the latter to `ap_fixed<32, 24>`
with a stable local alias. This evidence does not claim generic fixed-point
widths, decimal fixed-point values, mixed `Int`/`FixPt` GEMM, original Scala
`Lab2Part5GEMM` or `Lab2Part6GEMM` source compatibility, generic Spatial
`MemFold`, tail/min bounds, K tiling, `par`, banking, performance scheduling,
board execution, Vivado implementation, place-and-route, or timing closure.

## Stable Positive Examples

| Example | Surface covered | Local HLS status | Scala parity status |
|---|---|---|---|
| `spatial.tests.ee109.Lab1Part1RegExample` | Two scalar `ArgIn[Int]`, scalar `ArgOut[Int]`, integer add | Pass | Pass |
| `spatial.tests.ee109.Lab1Part1RegThreeInputExample` | Three scalar `ArgIn[Int]`, scalar `ArgOut[Int]`, nested integer add | Pass | Pass |
| `spatial.tests.ee109.Lab1Part2DramSramExample` | One input DRAM, one output DRAM, one scalar arg, fixed 32-element dense tiled load/compute/store | Pass | Pass |
| `spatial.tests.ee109.Lab2Part4LUT` | Constant 2-D integer LUT, row-major lookup, vector width one | Pass | Pass |
| `spatial.tests.ee109.Lab2Part4LUTNonSquareExample` | Non-square constant LUT stride check | Pass | Pass |

## Fail-Closed Negative Examples

| Example | Rejected surface | Expected status |
|---|---|---|
| `spatial.tests.compiler.HLSRejectsUnsupportedFSM` | Basic conditional FSM/control state machine | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab1FIFO` | FIFO construction, enqueue, dequeue | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab1Reduce` | Fold/reduction accumulator surface | Fails with `[hlsgen]` diagnostics |
| `spatial.tests.compiler.HLSRejectsUnsupportedLab3LocalMemories` | RegFile/local memory surface representative of later Lab3 work | Fails with `[hlsgen]` diagnostics |

## Verification Run

Positive and negative local HLS gate:

```bash
SBT_OPTS='-Xmx8G -XX:+UseG1GC' sbt -Dtest.HLS=true '; project spatial; compile; project test; testOnly spatial.tests.ee109.Lab1Part1RegExample spatial.tests.ee109.Lab1Part1RegThreeInputExample spatial.tests.ee109.Lab1Part2DramSramExample spatial.tests.ee109.Lab2Part4LUT spatial.tests.ee109.Lab2Part4LUTNonSquareExample spatial.tests.compiler.HLSRejectsUnsupportedFSM spatial.tests.compiler.HLSRejectsUnsupportedLab1FIFO spatial.tests.compiler.HLSRejectsUnsupportedLab1Reduce spatial.tests.compiler.HLSRejectsUnsupportedLab3LocalMemories'
```

Result: 9 suites completed, 9 tests succeeded, 0 failed.

Positive Scala parity gate:

```bash
SBT_OPTS='-Xmx8G -XX:+UseG1GC' sbt -Dtest.Scala=true '; project spatial; compile; project test; testOnly spatial.tests.ee109.Lab1Part1RegExample spatial.tests.ee109.Lab1Part1RegThreeInputExample spatial.tests.ee109.Lab1Part2DramSramExample spatial.tests.ee109.Lab2Part4LUT spatial.tests.ee109.Lab2Part4LUTNonSquareExample'
```

Result: 5 suites completed, 5 tests succeeded, 0 failed.

Generated-code hygiene:

- No empty generated HLS kernel files were found under `gen/HLS`.
- No positive HLSGen error logs were found for the five supported examples.
- Generated HLS C++ did not contain simulator-only strings such as `FringeContext`, `TopHost`, `Chisel`, `Verilog`, `DRAMSim`, `vcs`, or `instrument`.
- `git diff --check` passed in the Spatial repo.

## Current Limitations

- The original Scala Spatial HLS gate remains a local host-C++ gate. It does
  not invoke Vitis/Vivado HLS, synthesize RTL, check timing, or validate board
  integration.
- For the Rust rewrite, the explicitly listed accepted adapters,
  supported-feature representatives, and canaries through the exact alternate
  Lab2 FSM canary have historical Vitis `csim_design` and `csynth_design`
  evidence through the 31-program
  `docs/vitis-validation/2026-07-02-lab2-fsm-alt-31-program/` checkpoint. The
  active Rust-rewrite vendor-stability anchor is now the 39-program
  `docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`
  checkpoint. The previous scheduled Part6, Tile-K facts, post-refactor
  SRAM-tile fold, Lab3 raw-wrapper, fixed-point-policy, and par4x16 boundaries
  remain preserved under their earlier evidence folders. Board execution,
  Vivado implementation, timing closure, resource-fit implementation for the
  two over-DSP Tile-K schedules, generic
  Spatial `Fold`, arbitrary local-memory folds/effects, arbitrary K-tail shapes
  beyond the named serial and scheduled K-tail canaries, generic `par`,
  broad Scala source compatibility, and broad Spatial coverage remain pending.
- The Lab1Part2 memory lowering is a narrow structural slice, not a general Spatial memory backend. It accepts the selected fixed shape: `N = 32`, `tileSize = 16`, one input DRAM, one output DRAM, two 16-element SRAM tiles, one scalar integer multiplier, and dense unit-stride transfers.
- The Lab1Part2 generated harness uses an independent vector oracle, but the source initialization is currently fixed to the selected EE109 shape `src(i) = i % 256`.
- FIFO outside the exact raw Lab1 Part4 wrapper / `FifoTileScale32` semantic
  shape, generic reductions/folds, generic memory reductions/folds, generic
  FSMs, generic RegFile/LineBuffer lowering, dynamic sizes, non-unit strides,
  and non-`Int` element types beyond the exact Rust
  `FixPt[TRUE,_24,_8]` MemFold canary remain unsupported in HLS mode and should
  stay fail-closed until selected intentionally.
- The known local Lab3 teaching raw wrapper is now a scoped source-proof
  adapter only. It preserves the existing Vitis-proven
  `Lab3Part1Convolution` payload locally; the fresh current-head EC2/Vitis run
  proves the canonical payload with this adapter code present, not a distinct
  raw-wrapper validation program.
- The Scala runs still emit the existing `libisl appears to be missing` warning. That warning does not block these local regression results, but it is separate from vendor HLS readiness.

## Recommended Next Action

For the Rust rewrite, the clean current-head EC2/Vitis checkpoint is now the
39-program current-head refresh, captured in
`docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/`. Use it
as the vendor-stability anchor for the current EE109 MVP roster, while tracking
the two over-DSP Tile-K schedules separately from HLS acceptance.

The latest validation-roster steps promoted the exact full-K Tile-K `par4x16`
schedule canary and the non-Part6 `par4x8` row/column/K-tail canary into the
official roster with EC2/Vitis evidence. The latest local compiler steps
completed bounded no-HLS-drift structural-recovery and
proof/equality slices: Tile-K pre-fold/tail-bound role recovery for the covered
profiles, non-outer-K `Dense2dTileMemFold` `row_limit`/`col_limit` role
recovery for the local `MatrixTileMemFoldTail5x7x5` canary, and the
non-roster `MatrixTileMemFoldOuterKInPlaceFixPt24x20x12Tile8x5x4` Tile-K
parameter perturbation proof gate. The newest local semantic canary is
`MatrixTileMemFoldTailFixPt5x7x5`, which proves exact FixPt non-outer-K tail
MemFold locally through parser, classifier proof, checked IR, HLS/manifest, and
host compile/run. It also has one-kernel EC2/Vitis evidence in
`docs/vitis-validation/2026-07-05-fixpt-tail-oneoff/`, and the Rust validator
now revalidates that proof as selected diagnostic evidence with
`resource_fit=1/1`, `over_budget=0`, and `ii_caveated=0`. It remains outside
the 39-program validation roster. The next implementation action is either an
explicit roster promotion with a full current-head refresh, or a bounded
compiler-interface cleanup such as resolved-name reduction/fold facts. Do not
spend the next step optimizing `par4x16` DSP use unless the research goal
shifts toward board-fit implementation; the validator now keeps that caveat
visible while the compiler surface continues to deepen.

Current local diagnostic update: the Rust branch now also has
`MatrixTileMemFoldOuterKRowColTailInPlacePar2x8FixPt33x35x34`, a selected-plan
only lower-par Tile-K canary for the same 33x35x34 row/column/K-tail profile.
It preserves `partial_row_par=2` and `partial_col_par=8`, emits factor-2 row
partitions plus factor-2/factor-8 unroll pragmas, and is reachable through
`run-vitis-validation --kernel`. It is not part of the 39-program validation
roster, but selected EC2/Vitis evidence in
`docs/vitis-validation/2026-07-05-selected-par2x8-row-col-tail-f920a754/`
validates it as `resource_fit=1/1`, `over_budget=0`, and `ii_caveated=0`.
Use it as the lower-par resource diagnostic before changing the existing
`par4x16` or `par4x8` schedules.
Byte-stable refactors should keep using local equality, dry-run/plan, full
test, clippy, and evidence-validator gates; any generated-HLS text change or
validation-roster change should trigger a fresh EC2/Vitis execution.

The main remaining EE109 gaps are generic Spatial `MemFold`/`Fold`, arbitrary
K-tail shapes beyond the two named K-tail canaries, broader fixed-point/tail
semantics, generic `par` and banking inference beyond the fixed Part6 schedule,
and generic Lab3 local-window/stencil lowering beyond the known local
source-proof wrapper.

## 2026-06-30 Rust Rewrite Bulk Tile IO Bridge

The Rust rewrite now has a parser-only source-spelling bridge for canonical
rank-2 GEMM tile IO:

- `load lhs_tile <- lhs[row_base..row_base + row_limit, 0..K];`
- `load rhs_tile <- rhs[0..K, col_base..col_base + col_limit];`
- `load c_tile <- cin[row_base..row_base + row_limit, col_base..col_base + col_limit];`
- `store out[row_base..row_base + row_limit, col_base..col_base + col_limit] <- c_tile;`

Status:
- Local parser equivalence tests prove the bulk spelling normalizes to the
  existing expanded `Dense2dTileMemFold` exact FixPt and Int-tail payloads.
- Local HLS/manifest equality tests prove generated C++ and manifest JSON are
  unchanged for those canaries.
- The exact `MatrixTileMemFoldFixPt4x6x5` validation example now exercises the
  bulk IO spelling plus body-local `partial_tile` spelling without changing
  validation-program membership.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No generic DMA, raw Scala `::` ranges outside the later narrow infix tile-IO
  bridge, `SRAM[T](...)`, `val`, `par`, banking, K tiling, FixPt tail, board,
  or timing-closure claim was made at this bulk IO checkpoint; the later
  shell-alias bridge below narrows exact `SRAM[T]` and `val` support without
  changing the HLS evidence boundary.

## 2026-06-30 Rust Rewrite Lab2 Shell-Alias Buffer Bridge

The Rust rewrite now has a parser-only source-spelling bridge for the exact
FixPt `Dense2dTileMemFold` canary using selected Lab2-like shell names:

- input aliases `a`, `b`, and `c`
- local tile aliases `tileA_sram`, `tileB_sram`, and `tileC_sram`
- `.buffer` only on `tileC_sram`
- body-local `val partial_c = SRAM[T](TILE_R, TILE_C)`
- Scala-call `Foreach(end by 1) { idx => ... }`
- paren indexing/assignment such as
  `partial_c(ii, jj) = tileA_sram(ii, k_idx) * tileB_sram(k_idx, jj)`

Status:
- The parser canonicalizes those aliases to `lhs`, `rhs`, `cin`,
  `lhs_tile`, `rhs_tile`, `c_tile`, `partial_tile`, `r`, `c`, and `kk` before
  HIR/classification.
- Local parser equivalence proves the shell spelling normalizes to the
  existing expanded exact FixPt `Dense2dTileMemFold` payload.
- Local HLS/manifest equality proves generated C++ and manifest JSON are
  unchanged for `MatrixTileMemFoldFixPt4x6x5`.
- The validation-program list remains at 24 programs, and
  `Lab2Part5GEMM`/`Lab2Part6GEMM` remain absent.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No raw Scala `@spatial` source, generic/raw Scala `::` ranges outside the
  later narrow infix tile-IO bridge, in-place `c`, `ArgIn`/`setMem`, outer K
  tiling, `numel_k` MemFold bounds, Part6 `par`, banking, generic Spatial
  `MemFold`, generic DMA, broader fixed-point widths, FixPt tail tiles, board
  execution, or timing-closure claim is made.

## 2026-06-30 Rust Rewrite Infix Tile IO Bridge

The Rust rewrite now has a parser-only source-spelling bridge for exact infix
rank-2 tile IO around the existing `Dense2dTileMemFold` canaries:

- `tileA_sram load a(row_base :: row_base + row_limit, 0 :: K)`
- `tileB_sram load b(0 :: K, col_base :: col_base + col_limit)`
- `tileC_sram load c(row_base :: row_base + row_limit, col_base :: col_base + col_limit)`
- `out(row_base :: row_base + row_limit, col_base :: col_base + col_limit) store tileC_sram`

Status:
- `::` is accepted only inside this infix tile IO parser bridge.
- The parser canonicalizes Lab2 shell aliases to the existing internal roles
  and desugars the IO ranges to the same nested copy loops used by prefix bulk
  IO before HIR/classification.
- Local parser equivalence proves the infix spelling normalizes to the
  existing exact FixPt and Int-tail `Dense2dTileMemFold` payloads.
- Local HLS/manifest equality proves generated C++ and manifest JSON are
  unchanged for `MatrixTileMemFoldFixPt4x6x5`.
- The validation-program list remains at 24 programs, and
  `Lab2Part5GEMM`/`Lab2Part6GEMM` remain absent.

Evidence boundary:
- No new Vitis run is claimed for this bridge.
- No raw Scala `@spatial` source, generic `::` ranges, in-place
  `c(...) store`, `ArgIn`/`setMem`, outer K tiling, `numel_k` MemFold bounds,
  Part6 `par`, banking, generic Spatial `MemFold`, generic DMA, broader
  fixed-point widths, FixPt tail tiles, board execution, or timing-closure
  claim is made.

## 2026-06-30 Rust Rewrite Infix Tile IO EC2 Vitis Validation

The parser-only infix tile IO checkpoint above now has fresh EC2 Vitis 2025.1
execution evidence at Rust commit `1756d4d`.

Command:
- `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/infix-tile-io-20260630-1756d4d/spatial-rs/target/vitis-validation-infix-tile-io-20260630`

Result:
- All 24 validation programs completed with return code 0, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldFixPt4x6x5` passed C simulation with
  `PASS MatrixTileMemFoldFixPt4x6x5` and completed HLS synthesis.
- The FixPt canary reported estimated Fmax 121.61 MHz, estimated clock
  8.223 ns, latency 84 cycles, interval 60 cycles, and utilization estimate
  6 BRAM_18K, 8 DSP, 6457 FF, and 5919 LUT.
- Compact evidence is captured in
  `docs/vitis-validation/2026-06-30-infix-tile-io/`.

Scope:
- This evidence validates the current checked HLS payload after the source
  fixture moved to the narrow infix tile IO bridge.
- It does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim in-place `c`, outer K
  tiling, `numel_k`, Part6 `par`, banking, generic Spatial `MemFold`, generic
  DMA, board execution, Vivado implementation, or timing closure.

## 2026-06-30 Rust Rewrite In-Place C MemFold Canary

The Rust rewrite now has a separate narrow in-place `c` canary for the
fixed-shape FixPt `Dense2dTileMemFold` path:

- `inputs { a: Dram<FixPt[TRUE,_24,_8]>[ROWS,K], b: Dram<FixPt[TRUE,_24,_8]>[K,COLS] }`
- `inouts { c: Dram<FixPt[TRUE,_24,_8]>[ROWS,COLS] }`
- `tileC_sram load c(row_base :: row_base + TILE_R, col_base :: col_base + TILE_C)`
- `c(row_base :: row_base + TILE_R, col_base :: col_base + TILE_C) store tileC_sram`

Status:
- The parser, HIR, checked IR, manifest, HLS plan, C++ emitter, and host
  harness now model a single mutable `c` DRAM port for this canary.
- The manifest direction is `host_kernel_inout`, and generated HLS has a single
  mutable pointer parameter `spatial_fixpt_true_24_8_t *c`.
- The host harness seeds `actual` from the input `c` values before invoking the
  kernel and checks the mutated `c` buffer against the GEMM oracle.
- The local validation-program list is now 25 programs, with
  `MatrixTileMemFoldInPlaceFixPt4x6x5` added after the existing split
  `MatrixTileMemFoldFixPt4x6x5` canary.

Evidence:
- Local HLS/codegen/harness:
  `lab2_inplace_c_memfold_emits_single_mutable_c_pointer_and_harness`.
- Local fixture and plan-only lane:
  `cargo test -p ee109-examples --locked`.
- Local MemFold HLS regression:
  `cargo test -p spatial-rs-hls --locked --test m1_codegen memfold`.

Evidence boundary:
- At the initial local checkpoint this had host-C++ and Vitis plan-only
  evidence only. The follow-up EC2/Vitis checkpoint below covers the
  25-program lane including `MatrixTileMemFoldInPlaceFixPt4x6x5`.
- `Lab2Part5GEMM` and `Lab2Part6GEMM` remain rejected. This canary does not
  claim original Scala source compatibility, `ArgIn`/`setMem`, source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`, banking,
  generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.

## 2026-06-30 Rust Rewrite In-Place C MemFold EC2 Vitis Validation

The explicit-inout C MemFold canary now has EC2 Vitis 2025.1 execution
evidence at Rust commit `79d1b67`.

Command:
- `/home/ubuntu/.cargo/bin/cargo run --manifest-path /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/Cargo.toml -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out /home/ubuntu/spatial-rs-runs/inplace-c-memfold-20260630-79d1b67/spatial-rs/target/vitis-validation-inplace-c-memfold-20260630`

Result:
- All 25 validation programs completed with return code 0, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldInPlaceFixPt4x6x5` passed C simulation with
  `PASS MatrixTileMemFoldInPlaceFixPt4x6x5` and completed HLS synthesis.
- The in-place FixPt canary reported estimated Fmax 123.77 MHz, estimated
  clock 8.080 ns, latency 111 cycles, interval 96 cycles, and utilization
  estimate 6 BRAM_18K, 8 DSP, 5496 FF, and 5072 LUT.
- Compact evidence is captured in
  `docs/vitis-validation/2026-06-30-inplace-c-memfold/`.

Scope:
- This evidence validates the exact Rust-subset explicit-inout C path with
  `inputs { a, b } inouts { c }`, one mutable HLS pointer `c`, preload from
  `c`, and store back to `c`.
- It does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`,
  banking, generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.

## 2026-06-30 Rust Rewrite Static Outer-K In-Place C MemFold Canary

The Rust rewrite now has one static exact outer-K in-place C canary for the
Lab2 Part5 GEMM direction:

- `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`
- `ProgramKind::Dense2dTileKMemFold`
- `K_TILES = 2`, `TILE_K = 16`, `K = 32`
- local A/B SRAMs are `[TILE_R,TILE_K]` and `[TILE_K,TILE_C]`
- global K DRAM indexing is `kk_tile*TILE_K + k_idx`
- `c` is one explicit `DramInOut`/mutable HLS pointer

Status:
- The local validation-program list is now 26 programs.
- Parser/classifier support is separate from the old full-K
  `Dense2dTileMemFold v0` payload.
- HLS codegen emits a real outer `kk_tile` loop and `TILE_K`-sized local
  A/B arrays.
- The host-C++ harness seeds `actual` from `c`, mutates `c` in place, and
  checks against the existing `C + A*B` oracle.
- Vitis dry-run/plan-only sidecars include the new canary.
- EC2 Vitis 2025.1 `csim_design` and `csynth_design` now pass for all 26
  validation programs, including this canary.

Evidence:
- `cargo test -p spatial-rs-core --locked outer_k -- --nocapture`
- `cargo test -p spatial-rs-hls --locked lab2_outer_k_inplace_c_memfold_emits_static_k_tile_loops_and_harness -- --nocapture`
- `cargo test -p ee109-examples --locked validation_programs_include_supported_features_after_adapter_baseline -- --nocapture`
- `cargo test -p ee109-examples --locked emit_vitis_dry_run_binary_generates_m1_frontend_bundles -- --nocapture`
- `cargo test -p ee109-examples --locked run_vitis_validation_plan_only_writes_sidecar_tcl_for_all_examples -- --nocapture`
- EC2 command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-outer-k-run`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-outer-k-memfold/`
- New canary Vitis result:
  `returncode=0`, `csim=true`, `csynth=true`, estimated Fmax 136.99 MHz.

Evidence boundary:
- EC2/Vitis `csim_design` and `csynth_design` are claimed for the exact
  26-program validation lane only.
- The EC2/Vitis run itself is not raw Scala `Lab2Part5GEMM` or
  `Lab2Part6GEMM` source compatibility. Exact fixed Part5 raw-wrapper support
  is tracked below as a local parser/HLS-equality bridge over the same canary.
- Dynamic `ArgIn` dimensions, arbitrary K-tail shapes beyond the named serial
  canary, generic/source-compatible Spatial `MemFold`, Part6 `par`, banking,
  board execution, Vivado implementation, and timing closure remain
  unsupported.

## 2026-07-01 Rust Rewrite Lab2-Like Outer-K Parser Bridge

The Rust rewrite now accepts a Lab2-like shell/infix spelling for the same
static exact outer-K canary:

- `inputs { a, b } inouts { c }`
- `tileA_sram`, `tileB_sram`, and `tileC_sram.buffer`
- outer tile loops spelled as `kk`, `mm`, and `nn`
- a hoisted A-tile load before the column tile loop
- infix rank-2 tile loads/stores using `::` ranges
- exact static offset loops such as `Foreach(K by TILE_K)`, canonicalized back
  to the existing tile-count loop payload
- `MemFold(tileC_sram)(0 until TILE_K by 1) { k_idx => ... }{_+_}`
- a declared static `numel_k` alias equal to `TILE_K` inside K tile ranges and
  the MemFold bound
- tile-size-first or remaining-first static `val numel_k = min(...);` spelling
  under the same offset-loop proof
- row/column/K-tail forms where `row_limit` and the A-tile load are hoisted to
  tile-row scope before the column tile loop, while `col_limit`, B/C loads,
  fold, and C store remain column-local
- exact fixed raw dimension/tile aliases (`M/N=32`,
  `tileM/tileN/tileK=16`) in declarations, DRAM/SRAM dimensions, offset loops,
  and `min(tileK.to[Int], K - kk)`, canonicalized back to `ROWS/COLS` and
  `TILE_R/TILE_C/TILE_K` before HIR
- historical note: an earlier exact fixed raw `@spatial class Lab2Part5GEMM`
  wrapper bridge was accepted only under token-stream exact checks, but raw
  Lab2 Part5/Part6 wrapper ingress is now retired; the Rust-subset Tile-K
  source forms above remain the active regression anchors.
- the exact explicit-zero raw fold range
  `MemFold(tileC_sram)(0 until numel_k by 1)` for fixed Part5/Part6 wrappers,
  was likewise historical under the retired raw-wrapper bridge. Nonzero starts
  remain rejected by the active Rust-subset parser surface.

Status:
- This is parser/source-spelling coverage only. It canonicalizes to the
  existing `Dense2dTileKMemFold` checked payload for
  `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32`.
- The generated HLS and manifest match the expanded static outer-K canary
  exactly.
- The accepted raw Part5/Part6 wrappers now reuse this bounded frontend/HIR path
  after their fixed token-stream quarantine succeeds.
- This bridge slice did not add a validation-program member.
- No new EC2/Vitis evidence is claimed for this bridge because it does not
  change emitted HLS or validation membership.

Evidence boundary:
- Local proof is parser/classifier equivalence plus HLS/manifest equality:
  `cargo test -p spatial-rs-core --locked lab2_outer_k -- --nocapture`,
  `cargo test -p spatial-rs-core --locked raw_lab2_part5 -- --nocapture`, and
  `cargo test -p spatial-rs-hls --locked lab2_outer_k -- --nocapture`, plus
  `cargo test -p spatial-rs-hls --locked --test m1_codegen lab2_raw_part5 -- --nocapture`.
- Non-exact raw Scala `Lab2Part5GEMM` and non-exact `Lab2Part6GEMM` forms
  still fail closed. The bridge also keeps full-K MemFold bounds, undeclared or
  mismatched `numel_k`, malformed or dynamic `numel_k = min(...)` variants,
  non-exact offset-loop steps, token-split identifiers/operators, arbitrary
  K-tail shapes beyond the named serial canary, hoisted B/C/fold/store phases,
  Part6 `par`, banking, generic Spatial `MemFold`, board execution, Vivado
  implementation, and timing closure unsupported.

## 2026-07-01 Rust Rewrite `a16401b9` EC2 Vitis Refresh

After the tokenized raw Part5 wrapper bridge and shared frontend nested block
comment support, the Rust rewrite re-ran the exact 26-program Vitis lane at
source commit `a16401b9c1699d8f92d7ec0a93b04ae608d90617` on
`David/HLS-spatial`.

Evidence:
- Remote host: `[ec2-host — see private/ec2-lane.md]`
  (`ip-172-31-37-7`)
- Remote run directory:
  `/home/ubuntu/spatial-rs-runs/block-comments-a16401b/spatial-rs`
- Command:
  `cargo run -p ee109-examples --locked --bin run-vitis-validation -- --execute --mode both --settings /tools/Xilinx/2025.1/Vitis/settings64.sh --out target/vitis-validation-block-comments-a16401b`
- Durable evidence:
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-block-comments-refresh/`
- Result: all 26 programs reported `returncode=0`, `csim=true`, and
  `csynth=true`.
- `MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` result: estimated Fmax
  136.99 MHz, estimated clock 7.300 ns, latency 41053 cycles, interval 41054
  cycles, and utilization estimate 41 BRAM_18K, 64 DSP, 8120 FF, and 5896 LUT.

Evidence boundary:
- This refresh proves Vitis C simulation and HLS synthesis for the exact
  `a16401b9` 26-program validation set only.
- It also confirms that frontend block-comment support did not perturb the
  generated validation kernels.
- It does not claim board execution, Vivado implementation/place-and-route,
  post-implementation timing closure, broad Scala source compatibility,
  structured Scala wrapper parsing, `Lab2Part6GEMM`, Part6 `par`,
  dynamic/tail K tiling, generic Spatial `MemFold`, banking, generic DMA,
  generic in-place alias analysis, FixPt tail tiles, or broader Spatial
  language coverage.

## 2026-07-01 Rust Rewrite Lab1 Part6 SRAM-Tile Fold Vitis Checkpoint

The Rust rewrite added `ScalarSramTileFold v0` and the non-lab
`SramTileFoldSum32` validation canary after the refreshed 26-program Vitis
checkpoint.

Status:
- The validation list now contains 27 programs and all 27 passed EC2/Vitis
  `csim_design` and `csynth_design`.
- `SramTileFoldSum32` covers one rank-1 `Dram<Int>[32]` input, one scalar
  output, one local `Sram<Int>[16]` tile, an explicit DRAM-to-SRAM tile load,
  an inner tile sum, and scalar accumulator writeback.
- The exact raw `Lab1Part6ReduceExample` token stream canonicalizes to
  `SramTileFoldSum32` with generated HLS/manifest equality.
- Local host-C++ harness, Vitis dry-run/plan coverage, and durable EC2/Vitis
  evidence are in place.

Evidence boundary:
- Durable evidence is captured in
  `/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-01-lab1-part6-sram-hir-refactor/`
  at source commit `f0f3cb4ee03461fefacfeebc21dd8e4db38b8c51`.
- Generic Spatial `Fold`, arbitrary nested folds, arbitrary local-memory
  effects, tail tiles, dynamic bounds, non-`Int`, scheduling, banking, board
  execution, Vivado implementation, timing closure, and broad Scala source
  compatibility remain unsupported.

## 2026-06-30 Rust Rewrite Lab2 `numel_m`/`numel_n` Parser Bridge

The Rust rewrite now accepts one more Lab2 source-spelling detail in the
existing parser-only MemFold shell/infix bridge:

- `numel_m` may stand for the row tile extent.
- `numel_n` may stand for the column tile extent.
- Exact tile spellings normalize those names to the existing `TILE_R` and
  `TILE_C` extents.
- Tail spellings normalize those names to the existing `row_limit` and
  `col_limit` checked-payload names.

Status:
- This is a frontend canonicalization only. The checked IR payload remains the
  existing `Dense2dTileMemFold` payload.
- The validation-program list remains the same 25 programs.
- No generated HLS, manifest, harness, or Vitis evidence changed for this
  parser bridge.
- A new fail-closed parser guard keeps `numel_k` K tiling unsupported for the
  full-K `Dense2dTileMemFold` path; later outer-K work admits only named static
  and serial K-tail forms.

Evidence boundary:
- Local proof is parser regression only:
  `cargo test -p spatial-rs-core --locked lab2_infix_tile_io -- --nocapture`.
- This does not promote `Lab2Part5GEMM` or `Lab2Part6GEMM`, does not prove
  original Scala source compatibility, and does not claim source-level
  Part5/Part6 shell extraction, outer K tiling, `numel_k`, Part6 `par`,
  banking, generic Spatial `MemFold`, generic DMA, board execution, Vivado
  implementation, or timing closure.
