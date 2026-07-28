---
layout: page
title: Command Buffer ABI
permalink: /command-abi/
---

# Command buffer ABI

Status: **ABI 1.0 normative design; implementation unverified**

This document defines the bytes exchanged between the compiler/runtime and the
functional NPU model. It is intentionally independent of C/C++ structure
layout.

## Design goals

- Deterministic, little-endian encoding
- Fixed-width integer fields
- Simple validation before execution
- Forward-compatible version and reserved fields
- 16-byte command alignment
- Identical bytes in native and Spike paths
- Easy disassembly and malformed-buffer testing

Version 1 supports a two-layer quantized MLP. Convolution and advanced
operators may add later commands without changing valid version-one buffers.

## Scalar encoding rules

- `u8`, `u16`, `u32`, and `u64` are unsigned fixed-width integers.
- `i8` and `i32` use two's-complement encoding.
- Multi-byte values are little-endian.
- Every reserved field is written as zero and rejected if nonzero.
- Commands begin at 16-byte-aligned offsets from the start of the buffer.
- All sizes and offsets are measured in bytes.
- The byte stream is built field by field; native structs are never copied.

## Buffer header

The buffer begins with 32 bytes:

| Offset | Size | Field | Version-one rule |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `NPUC` |
| 4 | 2 | `major` | `1` |
| 6 | 2 | `minor` | `0` |
| 8 | 4 | `header_bytes` | `32` |
| 12 | 4 | `total_bytes` | Entire buffer size |
| 16 | 4 | `command_count` | Includes `END` |
| 20 | 4 | `flags` | `0` |
| 24 | 8 | `reserved` | `0` |

`total_bytes` must be a multiple of 16, at least 48, and no larger than the
v1 limit of 1,048,576 bytes. The MMIO `CMD_BYTES` value must equal
`total_bytes`, and the submitted guest address is 16-byte aligned.

Version-one compatibility policy is exact: a version 1.0 device accepts only
`major=1, minor=0`. A future device may accept older minor versions within its
major version, but this first implementation does not silently accept an
unknown minor version.

## Common command header

Every command starts with:

| Relative offset | Size | Field |
|---:|---:|---|
| 0 | 2 | `opcode` |
| 2 | 2 | `flags` |
| 4 | 4 | `record_bytes` |
| 8 | 4 | `sequence` |
| 12 | 4 | `reserved` |

Rules:

- `record_bytes` is at least 16 and a multiple of 16.
- `sequence` begins at zero and increases by one.
- Version-one `flags` and `reserved` are zero unless a command explicitly
  defines a flag.
- `offset + record_bytes` is checked for integer overflow and buffer bounds.
- The final counted command is exactly one `END`.

## Opcodes

| Value | Name | Record bytes |
|---:|---|---:|
| `0x0001` | `DMA_LOAD` | 32 |
| `0x0002` | `DMA_STORE` | 32 |
| `0x0010` | `GEMM_I8_I8_I32` | 48 |
| `0x0011` | `ADD_BIAS_I32` | 32 |
| `0x0012` | `RELU_I32` | 32 |
| `0x0013` | `REQUANTIZE_I32_I8` | 48 |
| `0x00f0` | `BARRIER` | 16 |
| `0x00ff` | `END` | 16 |

Unknown opcodes are errors. A later minor version may add an opcode only when
an older device rejects it safely.

## DMA commands

`DMA_LOAD` copies guest memory into scratchpad. `DMA_STORE` copies scratchpad
into guest memory.

| Relative offset | Size | Field |
|---:|---:|---|
| 16 | 8 | `guest_address` |
| 24 | 4 | `scratchpad_offset` |
| 28 | 4 | `byte_count` |

Validation:

- `byte_count` is nonzero.
- Guest `address + byte_count` cannot overflow and is accessible.
- Scratchpad `offset + byte_count` cannot overflow and fits.
- Source and destination ranges may not alias because they belong to different
  address domains.
