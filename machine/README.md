# Machine-readable layer

The machine layer is subordinate to legal instruments.

Principles:

1. Legal text controls.
2. Metadata may summarize rights, restrictions, and permission paths but may not
   silently expand rights.
3. Missing, unknown, malformed, conflicting, or unauthenticated values never
   imply permission.
4. Additional rights require a separately authenticated grant/agreement.
5. Agents inherit the authorization boundary of their principal.
6. Rights reservations are explicit where the controlling profile has them.
7. Standard Open Source profiles are represented without relabeling their legal
   licenses.

`KIYOSHIMA.json` is the **Kiyoshima License Passport**. Schema 1.3 is intended
for humans, CI systems, IDEs, package tooling, policy engines, and AI agents.
It supports a generic controlling license file plus optional hashed supporting
license files.

Use `klicense preflight` for a conservative action-level decision surface. For
Open profiles, AI actions are deliberately conditional: the framework adds no
AI-specific restriction, but the standard license and applicable law remain
controlling.
