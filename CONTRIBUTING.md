# Contributing

Changes to legal text are treated differently from ordinary documentation or tooling changes.

## Legal text

Do not submit silent edits to a released legal version. Before 1.0 is frozen, proposed changes must explain their semantic effect. After `source-v1.0`, any legal-text change targets a new legal version.

## Tooling, protocol, and metadata

Tooling, schemas, documentation, and registry improvements are welcome when they preserve the conservative machine-policy rule: metadata may restrict or explain, but unauthenticated metadata never creates rights beyond the legal instrument.

## Contributor rights

Material contributions may require acceptance of Kiyoshima Contributor Agreement 1.0 so projects can preserve public/commercial relicensing flexibility. Acceptance records should be attributable and durable.

## Security-sensitive changes

Changes to release workflows, integrity validation, signing/attestation behavior, or canonical digests should receive explicit review and must pass `python tools/klicense.py verify-framework` and the test suite.
