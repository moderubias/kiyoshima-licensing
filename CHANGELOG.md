# Changelog

## Framework 1.2.0-rc2 — lean project layout and safer migration

- Makes project generation lean by default: `NOTICE`, `REUSE.toml`, and README snippets are opt-in.
- Removes generated `LICENSE-MIT` / `LICENSE-APACHE` duplicates.
- Uses a short root dual-license notice plus canonical `LICENSES/MIT.txt` and `LICENSES/Apache-2.0.txt` for `MIT OR Apache-2.0`.
- Keeps canonical Apache-2.0 text byte-identical; its Appendix placeholders are intentionally not project metadata.
- Adds `compact-project` with dry-run-by-default planning, external backups, and conservative deletion of only recognized generated files.
- Stops forcing Source projects into duplicate REUSE license copies unless REUSE is explicitly requested or already present.
- Adds Rust/Cargo license-metadata diagnostics to `doctor`.
- Preserves Kiyoshima Source 1.0 rc.3 legal bytes and Passport schema 1.3 unchanged.

## Framework 1.2.0-rc1 — license-agnostic Open profile

- Upgrades Kiyoshima License Passport to schema 1.3.
- Removes Source-specific downstream-rights constraints from the generic Passport protocol.
- Adds one-command Kiyoshima Open initialization using `MIT`, `Apache-2.0`, or `MIT OR Apache-2.0` without renaming those legal licenses.
- Adds hashed supporting-license files to Passport metadata and verification.
- Adds Open-profile REUSE/NOTICE/README templates and a canonical MIT generation template.
- Makes Open AI preflight conservative: no extra Kiyoshima restriction, but standard license/applicable law still control.
- Adds rights matrix and source-available comparison documentation.
- Preserves Kiyoshima Source 1.0 rc.3 legal bytes unchanged.
- Adds `klicense --version` and upgrades Source sync/passport migration to schema 1.3.

## Framework 1.1.0-rc2 — hardened candidate

- Separates the framework repository's Apache-2.0 tooling/docs license from the Kiyoshima Source legal instrument.
- Clarifies that permitted Individuals may modify software for permitted freelance/tool use.
- Adds a bounded 30-day non-production Organization Evaluation grant.
- Adds explicit text-and-data-mining rights reservation language to the extent permitted by applicable law.
- Upgrades Kiyoshima License Passport to schema 1.2 with rights reservations, permission request routes, provenance, and declaration scope.
- Replaces self-referential grant hashes with detached digest/signature records.
- Makes public grant registry explicitly public-only; private grants should never be committed merely for registration.
- Adds `verify-manifest`, strict manifest coverage, project verification, project initialization, `doctor`, `query-right`, and safer registry commands.
- Adds a composite GitHub Action, Dependabot configuration, CODEOWNERS, security policy, repository hardening guidance, tests, and SHA-pinned GitHub Actions.
- Updates REUSE guidance to Specification 3.3.
- Clarifies that downstream recipients exercise Kiyoshima Source rights directly from the Licensor rather than through sublicensing.
- Adds Passport schema 1.2 protocol identity and normalized policy constraints.
- Adds operator `status`, agent/CI `preflight`, detached Rights Grant verification, and deployable TDMRep export commands.
- Corrects the TDM policy example to the TDMRep JSON-LD context required by the current Community Group report.

## Framework 1.0.0 — initial draft candidate

- Introduced Kiyoshima Source License 1.0 and the initial License Passport/tooling model.
