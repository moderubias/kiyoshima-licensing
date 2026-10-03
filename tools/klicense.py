#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    tomllib = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRAMEWORK_VERSION = "1.2.0-rc2"
CANONICAL = ROOT / "LICENSE-KIYOSHIMA-SOURCE-1.0.txt"
APACHE = ROOT / "LICENSES" / "Apache-2.0.txt"
MIT_TEMPLATE = ROOT / "templates" / "licenses" / "MIT.txt.template"
ROOT_LICENSE = ROOT / "LICENSE"
PASSPORT_NAME = "KIYOSHIMA.json"
MANIFEST_NAME = "MANIFEST.sha256"
CANONICAL_ID = "Kiyoshima-Source-1.0"
SPDX_REF = "LicenseRef-Kiyoshima-Source-1.0"
SUPPORTED_PASSPORT_SCHEMAS = {"1.0", "1.1", "1.2", "1.3"}
CURRENT_PASSPORT_SCHEMA = "1.3"
GENERATED_OPEN_LICENSES = {"MIT", "Apache-2.0", "MIT OR Apache-2.0"}
ALLOWED_PERMISSION_STATES = {
    "allowed",
    "allowed-with-conditions",
    "agreement-required",
    "permission-required",
    "reserved",
    "not-granted",
}
GENERATED_NAMES = {"kiyoshima-watch.json", "kiyoshima-fingerprint.json"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "dist", "node_modules", "target", "build"}


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: pathlib.Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def has_placeholder(value) -> bool:
    if isinstance(value, str):
        upper = value.upper()
        return "REPLACE_WITH" in upper or value.startswith("[") and value.endswith("]")
    if isinstance(value, dict):
        return any(has_placeholder(v) for v in value.values())
    if isinstance(value, list):
        return any(has_placeholder(v) for v in value)
    return False


def resolve_authoritative_file(passport_path: pathlib.Path, d: dict) -> pathlib.Path | None:
    lic = d.get("license")
    if not isinstance(lic, dict):
        return None
    auth = lic.get("authoritative_file")
    if not isinstance(auth, str) or not auth:
        return None
    candidate = (passport_path.parent / auth).resolve()
    try:
        candidate.relative_to(passport_path.parent.resolve())
    except ValueError:
        return None
    return candidate


def resolve_declared_file(passport_path: pathlib.Path, rel) -> pathlib.Path | None:
    if not isinstance(rel, str) or not rel:
        return None
    candidate = (passport_path.parent / rel).resolve()
    try:
        candidate.relative_to(passport_path.parent.resolve())
    except ValueError:
        return None
    return candidate


def validate_passport(path: pathlib.Path, require_current: bool = False) -> list[str]:
    errors = []
    try:
        d = load_json(path)
    except Exception as exc:
        return [f"cannot parse {path}: {exc}"]

    if not isinstance(d, dict):
        return ["Passport root must be a JSON object"]

    required = [
        "format",
        "schema_version",
        "project",
        "profile",
        "license",
        "permissions",
        "ai",
        "automation",
    ]
    for key in required:
        if key not in d:
            errors.append(f"missing passport field: {key}")

    if d.get("format") != "Kiyoshima License Passport":
        errors.append("format must be 'Kiyoshima License Passport'")

    schema = str(d.get("schema_version", ""))
    if schema not in SUPPORTED_PASSPORT_SCHEMAS:
        errors.append(f"unsupported schema_version: {schema!r}")
    if require_current and schema != CURRENT_PASSPORT_SCHEMA:
        errors.append(f"passport schema must be {CURRENT_PASSPORT_SCHEMA} for this framework release")

    if schema in {"1.1", "1.2", "1.3"}:
        for key in ["declaration_scope", "rights_reservations", "permission_requests"]:
            if key not in d:
                errors.append(f"schema {schema} requires field: {key}")
        if d.get("declaration_scope") not in {"covered-software", "framework-canonical-license"}:
            errors.append("invalid declaration_scope")
    if schema in {"1.2", "1.3"}:
        for key in ["protocol", "policy_constraints"]:
            if key not in d:
                errors.append(f"schema {schema} requires field: {key}")
        proto = d.get("protocol")
        if not isinstance(proto, dict):
            errors.append(f"schema {schema} requires protocol to be an object")
            proto = {}
        if proto.get("name") != "Kiyoshima License Passport Protocol" or proto.get("version") != "1.0":
            errors.append(f"schema {schema} requires Kiyoshima License Passport Protocol version 1.0")
        if proto.get("semantics") != "fail-closed-informational":
            errors.append("protocol.semantics must be fail-closed-informational")

    constraints = d.get("policy_constraints")
    if not isinstance(constraints, dict):
        if schema in {"1.2", "1.3"}:
            errors.append(f"schema {schema} requires policy_constraints to be an object")
        constraints = {}

    if schema == "1.2":
        if constraints.get("downstream_rights") != "direct-from-licensor-not-sublicensed":
            errors.append("policy_constraints.downstream_rights must be direct-from-licensor-not-sublicensed")

    source_semantics = schema == "1.3" and (
        d.get("profile") == "source" or d.get("declaration_scope") == "framework-canonical-license"
    )
    if source_semantics:
        required_source_constraints = {
            "organization_evaluation_days": 30,
            "organization_evaluation_nonproduction_only": True,
            "distribution_attribution_required": True,
            "modified_portions_source_required": True,
            "downstream_rights": "direct-from-licensor-not-sublicensed",
            "operational_ai_provider_must_not_acquire_reserved_rights": True,
        }
        for key, expected in required_source_constraints.items():
            if constraints.get(key) != expected:
                errors.append(f"source policy_constraints.{key} must equal {expected!r}")

    lic = d.get("license")
    if not isinstance(lic, dict):
        errors.append("license must be an object")
        lic = {}

    if source_semantics:
        expected_source_identity = {
            "canonical_id": CANONICAL_ID,
            "spdx_expression": SPDX_REF,
            "version": "1.0",
        }
        for key, expected in expected_source_identity.items():
            if lic.get(key) != expected:
                errors.append(f"source license.{key} must equal {expected!r}")

    auth = resolve_authoritative_file(path, d)
    expected_hash = lic.get("sha256")
    if not auth:
        errors.append("license.authoritative_file is missing or escapes the project root")
    elif not auth.exists():
        errors.append(f"authoritative license file does not exist: {auth}")
    elif not auth.is_file():
        errors.append(f"authoritative license path is not a file: {auth}")
    elif expected_hash:
        actual_hash = sha256_file(auth)
        if actual_hash.lower() != str(expected_hash).lower():
            errors.append(f"authoritative license hash mismatch: expected {expected_hash}, actual {actual_hash}")
    else:
        errors.append("license.sha256 is required")

    supporting_files = lic.get("supporting_files", [])
    if not isinstance(supporting_files, list):
        errors.append("license.supporting_files must be an array")
        supporting_files = []
    for i, item in enumerate(supporting_files):
        if not isinstance(item, dict):
            errors.append(f"license.supporting_files[{i}] must be an object")
            continue
        rel = item.get("path")
        expected = item.get("sha256")
        supporting = resolve_declared_file(path, rel)
        if not supporting:
            errors.append(f"license.supporting_files[{i}].path is missing or escapes the project root")
            continue
        if not supporting.exists():
            errors.append(f"declared supporting license file does not exist: {supporting}")
            continue
        if not supporting.is_file():
            errors.append(f"declared supporting license path is not a file: {supporting}")
            continue
        if not expected:
            errors.append(f"license.supporting_files[{i}].sha256 is required")
            continue
        actual = sha256_file(supporting)
        if actual.lower() != str(expected).lower():
            errors.append(f"supporting license hash mismatch for {rel}: expected {expected}, actual {actual}")

    if lic.get("canonical_id") == CANONICAL_ID and expected_hash and CANONICAL.exists():
        canonical_hash = sha256_file(CANONICAL)
        if str(expected_hash).lower() != canonical_hash.lower():
            errors.append(
                f"passport claims {CANONICAL_ID} but digest does not match this framework's canonical candidate: {canonical_hash}"
            )

    permissions = d.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("permissions must be an object")
        permissions = {}
    for key, value in permissions.items():
        if value not in ALLOWED_PERMISSION_STATES:
            errors.append(f"permissions.{key} has unknown state: {value!r}")

    auto = d.get("automation")
    if not isinstance(auto, dict):
        errors.append("automation must be an object")
        auto = {}
    invariants = {
        "conflict_policy": "deny-on-conflict",
        "missing_field_policy": "do-not-infer-rights",
        "machine_metadata_authority": "informational",
        "additional_permissions_require_authenticated_grant": True,
    }
    if schema in {"1.1", "1.2", "1.3"}:
        invariants["unknown_value_policy"] = "do-not-infer-rights"
    for key, expected in invariants.items():
        if auto.get(key) != expected:
            errors.append(f"automation.{key} must equal {expected!r}")

    return errors


def ignored_for_manifest(rel: pathlib.Path) -> bool:
    if rel.name == MANIFEST_NAME or rel.name in GENERATED_NAMES:
        return True
    return any(part in EXCLUDED_PARTS for part in rel.parts)


def manifest_files(root: pathlib.Path):
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if ignored_for_manifest(rel):
            continue
        rows.append(rel)
    return rows


