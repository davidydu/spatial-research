---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-25
---

# Open HLS Questions

Top architectural questions for the Rust plus HLS rewrite, drawn from the consolidated tracker in [[20 - Open Questions]].

1. Q-146, originally Q-sem-11 — FMA fused versus Scalagen unfused semantics: should HLS match Chisel's fused hardware path or Scalagen's emitted `($m1 * $m2) + $add` reference behavior?
2. Q-144, originally Q-sem-09 — Unbiased rounding nondeterminism: should the rewrite preserve Spatial's RNG-based fixed-point rounding or replace it with deterministic round-to-nearest behavior?
3. Q-150, originally Q-sem-15 — FIFO and LIFO elastic simulator versus back-pressure: should HLS semantics follow Scalagen's enqueue-without-back-pressure model or synthesized RTL handshakes?
4. Q-149, originally Q-sem-14 — Target accepted II versus compilerII: what is the contract when HLS scheduling produces an II different from Spatial metadata?
5. Q-112, originally Q-pmd-04 — Banking-search pruning strategy for HLS: should Spatial's existing alpha/N/B solver be reused, restricted to HLS partition forms, or replaced?
6. Q-152, originally Q-sem-17 — HLS host ABI manifest: what should replace Chisel/Fringe register maps, scalar argument layout, and generated host-side launch metadata?
7. Q-083, originally Q-mdf-05 — HLS replacement for Chisel instantiation globals: how should target, stream widths, memory channels, and file dependencies be represented without mutable Chisel globals?
8. Q-142, originally Q-sem-07 — OOB simulator versus synthesized hardware: should HLS preserve simulator invalid-value fallbacks, synthesize guards, or leave OOB undefined?
9. Q-154, originally Q-sem-19 — OneHotMux multi-true semantics: should HLS define priority, reject non-one-hot inputs, or reproduce Scalagen's bitwise-OR behavior?
10. Q-116, originally Q-pmd-08 — Runtime-model replacement for HLS DSE: should Phase 3 keep Spatial's runtime model path, build a static HLS model, or defer DSE until after code generation is stable?

Secondary candidates: Q-145 FloatPoint clamp heuristics, Q-130 transcendental precision, Q-118 duplicate unbiased-rounding tracker, Q-079 memory-resource taxonomy, Q-114 dense-load latency replacement, and Q-036 BigIP optional arithmetic behavior.
