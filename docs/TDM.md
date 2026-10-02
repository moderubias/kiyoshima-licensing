# Text and data mining reservation

Kiyoshima Source 1.0 expressly reserves text-and-data-mining rights for uses not already permitted by the license or mandatory law, to the extent applicable law allows a rightsholder to reserve those rights.

The License Passport mirrors this under `rights_reservations`.

## W3C TDM Reservation Protocol mapping

For websites or package documentation served from an HTTP origin you control, you may additionally implement the W3C Community Group TDM Reservation Protocol (TDMRep). A reservation is expressed as `tdm-reservation: 1`, optionally with a `tdm-policy` URL describing how permission can be acquired.

This repository includes `machine/tdm/tdmrep.example.json` for the origin-wide `/.well-known/tdmrep.json` mechanism and `machine/tdm/policy.example.jsonld` for a machine-readable TDMRep/ODRL policy using the required `http://www.w3.org/ns/tdmrep.jsonld` context. Replace all example URIs and identity/contact values before publishing them. `klicense export-tdm` can generate both deployable files from explicit origin/rightsholder/contact inputs.

Do not claim that merely committing the example file to GitHub configures GitHub's HTTP headers. TDMRep deployment must occur on an origin whose HTTP/HTML/TDM-file metadata you control.


A minimal deployment on a controlled origin is therefore conceptually:

```text
/.well-known/tdmrep.json
    tdm-reservation = 1
    tdm-policy      = https://your-origin.example/policies/kiyoshima-tdm.jsonld
```

TDMRep is a W3C Community Group report, not a W3C Recommendation. Treat it as an interoperability signal layered on top of the controlling license and applicable law.
