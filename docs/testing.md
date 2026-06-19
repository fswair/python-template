# Testing

Tests should cover public behavior first: config loading, CLI behavior, generated project files, and any user-facing API.

The current suite validates:

- package version export
- YAML config round-tripping
- thin, base, and full project generation
- security and agent file feature behavior
- helper package generation
- non-interactive CLI generation

Run tests with:

```bash
make tests
```

Run linting and type checks with:

```bash
make check
```
