# Reorganization logic review

Status: **reviewed; approved for documentation-first implementation**

Date: **2026-07-28**

Scope: the proposed transition from a flat Jekyll documentation set to an
original HelloAlgo-inspired MkDocs chapter book and public GitHub repository.

## Verdict

No P0 logic blocker remains. The wrapper-first chapter migration is safer than
moving every normative page in the initial release. GitHub Pages deployment can
be verified independently of WSL and the NPU implementation.

## Review method

The reorganization plan was checked for:

- Reader dependency order
- Normative-source duplication
- Broken-link and publishing risk
- Separation of documentation and implementation evidence
- External-reference copyright and license boundaries
- GitHub repository and Pages prerequisites
- Rollback and later migration cost

## Findings and resolutions

### L1 — The current material is a specification library, not yet a book

**Finding:** The existing pages are technically detailed, but the reader must
choose among plans, contracts, lessons, research tracks, and dated posts before
forming a mental model.

**Resolution:** Add numbered chapter introductions, summaries, and review
questions. Keep detailed pages as chapter sections rather than rewriting exact
contracts into friendlier but potentially divergent copies.

### L2 — Physical moves would create unnecessary first-release risk

**Finding:** Moving every established page into a new directory would require
large link rewrites and make the specification review harder to compare.

**Resolution:** Use chapter wrapper directories and explicit MkDocs navigation
first. Stable detailed pages remain at their current paths. A later,
redirect-backed cleanup can move them after publication.

### L3 — The learning order must follow the implementation dependency graph

**Finding:** A runtime-before-compiler book order would conflict with the
project's E4-before-E5 execution order.

**Resolution:** The book flows from command/memory contracts to compiler
emission, then to runtime/RV64 submission. This follows graph → command stream
→ host/device execution.

### L4 — Advanced branches are not one chapter

**Finding:** YOLO26, Transformer, and deformable convolution have different
operators, numerical questions, and memory behavior. Combining them would
produce an oversized, incoherent chapter.

**Resolution:** Give each branch an independent chapter after the shared
YOLOv8n and timing foundation.

### L5 — Chapter prose must not become a second ABI

**Finding:** Summaries and worked explanations can accidentally restate a field
or arithmetic rule differently from the normative document.

**Resolution:** Chapter pages explain motivation, ownership, and examples, then
link to the authoritative numerical/ABI/MMIO tables. Exact values are not
duplicated unless generated and checked.

### L6 — Documentation deployment must not imply implementation verification

**Finding:** A successful Pages workflow proves Markdown/site integrity, not
Python/C++ numerical behavior, Spike integration, or performance.

**Resolution:** Use a separate documentation workflow. Keep implementation CI
manual during the documentation phase and preserve all code statuses as
unverified.

### L7 — Jekyll-specific source cannot survive a MkDocs switch unchanged

**Finding:** Liquid `relative_url` expressions, generated post loops, Minima
configuration, and Jekyll front matter would either render literally or break
strict MkDocs builds.

**Resolution:** Convert internal links to ordinary Markdown, replace the
generated journal index with explicit navigation, remove Jekyll-only config,
and strengthen the checker to validate MkDocs navigation and YAML.

### L8 — HelloAlgo is a pattern reference, not a content source

**Finding:** HelloAlgo's prose, code, images, animation, branding, and theme
overrides have their own license. Copying them is unnecessary and would blur
the identity of this project.

**Resolution:** Use only high-level repository/book patterns and standard
MkDocs Material features. Create original NPU text, SVGs, colors, exercises,
and CSS. Record the inspected reference commit.

### L9 — Public repository policy requires owner decisions

**Finding:** No content license exists. Selecting one would create a legal
grant on the owner's behalf.

**Resolution:** Add contribution, conduct, security, and review policies, but
do not add a license or describe the project as open-source until the owner
chooses one.

### L10 — Initial publication has no existing base commit or remote

**Finding:** A normal feature-branch pull request cannot precede the first
commit because there is no base history or target repository.

**Resolution:** Review the complete initial scope locally, create the first
commit on `main`, create the requested public repository, push, enable workflow
Pages, and use pull requests for subsequent changes.

## Acceptance checks

- Every chapter is reachable from `mkdocs.yml`.
- Every detailed specification appears exactly once in the book navigation.
- No unresolved Liquid/Jekyll expression reaches generated HTML.
- `mkdocs build --strict` succeeds.
- Documentation checks do not scan generated or third-party directories.
- Repository and Pages links use the actual owner/repository.
- The site repeatedly states that implementation verification is deferred.
- No HelloAlgo content or visual asset is copied.

## Deferred logic review

After WSL setup, review whether chapter/lab ordering still matches the actual
developer workflow and whether observed failures require reordering gates.
