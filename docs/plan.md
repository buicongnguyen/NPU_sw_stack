---
layout: page
title: Reviewed Implementation Plan
permalink: /plan/
---

# Reviewed implementation plan

Status: **design reviewed; implementation unverified**

Last reviewed: **2026-07-28**

## 1. Goal

Build a small but complete NPU simulation stack in which:

1. A compiler lowers a static neural-network graph to an NPU command stream.
2. A bare-metal RV64 program runs under Spike.
3. A runtime submits commands to a memory-mapped NPU.
4. A deterministic C++ model executes INT8 tensor operations.
5. Tests compare every layer against a Python/NumPy reference.
6. A timing mode reports estimated cycles, utilization, and traffic; later
   timing-model versions add categorized stalls.
7. A later SystemVerilog implementation is checked against the same tests.

The first release is intentionally limited to a quantized two-layer MLP. It is
large enough to exercise compilation, tiling, DMA, runtime submission, and
numerical correctness without requiring a large framework.

The **course-level application goal** is broader than the first release:
execute the convolution-heavy portion of YOLOv8n detection on the NPU for a
fixed `NCHW = 1x3x320x320` input, while the RISC-V host initially performs box
decode and non-maximum suppression. YOLO26n is a stretch comparison after the
YOLOv8n path is correct and measured. The detailed rationale is in the
[YOLO target decision](yolo-target.md).

## 2. Non-goals for the first release

- Training neural networks
- Dynamic tensor shapes
- Full ONNX operator coverage
- Linux kernel drivers
- Cache-coherent DMA
- Floating-point NPU execution
- Transformer/LLM execution in the first release
- Deformable convolution in the first release
- Cycle-accurate RISC-V CPU or interconnect simulation
- Large models such as ResNet-50 or a complete transformer
- Production security, virtualization, or multi-process isolation

These can become later experiments, but they must not block the first
end-to-end execution.

## 3. Architecture decision

### 3.1 Accepted design

Use Spike as the functional RISC-V host and attach the NPU as an MMIO plug-in.
The NPU core model remains independent of Spike:

```text
                         +--------------------+
Python reference ------> | differential tests |
                         +----------+---------+
                                    |
                                    v
+-------------+    +---------+    +------------------+
| graph input | -> | compiler| -> | command buffer   |
+-------------+    +---------+    +--------+---------+
                                           |
                              +------------+------------+
                              |                         |
                              v                         v
                    +----------------+        +----------------+
                    | native runner  |        | RV64 on Spike  |
                    +-------+--------+        +--------+-------+
                            |                          |
                            +------------+-------------+
                                         v
                               +------------------+
                               | shared NPU model |
                               +------------------+
```

### 3.2 Why MMIO comes before custom instructions

An MMIO accelerator naturally exposes asynchronous work, submission, DMA,
polling, interrupts, and error handling. A single custom instruction that
performs an entire GEMM would hide those system-software concepts.

After the MMIO system works, add `npu.submit` and `npu.wait` custom
instructions as a controlled comparison experiment.

### 3.3 Simulation truth levels

The project must distinguish three claims:

| Mode | Valid claim | Invalid claim |
|---|---|---|
| Functional model | Exact numerical and ABI behavior | Hardware performance |
| Analytical timing model | Reproducible performance estimate | Cycle accuracy |
| Verilated RTL | RTL cycle count for the modeled block | Complete SoC timing |

Documentation and CLI output must use the words `estimated_cycles` until the
model has been correlated with RTL.

## 4. Version-one NPU

### 4.1 Datapath

- 8x8 systolic multiply-accumulate array
- Signed INT8 activations and weights
- Signed INT32 accumulation
- Configurable 64 KiB scratchpad
- INT32 accumulator tensors stored in the common scratchpad
- Static tensor shapes
- Optional double buffering after single-buffer execution is correct

### 4.2 Commands

```text
DMA_LOAD
DMA_STORE
GEMM
ADD_BIAS
RELU
REQUANTIZE
BARRIER
END
```

Every command has a fixed-width header containing:

