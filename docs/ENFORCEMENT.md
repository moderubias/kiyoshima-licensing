# Enforcement and monitoring

## What the framework can prove

Git history, signed tags, immutable release hashes, release artifacts, attestations, archived snapshots, and project fingerprints improve provenance and evidence quality. They do not automatically prove infringement.

## Monitoring layers

1. **Adoption discovery** — search public code for `LicenseRef-Kiyoshima-Source-1.0`, the canonical license name, and registered project identifiers.
2. **Project fingerprint watch** — maintain carefully chosen distinctive search queries for high-value projects in `monitor/targets.json`.
3. **Evidence capture** — when a suspicious match appears, preserve repository URL, commit SHA, timestamps, relevant files, screenshots where useful, and the applicable license/version before contacting the other party.
4. **Legal review** — check whether the observed use is actually prohibited, whether an Additional Permission exists, and whether an exception or limitation under applicable law could apply.
5. **Remedy** — use notice/cure, platform processes, negotiation, or formal enforcement as appropriate.

Do not use telemetry or covert tracking merely to catch license violations. It creates privacy/security liabilities and is easily removed.

## Monitoring tool

`tools/klicense.py monitor` can query GitHub's public code-search API using explicit queries from `monitor/targets.json`. It is a lead generator, not an infringement detector. False positives require human review.