- A guest DMA range may not overlap the submitted command-buffer range.
- The complete destination is committed or the command fails without a
  partial write.

Version one models byte copies and does not require burst alignment. Timing
parameters may penalize unaligned accesses without changing functional bytes.

## INT8 GEMM command

The operation is:

```text
C[m,n] = sum_k(A[m,k] * B[k,n])
```

Inputs are signed INT8 and output is signed INT32.

| Relative offset | Size | Field |
|---:|---:|---|
| 16 | 4 | `a_offset` |
| 20 | 4 | `b_offset` |
| 24 | 4 | `c_offset` |
| 28 | 2 | `m` |
| 30 | 2 | `n` |
| 32 | 2 | `k` |
| 34 | 2 | `reserved0` |
| 36 | 4 | `lda_bytes` |
| 40 | 4 | `ldb_bytes` |
| 44 | 4 | `ldc_bytes` |

Version-one matrices are row-major and not transposed. Leading dimensions are
byte strides between rows.

Validation:

- `m`, `n`, and `k` are nonzero.
- `lda_bytes >= k`.
- `ldb_bytes >= n`.
- `ldc_bytes >= 4*n`.
- The last addressed byte of A, B, and C fits in scratchpad.
- C begins at 4-byte alignment.
- A and B may overlap because they are read-only.
- C may not overlap either input in version one.

For a row-strided matrix with `rows`, row payload `row_bytes`, and
`stride_bytes`, the final byte is checked as:

```text
base + (rows - 1) * stride_bytes + row_bytes - 1
```

Every multiplication and addition in that expression is checked before use.
Overlap is evaluated over the addressed row intervals, including padding gaps
only when another operand actually addresses them.

Arithmetic follows the [numerical contract](numerical-contract.md).

## INT32 bias command

Add one bias per output column in place:

```text
data[row,col] += bias[col]
```

| Relative offset | Size | Field |
|---:|---:|---|
| 16 | 4 | `data_offset` |
| 20 | 4 | `bias_offset` |
| 24 | 2 | `rows` |
| 26 | 2 | `cols` |
| 28 | 4 | `data_stride_bytes` |

Both tensors are little-endian INT32 and 4-byte aligned. Addition uses the same
documented INT32 overflow rule as accumulation.

Validation:

- `rows` and `cols` are nonzero.
- `data_stride_bytes >= 4*cols` and is a multiple of four.
- `data_offset` and `bias_offset` are 4-byte aligned.
- Every data row and the `4*cols` bias range fit in scratchpad using checked
  arithmetic.
- The bias range does not overlap an addressed data row.
- All data and bias bytes were initialized earlier in the submission.

## INT32 ReLU command

Apply `max(x, 0)` in place:

| Relative offset | Size | Field |
|---:|---:|---|
| 16 | 4 | `data_offset` |
| 20 | 4 | `element_count` |
| 24 | 2 | `dtype` |
| 26 | 2 | `reserved0` |
| 28 | 4 | `reserved1` |

Version one defines `dtype=1` as INT32.

Validation:

- `element_count` is nonzero and `dtype` is exactly `1`.
- `4*element_count` is checked for overflow and the full range fits.
- `data_offset` is 4-byte aligned and all source bytes are initialized.
- Reserved fields are zero.

## Requantization command

Convert INT32 values to INT8:

```text
scaled = round_ties_to_even(src * multiplier / 2^shift)
shifted = scaled + zero_point
dst = clamp(shifted, clamp_min, clamp_max)
```

| Relative offset | Size | Field |
|---:|---:|---|
| 16 | 4 | `src_offset` |
| 20 | 4 | `dst_offset` |
| 24 | 4 | `element_count` |
| 28 | 4 | `multiplier` (`i32`) |
| 32 | 4 | `shift` (`i32`) |
| 36 | 4 | `zero_point` (`i32`) |
| 40 | 1 | `clamp_min` (`i8`) |
| 41 | 1 | `clamp_max` (`i8`) |
| 42 | 2 | `reserved0` |
| 44 | 4 | `reserved1` |

