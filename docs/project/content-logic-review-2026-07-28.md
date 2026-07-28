# Book content and logic review

Status: **reviewed; confirmed content defects corrected**

Date: **2026-07-28**

Scope: reader sequence, document authority, implementation status, numerical
and command boundaries, memory layout, compiler lowering, and cross-page
navigation. This is a documentation review; no implementation gate was run.

## Verdict

No documentation P0 was found. Two P1 compiler/ABI logic gaps and five P2
reader/status inconsistencies were confirmed and corrected. The resulting book
has one dependency order and now explains how every allowed v1 tiled transfer
can be represented by the existing contiguous DMA commands.

## Findings and resolutions

### L1 — Chapter and lesson orders disagreed

The chapter book taught commands, compiler, and runtime before convolution,
while the learning path put convolution first. Its convolution gate required a
compiler that the reader had not built yet.

**Resolution:** Make the chapter dependency graph canonical:

```text
baseline -> integers -> GEMM -> commands/native device
-> compiler -> runtime/Spike -> convolution -> tiny CNN
```

Add a missing commands/memory/native-device lesson. Treat convolution and tiny
CNN as Lessons 6A and 6B after the platform exists.

The compiler lesson now consumes the already-frozen ABI instead of telling the
reader to define it a second time.

### L2 — The native device had no guided implementation lesson

The plans required a native model before compiler and Spike integration, but
the course jumped from GEMM directly to convolution/compiler.

**Resolution:** Add Lesson 3 with explicit byte encoding, two-pass validation,
checked guest memory, scratchpad initialization, native execution, failure
atomicity, reset, and matching-language gates.

### L3 — In-place bias aliasing was undefined

The compiler design handled ReLU's in-place ABI behavior but omitted
`ADD_BIAS_I32`, even though the command also mutates its input buffer.

**Resolution:** Define a compiler-private unbiased accumulator, mandatory
scratchpad coalescing into the declared Linear output, lifetime transitions,
alias-map evidence, and out-of-place requantization.

### L4 — N tiling could not be emitted as described

An N-column slice of row-major B is noncontiguous, and a compact output tile
cannot be stored as one contiguous full-tensor range. The compiler plan allowed
N tiling without specifying either transformation.

**Resolution:** Require deterministic compile-time packing for immutable
weight tiles, record tile provenance in the manifest, and emit one output
`DMA_STORE` per logical row slice when N is tiled. Include those row stores in
the command-buffer size gate. Dynamic inputs are not silently repacked by the
device.

### L5 — Historical review text looked current

Chapter reviews still called already-remediated numerical, zero-dimension, and
PowerShell findings unresolved.

**Resolution:** Describe source remediation as complete while keeping
execution and WSL verification pending.

### L6 — “Next” links conflicted with book navigation

Normative pages linked directly to the next specification and called it
“Next,” even when chapter navigation placed lessons and reviews between them.

**Resolution:** Label those links **Next specification**. The sidebar and
previous/next footer remain the authority for book order.

### L7 — Initial publication identity looked like the current revision

The specification map labeled the immutable first-publication commit and run as
the generic reviewed deployment even after later deployments.

**Resolution:** Label both records as the **initial publication baseline** and
state that later deployments are identified by `main` history and their own
workflow runs.

## Remaining evidence boundary

- Documentation navigation, links, configuration, and strict rendering may be
  checked now.
- Python/C++, native model, Docker, WSL, Spike, timing, and RTL behavior remain
  unverified until their named gates execute.
- This review corrects intended behavior; it does not claim the intended
  behavior is implemented.
