---
type: design
project: spatial-spec
date: 2026-06-27
status: active
related:
  - "[[2026-06-26-rust-first-spatial-dsl-overlay]]"
  - "[[2026-06-26-rust-ee109-mvp-design]]"
  - "[[2026-06-27-rust-lab3-convolution-slice-contract]]"
  - "[[84 - EE109 HLS Stability Matrix]]"
  - "[[60 - EE109 HLS Lowering Map]]"
---

# Rust Spatial Rewrite Roadmap

## Framing

The long-term goal is a Rust rewrite of Spatial with HLS C++ as the primary backend. EE109 labs are the first acceptance ladder because they are concrete teaching examples, but they are not the final compiler boundary.

The current `spatial-rs` work should therefore be treated as a tracer slice:

- keep the working host-C++ fixture adapters as regression evidence
- avoid growing the compiler by adding endless exact lab recognizers
- promote lab adapters into reusable frontend, HIR, IR, lowering, and HLS modules
- preserve fail-closed diagnostics until a construct has a selected semantic and HLS story

## Current Position

`spatial-rs` currently has a 39-program EE109 MVP validation roster covering
the lab fixtures plus narrow reusable representatives for scalar expressions,
reductions/folds, SRAM tile fold, LUT lookup, rank-1/2 dense kernels, MemReduce
/ MemFold fill, FIFO tile scaling, ControlFsm, Stencil2d/Sobel, and named
Tile-K GEMM/tail/schedule canaries, including the exact full-K `par4x16`
schedule perturbation and the non-Part6 `par4x8` row/column/K-tail schedule
canary.

