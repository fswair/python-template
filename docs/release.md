# Release

Use `make prod` before publishing a `advanced_project_template` release.

The release gate verifies:

- formatting
- Ruff linting
- `ty`
- `basedpyright`
- pytest
- MkDocs strict build

## Bump Version

Update the package version and `VERSION` file together:

```bash
./bump.sh 0.2.0
```

Then validate:

```bash
make prod
uv build
```

Publishing is configured for PyPI trusted publishing on `v*` tags.
