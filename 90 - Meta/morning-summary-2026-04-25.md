---
type: research-note
project: spatial-spec
status: draft
date: 2026-04-25
---

# Morning Summary — 2026-04-25

## TL;DR

Phase 2 is substantially complete. The six missing Fringe/Targets specs were written, the open-question tracker was consolidated into one global Q-001..Q-164 sequence, an adversarial citation review was produced, and Phase 3 HLS mapping was kicked off with all spec entries classified. The main thing left is not more bulk writing; it is human judgment on the highest-risk semantics and whether to apply the citation-range fixes found in review.

## Final Tally

- `10 - Spec/`: 108 markdown files total, including 96 `type: spec` entries and 12 MOC/index files.
- Citations: 933 frontmatter `source_files` references; 4,582 explicit Scala file:line mentions across spec entries.
- Open questions: 164 total in [[20 - Open Questions]], including 158 Phase 2 questions consolidated from per-topic trackers.
- HLS classifications: 96 total — 23 clean, 58 needs rework, 15 Chisel-specific.
- Adversarial review: 26 entries reviewed; 303 citations checked; 17 line-range corrections found.

## Top 5 User-actionable Items

1. Review `[[30 - Adversarial Review]]` and decide whether to apply the 17 one-line citation corrections.
2. Decide FMA semantics for HLS: `[[20 - Open Questions#Q-146 — [2026-04-25] FMA fused versus Scalagen unfused semantics (originally Q-sem-11)|Q-146]]`.
3. Decide fixed-point unbiased rounding policy: preserve RNG behavior or make it deterministic, tracked by Q-144 and Q-118.
4. Decide whether HLS FIFO/LIFO semantics follow Scalagen's elastic simulator or RTL back-pressure, tracked by Q-150.
5. Start Phase 3 from `[[40 - Open HLS Questions]]`, then update the clean/rework/Chisel mapping rationales as decisions land.

## Needs Human Judgment

- Scalagen is called the reference semantics, but several known cases diverge from Chisel: FMA, FIFO/LIFO back-pressure, OneHotMux, and simulator OOB behavior.
- `MemoryAllocator` executes concrete first-fit allocation but still prints `TODO: un-gut memory allocator`; decide how much trust the Rust/HLS rewrite should place in that pass.
- The HLS host ABI needs a new source of truth to replace Fringe register maps, Chisel globals, and generated host launch metadata.
- Per-topic open-question files remain on disk to preserve links; decide whether to archive them after link cleanup.

## Next Session

Pick up with Phase 3 architecture decisions, not more Phase 2 inventory. Recommended order: FMA and numeric determinism, FIFO/LIFO and stream back-pressure, host ABI manifest, HLS banking/partition strategy, then DSE/model replacement.