Current Vitis status: the latest Rust rewrite vendor checkpoint is the
2026-07-05 39-program current-head refresh at source Rust commit `76158dd7`,
imported in Rust repo commit `9c966dd6`, after locking the explicit
`FixPt[TRUE,_24,_8]` signed truncation/wrap HLS policy, promoting the
`MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` Tile-K schedule canary,
promoting the
`MatrixTileMemFoldOuterKRowColTailInPlacePar4x8FixPt33x35x34` Tile-K
row/column/K-tail schedule canary, and refreshing the scheduled canonical
Tile-K bulk IO cleanup, extracting the Tile-K matcher/proof module, and adding
the Part6 canonical bulk `ROW_PAR`/`COL_PAR` source bridge, captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`.
It keeps `MemReduceFives8` and `MemFoldSevens12` in the validation roster
after the raw Lab2 Part5/Part6 GEMM Scala-ingress retirement, refreshes vendor
evidence for the updated fixed-point alias, adds the exact scheduled Tile-K
representatives, and proves the current 39-program roster after the Part6 alias
bridge. All 39 programs passed EC2/Vitis 2025.1 `csim_design` and
`csynth_design`. The imported evidence was trimmed to stable summaries,
sidecars, logs, and reports, then validates as
`resource_fit=37/39`, `over_budget=2`, and `ii_caveated=14`, so this proves
vendor HLS acceptance for the exact roster only, not board execution,
implementation, resource fit for the two over-DSP Tile-K schedules, timing
closure, performance optimality, generic Spatial compatibility, or broad Scala
source compatibility.
Follow-up Rust commit `88c7df1a` (`Report Vitis resource quality caveats`)
does not rerun Vitis, but makes that boundary machine-readable: the local
evidence validator now parses stable csynth reports and Vitis logs and reports
that 38-program bundle as `resource_fit=37/38`, `over_budget=1`, and
`ii_caveated=14`; the active 39-program bundle now reports
`resource_fit=37/39`, `over_budget=2`, and `ii_caveated=14`.
The exact full-K Tile-K schedule canary
`MatrixTileMemFoldOuterKInPlacePar4x16FixPt32x32x32` preserves
`partial_row_par=4` and `partial_col_par=16` through checked IR and lowers them
into row-cyclic partitions plus row/column unroll pragmas when factors divide
the static tile dimensions. Non-dividing schedule factors remain fail-closed;
the representative is now validation-roster and EC2/Vitis proven.
The current lower-par resource diagnostic is
`MatrixTileMemFoldOuterKRowColTailInPlacePar2x8FixPt33x35x34`. It remains
outside the 39-program validation roster, but selected EC2/Vitis evidence in
`docs/vitis-validation/2026-07-05-selected-par2x8-row-col-tail-f920a754/`
validates the requested `partial_row_par=2` / `partial_col_par=8` schedule as
`resource_fit=1/1`, `over_budget=0`, and `ii_caveated=0`.
The current local semantic-support slice makes `Stencil2d v0` local-memory role
discovery declaration-order-independent. The accepted Sobel shape still
requires exactly one matching LineBuffer, horizontal LUT, vertical LUT, RegFile
window, and row scratch SRAM; duplicate role candidates and extra local memories
fail closed. Reordered valid sources rebuild the same checked `Stmt::Stencil2d`
payload and preserve exact HLS/manifest output, so this does not change
validation-roster membership or vendor-HLS evidence.
The current `Stencil2d v1` source-spelling slice is Rust commit `8916d3f1`
(`Accept Stencil2d kernel-bound border spelling`). It admits the same top-left
zero border as matched kernel-bound-minus-one expressions such as
`rr < KROWS - 1 || cc < KCOLS - 1`, including commuted OR form, while rejecting
crossed row/column provenance. The accepted sources rebuild the same checked
`Stmt::Stencil2d` payload and exact HLS/manifest output as the alias-constant
representative, so validation-roster membership and vendor-HLS evidence remain
unchanged.
The recent local frontend/HIR cleanup at Rust commit `35c6944a` (`Move Tile-K
proof tests into module`). Tile-K proof/profile tests and Tile-K-local
LHS/RHS/C preload/store matcher tests now live under
`classifier/tiled2d/tile_k.rs`, and the Tile-K proof/matcher structs, fields,
and helpers are private to that module. The parent `tiled2d.rs` keeps only the
production classifier re-export plus shared rank-2/MemFold
partial-product/C-accumulation tests because non-outer-K
`Dense2dTileMemFold` still uses those helpers. This does not change accepted
syntax, checked IR, generated HLS, or validation-roster membership; the later
`76158dd7` current-head vendor checkpoint above proves the unchanged roster
after this cleanup and the following Part6 alias bridge.
The previous local frontend/HIR cleanup is Rust commit `32b3ac4b` (`Extract
Tile-K matcher module`). Tile-K local stride/index helpers, LHS/RHS/C
preload/store specs, phase-spine matching, the Tile-K MemFold wrapper, and
partial-schedule matching now live in `classifier/tiled2d/tile_k.rs` beside the
Tile-K proof facade.
The earlier local frontend/HIR cleanup is Rust commit `aafc0980` (`Extract
Tile-K proof module`). Tile-K entry/precheck/proof orchestration, proof
structs, payload-to-proof rebuild helpers, and the Tile-K-local bound helper
now live in `classifier/tiled2d/tile_k.rs`.
The older local frontend/HIR cleanup is Rust commit `26611e17` (`Guard Lab2
shell alias activation`). Lab2 shell-alias canonicalization now activates only
for actual local SRAM alias declarations, not for exact alias-name tokens used
as ordinary ports or assignment targets. Ordinary rank-2 copy sources with a
name like `tileA_sram` remain ordinary copies, while the accepted Lab2
shell-alias buffer and infix tile-I/O bridges preserve their checked payloads,
generated HLS, and manifests.
The earlier local frontend/HIR cleanup is Rust commit `be8511c9` (`Enforce
Tile-K schedule label factors`). Explicit Tile-K `ParRxC` labels now have to
match the proven `partial_row_par` / `partial_col_par` schedule facts at both
classifier and checked-IR gates, and the resource-fit policy is tied to the
recorded 39-program plus selected Par4x16/Par4x8/Par2x8 Vitis evidence.
The earlier local frontend/HIR cleanup is Rust commit `51de4c05` (`Record
Tile-K resource-fit policy`). `tile_k_resource_fit_policy()` records
`par4x16` and `par4x8` as requested validation-roster schedules with
over-budget evidence and `par2x8` as a separate selected diagnostic
resource-fit candidate.
The earlier local frontend/HIR cleanup is Rust commit `c797cbd9` (`Resolve
Dense2d FixPt tail proof facts`). The exact
`MatrixTileMemFoldTailFixPt5x7x5` canary now requires exact `ROWS`/`COLS`
total-symbol provenance, rejects the FixPt canary name with non-FixPt payloads,
and keeps dropped non-outer-K partial `par` schedules fail-closed until those
schedule facts are represented in checked IR. This does not change generated
HLS, manifests, validation-roster membership, or vendor-HLS evidence.
The earlier local frontend/HIR cleanup is Rust commit `69b350ef` (`Resolve
MemReduce fill proof facts`). `MemReduceFill v0` / `MemFoldFill v0` records
resolver-backed accumulator/temp/output symbols, length/step const-role
symbols, resolved step count, fill length, final output-store length/count,
temp-write loop/lane/count facts, and MemFold zero-init loop/lane/write/length
facts before checked IR emission without changing generated HLS, manifests,
validation-roster membership, or vendor-HLS evidence.
The older local frontend/HIR cleanup is Rust commit `f9fd4ae1` (`Resolve
FIFO proof facts`). `Fifo1dTileScalarMul v0` records resolver-backed
input/scalar/output ports, local FIFO symbols, outer/lane loop domains, static
length/depth facts, load/store tile ranges, dequeue/enqueue effect counts,
parent blocks, lexical order, and effect loop ids before checked IR emission
without changing generated HLS, manifests, validation-roster membership, or
vendor-HLS evidence.
The earlier local frontend/HIR cleanup is Rust commit `ce517499` (`Resolve
Stencil2d proof facts`). `Stencil2d v0` and the exact Lab3 Sobel adapter record
resolver-backed local-window symbols, row/column/shift loop domains, row-range
load/store facts, reset/shift effects, line-buffer and line-output accesses,
and exact horizontal/vertical reducer-symbol identities before checked IR
emission without changing generated HLS, manifests, validation-roster
membership, or vendor-HLS evidence.
The older local frontend/HIR cleanup is Rust commit `c344521b` (`Resolve
ControlFsm proof facts`). `ControlFsm v0` and the exact Lab2 FSM adapters
record resolver-backed output/scratch/reg/state symbols, the FSM loop domain,
scratch write effects, reg-value read facts, and final output store-range facts
before checked IR emission.
The older local frontend/HIR cleanup is Rust commit `879e8c21` (`Resolve
ScalarExpr proof facts`). `ScalarExpr v0` records resolver-backed scalar
input/output roles, symbols, `Int` types, port ordinals, expression read
symbols, integer expression counts, and zero memory access/effect facts before
checked IR emission.
The earlier local frontend/HIR cleanup is Rust commit `5b6d9d3c` (`Resolve LUT
proof facts`). `LutLookup v0` and the Lab2 LUT adapters record resolver-backed
table/input/row/column/output symbols plus rank-2 table read index facts before
checked IR emission.
The earlier Dense1d frontend/HIR cleanup is Rust commit `98d0d3fe` (`Resolve
Dense1d proof facts`). `Dense1dScalarMul v0` records resolver-backed outer/lane
loop domains, input/scalar/output symbols, input/output tile symbols, rank-1
remote load/store range facts, and local lane read/write facts before checked
IR emission.
The latest Lab2/Tile-K frontend cleanup is Rust commit `224d7a76` (`Accept
hoisted Tile-K tail lhs load`). It accepts `row_limit` and `tileA_sram load` at
tile-row scope before the column tile loop while keeping `col_limit`, B/C
loads, fold, and C store column-local, and normalizes both serial and Part6
scheduled forms to the existing row/column/K-tail checked payload and HLS.
The previous scalar frontend/HIR cleanup is Rust commit `9797d162` (`Accept scalar
reduction alias bounds`). `ScalarReduce v0` and `ScalarFold v0` now resolve the
constant identifiers used in their reduce/fold syntax, accepting equivalent
Rust-subset names such as `LEN`/`LANES` and `LEN`/`BLOCK`/`LANES` while keeping
the same narrow checked payloads, canonical validation representatives, and
historical Vitis evidence.
The previous local frontend/HIR foundation cleanup is Rust commit `2a7fe3bb`
(`Retire duplicate raw GEMM tile proof`). It removes the private raw-adapter
Tile-K tile-I/O role proof object from `source_adapter.rs`; the quarantined
raw Lab2 Part5/Part6 adapter now records only the matched scaffold, normalized
`Accel` body, generated frontend source, and expected Tile-K profile. The
frontend/HIR Tile-K classifier remains the semantic authority for rank-2
tile-copy/access-role proof. Accepted raw syntax, generated frontend source,
checked IR, generated HLS, manifests, validation membership, and imported
Vitis evidence are unchanged, so no fresh EC2/Vitis run was claimed.
The latest local semantic canary is Rust commit `2ed2ddec`
(`Add exact FixPt MemFold tail canary`). It adds
`MatrixTileMemFoldTailFixPt5x7x5` as the exact `FixPt[TRUE,_24,_8]`
counterpart to the local non-outer-K `MatrixTileMemFoldTail5x7x5` Int
tail/min-bound canary. The frontend, classifier proof, checked IR, HLS
codegen, manifest, and host harness now accept the exact 5x7x5 / 2x3 split-C
tail shape and emit `ap_fixed<32, 24, AP_TRN, AP_WRAP>` with runtime
`row_limit`/`col_limit` loops. Wrong FixPt tail names/shapes remain
fail-closed, as do raw Scala wrappers, generic Spatial `MemFold`, `par`,
banking, K tiling, and arbitrary FixPt tails. This is a new generated-HLS local
surface and now has one-kernel EC2/Vitis `csim_design` / `csynth_design`
evidence in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-05-fixpt-tail-oneoff/`.
The Rust evidence validator now revalidates that proof as selected diagnostic
evidence with `resource_fit=1/1`, `over_budget=0`, and `ii_caveated=0`. It is
still not a validation-roster member; a roster promotion would need an explicit
roster decision and full roster refresh.
The latest local frontend source-admission cleanup is Rust commit `00797aed`
(`Accept scheduled Tile-K bulk IO`). It accepts the exact scheduled Part6
full-K `MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` canary
through canonical Rust-subset arrow bulk rank-2 tile IO when only the
partial-product loops carry literal `par 2` / `par 16`. The source lowers to
the same checked scheduled Tile-K payload as the structural Part6 canary and
preserves exact generated HLS/manifest equality. Generic `par`, symbolic
canonical `par`, non-partial-loop `par`, `numel_k`, tails, raw Scala wrappers,
and broad Spatial scheduling remain fail-closed outside the already documented
bridge paths. The follow-up
`docs/vitis-validation/2026-07-05-current-head-00797aed-39-program/` bundle
then validates the unchanged 39-program roster after this source cleanup.
The preceding local frontend source-admission cleanup is Rust commit `5b428158`
(`Accept canonical Tile-K bulk IO`). It accepts canonical Rust-subset arrow
bulk rank-2 tile IO for the exact full-K
`MatrixTileMemFoldOuterKInPlaceFixPt32x32x32` Tile-K canary:
`load lhs_tile <- lhs[...]`, `load rhs_tile <- rhs[...]`,
`load c_tile <- c[...]`, `memfold c_tile with partial_tile over k_idx in
0..TILE_K`, and `store c[...] <- c_tile`. This path lowers to the same checked
Tile-K payload as the expanded loop canary and preserves exact generated
HLS/manifest equality. Lab2 shell aliases remain on the older Lab2 bridge
paths; `numel_k`, Part6 `par`, and tail semantics remain outside this
canonical full-K source spelling. Validation membership and Vitis evidence are
unchanged.
The preceding local proof/equality cleanup is Rust commit `3a4d753f`
(`Record parameterized Tile-K proof gate`). It promotes the existing local
non-roster `MatrixTileMemFoldOuterKInPlaceFixPt24x20x12Tile8x5x4`
Tile-K canary into an explicit classifier proof/equality gate: parser raw-alias
normalization, private `TileKMemFoldProof`, HLS/manifest equality, and local
host compile/run now pin the 24x20x12 / 8x5x4 exact full-K shape. New
fail-closed coverage rejects inconsistent parameterized alias coverage and
wrong stride-symbol provenance. Generated HLS, manifests, validation
membership, and the active Vitis evidence anchor are unchanged; this is not
raw Scala compatibility, generic `MemFold`, arbitrary K-tail support,
inferred banking, or a new vendor-HLS claim.
The preceding local frontend source-admission cleanup is Rust commit
`4834a9c8` (`Recover dense MemFold tail bounds by role`). It accepts the two
canonical non-outer-K `Dense2dTileMemFold` tail-bound lets, `row_limit` and
`col_limit`, in either declaration order for the local
`MatrixTileMemFoldTail5x7x5` canary. Local tests prove identical checked
payloads, generated HLS, and manifests; generated HLS, manifests, validation
membership, and the active Vitis evidence anchor are unchanged.
The preceding local frontend source-admission cleanup is Rust commit
`ef07ea51` (`Accept reversed MemFold tail min bounds`). It accepts
tile-size-first or remaining-first `min(...)` argument order for the bounded
non-outer-K MemFold tail, Tile-K K-tail, and Tile-K row/column/K-tail profiles.
Local tests prove identical checked payloads, generated HLS, and manifests for
those source spellings; generated HLS, manifests, validation membership, and
the active Vitis evidence anchor are unchanged.
The earlier local frontend source-admission cleanup is Rust
commit `6830f993`
(`Accept normalized Tile-K numel_k aliases`). It accepts the Lab2-like Tile-K
outer-K `numel_k` min alias with the existing
`min(TILE_K.to[Int], K - kk)` spelling, reversed min arguments
`min(K - kk, TILE_K.to[Int])`, and plain `min(TILE_K, K - kk)` tile-extent
spelling while the active K-offset loop proof is in scope. These forms lower to
the same checked Tile-K HIR/HLS payloads as the existing canaries. Wrong
offsets, missing `TILE_K`, duplicate aliases, and surrounding invalid Lab2
shapes remain fail-closed; generated HLS, manifests, validation membership, and
imported Vitis evidence are unchanged, so no fresh EC2/Vitis run was claimed.
The latest local evidence-validation cleanup is Rust commit `ba388096`
(`Reject stale Vitis evidence artifacts`). It makes the repo-local evidence
validator reject unexpected stable artifacts for kernels outside the expected
roster under `sidecars/`, `logs/`, and `reports/`, so a bundle cannot silently
carry retired-kernel leftovers while claiming the exact current roster. The
then-active `a62eb274` 37-program evidence bundle still validates; generated HLS,
manifests, validation membership, and imported Vitis evidence are unchanged, so
no fresh EC2/Vitis run was claimed.
The latest local backend-structure cleanup is Rust commit `871dd7de` (`Guard
remaining HLS plan frames`). It completes the obvious HLS plan-frame guard
sweep: `ControlFsm v0` now rejects malformed output-param frames; `ScalarFold
v0` and `ScalarSramTileFold v0` reject malformed input-param frames; and the
zero-DRAM `ScalarExpr v0`, `ScalarReduce v0`, and `LutLookup v0` families reject
stale non-empty param frames before kernel or harness rendering. Accepted
syntax, generated HLS, manifests, validation membership, and imported Vitis
evidence are unchanged; no fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `fd9c4de1` (`Guard
scalar multiply plan frames`). It moves Dense1d, rank-2 tile-scalar, and FIFO
plan-to-frame validation into their feature modules, rejecting malformed
internal plans unless params are exactly `[input, output]` in order. Accepted
syntax, generated HLS, manifests, validation membership, and imported Vitis
evidence are unchanged; no fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `c1581476` (`Guard
Stencil plan frames`). It moves `Stencil2d v0` / `Lab3Part1Convolution`
plan-to-frame validation into `spatial_rs_hls::stencil2d`, rejecting malformed
internal plans unless params are exactly `[input, output]` in order. Accepted
syntax, generated HLS, manifests, validation membership, and imported Vitis
evidence are unchanged; no fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `851586fb` (`Guard
DotAccum plan frames`). It moves `Dense2dTileDotAccum v0` plan-to-frame
validation into `spatial_rs_hls::dot_accum`, rejecting malformed internal plans
unless params are exactly `[lhs, rhs, output]` in order. Accepted syntax,
generated HLS, manifests, validation membership, and imported Vitis evidence
are unchanged; no fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `1810b21e` (`Guard
mem reduction fill plan frames`). It moves `MemReduceFill v0` / `MemFoldFill
v0` plan-to-frame validation into `spatial_rs_hls::mem_reduction_fill`,
rejecting malformed internal plans unless there is exactly one output ABI param
whose name matches the `MemReductionFillPlan` output. Accepted syntax,
generated HLS, manifests, validation membership, and imported Vitis evidence
are unchanged; no fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `ff9a94a7` (`Guard
Dense2d MemFold plan frames`). It moves non-outer-K `Dense2dTileMemFold`
plan-to-frame validation into `spatial_rs_hls::memfold`, rejecting malformed
internal split-output frames unless params are exactly `[lhs, rhs, cin, out]`
and rejecting in-place mutable-C frames unless params are exactly
`[lhs, rhs, c]` with `c_input == output`. Accepted syntax, generated HLS,
manifests, validation membership, and imported Vitis evidence are unchanged; no
fresh EC2/Vitis run was claimed.
An earlier local backend-structure cleanup is Rust commit `88e33a09`
(`Guard Dram2dCopy plan frames`). It gives rank-2 copy a named
`Dram2dCopyPlan` body and moves plan-to-frame validation into
`spatial_rs_hls::rank2_copy`, rejecting malformed internal copy plans with
swapped or extra ABI params before kernel or harness rendering. Accepted syntax,
generated valid HLS, manifests, validation membership, and imported Vitis
evidence were unchanged; the then-active `7a350983` vendor-HLS anchor is now
superseded by the `a62eb274` 37-program refresh.
The latest Tile-K backend-structure cleanup is Rust commit `2841cc56` (`Guard
Tile-K plan frames`). It moves Tile-K body/ABI-param adaptation into
`spatial_rs_hls::tile_k`, rejecting malformed internal Tile-K plans with
swapped, missing, or extra ABI params unless they are exactly
`[lhs, rhs, c_inout]` in order before kernel or harness rendering. Accepted
syntax, generated valid HLS, manifests, validation membership, and imported
Vitis evidence were unchanged; the then-active `7a350983` vendor-HLS anchor is
now superseded by the `a62eb274` 37-program refresh.
The latest local frontend/HIR proof cleanup is Rust commit `52953ae0`
(`Name Tile-K fold update proof`). It replaces the Tile-K fold schedule-only
helper with `TileKFoldUpdateProof`, recording row/column/K update domains,
effective bounds, local LHS/RHS/C/partial tile roles, and serial/scheduled
partial-product par factors after the existing partial-product and
C-accumulation resolved-fact checks pass. Accepted syntax, checked payloads,
generated HLS, manifests, validation membership, and imported Vitis evidence
were unchanged; the then-active `7a350983` vendor-HLS anchor is now superseded
by the `a62eb274` 37-program refresh.
The follow-up `ef07ea51` source-admission slice adds fold/update-level
fail-closed tests for resolved partial-product lane drift and C-accumulation
lane drift without changing production proof behavior.
The quarantined raw Lab2 GEMM source adapter has also been tightened locally:
Rust commit `38c5ebfddcc984d4c1af5407824d0246cf11f3e0` was an intermediate
proof-boundary cleanup that matched the fixed raw scaffold, normalized `Accel`
body, and generated frontend source before retaining the equality guard; later
frontend/HIR Tile-K classifier work now owns the rank-2 tile-I/O role/window
and access-role facts instead of the raw adapter. Accepted raw syntax, checked
payloads, generated HLS, validation membership, and imported Vitis evidence are
unchanged. Follow-up Rust commit
`47f9baa43f455f6078a514098f25ad7815a58298` completed that bridge by moving the
Tile-K profile vocabulary into checked IR as neutral
`Dense2dTileKMemFoldProfile` values and making the raw source proof validate
its generated frontend source against the expected profile. The covered raw
profile mappings are Part5 fixed32 -> `SerialFullK`, Part6 fixed32 ->
`Part6ScheduledFullK`, Part5 K-tail34 -> `SerialKTail`, and Part6 K-tail34 ->
`Part6ScheduledKTail`. This is still no-HLS-drift compiler structure work:
accepted raw syntax, generated HLS, manifests, validation membership, and
imported Vitis evidence are unchanged.
Follow-up Rust commit `c4f8eea6` (`Accept raw Lab2 row-col K-tail GEMM`) admits
only the exact row/column/K-tail lab runtime tuple `runtimeArgs = "33 35 34"`
in that same quarantined adapter. Part5 maps to `SerialRowColKTail` and Part6
maps to `Part6ScheduledRowColKTail`, preserving generated HLS/manifest equality
with the existing serial and scheduled row/column/K-tail Vitis-proven canaries.
Near-miss dimensions and wrong Part6 par factors remain fail-closed; validation
membership and imported Vitis evidence are unchanged.
The known local Lab3 convolution teaching wrapper has also moved off exact raw
wrapper equality. Rust commit
`0f16af3e7b042554369ce69972da580078651c6a` (`Record raw Lab3 source proof`)
records a scoped source/local-window proof before canonical
`Lab3Part1Convolution` payload emission: direct class image facts before
`main`, main setup facts before the single `Accel`, and local-window facts for
`lb`/`sr`/`lineOut`, `kh`/`kv`, row/column/shift loops, two-row/two-column
border handling, and `par 16`. Host scaffolding can vary, but moved facts and
accelerator-shape drift are rejected. This is also no-HLS-drift compiler
structure work: generated HLS, manifests, validation membership, and imported
Vitis evidence are unchanged.
The next bounded raw-Lab3 compatibility slice admits only the exact
static-kernel border predicate `r < Kh - 1 || c < Kw - 1`, normalizing it to the
same `pad_r`/`pad_c` source-proof form and preserving canonical Lab3
parser/HLS/manifest equality. Swapped `Kh`/`Kw` border expressions remain
fail-closed; validation membership and imported Vitis evidence are unchanged.
Landed Rust commit `5c21c48520b96425ee4303185ce262c699e02ac5` records the
accepted `Stencil2d v0` Sobel source shape plus resolved row/column/shift
local-window facts in a private classifier proof object, and checked IR rejects
flattened stencil extents beyond the supported HLS/harness `int` range before
HLS planning. This is again no-HLS-drift compiler structure work: accepted
syntax, generated HLS, manifests, validation membership, and imported Vitis
evidence are unchanged.
The same landed checkpoint tightens the raw Lab3 ingress: the accepted `Accel`
island must now be a direct top-level statement in `main`, so identical
accelerator text hidden inside a helper is rejected fail-closed. Generated HLS,
manifests, validation membership, and imported Vitis evidence are unchanged.
It also moves the FIFO tile-scalar host-harness renderer into
`crates/spatial-rs-hls/src/fifo.rs`, beside the existing FIFO kernel frame, and
moves the Lab3 convolution and reusable `Stencil2d v0` Sobel host-harness
renderers into `crates/spatial-rs-hls/src/stencil2d.rs`, beside the existing
Sobel kernel frame. `emit.rs` remains the HLS plan dispatcher and ABI
plan-to-frame adapter; generated kernel text, manifests, validation membership,
and imported Vitis evidence are unchanged.
A fifth verified working-tree checkpoint adds a full exact emitted-kernel
snapshot for `MatrixTileMemFoldInPlaceFixPt4x6x5`, the non-outer-K in-place
fixed-point MemFold canary. This is a test-coverage guard before deeper
ABI/frame helper work; generated HLS, manifests, validation membership, and
imported Vitis evidence are unchanged.
A sixth verified working-tree checkpoint moves the rank-2 tile-scalar
`MatrixTileScale4x6` host-harness renderer into
`crates/spatial-rs-hls/src/tile_scalar_mul.rs`, beside the existing kernel
frame. `emit.rs` remains the plan dispatcher and ABI plan-to-frame adapter.
This is no-HLS-drift backend helper work; generated kernels, manifests,
validation membership, and imported Vitis evidence are unchanged.
A seventh verified working-tree checkpoint moves `Dense2dTileKMemFold v0`
host-harness rendering into `crates/spatial-rs-hls/src/tile_k.rs`, beside the
existing Tile-K kernel frame/body helpers. `emit.rs` remains the plan
dispatcher and ABI plan-to-frame adapter. This is no-HLS-drift backend helper
work; generated kernels, manifests, validation membership, and imported Vitis
evidence are unchanged.
An eighth verified working-tree checkpoint hardens `Dense2dTileScalarMul v0`
classifier admission by routing load/store tile-copy phases through the shared
resolver-backed rank-2 tile-copy fact helper after structural matching. It
checks same access grouping, same parent statement, loop-symbol identity, and
const-backed stride provenance before reconstructing the existing checked
payload. This is no-HLS-drift compiler foundation work; generated kernels,
manifests, validation membership, and imported Vitis evidence are unchanged.
A ninth verified working-tree checkpoint hardens `Dense2dTileDotAccum v0`
classifier admission by routing the lhs load, rhs load, and final accumulator
store through resolver-backed rank-2 access facts after structural matching. It
checks same access grouping, same parent statement, loop-symbol identity, and
const-backed stride provenance before reconstructing the existing checked
payload. This is no-HLS-drift compiler foundation work; generated kernels,
manifests, validation membership, and imported Vitis evidence are unchanged.
A tenth verified working-tree checkpoint moves the `MatrixTileAccum4x6x5`
host-harness renderer into `crates/spatial-rs-hls/src/dot_accum.rs`, beside the
existing rank-2 dot-accum kernel frame. `emit.rs` remains the plan dispatcher
and ABI plan-to-frame adapter. This is no-HLS-drift backend helper work;
generated kernels, manifests, validation membership, and imported Vitis
evidence are unchanged.
An eleventh verified working-tree checkpoint moves the non-outer-K
`Dense2dTileMemFold v0` host-harness renderer into
`crates/spatial-rs-hls/src/memfold.rs`, beside the existing MemFold kernel
frame. Split-C, tail, exact fixed-point, and explicit in-place C harness paths
still route through `emit.rs` as the plan dispatcher and ABI plan-to-frame
adapter. This is no-HLS-drift backend helper work; generated kernels,
manifests, validation membership, and imported Vitis evidence are unchanged.
A twelfth verified working-tree checkpoint moves the
`Lab1Part2DramSramExample` / `DenseScale64` host-harness renderer into
`crates/spatial-rs-hls/src/dense1d_tile_scalar_mul.rs`, beside the existing
rank-1 Dense1d kernel frame. `emit.rs` remains the plan dispatcher and ABI
plan-to-frame adapter. This is no-HLS-drift backend helper work; generated
kernels, manifests, validation membership, and imported Vitis evidence are
unchanged.
A thirteenth verified working-tree checkpoint moves square/non-square lab LUT
and `LutBiasLookup` host-harness rendering into
`crates/spatial-rs-hls/src/lut.rs`, beside the existing LUT kernel frame.
`emit.rs` remains the plan dispatcher and ABI plan-to-frame adapter. This is
no-HLS-drift backend helper work; generated kernels, manifests, validation
membership, and imported Vitis evidence are unchanged.
A fourteenth verified working-tree checkpoint moves `ScalarExpr v0`,
`ScalarReduce v0`, `ScalarFold v0`, and `ScalarSramTileFold v0` host-harness
rendering into `crates/spatial-rs-hls/src/scalar.rs`, beside the existing
scalar kernel frames. `emit.rs` remains the plan dispatcher and ABI
plan-to-frame adapter. This is no-HLS-drift backend helper work; generated
kernels, manifests, validation membership, and imported Vitis evidence are
unchanged.
A fifteenth verified working-tree checkpoint moves `MemReduceFill v0` and
`MemFoldFill v0` host-harness rendering into
`crates/spatial-rs-hls/src/mem_reduction_fill.rs`, beside the existing fill
kernel frame. `emit.rs` remains the plan dispatcher and ABI plan-to-frame
adapter. This is no-HLS-drift backend helper work; generated kernels,
manifests, validation membership, and imported Vitis evidence are unchanged.
A seventh verified working-tree checkpoint moves `Dense2dTileKMemFold v0`
host-harness rendering into `crates/spatial-rs-hls/src/tile_k.rs`, beside the
existing Tile-K kernel frame/body helpers. `emit.rs` remains the plan
dispatcher and ABI plan-to-frame adapter. This is no-HLS-drift backend helper
work; generated kernels, manifests, validation membership, and imported Vitis
evidence are unchanged.
Current and future vendor-HLS claims should pass the repo-local evidence
validator and the EC2 Rust/Cargo 1.75 compatibility gate.
The earlier raw-adapter-retirement current-head refresh, scheduled
row/column/K-tail roster expansion, serial row/column/K-tail run, current-head
harness cleanup, control/FSM plan-seam refresh, Tile-K loop-body cleanup,
literal-`2` MemReduce/MemFold lane, Tile-K proof refresh, Lab2 alternate FSM,
scheduled K-tail, current-head Tile-K facts, partition-helper,
schedule-profile, scheduled Part6 canary, Lab3 raw-wrapper, post-refactor
`ScalarSramTileFold v0`, and refreshed 26-program block-comment/raw-Part5
lanes remain historical evidence anchors.
It validates the original adapter baseline plus the reusable
scalar/dense/LUT/rank-2-copy/control/stencil/scalar-reduction/scalar-fold
representatives, the local all-ones `MemReduceOnes16` / `MemFoldOnes16`
canaries, `FifoTileScale32`, rank-2 tiled GEMM precursors, fixed-point MemFold,
tail/min MemFold, explicit-inout C MemFold, static exact outer-K in-place C,
scheduled Part6 outer-K, serial and scheduled K-tail, serial and scheduled
row/column/K-tail Tile-K canaries, plus the Lab1 Part6 `SramTileFoldSum32`
SRAM-tile fold canary through Vitis 2025.1
`csim_design` and `csynth_design`.
Current raw-wrapper ingress is retired from the quarantined source adapter. The
old raw Lab1 Part4 FIFO, Lab1 Part6 fold, Lab2 Part1/Part2 memory-reduction,
Lab2 Part3 alternate FSM, Lab2 Part4 square/non-square LUT, fixed Lab2
Part5/Part6 GEMM, and local Lab3 convolution teaching wrappers are reserved or
historical only; their Rust-subset or canonical payloads remain the regression
anchors. The Lab2 Part1/Part2 memory-reduction behavior stays covered by
`MemReduceOnes16` / `MemFoldOnes16` and the promoted `MemReduceFill v0` /
`MemFoldFill v0` family, while the old raw lab class names remain reserved.
The Rust-subset `MemReduceFill v0` / `MemFoldFill v0` frontend now accepts
supported static rank-1 lengths beyond the 16-lane lab representative and
arbitrary integer literal temp fills. `MemReduceTwos16` / `MemFoldTwos16`
remain the validation-member literal-`2` canaries with EC2/Vitis 2025.1
`csim_design`/`csynth_design` evidence, while local non-roster canaries such as
`MemReduceFives8` and `MemFoldSevens12` prove the broader static
length/literal-fill path through parser/classifier payloads and local HLS
harness execution. The retired raw Lab2 class names remain reserved, while
`MemReduceOnes16` / `MemFoldOnes16` remain the all-ones 16-lane
representatives.
The classifier now also proves the same narrow rank-1 memory-reduction shape
through resolved HIR loop/symbol facts, so equivalent Rust-subset static
length/step aliases are accepted without changing checked payloads, generated
HLS, manifests, validation membership, or the reserved raw-name boundary.
The follow-up affine HIR helper cleanup centralizes lane, constant, and
tile-plus-lane index predicates on `IndexUseFact` for rank-1, rank-2 Tile-K /
MemFold, and Stencil2d proof checks without changing generated HLS or the
validation roster.
The serial Tile-K MemFold path now has a named local K-tail canary,
`MatrixTileMemFoldOuterKTailInPlaceFixPt32x32x34`: the Lab2-like offset-loop
`numel_k = min(...)` spelling, in tile-size-first or remaining-first order, is preserved as checked
`k_bound` for `K=34`, `K_TILES=3`, and `TILE_K=16`, and HLS emits runtime
bounded K loops while local A/B storage remains statically `TILE_K` wide. This
is now the 29th validation-program member with EC2/Vitis `csim_design` and
`csynth_design` evidence captured in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-k-tail-29-program/`.
Except for wrappers that introduced or rode a new canonical validation payload,
these adapters route to existing canaries without adding validation-program
membership or new Vitis evidence. The fixed Lab2 Part5/Part6 wrappers now
accept only `runtimeArgs = "32 32 32"`, the exact named K-tail
`runtimeArgs = "32 32 34"` profile, or the exact row/column/K-tail
`runtimeArgs = "33 35 34"` profile. For `K=32`, Part5 canonicalizes to the
serial outer-K canary and Part6 canonicalizes to
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32`, preserving the
exact `par 2` / `par 16` source shape as checked schedule metadata and emitting
the corresponding HLS `PIPELINE`, `UNROLL`, and local-array partition pragmas.
For the exact `K=34` profile, raw Part5/Part6 canonicalize to the existing
serial/scheduled K-tail canaries with generated HLS/manifest equality.
For the exact `33 35 34` profile, raw Part5/Part6 canonicalize to the existing
serial/scheduled row/column/K-tail canaries with generated HLS/manifest
equality.
The structural Lab2-like outer-K bridge now reaches that same scheduled Part6
payload for infix tile IO, static offset-loop, and tile-size-first or
remaining-first static `numel_k = min(...)` source shapes when the partial-tile fill
loops carry literal `par 2` / `par 16` or parser-only `ROW_PAR` / `COL_PAR`
aliases resolving to those values. This remains an equality bridge with no new
validation-program member or emitted-HLS surface. The alias widening did not
rerun vendor HLS; the earlier exact bridge commit has a full 28-program
EC2/Vitis refresh in
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-02-part6-structural-408e21c/`.
The next exact GEMM canary has landed locally as
`MatrixTileMemFoldOuterKTailInPlacePart6ScheduledFixPt32x32x34`, combining the
named `K=34` serial tail bound with the fixed Part6 `par 2` / `par 16`
schedule. It is now the 30th validation-program member, with parser, checked-IR,
manifest, generated-HLS, native host-harness, Vitis dry-run/plan coverage, and
EC2/Vitis `csim_design`/`csynth_design` evidence. The HLS emitter uses runtime
`numel_k` for the K load/fold loops while preserving the scheduled array
partition, pipeline, and unroll pragmas. Vitis emits II-violation warnings on the
final C writeback pipeline, so this is a vendor-acceptance checkpoint, not a
performance-optimality claim.
As the next compiler-foundation slice, `ResolvedHir` now carries loop
schedule/identity/nesting facts and resolver-owned affine/index-use facts for
memory accesses, including access occurrence ids, parent-statement joins, and
const-backed affine stride provenance. These facts are observational and
crate-private. The Tile-K LHS-load, RHS-load, C-preload, final-store,
partial-product, and C-accumulation classifier submatchers now consume those
facts as narrow classifier-internal migrations while retaining the existing
syntax guards and exact access/parent-statement checks. The fixed Tile-K
phase-spine guard also cross-checks the recovered `kk_tile -> tile_r -> tile_c`
loop-domain chain, canonical schedule-bound symbols, hoisted or non-hoisted LHS
placement, and fold assignment ancestry through resolver-owned loop/effect
facts, while structural statement recovery remains private and fail-closed. The
C-preload migration is limited to the inout-C copy into `c_tile`, proving
`c_tile[ii, jj] := c[tile_r*TILE_R + ii, tile_c*TILE_C + jj]` through
local/global rank-2 access facts, loop-symbol identity, and const-backed
`TILE_R`/`TILE_C` coefficient-symbol provenance. The final-store migration is
limited to the inout-C writeback from `c_tile`, proving
`c[tile_r*TILE_R + ii, tile_c*TILE_C + jj] := c_tile[ii, jj]` through the same
resolver-owned access grouping, parent-statement, loop-symbol, and
coefficient-symbol provenance. The partial-product migration is limited to
`partial_tile[ii, jj] := lhs_tile[ii, k_idx] * rhs_tile[k_idx, jj]`, proving the
partial write, LHS read, and RHS read through resolver-owned access grouping,
same parent statement, and row/column/K lane symbol identity while retaining the
existing AST operator guard. The C-accumulation migration is limited to
`c_tile[ii, jj] := c_tile[ii, jj] + partial_tile[ii, jj]`, proving the C-tile
write, C-tile read, and partial-tile read through resolver-owned access grouping,
same parent statement, and row/column lane symbol identity while preserving the
existing AST operator guard and accepting the Lab2 MemFold sugar's same-span
sibling loop symbols. The fixed Tile-K phase spine is resolver-guarded, and the
first bounded role-driven phase-recognition slice now identifies the covered
pre-fold LHS load, RHS load, and C-preload roles through those same classifier
matchers before the fold/store pair. A follow-up structural-recovery cleanup
now identifies the covered `row_limit` and `col_limit` tail-bound lets by role
in either declaration order before those pre-fold phases. Broader Tile-K phase
discovery, fold/store reordering, arbitrary structural statement recovery, and
generic Spatial `MemFold` still remain unsupported.
The exact raw Lab1 Part6 wrapper is different: it canonicalizes to the
`SramTileFoldSum32` / `ScalarSramTileFold v0` structural canary, the 27th local
validation member. The local validation list later grew to 35 programs after
the separate scheduled Lab2 Part6
`MatrixTileMemFoldOuterKInPlacePart6ScheduledFixPt32x32x32` member, the named
serial/scheduled K-tail members, `Lab2Part3BasicCondFSMAlt`,
`MemReduceTwos16`, `MemFoldTwos16`, and the serial/scheduled row/column/K-tail
`33 35 34` Tile-K canaries. A then-current Tile-K HLS loop-body cleanup
checkpoint captured 33-program EC2/Vitis `csim_design`/`csynth_design` evidence
in `docs/vitis-validation/2026-07-03-tile-k-loop-body-current-head-33-program/`;
the active current-head vendor anchor is now the 39-program
`docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/` refresh.
The current Tile-K HLS backend-ledger cleanup has now moved K-loop bounds,
local storage declarations, schedule/partition preflight, serial/scheduled
tile-body rendering, and the kernel frame itself into crate-private HLS helper
modules while preserving generated HLS C++, manifests, validation membership,
and vendor-evidence boundaries. This is reliability work toward a cleaner Rust
HLS backend, not a new language feature; the current-head vendor refresh proves
the existing 33-program roster still passes after the cleanup.
A later no-HLS-drift dense backend slice moved the `Dense2dTileDotAccum`
renderer into `spatial_rs_hls::dot_accum`, matching the MemFold helper pattern
while preserving generated HLS, manifests, validation membership, and
vendor-evidence boundaries.
A later no-HLS-drift dense backend slice moved the `MatrixTileAccum4x6x5`
host harness into `spatial_rs_hls::dot_accum`, matching the same helper pattern
while preserving generated HLS, manifests, validation membership, and
vendor-evidence boundaries.
A later no-HLS-drift dense backend slice moved the non-outer-K
`Dense2dTileMemFold v0` host harness into `spatial_rs_hls::memfold`, matching
the same helper pattern while preserving generated HLS, manifests, validation
membership, and vendor-evidence boundaries.
A later no-HLS-drift dense backend slice moved the
`Lab1Part2DramSramExample` / `DenseScale64` host harness into
`spatial_rs_hls::dense1d_tile_scalar_mul`, matching the same helper pattern
while preserving generated HLS, manifests, validation membership, and
vendor-evidence boundaries.
A later no-HLS-drift dense backend slice moved the `Dense2dTileScalarMul`
renderer into `spatial_rs_hls::tile_scalar_mul`, matching the same small-helper
pattern while preserving generated HLS, manifests, validation membership, and
vendor-evidence boundaries.
Follow-up Rust commit `ed9c2d3703c4bb98b285ae0e5ac3bb746bad25b5` (`Accept Lab2
memory reduction call sugar`) added a parser-only normal-frontend bridge for
the simple Lab2 memory-reduction spelling: `SRAM[Int](16)`, `Foreach(16 by 1)`,
uppercase `MemReduce(acc)(-5 until 5 by 1)` / `MemFold(acc)(-5 until 5 by 1)`
with `_+_`, and `out store acc`. It lowers to the existing
`MemReduceOnes16` / `MemFoldOnes16` checked programs, keeps generated HLS and
manifests unchanged, and leaves the 33-program validation roster unchanged.
Local full workspace tests, clippy, Vitis dry-run emission, and 33-program
plan-only sidecars passed; vendor HLS was not rerun for this slice because it
does not alter emitted artifacts or validation membership.
Follow-up Rust commit `328e9fda3b2d160a0e2fbd5100707a4343d31d32` (`Extract
Tile-K HLS kernel frame`) continued the Tile-K HLS backend ledger by moving the
extern signature, AXI interface pragmas, outer tile-loop frame, and
array-partition pragma rendering into `spatial_rs_hls::tile_k` /
`spatial_rs_hls::partition`. The stable scheduled HLS snapshot, outer-K
equality tests, full workspace tests, clippy, Vitis dry-run emission, and
33-program plan-only sidecars all passed. Vendor HLS was not rerun because this
was a no-HLS-drift refactor with unchanged generated artifacts and validation
membership.
Follow-up Rust commit `fa33d55` (`Add serial Tile-K row-col tail canary`) added
the first local non-square Tile-K GEMM tail canary,
`MatrixTileMemFoldOuterKRowColTailInPlaceFixPt33x35x34`. This is a new local
feature slice rather than a no-drift refactor: parser/checker/HLS now carry
canonical `row_limit`, `col_limit`, and `numel_k` bounds for serial
`33x35x34` Tile-K MemFold while global DRAM addressing still strides by static
`TILE_R`, `TILE_C`, and `TILE_K`. The local validation roster is now 34
programs, with plan-only sidecars generated at
`target/vitis-validation-row-col-k-tail-34-plan/`. Full local tests, clippy,
HLS host-harness coverage, dry-run, and plan-only generation passed.
Follow-up commit `2087625` (`Keep core compatible with Rust 1.75`) kept the
same compiler behavior compatible with the EC2 Rust toolchain, and the full
34-program roster then passed EC2/Vitis `csim_design` and `csynth_design`.
Durable evidence is under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-row-col-k-tail-34-program/`.
The serial row/column/K-tail canary reports estimated Fmax 136.99 MHz and
latency 2329-274840 cycles on `xc7z020-clg400-1`. Scheduled Part6 row/column
tails were then promoted in follow-up commit `d521a0f` (`Add scheduled row-col
K-tail canary`). The new
`MatrixTileMemFoldOuterKRowColTailInPlacePart6ScheduledFixPt33x35x34` canary
keeps load/store loops runtime-bounded by `row_limit`/`col_limit`, keeps
scheduled compute loops static at 16-wide tile bounds, and guards inactive
lanes before `partial_tile` writes and `c_tile` accumulation. It is the 35th
validation member, and the full 35-program EC2/Vitis run passed
`csim_design` and `csynth_design`. Durable evidence is under
`/Users/david/Documents/David_code/spatial-rs/docs/vitis-validation/2026-07-03-scheduled-row-col-k-tail-35-program/`.
The scheduled row/column/K-tail canary reports estimated Fmax 136.99 MHz and
latency 2707-26872 cycles on `xc7z020-clg400-1`.
These wrappers are not generic Spatial `FIFO`, `Fold`, `MemReduce`, `MemFold`,
GEMM, generic `par`, automatic banking inference, board execution, timing
closure, or broad Scala source compatibility.

