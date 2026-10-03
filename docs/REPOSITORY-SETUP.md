# Canonical GitHub repository setup

Recommended repository name: `kiyoshima-licensing`.

Recommended description:

> Machine-readable software licensing profiles: standard Open Source or Kiyoshima Source, with Passport validation, AI/TDM semantics, grants and provenance.

Recommended topics:

`kiyoshima-open`, `kiyoshima-source`, `source-available`, `software-licensing`, `machine-readable-licensing`, `ai-licensing`, `license-passport`, `spdx`, `reuse`, `provenance`, `software-law`

Recommended settings:

- Issues: enabled
- Wiki: disabled
- Projects: disabled unless actively used
- Discussions: optional after real third-party adoption
- Delete head branches after merge: enabled
- Default branch: `main`

Recommended `main` ruleset:

- block force pushes and deletion;
- require pull request before merging once outside contributors exist;
- require the `verify` status check from License integrity;
- require conversation resolution;
- require signed commits if it does not break your contribution workflow;
- require linear history if you prefer squash/rebase history.

Recommended release-tag ruleset for `source-v*` and `framework-v*`:

- restrict deletion and force update;
- restrict tag creation to maintainers/release automation.

GitHub Actions should use least-privilege permissions and third-party actions pinned to full commit SHAs. Dependabot is configured to propose updates to pinned GitHub Actions.
