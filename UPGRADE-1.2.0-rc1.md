# Local upgrade: 1.1.0-rc2 -> 1.2.0-rc1

The downloaded archive is expected at:

`~/Downloads/kiyoshima-licensing-framework-1.2.0-rc1-overlay.zip`

Run:

```bash
KLICENSE_BIN="$(command -v klicense)"
KLICENSE_SCRIPT="$(readlink -f "$KLICENSE_BIN")"
KLICENSE_ROOT="$(cd "$(dirname "$KLICENSE_SCRIPT")/.." && pwd)"
cd "$KLICENSE_ROOT"

git status
git switch -c licensing-framework-1.2-rc1
BACKUP="../kiyoshima-licensing.backup-$(date -u +%Y%m%dT%H%M%SZ)"
cp -a . "$BACKUP"

unzip -o ~/Downloads/kiyoshima-licensing-framework-1.2.0-rc1-overlay.zip -d .

klicense --version
klicense verify-framework
python3 -m unittest discover -s tests -v
python3 -m py_compile tools/klicense.py
git status --short
```

The existing `klicense` symlink should continue to work because the overlay
updates its target file in place. If it does not:

```bash
bash tools/install-cli.sh
```

Do not run the old `migrate-from-framework-1.0.sh` for this 1.1 -> 1.2 overlay;
there are no intentional file removals in this upgrade.