`ScalarExpr v0` is the first reusable supported feature rather than an exact
fixture adapter. It covers one scalar integer assignment over 1-4 scalar inputs
with nonnegative literals, `+`, `*`, and parentheses. The non-lab
`ScalarAffine4` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`.

`Dense1dScalarMul v0` is the second reusable supported feature. It covers one
rank-1 DRAM input, one scalar multiplier, one rank-1 DRAM output, two rank-1
SRAM tiles, positive static `N`/`TILE` with `N % TILE == 0`, and unit-stride
tiled load/compute/store. The non-lab `DenseScale64` representative has passed
local host-C++ and Vitis `csim_design`/`csynth_design`.

Dense 1-D DRAM/SRAM syntax no longer enters HIR as a fused whole-kernel marker.
The accepted dense path now parses and lowers through generic
`SequentialForeach`, loop-local SRAM, load, inner `Foreach`, indexed
assignment, and store nodes before the classifier reconstructs the same checked
dense adapter/feature programs. This is a frontend/HIR foundation step, not
generic loop scheduling or arbitrary memory lowering.

`LutLookup v0` is the third reusable supported feature. It covers one 2-D
integer LUT, scalar bias/row/column inputs, one scalar output, a rectangular
row-major literal payload, and exactly `out := bias + table[row, col]`. The
non-lab `LutBiasLookup` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`.