def manifest_text(root: pathlib.Path) -> str:
    return "".join(f"{sha256_file(root / rel)}  {rel.as_posix()}\n" for rel in manifest_files(root))


def verify_manifest(root: pathlib.Path) -> list[str]:
    errors = []
    path = root / MANIFEST_NAME
    if not path.exists():
        return [f"missing {MANIFEST_NAME}"]
    listed = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            digest, rel = raw.split("  ", 1)
        except ValueError:
            errors.append(f"invalid manifest line {lineno}: {raw!r}")
            continue
        if len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest):
            errors.append(f"invalid digest at manifest line {lineno}")
            continue
        if rel in listed:
            errors.append(f"duplicate manifest path: {rel}")
        listed[rel] = digest.lower()

    actual_paths = {rel.as_posix() for rel in manifest_files(root)}
    listed_paths = set(listed)
    for rel in sorted(actual_paths - listed_paths):
        errors.append(f"manifest missing file: {rel}")
    for rel in sorted(listed_paths - actual_paths):
        errors.append(f"manifest references missing/excluded file: {rel}")
    for rel in sorted(actual_paths & listed_paths):
        actual = sha256_file(root / rel)
        if actual != listed[rel]:
            errors.append(f"manifest hash mismatch: {rel}: expected {listed[rel]}, actual {actual}")
    return errors


def cmd_manifest(args):
    root = pathlib.Path(args.path).resolve()
    path = root / MANIFEST_NAME
    if args.write:
        path.write_text(manifest_text(root), encoding="utf-8")
        print(f"wrote {path} ({len(manifest_files(root))} files)")
        return 0
    errors = verify_manifest(root)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"manifest integrity: OK ({len(manifest_files(root))} files)")
    return 0


def framework_errors() -> list[str]:
    errors = []
    if not CANONICAL.exists():
        errors.append("canonical Kiyoshima Source legal text is missing")
    if not APACHE.exists() or not ROOT_LICENSE.exists():
        errors.append("Apache-2.0 repository license files are missing")
    elif APACHE.read_bytes() != ROOT_LICENSE.read_bytes():
        errors.append("root LICENSE must be byte-identical to LICENSES/Apache-2.0.txt")

    passport = ROOT / PASSPORT_NAME
    if passport.exists():
        errors.extend(validate_passport(passport, require_current=True))
    else:
        errors.append(f"missing {PASSPORT_NAME}")

    canonical_hash = sha256_file(CANONICAL) if CANONICAL.exists() else None
    releases = ROOT / "registry" / "releases.json"
    if releases.exists() and canonical_hash:
        try:
            data = load_json(releases)
            entries = [e for e in data.get("entries", []) if e.get("canonical_id") == CANONICAL_ID]
            if len(entries) != 1:
                errors.append(f"release registry must contain exactly one {CANONICAL_ID} entry")
            elif entries[0].get("sha256") != canonical_hash:
                errors.append("release registry canonical digest mismatch")
        except Exception as exc:
            errors.append(f"invalid release registry: {exc}")

    template = ROOT / "templates" / "project" / PASSPORT_NAME
    if template.exists() and canonical_hash:
        try:
            d = load_json(template)
            if d.get("license", {}).get("sha256") != canonical_hash:
                errors.append("project Passport template canonical digest mismatch")
            if d.get("schema_version") != CURRENT_PASSPORT_SCHEMA:
                errors.append("project Passport template is not on current schema")
        except Exception as exc:
            errors.append(f"invalid project Passport template: {exc}")

    for rel in [
        "registry/projects.json",
        "registry/adopters.json",
        "registry/grants.public.json",
        "registry/candidates.json",
        "monitor/targets.json",
        "machine/schema/kiyoshima-passport.schema.json",
        "machine/schema/kiyoshima-grant.schema.json",
        "machine/schema/kiyoshima-registry.schema.json",
    ]:
        try:
            load_json(ROOT / rel)
        except Exception as exc:
            errors.append(f"invalid JSON {rel}: {exc}")

    candidates = ROOT / "registry" / "candidates.json"
    if candidates.exists() and canonical_hash:
        try:
            data = load_json(candidates)
            current = [e for e in data.get("entries", []) if e.get("status") == "current-candidate"]
            if len(current) != 1:
                errors.append("candidate lineage must contain exactly one current-candidate while pre-final")
            elif current[0].get("sha256") != canonical_hash:
                errors.append("current candidate lineage digest mismatch")
        except Exception as exc:
            errors.append(f"invalid candidate lineage registry: {exc}")

    if (ROOT / "registry" / "grants.json").exists():
        errors.append("legacy registry/grants.json exists; use grants.public.json and keep private grants private")

    errors.extend(verify_manifest(ROOT))
    return errors


def cmd_verify_framework(args):
    errors = framework_errors()
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("Kiyoshima framework integrity: OK")
    print(f"canonical legal sha256: {sha256_file(CANONICAL)}")
    print(f"manifest files: {len(manifest_files(ROOT))}")
    return 0


def cmd_release_check(args):
    errors = framework_errors()
    if not errors:
        data = load_json(ROOT / "registry" / "releases.json")
        entry = next(e for e in data["entries"] if e.get("canonical_id") == CANONICAL_ID)
        if entry.get("status") != "final":
            errors.append("release registry status is not 'final'; legal review/freeze has not been recorded")
        first_lines = CANONICAL.read_text(encoding="utf-8").splitlines()[:5]
        if any("Release Candidate" in line for line in first_lines):
            errors.append("canonical legal text still declares 'Release Candidate'")
        passport = load_json(ROOT / PASSPORT_NAME)
        if passport.get("license", {}).get("status") != "final":
            errors.append("framework Passport license.status is not 'final'")
        if passport.get("license", {}).get("candidate_revision"):
            errors.append("framework Passport still carries candidate_revision; final release must remove it")
        candidates = load_json(ROOT / "registry" / "candidates.json")
        if any(e.get("status") == "current-candidate" for e in candidates.get("entries", [])):
            errors.append("candidate lineage still has a current-candidate; supersede it before final release")
        template = load_json(ROOT / "templates" / "project" / PASSPORT_NAME)
        if template.get("license", {}).get("status") != "final":
            errors.append("project Passport template license.status is not 'final'")
        if template.get("license", {}).get("candidate_revision"):
            errors.append("project Passport template still carries candidate_revision")
        if "planned" in str(passport.get("provenance", {}).get("release_attestation", "")).lower():
            errors.append("framework Passport still marks release attestation as planned")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print("release-check: NOT READY", file=sys.stderr)
        return 1
    print("release-check: READY")
    return 0


def cmd_validate_passport(args):
    path = pathlib.Path(args.path).resolve()
    errors = validate_passport(path, require_current=args.current)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"License Passport valid: {path}")
    return 0


def project_errors(base: pathlib.Path) -> list[str]:
    errors = []
    passport_path = base / PASSPORT_NAME
    if not passport_path.exists():
        return [f"missing {PASSPORT_NAME} in {base}"]
    errors.extend(validate_passport(passport_path))
    try:
        d = load_json(passport_path)
    except Exception:
        return errors
    if d.get("declaration_scope") not in {None, "covered-software"}:
        errors.append("project Passport declaration_scope must be covered-software")
    if d.get("profile") == "source":
        lic = d.get("license", {})
        if lic.get("canonical_id") != CANONICAL_ID:
            errors.append(f"source profile must use canonical_id {CANONICAL_ID}")
        if lic.get("spdx_expression") != SPDX_REF:
            errors.append(f"source profile must use spdx_expression {SPDX_REF}")
        lic_file = base / "LICENSE"
        if not lic_file.exists():
            errors.append("source profile project is missing root LICENSE")
        elif CANONICAL.exists() and lic_file.read_bytes() != CANONICAL.read_bytes():
            errors.append("project claims Kiyoshima Source 1.0 but legal bytes differ from canonical candidate")
    if has_placeholder(d):
        errors.append("Passport still contains REPLACE_WITH or bracket placeholders")
    return errors


def cmd_verify_project(args):
    base = pathlib.Path(args.path).resolve()
    errors = project_errors(base)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"Kiyoshima project policy: OK — {base}")
    d = load_json(base / PASSPORT_NAME)
    print(f"profile: {d.get('profile')}")
    print(f"license: {d.get('license', {}).get('name')}")
    return 0


def safe_write(path: pathlib.Path, data: bytes, force: bool):
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def safe_write_text(path: pathlib.Path, text: str, force: bool):
    safe_write(path, text.encode("utf-8"), force)


def render_mit_license(year: str, holder: str) -> bytes:
    text = MIT_TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("[year]", year).replace("[copyright holder]", holder)
    return text.encode("utf-8")


def render_dual_license_notice(project_name: str, year: str, holder: str) -> bytes:
    text = f"""{project_name} — licensing notice

Copyright (c) {year} {holder}
SPDX-License-Identifier: MIT OR Apache-2.0

This project is dual-licensed at your option under either:

- the MIT License: LICENSES/MIT.txt
- the Apache License, Version 2.0: LICENSES/Apache-2.0.txt

The complete license texts in LICENSES/ control. The Kiyoshima Open profile and
KIYOSHIMA.json are machine-readable metadata conventions and add no license terms.
"""
    return text.encode("utf-8")


