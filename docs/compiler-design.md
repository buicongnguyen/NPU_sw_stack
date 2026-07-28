---
layout: page
title: Tiny Compiler Design
permalink: /compiler-design/
---

# Tiny compiler design

Status: **v1 normative compiler design; implementation unverified**

The compiler is educational, deterministic, and intentionally small. Its first
input is a project-owned JSON graph. ONNX is added only after the internal
passes and command ABI are trustworthy.

## First graph

The first network is:

```text
input [1, 16] INT8
-> Linear [16, 32] with INT32 bias
-> ReLU
-> Requantize INT32 to INT8
-> Linear [32, 8] with INT32 bias
-> Requantize INT32 to INT8
-> output [1, 8] INT8
```

All weights, inputs, scales, multipliers, shifts, and biases are generated from
a fixed seed and stored or hashed in the workload manifest.

## Input schema

The first input format is strict JSON. This complete one-layer example uses the
same schema as the two-layer workload:

```json
{
  "format": "npu-lab-graph",
  "version": 1,
  "inputs": [
    {
      "name": "x",
      "shape": [1, 16],
      "dtype": "i8",
      "quantization": {"scale": "0.03125", "zero_point": 0}
    }
  ],
  "initializers": [
    {
      "name": "w1",
      "shape": [16, 32],
      "dtype": "i8",
      "quantization": {"scale": "0.015625", "zero_point": 0},
      "data_file": "one_layer.weights.bin",
      "byte_offset": 0,
      "byte_count": 512,
      "sha256": "full-lowercase-hex"
    },
    {
      "name": "b1",
      "shape": [32],
      "dtype": "i32",
      "quantization": {"scale": "0.00048828125", "zero_point": 0},
      "data_file": "one_layer.weights.bin",
      "byte_offset": 512,
      "byte_count": 128,
      "sha256": "full-lowercase-hex"
    }
  ],
  "values": [
    {"name": "fc1_i32", "shape": [1, 32], "dtype": "i32"},
    {
      "name": "y",
      "shape": [1, 32],
      "dtype": "i8",
      "quantization": {"scale": "0.0625", "zero_point": 0}
    }
  ],
  "nodes": [
    {
      "name": "fc1",
      "op": "Linear",
      "inputs": ["x", "w1", "b1"],
      "outputs": ["fc1_i32"],
      "attributes": {}
    },
    {
      "name": "quantize_output",
      "op": "Requantize",
      "inputs": ["fc1_i32"],
      "outputs": ["y"],
      "attributes": {}
    }
  ],
  "outputs": [{"name": "y"}]
}
```

The root requires exactly `format`, `version`, `inputs`, `initializers`,
`values`, `nodes`, and `outputs`; unknown fields are rejected. `values`
declares every node-produced tensor, including final outputs. Names are unique
ASCII identifiers matching `[A-Za-z_][A-Za-z0-9_.-]{0,127}`. File paths are
relative to the graph file, may not escape its directory, and are verified by
SHA-256.

Version one supports `i8` and `i32`, rank-one bias tensors, and rank-two data
and weight tensors. Dimensions are positive, no larger than `2^31-1`, and
their checked total byte size does not exceed the submission-image limit.
Rank-two contents are contiguous row-major; rank one is contiguous element
order. The binary initializer follows that order with little-endian INT32
elements.

Every signed INT8 tensor has a quantization object with zero point zero. INT32
bias initializers also declare zero point zero and the exact product of input
and weight scales. Scale is a canonical positive decimal string, not a JSON
binary float. The compiler parses it as an exact integer coefficient and power
of ten so multiplier selection is deterministic.

`Linear` has three inputs `(x, weight, bias)`, one output, and no attributes.
In version one, `weight` and `bias` must resolve to immutable initializers.
`Relu` and `Requantize` each have one input and one output. `Requantize`
requires the output tensor's quantization metadata. Unknown operators,
attributes, or arities are errors.

## Intermediate representation

Each tensor records:

```text
name
dtype
static shape
layout
producer
consumers
constant/data source
quantization parameters
guest-memory placement
scratchpad placement and lifetime
```

Each operation records a typed opcode and attributes rather than retaining an
arbitrary dictionary after parsing.

## Pass 0 — Parse and validate

Reject:

- Unknown format/version
- Duplicate tensor/node names
- Missing producer or initializer
- Cyclic graph
- Unsupported dtype/rank/operator
- Dynamic or nonpositive dimension
- Multiple writes to one tensor

Diagnostics include the node/tensor name and a stable error category.

## Pass 1 — Infer and verify shapes

For `Linear`:

```text
X [M, K]
W [K, N]
B [N]
Y [M, N]
```