`Dram2dCopy v0` is the fourth reusable supported feature. It covers one rank-2
DRAM input, one matching rank-2 DRAM output, nested static row/column
`foreach` loops, and exactly `out[row, col] := in[row, col]`. The non-lab
`MatrixCopy4x6` representative has passed local host-C++ and Vitis
`csim_design`/`csynth_design`, and the original
`Lab3Part0MatrixCopyRowMajor` adapter now routes through the
frontend/HIR/classifier path instead of compact-source equality.

`spatial_rs_core::memory::Access` is the first shared checked memory-access
primitive. It centralizes rank-1/rank-2 positive-shape validation, index-rank
matching, and row-major C offset rendering for the rank-2 DRAM copy emitter.
This is an architectural foundation step only; it does not yet provide generic
effect scheduling, alias analysis, FSM/control lowering, stencil lowering, or
broad memory lowering.

Rank-2 copy opened the crate-private `HlsKernelPlan` path before C++ rendering,
and scalar assignment, LUT lookup, and control/FSM have now joined that path.
The scalar plan carries ordered scalar inputs, the scalar output, and the
precedence-safe expression AST; the LUT plan carries ordered scalar ports,
table dimensions, and row-major values; the rank-2 copy plan uses
manifest-derived ABI facts and the shared row-major index expression; the
control/FSM plan carries the output DRAM ABI, scratch SRAM, register/state
names, fixed loop length, register initialization/update values, and body-kind
variant. This is still not a generic HLS MIR or scheduler.
Rust commit `82ebd3f78a6cb7b00ac33764d7f8462a4ce0d8c9` (`Add scalar HLS plan
seam`) added this scalar seam with exact scalar snapshot preservation, full
workspace tests, clippy, Vitis dry-run emission, and 33-program plan-only
sidecars. Vendor HLS was not rerun because generated artifacts and validation
membership did not change.
Rust commit `c3405563c93c0d3050e0dd89ac02d30faac55940` (`Add LUT HLS plan
seam`) added the LUT plan seam in the same no-HLS-drift style:
`Lab2Part4LUT`, `Lab2Part4LUTNonSquareExample`, and `LutBiasLookup` keep exact
generated HLS and harness behavior while the renderer now consumes
`HlsKernelPlan`. Full workspace tests, clippy, Vitis dry-run emission, and the
33-program plan-only sidecars passed; vendor HLS was not rerun because emitted
artifacts and validation membership did not change.
Rust commit `740b5b7bc67d587903eb47f1a73884e36545d2b8` (`Add control FSM HLS
plan seam`) added the Lab2/control-FSM seam: `Lab2Part3BasicCondFSM`,
`Lab2Part3BasicCondFSMAlt`, and `ControlFsm32` keep generated HLS and harness
behavior while kernel rendering now consumes `HlsKernelPlan`. Full workspace
tests, clippy, Vitis dry-run emission, and the 33-program plan-only sidecars
passed; vendor HLS was not rerun because this is a no-HLS-drift compiler
foundation change.
The later ControlFsm backend renderer extraction moved the kernel frame/body
renderer for `Lab2Part3BasicCondFSM`, `Lab2Part3BasicCondFSMAlt`, and
`ControlFsm32` behind `spatial_rs_hls::control_fsm` while keeping `emit.rs` as
the dispatcher/orchestrator and leaving the host harness/oracle path in place.
It is local-only and byte-stable against the `da1da8d` baseline; no fresh
vendor-HLS evidence is claimed.
The follow-up ControlFsm harness helper extraction moved the ControlFsm
host-harness template and oracle selection into the same
`spatial_rs_hls::control_fsm` module while preserving the three ControlFsm
dry-run `kernel.cpp`, `harness.cpp`, and `manifest.json` artifacts against the
`bb83bce` baseline; no fresh vendor-HLS evidence is claimed.
The follow-up raw Lab2 LUT retirement commit
`702d1819e833d856820ff83bc9d1adb262e52b8a` removed the exact raw Scala
`Lab2Part4LUT` / `Lab2Part4LUTNonSquareExample` source-adapter ingress while
keeping the canonical square/non-square LUT payloads, reserved adapter names,
generated HLS, manifests, validation roster, and `LutLookup v0` feature
representative unchanged. Local dry-run artifact bytes matched the `d0d6c0f`
baseline for the two canonical Lab2 LUT fixtures plus `LutBiasLookup`; no
fresh vendor-HLS evidence is claimed.
The follow-up raw Lab2 FSM-alt retirement commit
`1e564a79332d45103413cc4f3d1d9ae86a3bc0c0` removed the exact raw Scala
`Lab2Part3BasicCondFSMAlt` source-adapter ingress while keeping the canonical
alternate FSM payload, reserved adapter name, generated HLS, manifests,
validation roster, and historical Vitis evidence unchanged. Local dry-run
artifact bytes matched the `702d181` baseline for `Lab2Part3BasicCondFSM`,
`Lab2Part3BasicCondFSMAlt`, and `ControlFsm32`; no fresh vendor-HLS evidence
is claimed.
Rust commit `b2f884534dac5a744d396b12fbe5bbfa574554df` (`Record control FSM
plan seam Vitis evidence`) then refreshed the full 33-program EC2/Vitis 2025.1
roster at that control/FSM plan-seam head. All validation programs passed
`csim_design` and `csynth_design`; the captured evidence directory is
`docs/vitis-validation/2026-07-03-control-fsm-plan-seam-current-head-33-program/`.

