# Install / upgrade

The ZIP for this framework is intentionally **root-layout**: extract it directly into the root of the canonical licensing repository.

## Upgrade the current `moderubias/licensing` repository

Commit or stash any work first. Recommended:

```bash
git status
git switch -c licensing-framework-1.1-rc2
unzip -o /path/to/kiyoshima-licensing-framework-1.1.0-rc2.zip -d .
bash tools/migrate-from-framework-1.0.sh
bash tools/migrate-from-framework-1.0.sh --apply
python tools/klicense.py verify-framework
python -m unittest discover -s tests -v
git status
```

The first migration invocation is a dry run. The `--apply` invocation removes only known obsolete files left by the earlier bundle. `verify-framework` is strict and will fail if stale/unexpected files remain in the framework manifest.

When the diff is correct:

```bash
git add -A
git commit -S -m "Harden Kiyoshima Licensing Framework 1.1.0-rc2"
git push -u origin licensing-framework-1.1-rc2
```

Merge after review/CI. Then apply repository metadata/rename from the default branch:

```bash
bash tools/bootstrap-github.sh
bash tools/bootstrap-github.sh --apply --rename
```

Configure the branch/tag rulesets described in `docs/REPOSITORY-SETUP.md` manually after the repository rename.

## Fresh repository

For a fresh empty repository, extract the ZIP into the repository root and run:

```bash
python tools/klicense.py verify-framework
python -m unittest discover -s tests -v
```

No migration cleanup is needed.

## Optional CLI command

```bash
bash tools/install-cli.sh
klicense policy-summary .
```

This installs only a symlink in `~/.local/bin` (or `$XDG_BIN_HOME`) pointing back to this clone.

## Important release state

This bundle is a **hardened release candidate**, not the frozen legal `source-v1.0` release. `python tools/klicense.py release-check` is expected to fail until software/IP legal review is complete and the explicit finalization checklist in `docs/FORMALIZATION.md` / `docs/OPERATIONS.md` has been performed.

Do not create the final `source-v1.0` tag merely to make that command pass.
