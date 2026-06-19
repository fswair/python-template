# Python Template Upgrade Plan

## Goal

Turn this repository from a minimal Python boilerplate into a stronger reusable starter by:

- fixing template-level correctness issues in the current repo
- backporting production-proven patterns from `~/Desktop/acpkit`
- keeping the result single-package and template-friendly
- implementing a cookiecutter-style starter builder named `advanced_project_template`

## Implementation Status

Phase 1 through Phase 5 have been implemented in this repo:

- package behavior is now covered by real API and CLI tests
- pytest config ownership is consolidated in `pyproject.toml`
- package versioning is routed through `src/advanced_project_template/_version.py`
- Makefile, pre-commit hooks, and CI use `uv`-based commands
- docs, tests, type checks, and package build have local validation paths
- MkDocs now has a fuller starter navigation, strict config, API docs, and docs styling
- release ergonomics now include `bump.sh`, `CHANGELOG.md`, and a version consistency check
- `advanced_project_template` can now generate thin, base, and full workspaces from prompts, flags, or YAML
- builder variables, profiles, and feature categories are documented in `docs/starter-builder.md`

## Scope Reviewed

The plan is based on a direct read of the parts of `acpkit` that are template-relevant:

- root packaging and metadata
- Makefile and local developer workflow
- pre-commit strategy
- GitHub Actions workflows
- docs structure and MkDocs configuration
- CLI/version/layout patterns in `src/acpkit`
- support scripts for coverage, release hygiene, and docs indexing
- representative tests, examples, and contributor docs

The large `references/` tree in `acpkit` was not treated as template source material because it is reference data, not starter infrastructure.

## Current Template Problems To Fix First

These are not placeholder issues. They are template-quality issues:

1. `pytest` configuration is duplicated across `pyproject.toml` and `pytest.ini`, and the active run currently ignores the `pyproject.toml` pytest settings.
2. `examples/__main__.py` is not runnable as written.
3. The package CLI surface is too thin and inconsistent with the package identity.
4. The default test does not validate package behavior.
5. The developer workflow relies on globally installed tools instead of consistently routing through `uv`.
6. Docs, examples, and tests are not yet tied together as maintained surfaces.

## What To Backport From `acpkit`

### 1. Packaging And Layout

Backport:

- dynamic versioning through a dedicated `src/<package>/_version.py`
- `__main__.py` delegating to a real `cli.py`
- package `__init__.py` exporting a stable public surface and `__version__`
- consistent single source of truth for version text

Do not backport directly:

- the `uv` workspace monorepo layout
- multiple publishable subpackages
- adapter-specific exports

Template target:

- keep one package under `src/`
- keep the code layout ready for later growth without forcing monorepo complexity now

### 2. Tooling And Developer Workflow

Backport:

- `uv run` based Makefile commands instead of assuming globally installed tools
- separate `check-formatted` target
- stronger `prod` target
- optional Python matrix check target
- explicit `serve` target for docs
- explicit `pre-commit` target

Likely targets for this template:

- `format`
- `check-formatted`
- `check`
- `tests`
- `docs`
- `serve`
- `pre-commit`
- `prod`

### 3. Test Baseline

Backport:

- tests that validate public behavior instead of toy assertions
- `tests/conftest.py` only when it solves a real import or plugin problem
- a structure that leaves room for support helpers and focused suites

Template target:

- replace the Zen-of-Python smoke test with real tests for the package API and CLI
- ensure examples are either runnable and tested, or clearly documented as illustrative-only

### 4. Docs System

Backport:

- stricter MkDocs config
- `site_url`, `repo_url`, `repo_name`, `edit_uri`
- richer Material features
- markdown extensions that improve docs quality
- API reference pages via `mkdocstrings`
- small docs styling hook via `docs/stylesheets/tweaks.css`
- a cleaner landing page structure

Template target:

- keep docs simple, but real
- ship a docs structure that a new repo can fill in without rewriting the whole site

### 5. CI/CD

Backport:

- a clearer CI job with concurrency control
- formatting check separated from formatting rewrite
- docs deploy using strict mode
- publishing via trusted publishing instead of token-only publishing
- optional coverage upload workflow

Template target:

- preserve the simple single-package case
- validate install, format, lint, type-check, tests, docs build, and package build

### 6. Pre-commit Strategy

Backport:

