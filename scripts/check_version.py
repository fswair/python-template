from __future__ import annotations

import ast
from pathlib import Path


def _read_python_version(path: Path) -> str:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        if not isinstance(target, ast.Name) or target.id != "__version__":
            continue
        value = statement.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    raise SystemExit(f"{path} must assign a string literal to __version__")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    package_version = _read_python_version(root / "src" / "advanced_project_template" / "_version.py")
    plain_version = (root / "VERSION").read_text(encoding="utf-8").strip()

    if package_version != plain_version:
        raise SystemExit(
            f"Version mismatch: _version.py has {package_version}, VERSION has {plain_version}"
        )

    print(f"version ok: {package_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
