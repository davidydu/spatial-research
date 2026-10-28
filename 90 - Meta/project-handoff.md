---
type: runbook
project: spatial-python
date: 2026-10-22
status: active
---

# Spatial — shared project handoff

Start here in Codex, Claude Code or any other harness. This file preserves the
project context previously carried in chat and private agent memory. Existing
decisions, plans and evidence remain in their owning documents; this is the map
and restart route. No private memory service, old agent session or temporary
directory is required.

**26 October direction decision — current plan:** a direction review found the
research sufficient to start and to implement Lab 1–3 language semantics, but
not yet to finish the hardware half. David approved its recommendations: after
the corrected scalar-interface vendor batch, close the roadmap's S1 exit before
any Labs family or optimization; the next hardware milestone is an AWS F2 profile
with loop pipelining enabled; thin PlanRecords precede any check elision. The
vendor tooling and its acceptance rules are prepared and calibrated against the
22 October outputs; the host stays stopped until David's restart notice. The
compiler's `PROJECT_STATE.md` is the single current status; read it first. The
professor's response to the 22 October meeting is still to be recorded.

**27 October progress:** E1 (public check/prepare and an experimental compile-once native handle) and E2 (canonical SpatialJSON-v1 export and import) are complete, and the vendor batch passed ([[2026-10-27-scalar-interface-vitis-checkpoint]]). E3, the builder with its pending-effect ledger, is next.

**28 October order:** David approved E3 (trimmed builder) → E4 → E7 → E5, then Lab 1–3 features, with E6 and E8 after the labs and AWS F2 in parallel. He is arranging an F2 instance; the professor mentioned F2 at the 22 October meeting. The course uses Python Spatial in about six months, and each week should show the professor visible progress.

**22 October scalar interface correction — preceding local checkpoint:**
[[2026-10-22-scalar-interface-checkpoint]] records production `72fd513`, explicit seeds and output-only snapshots, and a small report correspondence reader. Both complete source and isolated-wheel suites pass 1,351 tests. The prepared batch has 15 projects/46 cases, including a fresh six-case composition that passed without repair. The previous hardware result below belongs to unchanged old wrappers. Resume from compiler `PROJECT_STATE.md` and `docs/plans/2026-10-22-scalar-interface.md`; new synthesis and RTL validation require host availability.

**27 October vendor checkpoint — latest hardware evidence:** [[2026-10-27-scalar-interface-vitis-checkpoint]]. The corrected scalar-interface batch passes all nine pre-registered rules on its third run. The first run failed one rule on two zero-latency fixtures, the rule was corrected with David's approval, and the second run had a staging-path error. All three runs are kept, and their hardware outputs are byte-identical.

**22 October completed vendor batch — earlier hardware evidence:** David supplied the
running HLS host and authorized the prepared scalar/shift batch after the earlier
meeting pause. [[2026-10-22-scalar-vitis-checkpoint]] records all 12 unchanged
projects and 32 independently specified cases passing C simulation, synthesis and
Verilog RTL co-simulation. Production remains `1e55eb8`; no language or student
API increment was made. The compiler's
`docs/evidence/task-06d-scalar-vendor.md` owns the exact evidence and limitations.
The subsequent local correction makes scalar interface policy explicit; actual
report correspondence for its new wrapper remains pending. Vitis ignored the
old depth-one `ap_memory` requests. Then complete a matched cost study before choosing
an optimization. Read the current checkpoint below and compiler `PROJECT_STATE.md`.

**Earlier 22 October meeting pause:** David asked to pause compiler
and HLS work before the professor meeting. At that point work concerned the
presentation and research navigation. [[2026-10-22-python-pipeline-presentation]] owns the
ten-minute, seven-slide story: follow up on the professor's fully Python request,
explain the architecture, and use the existing Lab 1 tiled-scale result as one
initial success through Python, generated C++, HLS and RTL simulation.

The saved scalar/shift batch was ready, with compiler work and vendor execution
paused until David asked. His later host instruction authorized the completed
batch above; it did not authorize instance lifecycle changes or a new language
increment. The seven-slide deck and matching script have been reviewed
against saved evidence, including desktop/phone layout and interactive controls.
The compiler project-state publication record holds the final deployment result.

