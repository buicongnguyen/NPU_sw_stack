# Static code and repository review

Status: **reviewed statically; fixes and execution deferred**

Date: **2026-07-28**

Scope: current Python/C++ numerical scaffolds, tests, PowerShell scripts,
build/CI files, documentation tooling, and publication readiness.

Follow-up: the deployed tree received a
[post-deployment static review](post-deployment-code-review-2026-07-28.md).

No Python test, C++ build, Docker build, WSL command, sanitizer, or simulator
was executed for this review.

## Verdict

No P0 issue was found. Four P1 implementation defects and several P2 contract,
test, tooling, and repository-hygiene gaps must be resolved before E0/E1 can be
verified. They do not block a documentation-only website release because the
site labels the code unverified.

## P1 findings

### C1 — Extreme finite quantization can violate the contract and C++ safety

The numerical contract requires safe saturation when a finite `real/scale`
division overflows. `src/numerics.cpp` instead checks a rounded
`double(INT64_MAX)` boundary before converting to INT64. A value at the rounded
`2^63` boundary can reach an out-of-range floating-to-integer conversion.
Other huge finite inputs throw rather than saturate.

Both Python and C++ dequantization can return infinity, although the normative
contract assigns an invalid-numeric category to an unrepresentable result.

Required later fix:

- Compare against safe saturation thresholds before integer conversion.
- Avoid representing INT64 endpoints as inexact doubles.
- Make Python/C++ saturation or error categories identical.
- Add extreme finite, division-overflow, and dequantization-overflow vectors.

### C2 — Zero-sized GEMM contradicts the normative v1 contract

The contract rejects zero `M`, `N`, or `K`. Current Python and C++ helpers can
accept zero-shaped storage and return empty or zero-valued outputs.

Required later fix:

- Reject each zero dimension in both languages.
- Add one named case per dimension.
- Keep ABI and helper behavior aligned.

### C3 — Native PowerShell failures may be reported as success

`$ErrorActionPreference = "Stop"` does not consistently convert nonzero native
program exits into terminating PowerShell errors. Bootstrap/build/test scripts
do not check every `pip`, `docker`, `cmake`, and `ctest` result immediately, so
`bootstrap.ps1` can print success after a failed command.

Required later fix:

- Add one shared native-command wrapper.
- Check and report the exact command/exit code.
- Add a controlled failure-propagation test.
- Provide Linux-native entry points when WSL work begins.

### C4 — Automatic implementation CI would overtake the declared phase

The existing CI runs Python/C++/sanitizer gates on every push to `main`, while
the project says these gates have not been reviewed in the intended WSL
environment.

Documentation-release fix:

- Make implementation CI manual until the environment phase resumes.
- Run a separate automatic documentation build/deploy workflow.
- Record the first CI result as an observation before changing implementation
  status.

Resolution status: **implemented for the documentation release**. The
implementation workflow is manual and the Pages workflow is independent.

## P2 findings

### C5 — Requantization helper legality is broader than ABI 1.0

The contract requires a positive INT32 multiplier and device zero point zero.
Python accepts arbitrary-size integers and C++ accepts zero/negative
multipliers and nonzero signed-INT8 zero points.

Decision for E1: either narrow public helpers to ABI 1.0 or name a general
teaching helper separately from the ABI function.

### C6 — Python GEMM silently coerces non-integer inputs

`np.asarray(..., dtype=np.int64)` converts floats and numeric strings before
range validation. This can hide invalid compiler/reference inputs.

Required later fix: validate integer type/category before conversion.

### C7 — Cross-language evidence is asymmetric

Python has 1,000 seeded GEMMs; C++ consumes one GEMM and the shared
requantization CSV. Neither language covers all newly frozen rejection rules.

Required later fix: generate one versioned shared corpus and consume identical
cases in both languages.

### C8 — The existing documentation checker is tied to Jekyll

It scans ignored/generated directories and checks YAML delimiters without
actually parsing YAML. A malformed configuration can pass while generated
third-party Markdown can fail the check.

Documentation-release fix:

- Restrict discovery to repository-owned files.
- Parse `mkdocs.yml`.
- Validate nav targets, Markdown links, placeholders, and leftover Liquid.
- Use `mkdocs build --strict` as the final site gate.

Resolution status: **implemented** in `scripts/check_docs.py` and the Pages
workflow.

### C9 — The scaffold review contains stale open decisions

Its extreme-quantization and zero-GEMM findings still say the behavior must be
decided, while the numerical contract now decides both.

Documentation-release fix: restate them as code-versus-contract defects.

Resolution status: **implemented** in the scaffold review; executable fixes
remain deferred.

### C10 — Supply-chain reproducibility is incomplete

Actions, runners, apt packages, and pip transitive dependencies are not all
immutably pinned. This is a documented risk, not evidence of compromise.

Required later fix: choose a pin/update policy and record resolved versions in
evidence manifests.

### C11 — Public repository policy files are missing

The initial tree lacks contribution, security, conduct, citation, editor, and
attribute policies. It also lacks a license.

Documentation-release fix: add operational policy files. Do not select a
license without the repository owner's explicit choice.

Resolution status: **partially implemented**. Contribution, conduct, security,
editor, attribute, issue, and pull-request policies are present. A citation
file and content license remain owner decisions; the README states the current
copyright position.

## Positive observations

- C++ avoids direct signed-overflow dependence in the explicit `wrap_i32`
  implementation.
- GEMM size arithmetic contains several checked-overflow guards.
- Numerical fixtures and Python tests are deterministic.
- Project code warnings and sanitizer options are already represented in CMake.
- The design documents accurately separate functional, timing, and RTL truth.

## Review gate after WSL setup

1. Fix C1–C3 and freeze C5 behavior.
2. Add shared invalid and randomized vectors for C2/C5–C7.
3. Run Python/C++ tests and sanitizers in the recorded environment.
4. Review the resulting diff and first divergent case.
5. Update statuses only from saved evidence.
