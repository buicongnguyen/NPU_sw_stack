---
layout: page
title: Plan Logic Review
permalink: /logic-review/
---

# Plan logic review

Review date: **2026-07-28**

Verdict: **core v1 contracts reviewed; implementation remains unverified**

The user chose a documentation-first checkpoint on 2026-07-27. This review
therefore approves dependency order, scope, and test design. It does not claim
that WSL, C++, Spike, or workload gates have passed.

## Review method

The plan was checked for:

- Dependency ordering
- Testability
- Hidden circular dependencies
- Unstable external APIs
- ABI ambiguity
- Numerical ambiguity
- Performance-claim validity
- Scope growth
- Reproducibility
- Licensing and asset provenance

## Critical findings and resolutions

### R1 — The application goal was ahead of its truth sources

**Problem:** YOLO or Transformer debugging without exact scalar numerics and
intermediate tensors would make failures difficult to localize.

**Resolution:** E1 establishes a cross-language numerical contract. Every later
layer compares at graph partition boundaries.

### R2 — Two implementations can drift

**Problem:** Python and C++ can each look correct while implementing different
rounding, overflow, or ABI behavior.

**Resolution:** Use shared golden byte fixtures and randomized cases. Neither
implementation is accepted merely because its own unit tests pass.

### R3 — Native C++ tools are absent

**Problem:** The host currently has no CMake, Ninja, or C++ compiler.

**Resolution:** Document a normal Ubuntu WSL2 setup as the preferred interactive
environment. Keep the existing pinned Ubuntu Docker file as a fallback and CI
path. Neither path is complete until its commands are actually executed and
recorded.

### R4 — ABI design could depend on C++ layout

**Problem:** Padding, alignment, and endianness make copied structs
non-portable.

**Resolution:** Encode every field explicitly in little-endian order. Keep
golden binary fixtures and compile-time field-size assertions.

### R5 — Scratchpad bytes have no inherent type

**Problem:** Reinterpreting arbitrary byte pointers as INT32 can cause
alignment, aliasing, and endianness bugs.

**Resolution:** Use checked little-endian load/store helpers. Command validation
checks alignment and byte ranges before execution.

### R6 — Fixed-point requantization was underspecified

**Problem:** “multiply by scale and round” does not define negative shifts,
ties, overflow, or saturation.

**Resolution:** E1 defines a single integer algorithm and boundary vectors
before it appears in the ABI.

### R7 — Spike is both valuable and unstable

**Problem:** Spike's internal C++ API is not public/stable, and the host lacks a
general Linux development distribution.

**Resolution:** Pin Spike in a Linux container, isolate it behind one adapter,
and execute a guest-memory proof before full integration.

### R8 — Timing can contaminate correctness

**Problem:** A model that advances state according to timing parameters can
produce different functional results.

**Resolution:** Functional execution and counter accounting are separate.
Fields remain named `estimated_cycles` until RTL correlation.

### R9 — YOLO's normal export boundary differs from the NPU boundary

**Problem:** The standard export follows detection inference/decode; it should
not be assumed to expose raw head tensors.

**Resolution:** Keep an immutable baseline ONNX model and generate a second,
hashed deployment partition with validated boundary values.

### R10 — Transformer support could become a second main project

**Problem:** A complete LLM adds tokenization, large weights, generation,
Softmax/norm precision, KV cache, and dynamic sequence behavior.

**Resolution:** The first target is one tiny decoder block after E4. It reuses
the common stack and reports prefill and decode separately.

### R11 — Deformable Conv hides irregular memory work

**Problem:** Counting it as normal convolution ignores runtime addresses,
bilinear sampling, optional masks, and additional traffic.

**Resolution:** Establish FP32 fallback semantics, then compare explicit
gather-to-column-buffer with a modeled streaming gather unit.

### R12 — External model assets create license and reproducibility risk

**Problem:** Committing weights, datasets, or images may violate licenses and
creates large, opaque repository state.

**Resolution:** Download assets separately. Record source, version, hash, and
license. Commit only small generated metadata unless a license review approves
the asset.

### R13 — Documentation status was easy to confuse with execution

**Problem:** Existing source files and prepared commands could be mistaken for
a passed build or test.

**Resolution:** Stable status terms now distinguish documented, reviewed,
scaffolded, executed, and verified. The
[static scaffold review](scaffold-review.md) records code
risks without claiming runtime evidence.

### R14 — Duplicate ABI summaries had already diverged