**22 October student testing direction:** David prefers generated C++ software
execution as the normal student-facing backend, with the Python reference engine
used internally for language/compiler verification. He approved the lab-style
model of inputs, independent expected answers and self-checking tests, and asked
to expose custom testing for open-ended final projects. Documentation now starts
at [[00 - Python Spatial Student Guide]], with basic and advanced guides. Ordinary
Python test functions, generators and custom assertions stay outside captured
kernel syntax. Reusable concrete cases can feed generated C++ testbenches for
Vitis and RTL; arbitrary Python tests are not translated into hardware. Public
wrappers, compile-once execution and convenient case export are planned, not
implemented. Existing internal native/HLS tools are linked. This documentation
direction does not resume implementation or vendor execution, remove reference
conformance obligations, or freeze a new public API spelling.

**Documentation ownership clarification:** David wants the student guide developed
alongside the language in this same vault for now. Every user-visible feature
checkpoint should update its explanation, syntax, example, functional test and
support status. Keep one editable source. Later, move or export the curated
student documentation into a docs-only public presentation, with student
navigation and no research handoffs or historical design material. Do not create
a separate docs repository/site yet. The existing research site is already public;
this organizational choice does not change visibility or promise private drafts.

## Read only what the next task needs

1. Read [[workflow]] and [[80 - Initial Compiler Goal]] for the current route.
2. For compiler work, read `AGENTS.md` and `PROJECT_STATE.md` on the implementation
   branch, then its active plan and the relevant checkpoint design/evidence.
3. For research, start at [[00 - Python Rewrite Index]] and the relevant study;
   keep decisions in the existing D-number register.
4. For presentation work, read [[05 - Python Professor Brief]],
   [[2026-10-22-python-pipeline-presentation]] and
   [[70 - Engineering Architecture Map]]. Verify progress against current
   compiler evidence before updating slides. Keep
   [[2026-10-21-python-progress-presentation]] as the earlier reference-only record.

## Repository map

Local paths below describe the current machine. Use repository URLs and branches
on another machine; do not make another harness depend on these absolute paths.

