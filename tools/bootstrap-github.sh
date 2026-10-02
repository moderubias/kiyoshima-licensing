#!/usr/bin/env bash
set -uo pipefail

apply=false
rename=false
new_name="kiyoshima-licensing"

for arg in "$@"; do
  case "$arg" in
    --apply) apply=true ;;
    --rename) rename=true ;;
    --help|-h)
      cat <<'EOF'
Usage: tools/bootstrap-github.sh [--apply] [--rename]

Without --apply, prints the GitHub metadata/settings plan only.
With --apply, uses authenticated `gh` to set description, topics, repository features,
and labels. --rename also renames the current repository to kiyoshima-licensing.
Branch/tag rulesets remain manual; see docs/REPOSITORY-SETUP.md.
EOF
      exit 0
      ;;
  esac
done

description="Machine-readable source-available licensing: free for individuals, learning and qualifying research; organizations evaluate, then ask. AI/TDM semantics, grants, provenance and monitoring."
topics=(kiyoshima-source source-available software-licensing machine-readable-licensing ai-licensing license-passport spdx reuse provenance software-law)
labels=(adoption commercial ai-rights license-review evaluation dependencies github-actions)

cat <<EOF
Kiyoshima GitHub bootstrap plan
- recommended repository name: $new_name
- description: $description
- disable Wiki
- disable Projects unless actively used
- enable delete-branch-on-merge
- prefer squash/rebase over merge commits
- add topics: ${topics[*]}
- ensure labels: ${labels[*]}
- configure branch/tag rulesets manually after CI check exists
EOF

if ! $apply; then
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI is required for --apply" >&2
  exit 2
fi

gh auth status >/dev/null || exit 2

if $rename; then
  gh repo rename "$new_name" --yes
fi

gh repo edit \
  --description "$description" \
  --enable-wiki=false \
  --enable-projects=false \
  --delete-branch-on-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge \
  --enable-squash-merge

for topic in "${topics[@]}"; do
  gh repo edit --add-topic "$topic"
done

for label in "${labels[@]}"; do
  gh label create "$label" --force >/dev/null
  echo "label ensured: $label"
done

echo "Applied repository metadata. Configure rulesets per docs/REPOSITORY-SETUP.md."
