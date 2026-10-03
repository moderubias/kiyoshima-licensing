# Versioning

The framework version, Passport schema version, and legal-license version are
independent.

- `Kiyoshima Source License 1.0` — legal version; still release-candidate rc.3.
- `Kiyoshima License Passport schema 1.3` — license-agnostic machine metadata.
- `Kiyoshima Licensing Framework 1.2.0-rc1` — tooling/docs/framework candidate.

## Legal version rule

Once Kiyoshima Source 1.0 is declared final and released as `source-v1.0`, its
canonical legal bytes are immutable. Textual or semantic changes require a new
legal version and digest. Framework or Passport changes do not silently
relicense existing software.

## Passport rule

Passport schemas can evolve independently when machine metadata changes do not
alter the controlling legal grant. Schema 1.3 removes Source-only assumptions
from the generic protocol while preserving Source-specific validation when the
Source profile is declared.

## Framework rule

Framework tooling/docs may evolve independently from the Source legal text.
Framework 1.2.0-rc1 leaves Source rc.3 legal bytes unchanged.
