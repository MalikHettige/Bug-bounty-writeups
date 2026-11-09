**Platform:** PortSwigger Web Security Academy

**Category:** JWT / Authentication

**Difficulty:** Practitioner

**Date Solved:** 2026-10-08

**Severity:** Critical

## Summary
The application uses RS256 JWT verification but fails to enforce the expected algorithm on incoming tokens. By switching `alg` to `HS256` and signing a forged token using the server's own public key as the HMAC secret — which is publicly available at `/jwks.json` — an attacker can produce a signature the server accepts as valid, bypassing authentication entirely.

## Affected Component
JWT verification middleware. All authenticated endpoints affected.

## Steps to Reproduce
1. Log in as `wiener`, capture the JWT session cookie.
2. Fetch the server's public key from `/jwks.json`.
3. In Burp JWT Editor, import the JWK as a new RSA key.
4. Copy the public key as PEM → base64-encode it in Decoder.
5. Create a new Symmetric Key in JWT Editor with `k` = that base64 value.
6. In Repeater, change token header `alg` to `HS256`.
7. Change payload `sub` to `administrator`.
8. Sign with the symmetric key, "Don't modify header" checked.
9. Send — admin access granted.

## Root Cause
The JWT library accepts algorithm values from the token itself without validating against an expected algorithm allowlist. When `alg` is switched from RS256 to HS256, the library uses the loaded public key as the HMAC secret, which the attacker already has access to since it is publicly exposed at `/jwks.json`.

## Impact
Complete authentication bypass. Full account takeover of any user including administrators. All protected functionality and data is exposed.

## Remediation
- Hardcode the expected algorithm server-side — never read `alg` from the token itself.
- Use a JWT library that enforces algorithm allowlisting by default.
- Separate asymmetric and symmetric keys entirely — never allow the same key material to be used for both modes.
- Remove or restrict access to public key endpoints if not required by clients.

## Chain Potential
Standalone: High (auth bypass to any account).Chained:
- Algorithm confusion → admin access → delete users = Critical
- Algorithm confusion → BOLA on other users' financial data = Critical
- Algorithm confusion → mass account takeover via scripted token generation = Critical + platform-wide impact multiplier

## Lessons Learned
- `alg` in JWT header is attacker-controlled. Never trust it server-side.
- RS256 + public key exposed at `/jwks.json` = always test algorithm confusion. The public key being public is the whole attack surface.
- The symmetric key `k` value must be the base64-encoded PEM of the server's public key — not the JWK, not raw bytes, specifically the PEM format base64-encoded.

## References
- PortSwigger Lab: JWT authentication bypass via algorithm confusion
- RFC 7519 — JSON Web Token

**Tags:** #JWT #AlgorithmConfusion #RS256 #HS256 #AuthenticationBypass
