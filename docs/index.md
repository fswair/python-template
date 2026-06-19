# Python Template

Tempx is a configurable project generator for modern Python libraries and small CLI tools.

It is intentionally small, but it includes the pieces that are expensive to retrofit later:
packaging, formatting, type checks, tests, docs, security/agent context files, pre-commit hooks, and release validation.

## What You Get

- `uv` for dependency syncing and command execution
- Hatchling packaging with dynamic versioning from `src/advanced_project_template/_version.py`
- Ruff formatting and linting
- `ty` and `basedpyright` type checks
- Pytest with the active config stored in `pyproject.toml`
- MkDocs Material documentation with API reference generation
- Optional `SECURITY.md`, `AGENTS.md`, and `llms.txt` for agent-facing repositories
- GitHub Actions for tests, docs, package build, and trusted publishing

## Quick Example

The packaged CLI can generate projects from prompts or YAML:

```bash
advanced_project_template new
advanced_project_template new my-project
advanced_project_template new my-project --profile base --no-input
advanced_project_template config starter.yml --profile thin
advanced_project_template new --config starter.yml --no-input
advanced_project_template new my-project --config starter.yml --no-input
```

## Recommended First Steps

1. Install dependencies with `uv sync --extra dev --extra docs`.
2. Generate a full project interactively with `advanced_project_template new`.
3. Generate a base project with `advanced_project_template new my-project --profile base --no-input`.
4. Generate a thin project with `advanced_project_template new my-project --profile thin --no-input`.
