---
layout: page
title: "Lesson 0: Baseline and Reproducibility"
permalink: /lessons/00-baseline/
---

# Lesson 0: baseline and reproducibility

## Outcome

Establish host-side floating-point references before writing NPU code.

At the end, the repository should contain metadata—not copyrighted model
weights—for:

- YOLOv8n PyTorch inference
- Fixed-shape YOLOv8n ONNX inference
- Optional YOLO26n comparison
- Model and graph hashes
- Operator histograms
- Saved input and output tensors for one permitted test image

## Why this comes first

If the original framework and exported ONNX model do not agree, NPU debugging
has no trustworthy starting point. Export version, opset, image preprocessing,
and output-head configuration are part of the model contract.

## Step 1 — Define the environment

Use WSL2 or a Linux dev container for consistency with Spike. Pin:

- Python
- Ultralytics
- PyTorch
- ONNX
- ONNX Runtime
- NumPy

The repository will eventually expose one bootstrap command. Until the lock
file is implemented, do not treat an unpinned `pip install` as reproducible.

Record:

```text
host OS:
Python:
Ultralytics:
PyTorch:
ONNX:
ONNX Runtime:
model name:
model SHA-256:
test image source and license:
```

## Step 2 — Run official host inference

The official Ultralytics CLI pattern is:

```bash
yolo predict model=yolov8n.pt source=path/to/image.jpg imgsz=320
```

Save:

- Preprocessed input tensor
- Raw model outputs before visualization
- Final boxes, classes, and confidence scores
- Preprocessing parameters

Do not compare only the rendered image.

## Step 3 — Export fixed-shape ONNX

Planned baseline command:

```bash
yolo export model=yolov8n.pt format=onnx imgsz=320 batch=1 dynamic=False opset=17 simplify=False
```

Why these settings:

- Fixed batch and image shapes simplify compiler work.
- Opset is explicit.
- Graph simplification is initially disabled so transformations remain
  attributable. A simplified export can be compared later.

The actual pinned project command and observed graph must be recorded in the
progress article; export behavior can change between Ultralytics releases.

## Step 4 — Inventory the graph

The future repository tool should print:

```text
IR version
opset imports
input/output names and shapes
initializer count and bytes
node count
operator histogram
dynamic dimensions
unsupported attributes
SHA-256 of the ONNX file
```

Example exploration code:

```python
from collections import Counter
import onnx

model = onnx.load("yolov8n.onnx")
onnx.checker.check_model(model)
counts = Counter(node.op_type for node in model.graph.node)
for op, count in sorted(counts.items()):
    print(f"{op:24s} {count}")
```

This is exploratory code. The project version should have tests and
machine-readable JSON output.

## Step 5 — Compare PyTorch and ONNX Runtime

Use the exact same preprocessed tensor. Compare:

- Output shapes and ordering
- Maximum absolute error
- Mean absolute error
- Selected element values
- Decoded detections

Set a documented floating-point tolerance. Do not silently use a loose
tolerance to hide export errors.

The official export is the behavioral baseline. Do not modify its outputs to
expose raw head tensors during this step.

## Correctness gate

- The model and dependencies are pinned.
- The ONNX checker passes.
- There are no unknown dynamic dimensions.
- PyTorch and ONNX Runtime outputs agree within the documented tolerance.
- All artifacts have hashes.
- No external weights or unlicensed images are committed.
- The documented output is identified as decoded or raw; it is not inferred
  from its file name.

## Progress article

Suggested title:

```text
Baseline: exporting fixed-shape YOLOv8n to ONNX
```

Include the complete operator histogram. Mark which operators appear to be
accelerator candidates and which belong to host postprocessing, but do not
finalize partitioning yet.

## Primary references

- [Official YOLOv8 documentation](https://docs.ultralytics.com/models/yolov8/)
- [Ultralytics export documentation](https://docs.ultralytics.com/modes/export/)
- [YOLOv8 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)
- [ONNX checker and Python introduction](https://onnx.ai/onnx/intro/python.html)
