---
type: log
project: spatial-spec
---

# Progress Log

Append-only, newest-first within day blocks. One line per discrete action when possible.

---

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
