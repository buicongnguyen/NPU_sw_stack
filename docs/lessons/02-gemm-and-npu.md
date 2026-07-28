---
layout: page
title: "Lesson 2: GEMM and the NPU Core"
permalink: /lessons/02-gemm-and-npu/
---

# Lesson 2: GEMM and the NPU core

## Outcome

Build a tiled INT8 GEMM and understand how an 8x8 systolic array, scratchpad,
and DMA model change performance.

## Step 1 — Start with a clear GEMM

Compute:

```text
C[M,N] = A[M,K] * B[K,N] + bias[N]
```

Implement the simple `M-N-K` loop first. It is the correctness reference, not
the optimized kernel.

## Step 2 — Measure data movement

Count:

- Elements read from A
- Elements read from B
- Accumulator reads and writes
- Final output writes
- MAC operations

Compare loop orders. The arithmetic result is unchanged, but reuse and traffic
are not.

## Step 3 — Add tiling

Introduce explicit tile sizes:

```text
TM, TN, TK
```

Each tile must fit its A, B, and accumulator regions. The allocator must reject
invalid configurations rather than silently spilling.

Test non-multiple shapes such as:

```text
M=13, N=19, K=27
```

Edge tiles reveal padding, mask, and bounds errors.

## Step 4 — Model the systolic array

For an 8x8 array, trace:

- Which A and B values enter each cycle
- When each processing element performs a MAC
- Pipeline fill
- Steady state
- Pipeline drain
- Partial-array utilization

For a single ideal tile, a useful starting latency relationship is based on K
plus spatial fill/drain terms. It must be derived and tested rather than
treated as a universal performance formula.

## Step 5 — Add scratchpad and DMA

Model separately:

- DMA setup latency
- Read and write bandwidth
- Scratchpad capacity
- Scratchpad banks
- Compute cycles
- Stall cycles

Start with serialized DMA and compute. Add double buffering only after the
single-buffer trace is correct.

## Step 6 — Export trace and counters

Recommended JSON fields:

```json
{
  "array_rows": 8,
  "array_cols": 8,
  "tile_m": 8,
  "tile_n": 8,
  "tile_k": 32,
  "macs": 0,
  "estimated_cycles": 0,
  "array_utilization": 0.0,
  "dram_read_bytes": 0,
  "dram_write_bytes": 0,
  "stall_cycles": 0
}
```

The tool that generates these fields must record its Git revision.

## Correctness gate

- Untiled and tiled GEMM agree exactly.
- Partial tiles are tested.
- Every out-of-bounds access is rejected.
- Counters have independent hand-calculated tests.
- Functional output does not depend on timing-model settings.

## Experiments

- Array: 4x4, 8x8, 16x16
- Small versus large M/N/K
- Scratchpad: 16–256 KiB
- Bandwidth sweep
- Single versus double buffering
- Weight-stationary versus output-stationary

For each plot, explain the knee or plateau rather than only showing it.

## Primary references

- [Gemmini](https://github.com/ucb-bar/gemmini)
- [Timeloop/Accelergy](https://timeloop.csail.mit.edu/)
- [NVDLA primer](https://nvdla.org/primer.html)
