from __future__ import annotations

import shutil
from pathlib import Path
from string import Template

from .models import GeneratedProject, HelperPackage, TemplateConfig

__all__ = ["generate_project"]


def _render(template: str, config: TemplateConfig) -> str:
    values = {
        "project_name": config.project_name,
        "package_name": config.package_name,
        "cli_name": config.cli_name,
        "description": config.description,
        "author_name": config.author_name,
        "author_email": config.author_email,
        "version": config.version,
        "license": config.license,
        "repo_owner": config.repo_owner,
        "repo_url": config.repo_url,
        "docs_site_url": config.docs_site_url,
    }
    return Template(template).safe_substitute(values)


def _write(files: list[Path], root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    files.append(path)


def _pyproject(config: TemplateConfig) -> str:
    dependencies = ""
    docs_extra = """
docs = [
    "mkdocs-material",
    "mkdocstrings[python]",
]"""
    all_extra = '"$project_name[dev,docs]"'
    if not config.include_docs:
        docs_extra = ""
        all_extra = '"$project_name[dev]"'

    script_block = ""
    if config.include_cli:
        script_block = """
[project.scripts]
$cli_name = "$package_name.__main__:main"
"""

    return _render(
        f"""[project]
name = "$project_name"
dynamic = ["version"]
description = "$description"
readme = "README.md"
requires-python = ">=3.11"
license = {{text = "$license"}}
authors = [
    {{name = "$author_name", email = "$author_email"}},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
keywords = []
dependencies = [{dependencies}]

[project.optional-dependencies]
dev = [
    "basedpyright",
    "pytest-asyncio",
    "pytest-cov",
    "pytest",
    "ruff",
    "ty",
    "pre-commit",
]
{docs_extra}

all = [{all_extra}]
{script_block}
[project.urls]
Homepage = "$docs_site_url"
Repository = "$repo_url"
Issues = "$repo_url/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/$package_name/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/$package_name"]

[tool.ruff]
line-length = 100
target-version = "py311"
exclude = [".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "tmp", "build", "dist", "site"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501", "B008"]

[tool.ty]
[tool.ty.environment]
python-version = "3.11"

[tool.ty.src]
exclude = [".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "tmp", "build", "dist", "site"]

[tool.basedpyright]
include = ["src", "tests", "examples", "scripts"]
exclude = [".venv", "__pycache__", ".ruff_cache", ".pytest_cache", "tmp", "build", "dist", "site"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--strict-markers", "--tb=short", "--color=yes"]
markers = []
""",
        config,
    )


def _makefile(config: TemplateConfig) -> str:
    phony_targets = ["format", "check-formatted", "check", "check-version", "all", "prod"]
    prod_targets = ["check-formatted", "check", "check-version"]
    type_paths = ["src", "scripts"]

    tests_target = ""
    if config.include_tests:
        type_paths.append("tests")
        phony_targets.append("tests")
        prod_targets.append("tests")
        tests_target = """
tests:
\t@printf "$(BLUE)==>$(RESET) Running tests with pytest...\\n"
\t@uv run --extra dev pytest
\t@printf "$(GREEN)✔ Tests complete.$(RESET)\\n"
"""

    docs_targets = ""
    if config.include_docs:
        phony_targets.extend(("docs", "serve"))
        prod_targets.append("docs")
        docs_targets = """
docs:
\t@printf "$(BLUE)==>$(RESET) Building docs with mkdocs --strict...\\n"
\t@uv run --extra docs mkdocs build --strict
\t@printf "$(GREEN)✔ Docs build complete.$(RESET)\\n"

serve:
\t@printf "$(BLUE)==>$(RESET) Serving docs with mkdocs...\\n"
\t@uv run --extra docs mkdocs serve --dev-addr 127.0.0.1:8080
        """

    if config.include_examples:
        type_paths.append("examples")

    pre_commit_target = ""
    if config.include_pre_commit:
        phony_targets.append("pre-commit")
        pre_commit_target = """
pre-commit:
\t@printf "$(BLUE)==>$(RESET) Running pre-commit checks...\\n"
\t@uv run --extra dev pre-commit run --all-files
\t@printf "$(GREEN)✔ Pre-commit checks complete.$(RESET)\\n"
"""

    rename_target = ""
    if config.include_rename_script:
        if "scripts" not in type_paths:
            type_paths.append("scripts")
        phony_targets.append("rename")
        rename_target = """
# Allow passing arguments to make commands, for example: make rename my_project
ifeq (rename,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

rename:
\t@if [ -z "$(RUN_ARGS)" ]; then \\
\t\techo "Error: Name is not provided. Usage: make rename my_awesome_project"; \\
\t\texit 1; \\
\tfi
\t@printf "$(BLUE)==>$(RESET) Renaming $package_name to $(RUN_ARGS)...\\n"
\t@python3 scripts/rename_workspace.py $(RUN_ARGS)
\t@printf "$(GREEN)✔ Project renamed to $(RUN_ARGS) successfully!$(RESET)\\n"
"""
    phony_line = " ".join(phony_targets)
    prod_line = " ".join(prod_targets)
    type_path_line = " ".join(type_paths)

    return _render(
        f"""BLUE := \\033[1;34m
GREEN := \\033[1;32m
RESET := \\033[0m

.PHONY: {phony_line}
{rename_target}
format:
\t@printf "$(BLUE)==>$(RESET) Formatting code with ruff...\\n"
\t@uv run --extra dev ruff format
\t@printf "$(GREEN)✔ Formatting complete.$(RESET)\\n"

check-formatted:
\t@printf "$(BLUE)==>$(RESET) Checking formatting with ruff format --check...\\n"
\t@uv run --extra dev ruff format --check
\t@printf "$(GREEN)✔ Formatting check complete.$(RESET)\\n"

check:
\t@printf "$(BLUE)==>$(RESET) Running ruff checks...\\n"
\t@uv run --extra dev ruff check
\t@printf "$(BLUE)==>$(RESET) Type checking with ty...\\n"
\t@uv run --extra dev ty check
\t@printf "$(BLUE)==>$(RESET) Type checking with basedpyright...\\n"
\t@uv run --extra dev basedpyright {type_path_line}
\t@printf "$(GREEN)✔ Checking complete.$(RESET)\\n"

check-version:
\t@printf "$(BLUE)==>$(RESET) Checking version consistency...\\n"
\t@python3 scripts/check_version.py
\t@printf "$(GREEN)✔ Version check complete.$(RESET)\\n"
{tests_target}
{docs_targets}
{pre_commit_target}

all: format check

prod: {prod_line}
""",
        config,
    )


def _package_init(config: TemplateConfig) -> str:
    return _render(
        """from __future__ import annotations

from ._version import __version__


def format_greeting(name: str) -> str:
    return f"Hello, {name.title()}!"


def say_hello(name: str) -> None:
    print(format_greeting(name))


__all__ = ["__version__", "format_greeting", "say_hello"]
""",
        config,
    )


def _cli(config: TemplateConfig) -> str:
    return _render(
        """from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import cast

from . import __version__, say_hello

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="$cli_name",
        description="$description",
    )
    _ = parser.add_argument("name", nargs="?", default="World")
    _ = parser.add_argument("--version", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if cast(bool, args.version):
        print(__version__)
        return 0
    say_hello(cast(str, args.name))
    return 0
""",
        config,
    )


def _main(config: TemplateConfig) -> str:
    if config.include_cli:
        return """from __future__ import annotations

from .cli import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
"""
    return """from __future__ import annotations

from . import say_hello


def main() -> int:
    say_hello("World")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _test(config: TemplateConfig) -> str:
    third_party_imports: list[str] = []
    package_imports = [f"from {config.package_name} import __version__, format_greeting"]
    cli_tests = ""
    if config.include_cli:
        third_party_imports.append("from pytest import CaptureFixture")
        package_imports.append(f"from {config.package_name}.cli import main")
        cli_tests = """def test_cli_prints_greeting(capsys: CaptureFixture[str]) -> None:
    exit_code = main(["grace hopper"])

    assert exit_code == 0
    assert capsys.readouterr().out == "Hello, Grace Hopper!\\n"


"""
    import_block = "\n\n".join(
        "\n".join(group) for group in (third_party_imports, package_imports) if group
    )
    return f"""from __future__ import annotations

{import_block}


{cli_tests}def test_version_is_exported() -> None:
    assert __version__ == "{config.version}"


def test_format_greeting_title_cases_name() -> None:
    assert format_greeting("ada lovelace") == "Hello, Ada Lovelace!"
"""


def _check_version(config: TemplateConfig) -> str:
    return _render(
        """from __future__ import annotations

import ast
from pathlib import Path


def _read_python_version(path: Path) -> str:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name) or target.id != "__version__":
            continue
        value = statement.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    raise SystemExit(f"{path} must assign a string literal to __version__")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    package_version = _read_python_version(root / "src" / "$package_name" / "_version.py")
    plain_version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if package_version != plain_version:
        raise SystemExit(
            f"Version mismatch: _version.py has {package_version}, VERSION has {plain_version}"
        )
    print(f"version ok: {package_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
        config,
    )


