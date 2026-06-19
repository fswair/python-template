# Quickstart

Generate a full project interactively:

```bash
advanced_project_template new
```

This prompts for the GitHub username and uses it with the project name for repository and docs URLs.

Generate a full project interactively with an explicit output directory:

```bash
advanced_project_template new my-project
```

Generate a thin project without prompts:

```bash
advanced_project_template new my-project --profile thin --no-input
```

Generate a base project with agent context and security files:

```bash
advanced_project_template new my-project --profile base --no-input
```

Create a reusable YAML config:

```bash
advanced_project_template config starter.yml --profile base --enable-packages --helper-package my-helper
advanced_project_template new --config starter.yml --no-input
advanced_project_template new my-project --config starter.yml --no-input
```

Validate the repository before committing:

```bash
make prod
```
