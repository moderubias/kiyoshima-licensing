# Versioning

The framework version, Passport schema version, and legal-license version are independent.

- `Kiyoshima Source License 1.0` — legal version; currently a release candidate until explicitly frozen.
- `Kiyoshima License Passport schema 1.2` — machine metadata schema.
- `Kiyoshima Licensing Framework 1.1.0-rc2` — tooling/docs/framework release candidate.

## Legal version rule

Once `Kiyoshima Source License 1.0` is declared final and released as `source-v1.0`, its canonical bytes are immutable. Any later textual change, including an editorial change that could affect matching or interpretation, requires a new legal version and a new digest.

Projects remain on the exact legal version they declared unless their copyright holder affirmatively relicenses them.

## Framework version rule

Framework tooling/docs may evolve independently when they do not change the legal rights expressed by an already frozen legal version. Breaking machine-schema changes require a new schema version.

Recommended tags after legal review:

- `source-v1.0` — frozen legal text;
- `framework-v1.1.0` — first stable hardened framework release.