Version one requires:

- `element_count > 0`
- `multiplier` in `[1, INT32_MAX]`
- `0 <= shift <= 62`
- `zero_point = 0`
- `clamp_min <= clamp_max`
- 4-byte-aligned source and fully checked source/destination ranges
- Initialized source bytes
- No source/destination byte overlap

The INT8 destination has no alignment requirement. Exact intermediate overflow
behavior is defined by the numerical contract.

## Barrier and end

`BARRIER` has no payload. In the initially synchronous functional model it
does not change output, but it defines a scheduling boundary for a future
asynchronous DMA/compute timing model.

`END` has no payload and must be the final command. Bytes after `END` are
invalid because `total_bytes` must end at the record boundary.

`BARRIER` and `END` reject nonzero flags or reserved fields. Completion of
either increments `COMMANDS_DONE`; a failing command never increments it.

## Two-pass validation

The device validates before mutating architectural state:

At accepted `START`, the device snapshots exactly `CMD_BYTES` command bytes.
Both validation passes and execution read this immutable snapshot. Tensor
payloads are not snapshotted and follow the
[memory and execution model](memory-execution-model.md).

### Pass 1 — structural

1. Validate header magic, version, flags, and sizes.
2. Walk exactly `command_count` records.
3. Validate record sizes, alignment, sequence, and reserved fields.
4. Require one final `END`.
5. Reject trailing or missing bytes.

### Pass 2 — semantic

1. Validate opcodes and command-specific fields.
2. Check all scratchpad ranges and alignments.
3. Check guest ranges through the adapter.
4. Check dimension/stride arithmetic for overflow.
5. Check prohibited overlaps.

Only after both passes succeed may execution begin. A later asynchronous model
may still report runtime DMA faults, but structurally invalid buffers cannot
partially execute.

Within each pass, checks occur in sequence order and in the bullet order given
for that command. The first failing rule determines the stable error code and
command sequence. Header errors use the sentinel command index
`0xffff_ffff`. Numeric codes and reset defaults are frozen in the
[MMIO/runtime contract](mmio-runtime.md).

## Exact validation precedence

This table, rather than prose bullet order, selects the first error when a
buffer violates multiple rules. Rows are evaluated top to bottom; command rows
are repeated in sequence order. Checks within a row that share a code need no
further ordering.

