# Adoption

## Source profile: recommended workflow

From a clone of the canonical framework repository:

```bash
python tools/klicense.py init-project /path/to/your/project \
  --name "YourProject" \
  --kind application \
  --repository "https://github.com/owner/repo" \
  --holder "Copyright Holder" \
  --contact "https://github.com/owner/repo/issues"

python tools/klicense.py verify-project /path/to/your/project
```

The initializer refuses to overwrite existing licensing files unless `--force` is explicitly supplied.

It creates the exact Kiyoshima legal text, `KIYOSHIMA.json`, `NOTICE`, `REUSE.toml`, and a README licensing snippet without rewriting your existing README.

## Manual adoption

1. Choose `Open`, `Source`, or `Commercial` profile.
2. For Source, copy the exact canonical legal text from `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` to the project's root `LICENSE` and to `LICENSES/LicenseRef-Kiyoshima-Source-1.0.txt`.
3. Copy/edit `templates/project/KIYOSHIMA.json`.
4. Copy/edit `templates/project/NOTICE.template` as `NOTICE`.
5. Merge `templates/project/README-LICENSING.md` into the project README.
6. Add source SPDX metadata where practical or use `REUSE.toml` mappings.
7. Preserve the legal text exactly. Put project-specific facts in `NOTICE` and `KIYOSHIMA.json`, not inside the legal text.
8. Optionally register the project in the canonical adopter registry.

## Why another developer might adopt it

Kiyoshima Source is intentionally opinionated: broad freedom for natural persons, qualifying learning/research, low-friction organization evaluation, and a direct permission boundary for organizational production/commercial/model-improvement use.

The adoption value is the surrounding protocol:

- stable canonical legal bytes and digest;
- machine-readable License Passport;
- agent delegation semantics;
- explicit model-training/TDM reservation;
- discoverable permission-request paths;
- standardized Commercial, Grant, AI, and Contributor instruments;
- integrity and release provenance;
- optional adopter registry and monitoring;
- Apache-2.0 reference tooling that vendors can integrate freely.

A third-party project can use the exact license without transferring project ownership or joining any organization.

## Registry model

Adoption registration is optional. Registration is evidence of a public declaration, not certification of legal compliance. Private grants and agreements should not be published merely to obtain a registry entry.

## Optional CI verification

After a stable framework release exists, a project may invoke the repository's composite GitHub Action to verify its Passport and legal bytes on every change. Pin the action to the full commit SHA of the framework release rather than a moving branch or tag.

```yaml
name: License policy
on: [push, pull_request]
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@FULL_COMMIT_SHA
      - uses: moderubias/kiyoshima-licensing@FULL_FRAMEWORK_COMMIT_SHA
        with:
          path: .
```

The placeholder SHAs are intentional. Replace them with verified immutable commits; do not copy this example literally. The composite Action also supports `mode: preflight`, an `action` key such as `model_training`, and optional `strict: true` for policy-gated CI workflows.
