---
layout: post
title: "Project kickoff: choosing the simulation boundary"
date: 2026-07-27 00:00:00 +0900
categories: progress
milestone: phase-0
record_type: decision
---

## Objective

Define a project small enough to finish while still exercising an NPU
compiler, runtime, device ABI, simulator, and RISC-V integration.

## Context and assumptions

The initial idea was to extend Spike with an NPU and place a software stack on
top. Inspection of Spike's source and documentation suggested that its
extension and internal abstract-device interfaces are plausible integration
points. This is a design inference, not a proven stable plug-in API; the exact
pinned revision and guest-memory path remain an E5 experiment.

Spike is a functional ISA simulator, so it cannot establish cycle-accurate NPU
or SoC performance. That boundary shapes the project.

## Decision

The first NPU will be a memory-mapped accelerator attached to an RV64 host in
Spike. A portable C++ NPU model will also execute without Spike.

An MMIO design was chosen before custom instructions because it exposes:

- Command submission
- DMA and address handling
- Busy, completion, timeout, reset, and error states
- Polling and later interrupts
- A programming model transferable to QEMU, RTL, or real hardware

## Scope correction

The first milestone will not begin with full ONNX support or Linux. It will use
a tiny JSON graph, a bare-metal runtime, INT8 GEMM, and a two-layer MLP.

ONNX import, convolution, timing exploration, RTL, and Linux are gated later
phases.

## Review outcome

The highest risks are:

1. Numerical rules that are not defined precisely
2. Accidental dependence of the core model on Spike internals
3. Guest-memory access from the Spike MMIO plug-in
4. Presenting analytical estimates as cycle-accurate results
5. Expanding the workload before the first end-to-end path is stable

The implementation plan now includes explicit gates for all five.

## Next step

Create the reproducible Phase 0 toolchain and run an RV64 hello-world ELF under
a pinned Spike revision.

## References

- [Spike source and API warning](https://github.com/riscv-software-src/riscv-isa-sim)
- [Spike extension interface](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/extension.h)
- [Spike abstract device interface](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/abstract_device.h)
