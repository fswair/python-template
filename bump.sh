#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  ./bump.sh <version>
EOF
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

target_version="$1"

python3 - "${target_version}" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

target_version = sys.argv[1]
if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([a-zA-Z0-9.\-+]+)?", target_version):
    raise SystemExit(f"Invalid version: {target_version!r}")

root = Path.cwd()
version_py = root / "src" / "advanced_project_template" / "_version.py"
version_txt = root / "VERSION"

content = version_py.read_text(encoding="utf-8")
updated, replacements = re.subn(
    r'^__version__ = (?P<quote>["\'])(?P<version>[^"\']+)(?P=quote)$',
    f'__version__ = "{target_version}"',
    content,
    count=1,
    flags=re.MULTILINE,
)
if replacements != 1:
    raise SystemExit(f"Expected exactly one __version__ assignment in {version_py}")

version_py.write_text(updated, encoding="utf-8")
version_txt.write_text(f"{target_version}\n", encoding="utf-8")

print(f"Version updated to {target_version}")
PY
