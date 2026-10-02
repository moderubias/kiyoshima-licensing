# Kiyoshima Licensing Framework

**Free for people. Free for learning. Free for qualifying research. Organizations evaluate, then ask.**

Kiyoshima Licensing Framework is a source-available licensing system built around a stable legal instrument and a machine-readable rights protocol. It separates ordinary human/agent use from organizational production rights and model-improvement rights, while providing a direct path to request additional permission.

The flagship legal instrument is **Kiyoshima Source License 1.0** (`Kiyoshima-Source-1.0`, SPDX reference `LicenseRef-Kiyoshima-Source-1.0`). This repository is the reference implementation and is itself Apache-2.0 for tooling and documentation; see `LICENSING.md`.

## The model

```text
legal instrument
      ↓ controls
Kiyoshima License Passport (KIYOSHIMA.json)
      ↓ summarizes conservatively
humans · agents · CI · IDEs · scanners · policy engines
      ↓ when extra rights are needed
Commercial / Grant / AI permission instruments
```

The machine layer can make restrictions and permission routes easier to discover. It can never silently expand the legal grant.

## Profiles

- **Open** — standard ecosystem licensing such as `MIT OR Apache-2.0` when frictionless adoption is the primary objective.
- **Source** — Kiyoshima Source 1.0: broad individual freedom, qualifying education/research, limited organization evaluation, and separately licensed organizational production/commercial/hosted/model-improvement use.
- **Commercial** — negotiated terms for organizations, proprietary distribution, SaaS, support, warranties, SLAs, and other scopes.

## Instruments

- **Kiyoshima Source 1.0** — public source-available software license.
- **Kiyoshima Commercial** — negotiated organization/commercial agreement.
- **Kiyoshima Grant** — targeted additional rights for a specific person or entity.
- **Kiyoshima AI 1.0** — model-training, dataset, and model-improvement rights.
- **Kiyoshima Contributor 1.0** — contributor copyright/patent grant preserving relicensing flexibility.

## License Passport

`KIYOSHIMA.json` is the project-local License Passport. Version 1.2 adds:

- stable legal-text digest;
- permission states for human and organizational use;
- operational-AI versus model-improvement semantics;
- explicit TDM/model-training rights reservations;
- machine-discoverable permission-request routes;
- conservative conflict behavior;
- optional authenticated grant references;
- normalized policy constraints such as evaluation duration and downstream-license semantics;
- a stable protocol identity for agent/CI integrations.

An automated system encountering missing, malformed, unknown, conflicting, or unauthenticated permission state must not infer extra rights.

## CLI

The zero-dependency utility is `tools/klicense.py`.

```bash
python tools/klicense.py verify-framework
python tools/klicense.py doctor .
python tools/klicense.py status
python tools/klicense.py init-project /path/to/project \
  --name GutenMorgen \
  --kind application \
  --repository https://github.com/moderubias/GutenMorgen \
  --holder "Akayo Kiyoshima" \
  --contact https://github.com/moderubias/kiyoshima-licensing/issues
python tools/klicense.py verify-project /path/to/project
python tools/klicense.py sync-project /path/to/existing-project --dry-run
python tools/klicense.py query-right /path/to/project organization_production_use
python tools/klicense.py preflight /path/to/project model_training --json
python tools/klicense.py verify-grant /path/to/KRG-2026-0001.record.json
python tools/klicense.py export-tdm --origin https://example.com --rightsholder "Akayo Kiyoshima" --contact https://example.com/licensing --output-dir ./tdm-deploy
python tools/klicense.py fingerprint /path/to/project
```

`init-project` is non-destructive by default and refuses to overwrite existing licensing files unless `--force` is supplied. `sync-project` upgrades an existing Kiyoshima Source project using an external backup before changing its legal bytes or Passport. See `docs/OPERATIONS.md` for the day-to-day workflow. Optionally run `tools/install-cli.sh` once to expose the executable as `klicense` through `~/.local/bin`.

## Repository layout

- `INSTALL.md` — safe fresh-install / upgrade procedure.
- `LICENSE` — Apache-2.0 for this framework repository's code/docs/tooling.
- `LICENSING.md` — repository licensing map.
- `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` — canonical Kiyoshima Source 1.0 candidate text.
- `KIYOSHIMA.json` — reference License Passport.
- `agreements/` — Commercial, Grant, AI, and Contributor instruments.
- `machine/` — schemas, examples, protocol details, and TDM mapping guidance.
- `registry/` — release, owned-project, public-grant, and adopter records.
- `monitor/` — optional public-source monitoring queries.
- `templates/project/` — project metadata templates; the CLI copies the canonical legal text directly.
- `tools/klicense.py` — validator, initializer/synchronizer, rights-query interface, grant generator, fingerprint generator, registry helper, and monitor.
- `docs/OPERATIONS.md` — day-to-day operator runbook.
- `action.yml` — composite GitHub Action for project policy verification after a tagged release.

## Status

**Kiyoshima Source 1.0 remains a release candidate until legal review and an explicit freeze.** The candidate text must not be silently changed after a final `source-v1.0` release.

Kiyoshima Source is **source-available, not OSI open source**. Its organizational/commercial restrictions intentionally do not satisfy the Open Source Definition.

Current candidate revision: **rc.3**

Current candidate legal-text digest:

`sha256:c3c5a834df1b0ef65b076aa4c8a233be1a17005016f60f6978a44ce0a17a6c85`

## Adoption

Another developer may apply an exact, unmodified Kiyoshima Source 1.0 text to their own software without transferring ownership to Kiyoshima or joining any organization. The framework's Apache-2.0 tooling is intentionally available to companies, package tooling, IDEs, scanners, and AI-agent vendors that want to implement support for the License Passport protocol.

Start with `docs/ADOPTION.md` and `docs/FORMALIZATION.md`.
