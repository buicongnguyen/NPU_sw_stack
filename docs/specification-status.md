---
layout: page
title: Specification Map
permalink: /specification-status/
---

# Specification map

Documentation release: **v1 design release candidate**

Implementation status: **not verified; WSL setup and experiments are deferred**

This page tells a reader which document answers each design question and which
statements are project decisions rather than measured results. The v1 release
candidate is complete enough for implementation review. Its immutable
repository revision and public Pages deployment are recorded at publication.
It is not evidence that the simulator, compiler, or Spike integration works.

## Read by goal

| If you want to... | Read |
|---|---|
| Understand the whole system | [Architecture walkthrough](architecture.md) |
| Review exact integer behavior | [Numerical contract](numerical-contract.md) |
| Review serialized bytes | [Command-buffer ABI](command-abi.md) |
| Review memory, queues, and execution | [Memory and execution model](memory-execution-model.md) |
| Review registers and driver behavior | [MMIO/runtime contract](mmio-runtime.md) |
| Understand graph lowering | [Tiny compiler design](compiler-design.md) |
| See how the design will be proved | [Verification plan](verification-plan.md) |
| Follow the later implementation order | [Executable milestone plan](execution-plan.md) |
| Study the application destination | [YOLO target decision](yolo-target.md) |
| Inspect sources and provenance rules | [Annotated references](references.md) |

## Authority and conflict rules

The documents have different jobs:

| Authority | Documents | Meaning |
|---|---|---|
| Normative v1 contract | Numerical contract, command ABI, memory/execution model, MMIO/runtime contract | Implementations and tests must agree with these rules |
| Normative compiler plan | Tiny compiler design | Defines deterministic input, IR, pass, and artifact behavior |
| Verification contract | Verification plan, executable milestone plan | Defines what evidence is required before a status becomes verified |
| Explanatory | Architecture walkthrough, lessons, learning path | Teaches and summarizes; does not redefine bytes or arithmetic |
| Decision record | Reviewed plan, logic review, workload decision pages | Explains scope and why choices were made |
| Decision/check record | Dated progress posts | Front matter distinguishes decisions, local checks, and reproducible observations |
| Evidence | Generated manifests and `record_type: observation` posts | Records executed results tied to an immutable project state |

If two pages disagree, the more specific normative contract wins. The conflict
must then be removed from the explanatory page. Code comments, examples, and
generated disassembly never override a normative document.

## Frozen v1 project decisions

These are design choices for this repository. They are not claims that all
commercial NPUs behave this way.

| Topic | v1 decision |
|---|---|
| Host | Bare-metal RV64 program under Spike, after native-model bring-up |
| Device interface | One 4 KiB, 32-bit MMIO aperture and a command-buffer doorbell |
| Compute | Conceptual 8x8 signed INT8 MAC array with signed INT32 accumulation |
| Local memory | One 65,536-byte, byte-addressed scratchpad |
| Queueing | One in-order submission; no preemption and no concurrent contexts |
| Command format | Explicit little-endian fields, 16-byte records, ABI 1.0 |
| Functional scheduling | Commands execute in sequence after whole-buffer validation |
| First graph | Static, batch-one, quantized two-layer MLP |
| First application | Fixed `1x3x320x320` YOLOv8n partition; decode/NMS on host |
| Timing claims | Analytical estimates only, named `estimated_cycles` |
| Recovery | Explicit reset after complete or error; reset clears submission state |

## Deliberately deferred

The following do not block the documentation baseline:

- Installing WSL2, building C++, or running Spike
- Selecting and pinning the exact Spike commit
- Freezing platform-specific RISC-V `fence` operands after the memory/I/O
  classification is proven
- Interrupts, multiple queues, preemption, virtual memory, and cache-coherent
  DMA
- ONNX import beyond a strict supported subset
- Specialized convolution, Softmax, normalization, gather, or floating-point
  engines
- Cycle-accurate timing and RTL correlation
- YOLO26n, Transformer, and deformable-convolution experiments

Each deferred item has a gate in the implementation or lesson plan. A later
decision must not silently change valid ABI 1.0 bytes or v1 arithmetic.

## Status language

| Label | Required meaning |
|---|---|
| Documented | Intended behavior is written |
| Reviewed | Scope, dependencies, ambiguity, and risks were checked |
| Scaffolded | Source/configuration files exist |
| Executed | A named command ran in a recorded environment |
| Verified | The documented exit gate passed with saved evidence |

At this checkpoint the documentation is the deliverable. The core design is
documented and under review; source scaffolds are not runtime evidence.

## Documentation release checklist

- Every public page identifies whether it is a contract, explanation, plan, or
  evidence.
- Exact bytes appear only in the command ABI.
- Exact registers appear only in the MMIO/runtime contract.
- Exact arithmetic appears only in the numerical contract.
- Examples are labeled illustrative until generated by verified tools.
- External facts cite primary or official sources.
- Repository-specific choices are labeled project decisions.
- Future experiments are separated from observed results.
- Local links, MkDocs navigation, and strict site build pass their documentation
  gates.
