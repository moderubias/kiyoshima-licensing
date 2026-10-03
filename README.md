# Kiyoshima Licensing Framework

**One licensing protocol, two public software profiles: standard Open Source or Kiyoshima Source.**

Kiyoshima Licensing Framework combines legal instruments with a machine-readable
License Passport (`KIYOSHIMA.json`). The Passport is license-agnostic: it can
summarize a standard SPDX license expression or a Kiyoshima instrument without
relabeling or modifying the controlling legal terms.

The framework repository itself is Apache-2.0. The custom public legal instrument
is **Kiyoshima Source License 1.0** (`LicenseRef-Kiyoshima-Source-1.0`), which
remains a release candidate pending legal review.

## Model

```text
controlling legal license / agreement
              ↓
Kiyoshima License Passport (KIYOSHIMA.json)
              ↓
humans · agents · CI · IDEs · scanners · policy engines
              ↓
optional permission / commercial / AI grant routes
```

The machine layer is informational. It may summarize rights and constraints but
may not silently expand the legal grant.

## Profiles

- **Open** — Kiyoshima profile + standard ecosystem license. The CLI generates
  `MIT`, `Apache-2.0`, or `MIT OR Apache-2.0`. Kiyoshima Open is not a separate
  software license and does not modify those standard terms.
- **Source** — Kiyoshima Source 1.0: broad individual use, qualifying education
  and research, 30-day organization evaluation, and separate permission for
  organization production/commercial/hosted/model-improvement use.
- **Commercial** — negotiated terms for scopes that need warranties, SLAs,
  indemnities, proprietary distribution, production rights, support, or other
  negotiated obligations.

For the exact decision matrix, see `docs/RIGHTS-MATRIX.md` and
`docs/PROFILES.md`.

## License Passport 1.3

Schema 1.3 removes Source-specific assumptions from the generic protocol layer.
It supports:

- arbitrary controlling SPDX expressions or custom `LicenseRef-*` instruments;
- authoritative legal-file digest verification;
- optional digests for supporting license files;
- permission and AI-policy summaries;
- explicit rights reservations when the controlling instrument has them;
- permission-request routes;
- conservative conflict/missing-value behavior;
- profile-specific policy constraints instead of globally assuming the Source
  profile's downstream-rights model.

## CLI

The utility is zero-dependency Python.

```bash
klicense --version
klicense verify-framework
klicense status
```

Create an unrestricted OSS project under Apache-2.0:

```bash
klicense init-project /path/to/project \
  --profile open \
  --open-license Apache-2.0 \
  --name YourProject \
  --kind library \
  --repository https://github.com/owner/project \
  --holder "Copyright Holder"
```

Use `--open-license MIT` or `--open-license "MIT OR Apache-2.0"` when that is
the intended controlling legal expression.

Create a Kiyoshima Source project:

```bash
klicense init-project /path/to/project \
  --profile source \
  --name YourProduct \
  --kind application \
  --repository https://github.com/owner/product \
  --holder "Copyright Holder" \
  --contact https://github.com/owner/product/issues
```

Then:

```bash
klicense verify-project /path/to/project
klicense policy-summary /path/to/project
klicense preflight /path/to/project organization_production_use --json
```

`init-project` refuses to overwrite licensing files unless `--force` is used.
For existing Kiyoshima Source projects, `sync-project` creates an external backup
before updating the Passport/legal files.

## Repository layout

- `LICENSE` — Apache-2.0 for framework code/docs/tooling.
- `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` — Kiyoshima Source 1.0 candidate.
- `KIYOSHIMA.json` — framework/reference Passport.
- `machine/` — Passport/grant/registry schemas and TDM mapping.
- `templates/project/` — Source/Open project templates.
- `templates/licenses/` — standard-license generation templates.
- `agreements/` — Commercial, Grant, AI, and Contributor instruments.
- `tools/klicense.py` — initialization, validation, preflight, grants, registry,
  fingerprinting, monitoring, and TDM tooling.
- `docs/` — adoption, protocol, comparison, formalization, and operations docs.

## Status

Framework: **1.2.0-rc1**
Passport schema: **1.3**
Kiyoshima Source candidate: **1.0 rc.3**

Kiyoshima Source is source-available, not OSI Open Source. Its organization and
commercial restrictions intentionally conflict with unrestricted Open Source use.
The Source legal text is not being declared final until software/IP legal review
and the freeze procedure in `docs/FORMALIZATION.md` are complete.

Current Source candidate SHA-256:

`c3c5a834df1b0ef65b076aa4c8a233be1a17005016f60f6978a44ce0a17a6c85`
