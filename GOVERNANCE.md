# Governance

## Stewardship

Kiyoshima Licensing Framework has a designated license steward. Stewardship may be assigned to a successor entity without retroactively changing an already published legal version.

## Immutable released legal versions

Once a legal version is declared final and tagged, its canonical text is immutable. Typographical, legal, policy, or semantic changes require a new legal version. The release registry records the digest of each frozen version.

## Open implementation surface

Framework tooling, schemas, integration code, workflows, and documentation are intentionally Apache-2.0 so third-party organizations can implement Kiyoshima support without negotiating rights merely to understand or validate the protocol.

## Machine metadata

Machine schemas and explanatory metadata may evolve independently when they do not change legal rights. A machine-schema change that materially changes permission semantics requires a new schema version.

## Conservative automation rule

No machine-readable file can silently expand a legal grant. An automation encountering malformed, absent, ambiguous, conflicting, unknown, or unauthenticated permission state must treat the relevant additional right as not established and surface the appropriate permission route.

## Public change process

Proposed legal changes should be discussed in public issues or pull requests before release. Release notes must identify legal changes, migration impact, and whether an older legal version remains supported.

## Privacy

Private commercial agreements and private Kiyoshima Grants do not belong in the public registry. Public registry entries must contain only intentionally publishable identity and scope information. Detached hashes may be published without publishing the private instrument itself.
