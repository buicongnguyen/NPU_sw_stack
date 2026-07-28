---
layout: page
title: "Lesson 11: Deformable Convolution"
permalink: /lessons/11-deformable-conv/
---

# Lesson 11: deformable convolution

## Outcome

Implement correct deformable sampling, quantify why it performs poorly on a
regular MAC array, and compare host fallback, column-buffer lowering, and a
streaming gather front end.

Read the full
[deformable-convolution study](../deformable-convolution.md).

## Fixed lab configuration

Start with:

| Parameter | Value |
|---|---:|
| Batch | 1 |
| Input channels | 1 |
| Output channels | 1 |
| Input height/width | 4x4 |
| Kernel | 3x3 |
| Stride | 1 |
| Dilation | 1 |
| Padding | 1 |
| Groups | 1 |
| Offset groups | 1 |
| Reference dtype | FP32 |

Use deterministic small integers for input and weights. The small tensor is
more important than realistic throughput because every sampled coordinate must
be inspectable.

## D0 — Freeze the semantic contract

Before coding, document:

- NCHW tensor layout
- Offset tensor channel ordering
- Whether offsets are stored as `(dy, dx)` or `(dx, dy)`
- Output-shape equation
- Padding and out-of-range value
- Bilinear interpolation equation
- Group and offset-group mapping
- Optional mask placement
- Accumulation dtype

Use one pinned ONNX DeformConv opset as the normative semantic reference.

Deliverable:

```text
docs/specs/deform-conv-v1.md
```

## D1 — Bilinear sampler without convolution

Implement one function:

```text
sample(input_plane, y, x) -> FP32
```

For `y0=floor(y)`, `x0=floor(x)`, `dy=y-y0`, and `dx=x-x0`, compare the four
neighbors:

```text
(1-dy)(1-dx) * I[y0,   x0]
(1-dy)dx     * I[y0,   x0+1]
dy(1-dx)     * I[y0+1, x0]
dy dx        * I[y0+1, x0+1]
```

Each out-of-range neighbor contributes the documented padding value.

Named tests:

- Exact integer coordinate
- Center of four pixels
- Fractional negative coordinate
- Bottom/right boundary
- Completely out-of-range coordinate

Include at least one hand calculation in the progress post.

## D2 — Zero-offset equivalence

Set all offsets to zero and the optional mask to one. Compare the deformable
implementation with ordinary convolution using identical weights, bias,
stride, padding, dilation, and groups.

This gate catches offset-channel order, base-coordinate, and padding mistakes
before irregular addresses are introduced.

## D3 — Integer offsets

Use offsets that shift selected kernel points by `-1`, `0`, and `+1`.
Interpolation should collapse to a single valid pixel for in-range integer
coordinates.

Record for one output element:

```text
kernel point
base y/x
offset dy/dx
sample y/x
loaded input or padding
convolution weight
contribution
```

## D4 — Fractional offsets

Use offsets such as `0.25`, `0.5`, and `-0.5`. Compare:

1. Hand-calculated sample
2. Scalar sampler
3. Full scalar deformable convolution
4. ONNX Runtime or Torchvision reference

Report the exact absolute/relative tolerance and the first failing coordinate.

## D5 — Modulation mask

Test masks of:

- Zero: selected sample contributes zero
- One: behavior is unchanged
- Fractional value: contribution scales predictably

Check the framework/operator contract for the mask tensor shape and ordering;
do not infer it from the offset tensor.

## D6 — Groups and offset groups

Increase channels only after the one-channel gate passes. Test:

- Convolution groups greater than one
- Offset groups greater than one
- Invalid divisibility
- Correct channel-to-offset-group mapping

Save a trace that identifies the offset group used by each input channel.

## D7 — Host fallback through the runtime

Pass the operation through the same graph/runtime partitioning mechanism used
by other unsupported operators.

Count:

- Input bytes transferred
- Offset bytes transferred
- Mask bytes transferred
- Weight/bias bytes
- Output bytes
- Host arithmetic operations
- Any synchronization boundaries

The output must match the scalar reference. The report must not assign this
work zero cost merely because it is outside the NPU.

## D8 — Gather-to-column-buffer lowering

Materialize one row per output/kernel sample so the existing GEMM engine can
consume regular data:

```text
input + offsets + mask
-> bounds-checked gather
-> bilinear interpolation
-> sampled column buffer
-> GEMM
-> output
```

Compare with host fallback and report:

- Temporary column-buffer bytes
- Logical samples
- Physical input loads
- Coalesced/burst opportunities
- NPU GEMM MACs and utilization
- Transfer and synchronization costs

This path accelerates the regular multiply stage but may increase memory
traffic. The experiment must measure that tradeoff.

## D9 — Streaming gather timing model

Model a front end with explicit parameters:

```text
address-generation lanes
outstanding memory requests
scratchpad banks
interpolation lanes
request coalescing width
queue depth
MAC-consumer rate
```

Track stalls caused by:

- Address generation
- Four-neighbor fetches
- Bank conflicts
- Out-of-range handling
- Interpolation throughput
- Backpressure from GEMM

Functional results remain identical to D8; only accounting changes.

## D10 — Offset precision study

Do not begin with a full INT8 operator. Quantize offsets independently to
candidate fixed-point formats and compare:

- Coordinate error
- Sample-value error
- Final output error
- Required multiplier/shift behavior
- Range versus fractional precision

Keep feature/weight quantization separate from offset quantization so their
effects can be attributed.

## Required measurements

- Input, offset, mask, temporary, and output bytes
- Number of physical input loads
- Coalesced versus independent requests
- Scratchpad bank conflicts
- Interpolation operations
- GEMM utilization
- Host/NPU transfer overhead

## Gate

- Reference matches ONNX/Torchvision semantics.
- Zero offsets match regular Conv.
- Fractional boundary cases have hand-calculated tests.
- All fallback and decomposition costs are visible.
- No INT8 ABI is proposed without an offset/interpolation error study.
- Group and offset-group behavior is covered.
- The functional output is invariant under timing-model parameters.

## Required progress posts

Write at least three posts:

1. `Deformable sampling semantics and hand-calculated boundaries`
2. `Host fallback versus deformable-im2col`
3. `Streaming gather model and irregular-memory stalls`

Publish the offset-precision study separately if it changes the proposed ABI.

## Primary references

- [Deformable Convolutional Networks](https://arxiv.org/abs/1703.06211)
- [Deformable ConvNets v2](https://arxiv.org/abs/1811.11168)
- [ONNX DeformConv](https://onnx.ai/onnx/operators/onnx__DeformConv.html)
- [Torchvision operators](https://docs.pytorch.org/vision/main/ops)
