# Formalization checklist

There is no universal authority that "registers" a software license and makes it legally valid. Copyright generally arises automatically; the operational goal is to make ownership, text, version, provenance, acceptance paths, and enforcement evidence unusually clear.

## Before declaring 1.0 final

1. Freeze the intended business model and legal semantics.
2. Have a software/IP lawyer review the text for the jurisdictions that materially matter to the steward and expected licensees.
3. Perform trademark/name clearance for the Kiyoshima license-family names in relevant registries before claiming registration.
4. Resolve contributor ownership: use Kiyoshima Contributor 1.0 (or another reviewed CLA) before accepting material third-party contributions when future relicensing is important.
5. Decide the stable public identity of the license steward and a durable contact route.

## Canonical release

6. Publish the canonical repository publicly.
7. Keep `LICENSE` and `LICENSES/LicenseRef-Kiyoshima-Source-1.0.txt` byte-identical.
8. Run the integrity validator and commit the release hash to `registry/releases.json`.
9. Create a signed Git tag for the legal version and a GitHub Release containing an archive of the framework.
10. Use GitHub artifact attestation for the release archive so consumers can verify provenance.
11. Archive the release through Software Heritage and, if useful, connect the repository to Zenodo to obtain a citable archived release/DOI.
12. Never alter the released 1.0 legal text in place. Publish 1.0.1/1.1/2.0 as a new legal version if the text changes.

## Ecosystem formalization

13. Use `LicenseRef-Kiyoshima-Source-1.0` immediately in SPDX-compatible metadata.
14. Follow REUSE conventions for project-level licensing metadata where practical.
15. After the license is stable and has meaningful real-world use, consider submitting it to the SPDX License List. Inclusion is case-by-case and should not be assumed.
16. Do not seek OSI approval for the current Source profile: organizational/commercial restrictions intentionally conflict with the Open Source Definition.
17. Maintain an adopter registry and public change log so third parties can verify the canonical text and stewardship history.

## Enforcement readiness

18. Maintain project copyright notices, signed releases, and source history.
19. For commercially important projects, register copyright in jurisdictions where voluntary registration materially improves remedies or litigation posture.
20. Keep every commercial agreement and special grant with a unique identifier and authenticated copy; never rely on an informal chat alone for high-value rights.
21. Record only the minimum identity data needed for a grant. Prefer public-key fingerprints or account identities when legal names need not be public.
