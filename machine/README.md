# Machine-readable layer

The machine layer is intentionally subordinate to the legal layer.

Principles:

1. Legal text controls.
2. Metadata may summarize but may not silently expand rights.
3. Missing or unknown values never imply permission.
4. Conflicts resolve conservatively: deny, stop, or request authenticated permission.
5. Additional rights require a separately authenticated grant.
6. Agents inherit the authorization boundary of their principal.

`KIYOSHIMA.json` is called a **Kiyoshima License Passport**. It is designed to be easy for humans, CI systems, package tooling, and AI agents to inspect before acting.
