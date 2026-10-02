# Kiyoshima Licensing Framework

**Free for people. Free for learning. Free for qualifying research. Organizations ask first.**

The Kiyoshima Licensing Framework is a licensing system for source-available software that combines a stable legal text with machine-readable policy, explicit commercial and AI permission instruments, provenance, integrity checks, and an adoption registry.

The flagship license is **Kiyoshima Source License 1.0** (`Kiyoshima-Source-1.0`, SPDX reference `LicenseRef-Kiyoshima-Source-1.0`).

## What is different

The framework has two surfaces:

1. **Legal surface** — immutable versioned license text and signed agreements.
2. **Machine surface** — `KIYOSHIMA.json`, schemas, hashes, registry records, and conservative automation rules.

The machine surface never silently expands legal rights. When the two disagree, the legal instrument controls and automated tools should deny or request permission.

## Profiles

- **Open** — use a standard ecosystem license such as `MIT OR Apache-2.0` when adoption is more valuable than licensing control.
- **Source** — Kiyoshima Source License 1.0 for products and source-available tools.
- **Commercial** — negotiated proprietary/commercial terms.

## Instruments

- **Kiyoshima Source 1.0** — public source-available license.
- **Kiyoshima Commercial** — negotiated organizational/commercial agreement.
- **Kiyoshima Grant** — targeted additional rights for a person or entity.
- **Kiyoshima AI 1.0** — additional model-training/dataset permissions.
- **Kiyoshima Contributor 1.0** — contributor copyright/patent grant preserving relicensing ability.

## Repository layout

- `LICENSE` — human-readable legal text.
- `LICENSES/` — canonical custom-license text for SPDX/REUSE workflows.
- `KIYOSHIMA.json` — this repository's License Passport.
- `agreements/` — commercial, grant, AI, and contributor instruments.
- `machine/` — schemas and protocol description.
- `registry/` — version hashes, project registry, and adopter registry.
- `monitor/` — optional public-source monitoring configuration.
- `templates/project/` — files to copy into a project.
- `tools/klicense.py` — zero-dependency local validator, hasher, fingerprint generator, and optional GitHub monitor.
- `docs/` — adoption, governance, formalization, AI, and enforcement guidance.

## Applying Kiyoshima Source 1.0 to a project

Copy `LICENSES/LicenseRef-Kiyoshima-Source-1.0.txt` to the project's root as `LICENSE`, copy and edit `templates/project/KIYOSHIMA.json`, add the notice from `templates/project/README-LICENSING.md`, and add copyright/SPDX metadata to source files where practical.

For an ecosystem library where frictionless downstream adoption is the primary objective, use the **Open** profile instead of Kiyoshima Source 1.0.

## Status

Version 1.0 is designed to be frozen once formally released. New legal terms require a new version. Do not silently edit a published license version.

Kiyoshima Source License 1.0 is **source-available, not OSI open source**. Its organizational and commercial-use restrictions intentionally do not satisfy the Open Source Definition.

## Legal review

This repository is a serious drafting and operational framework, not a substitute for jurisdiction-specific legal advice. Before relying on it for material commercial enforcement, obtain review from a software/IP lawyer in the jurisdictions that matter to you.
