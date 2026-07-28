# Post-deployment logic review

Status: **reviewed; repository hardening approved**

Review date: **2026-07-28**

Reviewed baseline: [`3b08e96`](https://github.com/buicongnguyen/NPU_sw_stack/commit/3b08e96a591707823c7f5b57c0d7457f2513d834)

Scope: the published chapter structure, specification authority, evidence
language, documentation workflow, navigation, and contribution path. This
review did not execute or validate the NPU implementation.

## Verdict

No P0 or P1 documentation-logic blocker was found. The book order still
matches the intended implementation dependency graph, and the site consistently
labels implementation behavior as unverified. Four repository-hardening
findings should be resolved in this change.

## Findings and resolutions

### L1 — Publication is successful but not recorded as an observation

**Finding:** The public repository and Pages workflow exist, but the journal
ends with a pre-publication `local_check`. A reader following the evidence
method cannot locate a dated record of the first deployed revision and workflow
run.

**Resolution:** Add a post-deployment `observation` entry tied to immutable
revision `3b08e96` and successful workflow run `30335780398`. The entry claims
only repository and documentation deployment facts.

### L2 — Documentation workflow path coverage is narrower than checker scope

**Finding:** The checker reads root policy Markdown and GitHub YAML, but the
workflow path filters trigger mainly for `docs/`, `mkdocs.yml`, and checker
files. A change to `README.md`, `CONTRIBUTING.md`, an issue form, or another
workflow can therefore bypass the checker.

**Resolution:** Extend pull-request and `main` path filters to root Markdown,
`CITATION.cff`, and `.github/**`.

### L3 — Navigation coverage is true but not fully enforced

**Finding:** All current files under `docs/` are in `mkdocs.yml`, but the custom
checker requires navigation only for chapter introduction/review pairs. A new
standalone public page could be committed without explicit navigation.

**Resolution:** Require every repository-owned Markdown page under `docs/` to
appear exactly once in the MkDocs navigation.

### L4 — YAML validation is uneven

**Finding:** `mkdocs.yml` is parsed, while workflow, issue-form, and citation
YAML receive only whitespace checks. GitHub catches some malformed workflow
syntax after push, which is later than the local documentation gate.

**Resolution:** Parse all repository-owned `.yml`, `.yaml`, and `.cff` files
locally. This is syntax validation, not a complete GitHub Actions semantic
validator.

### L5 — Normative and explanatory authority remains coherent

**Finding:** Chapter wrappers continue to link to the numerical, ABI, memory,
MMIO, compiler, and verification authorities without redefining their exact
values.

**Resolution:** No structural change. Preserve the wrapper-first organization.

### L6 — Deployment success must not change implementation status

**Finding:** A successful site build proves navigation, rendering, and
publication—not numerical, compiler, runtime, Spike, timing, or RTL behavior.

**Resolution:** Keep implementation CI manual and retain every executable
milestone as unverified until WSL evidence exists.

## Acceptance checks

- All repository YAML/CFF files parse.
- Every `docs/**/*.md` page is present once in `mkdocs.yml`.
- Root policy/community changes trigger documentation checks.
- The post-deployment observation identifies an immutable revision and run.
- `mkdocs build --strict` succeeds.
- No implementation test or status is implied by publication.
