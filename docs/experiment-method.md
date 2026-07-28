---
layout: page
title: Experiment and Evidence Method
permalink: /experiment-method/
---

# Experiment and evidence method

This project is a lab notebook as much as a codebase. A result is trustworthy
only when another reader can reproduce it and understand what it does—and does
not—prove.

## Begin with a falsifiable question

Good:

> Does the 8x8 timing model predict fewer estimated cycles for a 64x64 GEMM
> than a 16x16 GEMM while producing identical functional values?

Weak:

> Test performance.

State one independent variable, the measurements, and the expected invariant.

## Freeze the experiment identity

Record:

```yaml
experiment_id: E2-abi-roundtrip-001
git_revision: FULL_COMMIT_SHA
date_utc: YYYY-MM-DDTHH:MM:SSZ
environment:
  os: ...
  python: ...
  compiler: ...
  spike: ...
model:
  source: ...
  revision: ...
  sha256: ...
parameters:
  seed: 0
  shape: [1, 3, 320, 320]
  layout: NCHW
```

Never use only a human-readable filename as the identity of weights, exported
graphs, or datasets. Include a cryptographic hash.

## Keep truth sources separate

| Claim | Required evidence |
|---|---|
| Scalar arithmetic is correct | Hand-calculated named cases |
| Implementation is bit-exact | Shared Python/C++ golden vectors |
| Graph lowering is correct | Intermediate tensor comparisons |
| ABI is stable | Golden bytes and malformed-buffer tests |
| RV64 integration works | Same command hash/output under native and Spike paths |
| Timing estimate is useful | Stated equations and sensitivity tests |
| Timing is accurate | Correlation against RTL or measured hardware |
| Model accuracy is acceptable | Dataset, metric, baseline, and quantized result |

## Directory convention

Generated evidence is not committed by default:

```text
out/evidence/
  E1-numerics/
    manifest.json
    pytest.txt
    ctest.txt
    vectors.json
  E7-yolov8n/
    manifest.json
    operator-coverage.csv
    tensor-errors.csv
    performance.json
```

Small reviewed tables used by the public site may be copied to:

```text
docs/assets/data/
```

The article must name the generating command and source revision.

## Comparison rules

Choose the rule before seeing the result:

- Integer ABI/model tests: exact equality
- Command buffers: byte equality and SHA-256 equality
- FP32 operator references: explicit absolute/relative tolerance
- Quantized tensor studies: exact integer equality plus real-domain error
- Detection accuracy: fixed dataset split and named metric
- Performance: fixed architecture parameters and inclusion boundary

For floating-point tensors, record at least:

```text
max_abs_error
max_rel_error
mean_abs_error
cosine_similarity
first_failing_index
reference_value
observed_value
```

Do not use cosine similarity alone; it can hide a large local error.

## Performance accounting boundary

Every performance result must say whether it includes:

- Graph import/compile time
- Weight loading
- Host-to-device and device-to-host traffic
- NPU compute
- Host fallback
- Decode and NMS
- Simulator overhead

Report simulator wall-clock time separately from simulated or estimated target
cycles.

## Failure reporting

A useful failure record contains:

1. Smallest reproducer
2. Exact command
3. Expected result
4. Observed result
5. First divergent boundary
6. Root cause, if known
7. Fix or remaining hypothesis
8. Regression test

Failed approaches are valuable evidence. Preserve the explanation, not large
unreviewed logs.

## Progress article structure

Each dated post should use:

```text
Objective
Context and versions
Hypothesis
Design or implementation
Reproduction commands
Expected output
Observed evidence
Failure or boundary case
Interpretation
Decision
Next gate
References
```

Start from `docs/_drafts/progress-entry-template.md` in the repository.

## Review checklist

Before publishing:

- The commit is clean or working-tree status is disclosed.
- Dependency/model/dataset versions are explicit.
- Random seeds and shapes are explicit.
- Commands can be copied without hidden shell state.
- Expected outputs are labeled as examples until observed.
- Generated values are not presented as measured values.
- Host fallback and transfers are visible.
- Personal paths, credentials, and licensed assets are absent.
- Links point to primary sources where possible.
- The next gate is small and testable.
