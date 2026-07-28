---
layout: page
title: "Lesson 5: Runtime and Spike"
permalink: /lessons/05-spike-runtime/
---

# Lesson 5: runtime and Spike

## Outcome

Run an RV64 bare-metal application under Spike and submit the same command
buffer already proven in the native NPU runner.

Complete the [WSL2 setup](../setup-wsl.md) first, and use
the [MMIO/runtime contract](../mmio-runtime.md) as the
language-neutral interface.

## Step 1 — Pin and build Spike

Record:

- Exact Spike Git commit
- RISC-V compiler version
- Configure/build commands
- Host environment
- Supported RV64 ISA string

Spike's internal C++ interface is not a stable public API, so upgrading it is a
reviewed change.

## Step 2 — Prove the RV64 environment

Before adding the NPU:

- Build a freestanding hello-world or semihosted test.
- Verify the linker map.
- Inspect ELF sections and disassembly.
- Run under Spike.
- Confirm deterministic exit status.

## Step 3 — Build a minimal MMIO device

The first plug-in implements:

- `VERSION`
- `STATUS`
- Scratch test register
- Reset
- Invalid offset and width behavior

Do not add DMA or GEMM until MMIO reads and writes have focused tests.

## Step 4 — Prove guest-memory access

This is an explicit risk gate:

1. RV64 writes a known command/data pattern.
2. The plug-in reads it through the chosen guest-memory interface.
3. The plug-in writes a result pattern.
4. RV64 verifies it.
5. Bounds, alignment, and inaccessible addresses are tested.

If safe general guest-memory access is impractical in the pinned Spike
revision, use a documented shared-memory aperture for version one.

## Step 5 — Implement the driver

Driver sequence:

```text
validate arguments
-> write command address and size
-> order memory before device I/O
-> ring doorbell
-> poll status with timeout
-> decode completion or error
-> order device completion before reading results
```

Only the driver accesses raw MMIO. Applications call stable runtime functions.

## Step 6 — Add the real NPU adapter

The Spike adapter translates:

- MMIO transactions
- Guest-memory reads/writes
- Reset/tick callbacks

into the portable NPU model interface. The model itself must not include Spike
headers.

## Correctness gate

- Native and Spike paths execute identical command bytes.
- Output tensors agree exactly.
- Timeouts and invalid addresses return stable error codes.
- Reset during idle and after failure is deterministic.
- Driver ordering is documented.

## What Spike proves

- RV64 application and linker correctness
- MMIO ABI correctness
- Runtime and command submission correctness
- Functional device interaction

Spike does not prove cycle-accurate CPU, bus, DMA, or NPU performance.

## Primary references

- [Spike repository and build documentation](https://github.com/riscv-software-src/riscv-isa-sim)
- [Spike MMIO device interface](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/abstract_device.h)
- [Spike device bus](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/devices.cc)
- [RISC-V memory ordering explanation](https://docs.riscv.org/reference/isa/unpriv/mm-eplan.html)
