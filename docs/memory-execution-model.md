---
layout: page
title: Memory and Execution Model
permalink: /memory-execution-model/
---

# Memory and execution model

Status: **v1 normative design; implementation unverified**

This document defines how command execution changes memory and device state.
The [command ABI](command-abi.md) defines bytes, while
the [MMIO/runtime contract](mmio-runtime.md) defines the
host-visible registers.

## Address domains

| Domain | Width | Owner | Valid use |
|---|---:|---|---|
| Guest physical memory | 64-bit byte address | Runtime/platform adapter | Command buffers, inputs, constants, outputs |
| Scratchpad | 32-bit byte offset | NPU model/compiler | Explicit DMA and compute operands |
| Host virtual memory | Implementation-defined | Native process only | Backing storage behind checked callbacks |

Serialized commands never contain a host pointer. Converting a guest physical
address to backing storage is exclusively an adapter operation.

For every range `(base, length)`, validation uses checked arithmetic:

```text
length > 0
base <= address_space_limit
length - 1 <= address_space_limit - base
last = base + length - 1
```

The implementation must not validate with an already-wrapped `base + length`.

## Guest-memory contract

Version one uses a flat, byte-addressed guest-memory view supplied by the
adapter. The adapter provides checked `read(address, length)` and
`write(address, bytes)` operations. A request either transfers the entire
range or fails; short reads and writes are errors.

The first bare-metal platform assumes:

- One RV64 software context owns the NPU.
- The runtime keeps command, input, constant, and output buffers alive until
  completion or reset.
- Software does not mutate a submitted command buffer or input range.
- Device DMA and CPU accesses are ordered using the runtime's architectural
  fences.
- Cache coherence is not claimed; a future cached platform must add explicit
  cache-maintenance rules.

The device copies and validates the complete command buffer at accepted
`START`. This snapshot prevents command bytes from changing between validation
and execution. Tensor payloads are read by DMA commands at their in-order
execution point and are not snapshotted at submission.

## Submission image

The compiler emits two binary files plus a manifest:

```text
commands.bin  serialized ABI records
memory.bin    contiguous tensor payload image
manifest.json addresses, segments, hashes, and ownership
```

The default bare-metal placement is a project decision:

```text
payload_base          = 0x0000_0000_8100_0000
command_guest_address = payload_base
data_guest_address    = align_up(payload_base + command_bytes, 4096)
maximum memory.bin    = 16 MiB
```

The command buffer is 16-byte aligned. Every tensor segment begins at a
64-byte boundary in `memory.bin`; this is stricter than the command minimum and
makes transfer accounting predictable. INT32 contents remain at least
4-byte-aligned.

`memory.bin` offset zero maps to `data_guest_address`. Commands use:

```text
tensor_guest_address = data_guest_address + tensor_image_offset
```

The native runner maps these exact guest addresses to byte arrays. The RV64
linker/runtime reserves the same range and copies or embeds the two files
without rewriting command records. A platform that cannot reserve the default
range recompiles the artifact with a different explicit `payload_base`; the
new base and hashes define a different artifact set.

The manifest records at least:

```json
{
  "format": "npu-lab-submission",
  "version": 1,
  "payload_base": 2164260864,
  "command_guest_address": 2164260864,
  "command_bytes": 48,
  "data_guest_address": 2164264960,
  "memory_bytes": 64,
  "segments": [
    {
      "tensor": "x",
      "image_offset": 0,
      "guest_address": 2164264960,
      "byte_count": 16,
      "role": "input",
      "dtype": "i8",
      "shape": [1, 16],
      "layout": "row-major"
    }
  ],
  "sha256": {
    "commands.bin": "...",
    "memory.bin": "..."
  }
}
```

The hashes and workload-specific sizes above are illustrative. Allowed segment
roles are `input`, `constant`, `output`, and `workspace`. Segments do
not overlap. Inputs may be replaced by the workload before submission;
constants are immutable for the submission; outputs and workspace are
zero-filled in the initial image. Command and tensor ranges never overlap.

## Scratchpad contract

The scratchpad contains exactly 65,536 addressable bytes after reset. Bytes
have no inherent type. Commands interpret ranges as INT8 or little-endian
INT32 only after alignment, stride, and bounds validation.

Reset fills scratchpad with zero. Software must not depend on this value for
normal execution: every compute input must be initialized by a preceding DMA
or compute command in the same submission.

The validator maintains an initialization bitmap at byte granularity:

- `DMA_LOAD` initializes its destination bytes.
- `GEMM` requires initialized A and B bytes, then initializes C bytes.
- `ADD_BIAS` requires initialized data and bias bytes and updates data.
- `RELU` requires initialized data bytes and updates data.
- `REQUANTIZE` requires initialized source bytes and initializes destination.
- `DMA_STORE` requires initialized source bytes.

Reading an uninitialized scratchpad byte is a semantic error. This makes stale
data and missing-DMA bugs deterministic rather than dependent on reset history.

## Submission and queue model

Version one has one submission slot and one in-order command stream:

```text
IDLE
  -> snapshot and validate
  -> execute command 0, 1, ... END
  -> COMPLETE or ERROR
  -> explicit RESET
  -> IDLE
```

There is no queue depth beyond the active submission, no preemption, no
priority, and no concurrent DMA/compute in the functional model. `BARRIER`
therefore has no functional effect, but remains an explicit dependency marker
for a later timing scheduler.

