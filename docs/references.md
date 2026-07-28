---
layout: page
title: Annotated References
permalink: /references/
---

# Annotated references

Prefer specifications, official documentation, and source repositories. Blog
posts can help interpretation, but they should not define numerical behavior or
the device ABI.

## Source roles and freeze status

External sources do not choose this repository's architecture. They have one
of three roles:

| Role | Meaning | Citation rule |
|---|---|---|
| Normative external baseline | An imported format/operator behavior | Pin exact spec/operator version before its gate |
| Implementation dependency | Behavior depends on upstream source/API | Pin tag or full commit and record license/hash |
| Background | Explains context or alternatives | Moving official overview link is acceptable |

The links below are a reading library and may point to current upstream pages.
They are not an implementation lockfile. Before execution, the named gate
creates an immutable provenance entry:

| Source family | Freeze gate | Required identity |
|---|---|---|
| Spike and RISC-V toolchain | E5 | Full commits/releases, build options, licenses |
| ONNX MLP/CNN operators | Importer gate | Opset and individual operator versions |
| Ultralytics YOLOv8n | Y0 | Package/source revision, model config, weight hash, license |
| YOLO26n | Lesson 9 | Package/source revision, config, weight hash, license |
| Transformer semantics | T0 | ONNX operator versions and reference-model revision |
| Deformable convolution | D0 | ONNX DeformConv version and framework release |

An implementation-dependent progress post links the immutable permalink, not
only the moving overview below. Until that entry exists, the dependency remains
explicitly unpinned and execution is not verified.

## RISC-V and Spike

