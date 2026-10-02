# Kiyoshima License Passport protocol

`KIYOSHIMA.json` is a project-local declaration intended for package tooling, CI, IDEs, AI agents, repository scanners, and humans.

## Decision order for automated systems

1. Locate `KIYOSHIMA.json`.
2. Verify `format` and `schema_version`.
3. Resolve the authoritative legal file named by `license.authoritative_file`.
4. Treat the legal file as controlling.
5. Use Passport fields as a normalized summary only.
6. If a requested right is `agreement-required` or `permission-required`, stop and surface the project's contact route.
7. If a separately authenticated Kiyoshima Grant is referenced, verify recipient identity, scope, version, and document authentication before expanding rights.
8. On unknown, missing, conflicting, or malformed state, do not infer permission.

## Design property

The protocol is deliberately one-way-safe: metadata can help a machine discover restrictions and permission paths, but unauthenticated metadata cannot create rights that the legal instrument did not grant.

## Suggested future integrations

- package-manager metadata adapters;
- IDE/agent preflight checks;
- organization license-policy engines;
- public adopter registry API;
- signed grant envelopes;
- transparency-log publication for released license bundles and grants where privacy permits.
