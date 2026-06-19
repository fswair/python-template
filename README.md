# Tempx

`advanced_project_template` is a configurable Python starter generator. It builds thin, base, or full Python workspaces from prompts, command-line flags, or a reusable YAML config.

## Features

- Thin, base, and full starter profiles
- Interactive prompts with sensible defaults, including GitHub username
- YAML config export and repeatable regeneration
- Optional docs, tests, examples, GitHub Actions, pre-commit hooks, release helpers, security policy, agent-facing context files, and rename script
- Optional `packages/helpers/*` workspace-style helper packages
- Generated projects use `uv`, Ruff, `ty`, basedpyright, pytest, Hatchling, and optional MkDocs Material

## Usage

Create a full project interactively:

```bash
advanced_project_template new
```

The interactive flow uses the GitHub username and project name to derive repository placeholders, for example `https://github.com/<username>/<project>`.

Create a full project interactively with an explicit output directory:

```bash
advanced_project_template new my-project
```

Create a thin project without prompts:

```bash
advanced_project_template new my-project --profile thin --no-input
```

Create a base project with security and agent context files, but without the docs site:

```bash
advanced_project_template new my-project --profile base --no-input
```

Write a reusable config:

```bash
advanced_project_template config starter.yml --profile full
advanced_project_template config starter.yml --profile base --disable-security --enable-packages --helper-package my-helper
```

Generate from config:

```bash
advanced_project_template new --config starter.yml --no-input
advanced_project_template new my-project --config starter.yml --no-input
```

Generate with helper packages:

```bash
advanced_project_template new my-project --no-input --enable-packages --helper-package my-helper
```

Feature toggles are exposed as paired flags, for example:

```bash
advanced_project_template new my-project --no-input --disable-docs --enable-agent-files --enable-security
```

## Development

Install dependencies:

```bash
uv sync --extra dev --extra docs
```

Run the release-grade validation gate:

```bash
make prod
```

Run pre-commit checks:

```bash
make pre-commit
```

## Release

Update this package version:

```bash
./bump.sh 0.2.0
```

Then validate and build:

```bash
make prod
uv build
```
