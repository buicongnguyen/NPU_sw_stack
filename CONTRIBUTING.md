# Contributing

Thank you for helping make this NPU learning stack clearer and more reliable.

## Before opening a change

1. Check the chapter and normative specification that own the behavior.
2. Keep explanatory pages consistent with the normative contract.
3. Do not present planned or statically reviewed behavior as executed evidence.
4. Do not commit credentials, model weights, proprietary datasets, build trees,
   or copied third-party book content.

## Documentation changes

Install the pinned dependencies and run:

```powershell
python -m venv .venv-docs
./.venv-docs/Scripts/python -m pip install -r requirements-docs.txt
./scripts/check_docs.ps1
./.venv-docs/Scripts/python -m mkdocs build --strict
```

Add new public pages to the explicit `nav` in `mkdocs.yml`. A chapter must have
an `index.md` introduction and a `review.md` summary.

## Implementation changes

Implementation verification is deferred until the WSL environment is defined.
For now, describe code findings in the dated review and avoid claiming that
unexecuted tests pass. When implementation work resumes, each pull request
should include the exact environment, command, result, and related journal
entry.

## Pull requests

Use a focused branch, preferably prefixed with `codex/`, and keep each pull
request to one coherent purpose. Explain:

- the problem and owning contract;
- the chosen change and alternatives;
- validation performed;
- validation deliberately deferred;
- compatibility or migration impact.

By contributing, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
Because this repository currently has no license, contribution terms must be
clarified by the owner before outside code is merged.