def _rename_script(config: TemplateConfig) -> str:
    return _render(
        """from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/rename_workspace.py <new_name>")
        return 1

    new_name_underscore = sys.argv[1]
    new_name_dash = new_name_underscore.replace("_", "-")
    if not new_name_underscore.replace("_", "").isalnum():
        print("Error: Name must contain only letters, numbers, and underscores.")
        return 1

    root_dir = Path(__file__).parent.parent.resolve()
    current_name_dash = "$project_name"
    current_name_underscore = "$package_name"
    skip_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "build",
        "dist",
        "site",
    }

    changed_files_count = 0
    for file_path in root_dir.rglob("*"):
        if not file_path.is_file() or any(part in skip_dirs for part in file_path.parts):
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if current_name_underscore in content or current_name_dash in content:
            content = content.replace(current_name_underscore, new_name_underscore)
            content = content.replace(current_name_dash, new_name_dash)
            _ = file_path.write_text(content, encoding="utf-8")
            changed_files_count += 1

    src_dir = root_dir / "src" / current_name_underscore
    if src_dir.exists() and src_dir.is_dir():
        _ = src_dir.rename(root_dir / "src" / new_name_underscore)

    print(f"     -> Updated {changed_files_count} files.")
    print(f"     -> Source directory updated to src/{new_name_underscore}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
""",
        config,
    )