| Responsibility | Repository / branch | Local checkout |
|---|---|---|
| Research, decisions, specifications, progress | [spatial-research](https://github.com/davidydu/spatial-research), `main` | `/Users/david/Documents/Spatial Research` |
| Python compiler and test evidence | [spatial-py](https://github.com/davidydu/spatial-py/tree/work/initial-reference), `work/initial-reference` | `/Users/david/Documents/David_code/spatial-py/.worktrees/initial-reference` |
| Documentation build and presentation UI | [spatial-research-site](https://github.com/davidydu/spatial-research-site), `main` | `/Users/david/Documents/spatial-research-site` |
| Original Scala source evidence | Local reference clone; see [[reference-clones]] | `/Users/david/Documents/David_code/spatial` |

**Checkout trap:** the outer `David_code/spatial-py` directory is bootstrap
`main`, not the working compiler. Inspect Git status, branch and worktree list
before edits. Use the existing implementation worktree, or check out
`work/initial-reference` on a new machine. Do not merge or restart the compiler
just because the bootstrap checkout has little code. Earlier `spatial-rs` work
and Rust presentations are historical evidence.

## Decisions and user preferences from the conversation

- The professor requested a fully Python compiler after the earlier Python
  frontend/Rust-core proposal. Python owns the frontend, checker, reference
  engine and C++ generator. Generated C++ is target output, vendor HLS is external,
  and there is no Rust compiler core. One bounded hardware path now works;
  the full compiler and checked target planner remain unfinished.
- On 21 October David agreed to keep the Python compiler core, review hardware
  mapping now, and bring a small general HLS feasibility experiment forward.
  [[2026-10-21-hls-feasibility-checkpoint]] supersedes the 17 October instruction
  to finish all planned language/reference support before HLS. EE109 Labs 1–3
  still guide reusable language coverage and varied student programs. He corrected an
  initial mention of Lab 4: there are three labs. Use their memory/control/numeric
  patterns to choose small executable increments and require cross-feature
  compositions. Avoid both lab-specific compiler paths and unrelated verifier
  expansion. [[04 - Python Implementation Roadmap]] owns the revised progression.
- Assume a capable team and capable coding agents. Earlier Rust arguments based
  on maintenance skill or type safety are not grounds to reopen that direction.
- David authorized the initial implementation on 4 October. [[D-27]] owns the
  direction; [[D-28]] and the implementation blueprints describe the detailed
  proposal. User authorization is separate from professor approval of every
  architectural detail. No new implementation approval question was pending for
  continuing the initial goal.
- Research and compare designs before implementation. Implement general rules
  and unfamiliar compositions. A cherry-picked lab example or fixture-specific
  compiler path is not acceptance.
- Use agents for bounded parallel work to control time and cost. The integrating
  agent personally reviews their work. Codex agents are preferred; later user
  messages also authorize Claude Opus 5.5 through `claude2 -p`, with the approved
  account checked locally. Opus supersedes the earlier Fable preference. A
  harness without those tools may use equivalent independent review roles.
- Read local files and use command-line checks by default. Use browser UI when
  visual or interactive inspection is necessary. Preserve coherent Git
  checkpoints under `davidydu`; update research documentation with results.
- Professor-facing material should lead with the big picture, concrete progress
  and links. The main talk is about ten minutes. Explain what Python Spatial is,
  why the plan is feasible, implementation steps and next evidence. The professor
  already knows Spatial; avoid long program walkthroughs or re-arguing HLS.
- For the October 22 meeting, center one existing Lab 1 success through the
  complete experimental pipeline. Keep the four-kernel result as supporting
  context and the newer local scalar/shift extension separate from vendor
  evidence. Use a simple verbal explanation, then limitations and next steps;
  test internals and full source walkthroughs belong in linked records.
- Use plain, verbal scripts and explanatory slide text. The requested visual
  direction is restrained, inspired by Thinking Machines Lab. The Excalidraw map
  should support both overview and detail; render and inspect visual changes.
  Interactive illustrations are not executions of the compiler.

## Current checkpoint and next task

**22 October scalar/shift vendor run — latest hardware evidence:**
[[2026-10-22-scalar-vitis-checkpoint]] records all 12 projects and 32 cases through
Vitis C simulation, synthesis and Verilog RTL co-simulation: 27 successful
completions and five expected faults, with RTL post-checks of data, initialization,
status and fault owner. The same frozen sources and expected values were used.
All 110 production files, 287 execution files, 133 original inputs and 133 staged
inputs match; all 680 downloaded evidence files were hash-verified. The repository
retains 668 of those vendor files byte-for-byte. Twelve redundant simulator logs
with private infrastructure headers are omitted and recorded by hash; the raw
archive stays private. No compiler behavior changed, and no full-suite rerun is
claimed for this vendor-only checkpoint.

**Restart task:** validate the new explicit scalar wrapper with fresh Vitis
reports and RTL before broader IP integration. The local policy and reader are
implemented; see [[2026-10-22-scalar-interface-checkpoint]]. The reason for this correction remains: Vitis warning HLS 207-5572 rejects the requested depth-one
`ap_memory` protocol. In `scalar-sum`, scalar InOut uses `ap_ovld` and scalar Out
uses `ap_vld`. In the fresh composition, Out result data uses `ap_vld` but its
read/written initialization mask uses `ap_ovld`. Logical behavior passed; the
manifest's requested physical interface did not. Check actual report mappings
for data and initialization separately, including fault/incomplete-output cases.
Invocations are explicitly seeded; no automatic state feedback between calls is
established. Preserve the existing evidence unchanged.

Then use the saved size/tile variants for a matched cost study before selecting
one general storage or scheduling change. At map length 32, tile capacity 4
takes 581 RTL cycles and capacity 16 takes 767; fewer tiles do not establish a
faster schedule. Keep fault-path timing separate, distinguish transaction
interval from loop II, and exclude external port memories from claims about the
reported resource totals. The profile remains sequential; board/AXI integration,
routed timing and optimized parallelism remain open. Instance lifecycle changes
still require David's instruction; do not infer shutdown from completed jobs.

**21 October scalar state and shifts — preceding local implementation:**
[[2026-10-21-scalar-target-checkpoint]] records production
`1e55eb8f5a20c11c1cd4a17010b6fa6cd4332e99`, pushed on `work/initial-reference`.
Acceptance is `25a0e61`; code/evidence checkpoint `4273ff4` is unchanged.
Documentation-only commit `96ad7fb` records the meeting pause.
Only four backend modules changed: scalar Int32 Out/InOut cells now reach
generated C++ and the depth-one vendor interface, and Int shifts accept canonical
signed Index counts. The original rejected shift source and expectations now
pass as regression evidence; they are not a fresh acceptance program.

Eleven development projects and 28 cases separately match independent expected
results in reference execution, native C++ and the exact saved wrapper/testbench
compiled locally with `-O2`, `-DNDEBUG` and UBSan. A separate directional-follower
composition, authored after freeze, passed its first four-case execution unchanged.
The prepared total is **12 projects and 32 cases**. Both complete source and
isolated-wheel suites pass **1,329 tests**. All 110 production files, 287 execution
files and 80 installed modules match their manifests. Compiler `PROJECT_STATE.md`
and the linked evidence own exact acceptance records and 133 saved artifact files.

At that checkpoint the vendor stages were pending; the completed 22 October run
above adds those results. Keep fault order, initialization, aliases and earlier
writes intact in the next increment. Reg, Reduce/Fold, public check/prepare, real
resumption, the full initial goal, checked target planning and board/AXI
integration remain open.

**21 October vendor HLS — preceding hardware checkpoint:**
[[2026-10-21-vitis-rtl-checkpoint]] records four Python-generated kernels and nine
cases passing native C++, Vitis C simulation, synthesis and Verilog RTL
co-simulation. Production freeze `da4d35f` adds a thin data/mask/status interface
and self-checking testbench; the semantic core and C++ emitter are unchanged.
Acceptance is recorded at `0ac7c00`. The meeting's main example is the Lab 1
tiled-scale program: 32 Int32 values, two tiles of 16, scale 2, input `0…31`
producing `0,2,…,62`, plus a separate overflow case. Python reference execution
and native C++ separately matched independent expected results before vendor
validation. This older pass does not cover the newer scalar/shift extension.
The fresh pair-ordering program passed without repair. The first independent
candidate exposed unsupported normalized Int/Index shift counts and was retained
as negative evidence for that freeze. Read compiler `PROJECT_STATE.md` and linked evidence for
full-suite counts, exact settings, reports, acceptance and publication.

At that checkpoint, the next target increment was general shift-count lowering,
followed by measured banking/pipelining work with end-to-end fault/memory checks.
The IP profile is sequential; board/AXI integration, routed timing and full REP-S6
remain open. The original reference/public-workflow obligations are unchanged.
David subsequently reported stopping the HLS instance; the 22 October host
instruction later authorized the saved scalar batch. Private connection/lifecycle
information stays in the ignored infrastructure note.


**21 October generated C++ — preceding implementation:**
[[2026-10-21-generated-cpp-checkpoint]] records David's subsequent request to
start target work, prioritizing C++ functional correctness before hardware
simulation. The mapping audit and direct structured backend are implemented at
production freeze `348d15a`. Lab 1 and a helper/partial-tile program compile and
run natively against independent expectations. Read the linked compiler evidence
and `PROJECT_STATE.md` for acceptance results and exact next steps. Prepare a
scoped vendor project/testbench next; do not reopen the full-language prerequisite.
The first native ABI rejects aliased external ports; local aliases retain their
snapshot behavior. This is not yet a checked target plan or vendor evidence.

**21 October scaling discussion — preceding direction:**
[[2026-10-21-hls-feasibility-checkpoint]] records David's agreement and the source
review. Keep the frontend, immutable typed records, checker and reference engine.
Before further broad language expansion, audit hardware mapping and cost for the
existing tiled-memory example and a harder composition, then define an early,
operation-based lowering experiment. Correct reference results do not yet establish
synthesizability or useful hardware performance. Public check/prepare, resumption
and the original acceptance obligations remain pending. This documentation
checkpoint adds no compiler behavior and does not start the HLS instance.

**21 October meeting refresh — historical:** [[2026-10-21-python-progress-presentation]] owns
the seven-slide story, full verbal scripts and bounded verification record. The
site deck leads with working reference execution, includes the existing full
Excalidraw map, and displays recorded ordinary/overflow Lab 1 results. The
professor brief, Python index and architecture page now reflect the current
implementation. Both demonstrations and the accepted independent composition
passed today at compiler HEAD `0c79140`; all 75 production and 268 execution
manifest entries match. The complete 1,244-per-route suites remain dated
18 October. No compiler changes were made; public checking/preparation was the
next task before the scaling discussion above. The Lab 1 historical record differs only in its
semantic-revision metadata; fresh records preserve today's value.

**19 October closeout:** all implementation work to date is committed. The
[workspace closeout](https://github.com/davidydu/spatial-py/blob/b04fdc3/docs/reviews/2026-10-19-workspace-closeout.md)
records the repository audit, cleanup and restart checklist. All frozen code/test
hashes still match the accepted checkpoint; 25 focused tests and the saved demo
output were rechecked after removing generated package files. Compiler behavior
was unchanged. At that closeout, the next task was public checking and input
preparation. Use the 21 October discussion above and the compiler's
`PROJECT_STATE.md` for the current order.

Previous public-source execution checkpoint: **`spatial-py@8152d4e`**, verified on 18 October
with **1244 source tests and 1244 isolated installed-wheel tests**, CPython 3.14.5.

**A Python program can now be captured once and specialized for different settings.**
The public workflow is SourceUnit → CaptureBundle → capture → immutable Template
→ specialize. Capture validates retained syntax and bindings without requiring
compile-time values. Specialization rederives the same source and produces the
ordinary unchecked records used by the existing checker. It does not execute
Python source or let a template bypass checking.

The [public workflow example](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/run_public_source.py) specializes
one [source program](https://github.com/davidydu/spatial-py/blob/8152d4e/examples/kernels/public_source.py) twice:
`[3,7,11]` with bias `-2` produces `[1,5,9]`; `[3,7]` with bias `4` produces
`[7,11]`. The runs allocate and release 3/2 fresh scratch scopes. Both literal
outputs, ordered effects and unchanged host buffers are checked. See
[recorded outputs](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/public-source-reference-output.json),
[evidence](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source.md),
[review](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/reviews/2026-10-18-public-source.md) and the
[fresh composition](https://github.com/davidydu/spatial-py/blob/8152d4e/docs/evidence/task-03c-public-source-acceptance-second.md).

Capture and specialization are public; checking, preparation and simulation in
this demo still use the private reference bridge. One core-only module is
supported. Larger dependency bundles reject explicitly after aggregate source
admission. The installed prelude is a frozen registration manifest, not a proof
of compiler correctness. The existing checker and runtime are unchanged.

Independent specification and quality reviews and parent replay passed. Review
repairs preserve legacy metadata-error order and expected Unicode/resource-limit
diagnostics. A separate fresh composition followed an observer-only correction in the first
case; that earlier case remains regression evidence. Complete source
and wheel suites pass in 151.331s and 151.417s; all
74 packaged modules and both manifests match. These timings are verification
observations, not performance benchmarks. Full initial-goal, lab and HLS coverage
remain open.

The actual Lab 1 tiled DRAM/SRAM source completes both independent output vectors through shared
normalization, checked publication, strict host preparation and the generic
reference runner. Seven demands are proved and four enforced by ordered guards.
The [execution evidence](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/task-05a-reference-execution.md)
records exact scope, source/test hashes, review findings, timings and a fresh
post-freeze composition. The [runnable demo](https://github.com/davidydu/spatial-py/blob/d2460e3/examples/run_lab1_reference.py)
prints the [recorded outputs](https://github.com/davidydu/spatial-py/blob/d2460e3/docs/evidence/lab1-reference-output.json).

This is reference execution, not HLS or full initial-goal completion. Independent
cases cover aliases, signed/rank-2 views, lazy faults, snapshot copies, fresh local
lifetimes and precise committed prefixes. Private ResourceLimit results have no
continuation; do not describe them as resumable simulation.

Ordinary statement branches now pass the original conditional-fault and rank-2
recurrence sources, including full ordered control/memory traces. Separate arm
scopes share canonical arguments without granting missing lexical captures.
A fresh descending-window/alias composition passed three independent scenarios.
The selected-entry preparation repair and 811-test frozen package results are
in [branch evidence](https://github.com/davidydu/spatial-py/blob/10cc1be/docs/evidence/task-05b-statement-branches.md).
The first execution-only checkpoint was `d2460e3` (773 tests per route).

This is the tiled-scale part of Lab 1. Its Reg, FIFO and Reduce/Fold families
remain required. After the current general memory/helper and initial-contract
work, use those gaps, Lab 2 memory reductions/FSM/LUT/fixed-point tiles, and Lab 3
line/shift buffers and convolution to drive language expansion.

Top-level scalar/borrowed helpers now run through explicit CALL with fresh
frame-local bindings, per-call entry checks and cleanup before return. Original
DEV-TILE-TAIL gives `[5,-7,-2147483645,3,1]` (or empty output at n=0);
DEV-LOCAL-BORROW gives `37` after six calls. Both source and independently written
common records match their complete literal traces. The
[helper demo](https://github.com/davidydu/spatial-py/blob/aecacc0/examples/run_helpers_reference.py) and
[recorded results](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/helper-reference-output.json)
are repeatable. [Helper evidence](https://github.com/davidydu/spatial-py/blob/aecacc0/docs/evidence/task-05c-helper-execution.md)
records the reproduced ordered-call token repair, fresh post-freeze alias/return
composition, unchanged 176-file snapshot and both 870-test results.

Nested scalar/Unit helpers now capture immutable values, SRAM/DRAM handles,
Out/InOut cells and other lexical helpers through the existing source/common/CALL
route. Captures preserve aliases, hidden dimensions, exact call bindings and
local cleanup. The [capture demo](https://github.com/davidydu/spatial-py/blob/1260959/examples/run_captures_reference.py)
and [recorded results](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/capture-reference-output.json)
are repeatable. [Capture evidence](https://github.com/davidydu/spatial-py/blob/1260959/docs/evidence/task-05d-lexical-captures.md)
records independent source/common traces, the proportional-work review repair,
fresh first-pass acceptance, and both 938-test results on unchanged 192-file and
65-file manifests. An earlier composition's Unit observation-adapter repair is
retained as a regression, separately from final fresh acceptance.

**Helpers can now return memory windows that the caller keeps using.**
A returned view can be assigned to a named local, passed to another helper,
selected conditionally, read/written or used in a transfer. The chosen storage
and coordinates survive helper cleanup. Returning temporary helper-local memory
rejects, including an inactive return alternative. This lets ordinary tile/window
programs be split into reusable helpers through the shared compiler route.

See the [runnable demo](https://github.com/davidydu/spatial-py/blob/813718f/examples/run_borrowed_views_reference.py),
[Python source](https://github.com/davidydu/spatial-py/blob/813718f/examples/kernels/selected_views.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/borrowed-views-reference-output.json),
[review](https://github.com/davidydu/spatial-py/blob/813718f/docs/reviews/2026-10-17-borrowed-result-execution.md) and
[execution evidence](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/task-05e-borrowed-results.md).
The demo checks five separate/aliased and nested-helper scenarios. Independent
source/common programs agree on full traces; all eight original borrowed-result
groups now have execution or rejection evidence. Reviews repaired conditional
shape handling, two context-free selection gaps and an older explicit-slice
regression before the final production freeze.
A [separately authored composition](https://github.com/davidydu/spatial-py/blob/813718f/docs/evidence/task-05e-borrowed-acceptance-composition.md)
records its literal expectations and first-run results. Both complete package
routes pass **1019 tests** on unchanged frozen files.

Pure tokenless forwarding still rejects when its entry checks cannot be proved;
ordered helpers retain the existing runtime checks. This is a documented boundary,
not a claim that all helper compositions or the initial compiler are complete.

**Compile-time constants and type aliases now work in executable programs.**
Module constants may refer to later constants; local constants follow lexical
scope. Nested helpers can use them for memory sizes, signatures and calculations
without extra runtime arguments. Closed Int/Index/Bool/Unit aliases also support
conditional type selection. A tiled example combines these features with
captured memory and returned views; its ordinary output is `[1,3,6,11,19,32]`,
and a separate signed-overflow vector also passes.

See the [source](https://github.com/davidydu/spatial-py/blob/316cb7c/examples/kernels/constant_tiles.py),
[runnable demo](https://github.com/davidydu/spatial-py/blob/316cb7c/examples/run_constants_reference.py),
[recorded results](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/constants-reference-output.json),
[execution evidence](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/task-05f-constants.md),
[review](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/reviews/2026-10-17-constants.md) and
[fresh composition](https://github.com/davidydu/spatial-py/blob/316cb7c/docs/evidence/task-05f-constants-acceptance-third.md).
Independent specification and quality reviews passed after scope and source/common
parity repairs. An earlier composition used a possibly failing conversion in a
pure helper; its annotation-only repair is retained as regression. A second
case required a test-observer correction and is also regression evidence; a
third independent author supplied fresh acceptance. **1079 source tests and
1079 isolated-wheel tests pass** on unchanged frozen files. The existing canonical verifier and runtime were not expanded.

Pending language work after the meeting and target checkpoint: expose public checking and input preparation using the existing shared
checker and host preparation. Keep the execution bridge private until simulation
supports validated continuations and cumulative budgets without replaying effects.
Dependency linking and the remaining original acceptance obligations stay open;
then continue reusable Lab 1 register/queue/reduction families and Labs 2–3.
No new verifier framework or HLS instance is needed for this increment.

**18 October scope correction:** the previous memory/view-alias recommendation
misread the pinned contract. [[10 - Source Checker and IR Blueprint#Type-valued source constants]]
explicitly limits Const[Type] to value descriptors and excludes memory resources
and ports. Existing rejection behavior is correct. The
[review and correction](https://github.com/davidydu/spatial-py/blob/1585268/docs/reviews/2026-10-18-alias-scope-correction.md)
records the evidence; no memory-alias language extension is being implemented.

True resumable budgets, artifact agreement, verified
editing and final whole-goal acceptance remain required. Current private
resource-limit results have no continuation. Those reference obligations do not
require HLS tools.

Continued local implementation was authorized before the October 22 meeting
pause. That pause is now the current instruction; wait for David to resume work.
Ask separately before HLS reuse.

David stopped the instance after the 21 October vendor validation and asked to be
consulted when it is needed again. The next generated source and self-checking
testbench are saved; keep the host stopped during the meeting pause. When David
resumes the work, ask before vendor simulation/synthesis; confirm the installed toolchain, target
device and clock on the next authorized run. Public workflow work does not need HLS.

The compiler's tracked
[PROJECT_STATE.md](https://github.com/davidydu/spatial-py/blob/work/initial-reference/PROJECT_STATE.md)
owns the exact active task, reproduction commands and latest deployment record.
Follow its [execution plan](https://github.com/davidydu/spatial-py/blob/work/initial-reference/docs/plans/2026-10-13-reference-execution.md).
Local continuation is paused for the meeting; ask before HLS reuse. Check the worktree before editing because another
harness may have advanced beyond this publication. [[80 - Initial Compiler Goal]]
is the published big-picture status; older diagrams and slides can lag actual
compiler evidence.

## Documentation and presentation delivery

The [research site](https://davidydu.github.io/spatial-research-site/) builds from
this vault. The current [Python presentation](https://davidydu.github.io/spatial-research-site/presentation/python/)
lives in the site's `presentation/python/` directory. The deck at `/presentation/`
is the historical Rust-era proposal. The editable diagram and original exports
live under `50 - Python Rewrite/30 - Implementation Design/assets/`; the site
has presentation copies. Keep copies consistent when changing the map.

The October 22 presentation and [[2026-10-22-python-pipeline-presentation|speaker notes]]
follow seven steps: direction, architecture, one Lab 1 pipeline result,
reusable compiler rules, evidence boundaries and lessons, next steps, then records
and discussion. The full map remains a proposed design. Presentation changes do
not require compiler replays or a new HLS run during the pause.

From the site repository, build against the actual research checkout:

```sh
npm run build:site -- --directory '/Users/david/Documents/Spatial Research'
```

Use the Node/npm versions in the site `package.json`; install dependencies with
`npm ci` when needed. Follow the site README for previews and the publication
workflow. A docs-only Quartz rebuild can remove the presentation from generated
`public/`; `build:site` restores the combined output. Never edit generated output
or a build-time `content/` clone as the source of truth.

Publish in order: implementation checkpoint, research notes, then the site.
Research pushes alone do not immediately deploy the separate site. After the
research push completes, push site changes or dispatch its existing workflow:

```sh
gh workflow run deploy.yml --repo davidydu/spatial-research-site --ref main
```

Use the returned run URL/ID, or locate the newly dispatched run with `gh run list`
and verify its branch/commit, then wait for completion. Check changed live pages
for HTTP 200 and new content markers. A successful build or an old deployed page is
not proof that local changes were published. Validate internal links and anchors;
for presentation changes also inspect layouts, navigation, notes and map controls.

## Keep this context shared

Before ending a checkpoint, record the decision, correction, test evidence,
remaining gates, exact next task and any blocker in the owning tracked files.
Update compiler `PROJECT_STATE.md` for implementation state; update this map for
cross-project workflow/preferences; append dated results to [[progress-log]].
Keep `AGENTS.md` and `CLAUDE.md` as short entry pointers instead of parallel memory
stores. Preserve earlier evidence and mark stale resume documents as historical.

Temporary probe logs and old agent sessions may help an investigation, but
required expectations belong in tracked tests/evidence. Do not copy credentials,
unrelated personal memory or raw private transcripts into these repositories.
Model-specific skills are optional: planning, independent review, meaningful
red/green checks and verification can all be performed from these shared files.
