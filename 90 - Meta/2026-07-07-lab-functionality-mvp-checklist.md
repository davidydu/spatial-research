---
type: design
project: spatial-spec
date: 2026-07-07
status: active
depends_on:
  - "[[2026-06-27-rust-spatial-rewrite-roadmap]]"
  - "[[50 - EE109 MVP Blocker Matrix]]"
---

# Lab-Functionality MVP Checklist (Vault Record)

Authoritative ledger:
`/Users/david/Documents/David_code/spatial-rs/docs/lab-functionality-mvp-checklist.md`
(Rust repo commit `639f2de9`, branch `David/HLS-spatial`). This vault note
records the decision and definitions; checkbox state lives in the repo file
and each tick is mirrored into [[progress-log]].

## Why

The stated MVP is "support all functionality of Spatial used in the EE109
labs." That goal has two readings, and slice selection was drifting toward
spelling pins and no-HLS-drift refactors without a crisp definition of done:

- **MVP-A (lab-program acceptance)** — every Spatial class in the three lab
  checkouts compiles through a canonical Rust-subset representative with
  EC2/Vitis `csim_design` + `csynth_design` evidence. **Complete** at the
  39-program checkpoint (source commit `76158dd7`), with the recorded
  `resource_fit=37/39` and `ii_caveated=14` caveats.
- **MVP-B (lab-functionality acceptance)** — the knobs students actually turn
  are supported features under the repo's graduation standard: runtime GEMM
  dimensions (`ArgIn` M/N/K, per
  `lab-2-accelerator-bandits-2/src/test/scala/Lab2GEMM.scala:12-17`), `par`
  factor exploration, edited reducer/fill bodies, changed LUT/stencil
  constants, plus a standalone compile command. **Open** — tracked by the
  repo checklist sections G1-G11.

## Ground Rules Recorded

- Ticks require the six-point graduation standard (proof facts, perturbation
  tests, fail-closed negatives, host gate, dry-run gate, evidence policy).
- HLS-changing slices need a selected EC2/Vitis run before any tick; roster
  promotion needs a full refresh.
- Non-goals pinned: Scala source compatibility, F2/board execution, `Float`,
  inferred banking/scheduling, streams, rank-2 reductions, non-3x3 stencils.

## Open Items Snapshot (2026-07-07)

G2 tail diagnostic; G3/G4/G5 bounded body-expression family; G6 FSM
step/threshold constants; G7 LUT dims/values; G8 static-shape freedom,
dynamic dims, par legality model, QoR sweep; G9 stencil coefficients/dims/
load-par; G10 compile CLI + diagnostic goldens; G11 cosim/impl tier
(recommended). See the repo file for exact acceptance criteria.