- [Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
  Official Windows installation and distribution-selection procedure.

- [WSL filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
  Explains why Linux-heavy source trees should live in the WSL filesystem
  instead of under `/mnt/c`.

- [RISC-V GNU toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)
  Official source and prerequisite instructions for Newlib and Linux
  cross-toolchains. The repository is large, so use Ubuntu's packaged
  bare-metal compiler for the first proof when it is sufficient.

- [Spike RISC-V ISA simulator](https://github.com/riscv-software-src/riscv-isa-sim)
  Functional RV32/RV64 ISA simulator used as the host. Its README documents
  supported ISA features, extension loading, debugging, and the fact that its
  internal C++ interface is not a stable public API.

- [Spike extension interface](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/extension.h)
  Reference for later custom-instruction experiments.

- [Spike abstract device interface](https://github.com/riscv-software-src/riscv-isa-sim/blob/master/riscv/abstract_device.h)
  Defines MMIO device operations and plug-in registration used by the proposed
  NPU adapter.

- [RISC-V RVWMO explanatory material](https://docs.riscv.org/reference/isa/unpriv/mm-eplan.html)
  Informs the memory/device-I/O ordering analysis. Exact fence operands still
  depend on the selected platform's memory and I/O classification and are
  frozen during E5.

## Neural-network graph and quantization

- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)
  Normative model, graph, type, operator-set, and serialization concepts.

- [ONNX operators](https://onnx.ai/onnx/operators/)
  Versioned operator specifications. Record the exact opset used by every
  imported model.

- [ONNX shape inference](https://onnx.ai/onnx/repo-docs/ShapeInference.html)
  Describes both the API and its limitations with dynamic shapes.

- [ONNX QLinearMatMul](https://onnx.ai/onnx/operators/onnx__QLinearMatMul.html)
  Useful reference for quantized matrix multiplication, scales, zero points,
  saturation, and ties-to-even rounding.

- [ONNX Runtime quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
  Explains QOperator versus QDQ formats, static versus dynamic quantization,
  calibration, and activation debugging.

## YOLO models

- [Ultralytics YOLOv8](https://docs.ultralytics.com/models/yolov8/)
  Official model family, supported tasks, usage, and licensing summary.

- [YOLOv8 detection configuration](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
  Primary architecture description for the target backbone, neck, and head.

- [Ultralytics YOLO architecture guide](https://docs.ultralytics.com/guides/yolo-architecture/)
  Explains C2f, C3k2, C2PSA, DFL, and current detection-head differences.

- [Ultralytics YOLO26](https://docs.ultralytics.com/models/yolo26/)
  Official description of the later comparison target, including its
  one-to-one NMS-free head and output shape.

- [YOLO26 detection configuration](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/26/yolo26.yaml)
  Shows C3k2, SPPF, C2PSA, upsampling, concatenation, and the Detect head.

- [Ultralytics Detect source](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/nn/modules/head.py)
  Primary reference for DFL decode, end-to-end postprocessing, TopK, Gather,
  and output construction.

- [Ultralytics export documentation](https://docs.ultralytics.com/modes/export/)
  Export arguments and supported formats, including fixed/dynamic shapes and
  ONNX.

## Accelerator architecture

- [Gemmini](https://github.com/ucb-bar/gemmini)
  Full-stack systolic-array reference using Spike for functional testing and
  Verilator for cycle-accurate simulation. Study its layering; do not copy its
  complete complexity into the first milestone.

- [NVDLA primer](https://nvdla.org/primer.html)
  Reference for how a larger open NPU separates hardware engines, memory, and
  an on-device software stack.

- [Timeloop/Accelergy](https://timeloop.csail.mit.edu/)
  Analytical mapping and architecture exploration. Use it later to compare
  against the project's simpler timing model.

- [Verilator overview](https://verilator.org/guide/latest/overview.html)
  Describes converting SystemVerilog into a C++ or SystemC executable model
  with tracing and coverage support.

## Transformer and LLM operations

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
  The original Transformer paper and scaled dot-product attention definition.

- [FlashAttention](https://arxiv.org/abs/2205.14135)
  Primary reference for treating exact attention as an IO-aware tiled
  algorithm rather than only counting arithmetic operations.

- [ONNX Attention](https://onnx.ai/onnx/operators/onnx__Attention.html)
  Current standard semantics for Q/K/V shapes, causal behavior, scaling,
  precision, and cache-related inputs/outputs.

- [ONNX Softmax](https://onnx.ai/onnx/operators/onnx__Softmax.html)
  Standard normalized-exponential definition and axis behavior.

- [ONNX RMSNormalization](https://onnx.ai/onnx/operators/onnx__RMSNormalization.html)
  Standard RMSNorm function used as a reference for a Llama-style block.

- [Meta Llama 3 implementation](https://github.com/meta-llama/llama3/blob/main/llama/model.py)
  Historical implementation reference for RMSNorm, RoPE, grouped-query
  attention, SwiGLU-related feed-forward sizing, and KV cache. Meta archived
  this repository in March 2026, so pin a commit rather than treating `main` as
  an active upstream.

- [Current Meta Llama models repository](https://github.com/meta-llama/llama-models)
  Current official home for model utilities, model cards, licenses, and
  example scripts.

## Irregular vision operations

- [Deformable Convolutional Networks](https://arxiv.org/abs/1703.06211)
  Introduces learned offsets for spatial sampling.

- [Deformable ConvNets v2](https://arxiv.org/abs/1811.11168)
  Adds modulation to the deformable sampling behavior.

- [ONNX DeformConv](https://onnx.ai/onnx/operators/onnx__DeformConv.html)
  Versioned operator semantics, tensor shapes, interpolation, padding, groups,
  masks, and floating-point type constraints.

- [Torchvision deformable-convolution operators](https://docs.pytorch.org/vision/main/ops)
  Framework reference implementation for experiments.

## Full-system alternatives

- [QEMU RISC-V system emulator](https://qemu.readthedocs.io/en/master/system/target-riscv.html)
  Later choice for Linux driver work on the generic RISC-V `virt` platform.

- [gem5 standard library](https://www.gem5.org/documentation/gem5-stdlib/overview)
  Later choice for detailed CPU, cache, memory-system, and full-system timing
  studies.

## Documentation and publication

- [HelloAlgo repository](https://github.com/krahets/hello-algo/tree/69932aed1891a7b7f6a0de88cd116d3fe13e7032)
  Structural reference for chapter-oriented navigation, reader-first repository
  presentation, and colocated source. No prose, code, branding, or assets are
  copied.

- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
  Official artifact-based Actions deployment used by this repository.

- [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/)
  Official site, navigation, and strict-build configuration reference.

- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
  Theme documentation for search, navigation, code presentation, and palette
  features.

## Reference policy

Every progress article should:

1. Link the specification that defines the implemented behavior.
2. Link the exact source revision when behavior depends on implementation.
3. State the accessed or pinned version.
4. Avoid copying long source or documentation passages.
5. Clearly label inferences made from source code.
6. Record licenses for code, model weights, images, and datasets.

Use these claim labels in reviews:

- **External baseline** — behavior defined by a cited, versioned source.
- **Project decision** — normative behavior chosen in this repository.
- **Assumption** — unverified condition with a named validation gate.
- **Observation** — command output tied to a timestamp, project revision or
  file manifest, and artifact hash.

Model assets use separate provenance rows for source code, weights, datasets,
and images because their licenses and hashes may differ.
