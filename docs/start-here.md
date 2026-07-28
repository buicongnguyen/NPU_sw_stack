---
layout: page
title: Start Here
permalink: /start-here/
---

# Start here

This is the reading and execution order for the project. The current stage is
**documentation-first**: understand and review the design now, then perform the
environment setup and implementation later.

The project asks one concrete question:

> How does a neural-network graph become deterministic work submitted by a
> RISC-V program to a small, simulated NPU?

The answer is built in layers. Spike runs the RISC-V host software. A separate
NPU model implements DMA, scratchpad storage, matrix multiplication, activation
functions, and counters. A small compiler turns supported graph operations into
a versioned command buffer.

## What this project is—and is not

This project is:

- A learning implementation of an NPU software/hardware boundary
- A bit-exact functional simulator before it is a performance simulator
- A small compiler, runtime, device model, and workload suite
- A public lab notebook with reproducible evidence

This project is not:

- A claim that Spike itself models an NPU
- A complete production inference framework
- A cycle-accurate system model in the first release
- A full YOLO or LLM accelerator on the first day
- A reason to implement every ONNX operator

## The four simulation levels

Keep these levels separate in both code and documentation:

| Level | Question answered | Proposed tool |
|---|---|---|
| Numerical reference | Are values mathematically correct? | NumPy/Python |
| Functional NPU | Are commands, memory effects, and errors correct? | Portable C++ model |
| Host/device integration | Can RV64 software submit the same work? | Spike plus MMIO adapter |
| Timing/RTL | Are cycle and utilization estimates credible? | Analytical counters, then Verilator |

A result from one level must not be presented as evidence for another. For
example, Spike can prove the driver and MMIO protocol, but it does not prove
NPU cycle counts.

## Recommended reading order

Read these pages before installing anything:

1. [Specification map](specification-status.md) — what
   is authoritative, frozen, and deferred.
2. [Architecture walkthrough](architecture.md) — the
   complete graph-to-device path.
3. [Numerical contract](numerical-contract.md) — exact
   INT8/INT32 behavior.
4. [Command-buffer ABI](command-abi.md) — exact bytes.
5. [Memory and execution model](memory-execution-model.md)
   — address spaces, ordering, atomicity, and recovery.
6. [MMIO/runtime contract](mmio-runtime.md) — registers,
   state transitions, fences, and errors.
7. [Tiny compiler design](compiler-design.md) — graph,
   passes, allocation, scheduling, and artifacts.
8. [Verification plan](verification-plan.md) — the
   evidence required before implementation claims are accepted.
9. [Reviewed implementation plan](plan.md) and
   [logic review](logic-review.md) — scope and rationale.
10. [YOLO target decision](yolo-target.md) — the first
    application destination.

The [learning path](learning-path.md) expands this into
lessons. Transformer and deformable-convolution pages are later independent
research tracks, and the
[publishing workflow](publishing.md) explains how to
turn verified gates into progress posts.

When ready to implement:

1. [Set up WSL2 and Linux tools](setup-wsl.md)
2. Follow [the executable milestone plan](execution-plan.md)
3. Work through [the lessons](learning-path.md) in order
4. Publish one progress entry at every green gate

## Workload decision

The project deliberately uses three workload sizes:

| Workload | Purpose | When |
|---|---|---|
| Scalar ops and tiny matrices | Define exact arithmetic and expose bugs | First |
| Two-layer MLP and tiny CNN | Prove the full compiler/runtime/device path | Middle |
| Fixed-shape YOLOv8n | Demonstrate a useful application | First application goal |

YOLOv8n is therefore the first application destination, not the first test.
Trying it before the smaller gates would mix compiler, quantization, memory,
runtime, and model bugs into one failure.

YOLO26n is a comparison after YOLOv8n. It is newer, but adds architectural
differences that would distract from first bring-up. The target is frozen to
YOLOv8n detection, batch 1, NCHW, 320x320, with raw detection-head tensors
leaving the NPU and host-side decode/NMS initially.

## Why Transformers and deformable convolution remain in scope

They test limitations that ordinary CNN layers do not expose:

- A Transformer decoder adds reductions, normalization, Softmax, RoPE,
  mixed precision, KV-cache traffic, and low-utilization matrix-vector work.
- Deformable convolution adds data-dependent addresses, fractional sampling,
  bilinear interpolation, and irregular gathers.

They are independent research branches after the common matrix,
compiler, and runtime foundation. Neither branch blocks the first YOLO result.

## One learning session

Use this loop for each lesson:

```text
read the operator and architecture references
-> state one falsifiable hypothesis
-> implement one bounded change
-> run a focused correctness test
-> save raw evidence
-> interpret the result
-> update the progress article
-> run all earlier gates
```

Do not write “the result looks correct.” State how it was compared, the
tolerance or exact rule, the seed, and the first divergent tensor if it failed.

## Decision checkpoints

Pause for review at these points:

### Checkpoint A — after exact GEMM

You should be able to explain saturation, accumulation width, rounding, and
requantization. If Python and C++ disagree, do not define the command ABI yet.

### Checkpoint B — after the native command model

You should be able to inspect command bytes, scratchpad allocation, DMA bytes,
errors, and output tensors without Spike. If this path is not deterministic,
do not integrate Spike.

### Checkpoint C — after Spike integration

The native and RV64 paths must submit identical command bytes and produce the
same output hash. Only the control path should differ.

### Checkpoint D — after the tiny CNN

Every layer boundary must match the integer reference. Only then begin the
YOLO partitions.

### Checkpoint E — after YOLOv8n

Report separately:

- NPU-supported compute
- Host fallback and postprocessing
- Transfer bytes
- Quantization error
- Detection-level accuracy
- Estimated versus measured quantities

## Definition of success

The first complete release is successful when a clean checkout can:

1. Recreate the documented environment.
2. Generate a deterministic two-layer MLP workload.
3. Compile it to a documented binary command stream.
4. Run it in the native functional NPU model.
5. Submit the same bytes from RV64 software under Spike.
6. Match the reference exactly and produce stable error behavior.
7. Publish the commands, versions, outputs, and limitations.

The first application success adds a fixed-shape YOLOv8n partition with
measured host fallback. Transformer and deformable-convolution success criteria
remain separate so they cannot silently redefine the first release.

## Current status

The GitHub Pages source is the current deliverable. The architecture,
normative v1 contracts, workload choices, lesson sequence, verification plan,
and publication method are documented for reading and review. Some Phase 0 and
numerical source files exist, but the Linux toolchain and implementation gates
have intentionally not been executed. WSL setup begins only after the user
reports that the environment is ready.
