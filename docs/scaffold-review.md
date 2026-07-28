---
layout: page
title: Static Scaffold Review
permalink: /scaffold-review/
---

# Static scaffold review

Review date: **2026-07-27**, reconciled with the v1 contract on **2026-07-28**

Scope: read-only review of the Phase 0 and numerical source scaffold. No Python
test, C++ build, Docker build, or WSL command was executed after the user chose
the documentation-first checkpoint.

Verdict: **useful scaffold, not yet approved as a verified implementation**

## Priority findings

### S1 — Native command failures can be missed

Priority: **high**

The PowerShell scripts use native programs such as `python`, `pip`, `docker`,
`cmake`, and `ctest`. `$ErrorActionPreference = "Stop"` does not reliably turn
every nonzero native exit code into a terminating error across PowerShell
versions. Some calls check `$LASTEXITCODE`, but others do not, and
`bootstrap.ps1` can print “Bootstrap complete” after a failed native command.

Required correction before E0:

- Wrap native calls consistently.
- Check `$LASTEXITCODE` immediately.
- Stop with the failed command and code.
- Add one test or controlled failure proving the wrapper propagates failure.

### S2 — The randomized cross-language gate is incomplete

Priority: **high**

Python runs 1,000 seeded GEMM cases, while the C++ test consumes only the small
requantization CSV and one known GEMM. This does not yet prove that both
implementations agree on the same randomized GEMMs.

Required correction before E1:

- Generate shared binary/CSV/JSON GEMM vectors once.
- Consume identical vectors in Python and C++.
- Include cases that force partial-sum INT32 wrap, not only small matrices.
- Compare serialized output bytes or hashes.

### S3 — Extreme quantization code does not meet the frozen contract

Priority: **high**

The numerical contract now requires safe saturation when finite quantization
division is unrepresentable and a stable invalid-numeric category when
dequantization cannot produce a finite result. Current Python and C++ behavior
can diverge near INT64 limits, and the C++ boundary comparison uses inexact
`double` representations of those endpoints.

Required correction before E1:

- Implement the already-frozen saturation/error behavior.
- Test the smallest positive finite scale and very large finite values.
- Avoid an out-of-range floating-to-integer conversion.
- Compare stable error categories rather than language exception text.

### S4 — Zero-size GEMM code contradicts the frozen contract

Priority: **medium**

The v1 numerical contract and command ABI reject zero `m`, `n`, and `k`.
Current helpers can still return empty or zero-valued output for some zero
shapes.

Required correction:

- Reject each zero dimension in both reference helpers.
- Add named tests for each zero dimension.

### S5 — Linux-native entry points do not exist yet

Priority: **medium**

The preferred future environment is Ubuntu under WSL2, but the scaffold
currently exposes only PowerShell scripts and a Docker C++ path. The setup guide
correctly marks this as deferred.

Required correction during WSL setup:

- Add Linux-native bootstrap/build/test scripts or portable task commands.
- Add a Linux documentation checker or a documented PowerShell interop
  requirement.
- Run both local and CI paths before claiming E0.

### S6 — Package and action pinning policy is mixed

Priority: **medium**

Python packages and the Ubuntu Docker base are pinned, but apt packages float
within the pinned base metadata, pip itself is not frozen, and GitHub Actions
use major-version tags rather than immutable commit SHAs.

Required decision:

- Define which dependencies require bit-for-bit pinning.
- Record package versions in evidence even when update ranges are accepted.
- Consider commit-SHA action pins if supply-chain reproducibility is a project
  requirement.

### S7 — Entirely untracked trees evade `git diff --check`

Priority: **medium**

The local repository was initialized but has no tracked baseline. A successful
`git diff --check` therefore does not inspect the untracked files. The custom
documentation checker does inspect Markdown/YAML whitespace, but this is not a
general source-tree check.

Required correction before the first commit:

- Review `git status --short`.
- Run language formatters/checkers that read untracked files directly.
- After intentionally staging the first commit, inspect `git diff --cached
  --check`.

### S8 — Numerical test coverage is narrower in C++

Priority: **medium**

C++ lacks named invalid-argument, shape-overflow, zero-dimension, and extreme
rounding cases present or implied in the Python suite and plan.

Required correction:

- Build a shared test matrix organized by contract rule.
- Ensure both languages cover success and rejection behavior.
- Add sanitizer execution after the test content is complete.

## Non-blocking observations

- C++ signed overflow is avoided in the explicit `wrap_i32` path.
- The numerical contract correctly names ties-to-even and little-endian output.
- The CMake target isolates the numerical library and enables warnings.
- The Docker base uses a digest, which is better than a floating image tag.
- The CI sequence separates Python, C++, and documentation checks.
- The native NPU, ABI, compiler, and Spike code do not exist yet, so their code
  review remains future work.

## Review gate before implementation resumes

When WSL2 is ready:

1. Fix S1 so failed tools cannot report success.
2. Freeze the extreme/empty numerical rules from S3/S4.
3. Add Linux-native commands from S5.
4. Execute focused numerical tests.
5. Complete shared cross-language vectors from S2/S8.
6. Save actual versions and outputs.
7. Update statuses from `scaffolded` to `verified` only after the gate passes.
