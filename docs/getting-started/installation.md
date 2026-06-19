# Installation

## Requirements

- Python 3.11 or newer
- `uv`
- `git`

## Contributor Setup

Install the development and documentation tools:

```bash
uv sync --extra dev --extra docs
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

## Runtime Install

Install the package in editable mode through `uv`:

```bash
uv sync
```

The package exposes the `advanced_project_template` command after installation.
