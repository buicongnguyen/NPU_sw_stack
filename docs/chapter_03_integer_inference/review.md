# Chapter 3 summary and review

## Summary

Exact integer inference requires one shared definition of arithmetic. Widening,
rounding, clamping, and legal parameter ranges are part of the interface, not
implementation detail.

## Review questions

1. Why is the accumulator wider than the input tensors?
2. At what point should saturation occur?
3. How can two implementations both look reasonable yet disagree by one?
4. Which extreme inputs are most likely to reveal undefined behavior?
5. Why must cross-language vectors include invalid cases as well as valid ones?

## Deferred lab

Run the same boundary-vector table in Python and C++ with sanitizer-enabled
builds. Record exact mismatches before changing either implementation.
