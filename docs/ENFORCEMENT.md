# Enforcement and monitoring

## Evidence, not magic

Git history, signed commits/tags, immutable release hashes, release artifacts, attestations, archived snapshots, and project fingerprints improve provenance and evidence quality. They do not automatically prove infringement.

## Monitoring layers

1. **Adoption discovery** — search public code for `LicenseRef-Kiyoshima-Source-1.0`, the canonical license name, and registered project identifiers.
2. **Project fingerprint watch** — maintain carefully chosen distinctive public-source queries for high-value projects in `monitor/targets.json`.
3. **Triage** — distinguish known adopters/owned projects from unknown matches; a match is a lead, not a conclusion.
4. **Private evidence capture** — preserve URL, commit SHA, timestamps, relevant files, screenshots where useful, and applicable license/version. Do not commit sensitive enforcement evidence to this public repository.
5. **Rights check** — determine whether an Additional Permission, commercial agreement, mandatory exception, independent creation, or other lawful basis applies.
6. **Remedy** — use notice/cure, negotiation, platform processes, or formal enforcement as appropriate.

Do not add covert telemetry merely to detect violations. It creates privacy/security liabilities and is easily removed.

## Monitoring tool

`python tools/klicense.py monitor` queries GitHub public code search using `monitor/targets.json`. Reports classify repositories already present in the owned-project/adopter registries separately from unknown candidates.
