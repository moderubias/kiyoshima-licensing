import argparse
import importlib.util
import json
import pathlib
import tempfile
import unittest
import contextlib
import io

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("klicense", ROOT / "tools" / "klicense.py")
k = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(k)


class KlicenseTests(unittest.TestCase):
    def test_canonical_hash_consistency(self):
        digest = k.sha256_file(k.CANONICAL)
        passport = k.load_json(ROOT / "KIYOSHIMA.json")
        releases = k.load_json(ROOT / "registry" / "releases.json")
        self.assertEqual(passport["license"]["sha256"], digest)
        self.assertEqual(releases["entries"][0]["sha256"], digest)

    def test_framework_passport_current(self):
        self.assertEqual(k.validate_passport(ROOT / "KIYOSHIMA.json", require_current=True), [])

    def test_project_init_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "example"
            template = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
            template["project"].update({
                "name": "Example",
                "kind": "application",
                "repository": "https://example.invalid/example",
                "copyright_holder": "Example Holder",
                "contact": "https://example.invalid/licensing",
            })
            for key in template["permission_requests"]:
                template["permission_requests"][key] = "https://example.invalid/licensing"
            base.mkdir()
            (base / "LICENSES").mkdir()
            (base / "LICENSE").write_bytes(k.CANONICAL.read_bytes())
            (base / "LICENSES" / f"{k.SPDX_REF}.txt").write_bytes(k.CANONICAL.read_bytes())
            k.dump_json(base / "KIYOSHIMA.json", template)
            self.assertEqual(k.project_errors(base), [])

    def test_open_apache_init_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "open-apache"
            args = argparse.Namespace(
                path=str(base), profile="open", open_license="Apache-2.0",
                name="OpenApache", kind="library", repository="https://example.invalid/open-apache",
                holder="Example Holder", contact=None, commercial_contact=None,
                ai_contact=None, evaluation_contact=None, dry_run=False, force=False,
            )
            self.assertEqual(k.cmd_init_project(args), 0)
            self.assertEqual(k.project_errors(base), [])
            d = k.load_json(base / "KIYOSHIMA.json")
            self.assertEqual(d["profile"], "open")
            self.assertEqual(d["license"]["spdx_expression"], "Apache-2.0")
            self.assertNotIn("canonical_id", d["license"])
            self.assertEqual((base / "LICENSE").read_bytes(), (base / "LICENSES" / "Apache-2.0.txt").read_bytes())
            self.assertNotIn("commercial", d["permission_requests"])

    def test_open_dual_init_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "open-dual"
            args = argparse.Namespace(
                path=str(base), profile="open", open_license="MIT OR Apache-2.0",
                name="OpenDual", kind="library", repository="https://example.invalid/open-dual",
                holder="Example Holder", contact=None, commercial_contact=None,
                ai_contact=None, evaluation_contact=None, dry_run=False, force=False,
            )
            self.assertEqual(k.cmd_init_project(args), 0)
            self.assertEqual(k.project_errors(base), [])
            d = k.load_json(base / "KIYOSHIMA.json")
            self.assertEqual(d["license"]["spdx_expression"], "MIT OR Apache-2.0")
            self.assertEqual((base / "LICENSE-MIT").read_bytes(), (base / "LICENSES" / "MIT.txt").read_bytes())
            self.assertEqual((base / "LICENSE-APACHE").read_bytes(), (base / "LICENSES" / "Apache-2.0.txt").read_bytes())
            self.assertIn(b"Kiyoshima Open Profile", (base / "LICENSE").read_bytes())

    def test_open_supporting_license_tamper_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "open-mit"
            args = argparse.Namespace(
                path=str(base), profile="open", open_license="MIT",
                name="OpenMIT", kind="library", repository="https://example.invalid/open-mit",
                holder="Example Holder", contact=None, commercial_contact=None,
                ai_contact=None, evaluation_contact=None, dry_run=False, force=False,
            )
            self.assertEqual(k.cmd_init_project(args), 0)
            (base / "LICENSES" / "MIT.txt").write_text("tampered\n")
            errors = k.project_errors(base)
            self.assertTrue(any("supporting license hash mismatch" in e for e in errors))

    def test_source_identity_is_required_by_validator(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            (base / "LICENSES").mkdir()
            (base / "LICENSE").write_bytes(k.CANONICAL.read_bytes())
            (base / "LICENSES" / f"{k.SPDX_REF}.txt").write_bytes(k.CANONICAL.read_bytes())
            d = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
            d["project"].update({
                "name": "Example", "kind": "application",
                "repository": "https://example.invalid/example",
                "copyright_holder": "Example Holder",
                "contact": "https://example.invalid/licensing",
            })
            for key in d["permission_requests"]:
                d["permission_requests"][key] = "https://example.invalid/licensing"
            d["license"].pop("canonical_id")
            d["license"].pop("version")
            k.dump_json(base / "KIYOSHIMA.json", d)
            errors = k.validate_passport(base / "KIYOSHIMA.json", require_current=True)
            self.assertTrue(any("source license.canonical_id" in e for e in errors))
            self.assertTrue(any("source license.version" in e for e in errors))

    def test_malformed_authoritative_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            d = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA-OPEN.json")
            d["project"].update({
                "name": "Malformed", "kind": "library",
                "repository": "https://example.invalid/malformed",
                "copyright_holder": "Example Holder",
                "contact": "https://example.invalid/malformed",
            })
            d["permission_requests"]["general"] = "https://example.invalid/malformed"
            d["license"]["authoritative_file"] = 123
            k.dump_json(base / "KIYOSHIMA.json", d)
            errors = k.validate_passport(base / "KIYOSHIMA.json", require_current=True)
            self.assertTrue(any("authoritative_file" in e for e in errors))

    def test_open_ai_preflight_is_conditional_not_permission_required(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "open-ai"
            args = argparse.Namespace(
                path=str(base), profile="open", open_license="Apache-2.0",
                name="OpenAI", kind="library", repository="https://example.invalid/open-ai",
                holder="Example Holder", contact=None, commercial_contact=None,
                ai_contact=None, evaluation_contact=None, dry_run=False, force=False,
            )
            self.assertEqual(k.cmd_init_project(args), 0)
            preflight = argparse.Namespace(path=str(base), action="model_training", json=True, strict=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = k.cmd_preflight(preflight)
            self.assertEqual(code, 10)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["decision"], "allowed-with-conditions")
            self.assertNotIn("permission_request", payload)

    def test_sync_project_updates_legal_bytes_and_passport(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td) / "legacy"
            base.mkdir()
            (base / "LICENSES").mkdir()
            (base / "LICENSE").write_text("old candidate\n")
            (base / "LICENSES" / f"{k.SPDX_REF}.txt").write_text("old candidate\n")
            d = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
            d["schema_version"] = "1.0"
            d.pop("declaration_scope", None)
            d.pop("rights_reservations", None)
            d.pop("permission_requests", None)
            d["project"].update({
                "name": "Legacy",
                "kind": "application",
                "repository": "https://example.invalid/legacy",
                "copyright_holder": "Legacy Holder",
                "contact": "https://example.invalid/licensing",
            })
            d["license"]["sha256"] = "0" * 64
            k.dump_json(base / "KIYOSHIMA.json", d)
            args = argparse.Namespace(path=str(base), dry_run=False)
            self.assertEqual(k.cmd_sync_project(args), 0)
            self.assertEqual((base / "LICENSE").read_bytes(), k.CANONICAL.read_bytes())
            synced = k.load_json(base / "KIYOSHIMA.json")
            self.assertEqual(synced["schema_version"], k.CURRENT_PASSPORT_SCHEMA)
            self.assertEqual(synced["license"]["sha256"], k.sha256_file(k.CANONICAL))
            self.assertEqual(k.project_errors(base), [])
            backups = list(pathlib.Path(td).glob("legacy.kiyoshima-backup-*"))
            self.assertEqual(len(backups), 1)

    def test_project_tampered_license_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            d = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
            d["project"].update({
                "name":"X", "kind":"application", "repository":"https://example.invalid/x",
                "copyright_holder":"X", "contact":"https://example.invalid/licensing"
            })
            for key in d["permission_requests"]:
                d["permission_requests"][key] = "https://example.invalid/licensing"
            (base / "LICENSES").mkdir()
            (base / "LICENSE").write_text("tampered\n")
            (base / "LICENSES" / f"{k.SPDX_REF}.txt").write_text("tampered\n")
            k.dump_json(base / "KIYOSHIMA.json", d)
            errors = k.project_errors(base)
            self.assertTrue(any("hash mismatch" in e or "differ" in e for e in errors))

    def test_manifest_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            (base / "a.txt").write_text("a")
            (base / "b.txt").write_text("b")
            (base / k.MANIFEST_NAME).write_text(k.manifest_text(base))
            self.assertEqual(k.verify_manifest(base), [])
            (base / "a.txt").write_text("changed")
            self.assertTrue(any("hash mismatch" in e for e in k.verify_manifest(base)))

    def test_unknown_right_is_not_allowed(self):
        d = k.load_json(ROOT / "KIYOSHIMA.json")
        self.assertNotIn("totally_unknown_right", d["permissions"])
        self.assertEqual(d["automation"]["unknown_value_policy"], "do-not-infer-rights")

    def test_preflight_model_training_requires_permission(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            d = k.load_json(ROOT / "templates" / "project" / "KIYOSHIMA.json")
            d["project"].update({
                "name": "Example", "kind": "application", "repository": "https://example.invalid/example",
                "copyright_holder": "Example Holder", "contact": "https://example.invalid/licensing"
            })
            for key in d["permission_requests"]:
                d["permission_requests"][key] = "https://example.invalid/licensing"
            (base / "LICENSES").mkdir()
            (base / "LICENSE").write_bytes(k.CANONICAL.read_bytes())
            (base / "LICENSES" / f"{k.SPDX_REF}.txt").write_bytes(k.CANONICAL.read_bytes())
            k.dump_json(base / "KIYOSHIMA.json", d)
            args = argparse.Namespace(path=str(base), action="model_training", json=True, strict=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = k.cmd_preflight(args)
            self.assertEqual(code, 20)
            self.assertIn('"decision": "permission-required"', buf.getvalue())

    def test_grant_digest_verification(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td)
            doc = base / "KRG-2026-TEST.md"
            doc.write_text("grant bytes\n")
            record = {
                "format": "Kiyoshima Rights Grant Record",
                "schema_version": "1.2",
                "grant_id": "KRG-2026-TEST",
                "authentication": {"document_sha256": k.sha256_file(doc), "signature_type": "pending", "signature_reference": "pending"},
            }
            record_path = base / "KRG-2026-TEST.record.json"
            k.dump_json(record_path, record)
            args = argparse.Namespace(record=str(record_path), document=None)
            self.assertEqual(k.cmd_verify_grant(args), 0)
            doc.write_text("tampered\n")
            self.assertEqual(k.cmd_verify_grant(args), 1)

    def test_export_tdm(self):
        with tempfile.TemporaryDirectory() as td:
            args = argparse.Namespace(
                origin="https://example.com", rightsholder="Example Holder",
                contact="https://example.com/licensing", output_dir=td, policy_url=None, location="/", target=None
            )
            self.assertEqual(k.cmd_export_tdm(args), 0)
            rep = k.load_json(pathlib.Path(td) / ".well-known" / "tdmrep.json")
            policy = k.load_json(pathlib.Path(td) / "policies" / "kiyoshima-tdm.jsonld")
            self.assertEqual(rep[0]["tdm-reservation"], 1)
            self.assertEqual(policy["@context"][1], "http://www.w3.org/ns/tdmrep.jsonld")



if __name__ == "__main__":
    unittest.main()
