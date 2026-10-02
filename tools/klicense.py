#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "LICENSES" / "LicenseRef-Kiyoshima-Source-1.0.txt"
ROOT_LICENSE = ROOT / "LICENSE"
PASSPORT_NAME = "KIYOSHIMA.json"


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


def validate_passport(path: pathlib.Path) -> list[str]:
    errors = []
    try:
        d = load_json(path)
    except Exception as exc:
        return [f"cannot parse {path}: {exc}"]
    required = ["format", "schema_version", "project", "profile", "license", "permissions", "ai", "automation"]
    for key in required:
        if key not in d:
            errors.append(f"missing passport field: {key}")
    if d.get("format") != "Kiyoshima License Passport":
        errors.append("format must be 'Kiyoshima License Passport'")
    if d.get("schema_version") != "1.0":
        errors.append("unsupported schema_version")
    lic = d.get("license", {})
    auth = lic.get("authoritative_file")
    expected_hash = lic.get("sha256")
    if auth and expected_hash:
        candidate = path.parent / auth
        if candidate.exists():
            actual_hash = sha256_file(candidate)
            if actual_hash.lower() != str(expected_hash).lower():
                errors.append(f"authoritative license hash mismatch: expected {expected_hash}, actual {actual_hash}")
    auto = d.get("automation", {})
    invariants = {
        "conflict_policy": "deny-on-conflict",
        "missing_field_policy": "do-not-infer-rights",
        "machine_metadata_authority": "informational",
        "additional_permissions_require_authenticated_grant": True,
    }
    for key, expected in invariants.items():
        if auto.get(key) != expected:
            errors.append(f"automation.{key} must equal {expected!r}")
    return errors


def cmd_verify(args):
    errors = []
    if not CANONICAL.exists() or not ROOT_LICENSE.exists():
        errors.append("canonical license files are missing")
    elif CANONICAL.read_bytes() != ROOT_LICENSE.read_bytes():
        errors.append("LICENSE and canonical LICENSES copy differ")

    passport = ROOT / PASSPORT_NAME
    if passport.exists():
        errors.extend(validate_passport(passport))
    else:
        errors.append(f"missing {PASSPORT_NAME}")

    releases = ROOT / "registry" / "releases.json"
    if releases.exists() and CANONICAL.exists():
        data = load_json(releases)
        expected = None
        for entry in data.get("entries", []):
            if entry.get("canonical_id") == "Kiyoshima-Source-1.0":
                expected = entry.get("sha256")
                break
        actual = sha256_file(CANONICAL)
        if not expected:
            errors.append("release registry has no Kiyoshima-Source-1.0 hash")
        elif expected != actual:
            errors.append(f"canonical license hash mismatch: expected {expected}, actual {actual}")

    for rel in [
        "registry/projects.json",
        "registry/adopters.json",
        "registry/grants.json",
        "monitor/targets.json",
        "machine/schema/kiyoshima-passport.schema.json",
        "machine/schema/kiyoshima-grant.schema.json",
        "machine/schema/kiyoshima-registry.schema.json",
    ]:
        try:
            load_json(ROOT / rel)
        except Exception as exc:
            errors.append(f"invalid JSON {rel}: {exc}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("Kiyoshima framework integrity: OK")
    print(f"license sha256: {sha256_file(CANONICAL)}")
    return 0


def cmd_validate_passport(args):
    path = pathlib.Path(args.path)
    errors = validate_passport(path)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"License Passport valid: {path}")
    return 0


def ignored(path: pathlib.Path) -> bool:
    banned = {".git", "target", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
    return any(part in banned for part in path.parts)


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
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
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
            "User-Agent": "kiyoshima-license-monitor/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


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
    rows = []
    for q in cfg.get("queries", []) + cfg.get("project_queries", []):
        row = {"name": q.get("name"), "query": q.get("query"), "project": q.get("project")}
        try:
            result = github_search(q["query"], token)
            row["total_count"] = result.get("total_count", 0)
            row["items"] = [
                {
                    "repository": i.get("repository", {}).get("full_name"),
                    "html_url": i.get("html_url"),
                    "path": i.get("path"),
                    "sha": i.get("sha"),
                }
                for i in result.get("items", [])
            ]
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
    payload = {
        "format": "Kiyoshima License Watch Report",
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "warning": "Search hits are leads, not proof of infringement.",
        "results": rows,
    }
    out = pathlib.Path(args.output)
    dump_json(out, payload)
    print(f"wrote {out}")
    return 0


def register_entry(registry_path: pathlib.Path, entry: dict):
    data = load_json(registry_path)
    entries = data.setdefault("entries", [])
    key = entry.get("repository")
    if key and any(e.get("repository") == key for e in entries):
        raise SystemExit(f"entry already exists for {key}")
    entries.append(entry)
    dump_json(registry_path, data)


def cmd_register_project(args):
    entry = {
        "name": args.name,
        "repository": args.repository,
        "profile": args.profile,
        "license": args.license,
        "added_at": datetime.now(timezone.utc).date().isoformat(),
    }
    register_entry(ROOT / "registry" / "projects.json", entry)
    print(f"registered project: {args.repository}")
    return 0


def cmd_register_adopter(args):
    entry = {
        "name": args.name,
        "repository": args.repository,
        "license": "Kiyoshima-Source-1.0",
        "added_at": datetime.now(timezone.utc).date().isoformat(),
        "verified": False,
    }
    register_entry(ROOT / "registry" / "adopters.json", entry)
    print(f"registered adopter candidate: {args.repository}")
    return 0


def cmd_init(args):
    template = load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
    template["project"].update({
        "name": args.name,
        "kind": args.kind,
        "repository": args.repository,
        "copyright_holder": args.holder,
        "contact": args.contact,
    })
    out = pathlib.Path(args.output)
    dump_json(out, template)
    print(f"wrote {out}")
    return 0


def main():
    p = argparse.ArgumentParser(prog="klicense", description="Kiyoshima Licensing Framework utility")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("verify-framework")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("validate-passport")
    s.add_argument("path")
    s.set_defaults(func=cmd_validate_passport)

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

    s = sub.add_parser("register-project")
    s.add_argument("--name", required=True)
    s.add_argument("--repository", required=True)
    s.add_argument("--profile", choices=["open", "source", "commercial"], required=True)
    s.add_argument("--license", default="Kiyoshima-Source-1.0")
    s.set_defaults(func=cmd_register_project)

    s = sub.add_parser("register-adopter")
    s.add_argument("--name", required=True)
    s.add_argument("--repository", required=True)
    s.set_defaults(func=cmd_register_adopter)

    s = sub.add_parser("init-passport")
    s.add_argument("--name", required=True)
    s.add_argument("--kind", default="application")
    s.add_argument("--repository", required=True)
    s.add_argument("--holder", required=True)
    s.add_argument("--contact", required=True)
    s.add_argument("--output", default=PASSPORT_NAME)
    s.set_defaults(func=cmd_init)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
