# Starter Builder

`advanced_project_template` is the starter builder for this repository.

It can generate a workspace from interactive prompts, command-line flags, or a YAML config that can be checked in and reused.

Run `advanced_project_template new` for a fully prompted project creation flow. The interactive flow asks for the project name, output directory, import package, CLI command, GitHub username, helper packages, and feature toggles.

## Template Variables

The builder parameterizes:

- project name, such as `python-template`
- import package name, such as `python_template`
- CLI command name, such as `pytemp`
- description
- author name and email
- repository owner and repository URL
- docs site URL
- license
- initial version

Repository URLs are derived from the GitHub username and project name unless explicitly overridden:

- `https://github.com/<username>/<project>`
- `https://<username>.github.io/<project>/`

## Profiles

`thin` keeps the package, tests, Makefile, and version checks, while disabling the heavier project surfaces.

`base` adds the production baseline: GitHub Actions, pre-commit hooks, `SECURITY.md`, `AGENTS.md`, and `llms.txt`, but keeps the docs site, examples, release helpers, and rename script off.

`full` includes docs, tests, examples, GitHub Actions, pre-commit hooks, release helpers, agent context files, security policy, and rename support.

## Feature Toggles

Every generated surface can be toggled with YAML or paired CLI flags:

- `cli`
- `docs`
- `tests`
- `github`
- `pre_commit`
- `examples`
- `release`
- `rename_script`
- `security`
- `agent_files`
- `packages`

`agent_files` writes `AGENTS.md` plus `llms.txt` or `docs/llms.txt`. When enabled from CLI or YAML without an explicit `security` value, it also enables `SECURITY.md`.

The same placeholder and feature flags are accepted by `advanced_project_template config`, so a reusable YAML can be generated without hand-editing:

```bash
advanced_project_template config starter.yml --profile base --disable-security --enable-packages --helper-package my-helper
```

## File Categories

Static files:

- base source layout
- test layout
- docs layout
- agent, security, release, and helper package surfaces

Computed files:

- `pyproject.toml`
- `mkdocs.yml`
- `README.md`
- GitHub Actions workflows

Generated or refreshed files:

- `advanced_project_template.yml`
- `VERSION`
- `src/<package>/_version.py`

Optional modes:

- library-only package
- library plus CLI
- docs-enabled package
- agent-ready package
- workspace-ready package
