# Contributing

First off, thank you for considering contributing to this project!

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd python_template
   ```

2. **Install dependencies using `uv`:**
   ```bash
   uv sync --extra dev --extra docs
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

We use a `Makefile` to simplify common tasks:

- `make format`: Formats code using `ruff`.
- `make check-formatted`: Verifies formatting without rewriting files.
- `make check`: Runs linters (`ruff check`) and type checkers (`basedpyright`, `ty`).
- `make check-version`: Verifies `VERSION` and `_version.py` agree.
- `make tests`: Runs the test suite using `pytest`.
- `make docs`: Builds the documentation with MkDocs strict mode.
- `make all`: Runs formatting and checking consecutively.
- `make prod`: Runs formatting checks, lint/type checks, tests, and docs.

Before submitting a Pull Request, please ensure `make prod` runs without any errors.

## Pull Requests

1. Create a new branch for your feature or bugfix.
2. Commit your changes (your commit will be checked by `pre-commit`).
3. Push to your branch and open a Pull Request.
4. Ensure the CI workflows (GitHub Actions) pass.
