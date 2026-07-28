---
layout: page
title: "Lesson 3: Commands, Memory, and the Native Device"
permalink: /lessons/03-commands-memory/
---

# Lesson 3: commands, memory, and the native device

## Outcome

Encode one ABI 1.0 command buffer, validate it without executing it, and run it
through the portable native device model before adding a graph compiler or
Spike.

Use the [command ABI](../command-abi.md) and
[memory and execution model](../memory-execution-model.md) as the immediate
authorities. The native state names stay aligned with the later
[MMIO/runtime contract](../mmio-runtime.md), but Lesson 5 implements the MMIO
adapter and RV64 submission sequence. This lesson explains an implementation
sequence; it does not redefine fields or error precedence.

## Step 1 — Encode and decode exact bytes

Implement explicit little-endian readers and writers for:

- the command-buffer header;
- every ABI 1.0 record;
- checked offsets and record lengths;
- reserved-zero fields;
- exact version and opcode rejection.

Do not copy native structures into the buffer. Add one golden valid buffer and
one named mutation for every structural rejection rule.

## Step 2 — Separate structural and semantic validation

The first pass proves that the counted records are well formed and end exactly
at `total_bytes`. The second pass proves dimensions, strides, alignments,
ranges, initialization, and prohibited overlap.

Both passes consume the immutable command snapshot. Neither pass mutates guest
memory, scratchpad bytes, counters, or status-visible results.

## Step 3 — Implement checked memory adapters

Provide one guest-memory adapter for the native runner. Every read or write:

1. checks address-plus-length arithmetic before adding;
2. either transfers the complete range or fails;
3. never treats a guest address as a host pointer;
4. stages a destination before committing it.

Model the 65,536-byte scratchpad and its byte-level initialization state
separately from guest memory.

## Step 4 — Execute a hand-built submission

Use a small command stream:

```text
DMA_LOAD A/B/bias
-> GEMM
-> ADD_BIAS
-> RELU
-> REQUANTIZE
-> DMA_STORE
-> END
```

The native device must expose the same state transitions, error code, failing
command index, command count, memory effects, and counters later observed
through MMIO. It must not contain graph parsing or compiler policy.

## Step 5 — Prove failure boundaries

Test separately:

- validation failure before any command executes;
- execution failure after earlier commands complete;
- no partial destination write by the failing command;
- timeout handling outside the device model;
- explicit reset after `COMPLETE` or `ERROR`;
- deterministic replay from reset.

## Correctness gate

- Python and C++ encode/decode fixtures agree byte for byte.
- Malformed buffers return the same stable error code and command index.
- Native execution matches the numerical reference exactly.
- Guest and scratchpad bounds are checked before access.
- A failed command never commits a partial destination.
- Reset restores every documented architectural default.

## Why this precedes the compiler

A compiler should emit into an independently testable interface. Building the
decoder, validator, memory model, and native executor first prevents compiler
bugs from being confused with device-contract bugs. The next lesson can then
produce commands for a device path that already accepts hand-built fixtures.