**Problem:** The high-level plan described a per-command ABI version and a
different MMIO map from the detailed design.

**Resolution:** The command-buffer header is the sole ABI version source. Exact
bytes live in the command ABI, and exact registers live in the MMIO/runtime
contract. The plan links those documents instead of duplicating offsets.

### R15 — Two editable Windows/WSL checkouts create drift

**Problem:** Building a Windows checkout through `/mnt/c` is slower, while
editing independent Windows and WSL copies can lose changes.

**Resolution:** After WSL setup, use one canonical Linux-filesystem checkout
and GitHub as the synchronization boundary. The setup guide makes this choice
explicit.

### R16 — An optional Docker path should not block learning

**Problem:** Requiring both WSL and Docker for E0 adds a second environment
before it teaches an NPU concept.

**Resolution:** WSL2 is the primary interactive gate. Docker must pass only if
the repository claims it as a supported reproducibility/CI path.

### R17 — “Queue” implied behavior that v1 did not provide

**Problem:** A single doorbell and mandatory reset were described as a command
queue, which could imply multiple pending submissions, backpressure, or
concurrent contexts.

**Resolution:** Version one is now explicitly one in-flight command buffer,
executed in order with no preemption. Queueing is a later versioned extension.

### R18 — Accumulator placement contradicted the ABI

**Problem:** One plan bullet named separate accumulator storage, while GEMM and
post-operation commands addressed INT32 C through the common scratchpad.

**Resolution:** ABI 1.0 stores accumulator tensors in the byte-addressed 64 KiB
scratchpad. A separate accumulator address space would require a future ABI.

### R19 — Binary artifacts lacked a shared guest-address contract

**Problem:** `commands.bin` contained absolute DMA addresses, but
`memory.bin`, native backing storage, and RV64 placement had no common mapping.

**Resolution:** The memory/execution contract now defines default payload/data
bases, alignment, segment roles, a manifest, and the rule that native and Spike
paths map the same guest addresses without rewriting commands.

### R20 — Failure and recovery allowed divergent implementations

**Problem:** Post-operation bounds, command immutability, partial writes,
scratchpad initialization, reset defaults, numeric error codes, and runtime
return values were incomplete.

**Resolution:** The command, memory/execution, MMIO/runtime, and numerical
contracts now freeze these behaviors. Verification includes every state
transition and malformed-record class.

### R21 — Moving sources could be mistaken for pinned dependencies

**Problem:** The reference library used current upstream links even where a
later implementation will depend on one exact revision.

**Resolution:** References now distinguish background links from normative
external baselines and implementation dependencies. Each volatile dependency
has a named freeze gate and requires an immutable provenance entry before its
execution result can be verified.

## Dependency review

The execution graph is acyclic:

```text
E0 build
 |
 v
E1 numerics
 |
 v
E2 ABI
 |
 v
E3 native NPU
 |
 v
E4 compiler/MLP
 |
 +-----------> E5 Spike/runtime
 |                |
 v                v
E6 tiny CNN ----> E7 YOLOv8n
                  |
                  +-> RTL / YOLO26 / Transformer / DeformConv / Linux
```

## Go/no-go rules

Stop a milestone when:

- An external format lacks a pinned version.
- A mismatch cannot identify its first divergent tensor.
- Guest-controlled sizes are not bounds checked.
- A performance number omits host fallback or transfer cost.
- A test depends on wall-clock timing.
- A generated artifact cannot name its generating command.

Proceed when:

- The focused gate and all earlier gates pass.
- Output is deterministic.
- Failure behavior is tested.
- Documentation matches observed commands.

## Documentation review versus execution proof

Use these labels consistently:

| Label | Meaning |
|---|---|
| Documented | The intended behavior and commands are written |
| Reviewed | Dependencies, ambiguity, and risks have been checked |
| Scaffolded | Source/configuration files exist |
| Executed | A named command was actually run |
| Verified | The exit gate passed with saved evidence |

At the current checkpoint, the plan is documented and reviewed. Parts of E0
and E1 are scaffolded. They are not yet verified.

## Residual risks

- Docker base packages can change even with an image digest unless package
  snapshots are also pinned.
- Spike guest-memory APIs may require a local compatibility patch.
- YOLO exporter graphs can change with Ultralytics revisions.
- Quantized SiLU and detection accuracy may require mixed precision.
- The MkDocs site is validated separately from implementation gate E0.

These risks are accepted because each has an explicit detection gate and does
not invalidate earlier work.
