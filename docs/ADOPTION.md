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
license expression remains the controlling legal license. The generator creates
`KIYOSHIMA.json`, `NOTICE`, `REUSE.toml`, the relevant `LICENSES/` files, and a
README snippet. For dual MIT/Apache it also creates `LICENSE-MIT` and
`LICENSE-APACHE`.

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

The initializer copies the exact Kiyoshima Source candidate bytes and creates
its `LicenseRef-*` REUSE file. `--contact` is required because organization,
commercial, evaluation-extension, and AI rights may need a route to the
licensor.

## Existing Source projects

Use a dry run first:

```bash
klicense sync-project /path/to/project --dry-run
klicense sync-project /path/to/project
```

The apply step creates an external timestamped backup before updating the legal
files/Passport. The Source `rc.3` legal bytes are unchanged in Framework
1.2.0-rc1; the main migration is Passport schema 1.3 plus supporting-file
integrity metadata.

## Manual adoption invariant

Do not claim Kiyoshima, MIT, Apache, or any other license over third-party
material you do not have authority to license. Keep dependency/vendor license
boundaries intact and represent exceptions explicitly.

## Optional CI

After a stable framework release exists, projects can use the composite action
to verify a Passport or run preflight. Pin the action to a full immutable commit
SHA rather than a moving branch/tag.
