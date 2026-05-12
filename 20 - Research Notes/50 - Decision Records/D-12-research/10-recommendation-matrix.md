---
type: research
decision: D-12
angle: 10
---

# Recommendation Matrix and Failure Modes

## Decision Frame

Q-137 asks whether the Rust port preserves Argon's `enableMutableAliases` escape hatch or makes mutable aliasing a hard error (`20 - Open Questions.md:1968-1973`). The source baseline is asymmetric: Argon defaults the flag to false and reports mutable-alias errors only when the alias candidate set is nonempty and the flag is not enabled, while immutable writes remain unconditional errors (`01-argon-current-alias-check.md:13-17`; `30 - Effects and Aliasing.md:129-133`). Spatial deliberately flips the policy with the comment that DRAM, SRAM, and similar memories allow mutable aliases, and public memory APIs, tests, examples, and dealiasing passes rely on alias views rather than treating them as accidental host-language aliases (`02-spatial-settings-usage.md:5-17`). The decision is therefore about the Spatial IR legality contract, not whether Rust's own `&mut` rule should replace the staged alias/effect graph (`10 - Effects and Aliasing.md:61-63`; `07-spec-open-question-contract.md:19-21`).

## Matrix

| Option | Correctness | Compatibility | HLS scheduling risk | Implementation cost | Migration risk |
|---|---|---|---|---|---|
| **Default-hard-error** | Strong for a new Rust-like ownership story, but source-divergent because Spatial aliases are first-class graph metadata and mutable symbols are identified through effects, not an ownership bit (`04-rust-ownership-options.md:5-9`). | Poor: rejects DRAM/SRAM views, `par` views, nested aliases, and transfer examples that Spatial accepts (`02-spatial-settings-usage.md:9-13`). | Low only because it removes hard cases; it may also remove legal alias patterns the scheduler/dealiaser expects. | Low-medium: one validation rule, but downstream tests and docs churn. | High: users experience accepted Spatial code as newly illegal. |
| **Legacy flag parity** | Source-faithful if Rust reproduces `checkAliases`, immutable-write errors, write propagation, and anti-dependency computation (`04-rust-ownership-options.md:19-21`). | Best: matches Spatial's current global enablement and compiler expectation (`02-spatial-settings-usage.md:5`, `02-spatial-settings-usage.md:17`). | Medium: HLS must remain conservative because aliases can denote the same storage; risk is controlled only if expanded `reads`, `writes`, and `antiDeps` are exact (`04-rust-ownership-options.md:9`). | Medium: port existing dataflow and config surface. | Low initially, but strictness debt remains. |
| **Memory-alias allowlist** | Medium: hard-error by default, but allow known memory-view nodes such as dense/sparse aliases. Correct only if the allowlist is semantic, not syntactic (`02-spatial-settings-usage.md:9`; `04-rust-ownership-options.md:7`). | Medium-high for known DRAM/SRAM/RegFile/LockSRAM views; fragile for library growth and transformed aliases. | Medium-low when allowlisted nodes still participate in alias closure; high if the allowlist bypasses effect propagation. | Medium: needs node taxonomy and regression coverage. | Medium: misses show up as surprising rejects. |
| **Explicit alias-capability / provenance model** | Best long-term: alias creation carries base, range, mode, provenance, and optional disjointness proof while still recording Argon-compatible effects (`04-rust-ownership-options.md:15-17`). | High if introduced behind legacy compatibility; low if required immediately. | Lowest long-term: capabilities can feed conservative dependence by default and justify HLS pragmas only when provenance proves disjoint banks/ranges. | High: new schema, diagnostics, proof rules, and lowering hooks. | Medium-high unless staged gradually. |
| **Warning-only** | Weak: diagnostics exist, but illegal or unsupported aliasing remains accepted even when Rust wants a stricter contract. Argon diagnostics are useful provenance, not a replacement for policy (`04-rust-ownership-options.md:23-25`). | High short-term. | High: warnings can be ignored while HLS scheduling silently assumes unsafe independence. | Low. | Hidden high: failures move from compile time to synthesis/simulation mismatch. |

## Failure Modes

The hard-error failure mode is semantic amputation: it treats Spatial views as unsound Rust references, even though Spatial's compiler has dedicated alias rewrites and dealiasing support (`02-spatial-settings-usage.md:15-17`). The legacy-flag failure mode is the opposite: implementing "flag on" as "skip all alias reasoning." That would be unsound, because the compatibility flag only suppresses one error path; write propagation, mutable-input reads, and anti-dependencies still define scheduler-visible effects (`01-argon-current-alias-check.md:19-21`; `30 - Effects and Aliasing.md:135-142`).

The allowlist failure mode is taxonomy drift: a new memory view, transformed alias, or sparse access path is rejected or, worse, accepted without full effect propagation. The capability model's failure mode is overdesign before migration: a beautiful provenance system can block the first Rust port if every existing view must gain range proofs up front. Warning-only fails by turning an architectural decision into log noise; it preserves compatibility but provides no hard contract for HLS.

## Preliminary Recommendation

**Preliminary recommendation: choose legacy flag parity for v1, with unconditional diagnostics and an explicit migration path to alias capabilities.** This keeps Rust aligned with current Spatial behavior while avoiding the misleading idea that Rust ownership alone explains the IR. The mode should default according to the chosen Spatial compatibility profile, preserve immutable-write hard errors, retain the "aliases already being written are not flagged" exception, and label every accepted mutable alias with provenance suitable for later capability checking (`07-spec-open-question-contract.md:11-21`). The strict hard-error mode should exist as a conformance target only after memory alias capabilities can distinguish legal views from genuinely unsafe aliasing.