def _helper_pyproject(helper: HelperPackage, config: TemplateConfig) -> str:
    return f"""[project]
name = "{helper.project_name}"
dynamic = ["version"]
description = "{helper.description}"
readme = "README.md"
requires-python = ">=3.11"
license = {{text = "{config.license}"}}

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "src/{helper.package_name}/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/{helper.package_name}"]
"""


def _mkdocs(config: TemplateConfig) -> str:
    return _render(
        """site_name: $project_name
site_description: $description
site_url: $docs_site_url
strict: true
repo_name: $repo_owner/$project_name
repo_url: $repo_url
edit_uri: edit/main/docs/

theme:
  name: material
  features:
    - navigation.sections
    - navigation.path
    - navigation.top
    - search.suggest
    - search.highlight
    - toc.follow
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths:
            - src

extra_css:
  - stylesheets/tweaks.css

nav:
  - Home: index.md
  - Getting Started: getting-started/quickstart.md
  - API Reference: api/$package_name.md
""",
        config,
    )


def _github_test_workflow() -> str:
    return """name: Tests

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
      - run: uv sync --frozen --all-extras
      - run: make prod
      - run: uv build
"""


def _pre_commit() -> str:
    return """default_install_hook_types: [pre-commit]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--unsafe]
      - id: check-toml
      - id: check-added-large-files

  - repo: local
    hooks:
      - id: ruff-check-fix
        name: ruff check --fix
        entry: uv run --extra dev ruff check --fix
        language: system
        pass_filenames: false
      - id: ruff-format
        name: ruff format
        entry: uv run --extra dev ruff format
        language: system
        pass_filenames: false
      - id: check-version
        name: check version consistency
        entry: python3 scripts/check_version.py
        language: system
        pass_filenames: false
"""


def _security(config: TemplateConfig) -> str:
    return _render(
        """# Security Policy

Report suspected vulnerabilities privately to $author_email.

Do not open a public issue for sensitive reports. Include a minimal reproduction,
affected versions, and any known workaround when possible.
""",
        config,
    )


def _agents(config: TemplateConfig) -> str:
    return _render(
        """# Agent Instructions

This repository was generated with `advanced_project_template`.

- Prefer small, reviewable changes.
- Use `uv run` and `make` targets instead of relying on an activated shell.
- Run `make prod` before release-oriented changes.
- Keep generated project placeholders valid until the owner replaces them.
""",
        config,
    )


def _llms(config: TemplateConfig) -> str:
    docs_command = "- `make docs` builds the documentation site.\n" if config.include_docs else ""
    return _render(
        f"""# $project_name LLM Context

$description

## Project Shape

- Runtime package: `src/$package_name`
- CLI command: `$cli_name`
- Tests: `tests/`
- Version source: `src/$package_name/_version.py` and `VERSION`

## Common Commands

- `uv sync --all-extras` installs all configured extras.
- `make check` runs lint and type checks.
- `make tests` runs the test suite.
- `make prod` runs the production validation path.
{docs_command}
## Agent Notes

- Preserve placeholder values when this repository is still being used as a template.
- Prefer explicit feature toggles over deleting generated files by hand.
""",
        config,
    )


def _write_core(config: TemplateConfig, root: Path, files: list[Path]) -> None:
    _write(files, root, "pyproject.toml", _pyproject(config))
    _write(files, root, "VERSION", f"{config.version}\n")
    _write(
        files,
        root,
        ".gitignore",
        ".venv\n__pycache__/\n.ruff_cache/\n.pytest_cache/\ndist/\nsite/\n",
    )
    _write(
        files,
        root,
        "README.md",
        _render("# $project_name\n\n$description\n\nRun `make prod` before release.\n", config),
    )
    _write(files, root, "Makefile", _makefile(config))
    _write(files, root, f"src/{config.package_name}/__init__.py", _package_init(config))
    _write(
        files,
        root,
        f"src/{config.package_name}/_version.py",
        f'from __future__ import annotations\n\n__version__ = "{config.version}"\n',
    )
    _write(files, root, f"src/{config.package_name}/__main__.py", _main(config))
    _write(files, root, f"src/{config.package_name}/py.typed", "")
    if config.include_cli:
        _write(files, root, f"src/{config.package_name}/cli.py", _cli(config))
    _write(files, root, "scripts/check_version.py", _check_version(config))


