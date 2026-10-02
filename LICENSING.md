# Repository licensing map

This repository contains **two distinct licensing layers**.

1. **Framework code, schemas, documentation, templates, workflows, and tooling** are licensed under Apache License 2.0 unless a file says otherwise. The repository root `LICENSE` contains Apache-2.0.
2. **Kiyoshima Source License 1.0** is the legal instrument defined in `LICENSE-KIYOSHIMA-SOURCE-1.0.txt`. Section 22 of that text authorizes anyone to reproduce and apply an exact, unmodified copy to software they have authority to license.

The Apache-2.0 grant for this repository does **not** relicense software that another project places under Kiyoshima Source 1.0. Conversely, adopting Kiyoshima Source 1.0 does not require a commercial agreement merely to use this repository's Apache-licensed tooling to inspect, validate, or integrate the protocol.

Canonical candidate digest for Kiyoshima Source 1.0:

`sha256:c3c5a834df1b0ef65b076aa4c8a233be1a17005016f60f6978a44ce0a17a6c85`

See `REUSE.toml` and `LICENSES/` for machine-readable file licensing.

The root `REUSE.toml` uses `override` deliberately because every REUSE-covered framework file is Apache-2.0 and several documentation/template files contain literal SPDX examples that must not be misread as the framework file's own license. The canonical `LICENSE-KIYOSHIMA-SOURCE-1.0.txt` is a root `LICENSE-*` legal file and is ignored by REUSE 3.3 as a Covered File. Consumer-project `REUSE.toml` uses `closest` instead so explicit third-party file licensing can take precedence.