def render_open_license(expression: str, year: str, holder: str, project_name: str):
    if expression not in GENERATED_OPEN_LICENSES:
        raise ValueError(f"unsupported generated Open license expression: {expression}")
    mit = render_mit_license(year, holder)
    apache = APACHE.read_bytes()
    if expression == "MIT":
        return mit, {}
    if expression == "Apache-2.0":
        return apache, {}
    return render_dual_license_notice(project_name, year, holder), {
        "MIT": mit,
        "Apache-2.0": apache,
    }


def open_license_display_name(expression: str) -> str:
    return {
        "MIT": "MIT License",
        "Apache-2.0": "Apache License 2.0",
        "MIT OR Apache-2.0": "MIT License OR Apache License 2.0",
    }[expression]


def _optional_project_path(base: pathlib.Path, rel: str | None) -> pathlib.Path | None:
    if not rel:
        return None
    candidate = (base / rel).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        raise ValueError(f"path escapes project root: {rel}")
    return candidate


def _render_open_notice(args, year: str, expression: str) -> str:
    notice = (ROOT / "templates" / "project" / "NOTICE-OPEN.template").read_text(encoding="utf-8")
    for old, new in {
        "[project name]": args.name,
        "[year]": year,
        "[copyright holder]": args.holder,
        "[repository URL]": args.repository,
        "[SPDX expression]": expression,
    }.items():
        notice = notice.replace(old, new)
    return notice


def _render_open_reuse(year: str, holder: str, expression: str) -> str:
    reuse = (ROOT / "templates" / "project" / "REUSE-OPEN.toml").read_text(encoding="utf-8")
    reuse = reuse.replace("REPLACE_WITH_COPYRIGHT_NOTICE", f"{year} {holder}")
    return reuse.replace("REPLACE_WITH_SPDX_EXPRESSION", expression)


