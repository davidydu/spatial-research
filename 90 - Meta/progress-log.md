---
type: log
project: spatial-spec
---

# Progress Log

Append-only, newest-first within day blocks. One line per discrete action when possible.

---

## 2026-06-28 — Rust rewrite frontend/HIR foundation

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
