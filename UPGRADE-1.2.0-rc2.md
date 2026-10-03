# Upgrade to Framework 1.2.0-rc2

Framework 1.2.0-rc2 is a project-layout/tooling correction over rc1. It does not
change Kiyoshima Source 1.0 rc.3 legal bytes and does not change Passport schema
1.3.

## Framework clone

From the installed framework clone:

```bash
cd "$(cd "$(dirname "$(readlink -f "$(command -v klicense)")")/.." && pwd)"
```

If rc1 changes are staged but not committed:

```bash
git reset
```

Back up the clone, apply the rc2 overlay from `~/Downloads`, then run:

```bash
klicense --version
klicense verify-framework
python3 -m unittest discover -s tests -v
python3 -m py_compile tools/klicense.py
git diff --check
```

## Project migration

Projects initialized by rc1 can be compacted without hand-deleting files:

```bash
klicense compact-project /path/to/project
klicense compact-project /path/to/project --apply
klicense verify-project /path/to/project
klicense doctor /path/to/project
```

The first command is a dry-run. The apply command creates an external backup and
removes only generated/redundant artifacts it recognizes safely.
