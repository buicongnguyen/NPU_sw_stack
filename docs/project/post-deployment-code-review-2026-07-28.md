# Post-deployment static code review

Status: **reviewed statically; implementation fixes remain deferred**

Review date: **2026-07-28**

Reviewed baseline: [`3b08e96`](https://github.com/buicongnguyen/NPU_sw_stack/commit/3b08e96a591707823c7f5b57c0d7457f2513d834)

Scope: C++ and Python numerical helpers, numerical tests and fixtures,
PowerShell entry points, documentation validation, and GitHub workflows.

No Python numerical test, C++ build, sanitizer, Docker build, WSL command,
Spike run, model inference, timing model, or RTL simulation was executed.

## Verdict

No P0 defect was found. The three unresolved P1 implementation findings from
the initial review remain valid. Repository-side validation gaps found in this
review can be fixed safely without changing numerical behavior.

## P1 implementation findings

### C1 — Extreme quantization still risks divergent or unsafe behavior

`quantize_s8` in Python can receive a finite quotient that overflows to
infinity before `round`. The C++ boundary check represents INT64 endpoints as
inexact `double` values and can reach an out-of-range floating-to-integer
conversion. `dequantize_s8` in both languages can return infinity.

Required after WSL setup:

- implement the frozen saturation/error rules without unsafe conversion;
- add extreme finite, quotient-overflow, and dequantization-overflow vectors;
- compare stable error categories across Python and C++.

### C2 — Zero-sized GEMM remains accepted below an ABI that rejects it

The v1 numerical and command contracts reject zero `M`, `N`, or `K`. Current
Python/C++ helpers can return empty or zero-valued output for some zero shapes.

Required after WSL setup: reject each zero dimension and add matching language
tests.

### C3 — Native command failures can still be reported as success

`bootstrap.ps1`, `build.ps1`, and the final Docker/CTest path in `test.ps1` do
not check every native exit code immediately. `$ErrorActionPreference = "Stop"`
does not make this reliable across PowerShell versions.

Required after WSL setup: centralize native invocation, report command and exit
code, and prove propagation with a controlled failure.

## P2 implementation and test findings

### C4 — Requantization helper inputs remain broader than ABI 1.0

Python accepts arbitrary integer-like multipliers and zero points; C++ accepts
non-positive multipliers and nonzero zero points. Decide whether these are
general teaching helpers or ABI-specific entry points.

### C5 — Python silently coerces invalid input categories

`np.asarray(..., dtype=np.int64)` and explicit `int(...)` calls can accept
floats or numeric strings before validation. Validate type/category before
conversion.

### C6 — Cross-language evidence remains asymmetric

Python owns randomized GEMM coverage while C++ consumes a small requantization
fixture and one known GEMM. Create one versioned shared corpus for valid and
invalid cases.

### C7 — One C++ boundary assertion is implementation-sensitive

The C++ test converts unsigned `0x80000000U` to signed INT32 for its expected
value. Replace that conversion with `std::numeric_limits<std::int32_t>::min()`
when implementation work resumes.

### C8 — Dependency pinning is not a complete lock

Top-level documentation packages and action release tags are pinned, but
transitive Python packages and Actions are not immutable. Define an update and
pinning policy before claiming bit-for-bit reproducibility.

## Repository-side findings resolved by this change

### R1 — All YAML-family configuration should fail locally when malformed

Resolution: parse `.yml`, `.yaml`, and `.cff` through the documentation checker.

### R2 — Every book page should be intentionally navigable

Resolution: compare all `docs/**/*.md` paths with the explicit MkDocs nav.

### R3 — HTML-authored local links were outside link validation

Resolution: validate local `href` and `src` attributes in addition to Markdown
links.

### R4 — Documentation checks should follow their actual input surface

Resolution: expand workflow path filters to root Markdown, citation metadata,
and GitHub community/workflow files.

## Gate after WSL setup

1. Fix C1–C3 before accepting E0/E1.
2. Freeze C4 behavior.
3. Add type rejection and shared vectors for C5–C7.
4. Run Python, C++, sanitizer, and controlled script-failure gates.
5. Record tool versions and immutable outputs before changing status.