- Opcode
- Command size
- Flags
- Sequence number
- Reserved field, written as zero in ABI version 1

The command-buffer header carries the ABI major/minor version. Exact field
offsets, sizes, and validation order are frozen in the
[command ABI](command-abi.md).

Unknown opcodes, unsupported versions, invalid sizes, misaligned addresses,
and scratchpad overflows must produce explicit device errors.

### 4.3 MMIO register groups

Version one exposes an aligned 32-bit MMIO aperture containing:

- Device version and capabilities
- Control and state
- Split 64-bit command-buffer address
- Command-buffer byte count
- Stable error code and failing command
- Completed-command count
- Latched 64-bit MAC, traffic, and estimated-cycle counters

The exact offsets, access widths, status transitions, fence requirements, and
error behavior live in the
[MMIO/runtime contract](mmio-runtime.md). C/C++ headers,
the Spike adapter, and tests must all validate against that language-neutral
definition.

Memory ownership, command-buffer snapshots, scratchpad initialization,
partial-effect rules, and the single-submission scheduler live in the
[memory and execution model](memory-execution-model.md).

## 5. Software layers

### 5.1 Python reference

Responsibilities:

- Define exact INT8, INT32, rounding, scaling, clipping, and saturation rules.
- Produce layer-by-layer golden tensors.
- Generate deterministic random test vectors.
- Export small test graphs and model inputs.

The reference prioritizes clarity over performance.

### 5.2 Compiler

Initial flow:

```text
Tiny JSON graph
  -> validation and static shape inference
  -> quantization validation
  -> tiling
  -> scratchpad allocation
  -> DMA/compute scheduling
  -> command serialization
```

Version one keeps post-operations explicit. Constant folding and numerical
fusion are later optimizations that require their own equivalence evidence.

Only after the JSON path is stable, add an ONNX importer for:

- `MatMul` or `Gemm`
- `Add`
- `Relu`
- `Conv`
- `MaxPool`
- `Flatten`
- `Reshape`

The compiler must have a human-readable IR dump and command disassembler.
Binary output without explainable intermediate forms is not acceptable for a
learning project.

### 5.3 Runtime

The bare-metal C API, return values, output initialization, timeout behavior,
and numeric device errors are frozen in the
[MMIO/runtime contract](mmio-runtime.md). The runtime
owns MMIO barriers, status decoding, timeout behavior, and device error
translation. Applications must not access raw MMIO registers directly.

### 5.4 NPU model

The portable C++ model has no dependency on Spike. It exposes a narrow
interface for:

- Guest-memory reads and writes
- Register reads and writes
- Reset
- Command execution
- Counter snapshots
- Trace events

The native runner implements the memory interface with a byte array. The Spike
adapter implements it through Spike guest-memory access.

## 6. Proposed repository structure

```text
NPU_sw_stack/
|-- README.md
|-- CMakeLists.txt
|-- Makefile
|-- docs/
|   |-- plan.md
|   |-- progress.md
|   |-- publishing.md
|   `-- _posts/
|-- include/npu/
|   |-- abi.h
|   |-- commands.h
|   `-- registers.h
|-- model/
|   |-- dma/
|   |-- scratchpad/
|   |-- systolic_array/
|   `-- npu_model/
|-- simulators/
|   |-- native/
|   |-- spike_plugin/
|   `-- verilator/
|-- compiler/
|   |-- frontend/
|   |-- ir/
|   |-- passes/
|   |-- scheduler/
|   `-- emitter/
|-- runtime/
|   |-- include/
|   |-- baremetal/
|   `-- linux/
|-- firmware/
|   |-- startup/
|   |-- linker/
|   `-- examples/
|-- python/
|   |-- reference/
|   |-- quantization/
|   `-- tools/
|-- workloads/
|-- tests/
|   |-- unit/
|   |-- compiler/
|   |-- differential/
|   `-- end_to_end/
`-- scripts/
```

Directories should be created only when their first real file is added.

## 7. Milestones and gates

### Phase 0 — Reproducible foundation

Deliver:

