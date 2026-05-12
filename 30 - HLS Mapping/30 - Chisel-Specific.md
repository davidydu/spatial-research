---
type: hls-mapping-index
project: spatial-spec
date_started: 2026-04-23
date_updated: 2026-04-25
---

# HLS Mapping - Chisel-Specific

Constructs tied to Chisel, RTL elaboration, or Spatial hardware templates that need redesign for HLS.

Each line is generated from spec-entry `hls_status` frontmatter. Entries marked `unknown` are included with a suggested classification rather than modifying the source spec.

[[70 - Timing Model]] — Explicit RTL delay and cycle-alignment machinery has no direct HLS equivalent and needs architectural redesign.
[[C0 - Retiming]] — Explicit RTL delay and cycle-alignment machinery has no direct HLS equivalent and needs architectural redesign.
[[10 - Overview]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[20 - Types and Ports]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[30 - Memory Emission]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[40 - Controller Emission]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[50 - Streams and DRAM]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[60 - Math and Primitives]] — Emits Chisel/RTL structures directly; an HLS backend needs C++ emission and scheduling instead.
[[10 - Pirgen]] — Backend-specific PIR path does not transfer directly to an HLS C++ generator.
[[10 - Fringe Architecture]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
[[20 - DRAM Arbiter and AXI]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
[[30 - Ledger and Kernel]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
[[40 - Hardware Templates]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
[[50 - BigIP and Arithmetic]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
[[60 - Instantiation]] — Current design is Chisel shell, AXI, template, or IP plumbing; HLS should use tool pragmas and a redesigned host/fringe boundary.
