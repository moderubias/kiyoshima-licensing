# Machine-readable layer

The machine layer is intentionally subordinate to legal instruments.

Principles:

1. Legal text controls.
2. Metadata may summarize restrictions and permission paths but may not silently expand rights.
3. Missing, unknown, malformed, conflicting, or unauthenticated values never imply permission.
4. Additional rights require a separately authenticated grant/agreement.
5. Agents inherit the authorization boundary of their principal.
6. Rights reservations are explicit, including model-improvement and non-research TDM reservations to the extent recognized by applicable law.
7. Permission-request routes should be discoverable so an automated system can stop safely and tell the operator how to obtain rights.

`KIYOSHIMA.json` is the **Kiyoshima License Passport**. Schema 1.2 is intended for humans, CI systems, IDEs, package tooling, policy engines, and AI agents to inspect before acting.

The framework also includes a W3C TDM Reservation Protocol mapping example in `machine/tdm/` for operators who publish Covered Software through an HTTP origin they control.

Schema 1.2 adds `protocol` and `policy_constraints` so an integration can identify the protocol version and display important normalized conditions without trying to parse legal prose. Use `klicense preflight` for a conservative action-level decision surface.
