#!/usr/bin/env bash
set -uo pipefail

apply=0
if [[ "${1:-}" == "--apply" ]]; then
  apply=1
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--apply]" >&2
  exit 2
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root" || exit 1

if [[ ! -f README.md ]] || ! grep -q "Kiyoshima Licensing Framework" README.md; then
  echo "ERROR: this does not look like a Kiyoshima Licensing Framework repository" >&2
  exit 2
fi

obsolete=(
  "LICENSES/LicenseRef-Kiyoshima-Source-1.0.txt"
  "registry/grants.json"
  "templates/project/LICENSE"
  "templates/project/LICENSES/LicenseRef-Kiyoshima-Source-1.0.txt"
  "legal/LicenseRef-Kiyoshima-Source-1.0.txt"
  "legal/README.md"
)

found=0
for path in "${obsolete[@]}"; do
  if [[ -e "$path" ]]; then
    found=1
    if (( apply )); then
      rm -f -- "$path"
      echo "removed obsolete: $path"
    else
      echo "would remove obsolete: $path"
    fi
  fi
done

if (( apply )); then
  rmdir templates/project/LICENSES 2>/dev/null || true
  rmdir legal 2>/dev/null || true
  find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
  echo "migration cleanup complete"
else
  if (( ! found )); then
    echo "no known framework-1.0 leftovers found"
  fi
  echo "dry run only; re-run with --apply to remove listed obsolete files"
fi