This proves useful local compiler plumbing:

- checked Rust construction
- ABI manifest emission
- independent oracles
- HLS-style C++ emission
- local host-C++ harness compile/run
- Vitis C simulation and HLS synthesis for the original adapter baseline,
  `ScalarExpr v0`, `Dense1dScalarMul v0`, `LutLookup v0`, `Dram2dCopy v0`,
  `ControlFsm v0`, `Stencil2d v0`, `ScalarReduce v0`, `ScalarFold v0`,
  `Fifo1dTileScalarMul v0`, `ScalarSramTileFold v0`, the local
  `MemReduceFill v0` / `MemFoldFill v0` canaries, including the literal-`2`
  `MemReduceTwos16` / `MemFoldTwos16` validation canaries, and the exact
  scheduled Lab2 Part6 HLS canary
- explicit rejection of unsupported forms

It does not yet prove:

- general Spatial parsing
- reusable lowering for generic `LineBuffer`, `RegFile`, generic reductions,
  generic memory folds/reductions, generic `par`, FIFO/streams, fixed-point,
  or GEMM
- generic memory/effect lowering beyond the selected dense and rank-2 copy
  shapes
- timing, resource, RTL, or board readiness

## Architecture Target

```text
accel! DSL source
  -> lexer/parser
  -> AST with spans
  -> typed Spatial HIR
  -> subset classifier and validators
  -> checked semantic IR
  -> manifest, ABI, partition, schedule, and provenance ledgers
  -> HLS lowering passes
  -> HLS C++ kernel and harness emission
  -> local host-C++ gate
  -> Vitis/Vivado csim and csynth gates
```

