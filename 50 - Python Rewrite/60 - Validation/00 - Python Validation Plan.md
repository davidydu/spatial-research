---
type: plan
title: "Python Spatial validation plan"
scope: "Research evidence, future semantic conformance, and publication checks"
project: spatial-python
date: 2026-09-30
status: active
---

## Research checks now

Check source claims at the cited revision, not just at the current working-tree line numbers. Check both whether a range exists and whether it supports the claim. Preserve the distinction between original Spatial, earlier Rust policies, Python proposals, and execution results.

Before a design decision, review the compared forms for equivalent intended behavior, complete capture/runtime explanations, meaningful error cases, and unresolved semantic differences. A returned agent summary is a guide to evidence; the integrating reviewer independently verifies the claims that determine the result.

For the first study, [[PY-E001 - Initial Example Corpus]] records reference expectations. No Python conformance runs exist. Matching a sum alone cannot validate stateful effects; include relevant reads, writes, branches, and state transitions under a stated model.

## Specification checks before implementation

Each future Python specification must link to the adopted decision, supporting study, relevant source, and example cases. Distinguish document review, design adoption, and implementation status. Do not mark a feature implemented because its source sketch is valid Python syntax or a document was reviewed.

Record supported inputs, output/effect semantics, intended rejections, and unresolved limits. New behavior that diverges from original Spatial requires an explicit decision; compatibility with an earlier Rust contract is not sufficient justification by itself.

## Future executable validation

When implementation is authorized, check the represented program as well as final outputs. Use an independent arithmetic/reference calculation where possible, meaningful variations of accepted examples, and invalid cases that test actual semantic requirements. Do not construct a suite that only recognizes the exact three starting programs.

Measure absolute compilation and simulation times against declared workloads and latency targets. Keep setup costs, repeated runs, environments, and measurement uncertainty visible. Earlier D-26 ratios remain evidence about the old experiment and are not silently changed into new acceptance thresholds.

Later HLS work needs separate evidence for generated C++ behavior, vendor simulation, synthesis, resource fit, timing, and board execution where required. Passing one does not establish the others. No HLS support is inferred from the present documentation work.

## Documentation and publication

- Parse frontmatter and check required fields for each documented type.
- Check new wikilinks and anchors; add no ambiguous filename stems. Existing ambiguous names must not be copied into the new structure.
- Check citation bounds against pinned revisions, then separately inspect support for substantive claims.
- Check that the homepage, new index, workflow, shared decision queue, and progress log agree on the current phase.
- Confirm that the diff contains only intended paths and preserves existing historical files and results.
- Commit and push the research vault, then build and publish the website. Check generated links and HTTP content directly; use browser UI only for a requested visual task or a visual defect.

The old D-26-specific validation script does not cover this new subtree. Passing it would not validate the Python research. Begin with scoped document and build checks; add reusable validators when recurring rules justify them.
