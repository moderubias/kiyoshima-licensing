# Licensing profiles

## Open

Use Kiyoshima Open when third parties should be able to use the project,
including commercially, under a standard Open Source license without asking you
for organization-specific permission.

The Kiyoshima profile is metadata/tooling. The controlling legal license remains
its standard SPDX license. The CLI currently generates:

- `Apache-2.0` — useful default when an explicit patent grant and NOTICE model are
  desirable;
- `MIT` — minimal permissive terms;
- `MIT OR Apache-2.0` — recipient chooses either license.

Do not rename these licenses as “Kiyoshima MIT”, “Kiyoshima Apache”, or another
name that suggests Kiyoshima authored or modified their legal terms.

Typical Open targets: libraries, SDKs, protocols, crates/packages,
interoperability layers, developer tools, and infrastructure intended for broad
adoption.

## Source

Use Kiyoshima Source 1.0 when source visibility and broad individual freedom are
desired but organization production use, commercial distribution, hosted
commercial exploitation, and model-improvement use should require separate
permission.

The current candidate includes a bounded 30-day non-production organization
evaluation right. It is source-available and is not an OSI Open Source license.

Typical Source targets: products whose code you want public/inspectable while
reserving commercial organization deployment or productization for negotiated
rights.

## Commercial

Use a separate negotiated agreement when the relationship needs production
rights, proprietary redistribution, SaaS rights, support, SLAs, warranties,
indemnities, negotiated liability, extended evaluation, or jurisdiction-specific
terms.

The public framework does not pretend that one static public license can replace
all commercial contracting.

## Ownership boundary

A profile can only be applied to code and other material you have authority to
license. Dependencies, vendored components, copied code, assets, datasets, and
contributions may remain under their own licenses. Kiyoshima metadata must not
claim to relicense third-party material.
