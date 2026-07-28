# Static implementation remediation review

Status: **remediated statically; execution and verification deferred**

Date: **2026-07-28**

Scope: the P1/P2 numerical and PowerShell findings recorded in the
[post-deployment static review](post-deployment-code-review-2026-07-28.md).
This review covers source and test intent only. It is not evidence that Python,
C++, Docker, sanitizers, or WSL execution passed.

## Verdict

The actionable contract mismatches found in the initial static review now have
source-level corrections and matching deferred tests. No implementation status
is upgraded: E0 and E1 remain scaffolded until their gates run in the declared
Linux environment.

## Corrections

| Finding | Static correction |
|---|---|
| Extreme finite quantization | Saturate before any wide floating-to-integer conversion; handle division overflow by sign |
| Nonfinite dequantization | Reject a nonfinite result in both Python and C++ |
| Zero-sized GEMM | Reject zero `M`, `N`, or `K` before storage or output arithmetic |
| ABI requantization legality | Require a positive INT32 multiplier and zero output zero point |
| Python input coercion | Reject float, string, Boolean, and other non-integer GEMM arrays before casting |
| Cross-language asymmetry | Define one versioned xorshift32 corpus configuration consumed by both test suites |
| C++ boundary expectation | Use `numeric_limits<int32_t>::min()` instead of an unsigned-to-signed conversion |
| Native command failures | Route required native commands through one exit-code-checking PowerShell helper |
| Controlled failure proof | Add a tooling check that requires child exit code 7 to be propagated |

## Added deferred gates

- Extreme finite input divided by the smallest positive finite scale
- Positive and negative quantization saturation
- Dequantization overflow rejection
- Invalid multiplier and nonzero ABI zero-point rejection
- Named zero-`M`, zero-`N`, and zero-`K` GEMM rejection
- Python float, string, and Boolean GEMM rejection
- A shared 1,000-case seeded GEMM corpus
- PowerShell native-command failure propagation

The corpus configuration is
`tests/fixtures/numerics/gemm-corpus.csv`. Its algorithm identifier, seed,
case count, and dimension limits are repository-owned inputs rather than
language-specific random defaults.

## Remaining gates

The following work still requires the user-approved WSL phase:

1. Run the PowerShell tooling check and Python numerical suite.
2. Build the C++ target with project warnings and sanitizers.
3. Run the C++ corpus and compare the first divergence, if any.
4. Add Linux-native bootstrap/build/test entry points.
5. Record exact tool versions, commands, output, and artifact hashes.

Dependency lock depth and a repository content license remain policy decisions,
not defects silently resolved by this change.
