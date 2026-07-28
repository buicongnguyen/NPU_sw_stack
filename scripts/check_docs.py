"""Validate repository-owned documentation and explicit MkDocs navigation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


class MkDocsLoader(yaml.SafeLoader):
    """Safe loader that accepts PyMdown's named formatting callback."""


def _named_python_value(
    loader: MkDocsLoader, suffix: str, node: yaml.Node
) -> str:
    del loader, node
    return suffix


MkDocsLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:", _named_python_value
)

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
LIQUID = re.compile(r"\{\{\s*[^}]*relative_url[^}]*\}\}|\{%\s*(?:assign|for|else|endfor)\b")
RECORD_TYPE = re.compile(
    r"(?m)^record_type:\s*(decision|local_check|observation)\s*$"
)
JSON_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
TRAILING_WHITESPACE = re.compile(r"[ \t]+$")
IGNORED_DIRS = {".git", ".venv", ".venv-docs", "build", "out", "site"}


def repository_files(root: Path, suffixes: set[str]) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)
    )


def nav_targets(value: object) -> list[str]:
    if isinstance(value, str):
        return [value] if value.endswith(".md") else []
    if isinstance(value, list):
        return [target for item in value for target in nav_targets(item)]
    if isinstance(value, dict):
        return [target for item in value.values() for target in nav_targets(item)]
    return []


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith(("#", "/")):
        return None
    if not parsed.path:
        return None

    return (source.parent / unquote(parsed.path)).resolve()


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    docs = root / "docs"
    errors: list[str] = []

    markdown_files = repository_files(root, {".md"})
    text_files = repository_files(root, {".md", ".yml", ".yaml"})

    for path in text_files:
        relative = path.relative_to(root).as_posix()
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if TRAILING_WHITESPACE.search(line):
                errors.append(f"{relative}:{number}: trailing whitespace")

    for path in markdown_files:
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8")

        if LIQUID.search(content):
            errors.append(f"{relative}: unresolved Jekyll/Liquid expression")

        if relative.startswith("docs/_posts/") and not RECORD_TYPE.search(content):
            errors.append(f"{relative}: missing or invalid record_type")

        if (
            relative.startswith("docs/_posts/")
            and re.search(r"(?m)^record_type:\s*local_check\s*$", content)
            and re.search(r"(?m)^##\s+(Observed evidence|Test evidence)\s*$", content)
        ):
            errors.append(
                f"{relative}: local_check must not be labeled reproducible evidence"
            )

        for number, block in enumerate(JSON_FENCE.findall(content), start=1):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"{relative}: invalid JSON fence {number}: "
                    f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
                )

        for match in MARKDOWN_LINK.finditer(content):
            raw = match.group(1)
            if re.search(r"(GITHUB_USER|github\.com/OWNER/|example\.com)", raw):
                errors.append(f"{relative}: unresolved placeholder link '{raw}'")
                continue
            target = local_target(path, raw)
            if target is not None and not target.exists():
                errors.append(f"{relative}: broken local link '{raw}'")

    config_path = root / "mkdocs.yml"
    try:
        config = yaml.load(
            config_path.read_text(encoding="utf-8"), Loader=MkDocsLoader
        )
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"mkdocs.yml: cannot parse configuration: {exc}")
        config = {}

    targets = nav_targets(config.get("nav", [])) if isinstance(config, dict) else []
    seen: set[str] = set()
    for target in targets:
        if target in seen:
            errors.append(f"mkdocs.yml: duplicate navigation target '{target}'")
        seen.add(target)
        candidate = (docs / target).resolve()
        try:
            candidate.relative_to(docs.resolve())
        except ValueError:
            errors.append(f"mkdocs.yml: navigation target escapes docs: '{target}'")
            continue
        if not candidate.is_file():
            errors.append(f"mkdocs.yml: missing navigation target '{target}'")

    for chapter in sorted(docs.glob("chapter_*")):
        for name in ("index.md", "review.md"):
            required = (chapter / name).relative_to(docs).as_posix()
            if not (chapter / name).is_file():
                errors.append(f"{required}: required chapter page is missing")
            elif required not in seen:
                errors.append(f"mkdocs.yml: chapter page is not in nav: '{required}'")

    if errors:
        for error in sorted(set(errors)):
            print(error, file=sys.stderr)
        return 1

    print(
        f"Documentation checks passed: {len(markdown_files)} Markdown files, "
        f"{len(targets)} navigation targets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
