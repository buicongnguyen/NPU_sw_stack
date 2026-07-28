---
layout: page
title: Step-by-Step Learning Path
permalink: /learning-path/
---

# Step-by-step learning path

The goal is not to choose between simple operations and YOLO. Simple operations
are the proof steps needed to understand and trust a YOLO execution.

The path is:

```text
integer arithmetic
  -> GEMM
  -> systolic-array model
  -> command ABI, memory, and native device
  -> graph compiler
  -> runtime and Spike MMIO integration
  -> convolution lowering
  -> tiny CNN
  -> YOLOv8n backbone and neck
  -> YOLOv8n detection with host postprocessing
  -> RTL correlation
  -> optional YOLO26n comparison
```

## How to use the course

Begin with [Start Here](start-here.md) and the
[architecture walkthrough](architecture.md). When ready
to execute the labs, complete the
[deferred WSL2 setup](setup-wsl.md).

For each lesson:

1. Read the concepts and primary references.
2. Implement only the stated deliverable.
3. Run the correctness gate.
4. Save machine-readable evidence using the
   [experiment method](experiment-method.md).
5. Write a progress post using `docs/_drafts/progress-entry-template.md`.
6. Do not move forward while the gate is red.

## Course map

| Lesson | Main question | Required output |
|---|---|---|
| [0. Baseline and reproducibility](lessons/00-baseline.md) | What exactly are we trying to reproduce? | Pinned host baselines and graph inventory |
| [1. Integer inference](lessons/01-integer-inference.md) | What does INT8 inference mean bit-for-bit? | NumPy and C++ numerical contract |
| [2. GEMM and the NPU core](lessons/02-gemm-and-npu.md) | How does data reuse create acceleration? | Tiled GEMM and systolic timing model |
| [3. Commands, memory, and native device](lessons/03-commands-memory.md) | Can exact commands execute safely without a compiler or Spike? | Golden ABI buffers and native command model |
| [4. Compiler and command stream](lessons/04-compiler.md) | How is a graph converted into device commands? | Typed IR and deterministic command buffer |
| [5. Runtime and Spike](lessons/05-spike-runtime.md) | How does RISC-V software control the NPU? | MMIO plug-in and bare-metal driver |
| [6A. Convolution and graph lowering](lessons/03-convolution.md) | How do CNN layers become accelerator work? | Conv2D reference, fusion, and lowering |
| [6B. Tiny CNN integration](lessons/06-tiny-cnn.md) | Does the complete stack work across layers? | Quantized tiny CNN under Spike |
| [7. YOLOv8n deployment](lessons/07-yolov8n.md) | Can the stack run a real detector? | Fixed-shape hybrid YOLOv8n |
| [8. Performance and RTL](lessons/08-performance-rtl.md) | Which performance claims survive RTL? | Correlated analytical and RTL results |
| [9. YOLO26n comparison](lessons/09-yolo26n.md) | What changes for a newer architecture? | Operator and performance comparison |
| [10. Transformer/LLM operations](lessons/10-transformer.md) | What changes for attention and autoregressive decoding? | Tiny decoder block with KV cache |
| [11. Deformable convolution](lessons/11-deformable-conv.md) | How should irregular fractional sampling be handled? | Reference, fallback, and gather-engine study |

## Completion levels

### Level A — Numerical foundations

Complete Lessons 0–2. You should be able to explain:

- Why INT8 multiplication normally accumulates into INT32
- How scale and zero point represent real values
- Why loop ordering changes memory traffic
- How a systolic array fills and drains
- Why utilization falls on small or badly shaped tiles

### Level B — Full-stack simulator

Complete Lessons 3–6B. You should be able to trace:

```text
graph node
-> compiler IR
-> tile schedule
-> command bytes
-> RISC-V submission
-> MMIO transaction
-> simulated DMA
-> NPU result
```

### Level C — Application deployment

Complete Lesson 7. You should be able to explain why some YOLO nodes run on the
NPU and others run on the host, and measure both the numerical effect of INT8
quantization and the architectural cost of data movement.

### Level D — Hardware correlation

Complete Lessons 8–9. You should be able to identify which assumptions in the
analytical model are inaccurate and evaluate how a newer model architecture
changes accelerator requirements.

### Level E — Irregular and generative workloads

Lessons 10–11 are branches rather than prerequisites for YOLOv8n:

```text
                         +-> Transformer/LLM track
common GEMM + runtime ---+
                         +-> deformable-convolution track
```

The Transformer track studies mixed precision, reductions, Softmax,
autoregressive decode, and KV-cache bandwidth. The deformable-convolution track
studies data-dependent addressing, interpolation, and gather behavior.

## Documentation definition of done

A lesson is not complete until its article includes:

- Exact dependency versions and Git commit
- Architecture parameters
- Input shapes and tensor layouts
- Commands used
- Test names and results
- Random seeds
- Expected and observed output
- At least one failure or boundary case
- Machine-readable counter or accuracy data
- Interpretation, not only raw numbers
- Primary reference links

Use the [annotated reference library](references.md) and
link the most relevant references again inside each lesson.
