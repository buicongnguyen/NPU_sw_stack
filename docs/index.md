<section class="npu-hero" markdown>

<div class="npu-hero__copy" markdown>

# From Graph to NPU

Build a small, inspectable NPU software stack—from exact INT8 arithmetic and a
graph compiler to an RV64 runtime, simulated device, real detector, and later
RTL comparison.

<div class="npu-actions" markdown>

[Start reading](chapter_preface/index.md){ .md-button .md-button--primary }
[Open the specification map](specification-status.md){ .md-button }
[View on GitHub](https://github.com/buicongnguyen/NPU_sw_stack){ .md-button }

</div>

</div>

![From Graph to NPU](assets/images/npu-stack-logo.svg){ .npu-hero__logo }

</section>

!!! warning "Documentation-first release"
    The book and contracts are the current deliverable. The source scaffold has
    received static review, but Linux builds, numerical tests, Spike, timing,
    and RTL experiments remain unverified until WSL is configured.

## One stack, explicit boundaries

```mermaid
flowchart LR
  G["Static graph"] --> C["Compiler"]
  C --> A["Command ABI"]
  A --> R["RV64 runtime"]
  R --> N["NPU model"]
  N --> V["Evidence"]
```

The project treats arithmetic, bytes, addresses, register behavior, lowering,
and evidence as contracts. That makes each layer teachable and lets failures be
located without guessing which component owns the rule.

<div class="chapter-card-grid" markdown>

<article class="chapter-card" markdown>

### Foundations

Learn the architecture, reproducibility method, exact integer inference, and
GEMM core.

[Chapters 1–4](chapter_01_system/index.md)

</article>

<article class="chapter-card" markdown>

### Compiler and runtime

Follow commands through memory planning, graph lowering, MMIO, RV64, and
Spike.

[Chapters 5–7](chapter_05_commands_memory/index.md)

</article>

<article class="chapter-card" markdown>

### Application path

Build from convolution and a tiny CNN toward a fixed-shape YOLOv8n detector.

[Chapters 8–10](chapter_08_cnn/index.md)

</article>

<article class="chapter-card" markdown>

### Research branches

Compare YOLO26 and study Transformer execution and deformable convolution
without blocking the primary path.

[Chapters 11–13](chapter_11_yolo26/index.md)

</article>

</div>

## How to use the book

- First-time reader: begin with the [Preface](chapter_preface/index.md).
- Implementer: follow the [course map](learning-path.md) and milestone gates.
- Reviewer: use the [specification map](specification-status.md), then read the
  [logic](project/reorganization-logic-review.md) and
  [static code](project/static-code-review-2026-07-28.md) reviews.
- Future experimenter: preserve the [evidence method](experiment-method.md) and
  add results to the [project journal](progress.md).

## Primary milestone

The first complete application is a quantized, fixed-batch YOLOv8n detector
with fixed `320 × 320` input. The NPU executes supported compute-heavy
subgraphs; decode and non-maximum suppression initially remain on the RISC-V
host. Results will be added only after the WSL toolchain and repeatable gates
are ready.
