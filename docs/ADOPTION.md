# Adoption

## Open profile

Use Open when third parties should be able to use the project under standard
Open Source terms without asking Kiyoshima or the project author for separate
commercial permission.

Apache-2.0 example:

```bash
klicense init-project /path/to/project \
  --profile open \
  --open-license Apache-2.0 \
  --name "YourProject" \
  --kind library \
  --repository "https://github.com/owner/repo" \
  --holder "Copyright Holder"

klicense verify-project /path/to/project
```

Alternative expressions supported by the generator:

```bash
--open-license MIT
--open-license "MIT OR Apache-2.0"
```

The project is branded/profiled as **Kiyoshima Open**, but the standard SPDX
license expression remains the controlling legal license. The default layout is
intentionally lean:

- `MIT` or `Apache-2.0`: `LICENSE` + `KIYOSHIMA.json`;
- `MIT OR Apache-2.0`: a short root `LICENSE`, `LICENSES/MIT.txt`,
  `LICENSES/Apache-2.0.txt`, and `KIYOSHIMA.json`.

`NOTICE`, `REUSE.toml`, and README snippets are not generated unless requested.
Use `--notice`, `--reuse`, or `--readme-snippet docs/README-LICENSING.md` when
those artifacts are actually useful. The generator never creates redundant
`LICENSE-MIT` / `LICENSE-APACHE` copies.

## Compact an older generated layout

Framework 1.2.0-rc1 generated duplicate root license files and optional metadata
unconditionally. Preview a safe cleanup first:

```bash
klicense compact-project /path/to/project
```

Apply only after reviewing the plan:

```bash
klicense compact-project /path/to/project --apply
klicense verify-project /path/to/project
klicense doctor /path/to/project
```

The apply step creates an external timestamped backup. Customized `NOTICE`,
`REUSE.toml`, or licensing snippets are preserved rather than silently deleted.


## Source profile

```bash
klicense init-project /path/to/project \
  --profile source \
  --name "YourProduct" \
  --kind application \
  --repository "https://github.com/owner/repo" \
  --holder "Copyright Holder" \
  --contact "https://github.com/owner/repo/issues"

klicense verify-project /path/to/project
```

The initializer copies the exact Kiyoshima Source candidate bytes to root
`LICENSE` and creates `KIYOSHIMA.json`. A duplicate `LicenseRef-*` file and
`REUSE.toml` are created only with `--reuse`. `--contact` is required because
organization, commercial, evaluation-extension, and AI rights may need a route
to the licensor.

## Existing Source projects

Use a dry run first:

```bash
klicense sync-project /path/to/project --dry-run
klicense sync-project /path/to/project
```

The apply step creates an external timestamped backup before updating the legal
files/Passport. The Source `rc.3` legal bytes are unchanged in Framework
1.2.0-rc2; the main migration is Passport schema 1.3 plus supporting-file
integrity metadata.

## Manual adoption invariant

Do not claim Kiyoshima, MIT, Apache, or any other license over third-party
material you do not have authority to license. Keep dependency/vendor license
boundaries intact and represent exceptions explicitly.

## Optional CI

After a stable framework release exists, projects can use the composite action
to verify a Passport or run preflight. Pin the action to a full immutable commit
SHA rather than a moving branch/tag.
