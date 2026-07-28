# Visual content review

Status: **reviewed; high-value diagrams added**

Date: **2026-07-28**

Scope: explanatory flow, state changes, serialization hierarchy, memory
ownership, compiler lifetime/tiling logic, verification order, and application
partitioning. The diagrams explain existing reviewed contracts; they do not add
new implementation behavior or execution evidence.

## Selection rule

A diagram was added only when the reader must follow at least three dependent
steps, distinguish multiple branches, or understand ownership/aliasing across
components. Tables remain tables when exact fields or comparisons matter more
than flow. Short procedures remain prose.

## Added visuals

| Page | Visual | Reader question answered |
|---|---|---|
| Architecture walkthrough | Build-time/run-time component flow | Which artifacts and components connect the graph to the NPU? |
| Learning path | Prerequisite spine and post-foundation branch diagrams | What must be learned before convolution, YOLO, and optional branches? |
| Command-buffer ABI | Serialized record hierarchy and two-pass validation | What is inside a buffer, and when can execution begin? |
| Memory/execution model | Address ownership and failure atomicity | Which address space owns each value, and what survives a failure? |
| Compiler design | In-place lifetime aliases and N-tile movement | Which logical values share bytes, and why are weights packed/output rows stored separately? |
| MMIO/runtime contract | Device state machine | Which transitions require `START`, `RESET`, or an error? |
| Verification plan | Evidence ladder in two linked stages | Which oracle must pass before a later integration claim matters? |
| YOLO target | Official-export versus deployment-partition boundary | Which artifact proves framework equivalence, and which one feeds the NPU/host split? |

## Supplemental audit

A second pass covered pages whose long prose sequences were not part of the
first architecture/ABI review.

| Page | Visual | Reader question answered |
|---|---|---|
| Executable milestone plan | Required spine with advanced branches | Which gates are sequential, and where can independent research begin? |
| How to read this book | Evidence-driven learning loop | What happens after a failed earlier gate? |
| Transformer capability track | Prefill/decode paths and tiny decoder block | Why do the two paths stress different resources, and where do mixed-precision operations sit? |
| Deformable convolution study | Lowering path and four-neighbor sampling | How do offsets become regular GEMM work, and how is one fractional sample formed? |
| Performance and RTL lesson | Functional/timing correlation loop | What is compared, and when may the analytical model be revised? |

## Consistency constraints

- Diagram labels use the exact ABI 1.0 command names where commands are shown.
- State and failure branches agree with the normative MMIO and memory contracts.
- The course diagram preserves the reviewed compiler/runtime-before-convolution
  dependency.
- YOLO visuals keep DFL decode and NMS on the RV64 host.
- Mermaid inherits the site palette, so the same source works in light and
  eye-comfort dark modes.
- Nearby prose remains the accessible detailed explanation and normative source
  of truth.

## Deliberate exclusions

- Exact register offsets, record fields, error precedence, and test matrices
  remain tables because a diagram would hide values readers need to compare.
- Numerical formulas remain equations and worked examples.
- Historical review pages are not decorated with redundant diagrams.
- No performance chart is added before measured data exists.

## Local documentation validation

- Twenty detailed diagrams are present across thirteen audited reader-facing
  pages after the supplemental pass.
- Every diagram rendered through the existing Material for MkDocs Mermaid
  integration.
- The densest pages were inspected at the normal desktop viewport and at
  `390x844`; no page-level horizontal overflow was observed.
- The architecture visual was inspected in both the light and eye-comfort dark
  palettes.
- The repository validator passed for 90 Markdown files and 85 navigation
  targets.
- `mkdocs build --strict` completed successfully.

These are documentation-rendering observations only. They do not change the
deferred implementation evidence boundary.
