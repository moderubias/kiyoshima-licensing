# Agreement instruments

These files expand rights beyond the public license and should be treated as controlled legal instruments.

- `Kiyoshima-Commercial-Agreement.template.md` — organizational/commercial rights.
- `Kiyoshima-Rights-Grant.template.md` — targeted rights for a trusted person or entity.
- `Kiyoshima-AI-Use-Addendum-1.0.template.md` — model-training/dataset/model-improvement rights.
- `Kiyoshima-Contributor-Agreement-1.0.md` — contributor copyright and patent grant.

## Authentication rule

For high-value rights:

1. assign a unique ID;
2. finalize the exact instrument bytes;
3. compute a SHA-256 digest **after** finalization;
4. store that digest in a detached `.sha256` file, registry record, signature envelope, attestation, or trusted platform record;
5. authenticate the final bytes with a signature or attributable platform workflow.

Do not insert a document's own digest into the bytes whose digest is being computed. That creates a self-referential value and is not the verification model used here.

Private agreements/grants should remain private unless both the issuer and recipient intend public disclosure. A public registry may contain only a detached digest and minimal public metadata.
