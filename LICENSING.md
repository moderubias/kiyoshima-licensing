# Repository licensing map

This repository contains distinct legal and protocol layers.

1. Framework code, schemas, documentation, templates, workflows, and tooling are
   Apache-2.0 unless a file says otherwise. The root `LICENSE` contains
   Apache-2.0.
2. `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` is the canonical Kiyoshima Source 1.0
   candidate instrument. It is not the repository's default license.
3. **Kiyoshima Open** is not another legal license. It is a Passport/profile
   configuration that keeps the project's actual standard SPDX license
   (`MIT`, `Apache-2.0`, etc.) controlling.

The Apache-2.0 grant for this framework does not relicense projects that adopt
Kiyoshima Source. Conversely, adopting Kiyoshima Source does not require a
commercial agreement merely to use this repository's Apache-licensed tooling.

Current Kiyoshima Source 1.0 candidate digest:

`sha256:c3c5a834df1b0ef65b076aa4c8a233be1a17005016f60f6978a44ce0a17a6c85`

See `REUSE.toml` and `LICENSES/` for this framework repository's file licensing.
Generated projects use a lean layout by default: single standard licenses live in
root `LICENSE`; compound expressions such as `MIT OR Apache-2.0` place their full
component texts under project `LICENSES/`. REUSE metadata is opt-in for generated
projects.