- Git repository, README, license, formatting rules, and CI
- WSL2 or Linux dev-container instructions
- Pinned RISC-V compiler and Spike revision
- Native C++ and Python test commands
- RV64 hello-world ELF running in Spike

Exit gate:

```text
configure -> build -> test -> run Spike hello world
```

must work from a clean checkout using documented commands.

### Phase 1 — Numerical contract

Deliver:

- NumPy INT8 GEMM, bias, ReLU, and requantization
- Matching portable C++ kernels
- Boundary, random, and malformed-input tests

Exit gate:

- At least 1,000 deterministic randomized cases
- Exact output agreement
- Explicit tests for overflow, saturation, and rounding ties

### Phase 2 — Functional NPU

Deliver:

- Command decoder
- Scratchpad and accumulator bounds checking
- DMA operations against native simulated memory
- GEMM execution and error states
- Command disassembler

Exit gate:

- Native command-buffer execution matches Phase 1
- Invalid buffers never crash or access memory out of range

### Phase 3 — Compiler

Deliver:

- Tiny JSON graph schema
- Typed graph IR
- Static shapes
- Fusion and tiling
- Scratchpad allocation
- Binary emitter and readable dumps

Exit gate:

- `GEMM + bias + ReLU` graph compiles and executes
- Recompiling the same graph produces identical bytes

### Phase 4 — Spike integration

Deliver:

- Pinned Spike dependency
- Thin MMIO plug-in
- Guest-memory adapter
- Bare-metal runtime and linker setup
- Polling completion and timeout

Risk-reduction gate before full integration:

- Prove that the chosen Spike revision can safely read and write guest physical
  memory from an MMIO plug-in.
- Prove that reset and device ticking are deterministic.

Exit gate:

- RV64 program submits the same command buffer used by native tests
- Spike output matches NumPy and the native runner

### Phase 5 — Timing model and experiments

Deliver:

- Systolic fill/drain model
- DMA bandwidth and setup latency
- Scratchpad-bank conflicts
- Single and double buffering
- CSV/JSON counter export

Experiments:

- Array sizes 4x4, 8x8, and 16x16
- Scratchpads from 16 to 256 KiB
- M/N/K tile selection
- Weight-stationary versus output-stationary
- Bandwidth sensitivity and arithmetic intensity

Exit gate:

- Every estimate identifies its assumptions
- Changing one architecture parameter produces explainable counter changes

### Phase 6 — Workloads

Progression:

1. Rectangular GEMM
2. Two-layer quantized MLP
3. Conv2D lowered to GEMM
4. Small CNN
5. Depthwise convolution
6. Small attention block

Each workload requires layer-level golden outputs and a documented performance
experiment.

After the small CNN, the workload path becomes:

1. YOLOv8n operator inventory and floating-point ONNX baseline
2. One extracted C2f block
3. YOLOv8n backbone
4. YOLOv8n backbone and neck
5. Quantized convolutional detection head
6. Host-side DFL decode and NMS
7. Fixed-shape end-to-end image inference

The NPU does not need to implement NMS to satisfy the first YOLO milestone.

### Phase 7 — RTL correlation

Deliver:

- SystemVerilog processing element and systolic array
- Verilator harness
- Waveform generation
- Shared command/test-vector input

Exit gate:

```text
NumPy = C++ model = Spike model = Verilated RTL
```

for selected tests, with differences in analytical and RTL cycle counts
explained.

### Phase 8 — Optional Linux path

Only after the ABI is stable:

- QEMU RISC-V `virt` device model
- Device-tree binding
- Linux character or platform driver
- Interrupt completion
- User-space runtime and buffer management

### Phase 9 — Transformer/LLM capability track

This is a branch after the common GEMM/compiler/runtime foundation, not a
YOLO prerequisite.

Progression:

1. Batched MatMul and linear projections
2. FP32 reference Softmax and RMSNorm
3. RoPE and causal masking
4. Tiny multi-head attention
5. SwiGLU feed-forward block
6. KV-cache allocation and update
7. Prefill versus one-token decode
8. Mixed-precision and quantization experiments
9. IO-aware tiled attention

