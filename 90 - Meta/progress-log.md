---
type: log
project: spatial-spec
---

# Progress Log

Append-only, newest-first within day blocks. One line per discrete action when possible.

---


## 2026-06-30 — Rust rewrite source-spelling bridge

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
