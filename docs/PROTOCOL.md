# Kiyoshima License Passport protocol

`KIYOSHIMA.json` is a project-local declaration intended for package tooling, CI, IDEs, AI agents, repository scanners, policy engines, and humans.

## Decision order for automated systems

1. Locate `KIYOSHIMA.json`.
2. Verify `format`, supported `schema_version`, and `declaration_scope`.
3. Resolve the authoritative legal file named by `license.authoritative_file`.
4. Verify the legal file digest when `license.sha256` is present.
5. Treat the legal instrument as controlling.
6. Use Passport fields as a normalized summary only.
7. If a requested right is `agreement-required` or `permission-required`, stop and surface the relevant `permission_requests` route.
8. If an authenticated Kiyoshima Grant is referenced, verify recipient identity, covered scope, version range, detached digest/signature/attestation, and conditions before expanding rights.
9. Apply `policy_constraints` as normalized hints only after the controlling license state is established.
10. On unknown, missing, malformed, conflicting, or unauthenticated state, do not infer permission.

## State vocabulary

Recommended permission states are:

- `allowed`
- `allowed-with-conditions`
- `agreement-required`
- `permission-required`
- `reserved`
- `not-granted`

Tools may display richer legal explanations, but they must not invent an `allowed` state. Schema 1.2 also carries a stable protocol identity and normalized constraints such as the organization-evaluation duration, attribution/source obligations, downstream-rights model, and AI-provider boundary.

## Agent/CI preflight

`klicense preflight PATH ACTION --json` converts a declared action key into a conservative machine decision plus relevant constraints and a permission-request route. It is intentionally not a legal reasoner: it does not infer facts about the caller, applicable law, fair use, mandatory exceptions, or private agreements that have not been authenticated. `--strict` provides stable non-zero exit classes for conditional, permission-required, and unknown states.

## Rights reservations

`rights_reservations` provides an explicit machine-readable notice for areas such as model training, reusable dataset construction, and non-research text/data mining. It is informational and does not override mandatory law.

For HTTP content under an operator's control, `machine/tdm/` shows how this intent can be mapped to the W3C Community Group TDM Reservation Protocol (`tdm-reservation: 1` plus a policy URL).

## Design property

The protocol is deliberately one-way-safe: metadata can help a machine discover restrictions and permission paths, but unauthenticated metadata cannot create rights that the legal instrument did not grant.

## Future-compatible integrations

- package-manager metadata adapters;
- IDE/agent preflight checks;
- organization license-policy engines;
- public adopter registry API;
- detached signed grant envelopes;
- transparency-log publication for public release bundles and grants where privacy permits;
- SPDX 3.x custom-license representations and SBOM integration.