The student surface should remain a hardware DSL island. Rust is the compiler implementation language, not the language students need to master before learning hardware design.

## Vocabulary

- `accepted fixture adapter`: exact lab-shaped program accepted and checked through host-C++.
- `supported feature`: reusable semantic module with lab and non-lab tests, legal parameter perturbations, fail-closed negatives, and non-template HLS lowering.
- `host_cpp_structural_gate`: generated kernel and harness compile/run with the local system compiler.
- `vitis_csim_validated`: generated Vitis/Vivado project runs `csim_design`.
- `vitis_csynth_validated`: generated Vitis/Vivado project runs `csynth_design`, and reports record tool version, part, clock, latency, resource use, and accepted II.

Use `accepted fixture adapter` for the current `ProgramKind::LabX...` style cases unless a feature has graduated through reusable semantics.

## Feature Ladder

1. Scalar integer ports and arithmetic.
2. Dense 1-D DRAM/SRAM load-compute-store.
3. LUT lookup and row-major indexing.
4. FIFO and stream lowering.
5. Scalar `Fold` and `Reduce`.
6. `MemReduce` and `MemFold`.
7. FSMs with conditions, state updates, SRAM writes, and mux-like expressions.
8. 2-D DRAM/SRAM, fixed-point types, dynamic dimensions, and GEMM tiling.
9. Local-window/stencil lowering for `LineBuffer`, `RegFile`, `Reduce`, `mux`, `abs`, and `par`.
10. HLS performance surface: `PIPELINE`, `UNROLL`, `ARRAY_PARTITION`, vector ports, project Tcl, and report parsing.