The first target is one tiny Llama-style decoder block, not a multi-billion
parameter model.

### Phase 10 — Deformable-convolution capability track

Progression:

1. FP32 reference matching ONNX DeformConv semantics
2. Zero-offset equivalence with regular Conv
3. Integer and fractional offsets
4. Bilinear interpolation and optional modulation mask
5. Host fallback through the runtime
6. Explicit deformable-im2col buffer followed by existing GEMM
7. Streaming gather/interpolation engine model
8. Memory-traffic, bank-conflict, and quantization study

Deformable convolution is not present in the base YOLOv8n or YOLO26n
architectures selected by this project.

## 8. Logic review

### Finding L1 — Original scope was too broad

**Severity:** High

**Resolution:** The first release ends at a two-layer MLP. ONNX, convolution,
RTL, and Linux are separately gated expansions.

### Finding L2 — Spike cannot validate performance

**Severity:** High

**Resolution:** Spike is used only for functional CPU/software integration.
Timing results come from an explicitly analytical NPU model and later RTL.

### Finding L3 — Starting with ONNX adds unrelated complexity

**Severity:** Medium

**Resolution:** Implement a tiny static JSON graph first. ONNX becomes an
import adapter after compiler IR and lowering work.

### Finding L4 — Spike coupling could contaminate the design

**Severity:** High

**Resolution:** The core model cannot include Spike headers. A narrow adapter
owns all Spike interaction. E5 must select and pin an exact reviewed Spike
revision because its internal C++ API is not stable; no revision is pinned at
the documentation-only checkpoint.

### Finding L5 — DMA access is the largest integration uncertainty

**Severity:** High

**Resolution:** Add a Phase 4 risk-reduction test before building the full
plug-in. If direct guest-memory access is unsuitable, use a staged shared
memory window for version one rather than redesigning the NPU.

### Finding L6 — Numerical behavior was underspecified

**Severity:** High

**Resolution:** Phase 1 defines signedness, accumulation width, rounding,
saturation, scale representation, tensor layout, and endianness before ABI or
compiler work.

### Finding L7 — An asynchronous device needs failure semantics

**Severity:** Medium

**Resolution:** The ABI includes busy, complete, timeout, reset, and specific
error states. Invalid commands fail deterministically instead of asserting.

### Finding L8 — Documentation could drift from implementation

**Severity:** Medium

**Resolution:** Every merged milestone updates the progress journal, command
examples, test evidence, and current-status section. Generated counter tables
should be committed only when the generating command is documented.

### Finding L9 — “YOLOv8n support” could hide an unstable graph cut

**Severity:** High

**Resolution:** Keep the official fixed-shape ONNX model immutable as a
baseline. Generate the raw-head deployment partition as a second hashed
artifact, validate boundary names and shapes, and reject exporter changes that
invalidate the partition.

### Finding L10 — YOLO host fallback could be excluded from measurements

**Severity:** Medium

**Resolution:** The operator-support report accounts for NPU MAC coverage,
partition traffic, and all host operations including decode and NMS.

### Finding L11 — Adding LLM support could turn the project into two projects

**Severity:** High

**Resolution:** Reuse the common GEMM, compiler, ABI, runtime, and memory model.
Add one tiny decoder block as a post-foundation branch. A complete LLM is not a
milestone.

### Finding L12 — INT8 MAC support is not complete Transformer support

**Severity:** High

**Resolution:** Model Softmax, normalization, RoPE, causal masking, KV cache,
and prefill/decode separately. Begin with host or FP32 reference execution for
reduction-sensitive operations before proposing mixed-precision hardware.

### Finding L13 — Deformable Conv cannot be treated as ordinary Conv

**Severity:** High

**Resolution:** Treat runtime offset generation, bounds checks, four-neighbor
bilinear sampling, optional masks, and irregular memory traffic as explicit
work. The first implementation is a host fallback; the first accelerator
experiment is gather-to-column-buffer plus the existing GEMM.

