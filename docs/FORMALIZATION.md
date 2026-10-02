# Formalization checklist

There is no universal authority that registers a software license and makes it valid. Copyright generally arises automatically; the operational objective is to make ownership, text, version, provenance, permission paths, and evidence unusually clear.

## Before declaring Source 1.0 final

1. Freeze the intended business model and legal semantics. Preserve every already-published candidate digest in `registry/candidates.json`; never silently reuse an immutable release identity for different final bytes.
2. Have a software/IP lawyer review the legal text for jurisdictions that materially matter to the steward and expected licensees.
3. Perform trademark/name clearance for the Kiyoshima license-family names before claiming registration.
4. Resolve contributor ownership/relicensing rights before accepting material third-party contributions where future dual licensing matters.
5. Decide the durable public identity/contact route of the license steward.
6. Run `python tools/klicense.py release-check`; do not release while it reports draft placeholders or integrity problems.

## Canonical release

7. Keep the canonical legal text only at the defined `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` path in the framework; project initializers copy those exact bytes.
8. Run `python tools/klicense.py manifest --write`, then `python tools/klicense.py verify-framework`.
9. Change release status from candidate to final only after legal review; recompute all legal-text digests in the same commit.
10. Protect `main` and release tags; require integrity checks and signed commits where practical.
11. Create a signed Git tag for the legal version and a separate framework tag.
12. Publish GitHub Release archives and provenance attestations.
13. Archive the frozen release through independent archival infrastructure such as Software Heritage and, when useful, Zenodo.
14. Never alter released 1.0 legal bytes in place.

## Ecosystem formalization

15. Use `LicenseRef-Kiyoshima-Source-1.0` immediately in SPDX-compatible metadata.
16. Follow REUSE Specification 3.3 for per-file licensing metadata.
17. After meaningful real-world adoption, consider submitting the legal instrument to the SPDX License List; inclusion is case-by-case and should not be assumed.
18. Do not seek OSI approval for the current Source profile because its organizational/commercial restrictions intentionally conflict with the Open Source Definition.
19. Maintain public release/adopter history and an explicit change log.

## Enforcement readiness

20. Maintain copyright notices, signed releases, and source history for commercially important projects.
21. Consider voluntary copyright registration where a relevant jurisdiction makes it materially useful for remedies or litigation posture.
22. Give every commercial agreement and special grant a unique ID and authenticated final copy.
23. Use detached hashes/signatures/attestations. Do not attempt to embed a file's own SHA-256 digest inside the exact bytes being hashed.
24. Record only the minimum identity data needed for a grant. Public-key fingerprints or verified account identities may be preferable where legal names need not be public.