## Near-Term Manager Plan

Historical post-FIFO decision: after the narrow FIFO v0 slice completed with
fresh 19-program Vitis evidence, the next phase became compiler foundation
rather than another ad hoc feature promotion. Current status: the compiler spine
exists, `ResolvedHir` now carries loop/effect/affine/index facts, and the
Tile-K LHS/RHS loads, C-preload, final-store, partial-product, and
C-accumulation submatchers consume those facts. The fixed Tile-K phase spine has
a resolver-backed guard, and a bounded role-driven phase-recognition slice now
identifies the covered pre-fold LHS/RHS/C-preload roles before the fold/store
pair. A follow-up no-HLS-drift structural-recovery slice now identifies the
covered `row_limit`/`col_limit` tail-bound lets by role in either declaration
order before the pre-fold phases. Broader phase discovery and arbitrary
structural statement recovery remain fail-closed/private. These
fact-consumption, role-recognition, and bound-recovery slices do not change
generated HLS/manifest output or validation membership. The current
non-outer-K `Dense2dTileMemFold` cleanup applies the same bounded role-recovery
principle to the local `MatrixTileMemFoldTail5x7x5` canary: canonical
`row_limit`/`col_limit` lets may appear in either declaration order, but phase
order, Int-only tail scope, checked payloads, generated HLS, manifests,
validation membership, and imported Vitis evidence remain fixed. The current
vendor-HLS anchor for the Tile-K compiler-foundation line is the 39-program
`docs/vitis-validation/2026-07-05-current-head-76158dd7-39-program/`
current-head refresh; the earlier 38-program Tile-K `par4x16` refresh and
resource-caveat reporting remain historical evidence for the pre-`par4x8`
roster. The
earlier 28-program
`docs/vitis-validation/2026-07-02-tile-k-facts-current-head/` run remains the
anchor for the narrower fact-consumption and same-span loop-symbol cleanup. The
structural Part6 source bridge is a later equivalence slice over the same
scheduled HLS surface, and its exact commit has its own 28-program vendor-HLS
refresh in `docs/vitis-validation/2026-07-02-part6-structural-408e21c/`.

Current local foundation continuation: Rust commit `26611e17` (`Guard Lab2
shell alias activation`) makes the Lab2 shell-alias bridge source-boundary
explicit: exact alias-name tokens do not activate canonicalization unless they
occur in local SRAM alias declarations. This preserves accepted Lab2
shell-alias buffer and infix tile-I/O behavior while keeping ordinary rank-2
copy sources with names like `tileA_sram` outside the Lab2 bridge.

Previous foundation continuation: Rust commit `be8511c9` (`Enforce Tile-K
schedule label factors`) makes explicit Tile-K `ParRxC` schedule labels fail
closed when they disagree with resolved/proven schedule facts, and locks the
Par4x16/Par4x8/Par2x8 resource policy to recorded Vitis evidence quality
without changing generated HLS, validation membership, or vendor evidence.

Earlier foundation continuation: the Tile-K MemFold classifier has a
private proof path on Rust commit
`24eb75b9d3a33003e1806fab5ea55055817deebe`. The classifier entrypoint preserves
the old cheap candidate precheck before resolver work, then routes true Tile-K
candidates through a proof-shaped result carrying the current serial/scheduled
full-K and K-tail profiles before rebuilding the same checked `Program`. The
proof constructor now builds the same `Dense2dTileKMemFold` payload directly
and rehydrates it through checked `Program` validation before accepting the
proof, so earlier diagnostic priority for invalid scheduled profiles is
preserved. This is deliberately not a syntax/HLS expansion: generated HLS and
validation membership stay unchanged, and EC2/Vitis is postponed until an
emitted artifact or validation roster changes.

Follow-up on Rust commit
`ab1697d6067186df415e955e1034307b3186fafb` (`Enrich Tile-K proof facts`):
the private proof now carries explicit source-shape and phase-spine sub-proofs.
Those facts record DRAM/SRAM roles, matrix/tile dimensions, outer/tile/lane
index names, canonical loop-bound symbols, K-tail `numel_k`, and hoisted-LHS
placement. Tile counts are validated from loop bounds rather than
source-shape matching. They remain private compiler facts for later
diagnostics/lowering; checked `Program` payloads, generated HLS, manifests,
validation membership, and Vitis evidence are unchanged.

Follow-up on Rust commit
`dd8fafbcbcd045d92acb94c7d7ee17f41319253a` (`Extract Tile-K source-shape proof`):
`prove_tile_k_source_shape` now owns the accepted Tile-K DRAM/SRAM role,
element-type, and matrix/tile-dimension proof before the main proof path
validates loop bounds, phase spine, access roles, fold schedule, payload, and
checked `Program` rehydration. This is still no-HLS-drift compiler
factoring.

Follow-up on Rust commit
`787510498f0fcca269db571b0418c4f6c4d6f773` (`Extract Tile-K phase-spine proof`):
`prove_tile_k_phase_spine` now owns the accepted Tile-K outer/tile loop
recovery, optional `numel_k`, canonical tile-count validation, exact/ceil
coverage checks, non-degenerate K-split validation, hoisted/non-hoisted phase
layout, phase statement recovery, and resolver-backed phase-spine ancestry
guard. Access-role matching, fold/update semantics, schedule extraction,
payload construction, and checked `Program` rehydration remain separate proof
path responsibilities. This is still no-HLS-drift compiler factoring; local
full gates passed and EC2/Vitis was skipped because emitted artifacts and
validation membership did not change.

Follow-up on Rust commit
`61d24eea248d73a4c46718bd278e3dae8fdc58ed` (`Extract Tile-K access-role proof`):
`prove_tile_k_access_roles` now owns LHS/RHS load role matching, shared
inner-K lane/bound agreement, canonical access bounds, C preload role matching,
C preload lane coherence, and final C-store proof. The helper returns owned
row/column/inner-K lane names and bounds to the remaining fold/update schedule
matcher and payload construction. This is still no-HLS-drift compiler
factoring; local full gates passed and EC2/Vitis was skipped because emitted
artifacts and validation membership did not change. The next internal proof
factoring target is fold/update schedule extraction.

