---
type: moc
project: spatial-spec
date_started: 2026-04-23
---

# IR — Index

The intermediate representation. Three layers:

1. **Argon framework** (`00 - Argon Framework/`) — the generic staged-IR substrate: `Exp`/`Sym`/`Ref`, `Op`/`Block`/`Effects`, `State`, staging engine, pass/traversal/transformer scaffolding, scheduler, codegen skeleton.
2. **Spatial nodes** (`10 - Spatial Nodes/`) — the per-node entries for every `spatial.node.*` op: controllers, memories, memory accesses, counters, primitives, streams, blackboxes, host, debugging.
3. **Metadata** (`20 - Metadata/`) — metadata categories attached to symbols: control, access, memory, retiming, bounds, math, params, types, blackbox.

## Upstream coverage

- [[argon-coverage]] — Argon framework
- [[spatial-ir-coverage]] — Spatial nodes + metadata
- [[forge-runtime-coverage]] — Forge macros + shared runtime (emul, utils)
