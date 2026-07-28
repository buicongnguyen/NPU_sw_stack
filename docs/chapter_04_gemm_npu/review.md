# Chapter 4 summary and review

## Summary

GEMM supplies a compact correctness target and a reusable accelerator
primitive. Tiling introduces execution order, storage, and utilization
questions without changing the mathematical result.

## Review questions

1. Why are partial tiles a correctness case rather than only a performance case?
2. Which dimension controls the length of the accumulation?
3. What data should remain resident to reduce memory traffic?
4. How does padding affect utilization but not valid output elements?
5. Should a zero-sized GEMM be legal? Which contract decides?

## Deferred lab

Compare reference and tiled GEMM on square, rectangular, partial-tile, and
zero-dimension inputs. The current zero-dimension contract discrepancy is
already recorded for resolution during executable review.