Follow-up on Rust commit
`ee9132795951336bdd95225077efd7b5d4ee8763` (`Extract Tile-K fold schedule proof`):
`prove_tile_k_fold_schedule` now owns the partial-product and C-accumulation
fold matcher, including resolver-backed local read/write facts and serial/Part6
`partial_row_par` / `partial_col_par` recovery. The Tile-K proof path is now
staged as source shape, phase spine, access roles, fold schedule, payload
construction, and checked `Program` rehydration. This is still no-HLS-drift
compiler factoring. Follow-up commit
`962fbcec1ae979f02e7bfbf232f27dbb817ff20c` (`Tighten Tile-K fold schedule helper`)
made the helper return a Tile-K-specific schedule result and expanded direct
helper coverage across all four current Tile-K profiles. Local full gates
passed after both commits. A current-head EC2/Vitis refresh on commit
`962fbcec1ae979f02e7bfbf232f27dbb817ff20c` then passed all 31 validation
programs with `csim_design` and `csynth_design`; evidence is recorded in
`docs/vitis-validation/2026-07-03-tile-k-proof-current-head/`. This remains a
no-HLS-drift checkpoint because emitted artifacts and validation membership did
not change. Follow-up Rust commit `3137a8b` (`Start Tile-K HLS lowering ledger`)
created crate-private `spatial_rs_hls::tile_k` and moved runtime/static
K-loop-bound rendering out of the monolithic emitter into `tile_k_loop_bound`.
Follow-up Rust commit `100c18fa970dc4826a5a8c7ede96c6a701c376ab`
(`Extract Tile-K HLS local storage layout`) moved serial/scheduled local tile
array declarations into `tile_k_local_storage`. Existing Lab2 outer-K and
K-tail HLS/manifest preservation tests stayed green, the stable scheduled HLS
snapshot stayed byte-stable, and the plan-only validation roster remained 33
programs, so these are no-HLS-drift backend reliability slices. The next
manager move switched to the raw Lab2 GEMM source/Accel proof: follow-up Rust
commit `44cbbbbfa6fb06bbe980deac351ee26b3ca52c71` (`Extract raw Lab2 GEMM
source proof`) added a private source-adapter proof object for the fixed raw
Part5/Part6 shell profile and normalized single-`Accel` body before generated
frontend-source emission. This kept accepted profiles, HLS, manifests, and the
33-program validation roster unchanged, so it is also a no-HLS-drift compiler
structure slice. Later Rust commit
`47f9baa43f455f6078a514098f25ad7815a58298` (`Bridge raw GEMM to Tile-K
profiles`) closed the raw-to-checked-profile gap by validating accepted raw
Part5/Part6 generated frontend sources against neutral checked-IR Tile-K
profiles without changing HLS, manifests, validation membership, or vendor
evidence. Follow-up Rust commit `0f16af3e7b042554369ce69972da580078651c6a`
(`Record raw Lab3 source proof`) tightened the known local Lab3 teaching
wrapper from exact wrapper equality to a scoped source/local-window proof
before canonical `Lab3Part1Convolution` emission. It records direct class
image facts before `main`, main setup facts before the single `Accel`, and the
local-window `lb`/`sr`/`lineOut` plus `kh`/`kv`/border/`par 16` shape, with
negative tests for facts moved outside their valid scopes. HLS, manifests,
validation membership, and vendor evidence remain unchanged. Follow-up Rust
commit `5c21c48520b96425ee4303185ce262c699e02ac5`
(`Record no-HLS-drift helper checkpoints`) recorded the `Stencil2d v0` Sobel
source-shape/local-window proof object, an HLS/harness `int` extent-product
preflight guard, and the raw Lab3 direct-`main` `Accel` scope requirement while
preserving generated HLS, manifests, validation membership, and imported vendor
evidence. Follow-up Rust commit
`3bd86c13c5ffe99828b8cf6fa46f136d8746b6e9`
(`Extract Tile-K HLS schedule preflight`) continued the HLS ledger by moving
schedule/payload factor agreement, ordered Part6 partition-recipe validation,
and the serial no-partitions guard into `spatial_rs_hls::tile_k`; Lab2
outer-K/HLS equality tests and the 33-program plan-only roster remained stable.
Follow-up Rust commit `ed9c2d3703c4bb98b285ae0e5ac3bb746bad25b5` (`Accept Lab2
memory reduction call sugar`) switched the manager path back to EE109 source
coverage: the simple Lab2 memory-reduction frontend now accepts the narrow
Spatial-ish call syntax directly, with fail-closed tests for wrong bounds,
wrong fill, wrong store source, missing MemFold zero-init, wrong combiner, and
wrong local size. This is no-HLS-drift frontend coverage, not a new backend
feature.
Follow-up Rust commit `328e9fda3b2d160a0e2fbd5100707a4343d31d32` (`Extract
Tile-K HLS kernel frame`) switched back to HLS backend-ledger cleanup: the
Tile-K extern signature, AXI interface pragmas, outer tile-loop frame, and
array-partition pragma rendering now live in `spatial_rs_hls::tile_k` /
`spatial_rs_hls::partition` instead of the monolithic emitter. Stable scheduled
HLS and outer-K equality tests remained green, the 33-program plan-only roster
was regenerated, and vendor HLS was skipped because emitted artifacts and
validation membership did not change.
The later Stencil2d local-window role-payload slice keeps the rewrite moving
from stringly checked IR toward explicit proof-carrying payloads: the checked
`Stmt::Stencil2d` now stores typed `Stencil2dLineBuffer` and
`Stencil2dWindow` roles, validation rejects forged local-window role shape/type
metadata, and manifests still expose only the row SRAM plus Sobel LUTs. It is
no-HLS-drift and does not claim generic `LineBuffer` or `RegFile` lowering.
The subsequent Stencil2d const-role/order hardening removes the positional
`hir.consts[5]` load-par dependency. Reordered Sobel and Lab3 convolution
sources preserve the same checked payload, HLS, and manifests, while width
constants such as `COLS`, `CMAX`, and `LINE_COLS` still fail closed as invalid
load-par roles. This is also local-only and does not change validation-roster
membership or vendor-HLS evidence.
The next Stencil2d reduce-role source-shape canary accepts swapped declaration
order for the horizontal and vertical Sobel reduce lets. The classifier still
recovers roles from the LUT each reduce reads and still requires the canonical
`abs(horizontal) + abs(vertical)` row-output expression, so reordered Sobel and
Lab3 sources preserve the same checked payload, HLS, and manifests without
claiming generic `Reduce` or arbitrary stencil lowering.

The next small frontend/HIR foundation cleanup moves exact identifier binding
queries into `ResolvedHir`: symbol lookup by `HirIdent` plus `SymbolKind`,
symbol-id lookup, and single loop-domain lookup by loop-index identifier plus
`LoopKind`. `Dram2dCopy`, `ControlFsm`, and `Stencil2d` now share that
fail-closed helper surface while retaining their feature-local syntax, role,
schedule, and payload gates. The follow-up rank-2 tile-copy helper-boundary
cleanup now moves the shared local/global copy-role predicate into
`rank2_access.rs` for non-outer-K MemFold and Tile-K C preload/store paths,
while keeping feature-local syntax, schedule, const-symbol, and payload gates
in the classifiers. A second exact-binding migration now removes the remaining
classifier-local exact ident/span helper copies from scalar, LUT, 1-D tiled,
and reduction classifiers; those paths use `ResolvedHir::symbol_for_ident` /
`symbol_id_for_ident`, while name-only uniqueness helpers remain local. The
same cleanup line now centralizes remaining exact loop-index-to-domain lookups
for 1-D tiled and reduction classifiers in `ResolvedHir`; kind-only loop-domain
discovery remains local where no concrete source identifier is being bound.
The following rank-2 local-compute helper-boundary cleanup moves the shared
partial-product/C-accumulation proof wrapper layer into `rank2_access.rs` as
well, while `tiled2d.rs` and `tiled2d/tile_k.rs` keep `TilePhase`, MemFold
syntax guards, Tile-K schedule checks, and checked-payload construction. This
is still no-HLS-drift compiler-foundation work.
The next rank-2 tiled-load helper-boundary cleanup moves the shared MemFold and
Tile-K LHS/RHS local-write/global-read fact comparison into `rank2_access.rs`.
The helper owns expected plain-lane and tile-plus-lane dimension checks; the
feature classifiers still own source syntax, schedule/role guards,
const-symbol lookup, and checked-payload construction. This remains
no-HLS-drift foundation work, not a new Spatial syntax or HLS lowering feature.

ResolvedHir update: the reviewed design now lives in the Rust repo as
`docs/superpowers/specs/2026-06-28-resolved-hir-design.md`. It preserves checked
`Program` as the HLS contract, reserves resolver diagnostics to
`spatial:E0301` through `spatial:E0310`, and makes the next implementation slice
crate-private and test-first so HLS output and validation membership stay
unchanged.

The already-completed foundation items below remain useful historical context:

1. Reword repo docs so they describe the Rust rewrite correctly and stop overclaiming fixture adapters as general support.
2. Add a source model for `parse_accel(&str)`: source id, byte ranges, line/column lookup, and diagnostic labels. Keep `macro_rules! accel` on `stringify!` until a proc-macro is worth its cost.
3. Add a real frontend path: tokenization, AST, source spans, and typed HIR for scalar ports, LUTs, dense 1-D DRAM/SRAM, expressions, loops, loads, and stores.
4. Add a first-class EE109 subset classifier that consumes HIR and produces checked semantic modules or fixture adapters.
5. Decouple semantic feature identity from lab kernel names before adding non-lab semantic-equivalent tests.
6. Route scalar/LUT/dense/rank-2 copy accepted adapters through `AST -> HIR -> EE109 subset classifier -> checked Program` while keeping current host-C++ outputs stable.
7. Keep Lab3 convolution explicitly transitional and opaque until reusable local-window/stencil lowering exists.
8. Add HLS project artifact generation in dry-run mode: top name, part, clock, kernel/harness paths, and `run_hls.tcl`.
9. Use the EC2 Vitis lane as a regular gate for every promoted supported-feature slice.
10. Extend the new memory foundation toward checked `Shape`/effect/layout views
   shared by validation, manifesting, and HLS lowering.
11. Extend the new HLS plan seam beyond rank-2 copy to dense/LUT/scalar/control
   after exact output-preservation tests are in place.
12. Factor shared loop, memory, expression, and control structure before promoting FIFO, reductions, FSM variants, or Lab3-style performance/synthesis readiness.

## Guardrails

- No new `compact_source(EXACT_FIXTURE)` cases outside a clearly named fixture-adapter layer.
- No new `ProgramKind::LabX...` without a retirement criterion.
- No generic support claim until there is at least one non-lab semantic test.
- No vendor HLS claim without fresh tool evidence.
- No direct port of Scala `HLSGen`; preserve its useful semantics and fixtures, but design Rust modules around frontend, HIR, validation, manifests, lowering, diagnostics, and HLS emission.
