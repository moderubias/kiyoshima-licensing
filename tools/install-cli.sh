#!/usr/bin/env bash
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_dir="${XDG_BIN_HOME:-$HOME/.local/bin}"
target="$target_dir/klicense"
source="$root/tools/klicense.py"

if [[ "${1:-}" == "--uninstall" ]]; then
  if [[ -L "$target" ]] && [[ "$(readlink -f "$target")" == "$(readlink -f "$source")" ]]; then
    rm -- "$target"
    echo "removed $target"
  else
    echo "nothing removed: $target is not this framework's CLI symlink"
  fi
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--uninstall]" >&2
  exit 2
fi

mkdir -p "$target_dir"
ln -sfn "$source" "$target"
echo "installed symlink: $target -> $source"
case ":${PATH}:" in
  *":${target_dir}:"*) ;;
  *) echo "note: add $target_dir to PATH to invoke 'klicense' directly" ;;
esac