- local hooks using repo commands, not only third-party hook wrappers
- staged-change-aware expensive checks
- one place to encode quality policy

Template target:

- lightweight default hook set
- optional heavy-hook script pattern, but probably behind a simple threshold and documented as opt-in or phase 2

### 7. Release Hygiene

Backport:

- version bump script pattern
- changelog discipline
- version consistency checks
- optional release validation before publish

Template target:

- add a minimal `bump.sh` plus `_version.py` flow
- decide whether to keep `VERSION`; if kept, it must be synchronized intentionally

### 8. LLM/Agent Context Surfaces

Backport:

- useful `docs/llms.txt`
- optional generated long-form LLM docs index

Template target:

- keep a short, truthful `llms.txt`
- only add generation scripts if they stay generic

## What Not To Port

These are valuable in `acpkit` but should not enter the base template yet:

- monorepo workspace members and local workspace package wiring
- package-specific release guards against PyPI for multiple distributions
- adapter/domain-specific examples
- coverage gates tuned for a mature large codebase
- ACP-specific docs, compatibility matrices, and runtime bridges
- large reference corpora

## Proposed Implementation Phases

### Phase 1: Correctness And Baseline Trust

Goal: make the current template internally consistent and honestly runnable.

Changes:

- remove pytest config duplication and keep one source of truth
- replace the current CLI placeholder with a real minimal CLI entrypoint
- add `_version.py` and export `__version__` cleanly
- fix the example execution path
- replace toy tests with package and CLI tests
- switch Makefile commands to `uv run`

Exit criteria:

- `make check`
- `make tests`
- example invocation works as documented
- no config warnings during pytest startup

### Phase 2: Production-Grade Developer Experience

Goal: make the template feel closer to a serious maintained package.

Changes:

- add `check-formatted`, `serve`, `pre-commit`, and `prod`
- improve `CONTRIBUTING.md` around `uv sync` / `uv run`
- strengthen `.pre-commit-config.yaml`
- add docs strict build command
- align GitHub Actions with the local commands

Exit criteria:

- CI mirrors local commands
- hooks and docs build are documented and reproducible

### Phase 3: Docs And Public Surface

Goal: turn placeholder docs into a reusable documentation starter.

Changes:

- improve `mkdocs.yml`
- add docs navigation for getting started, API, and contributing surfaces
- add `docs/stylesheets/tweaks.css`
- add API reference page(s)
- rewrite `docs/index.md` into a more intentional landing page

Exit criteria:

- `mkdocs build --strict` passes
- docs structure works as a fill-in starter for downstream projects

### Phase 4: Release And Maintenance Ergonomics

Goal: make the starter safer to release and easier to maintain.

Changes:

- add bump/version workflow
- convert publish workflow to trusted publishing
- optionally add changelog starter
- optionally add a minimal coverage summary script and artifact

Exit criteria:

- release path is documented and reproducible
- version ownership is unambiguous

### Phase 5: Builder Readiness

Goal: reshape the template so it can be parameterized cleanly by a future starter builder.

Changes:

- isolate all fields that should become template variables
- remove hard-coded project strings from code, docs, workflows, and examples
- define which files are static, computed, optional, or generated
- decide whether the future builder should support modes such as:
  - library
  - CLI app
  - docs-enabled package
  - single-package vs future workspace-ready layout

Exit criteria:

- the repo can be generated from a small set of variables without brittle search/replace

## Recommended Backport Order

1. Phase 1 correctness fixes
2. `uv run` workflow normalization
3. CLI/version layout upgrade
4. real tests
5. docs hardening
6. CI/CD alignment
7. release ergonomics
8. builder extraction

## File-Level Backport Candidates

Use these `acpkit` files as source patterns, not literal copies:

- `pyproject.toml`
- `Makefile`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/publish.yml`
- `mkdocs.yml`
- `src/acpkit/__init__.py`
- `src/acpkit/__main__.py`
- `src/acpkit/cli.py`
- `src/acpkit/_version.py`
- `scripts/save_coverage_summary.py`
- `scripts/run_if_major_change.py`
- `scripts/generate_llms_docs.py`
- `bump.sh`
- `CONTRIBUTING.md`
- `docs/testing.md`
- `docs/index.md`
- `docs/api/acpkit.md`
- `docs/stylesheets/tweaks.css`

## Concrete Next Step

Use this upgraded repository as the source of truth for the future cookiecutter-style starter builder.
