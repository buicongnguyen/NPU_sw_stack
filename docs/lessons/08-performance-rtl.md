---
layout: page
title: "Lesson 8: Performance and RTL"
permalink: /lessons/08-performance-rtl/
---

# Lesson 8: performance and RTL

## Outcome

Determine which analytical performance assumptions agree with a small
SystemVerilog implementation and which need correction.

## Step 1 — Freeze the analytical model

Document:

- Array dimensions
- PE pipeline behavior
- Scratchpad ports and banks
- DMA width, bandwidth, and setup latency
- Command overhead
- Arbitration assumptions
- Clock-frequency assumption

Do not tune the analytical model after seeing RTL without recording the change.

## Step 2 — Implement the smallest RTL

Order:

1. One INT8 MAC processing element
2. One row/column dataflow test
3. Small systolic array
4. Accumulator behavior
5. Scratchpad interface
6. Command controller

Use the same test vectors and numerical contract as the C++ model.

## Step 3 — Build with Verilator

The harness must support:

- Deterministic reset
- Cycle stepping
- Input/output loading
- Assertions
- Waveform generation for selected failing tests
- Counter export

## Step 4 — Correlate

For each microbenchmark, compare:

| Metric | Analytical | RTL | Difference |
|---|---:|---:|---:|
| Result tensor | hash | hash | exact/mismatch |
| Compute cycles | value | value | percent |
| Stall cycles | value | value | percent |
| MAC utilization | value | value | points |
| Bytes transferred | value | value | bytes |

Explain differences using waveforms or state traces.

## Step 5 — Run architecture sweeps

Only after correlation:

- 4x4, 8x8, and 16x16 arrays
- Scratchpad sizes
- Banking
- Bandwidth
- Tile shapes
- Double buffering

Use the analytical model for broad exploration and RTL for representative
points.

## Correctness gate

- RTL matches integer outputs exactly.
- Reset and backpressure are tested.
- Analytical-versus-RTL differences are explained.
- Estimated and RTL cycle counts have different field names.
- Reproduction commands and waveforms are linked.

## Primary references

- [Verilator overview](https://verilator.org/guide/latest/overview.html)
- [Gemmini](https://github.com/ucb-bar/gemmini)
- [Timeloop/Accelergy](https://timeloop.csail.mit.edu/)
