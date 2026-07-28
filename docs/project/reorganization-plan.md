# Repository and book reorganization plan

Status: **approved for documentation-first execution**

Date: **2026-07-28**

## Objective

Turn `NPU_sw_stack` into two complementary products:

1. A clean GitHub repository for source, review, contribution, and future
   experiments.
2. A searchable GitHub Pages chapter book that teaches the complete path from
   integer inference to a RISC-V-hosted simulated NPU.

The release is documentation-first. It does not claim that the Python/C++
scaffolds, WSL setup, Spike integration, workloads, or performance estimates
have been executed.

## Reference pattern

The structural reference is
[`krahets/hello-algo`](https://github.com/krahets/hello-algo) at commit
[`69932ae`](https://github.com/krahets/hello-algo/commit/69932aed1891a7b7f6a0de88cd116d3fe13e7032),
inspected on 2026-07-28.

Reusable patterns:

- A book-first README with a direct online-reading path
- Explicit chapter navigation in `mkdocs.yml`
- Chapter directories with introductions, focused sections, summaries, and
  review exercises
- Source code kept in the same repository as the teaching text
- Material for MkDocs for search, responsive navigation, code copy, dark mode,
  table of contents, and previous/next chapter navigation
- Contribution and pull-request guidance
- Automated checks for the languages and documentation the repository claims
  to support

This project adopts those patterns only. It does not copy HelloAlgo prose,
artwork, branding, animations, code, or licensing terms.

## Constraints

- Preserve all current NPU design decisions and normative contracts.
- Use original English text and project-owned vector assets.
- Keep exact arithmetic, command bytes, registers, and error behavior in one
  authoritative location each.
- Do not run or claim WSL, C++, Spike, YOLO, Transformer, or RTL verification.
- A documentation build may run on Windows because it does not validate the
  NPU implementation.
- Public pages must distinguish project decisions, external baselines, local
  checks, and reproducible observations.
- The first public repository is a release candidate, not a verified NPU.

## Target repository structure

```text
NPU_sw_stack/
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   |-- PULL_REQUEST_TEMPLATE.md
|   `-- workflows/
|       |-- ci.yml
|       `-- docs.yml
|-- docs/
|   |-- assets/
|   |-- chapter_preface/
|   |-- chapter_01_system/
|   |-- chapter_02_reproducible_truth/
|   |-- chapter_03_integer_inference/
|   |-- chapter_04_gemm_npu/
|   |-- chapter_05_commands_memory/
|   |-- chapter_06_compiler/
|   |-- chapter_07_runtime_riscv/
|   |-- chapter_08_cnn/
|   |-- chapter_09_yolo/
|   |-- chapter_10_timing_rtl/
|   |-- chapter_11_yolo26/
|   |-- chapter_12_transformer/
|   |-- chapter_13_deformable_conv/
|   |-- chapter_14_verification/
|   |-- project/
|   `-- index.md
|-- include/                  # future portable C++ API
|-- python/                   # mathematical/reference implementation
|-- src/                      # portable C++ implementation
|-- tests/                    # shared fixtures and language tests
|-- tools/                    # developer/build helpers
|-- CONTRIBUTING.md
|-- CODE_OF_CONDUCT.md
|-- SECURITY.md
|-- mkdocs.yml
|-- requirements-docs.txt
`-- README.md
```

Existing detailed pages remain the normative bodies during this migration.
Chapter directories add reader-oriented introductions, summaries, and review
questions, while `mkdocs.yml` assembles both into one coherent book. Moving
every stable specification into a new path is deliberately deferred to avoid
breaking references and review history during the initial publication.

## Book map

| Chapter | Reader outcome | Existing detailed material |
|---|---|---|
| Preface | Understand scope, status, and how to read | Start Here, specification map |
| 1. From graph to NPU | See every component and trust boundary | Architecture, reviewed plan |
| 2. Reproducible truth | Separate baselines, specifications, scaffolds, and evidence | Lesson 0, evidence method |
| 3. Integer inference | Explain INT8, INT32 wrap, and requantization | Numerical contract, Lesson 1 |
| 4. GEMM and the NPU core | Relate tiling, reuse, scratchpad, and systolic execution | Lesson 2 |
| 5. Commands and memory | Read command bytes and reason about memory effects | Command ABI, memory/execution model |
| 6. Compiler and scheduling | Follow graph validation through command emission | Compiler design, Lesson 4 |
| 7. Runtime and RISC-V | Understand MMIO, fences, errors, reset, and Spike's role | MMIO/runtime, Lesson 5 |
| 8. Convolution and tiny CNN | Lower CNN blocks before a large detector | Lessons 3 and 6 |
| 9. YOLO deployment | Understand the fixed target and staged bring-up | YOLO decision, Lesson 7 |
| 10. Timing and RTL | Separate analytical estimates from hardware truth | Lesson 8 |
| 11. YOLO26 comparison | Isolate newer detector changes | Lesson 9 |
| 12. Transformer systems | Study attention, KV cache, and mixed host/NPU work | Transformer track, Lesson 10 |
| 13. Deformable convolution | Study irregular gathers and fractional sampling | Deformable Conv study, Lesson 11 |
| 14. Verification and project method | Know what evidence changes a status to verified | Verification, execution, experiment, and review pages |

Each chapter gets:

- A one-page orientation and dependency map
- Stated learning objectives
- Links to authoritative detailed sections
- A concise summary
- Review questions that can be answered before implementation
- Experiment gates clearly marked as deferred

## GitHub and Pages design

### Repository

- Create `buicongnguyen/NPU_sw_stack` as a public repository because the user
  requested a public GitHub.io reading experience.
- Use `main` as the initial default branch.
- Add repository description, topics, and homepage URL.
- Add issue templates for documentation, design review, and implementation
  defects.
- Add a pull-request template that separates documentation evidence from
  runtime evidence.
- Add contribution, conduct, and security guidance.

No content license is selected on the user's behalf. Until the owner adds a
license, normal copyright applies; the README must not call the project
open-source.

### Website

- Replace the Jekyll/minima configuration with Material for MkDocs.
- Pin the documentation dependency.
- Build with `mkdocs build --strict`.
- Deploy the generated `site/` artifact through the official GitHub Pages
  Actions flow.
- Trigger deployment only from `main` or manual dispatch.
- Use the repository's GitHub.io project URL as `site_url`.

## Execution phases

### Phase A — Review before mutation

1. Inventory current documents, source scaffolds, workflows, and scripts.
2. Perform logic review for scope, authority, duplication, and dependency
   order.
3. Perform static code/repository review without executing implementation
   gates.
4. Record findings and decide which are documentation blockers versus later
   WSL work.

Exit: reviews are written and no unresolved documentation P0 remains.

### Phase B — Book and repository implementation

1. Add chapter directories and reader-oriented pages.
2. Create `mkdocs.yml`, original assets, and restrained custom styling.
3. Convert Jekyll-only links to ordinary Markdown/MkDocs links.
4. Rewrite documentation checks for MkDocs navigation and links.
5. Add GitHub community files and Pages workflow.
6. Refresh README and publishing instructions.

Exit: the book has one obvious reading order and every current page is
reachable from navigation.

Status: **complete locally**

### Phase C — Documentation validation

1. Run the repository documentation checker.
2. Parse the canonical compiler JSON example.
3. Build the site with `mkdocs build --strict`.
4. Inspect desktop and mobile navigation when a local preview is available.
5. Scan the generated site for unresolved Liquid/Jekyll syntax and placeholders.

Exit: local documentation gates are green. No NPU implementation status changes.

Status: **complete locally** — repository checker and strict MkDocs build pass.

### Phase D — Publish

1. Review all untracked files as one initial-repository scope.
2. Create the initial commit on `main`.
3. Create and connect the public GitHub repository.
4. Push `main`.
5. Configure Pages to use the custom workflow.
6. Monitor Actions through deployment.
7. Open the production URL and inspect the home page, chapter navigation,
   search, repository link, and representative specification pages.

Exit: repository and production Pages URL are reachable, and the deployment
run is successful.

Status: **complete** — the public repository and Pages site were observed at
revision [`3b08e96`](https://github.com/buicongnguyen/NPU_sw_stack/commit/3b08e96a591707823c7f5b57c0d7457f2513d834)
in successful workflow run
[`30335780398`](https://github.com/buicongnguyen/NPU_sw_stack/actions/runs/30335780398).

## Logic safeguards

- Chapter introductions summarize; normative pages define behavior.
- No chapter may change ABI bytes or numerical rules through paraphrase.
- The site build and source CI are separate workflows.
- Documentation deployment must not wait for unavailable WSL/Spike tools.
- CI may continue to describe implementation checks as planned until its first
  successful run is observed.
- A failed Pages deployment is fixed before claiming publication.
- The source tree is never replaced by generated `site/` output.

## Deferred follow-up

After the user reports that WSL and toolchains are ready:

1. Re-audit the actual environment.
2. Execute the statically corrected numerical and tooling findings.
3. Run E0 and E1 gates.
4. Save immutable evidence.
5. Change only proven statuses from scaffolded to verified.