| Order | Scope and check | Error code |
|---:|---|---|
| 1 | `CMD_BYTES` is zero, below 48, or not a multiple of 16 | `START_CONFIG_INVALID` |
| 2 | `CMD_BYTES` exceeds `MAX_CMD_BYTES` | `COMMAND_TOO_LARGE` |
| 3 | Command guest address is not 16-byte aligned | `ALIGNMENT_INVALID` |
| 4 | Command range overflows, is unreadable, or snapshot read fails | `GUEST_RANGE_INVALID` |
| 5 | Header magic | `BAD_MAGIC` |
| 6 | Header major/minor | `UNSUPPORTED_COMMAND_ABI` |
| 7 | `header_bytes` | `BAD_HEADER_SIZE` |
| 8 | Header `total_bytes` mismatch/limit/alignment | `BAD_TOTAL_SIZE` |
| 9 | Zero or impossible `command_count` | `BAD_COMMAND_COUNT` |
| 10 | Header flags or reserved bytes | `NONZERO_RESERVED` |
| 11 | Common header unavailable; generic record size/alignment/bounds | `BAD_RECORD_SIZE` |
| 12 | Sequence value | `BAD_SEQUENCE` |
| 13 | Common flags or reserved bytes | `NONZERO_RESERVED` |
| 14 | Counted walk does not consume exactly `total_bytes` | `TRAILING_OR_MISSING_BYTES` |
| 15 | Final record is not the only final `END` | `BAD_END` |
| 16 | Opcode is unknown | `UNKNOWN_OPCODE` |
| 17 | Known opcode has the wrong exact record size | `BAD_RECORD_SIZE` |
| 18 | DMA `byte_count` is zero | `ZERO_LENGTH_DMA` |
| 19 | DMA guest range overflow/map/permission/command overlap | `GUEST_RANGE_INVALID`, then `OPERAND_OVERLAP` |
| 20 | DMA scratchpad range | `SCRATCHPAD_RANGE_INVALID` |
| 21 | GEMM zero/unrepresentable dimensions | `INVALID_DIMENSION` |
| 22 | GEMM leading dimensions | `INVALID_STRIDE` |
| 23 | GEMM C alignment | `ALIGNMENT_INVALID` |
| 24 | GEMM A, then B, then C ranges | `SCRATCHPAD_RANGE_INVALID` |
| 25 | GEMM C overlap with A, then B | `OPERAND_OVERLAP` |
| 26 | GEMM A, then B initialization | `UNINITIALIZED_SCRATCHPAD` |
| 27 | Bias zero dimensions | `INVALID_DIMENSION` |
| 28 | Bias stride | `INVALID_STRIDE` |
| 29 | Bias data, then bias alignment | `ALIGNMENT_INVALID` |
| 30 | Bias data, then bias ranges | `SCRATCHPAD_RANGE_INVALID` |
| 31 | Bias/data overlap | `OPERAND_OVERLAP` |
| 32 | Bias data, then bias initialization | `UNINITIALIZED_SCRATCHPAD` |
| 33 | ReLU zero element count | `INVALID_DIMENSION` |
| 34 | ReLU dtype | `INVALID_DTYPE` |
| 35 | ReLU alignment, range, initialization | `ALIGNMENT_INVALID`, then `SCRATCHPAD_RANGE_INVALID`, then `UNINITIALIZED_SCRATCHPAD` |
| 36 | Requantization count/multiplier/shift/zero point/clamp | `INVALID_REQUANTIZATION` |
| 37 | Requantization source alignment | `ALIGNMENT_INVALID` |
| 38 | Requantization source, then destination ranges | `SCRATCHPAD_RANGE_INVALID` |
| 39 | Requantization overlap | `OPERAND_OVERLAP` |
| 40 | Requantization source initialization | `UNINITIALIZED_SCRATCHPAD` |

For table rows that list several codes, checks and codes are paired left to
right. Semantic prevalidation simulates initialization effects in command
order without mutating architectural scratchpad bytes.

## Required malformed fixtures

Create one named fixture for each:

- Wrong magic
- Unsupported major/minor policy
- Header smaller/larger than version one
- `total_bytes` underflow, overflow, or nonalignment
- Wrong command count
- Zero/small/nonaligned record size
- Sequence gap
- Unknown opcode
- Nonzero reserved field
- Missing/multiple/nonfinal `END`
- Scratchpad range overflow
- Guest-address overflow
- Invalid GEMM dimension/stride
- Unaligned INT32 tensor
- Invalid requantization shift/clamp
- Command/tensor guest-range overlap
- Read of uninitialized scratchpad bytes
- Prohibited scratchpad operand overlap
- Compound-invalid records that prove the precedence table

Python and C++ must return the same stable error code and failing command index.

## Golden fixture workflow

One canonical Python generator emits:

```text
tests/fixtures/abi/mlp-v1.commands.bin
tests/fixtures/abi/mlp-v1.disassembly.txt
tests/fixtures/abi/mlp-v1.manifest.json
```

The manifest records:

- ABI version
- Buffer length
- Command count
- SHA-256
- Generator command and revision
- Human-readable tensor allocation

Both languages parse and re-encode the fixture. Re-encoded bytes must be
identical, not merely semantically equivalent.

## Change policy

- Clarification without byte changes edits this document and tests.
- Backward-compatible new commands increment the minor version.
- Reinterpreting an existing field or command increments the major version.
- Every ABI change updates golden bytes, disassembly, malformed cases, runtime
  headers, and the progress article in one reviewed change.

## Continue through the specification

Next specification: [Memory and execution model](memory-execution-model.md)