def _write_optional(config: TemplateConfig, root: Path, files: list[Path]) -> None:
    if config.include_tests:
        _write(files, root, "tests/conftest.py", "from __future__ import annotations\n")
        _write(files, root, f"tests/test_{config.package_name}.py", _test(config))
    if config.include_examples:
        _write(files, root, "examples/__init__.py", "")
        _write(
            files,
            root,
            "examples/__main__.py",
            f'from {config.package_name} import say_hello\n\nsay_hello("Mert")\n',
        )
    if config.include_docs:
        _write(files, root, "mkdocs.yml", _mkdocs(config))
        _write(files, root, "docs/index.md", _render("# $project_name\n\n$description\n", config))
        _write(
            files,
            root,
            "docs/getting-started/quickstart.md",
            f"# Quickstart\n\n```bash\nuv run {config.cli_name} World\n```\n",
        )
        _write(
            files,
            root,
            f"docs/api/{config.package_name}.md",
            f"# `{config.package_name}` API\n\n::: {config.package_name}\n",
        )
        _write(
            files,
            root,
            "docs/stylesheets/tweaks.css",
            ".md-typeset .doc-object { margin-bottom: 1rem; }\n",
        )
    if config.include_github:
        _write(files, root, ".github/workflows/test.yml", _github_test_workflow())
    if config.include_pre_commit:
        _write(files, root, ".pre-commit-config.yaml", _pre_commit())
    if config.include_release:
        _write(
            files,
            root,
            "CHANGELOG.md",
            f"# Changelog\n\n## {config.version} - Unreleased\n\n### Added\n\n- Initial starter project.\n",
        )
        _write(
            files,
            root,
            "bump.sh",
            _render(
                """#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: ./bump.sh <version>" >&2
  exit 1
fi
python3 - "$1" <<'PY'
from pathlib import Path
import re
import sys
version = sys.argv[1]
root = Path.cwd()
version_file = root / "src" / "$package_name" / "_version.py"
content = version_file.read_text(encoding="utf-8")
content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{version}"', content)
version_file.write_text(content, encoding="utf-8")
(root / "VERSION").write_text(f"{version}\\n", encoding="utf-8")
PY
""",
                config,
            ),
        )
    if config.include_rename_script:
        _write(files, root, "scripts/rename_workspace.py", _rename_script(config))
    if config.include_security:
        _write(files, root, "SECURITY.md", _security(config))
    if config.include_agent_files:
        _write(files, root, "AGENTS.md", _agents(config))
        llms_path = "docs/llms.txt" if config.include_docs else "llms.txt"
        _write(files, root, llms_path, _llms(config))


def _write_helpers(config: TemplateConfig, root: Path, files: list[Path]) -> None:
    if not config.include_packages:
        return
    for helper in config.helper_packages:
        base = root / "packages" / "helpers" / helper.project_name
        _write(files, base, "pyproject.toml", _helper_pyproject(helper, config))
        _write(files, base, "README.md", f"# {helper.project_name}\n\n{helper.description}\n")
        _write(files, base, "VERSION", f"{config.version}\n")
        _write(
            files,
            base,
            f"src/{helper.package_name}/__init__.py",
            'from ._version import __version__\n\n__all__ = ["__version__"]\n',
        )
        _write(
            files,
            base,
            f"src/{helper.package_name}/_version.py",
            f'__version__ = "{config.version}"\n',
        )
        _write(files, base, f"src/{helper.package_name}/py.typed", "")


def _clean_destination(destination: Path) -> None:
    protected_paths = {Path("/").resolve(), Path.home().resolve()}
    if destination in protected_paths:
        raise ValueError(f"Refusing to clean protected path: {destination}")
    for child in destination.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def generate_project(
    config: TemplateConfig, destination: Path, *, force: bool = False
) -> GeneratedProject:
    config.validate()
    destination = destination.resolve()
    if destination.exists() and any(destination.iterdir()) and not force:
        raise FileExistsError(f"Destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    if force:
        _clean_destination(destination)

    files: list[Path] = []
    _write_core(config, destination, files)
    _write_optional(config, destination, files)
    _write_helpers(config, destination, files)

    from .config import write_config

    write_config(config, destination / "advanced_project_template.yml")
    files.append(destination / "advanced_project_template.yml")
    return GeneratedProject(destination=destination, files=tuple(files))