## 9. Engineering and code review

This is a prospective code review: it defines constraints that future changes
must satisfy.

### 9.1 ABI review rules

- Use fixed-width integer types.
- Make byte order explicitly little-endian.
- Do not serialize native C++ structs by copying their memory.
- Encode/decode fields with tested helper functions.
- Version every external structure.
- Reserve fields and require writers to zero them.
- Reject integer overflow in address-plus-size calculations.
- Add compile-time size checks to C-facing declarations.

### 9.2 C++ model review rules

- Target C++17 unless a later feature has a demonstrated benefit.
- Avoid global mutable state.
- Use deterministic clocks and random seeds.
- Separate functional state changes from counter accounting.
- Bounds-check all scratchpad, accumulator, and guest-memory accesses.
- Return structured errors for guest-controlled input.
- Run address/undefined-behavior sanitizers in native CI where supported.

### 9.3 Compiler review rules

- Passes consume and produce valid typed IR.
- Each pass has before/after text fixtures.
- Shape calculations check multiplication overflow.
- Buffer lifetimes are explicit.
- Scheduling is deterministic.
- Binary emission is separated from optimization.
- Unsupported operators and dynamic shapes fail with actionable diagnostics.

### 9.4 Runtime review rules

- Only the driver layer performs MMIO.
- MMIO accessors are volatile and use appropriate compiler/CPU barriers.
- All waits have timeouts.
- Reset handles in-flight work deterministically.
- Applications receive stable error codes, not simulator exceptions.
- Bare-metal code does not silently depend on hosted C-library behavior.

### 9.5 Test review rules

- A test identifies its truth source: NumPy, model, or RTL.
- Differential tests compare intermediate tensors, not only final output.
- Tests cover zero-sized, minimum, maximum, misaligned, and malformed inputs.
- Random tests record their seed.
- Performance tests never assert unstable wall-clock time.
- CI starts with small tests; long architecture sweeps run separately.

## 10. Pull-request checklist

Every implementation pull request should answer:

- What layer and milestone does this change belong to?
- What behavior or ABI changes?
- What is the golden reference?
- Which new tests fail without the change?
- Are results deterministic?
- Are errors and boundary cases tested?
- Does this change add a performance claim? If so, what assumptions support it?
- Which documentation and progress entry were updated?

## 11. Definition of the first release

Version `v0.1.0` is complete when a clean checkout can run one documented
command that:

1. Generates deterministic MLP inputs and weights.
2. Computes NumPy golden results.
3. Compiles the graph into a command buffer.
4. Runs it through the native NPU model.
5. Runs an RV64 application under Spike against the MMIO NPU.
6. Confirms exact output equality.
7. Writes machine-readable counters.
8. Links to a progress article explaining the design and results.

## 12. Definition of the YOLOv8n course goal

Version `v1.0.0` is complete when:

1. A pinned YOLOv8n model is exported to fixed-shape ONNX.
2. An operator-support report explains every compiled and host-fallback node.
3. INT8 NPU layers match the project's integer reference within the exact
   numerical contract.
4. Intermediate tensors are compared at every graph partition boundary.
5. The RV64 application executes NPU command buffers under Spike.
6. Host code decodes boxes and performs NMS.
7. At least one documented image produces plausible detections.
8. A small validation set records floating-point and quantized accuracy.
9. Estimated cycles, utilization, and memory traffic are reported with all
   assumptions.
10. The GitHub Pages course contains reproduction commands, failure notes, and
    links to machine-readable results.

## 13. References

- [Spike RISC-V ISA simulator](https://github.com/riscv-software-src/riscv-isa-sim)
- [Gemmini full-stack accelerator project](https://github.com/ucb-bar/gemmini)
- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)
- [ONNX shape inference](https://onnx.ai/onnx/repo-docs/ShapeInference.html)
- [Verilator overview](https://verilator.org/guide/latest/overview.html)
- [gem5 documentation](https://www.gem5.org/documentation/)
- [Timeloop/Accelergy](https://timeloop.csail.mit.edu/)