All structural and semantic checks that can be decided from the snapshot,
guest map, and current scratchpad capacity occur before command zero mutates
architectural state. Runtime adapter failures that arise only during an actual
DMA can still produce an execution error.

## Portable functional-model interface

The C++ core remains independent of Spike and exposes these conceptual
operations:

```text
reset()
mmio_read32(offset) -> value or access fault
mmio_write32(offset, value) -> success or access fault
step() -> idle, progressed, complete, or error
snapshot_counters()
drain_trace()
```

Guest memory is supplied through total-transfer callbacks:

```text
validate_read_range(guest_address, byte_count) -> valid or range fault
validate_write_range(guest_address, byte_count) -> valid or range fault
read(guest_address, byte_count) -> bytes or DMA fault
write(guest_address, bytes) -> success or DMA fault
```

The validation callbacks are non-mutating and check overflow, mapping,
permissions, and complete-range accessibility. The semantic prevalidation pass
uses them for every DMA. Actual transfer callbacks can still report a later
execution fault if the backing mapping changes or an injected fault occurs.

An accepted `START` snapshots and validates the buffer, then leaves the model
`BUSY`. One `step()` completes at most one whole command. The native runner
steps directly; the Spike adapter advances the model from its device tick or
poll integration. This keeps reset/timeout behavior testable without making
functional values depend on wall-clock time.

Guest-controlled failures return stable status/error values and never throw
through the adapter boundary. C++ exceptions are reserved for host allocation
failure or violated internal invariants and are converted to a fatal simulator
diagnostic outside the architectural device state.

Every completed command may append one trace record:

```json
{
  "event": "command_complete",
  "sequence": 0,
  "opcode": "DMA_LOAD",
  "scratchpad_reads": [],
  "scratchpad_writes": [[0, 16]],
  "guest_reads": [[2164264960, 16]],
  "guest_writes": [],
  "macs_delta": 0,
  "estimated_cycles_delta": 5
}
```

Trace collection is observational: enabling or disabling it cannot alter
status, memory, errors, or counters.

## Command effects

Commands execute strictly in sequence:

| Command | Reads | Writes | Counter effect |
|---|---|---|---|
| `DMA_LOAD` | Guest bytes | Scratchpad bytes | Adds to DRAM read bytes |
| `DMA_STORE` | Scratchpad bytes | Guest bytes | Adds to DRAM write bytes |
| `GEMM` | A and B scratchpad ranges | C scratchpad range | Adds `M*N*K` MACs |
| `ADD_BIAS` | Data and bias | Data | No MAC count |
| `RELU` | Data | Data | No MAC count |
| `REQUANTIZE` | INT32 source | INT8 destination | No MAC count |
| `BARRIER` | None | None | Completes as one command |
| `END` | None | None | Terminates successfully |

`COMMANDS_DONE` increments only after a command completes successfully,
including `BARRIER` and `END`. The failing command is not counted.

## Atomicity and partial effects

Validation failure is atomic: no command executes, guest output is unchanged,
scratchpad is unchanged, counters remain zero, and `COMMANDS_DONE` is zero.

Execution failure is not submission-atomic. Effects of earlier completed
commands remain visible, the failing command must not perform a partial
destination write, and later commands do not execute. Software must treat all
outputs from a failed submission as invalid and issue `RESET`.

For DMA, the adapter must stage a complete transfer before committing its
destination. For compute commands, destination elements are calculated into a
temporary buffer or otherwise committed only after all required reads and
checks succeed.

## Overlap and alias rules

Version one chooses simple, reviewable behavior:

- DMA source and destination are in different address domains and cannot
  alias.
- GEMM C may not overlap A or B; A and B may overlap each other because both
  are read-only.
- Bias storage may not overlap the in-place INT32 data range.
- ReLU is explicitly in place.
- Requantization source and destination may not overlap.
- Strided tensors are treated as the union of addressed row intervals, not as
  an unchecked dense bounding box.

The compiler may reuse a scratchpad region only when tensor lifetimes do not
intersect and no scheduled command still reads the prior value.

## Error containment and recovery

On an error:

1. The device records one stable numeric code and failing sequence number.
2. State becomes `ERROR`.
3. No later command executes.
4. The runtime reports the device error separately from a host polling timeout.
5. Results are discarded by software.
6. `RESET` clears submission configuration, errors, counters, command
   snapshot, initialization state, and scratchpad before returning to `IDLE`.

Reset during `BUSY` is an abort. The synchronous native implementation observes
it only at command boundaries; a future asynchronous model must preserve the
same rule that no command commits a partial destination.

## Security and robustness boundary

Version one is a single-owner educational device, not a multi-tenant security
boundary. It still treats the command buffer as untrusted:

- Every size, stride, offset, dimension, opcode, and reserved bit is validated.
- All multiplications and additions used for byte ranges are checked.
- Guest access occurs only through range-checked callbacks.
- Command parsing never casts serialized bytes to native structs.
- Logs do not print guest buffer contents unless an explicit trace option is
  enabled.
- Malformed-input tests and fuzzing run under memory/undefined-behavior
  sanitizers when the native environment is available.

Virtual memory translation, IOMMU isolation, process ownership, secrets, and
side-channel resistance are outside v1 scope and must not be implied.

## Timing-model separation

Functional command order is invariant. A later timing model may calculate DMA
and compute overlap, bank conflicts, stalls, and array utilization from the
same trace, but timing parameters cannot alter bytes, status, error selection,
or command completion order.

## Continue reading

Next: [MMIO and runtime contract](mmio-runtime.md)
