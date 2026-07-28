# Chapter 3: Exact integer inference

Integer inference is not merely “floating point with smaller storage.” Results
depend on widening, accumulation, scaling, rounding, saturation, and overflow
rules. Those choices must match across Python, C++, the compiler, and hardware.

## Learning goals

- trace an INT8 operation through a wider accumulator;
- distinguish quantization parameters from tensor data;
- explain why rounding and saturation order is normative;
- recognize boundary cases that require dedicated vectors.

## Numerical pipeline

```mermaid
flowchart LR
  A["INT8 activation"] --> M["Widen and multiply"]
  W["INT8 weight"] --> M
  M --> ACC["Wide accumulator"]
  ACC --> B["Bias / zero-point correction"]
  B --> Q["Requantize and round"]
  Q --> S["Saturate to output type"]
```

The prose contract is the authority. Code is an implementation of that
contract, and discrepancies must be resolved explicitly.

## Reading path

1. Study the [numerical contract](../numerical-contract.md).
2. Work through the
   [integer inference lesson](../lessons/01-integer-inference.md).
3. Review the boundary cases in [this chapter’s questions](review.md).

!!! note "Static review finding"
    Source-level corrections and matching vectors now cover the reviewed
    extreme-quantization cases. Execution with sanitizers remains pending
    until WSL setup. See the
    [remediation review](../project/static-remediation-review-2026-07-28.md).