def cmd_init_project(args):
    base = pathlib.Path(args.path).resolve()
    base.mkdir(parents=True, exist_ok=True)
    year = str(datetime.now(timezone.utc).year)
    outputs = {}
    want_reuse = bool(getattr(args, "reuse", False))
    want_notice = bool(getattr(args, "notice", False))
    readme_rel = getattr(args, "readme_snippet", None)

    try:
        readme_path = _optional_project_path(base, readme_rel)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.profile == "source":
        if not args.contact:
            print("ERROR: --contact is required for the Source profile", file=sys.stderr)
            return 2
        template = load_json(ROOT / "templates" / "project" / PASSPORT_NAME)
        template["project"].update({
            "name": args.name,
            "kind": args.kind,
            "repository": args.repository,
            "copyright_holder": args.holder,
            "contact": args.contact,
        })
        template["permission_requests"]["general"] = args.contact
        template["permission_requests"]["commercial"] = args.commercial_contact or args.contact
        template["permission_requests"]["ai"] = args.ai_contact or args.contact
        template["permission_requests"]["evaluation"] = args.evaluation_contact or args.commercial_contact or args.contact
        digest = sha256_file(CANONICAL)
        template["license"]["sha256"] = digest
        template["license"]["supporting_files"] = []
        template["provenance"]["legal_text_digest"] = digest

        outputs = {
            base / "LICENSE": CANONICAL.read_bytes(),
            base / PASSPORT_NAME: (json.dumps(template, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        }
        if want_reuse:
            template["license"]["supporting_files"] = [{
                "path": f"LICENSES/{SPDX_REF}.txt",
                "spdx_id": SPDX_REF,
                "sha256": digest,
            }]
            reuse = (ROOT / "templates" / "project" / "REUSE.toml").read_text(encoding="utf-8")
            reuse = reuse.replace("REPLACE_WITH_COPYRIGHT_NOTICE", f"{year} {args.holder}")
            outputs[base / "LICENSES" / f"{SPDX_REF}.txt"] = CANONICAL.read_bytes()
            outputs[base / "REUSE.toml"] = reuse.encode("utf-8")
            outputs[base / PASSPORT_NAME] = (json.dumps(template, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if want_notice:
            notice = (ROOT / "templates" / "project" / "NOTICE.template").read_text(encoding="utf-8")
            notice = notice.replace("[project name]", args.name)
            notice = notice.replace("[year]", year)
            notice = notice.replace("[copyright holder]", args.holder)
            notice = notice.replace("[repository URL]", args.repository)
            notice = notice.replace("[contact URL or email]", args.contact)
            outputs[base / "NOTICE"] = notice.encode("utf-8")
        if readme_path:
            snippet = (ROOT / "templates" / "project" / "README-LICENSING.md").read_bytes()
            outputs[readme_path] = snippet

    elif args.profile == "open":
        expression = args.open_license
        root_license, component_licenses = render_open_license(expression, year, args.holder, args.name)
        template = load_json(ROOT / "templates" / "project" / "KIYOSHIMA-OPEN.json")
        contact = args.contact or args.repository
        template["project"].update({
            "name": args.name,
            "kind": args.kind,
            "repository": args.repository,
            "copyright_holder": args.holder,
            "contact": contact,
        })
        template["license"].update({
            "name": open_license_display_name(expression),
            "spdx_expression": expression,
            "sha256": hashlib.sha256(root_license).hexdigest(),
            "legal_priority": (
                "license-declaration-plus-component-texts-control"
                if expression == "MIT OR Apache-2.0"
                else "license-text-controls"
            ),
        })
        template["permission_requests"]["general"] = contact
        template["provenance"]["legal_text_digest"] = hashlib.sha256(root_license).hexdigest()
        template["policy_constraints"]["open_profile_spdx_expression"] = expression

        # A compound SPDX expression needs both complete license texts. Single-license
        # projects keep the full legal text in root LICENSE and need no duplicate copy.
        if want_reuse and expression in {"MIT", "Apache-2.0"}:
            component_licenses = {expression: root_license}
        template["license"]["supporting_files"] = [
            {
                "path": f"LICENSES/{spdx_id}.txt",
                "spdx_id": spdx_id,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            for spdx_id, data in component_licenses.items()
        ]

        outputs = {
            base / "LICENSE": root_license,
            base / PASSPORT_NAME: (json.dumps(template, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
        }
        for spdx_id, data in component_licenses.items():
            outputs[base / "LICENSES" / f"{spdx_id}.txt"] = data
        if want_notice:
            outputs[base / "NOTICE"] = _render_open_notice(args, year, expression).encode("utf-8")
        if want_reuse:
            outputs[base / "REUSE.toml"] = _render_open_reuse(year, args.holder, expression).encode("utf-8")
        if readme_path:
            snippet = (ROOT / "templates" / "project" / "README-LICENSING-OPEN.md").read_text(encoding="utf-8")
            snippet = snippet.replace("REPLACE_WITH_SPDX_EXPRESSION", expression)
            outputs[readme_path] = snippet.encode("utf-8")
    else:
        print(f"ERROR: init-project does not generate profile {args.profile!r}", file=sys.stderr)
        return 2

    conflicts = [str(p) for p in outputs if p.exists() and not args.force]
    if conflicts:
        print("ERROR: refusing to overwrite existing files:", file=sys.stderr)
        for p in conflicts:
            print(f"  {p}", file=sys.stderr)
        print("Use --force only after reviewing the existing project licensing.", file=sys.stderr)
        return 2
    if args.dry_run:
        print("Would create/update:")
        for p in outputs:
            print(f"  {p}")
        return 0
    for p, data in outputs.items():
        safe_write(p, data, args.force)
    print(f"initialized Kiyoshima {args.profile.capitalize()} profile in {base}")
    print("layout: lean (NOTICE, REUSE.toml, and README snippets are opt-in)")
    print("Next: run verify-project and doctor.")
    return 0



def cmd_sync_project(args):
    base = pathlib.Path(args.path).resolve()
    passport_path = base / PASSPORT_NAME
    if not passport_path.exists():
        print(f"ERROR: missing {PASSPORT_NAME} in {base}; use init-project for a new project", file=sys.stderr)
        return 2
    try:
        current = load_json(passport_path)
    except Exception as exc:
        print(f"ERROR: cannot parse {passport_path}: {exc}", file=sys.stderr)
        return 2
    lic = current.get("license", {})
    if current.get("profile") != "source" or lic.get("canonical_id") != CANONICAL_ID:
        print(f"ERROR: sync-project only upgrades projects already declaring {CANONICAL_ID}", file=sys.stderr)
        return 2

    template = load_json(ROOT / "templates" / "project" / PASSPORT_NAME)
    synced = template
    synced["project"].update(current.get("project", {}))
    synced["profile"] = "source"
    synced["grants"] = current.get("grants", [])
    contact = synced.get("project", {}).get("contact") or current.get("permission_requests", {}).get("general")
    if not contact or has_placeholder(contact):
        print("ERROR: project has no usable license contact; fix project.contact before syncing", file=sys.stderr)
        return 2
    for key in synced["permission_requests"]:
        synced["permission_requests"][key] = current.get("permission_requests", {}).get(key) or contact
    digest = sha256_file(CANONICAL)
    synced["license"]["sha256"] = digest
    reuse_copy = base / "LICENSES" / f"{SPDX_REF}.txt"
    if reuse_copy.exists():
        synced["license"]["supporting_files"] = [{
            "path": f"LICENSES/{SPDX_REF}.txt",
            "spdx_id": SPDX_REF,
            "sha256": digest,
        }]
    else:
        synced["license"]["supporting_files"] = []
    synced["provenance"]["legal_text_digest"] = digest

    notice_path = base / "NOTICE"
    old_notice = notice_path.read_text(encoding="utf-8") if notice_path.exists() else None
    outputs = {
        base / "LICENSE": CANONICAL.read_bytes(),
        passport_path: (json.dumps(synced, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    }
    if reuse_copy.exists():
        outputs[reuse_copy] = CANONICAL.read_bytes()

    if args.dry_run:
        old_hash = lic.get("sha256", "unknown")
        print(f"Would sync {base}")
        print(f"  Passport schema: {current.get('schema_version', 'unknown')} -> {CURRENT_PASSPORT_SCHEMA}")
        print(f"  Legal digest: {old_hash} -> {digest}")
        for path in outputs:
            print(f"  update: {path}")
        return 0

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = base.parent / f"{base.name}.kiyoshima-backup-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    for path in outputs:
        if path.exists():
            rel = path.relative_to(base)
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    if old_notice is not None:
        dest = backup / "NOTICE"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(notice_path, dest)

    for path, data in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    print(f"synced {base} to {CANONICAL_ID} candidate digest {digest}")
    print(f"backup: {backup}")
    print("NOTICE and README text are not rewritten automatically; review them if policy wording changed.")
    errors = project_errors(base)
    if errors:
        for e in errors:
            print(f"ERROR after sync: {e}", file=sys.stderr)
        return 1
    print("post-sync verification: OK")
    return 0

def cmd_upgrade_passport(args):
    path = pathlib.Path(args.path).resolve()
    d = load_json(path)
    old = str(d.get("schema_version", ""))
    if old == CURRENT_PASSPORT_SCHEMA:
        print(f"already schema {CURRENT_PASSPORT_SCHEMA}: {path}")
        return 0
    if old not in {"1.0", "1.1", "1.2"}:
        print(f"ERROR: only schema 1.0/1.1/1.2 -> {CURRENT_PASSPORT_SCHEMA} upgrade is supported, got {old!r}", file=sys.stderr)
        return 2

    profile = d.get("profile", "source")
    is_source = profile == "source" or d.get("license", {}).get("canonical_id") == CANONICAL_ID
    if is_source:
        upgraded = load_json(ROOT / "templates" / "project" / PASSPORT_NAME)
        upgraded["project"].update(d.get("project", {}))
        upgraded["profile"] = "source"
        upgraded["permissions"].update(d.get("permissions", {}))
        upgraded["ai"].update(d.get("ai", {}))
        upgraded["grants"] = d.get("grants", [])
        upgraded["rights_reservations"].update(d.get("rights_reservations", {}))
        contact = upgraded.get("project", {}).get("contact") or d.get("permission_requests", {}).get("general")
        if not contact or has_placeholder(contact):
            print("ERROR: source Passport has no usable project.contact/general permission route", file=sys.stderr)
            return 2
        for key in upgraded["permission_requests"]:
            upgraded["permission_requests"][key] = d.get("permission_requests", {}).get(key) or contact
        digest = sha256_file(CANONICAL)
        upgraded["license"]["sha256"] = digest
        project_root = path.parent
        reuse_copy = project_root / "LICENSES" / f"{SPDX_REF}.txt"
        upgraded["license"]["supporting_files"] = ([{
            "path": f"LICENSES/{SPDX_REF}.txt",
            "spdx_id": SPDX_REF,
            "sha256": digest,
        }] if reuse_copy.exists() else [])
        upgraded["provenance"]["legal_text_digest"] = digest
    else:
        upgraded = dict(d)
        upgraded["schema_version"] = CURRENT_PASSPORT_SCHEMA
        upgraded.setdefault("declaration_scope", "covered-software")
        upgraded.setdefault("rights_reservations", {})
        upgraded.setdefault("permission_requests", {})
        upgraded.setdefault("provenance", {})
        upgraded.setdefault("grants", [])
        upgraded.setdefault("policy_constraints", {})
        upgraded["protocol"] = {
            "name": "Kiyoshima License Passport Protocol",
            "version": "1.0",
            "semantics": "fail-closed-informational",
            "canonical_repository": "https://github.com/moderubias/kiyoshima-licensing",
        }
        auto = upgraded.setdefault("automation", {})
        auto.update({
            "conflict_policy": "deny-on-conflict",
            "missing_field_policy": "do-not-infer-rights",
            "unknown_value_policy": "do-not-infer-rights",
            "machine_metadata_authority": "informational",
            "additional_permissions_require_authenticated_grant": True,
        })
    if args.dry_run:
        print(json.dumps(upgraded, indent=2, ensure_ascii=False))
        return 0
    backup = path.with_suffix(path.suffix + f".v{old}.bak")
    if backup.exists() and not args.force:
        print(f"ERROR: backup already exists: {backup}; use --force to replace it", file=sys.stderr)
        return 2
    shutil.copy2(path, backup)
    dump_json(path, upgraded)
    print(f"upgraded {path} from schema {old} to {CURRENT_PASSPORT_SCHEMA}; backup: {backup}")
    return 0



def _extract_mit_year(data: bytes) -> str | None:
    text = data.decode("utf-8", errors="replace")
    match = re.search(r"Copyright\s*\(c\)\s*([0-9]{4}(?:-[0-9]{4})?)\s+", text)
    return match.group(1) if match else None


def _render_open_notice_from_passport(d: dict, year: str) -> bytes:
    project = d.get("project", {})
    expression = d.get("license", {}).get("spdx_expression", "")
    notice = (ROOT / "templates" / "project" / "NOTICE-OPEN.template").read_text(encoding="utf-8")
    replacements = {
        "[project name]": str(project.get("name", "")),
        "[year]": year,
        "[copyright holder]": str(project.get("copyright_holder", "")),
        "[repository URL]": str(project.get("repository", "")),
        "[SPDX expression]": str(expression),
    }
    for old, new in replacements.items():
        notice = notice.replace(old, new)
    return notice.encode("utf-8")


def _render_source_notice_from_passport(d: dict, year: str) -> bytes:
    project = d.get("project", {})
    notice = (ROOT / "templates" / "project" / "NOTICE.template").read_text(encoding="utf-8")
    replacements = {
        "[project name]": str(project.get("name", "")),
        "[year]": year,
        "[copyright holder]": str(project.get("copyright_holder", "")),
        "[repository URL]": str(project.get("repository", "")),
        "[contact URL or email]": str(project.get("contact", "")),
    }
    for old, new in replacements.items():
        notice = notice.replace(old, new)
    return notice.encode("utf-8")


def _render_source_reuse_from_passport(d: dict, year: str) -> bytes:
    project = d.get("project", {})
    reuse = (ROOT / "templates" / "project" / "REUSE.toml").read_text(encoding="utf-8")
    reuse = reuse.replace(
        "REPLACE_WITH_COPYRIGHT_NOTICE",
        f"{year} {project.get('copyright_holder', '')}",
    )
    return reuse.encode("utf-8")


def _project_year(base: pathlib.Path, d: dict) -> str:
    candidates = [
        base / "LICENSES" / "MIT.txt",
        base / "LICENSE-MIT",
        base / "LICENSE",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            year = _extract_mit_year(candidate.read_bytes())
            if year:
                return year
    notice = base / "NOTICE"
    if notice.exists() and notice.is_file():
        text = notice.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(?:COPYRIGHT:\s*©?|Copyright(?:\s*\(c\))?)\s*([0-9]{4}(?:-[0-9]{4})?)", text, re.IGNORECASE)
        if match:
            return match.group(1)
    return str(datetime.now(timezone.utc).year)


def _backup_project_paths(base: pathlib.Path, paths: list[pathlib.Path]) -> pathlib.Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = base.parent / f"{base.name}.kiyoshima-backup-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    seen = set()
    for path in paths:
        if path in seen or not path.exists():
            continue
        seen.add(path)
        rel = path.relative_to(base)
        dest = backup / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_file():
            shutil.copy2(path, dest)
    return backup


def cmd_compact_project(args):
    base = pathlib.Path(args.path).resolve()
    passport_path = base / PASSPORT_NAME
    if not passport_path.exists():
        print(f"ERROR: missing {PASSPORT_NAME} in {base}", file=sys.stderr)
        return 2

    errors = project_errors(base)
    if errors:
        print("ERROR: project must verify before layout compaction:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    d = load_json(passport_path)
    profile = d.get("profile")
    lic = d.get("license", {})
    project = d.get("project", {})
    year = _project_year(base, d)
    updates: dict[pathlib.Path, bytes] = {}
    removals: list[pathlib.Path] = []
    preserved: list[pathlib.Path] = []

    if profile == "open":
        expression = lic.get("spdx_expression")
        if expression not in GENERATED_OPEN_LICENSES:
            print(f"ERROR: unsupported Open expression for compaction: {expression!r}", file=sys.stderr)
            return 2

        if expression == "MIT OR Apache-2.0":
            mit_path = base / "LICENSES" / "MIT.txt"
            apache_path = base / "LICENSES" / "Apache-2.0.txt"
            if not mit_path.exists() or not apache_path.exists():
                print("ERROR: dual-license compaction requires LICENSES/MIT.txt and LICENSES/Apache-2.0.txt", file=sys.stderr)
                return 2
            root_license = render_dual_license_notice(
                str(project.get("name", base.name)),
                year,
                str(project.get("copyright_holder", "")),
            )
            updates[base / "LICENSE"] = root_license
            component_paths = [("MIT", mit_path), ("Apache-2.0", apache_path)]
            lic["supporting_files"] = [
                {
                    "path": f"LICENSES/{spdx_id}.txt",
                    "spdx_id": spdx_id,
                    "sha256": sha256_file(path),
                }
                for spdx_id, path in component_paths
            ]
            lic["legal_priority"] = "license-declaration-plus-component-texts-control"
            lic["sha256"] = hashlib.sha256(root_license).hexdigest()
            d.setdefault("provenance", {})["legal_text_digest"] = lic["sha256"]
        else:
            root_license = base / "LICENSE"
            if not root_license.exists():
                print("ERROR: single-license Open project is missing root LICENSE", file=sys.stderr)
                return 2
            lic["sha256"] = sha256_file(root_license)
            d.setdefault("provenance", {})["legal_text_digest"] = lic["sha256"]
            component = base / "LICENSES" / f"{expression}.txt"
            reuse_path = base / "REUSE.toml"
            generated_reuse = _render_open_reuse(
                year,
                str(project.get("copyright_holder", "")),
                expression,
            ).encode("utf-8")
            can_remove_reuse = reuse_path.exists() and reuse_path.read_bytes() == generated_reuse
            if component.exists() and component.read_bytes() == root_license.read_bytes() and (not reuse_path.exists() or can_remove_reuse):
                removals.append(component)
                lic["supporting_files"] = []
            elif component.exists():
                lic["supporting_files"] = [{
                    "path": f"LICENSES/{expression}.txt",
                    "spdx_id": expression,
                    "sha256": sha256_file(component),
                }]
            else:
                lic["supporting_files"] = []

        for duplicate, canonical in [
            (base / "LICENSE-MIT", base / "LICENSES" / "MIT.txt"),
            (base / "LICENSE-APACHE", base / "LICENSES" / "Apache-2.0.txt"),
        ]:
            if not duplicate.exists():
                continue
            if canonical.exists() and duplicate.read_bytes() == canonical.read_bytes():
                removals.append(duplicate)
            else:
                preserved.append(duplicate)

        notice_path = base / "NOTICE"
        if notice_path.exists():
            expected_notice = _render_open_notice_from_passport(d, year)
            if notice_path.read_bytes() == expected_notice:
                removals.append(notice_path)
            else:
                preserved.append(notice_path)

        reuse_path = base / "REUSE.toml"
        if reuse_path.exists():
            expected_reuse = _render_open_reuse(
                year,
                str(project.get("copyright_holder", "")),
                str(expression),
            ).encode("utf-8")
            if reuse_path.read_bytes() == expected_reuse:
                removals.append(reuse_path)
            else:
                preserved.append(reuse_path)

        snippet_path = base / "README-LICENSING.md"
        if snippet_path.exists():
            expected = (ROOT / "templates" / "project" / "README-LICENSING-OPEN.md").read_text(encoding="utf-8")
            expected = expected.replace("REPLACE_WITH_SPDX_EXPRESSION", str(expression)).encode("utf-8")
            if snippet_path.read_bytes() == expected:
                removals.append(snippet_path)
            else:
                preserved.append(snippet_path)

    elif profile == "source":
        root_license = base / "LICENSE"
        if not root_license.exists() or root_license.read_bytes() != CANONICAL.read_bytes():
            print("ERROR: Source project root LICENSE is not the canonical candidate", file=sys.stderr)
            return 2
        lic["sha256"] = sha256_file(root_license)
        d.setdefault("provenance", {})["legal_text_digest"] = lic["sha256"]
        reuse_copy = base / "LICENSES" / f"{SPDX_REF}.txt"
        reuse_path = base / "REUSE.toml"
        expected_reuse = _render_source_reuse_from_passport(d, year)
        if reuse_path.exists() and reuse_path.read_bytes() == expected_reuse:
            removals.append(reuse_path)
            if reuse_copy.exists() and reuse_copy.read_bytes() == root_license.read_bytes():
                removals.append(reuse_copy)
                lic["supporting_files"] = []
        notice_path = base / "NOTICE"
        if notice_path.exists():
            expected_notice = _render_source_notice_from_passport(d, year)
            if notice_path.read_bytes() == expected_notice:
                removals.append(notice_path)
            else:
                preserved.append(notice_path)
    else:
        print(f"ERROR: compact-project does not support profile {profile!r}", file=sys.stderr)
        return 2

    updates[passport_path] = (json.dumps(d, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    # Keep plan deterministic and avoid trying to remove paths that are also updated.
    removals = sorted({p for p in removals if p not in updates}, key=lambda p: p.as_posix())

    print(f"Kiyoshima compact layout plan — {base}")
    for path in sorted(updates, key=lambda p: p.as_posix()):
        action = "update" if path.exists() else "create"
        print(f"  {action}: {path.relative_to(base)}")
    for path in removals:
        print(f"  remove generated/redundant: {path.relative_to(base)}")
    for path in sorted(set(preserved), key=lambda p: p.as_posix()):
        print(f"  preserve customized file: {path.relative_to(base)}")

    if not args.apply:
        print("dry-run only; re-run with --apply to make these changes")
        return 0

    touched = list(updates) + removals
    backup = _backup_project_paths(base, touched)
    for path, data in updates.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for path in removals:
        if path.exists() and path.is_file():
            path.unlink()
    licenses_dir = base / "LICENSES"
    if licenses_dir.exists() and licenses_dir.is_dir() and not any(licenses_dir.iterdir()):
        licenses_dir.rmdir()

    post_errors = project_errors(base)
    if post_errors:
        for error in post_errors:
            print(f"ERROR after compaction: {error}", file=sys.stderr)
        print(f"backup: {backup}", file=sys.stderr)
        return 1
    print(f"backup: {backup}")
    print("post-compaction verification: OK")
    return 0

def cmd_query_right(args):
    base = pathlib.Path(args.path).resolve()
    pp = base if base.is_file() else base / PASSPORT_NAME
    errors = validate_passport(pp)
    if errors:
        payload = {"status":"unknown","reason":"invalid-passport","errors":errors}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print("unknown — Passport is invalid")
            for e in errors:
                print(f"  {e}")
        return 0
    d = load_json(pp)
    key = args.right
    source = None
    value = None
    for section in ["permissions", "ai", "rights_reservations"]:
        if key in d.get(section, {}):
            source = section
            value = d[section][key]
            break
    if value is None:
        payload = {"right":key,"status":"unknown","policy":"do-not-infer-rights"}
    else:
        payload = {"right":key,"status":value,"source":source}
        if value in {"agreement-required", "permission-required", "reserved", "not-granted"} or (key == "organization_evaluation" and value == "allowed-with-conditions"):
            requests = d.get("permission_requests", {})
            category = "ai" if source in {"ai", "rights_reservations"} else ("evaluation" if key == "organization_evaluation" else "commercial")
            payload["permission_request"] = requests.get(category) or requests.get("general")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{key}: {payload['status']}")
        if payload.get("permission_request"):
            print(f"permission request: {payload['permission_request']}")
        if payload["status"] in {"allowed-with-conditions", "agreement-required", "permission-required", "reserved", "not-granted"}:
            print("See the controlling legal instrument; this output is informational metadata, not legal authorization.")
    return 0




def _lookup_policy_value(d: dict, key: str):
    for section in ["permissions", "ai", "rights_reservations"]:
        if key in d.get(section, {}):
            return section, d[section][key]
    return None, None


def _request_route(d: dict, key: str, section: str | None):
    requests = d.get("permission_requests", {})
    if key == "organization_evaluation":
        category = "evaluation"
    elif section in {"ai", "rights_reservations"} or any(token in key for token in ["model", "training", "dataset", "fine_tuning", "pretraining"]):
        category = "ai"
    else:
        category = "commercial"
    return requests.get(category) or requests.get("general")


def cmd_preflight(args):
    base = pathlib.Path(args.path).resolve()
    pp = base if base.is_file() else base / PASSPORT_NAME
    errors = validate_passport(pp)
    if errors:
        payload = {
            "format": "Kiyoshima Preflight Decision",
            "decision": "unknown",
            "reason": "invalid-passport",
            "errors": errors,
            "legal_authority": "informational-only",
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else "unknown — invalid Passport")
        return 4 if args.strict else 0
    d = load_json(pp)
    section, value = _lookup_policy_value(d, args.action)
    if value is None:
        decision = "unknown"
    elif value in {"allowed", "allowed-within-principal-rights"}:
        decision = "allowed-within-declared-scope"
    elif value in {"allowed-with-conditions", "allowed-within-license-scope", "no-additional-kiyoshima-restriction"}:
        decision = "allowed-with-conditions"
    elif value in {"agreement-required", "permission-required"}:
        decision = "permission-required"
    elif value in {"reserved", "reserved-to-extent-permitted-by-law", "not-granted"}:
        decision = "not-granted-by-public-license"
    else:
        decision = "unknown"
    payload = {
        "format": "Kiyoshima Preflight Decision",
        "protocol_version": d.get("protocol", {}).get("version", "unknown"),
        "project": d.get("project", {}).get("name"),
        "action": args.action,
        "state": value,
        "source": section,
        "decision": decision,
        "constraints": d.get("policy_constraints", {}),
        "legal_authority": "informational-only-license-text-controls",
    }
    needs_route = decision in {"permission-required", "not-granted-by-public-license", "unknown"}
    if decision == "allowed-with-conditions" and d.get("profile") == "source" and args.action == "organization_evaluation":
        needs_route = True
    if needs_route:
        payload["permission_request"] = _request_route(d, args.action, section)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{args.action}: {decision}")
        if value is not None:
            print(f"declared state: {value}")
        if payload.get("permission_request"):
            print(f"permission request: {payload['permission_request']}")
        if d.get("policy_constraints"):
            print("constraints:")
            for key, val in sorted(d["policy_constraints"].items()):
                print(f"  {key}: {val}")
        print("Legal text controls; preflight is conservative informational metadata, not legal advice or authorization.")
    if not args.strict:
        return 0
    if decision == "allowed-within-declared-scope":
        return 0
    if decision == "allowed-with-conditions":
        return 10
    if decision in {"permission-required", "not-granted-by-public-license"}:
        return 20
    return 30


def cmd_verify_grant(args):
    record_path = pathlib.Path(args.record).resolve()
    try:
        record = load_json(record_path)
    except Exception as exc:
        print(f"ERROR: cannot parse grant record: {exc}", file=sys.stderr)
        return 2
    grant_id = record.get("grant_id")
    if not grant_id:
        print("ERROR: grant record has no grant_id", file=sys.stderr)
        return 2
    doc = pathlib.Path(args.document).resolve() if args.document else record_path.with_name(f"{grant_id}.md")
    if not doc.exists():
        print(f"ERROR: grant document not found: {doc}", file=sys.stderr)
        return 2
    expected = record.get("authentication", {}).get("document_sha256")
    actual = sha256_file(doc)
    errors = []
    if not expected:
        errors.append("record has no authentication.document_sha256")
    elif expected.lower() != actual.lower():
        errors.append(f"document digest mismatch: expected {expected}, actual {actual}")
    if record.get("format") != "Kiyoshima Rights Grant Record":
        errors.append("unexpected record format")
    if record.get("schema_version") not in {"1.1", "1.2"}:
        errors.append("unsupported grant-record schema")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"grant integrity: OK — {grant_id}")
    print(f"document sha256: {actual}")
    sig_type = record.get("authentication", {}).get("signature_type")
    sig_ref = record.get("authentication", {}).get("signature_reference")
    if sig_type in {None, "pending"} or sig_ref in {None, "pending"}:
        print("authentication: digest verified; external signature/platform authentication is not recorded yet")
    else:
        print(f"authentication metadata: {sig_type} — {sig_ref}")
    return 0


def cmd_export_tdm(args):
    origin = args.origin.rstrip("/")
    policy_url = args.policy_url or f"{origin}/policies/kiyoshima-tdm.jsonld"
    outdir = pathlib.Path(args.output_dir).resolve()
    well_known = outdir / ".well-known"
    policy_dir = outdir / "policies"
    well_known.mkdir(parents=True, exist_ok=True)
    policy_dir.mkdir(parents=True, exist_ok=True)
    tdmrep = [{"location": args.location, "tdm-reservation": 1, "tdm-policy": policy_url}]
    policy = {
        "@context": [
            "http://www.w3.org/ns/odrl.jsonld",
            "http://www.w3.org/ns/tdmrep.jsonld"
        ],
        "uid": policy_url,
        "@type": "Offer",
        "profile": "http://www.w3.org/ns/tdmrep",
        "assigner": {
            "uid": origin,
            "vcard:fn": args.rightsholder,
            "vcard:hasURL": args.contact,
        },
        "permission": [{
            "target": args.target or origin + "/",
            "action": "tdm:mine",
            "duty": [{"action": "obtainConsent"}],
            "constraint": [{"leftOperand": "purpose", "operator": "eq", "rightOperand": "tdm:non-research"}],
        }],
    }
    dump_json(well_known / "tdmrep.json", tdmrep)
    dump_json(policy_dir / "kiyoshima-tdm.jsonld", policy)
    print(f"wrote {well_known / 'tdmrep.json'}")
    print(f"wrote {policy_dir / 'kiyoshima-tdm.jsonld'}")
    print("Deploy these files only on an HTTP origin you control. The legal license remains controlling.")
    return 0

def cmd_policy_summary(args):
    base = pathlib.Path(args.path).resolve()
    pp = base if base.is_file() else base / PASSPORT_NAME
    errors = validate_passport(pp)
    if errors:
        if args.json:
            print(json.dumps({"status": "invalid-passport", "errors": errors}, indent=2))
        else:
            print("Passport invalid:")
            for e in errors:
                print(f"- {e}")
        return 1
    d = load_json(pp)
    payload = {
        "project": d.get("project", {}),
        "profile": d.get("profile"),
        "license": d.get("license", {}),
        "permissions": d.get("permissions", {}),
        "ai": d.get("ai", {}),
        "rights_reservations": d.get("rights_reservations", {}),
        "permission_requests": d.get("permission_requests", {}),
        "policy_constraints": d.get("policy_constraints", {}),
        "protocol": d.get("protocol", {}),
        "automation": d.get("automation", {}),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    name = payload["project"].get("name", "unknown project")
    print(f"Kiyoshima policy summary — {name}")
    print(f"profile: {payload['profile']}")
    print(f"license: {payload['license'].get('name')} [{payload['license'].get('status', 'unspecified')}]" )
    print()
    for title, section in [("permissions", "permissions"), ("AI", "ai"), ("rights reservations", "rights_reservations")]:
        print(f"{title}:")
        for key, value in sorted(payload[section].items()):
            print(f"  {key}: {value}")
        print()
    print("permission requests:")
    for key, value in sorted(payload["permission_requests"].items()):
        print(f"  {key}: {value}")
    print()
    print("Legal text controls. Unknown or conflicting metadata does not create permission.")
    return 0


def cmd_status(args):
    releases = load_json(ROOT / "registry" / "releases.json")
    entry = next((e for e in releases.get("entries", []) if e.get("canonical_id") == CANONICAL_ID), {})
    projects = load_json(ROOT / "registry" / "projects.json").get("entries", [])
    adopters = load_json(ROOT / "registry" / "adopters.json").get("entries", [])
    grants = load_json(ROOT / "registry" / "grants.public.json").get("entries", [])
    targets = load_json(ROOT / "monitor" / "targets.json")
    queries = targets.get("queries", []) + targets.get("project_queries", [])
    blockers = []
    if entry.get("status") != "final":
        blockers.append("legal text is not frozen/final")
    pp = load_json(ROOT / PASSPORT_NAME)
    if pp.get("license", {}).get("status") != "final":
        blockers.append("framework Passport marks the license as release-candidate")
    if pp.get("license", {}).get("candidate_revision"):
        blockers.append(f"current candidate revision is {pp['license']['candidate_revision']}")
    errors = framework_errors()
    if errors:
        blockers.append(f"framework integrity has {len(errors)} issue(s)")
    payload = {
        "format": "Kiyoshima Operator Status",
        "framework_version": FRAMEWORK_VERSION,
        "framework_root": str(ROOT),
        "license": {
            "canonical_id": CANONICAL_ID,
            "status": entry.get("status", "unknown"),
            "candidate_revision": entry.get("candidate_revision"),
            "sha256": sha256_file(CANONICAL) if CANONICAL.exists() else None,
            "passport_schema": CURRENT_PASSPORT_SCHEMA,
        },
        "registries": {
            "owned_projects": len(projects),
            "adopters": len(adopters),
            "public_grants": len(grants),
        },
        "monitoring": {"queries": len(queries)},
        "integrity": "healthy" if not errors else "issues",
        "finalization_blockers": blockers,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if not errors else 1
    print("Kiyoshima Licensing Framework status")
    print(f"framework: {FRAMEWORK_VERSION}")
    print(f"license: {CANONICAL_ID} — {payload['license']['status']}")
    if payload['license']['candidate_revision']:
        print(f"candidate: {payload['license']['candidate_revision']}")
    print(f"sha256: {payload['license']['sha256']}")
    print(f"Passport schema: {CURRENT_PASSPORT_SCHEMA}")
    print(f"integrity: {payload['integrity']}")
    print(f"owned projects: {len(projects)}")
    print(f"registered adopters: {len(adopters)}")
    print(f"public grants: {len(grants)}")
    print(f"monitor queries: {len(queries)}")
    if blockers:
        print("finalization blockers:")
        for item in blockers:
            print(f"  - {item}")
    else:
        print("finalization blockers: none detected locally")
    return 0 if not errors else 1

def _cargo_member_manifests(base: pathlib.Path, root_data: dict) -> list[pathlib.Path]:
    workspace = root_data.get("workspace")
    if not isinstance(workspace, dict):
        return []
    manifests = []
    seen = set()
    for pattern in workspace.get("members", []) or []:
        if not isinstance(pattern, str):
            continue
        for match in base.glob(pattern):
            candidate = match / "Cargo.toml" if match.is_dir() else match
            if candidate.name != "Cargo.toml" or not candidate.is_file():
                continue
            candidate = candidate.resolve()
            if candidate not in seen:
                seen.add(candidate)
                manifests.append(candidate)
    return sorted(manifests)


def _cargo_package_license_warning(
    manifest: pathlib.Path,
    data: dict,
    expected: str,
    workspace_license: str | None,
    base: pathlib.Path,
) -> list[str]:
    package = data.get("package")
    if not isinstance(package, dict):
        return []
    rel = manifest.relative_to(base).as_posix()
    value = package.get("license")
    if isinstance(value, str):
        if value != expected:
            return [f"{rel}: package.license is {value!r}, expected {expected!r}"]
        return []
    if isinstance(value, dict) and value.get("workspace") is True:
        if workspace_license != expected:
            return [f"{rel}: license.workspace=true but workspace.package.license is not {expected!r}"]
        return []
    if package.get("license-file"):
        return [f"{rel}: uses package.license-file; standard Kiyoshima Open projects should prefer package.license = {expected!r}"]
    return [f"{rel}: package license metadata is missing; add license = {expected!r} or inherit it from workspace.package"]


def cargo_license_warnings(base: pathlib.Path, expected: str) -> list[str]:
    cargo = base / "Cargo.toml"
    if not cargo.exists() or tomllib is None:
        return []
    try:
        root_data = tomllib.loads(cargo.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"Cargo.toml could not be parsed for license metadata: {exc}"]

    workspace = root_data.get("workspace")
    workspace_license = None
    if isinstance(workspace, dict):
        package_defaults = workspace.get("package")
        if isinstance(package_defaults, dict) and isinstance(package_defaults.get("license"), str):
            workspace_license = package_defaults["license"]

    warnings = _cargo_package_license_warning(cargo, root_data, expected, workspace_license, base)
    for manifest in _cargo_member_manifests(base, root_data):
        try:
            data = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            warnings.append(f"{manifest.relative_to(base).as_posix()}: could not parse Cargo manifest: {exc}")
            continue
        warnings.extend(_cargo_package_license_warning(manifest, data, expected, workspace_license, base))
    return warnings


def project_warnings(base: pathlib.Path) -> list[str]:
    passport_path = base / PASSPORT_NAME
    if not passport_path.exists():
        return []
    try:
        d = load_json(passport_path)
    except Exception:
        return []
    warnings = []
    if d.get("profile") == "open":
        expression = d.get("license", {}).get("spdx_expression")
        if isinstance(expression, str):
            warnings.extend(cargo_license_warnings(base, expression))
        for name in ["LICENSE-MIT", "LICENSE-APACHE"]:
            if (base / name).exists():
                warnings.append(f"legacy redundant file {name} is present; run compact-project")
        if (base / "README-LICENSING.md").exists():
            warnings.append("generated README-LICENSING.md is at project root; prefer README/docs or remove it after merging")
    return warnings


def cmd_doctor(args):
    base = pathlib.Path(args.path).resolve()
    is_framework = (base / "registry" / "releases.json").exists() and (base / "tools" / "klicense.py").exists()
    if is_framework:
        errors = framework_errors()
        warnings = []
        kind = "framework"
    else:
        errors = project_errors(base)
        warnings = project_warnings(base) if not errors else []
        kind = "project"
    print(f"Kiyoshima doctor — {kind}: {base}")
    if errors:
        print(f"status: {len(errors)} issue(s)")
        for e in errors:
            print(f"- ERROR: {e}")
        return 1
    print("status: healthy")
    if warnings:
        print("recommendations:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


def ignored(path: pathlib.Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def cmd_fingerprint(args):
    base = pathlib.Path(args.path).resolve()
    files = []
    for p in sorted(base.rglob("*")):
        if not p.is_file() or ignored(p.relative_to(base)):
            continue
        if p.stat().st_size > args.max_bytes:
            continue
        rel = p.relative_to(base).as_posix()
        files.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    tree = hashlib.sha256()
    for item in files:
        tree.update(item["path"].encode())
        tree.update(b"\0")
        tree.update(item["sha256"].encode())
        tree.update(b"\n")
    payload = {
        "format": "Kiyoshima Project Fingerprint",
        "schema_version": "1.1",
        "generated_at": now_iso(),
        "root": base.name,
        "tree_sha256": tree.hexdigest(),
        "files": files,
    }
    out = pathlib.Path(args.output)
    dump_json(out, payload)
    print(f"wrote {out} ({len(files)} files, tree {payload['tree_sha256']})")
    return 0


def github_search(query: str, token: str):
    params = urllib.parse.urlencode({"q": query, "per_page": 100})
    req = urllib.request.Request(
        f"https://api.github.com/search/code?{params}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "kiyoshima-license-monitor/1.1",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def known_repositories() -> set[str]:
    repos = set()
    for rel in ["registry/projects.json", "registry/adopters.json"]:
        try:
            for e in load_json(ROOT / rel).get("entries", []):
                r = e.get("repository", "")
                if r.startswith("https://github.com/"):
                    repos.add(r.removeprefix("https://github.com/").strip("/"))
                elif "/" in r and not r.startswith("http"):
                    repos.add(r.strip("/"))
        except Exception:
            pass
    repos.add("moderubias/licensing")
    repos.add("moderubias/kiyoshima-licensing")
    return repos


def cmd_monitor(args):
    token = os.environ.get("KIYOSHIMA_MONITOR_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        msg = "No GitHub token found; set KIYOSHIMA_MONITOR_TOKEN, GH_TOKEN, or GITHUB_TOKEN."
        if args.allow_no_token:
            print(msg)
            return 0
        print(f"ERROR: {msg}", file=sys.stderr)
        return 2
    cfg = load_json(pathlib.Path(args.config))
    known = known_repositories()
    rows = []
    unknown_repos = set()
    for q in cfg.get("queries", []) + cfg.get("project_queries", []):
        row = {"name": q.get("name"), "query": q.get("query"), "project": q.get("project")}
        try:
            result = github_search(q["query"], token)
            items = []
            for i in result.get("items", []):
                repo = i.get("repository", {}).get("full_name")
                classification = "known" if repo in known else "unknown-candidate"
                if repo and classification == "unknown-candidate":
                    unknown_repos.add(repo)
                items.append({
                    "repository": repo,
                    "classification": classification,
                    "html_url": i.get("html_url"),
                    "path": i.get("path"),
                    "sha": i.get("sha"),
                })
            row["total_count"] = result.get("total_count", 0)
            row["items"] = items
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    payload = {
        "format": "Kiyoshima License Watch Report",
        "schema_version": "1.1",
        "generated_at": now_iso(),
        "warning": "Search hits are leads, not proof of infringement.",
        "unknown_candidate_repositories": sorted(unknown_repos),
        "results": rows,
    }
    out = pathlib.Path(args.output)
    dump_json(out, payload)
    print(f"wrote {out}; unknown candidate repositories: {len(unknown_repos)}")
    return 0


def cmd_summarize_watch(args):
    d = load_json(pathlib.Path(args.path))
    unknown = d.get("unknown_candidate_repositories", [])
    print("## Kiyoshima License Watch")
    print()
    print(f"Generated: {d.get('generated_at', 'unknown')}")
    print()
    print(f"Unknown candidate repositories: **{len(unknown)}**")
    if unknown:
        print()
        for repo in unknown[:50]:
            print(f"- `{repo}`")
    print()
    print("> Search hits are leads, not proof of infringement. Human rights/scope review is required.")
    return 0


def register_entry(registry_path: pathlib.Path, entry: dict):
    data = load_json(registry_path)
    entries = data.setdefault("entries", [])
    key = entry.get("repository") or entry.get("grant_id")
    if key and any((e.get("repository") or e.get("grant_id")) == key for e in entries):
        raise SystemExit(f"entry already exists for {key}")
    entries.append(entry)
    dump_json(registry_path, data)


def cmd_register_project(args):
    license_id = args.license
    if not license_id:
        if args.profile == "source":
            license_id = CANONICAL_ID
        else:
            print("ERROR: --license is required for open/commercial registry entries", file=sys.stderr)
            return 2
    entry = {
        "name": args.name,
        "repository": args.repository,
        "profile": args.profile,
        "license": license_id,
        "added_at": today_iso(),
    }
    register_entry(ROOT / "registry" / "projects.json", entry)
    print(f"registered owned project: {args.repository}")
    return 0


def cmd_register_adopter(args):
    entry = {
        "name": args.name,
        "repository": args.repository,
        "license": CANONICAL_ID,
        "passport": args.passport,
        "added_at": today_iso(),
        "verified": False,
    }
    register_entry(ROOT / "registry" / "adopters.json", entry)
    print(f"registered adopter candidate: {args.repository}")
    return 0


def cmd_new_grant(args):
    if not (args.grantee_github or args.grantee_fingerprint or args.grantee_name):
        print("ERROR: provide at least one grantee identifier", file=sys.stderr)
        return 2
    outdir = pathlib.Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    md = outdir / f"{args.grant_id}.md"
    if md.exists() and not args.force:
        print(f"ERROR: refusing to overwrite {md}; use --force", file=sys.stderr)
        return 2
    grantee_lines = []
    if args.grantee_name:
        grantee_lines.append(f"- Legal/public name: {args.grantee_name}")
    if args.grantee_github:
        grantee_lines.append(f"- GitHub: @{args.grantee_github.lstrip('@')}")
    if args.grantee_fingerprint:
        grantee_lines.append(f"- Public-key fingerprint: {args.grantee_fingerprint}")
    rights = sorted(set(args.right or []))
    text = f"""# Kiyoshima Rights Grant\n\n**Grant ID:** {args.grant_id}\n\n**Issuer / Licensor:** {args.issuer}\n\n**Effective date:** {args.effective_date or today_iso()}\n\n**Visibility:** {args.visibility}\n\n## Grantee identity\n\n{chr(10).join(grantee_lines)}\n\n## Covered scope\n\n- Projects: {args.project}\n- Versions: {args.versions}\n- Future versions: {args.future_versions}\n- Territory: {args.territory}\n- Expiry: {args.expiry}\n\n## Granted rights\n\n"""
    for r in rights:
        text += f"- {r}\n"
    text += "\nAll rights not expressly listed remain reserved. No trademark, sublicensing, relicensing, transfer, or AI/model-improvement right is implied.\n\n## Conditions\n\n" + (args.conditions or "None beyond applicable underlying conditions and this Grant.") + "\n\n## Authentication\n\nAuthenticate these final bytes with a signature or attributable platform record. The detached SHA-256 record accompanying this file identifies the exact bytes.\n"
    md.write_text(text, encoding="utf-8")
    digest = sha256_file(md)
    sha_path = md.with_suffix(md.suffix + ".sha256")
    sha_path.write_text(f"{digest}  {md.name}\n", encoding="utf-8")
    record = {
        "format":"Kiyoshima Rights Grant Record",
        "schema_version":"1.1",
        "grant_id":args.grant_id,
        "visibility":args.visibility,
        "issuer":{"display":args.issuer},
        "grantee":{k:v for k,v in {"name":args.grantee_name,"github":args.grantee_github,"public_key_fingerprint":args.grantee_fingerprint}.items() if v},
        "scope":{"projects":args.project,"versions":args.versions,"future_versions":args.future_versions,"territory":args.territory,"expiry":args.expiry},
        "rights":{r:True for r in rights},
        "conditions":[args.conditions] if args.conditions else [],
        "authentication":{"document_sha256":digest,"signature_type":"pending","signature_reference":"pending"},
    }
    record_path = outdir / f"{args.grant_id}.record.json"
    dump_json(record_path, record)
    print(f"wrote {md}")
    print(f"wrote {sha_path}")
    print(f"wrote {record_path}")
    print("Sign/authenticate the finalized .md file; then update signature metadata in the record if desired.")
    return 0


def main():
    p = argparse.ArgumentParser(prog="klicense", description="Kiyoshima Licensing Framework utility")
    p.add_argument("--version", action="version", version=f"klicense {FRAMEWORK_VERSION} (Passport schema {CURRENT_PASSPORT_SCHEMA})")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("verify-framework", help="Verify canonical legal digest, repository licensing, registries, Passport, and manifest.")
    s.set_defaults(func=cmd_verify_framework)

    s = sub.add_parser("release-check", help="Fail unless the framework is integrity-clean and explicitly frozen/final.")
    s.set_defaults(func=cmd_release_check)

    s = sub.add_parser("manifest", help="Verify or regenerate MANIFEST.sha256.")
    s.add_argument("path", nargs="?", default=str(ROOT))
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_manifest)

    s = sub.add_parser("validate-passport")
    s.add_argument("path")
    s.add_argument("--current", action="store_true", help="Require the current schema version.")
    s.set_defaults(func=cmd_validate_passport)

    s = sub.add_parser("verify-project")
    s.add_argument("path", nargs="?", default=".")
    s.set_defaults(func=cmd_verify_project)

    s = sub.add_parser("policy-summary", help="Print the normalized human/machine policy summary for a Passport.")
    s.add_argument("path", nargs="?", default=".")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_policy_summary)

    s = sub.add_parser("status", help="Show operator status: candidate/release state, registries, monitoring, integrity, and finalization blockers.")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("doctor")
    s.add_argument("path", nargs="?", default=".")
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("init-project")
    s.add_argument("path")
    s.add_argument("--profile", choices=["open", "source"], default="source")
    s.add_argument(
        "--open-license",
        choices=sorted(GENERATED_OPEN_LICENSES),
        default="Apache-2.0",
        help="Controlling SPDX license expression generated for --profile open.",
    )
    s.add_argument("--name", required=True)
    s.add_argument("--kind", default="application")
    s.add_argument("--repository", required=True)
    s.add_argument("--holder", required=True)
    s.add_argument("--contact", help="General licensing contact or request URL. Required for Source; defaults to repository URL for Open.")
    s.add_argument("--commercial-contact", help="Optional dedicated commercial/organizational request URL.")
    s.add_argument("--ai-contact", help="Optional dedicated AI/model-training request URL.")
    s.add_argument("--evaluation-contact", help="Optional dedicated organization-evaluation extension URL.")
    s.add_argument("--reuse", action="store_true", help="Opt in to REUSE.toml and duplicate LICENSES/ copies where needed.")
    s.add_argument("--notice", action="store_true", help="Opt in to a project NOTICE file. Not generated by default.")
    s.add_argument("--readme-snippet", help="Optional project-relative path for a generated licensing snippet, e.g. docs/README-LICENSING.md.")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_init_project)

    s = sub.add_parser("compact-project", help="Migrate generated Kiyoshima project licensing to the lean layout with a backup.")
    s.add_argument("path", nargs="?", default=".")
    s.add_argument("--apply", action="store_true", help="Apply the compaction. Without this flag, only print the plan.")
    s.set_defaults(func=cmd_compact_project)

    s = sub.add_parser("sync-project", help="Safely sync an existing Kiyoshima Source project to this framework candidate, with backups.")
    s.add_argument("path")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=cmd_sync_project)

    s = sub.add_parser("upgrade-passport", help=f"Upgrade a project Passport from schema 1.0/1.1/1.2 to {CURRENT_PASSPORT_SCHEMA} with a backup.")
    s.add_argument("path")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_upgrade_passport)

    s = sub.add_parser("query-right", help="Query one machine-readable permission/reservation key.")
    s.add_argument("path")
    s.add_argument("right")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_query_right)

    s = sub.add_parser("preflight", help="Conservative agent/CI preflight for a declared action key.")
    s.add_argument("path")
    s.add_argument("action")
    s.add_argument("--json", action="store_true")
    s.add_argument("--strict", action="store_true", help="Use non-zero exit codes for conditional/permission-required/unknown states.")
    s.set_defaults(func=cmd_preflight)

    s = sub.add_parser("verify-grant", help="Verify a Kiyoshima Rights Grant document against its detached machine record digest.")
    s.add_argument("record")
    s.add_argument("--document")
    s.set_defaults(func=cmd_verify_grant)

    s = sub.add_parser("export-tdm", help="Generate deployable W3C TDMRep reservation and policy files for an origin you control.")
    s.add_argument("--origin", required=True)
    s.add_argument("--rightsholder", required=True)
    s.add_argument("--contact", required=True)
    s.add_argument("--output-dir", required=True)
    s.add_argument("--policy-url")
    s.add_argument("--location", default="/")
    s.add_argument("--target")
    s.set_defaults(func=cmd_export_tdm)

    s = sub.add_parser("fingerprint")
    s.add_argument("path")
    s.add_argument("--output", default="kiyoshima-fingerprint.json")
    s.add_argument("--max-bytes", type=int, default=2_000_000)
    s.set_defaults(func=cmd_fingerprint)

    s = sub.add_parser("monitor")
    s.add_argument("--config", default=str(ROOT / "monitor" / "targets.json"))
    s.add_argument("--output", default="kiyoshima-watch.json")
    s.add_argument("--allow-no-token", action="store_true")
    s.set_defaults(func=cmd_monitor)

    s = sub.add_parser("summarize-watch")
    s.add_argument("path")
    s.set_defaults(func=cmd_summarize_watch)

    s = sub.add_parser("register-project")
    s.add_argument("--name", required=True)
    s.add_argument("--repository", required=True)
    s.add_argument("--profile", choices=["open", "source", "commercial"], required=True)
    s.add_argument("--license", default=None, help="License/SPDX expression. Defaults to Kiyoshima Source only for --profile source.")
    s.set_defaults(func=cmd_register_project)

    s = sub.add_parser("register-adopter")
    s.add_argument("--name", required=True)
    s.add_argument("--repository", required=True)
    s.add_argument("--passport", default=None)
    s.set_defaults(func=cmd_register_adopter)

    s = sub.add_parser("new-grant", help="Create a Rights Grant plus detached SHA-256 and machine record.")
    s.add_argument("--grant-id", required=True)
    s.add_argument("--issuer", required=True)
    s.add_argument("--project", required=True)
    s.add_argument("--versions", default="existing versions")
    s.add_argument("--future-versions", choices=["included", "excluded"], default="excluded")
    s.add_argument("--territory", default="worldwide")
    s.add_argument("--expiry", default="none")
    s.add_argument("--effective-date", default=None)
    s.add_argument("--visibility", choices=["private", "public"], default="private")
    s.add_argument("--grantee-name")
    s.add_argument("--grantee-github")
    s.add_argument("--grantee-fingerprint")
    s.add_argument("--right", action="append", default=[])
    s.add_argument("--conditions")
    s.add_argument("--output-dir", default=".")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_new_grant)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
