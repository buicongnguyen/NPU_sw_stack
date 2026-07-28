# Publishing and maintenance

The book is built with MkDocs Material and published by the
`Documentation and Pages` GitHub Actions workflow. It does not depend on the
deferred WSL implementation environment.

## Local documentation check

Install the pinned documentation dependencies in a disposable environment:

```powershell
python -m venv .venv-docs
./.venv-docs/Scripts/python -m pip install -r requirements-docs.txt
```

Then validate links, navigation, and the production build:

```powershell
./scripts/check_docs.ps1
./.venv-docs/Scripts/python -m mkdocs build --strict
```

The generated `site/` directory is ignored. GitHub Actions rebuilds it from
source rather than accepting locally generated HTML.

## GitHub Pages deployment

On a pull request, the workflow checks the documentation and performs a strict
MkDocs build. On a push to `main`, it also:

1. configures the GitHub Pages environment;
2. uploads the generated site as a Pages artifact;
3. deploys that artifact with the repository’s `github-pages` environment.

The repository Pages setting uses **GitHub Actions** as its source. Branch
publishing and Jekyll are not used.

The canonical URLs are:

- Book: <https://buicongnguyen.github.io/NPU_sw_stack/>
- Repository: <https://github.com/buicongnguyen/NPU_sw_stack>

## Normal contribution flow

After the initial repository publication, use a short-lived branch:

```powershell
git switch -c codex/docs-short-description
```

Make one coherent change, run the documentation gates, and open a pull request.
The pull request should state:

- the chapter or contract affected;
- whether behavior is normative or explanatory;
- validation commands and results;
- known limitations;
- any implementation test deliberately deferred.

## Book organization

| Content | Location | Purpose |
|---|---|---|
| Chapter introductions and reviews | `docs/chapter_*/` | Teaching spine and navigation |
| Normative specifications | `docs/*.md` | Current behavior and interfaces |
| Guided lessons | `docs/lessons/` | Ordered future implementation gates |
| Project decisions and reviews | `docs/project/` | Plans, audits, and rationale |
| Dated journal | `docs/_posts/` | Decisions, checks, and observations over time |
| Site assets | `docs/assets/` | Original logo, styles, and future small figures |

The explicit navigation in `mkdocs.yml` is part of the reader experience.
Every new public chapter page must be added there and pass the checker.

## Recording implementation evidence later

When WSL is ready, copy the journal template and record:

1. objective and governing specification;
2. immutable commit identifier;
3. environment and tool versions;
4. exact commands and inputs;
5. observed outputs or artifact hashes;
6. failed cases and interpretation;
7. the claim the result supports—and what it does not support.

Use `record_type: observation` only when the result is tied to an immutable
revision and can be reproduced. Static inspection remains `local_check`.

## Publication safety

Before pushing a page or artifact, check that it contains no credentials,
private paths, personal data, restricted model weights, or copied third-party
book content. External material should be cited; repository prose, diagrams,
logo, and styling should remain original.

## Official references

- [GitHub Pages custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [MkDocs configuration documentation](https://www.mkdocs.org/user-guide/configuration/)
- [Material for MkDocs documentation](https://squidfunk.github.io/mkdocs-material/)
