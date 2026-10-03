# Kiyoshima License Passport protocol

`KIYOSHIMA.json` is a project-local declaration for package tooling, CI, IDEs,
AI agents, repository scanners, policy engines, and humans. Schema 1.3 is
license-agnostic: it can describe a standard SPDX license expression, a custom
`LicenseRef-*`, or another controlling instrument represented by the project.

## Decision order

1. Locate `KIYOSHIMA.json`.
2. Verify `format`, `schema_version`, and `declaration_scope`.
3. Resolve `license.authoritative_file` inside the project root.
4. Verify `license.sha256`.
5. Verify any optional `license.supporting_files` digests.
6. Treat the controlling legal instrument as authoritative.
7. Use Passport fields only as a normalized summary.
8. If a requested right is `agreement-required` or `permission-required`, stop
   and surface the relevant `permission_requests` route.
9. Verify any authenticated additional grant before expanding rights.
10. Apply `policy_constraints` only as hints subordinate to the legal text.
11. On unknown, missing, malformed, conflicting, or unauthenticated state, do
    not infer permission.

## State vocabulary

General permission states:

- `allowed`
- `allowed-with-conditions`
- `agreement-required`
- `permission-required`
- `reserved`
- `not-granted`

The AI section can use `allowed-within-principal-rights` for delegated tools or
`no-additional-kiyoshima-restriction` where the profile adds no independent AI-specific
grant or restriction. The latter is intentionally mapped to a conditional
preflight result.

## Profile-specific constraints

Schema 1.3 no longer assumes every Passport uses Kiyoshima Source semantics.
Source Passports still require Source-specific constraints such as the 30-day
organization evaluation and direct-from-licensor downstream-rights model. Open
Passports instead carry standard-license conditions and explicitly state that
Kiyoshima adds no field-of-use restriction.

## Design property

Metadata is one-way-safe: it can make restrictions and routes discoverable, but
it cannot create legal permission beyond the controlling instrument.
