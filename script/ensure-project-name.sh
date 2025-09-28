#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project_dir="$(basename "$repo_root")"
expected_name="oc-student-${project_dir}"

pulumi_file="${repo_root}/infra/Pulumi.yaml"
pyproject_file="${repo_root}/pyproject.toml"

ensure_pulumi_name() {
  local file="$1"
  local expected="$2"
  [[ -f "$file" ]] || return 0
  python3 - "$file" "$expected" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
expected = sys.argv[2]
text = path.read_text()
pattern = r'(?m)^name:\s*(\S+)'
if re.search(pattern, text):
    updated = re.sub(pattern, f"name: {expected}", text, count=1)
else:
    updated = f"name: {expected}\n{text}"
if updated != text:
    path.write_text(updated)
    print(f"Updated {path} project name -> {expected}")
PY
}

ensure_pyproject_name() {
  local file="$1"
  local expected="$2"
  [[ -f "$file" ]] || return 0
  python3 - "$file" "$expected" <<'PY'
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
expected = sys.argv[2]
text = path.read_text()
pattern = r'(?m)^(name\s*=\s*")[^"]*(")'
if re.search(pattern, text):
    updated = re.sub(pattern, rf'\1{expected}\2', text, count=1)
else:
    updated = text
if updated != text:
    path.write_text(updated)
    print(f"Updated {path} project name -> {expected}")
PY
}

ensure_pulumi_name "$pulumi_file" "$expected_name"
ensure_pyproject_name "$pyproject_file" "$expected_name"
