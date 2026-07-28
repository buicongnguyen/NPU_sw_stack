---
layout: page
title: "Lesson 7: YOLOv8n Deployment"
permalink: /lessons/07-yolov8n/
---

# Lesson 7: YOLOv8n deployment

## Outcome

Execute fixed-shape YOLOv8n convolutional inference on the simulated INT8 NPU
and perform initial detection postprocessing on the RV64 host.

Read the [YOLO target decision](../yolo-target.md) first.

## Step 1 — Freeze the target

Record:

```text
Ultralytics version
model file hash
ONNX file hash
opset
input shape: 1x3x320x320
class count
end-to-end/head settings
calibration dataset and license
test images and licenses
```

No implementation result is reproducible without this data.

## Step 2 — Produce an operator support report

Classify every ONNX node:

- Direct NPU command
- Compiler-fused into another command
- Lowered into multiple commands
- RISC-V host fallback
- Unsupported/error

Include tensor shapes and estimated bytes crossing each partition.

The official ONNX export usually follows the `Detect` inference path through
DFL and box decoding. Preserve that model as the ONNX Runtime baseline. Create
a second, explicitly named deployment graph that cuts at validated raw head
tensors. Do not mutate the baseline file in place.

## Step 3 — Bring up one block at a time

Order:

1. First Conv
2. First C2f block
3. Backbone through P3
4. Backbone through P4 and P5
5. SPPF
6. First upsample and concat
7. Complete neck
8. Box and class head convolutions

At every step, compare intermediate tensors before adding more layers.

## Step 4 — Control activation memory

YOLO skip connections keep feature maps alive. Publish:

- Tensor birth and last use
- Tensor size
- Assigned DRAM or scratchpad address
- Peak live bytes
- Copies created by concat

Investigate whether concat can be eliminated by allocating producer outputs
directly into adjacent regions.

## Step 5 — Calibrate INT8

Use static calibration for the CNN:

- Record sample count and selection.
- Record MinMax, Entropy, or Percentile method.
- Save per-layer scales.
- Compare float and quantized activations.
- Exclude numerically sensitive nodes only with evidence.

Quantization accuracy and simulator correctness are different tests.

## Step 6 — Execute raw detection heads

The NPU returns raw box and class tensors. Verify them against the project's
integer reference before decoding boxes.

The graph-cut tool must emit:

- Source model hash
- Output value names and shapes
- Removed/fallback node inventory
- New deployment-graph hash
- A test proving the cut tensors match the same values captured from the
  baseline framework

## Step 7 — Implement host postprocessing

On RV64:

- DFL projection/decode
- Anchor and stride handling
- Sigmoid if not already executed
- Confidence threshold
- Non-maximum suppression
- Top detections

Start with a clear scalar implementation. Optimization is a later experiment.

## Step 8 — End-to-end image

For one documented image, publish:

- Original image and license/source
- Preprocessed input hash
- Float detections
- INT8 reference detections
- Spike/NPU detections
- Layer/partition errors
- NPU counters
- Host instruction count if measured

## Step 9 — Small accuracy study

Use a permitted small dataset, initially COCO8:

- Float baseline
- ONNX baseline
- Quantized host reference
- Spike/NPU result

Report precision/recall or mAP with dataset size prominently stated. Do not
present COCO8 results as full COCO accuracy.

## Correctness gate

- Every graph node is classified.
- All NPU partition boundaries match the integer reference.
- At least one image produces plausible, comparable detections.
- The small-set accuracy delta is recorded.
- Performance output is explicitly analytical.
- No model weights or dataset assets are committed without license approval.

## Primary references

- [Official YOLOv8 documentation](https://docs.ultralytics.com/models/yolov8/)
- [YOLOv8 architecture YAML](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/models/v8/yolov8.yaml)
- [Ultralytics detection head source](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/nn/modules/head.py)
- [Ultralytics export documentation](https://docs.ultralytics.com/modes/export/)
- [ONNX Runtime quantization](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html)
