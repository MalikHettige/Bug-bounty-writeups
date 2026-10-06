# JWT Authentication Bypass via Flawed Signature Verification

**Platform:** PortSwigger Web Security Academy
**Category:** Authentication / API Security - JWT
**Difficulty:** Practitioner
**Date Solved:** 2026-10-06
**Severity:** Critical

## Summary
The application issues JWT-based session cookies signed with RS256. The server accepts the `alg` field declared in an incoming token's header and dynamically selects its verification behavior based on that client-controlled value, instead of enforcing one fixed algorithm. Declaring `alg: none` — a value the JWT spec reserves to mean "unsigned token" — causes the server to skip signature verification entirely, allowing an attacker to forge arbitrary session claims.

## Affected Component
Session authentication middleware handling JWT cookie verification; admin panel at `/admin`.

## Steps to Reproduce
1. Log in as a low-privilege user (`wiener:peter`) and capture the resulting JWT session cookie.
2. Decode the token; confirm structure `header.payload.signature` with `alg: RS256`.
3. Send `GET /admin` with the valid wiener token — confirm 401, access restricted to `administrator`.
4. Edit the token's header: change `alg` from `RS256` to `none`.
5. Edit the payload: change `sub` from `wiener` to `administrator`.
6. Strip the signature segment entirely, retaining the trailing dot (`header.payload.`).
7. Send `GET /admin` with the modified token.

## Proof of Concept
Modified token structure sent: 
```
eyJraWQiOi...bmUifQ.eyJpc3MiOi...pbiJ9.
```
(header declares `alg: none`; payload declares `sub: administrator`; signature segment empty)
Result: `200 OK`, admin panel content returned. Located and sent `GET /admin/delete?username=carlos` to confirm full exploitability — user successfully deleted.

## Root Cause
The server's JWT verification logic trusts the `alg` value supplied in the attacker-controlled token header to determine which verification routine to execute. When `alg` is set to `none`, the library correctly follows the JWT spec's definition of that value ("no signature expected") and skips verification — but the application never restricts which algorithms it will accept in the first place. An attacker can unilaterally downgrade the token's trust model to "no verification required."

## Impact

### Technical
Complete authentication bypass. Any authenticated user (or anyone capable of obtaining a structurally valid token) can forge arbitrary session claims, including privilege/role fields, without needing any cryptographic key material.

### Business / Real-World
Full account takeover of any user, including administrators, with no credential knowledge required beyond a single low-privilege login. In a production system this enables data exfiltration, unauthorized administrative actions, and full compromise of the access-control model.

### Scope
Any endpoint gated by this JWT-based session mechanism is affected — not limited to `/admin`.

## Remediation
- Enforce a single, fixed, server-defined algorithm for JWT verification; reject any token whose `alg` does not exactly match the expected value, including `none`.
- Do not allow the token itself to influence verification logic — the server should decide the algorithm, not the client.
- Use a well-maintained JWT library configured to explicitly whitelist accepted algorithms rather than trusting the header.

## Lessons Learned & Patterns
- `alg: none` is a spec-legal value meaning "unsigned" — exists for niche internal use cases but is dangerous if a verification library honors it blindly on untrusted input.
- Distinct from "unverified signature" (verification code missing entirely) — here verification code runs, but its behavior is client-steerable via the `alg` field.
- General pattern: never let attacker-supplied metadata (header fields, declared types, declared algorithms) control which validation logic a server runs. Metadata should inform; validation logic should be fixed.
- Always test `alg` manipulation as a default check against any JWT-based session mechanism, not just when prompted.

## References
- PortSwigger Lab
- OWASP: JWT Security Cheat Sheet

**Tags:** #PortSwigger #JWT #AuthenticationBypass #AlgorithmConfusion
