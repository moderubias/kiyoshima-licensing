# Operations

This is the practical operating guide for the Kiyoshima Licensing Framework.

## Optional: install the CLI name

From the framework repository:

```bash
bash tools/install-cli.sh
```

This creates a symlink in `${XDG_BIN_HOME:-$HOME/.local/bin}` so the same commands can be invoked as `klicense ...`. The CLI still uses the canonical framework files from this clone. Run `bash tools/install-cli.sh --uninstall` to remove only that symlink.

## 1. Check operator status

```bash
python tools/klicense.py status
python tools/klicense.py status --json
```

This summarizes the current legal candidate/final state, digest, Passport schema, integrity, owned projects, adopters, public grants, monitor queries, and local finalization blockers.

## 2. Verify the canonical framework

Run after every framework change:

```bash
python tools/klicense.py manifest --write
python tools/klicense.py verify-framework
python -m unittest discover -s tests -v
```

`release-check` is intentionally stricter. It must fail while Kiyoshima Source 1.0 is a release candidate and should pass only after legal review and an explicit final freeze.

```bash
python tools/klicense.py release-check
```

## 3. Initialize a new project

For an unrestricted OSS project:

```bash
klicense init-project /path/to/project \
  --profile open \
  --open-license Apache-2.0 \
  --name PROJECT_NAME \
  --kind library \
  --repository https://github.com/OWNER/REPO \
  --holder "COPYRIGHT HOLDER"
```

For a Kiyoshima Source product:

```bash
klicense init-project /path/to/project \
  --profile source \
  --name PROJECT_NAME \
  --kind application \
  --repository https://github.com/OWNER/REPO \
  --holder "COPYRIGHT HOLDER" \
  --contact https://github.com/OWNER/REPO/issues
```

Then:

```bash
klicense verify-project /path/to/project
klicense doctor /path/to/project
```

The default project layout is lean. `NOTICE`, `REUSE.toml`, and a generated
README snippet are opt-in. For example, request a docs snippet explicitly with
`--readme-snippet docs/README-LICENSING.md`.

## 4. Compact a Framework 1.2.0-rc1 project

Preview:

```bash
klicense compact-project /path/to/project
```

Apply:

```bash
klicense compact-project /path/to/project --apply
```

The command backs up every file it changes or removes outside the project. It
removes only generated/redundant artifacts it can recognize byte-for-byte;
customized files are preserved.

## 5. Sync an existing Kiyoshima Source project

Preview first:

```bash
python tools/klicense.py sync-project /path/to/project --dry-run
```

Apply:

```bash
python tools/klicense.py sync-project /path/to/project
```

The command backs up the affected licensing files outside the project directory before replacing the legal text and Passport. It deliberately does not rewrite project README or NOTICE prose automatically.

## 6. Ask the Passport a rights question

Humans, agents, CI, and policy tooling can query normalized state:

```bash
python tools/klicense.py query-right /path/to/project organization_production_use
python tools/klicense.py query-right /path/to/project model_training --json
```

An unknown key remains unknown. The CLI never turns missing metadata into permission.

## 7. Agent/CI preflight

For a conservative machine decision about one declared action:

```bash
python tools/klicense.py preflight /path/to/project organization_production_use --json
python tools/klicense.py preflight /path/to/project model_training --json --strict
```

Without `--strict`, preflight is informational and exits successfully even when permission is required. With `--strict`, exit code `0` means allowed within declared scope, `10` means allowed with conditions, `20` means permission is required/not granted by the public license, and `30` means unknown. Invalid Passports use exit code `4`. The legal text always controls.

## 8. Register an owned project

From the canonical framework repository:

```bash
python tools/klicense.py register-project \
  --name GutenMorgen \
  --repository https://github.com/moderubias/GutenMorgen \
  --profile source
```

For an Open-profile project, record the controlling SPDX expression explicitly, for example `--profile open --license "MIT OR Apache-2.0"`. Commercial registry entries likewise require `--license` rather than silently inheriting the Source identifier.

Commit the registry change. The registry is public metadata, not the source of legal rights.

## 9. Issue a private or public Rights Grant

Example:

```bash
python tools/klicense.py new-grant \
  --grant-id KRG-2026-0001 \
  --issuer "Akayo Kiyoshima" \
  --project "GutenMorgen" \
  --grantee-github example \
  --right modify \
  --right commercial_use \
  --visibility private \
  --output-dir ../private-grants
```

The command creates the grant, a detached SHA-256 file, and a machine record. Authenticate the final grant with a signature or attributable platform record. Do not publish private grants in `registry/grants.public.json`.

After creating or receiving a grant, verify its detached digest:

```bash
python tools/klicense.py verify-grant ../private-grants/KRG-2026-0001.record.json
```

Digest verification does not itself verify a pending external signature; it proves only that the document bytes match the recorded digest.

## 10. Fingerprint a commercially important project

```bash
python tools/klicense.py fingerprint /path/to/project --output /secure/path/project-fingerprint.json
```

A fingerprint supports provenance comparison. It is not proof that a later match is infringing.

## 11. Monitor public discovery signals

Add carefully chosen public-code queries to `monitor/targets.json`, then run:

```bash
KIYOSHIMA_MONITOR_TOKEN=... python tools/klicense.py monitor
python tools/klicense.py summarize-watch kiyoshima-watch.json
```

The scheduled GitHub workflow can do this automatically. Search results are leads only and require human review.

## 12. Export TDM reservation metadata for an origin you control

```bash
python tools/klicense.py export-tdm \
  --origin https://example.com \
  --rightsholder "Akayo Kiyoshima" \
  --contact https://example.com/licensing \
  --output-dir ./tdm-deploy
```

Deploy the generated `/.well-known/tdmrep.json` and policy JSON-LD only on an HTTP origin you control. This is an interoperability signal layered on top of the license; it is not a replacement for the controlling legal text.

## 13. Framework release procedure

Before a final legal release:

1. obtain software/IP counsel review for material jurisdictions;
2. make all legal-text changes before freeze;
3. set the Kiyoshima Source release registry entry to `final`;
4. remove `Release Candidate` and `Candidate Revision` from the final legal heading;
5. remove `candidate_revision` from the final Passport/release record, supersede the current candidate lineage entry, and mark Passport license status as `final` and point provenance to the actual release/attestation;
6. regenerate `MANIFEST.sha256`;
7. run `verify-framework`, tests, and `release-check`;
8. create signed tags (`source-v1.0` and `framework-vX.Y.Z`);
9. let the release workflow package and attest the exact tagged commit.

Never edit the bytes of an already-final legal version. Publish a new legal version instead.

## 14. Framework repository upgrades

For the 1.2.0-rc1 -> 1.2.0-rc2 overlay, follow `UPGRADE-1.2.0-rc2.md`. The already-installed `klicense` symlink normally continues to work because its target file is updated in place. Do not run the old 1.0 migration cleanup for this overlay.