For every operation, compare inferred output with any declared shape. Use
checked multiplication when calculating element counts and byte sizes.

## Pass 2 — Normalize and lower

Convert high-level `Linear` into:

```text
GEMM_I8_I8_I32 -> private unbiased accumulator
ADD_BIAS_I32    -> declared Linear output
```

Keep ReLU and Requantize explicit in version one. Later fusion may change
scheduling but not observable numerical behavior.

The IR is SSA-like, while ABI 1.0 `ADD_BIAS_I32` and `RELU_I32` operate in
place. Lowering therefore creates explicit logical values around one
coalesced scratchpad range:

- GEMM produces a compiler-private unbiased accumulator consumed only by the
  following bias command.
- `ADD_BIAS_I32` ends that temporary lifetime and begins the declared
  `Linear` output lifetime in the same bytes.
- A ReLU input must have no other consumer and must not also be a graph output;
  the ReLU output begins in the same bytes after the command.

The allocation map records these alias predecessors rather than pretending the
values occupy independent storage. A graph that cannot satisfy mandatory
coalescing is rejected with `UNSUPPORTED_ALIASING`; version one does not insert
a hidden copy. `REQUANTIZE_I32_I8` remains out of place because ABI 1.0
prohibits source/destination overlap.

For future Conv2D, lowering records padding/dilation/layout transformations
explicitly before producing matrix/tile operations.

Version one performs no algebraic constant folding or numerical fusion.
Keeping GEMM, bias, ReLU, and requantization explicit makes the first
differential traces readable. Such optimizations require a later equivalence
gate.

## Tiling policy

The first MLP is emitted as whole operations when its live operands fit. If a
GEMM does not fit, v1 may tile only the output `M` and `N` dimensions; it does
not tile `K`, because ABI 1.0 has no accumulate-into-existing-C command.

Candidate `(tile_m, tile_n)` pairs must keep full-K A and B slices, INT32 C,
bias, and INT8 output inside scratchpad. Search legal candidates by:

1. Largest `tile_m * tile_n`.
2. Then largest `tile_n`.
3. Then largest `tile_m`.

Prefer multiples of eight for non-edge tiles. The loop order is M outer, N
inner. Edge tiles use their exact smaller dimensions. If no pair fits or K
cannot be represented by the ABI field, compilation fails with
`UNSUPPORTED_TILING`; it never silently changes arithmetic.

An M tile of row-major A is contiguous because it retains the complete K
dimension. An N tile of row-major B is not contiguous in the original
initializer. Because version-one Linear weights are immutable initializers,
the compiler packs each `K × tile_n` weight tile into a deterministic
tile-row-major constant segment in `memory.bin` and emits `ldb_bytes =
tile_n`. The manifest records the logical tensor, tile origin, tile shape, and
storage layout for every packed segment.

A tiled output must still appear as one logical row-major tensor. When
`tile_n < N`, the scheduler emits one contiguous `DMA_STORE` per output-tile
row to its final guest row/column address. It never stores the compact
`tile_m × tile_n` scratchpad block as though those rows were contiguous in the
full logical output. The same rule applies when a materialized intermediate is
written to guest memory.

The compiler estimates the exact record count and serialized command bytes for
each candidate, including row-wise stores. A candidate that exceeds ABI 1.0
`MAX_CMD_BYTES`, the representable command count, or the 16 MiB submission
image limit after tile packing is illegal even when its scratchpad footprint
fits.

## Pass 3 — Lifetime analysis

For each nonconstant tensor, compute:

```text
birth = producing operation index
death = last consuming operation index
```

Graph outputs live through the final store. Constants live in guest memory and
occupy scratchpad only during scheduled tiles.

Create a debug table:

| Tensor | Bytes | Birth | Death | Scratchpad offset |
|---|---:|---:|---:|---:|
| `x` | 16 | 0 | 0 | assigned |
| `fc1_i32` | 128 | 0 | 2 | assigned |
| `fc1_i8` | 32 | 2 | 3 | assigned/reused |

Values here are illustrative until emitted by the compiler.

## Pass 4 — Scratchpad allocation

Version one uses a deterministic first-fit allocator:

1. Sort allocations by birth, then stable tensor name.
2. Release regions only after the death operation.
3. Align INT8 to 1 byte and INT32 to 4 bytes.
4. Choose the lowest fitting offset.
5. Reject a graph that exceeds 64 KiB.

The compiler emits an allocation map and peak live bytes. Optimization can
later compare first-fit with alternate policies.

## Pass 5 — Schedule commands

For each layer:

1. Load required inputs, weights, and bias.
2. Issue GEMM.
3. Issue bias/activation/requantization commands.
4. Store the graph output or keep a live intermediate.
5. Do not insert `BARRIER` in generated ABI 1.0 streams.
6. Emit one final `END`.

Version one is conservative and serial:

- A tensor must be initialized before its first read.
- For each M tile, load A once when its scratchpad lifetime can span all N
  tiles; otherwise reload it deterministically.
- For each N tile, load its packed B constant and contiguous bias slice, run
  GEMM and explicit post-operations, then store each logical output row
  separately when the N tile cannot remain live for its consumer.
- Materialize a graph boundary in guest memory whenever keeping it live would
  exceed scratchpad or cross a separately compiled partition.
- Emit no automatic `BARRIER` in ABI 1.0 because commands are already serial.
- Reuse a scratchpad range only after the prior tensor's last scheduled read.

Overlapped DMA/compute scheduling comes after functional equivalence and uses a
new scheduler version recorded in the manifest.

## Pass 6 — Emit bytes

The emitter consumes scheduled typed commands and follows the
[command ABI](command-abi.md). It does not infer shapes,
allocate memory, or select operators.

Output:

```text
commands.bin
memory.bin
disassembly.txt
allocation.json
manifest.json
```

Repeated compilation with identical input bytes/options must produce identical
outputs and hashes.

The submission addresses, segment roles, and binary-image mapping follow the
[memory and execution model](memory-execution-model.md).
`allocation.json` records tensor, tile, offset, byte count, alignment, birth,
death, and reuse predecessor. `manifest.json` records the graph/input hashes,
compiler and scheduler versions, payload base, quantization approximation,
artifact hashes, and all warnings.

## Pass 7 — Disassemble

Example form:

```text
seq=0000 DMA_LOAD guest=0x0000000000001000 spad=0x0000 bytes=16
seq=0001 DMA_LOAD guest=0x0000000000002000 spad=0x0040 bytes=512
seq=0002 GEMM_I8_I8_I32 A=0x0000 B=0x0040 C=0x0240 M=1 N=32 K=16
...
seq=0008 END
```

The exact text format is stable enough for review fixtures. It should show
tensor names in comments when debug metadata is available, but names are not
part of the binary ABI.

## Pass 8 — Execute and compare

The workload command performs:

```text
generate deterministic input/weights
-> evaluate NumPy reference
-> compile
-> run Python command model
-> run native C++ model
-> compare output bytes
-> save manifest and first-divergence report
```

The Spike path consumes the already-generated command and memory images; it is
not a second compiler.

The planned command-line interface is:

```text
python -m npu_lab compile workloads/mlp/two_layer.json \
  --output out/mlp --payload-base 0x81000000
python -m npu_lab inspect out/mlp/commands.bin
python -m npu_lab compare workloads/mlp/two_layer.json --artifacts out/mlp
```

Each command returns zero only after its complete artifact set is valid.
Compilation writes to a staging directory and publishes outputs atomically;
failure leaves no partial final artifact set.

## Test layers

| Test | Purpose |
|---|---|
| Schema unit tests | Reject malformed graphs |
| Shape tests | Catch rank/dimension/orientation errors |
| Pass golden tests | Make IR changes reviewable |
| Allocator property tests | No overlap for intersecting lifetimes |
| ABI golden tests | Exact bytes |
| Metamorphic tests | Renaming does not change semantics |
| End-to-end MLP | Reference/Python/C++ exact output |
| Determinism test | Same inputs produce same hashes |

## ONNX importer boundary

Add ONNX after the JSON graph succeeds. The importer:

- Pins an opset
- Runs/checks static shape inference
- Maps only an allowlist of operators
- Converts initializers into project tensor records
- Produces the same typed IR
- Emits an unsupported-operator report

It does not allow ONNX-specific objects to leak into scheduling or the device
model.

## Compiler review questions

- Can every emitted command point back to one IR operation?
- Does every byte range have one owner and valid lifetime?
- Is allocation deterministic?
- Are element counts and byte sizes overflow checked?
- Can an unsupported graph fail before creating partial output files?
- Does the disassembler agree with the encoder and decoder?
- Is numerical fusion proven equivalent?
- Are layout copies visible in traffic accounting?

## Primary references

- [ONNX IR specification](https://onnx.ai/onnx/repo-docs/IR.html)
- [ONNX operators](https://onnx.ai/onnx/operators/)
- [ONNX shape inference](https://onnx.ai/onnx/repo-docs/ShapeInference.html)
- [Command buffer ABI](command-abi.md)

## Continue through the specification

Next specification: [Verification plan](verification-plan.md)
