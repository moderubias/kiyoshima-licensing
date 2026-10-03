# Install / upgrade

## Upgrade Framework 1.1.0-rc2 to 1.2.0-rc1 from Downloads

This overlay archive is designed to be extracted over the existing framework
clone. It does not contain `.git` or `.venv`.

If `klicense` is already installed with `tools/install-cli.sh`, it is normally a
symlink to `tools/klicense.py` inside the framework clone. Updating that clone
therefore updates the command automatically; reinstalling the symlink is not
required.

Locate the clone through the installed command:

```bash
KLICENSE_BIN="$(command -v klicense)"
KLICENSE_SCRIPT="$(readlink -f "$KLICENSE_BIN")"
KLICENSE_ROOT="$(cd "$(dirname "$KLICENSE_SCRIPT")/.." && pwd)"
printf 'klicense: %s\nframework: %s\n' "$KLICENSE_BIN" "$KLICENSE_ROOT"
cd "$KLICENSE_ROOT"
```

Before overwriting files:

```bash
git status
```

Commit/stash unrelated work first. Then create an upgrade branch and a local
filesystem backup:

```bash
git switch -c licensing-framework-1.2-rc1
BACKUP="../kiyoshima-licensing.backup-$(date -u +%Y%m%dT%H%M%SZ)"
cp -a . "$BACKUP"
echo "$BACKUP"
```

Apply the archive that was downloaded to `~/Downloads`:

```bash
unzip -o ~/Downloads/kiyoshima-licensing-framework-1.2.0-rc1-overlay.zip -d .
```

Verify the installed command and framework:

```bash
klicense --version
klicense verify-framework
python3 -m unittest discover -s tests -v
python3 -m py_compile tools/klicense.py
git status --short
```

Expected version output begins with:

```text
klicense 1.2.0-rc1 (Passport schema 1.3)
```

If `command -v klicense` no longer resolves to this clone, reinstall only the
symlink:

```bash
bash tools/install-cli.sh
```

## Existing Kiyoshima Source projects

Framework 1.2.0-rc1 does **not** change Source 1.0 rc.3 legal bytes. To move an
existing Source project's Passport to schema 1.3, preview and then apply:

```bash
klicense sync-project /path/to/project --dry-run
klicense sync-project /path/to/project
```

`sync-project` creates an external timestamped backup before writing project
licensing files.

For a non-Source Passport that is already manually configured on schema
1.0/1.1/1.2:

```bash
klicense upgrade-passport /path/to/project/KIYOSHIMA.json --dry-run
klicense upgrade-passport /path/to/project/KIYOSHIMA.json
klicense verify-project /path/to/project
```

## Fresh framework clone

The overlay is intended for the existing 1.1.0-rc2 tree. For a fresh clone, use
the complete repository/release rather than treating the overlay as a standalone
source distribution.

## Release state

Kiyoshima Source 1.0 remains a legal release candidate. `klicense release-check`
is expected to fail until software/IP legal review and the explicit final freeze
are completed. Do not create `source-v1.0` merely to make the command pass.
