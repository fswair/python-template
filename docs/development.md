# Development Workflow

Use the Makefile targets as the canonical local workflow for `advanced_project_template`.

```bash
make format
make check
make tests
make docs
```

For the full release-grade validation gate:

```bash
make prod
```

The commands use `uv run`, so manual virtual environment activation is not required.

## Pre-commit

Install hooks once:

```bash
uv run pre-commit install
```

Run the full hook set manually:

```bash
make pre-commit
```
