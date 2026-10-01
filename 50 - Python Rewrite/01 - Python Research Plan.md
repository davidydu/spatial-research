---
type: plan
title: "Python Spatial research plan"
scope: "Programming model, semantics, compiler design, and later HLS research"
project: spatial-python
date: 2026-09-30
status: active
---

## Objective and boundaries

Produce a source-grounded, reviewable design for pure Python Spatial before implementing the compiler. Begin with programs people can read and explain. Use those programs to expose semantic and compiler-design choices; investigate HLS after the programming model is sufficiently clear.

The current unattended research mandate is tracked in [[03 - Managed Research Execution]], including the complete deliverables, review sequence, and completion audit. David assigned the main agent to manage the work and specified GPT-6.1 Sol at extra-high reasoning for Codex subagents.

The settled direction is [[D-27]]. Assume adequate implementation and maintenance capability. Do not repeat Rust-versus-Python selection merely because Rust offers stronger implementation-language checks. Capability does not replace correctness evidence or performance measurements.

## Why this documentation structure

Keep a dedicated `50 - Python Rewrite/` section, linked to the existing evidence. Extending the original specification in place would mix descriptions of Scala Spatial with proposals for the new language. Extending only `35 - Python Surface Mapping/` would put compiler architecture and validation inside a folder scoped to an earlier surface comparison. A separate repository would fragment the shared source and research trail without a current need.

This is a documentation organization choice, not a decision about compiler modules. Existing files are retained in place. Do not copy a source fact into several competing specifications; link to its evidence and state the Python decision once.

## Study order

| Phase | Question | Deliverable and completion criterion |
|---|---|---|
| 1. Programming model | What does a Spatial program look like in Python? | Three comparable source-capture and builder examples, with capture-time/runtime behavior, limitations, and a supported recommendation |
| 2. Semantic contract | What exactly do those programs mean? | Explicit rules for numbers, names, memory, effects, controllers, and errors; each inherited rule traced to original Spatial or identified as a redesign |
| 3. Compiler design | How does Python represent and check that meaning? | Candidate program representations, checking stages, source diagnostics, and simulation strategy; alternatives compared on the same cases |
| 4. HLS research | How can the chosen operations lower to HLS? | Per-construct mapping, behavior to preserve, unsupported cases, and a staged validation design |
| 5. Implementation planning | What is the smallest approved end-to-end slice? | A plan derived from reviewed decisions and specifications, with concrete acceptance cases and clearly bounded claims |

Phases are research order, not a requirement to finish a whole simulator before discussing HLS. Record hardware-related questions early, but avoid choosing syntax solely to fit an emitter before its meaning is clear. Production implementation begins only after review of the relevant design; neither this plan nor the Python-language decision approves a full architecture.

## First research wave

[[PY-R001 - Programming Model Study]] defines the first comparison. [[PY-E001 - Initial Example Corpus]] fixes the starting programs and known evidence. Cover tiled scale, scalar reduction, and a runtime branch with FIFO state.

Use Codex agents for bounded, independent source checks, candidate designs, and adversarial review. Give each writer a distinct file or task. The integrating agent reopens the sources behind the claims that determine a decision and resolves disagreements in the study note. Do not treat votes or number of agents as proof.

Complete one useful comparison before expanding to GEMM or the full language inventory. The initial corpus is deliberately small; it does not establish coverage of every Spatial construct.

## Notes before specification

For each topic:

1. Open a research question with a stable `PY-Q` identifier.
2. Read the original source and relevant historical evidence; write a dated `PY-R` study before a specification.
3. Compare alternatives against the same example semantics. Preserve failed cases and contrary evidence.
4. Record a proposed conclusion with its limits in the next shared `D-NN` decision, with `scope: python-rewrite`. Update adoption status only when authority is explicit; preserve the proposal history.
5. Distill the recommended behavior into `40 - Specification/`, linking both the decision proposal and the evidence, with `adoption_status: proposed`. After explicit adoption, update that field and its authority record. Record unresolved details explicitly; a review contract is not implementation approval.
6. Define validation cases and expected behavior before compiler implementation. Add observed results only after execution.
7. Update the index, affected questions, and [[progress-log]]. Commit coherent batches and publish the same files through the existing website.

Research prototypes, if useful later, must be isolated, reproducible experiments with a stated question. They are not silently promoted to production code. No experiment or compiler scaffold is introduced by this organizational work.

## Evidence and status

Distinguish four things in every study: behavior observed in the original source, choices made in the Rust rewrite, proposed Python behavior, and results from actual executions. Cite the source revision and lines for code claims. A calculated expected output is not a successful compiler run.

Keep review status separate from adoption and implementation status. `reviewed` means the document's claims have been checked; it does not mean the API is adopted or the feature works. An adopted decision is not an implementation result. For future Python specifications, include `scope: python-rewrite`, links to the deciding records, and separate `adoption_status` and `implementation_status` fields.

Identifiers are stable and never reused: `PY-R001` for studies, `PY-E001` for example collections, and `PY-Q001` for questions. Decisions continue the shared `D-NN` sequence beginning with [[D-27]]; do not create a second decision registry. New study/example filenames include their ID and topic so their stems remain unique across the vault. Split a collection only when its size justifies separate pages, keeping the original index and links.

## Review and checks

Follow [[00 - Python Validation Plan]]. Check changed frontmatter, citations, links, status claims, and the site build. Use files, source retrieval, and command-line checks by default. Browser UI is reserved for a requested visual task or a visual defect.

Use the existing `davidydu` research repository for documentation commits. The site repository owns presentation and publishing code; do not duplicate the research there. Publish the vault first, then rebuild the website, and distinguish a pushed commit from a successful deployment.
