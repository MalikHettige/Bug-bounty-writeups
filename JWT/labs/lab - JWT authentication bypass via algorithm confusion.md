# JWT authentication bypass via algorithm confusion

**Platform:** PortSwigger Web Security Academy
**Category:** Authentication / JWT
**Difficulty:** Practitioner
**Date Solved:** 2026-10-12
**Severity:** Critical

## Summary

The application issues JWTs signed with RS256 and publishes its RSA public key at a `/jwks.json` endpoint. The token verification logic trusts the `alg` header to determine how to validate the signature, rather than enforcing a fixed algorithm per key. By fetching the public key and reusing its exact byte representation as an HMAC secret, I forged a token signed with HS256 that the server verified as valid — allowing full authentication bypass to any arbitrary user, including `administrator`.

## Affected Component

JWT verification middleware on session-protected endpoints (`/admin` and other authenticated routes). Key disclosure endpoint: `/jwks.json`.

## Steps to Reproduce

1. Log in with the lab's low-privilege credentials and capture a valid session JWT via Burp Proxy.
2. Fetch the server's public key set: `GET /jwks.json`. Response contains a JWK object with `kty: RSA`, `e`, `n`, and a `kid`.
3. Import that JWK into Burp's JWT Editor as a new RSA key (JWK format, pasted directly from the response to avoid transcription errors).
4. Export the imported key as PEM, then convert it into the byte format usable as an HMAC secret (base64-encoded PEM).
5. Create a new Symmetric Key in JWT Editor using those bytes as the `k` value.
6. On the captured token: change the header `alg` to `HS256` (leave `kid` unmodified — this server does not key off it), change the payload `sub` claim to `administrator`.
7. Sign the modified token using the symmetric key, with "Don't modify header" selected.
8. Replace the session cookie with the forged token and send a request to `/admin`.
9. Server returned `200 OK` and rendered the admin panel.
10. Used the `/admin/delete?username=carlos` link exposed in the admin panel response to confirm full administrative action capability.

## Proof of Concept

```bash
Original token header:
{"kid": "<server-key-id>", "alg": "RS256"}

Forged token header:
{"kid": "<server-key-id>", "alg": "HS256"}

Forged token payload:
{"iss": "portswigger", "exp": <future-timestamp>, "sub": "administrator"}

Signature: HMAC-SHA256 computed using the server's own RSA public key
(PEM-encoded bytes) as the shared secret.
```

Request:
```
GET /admin HTTP/2
Host: <lab-id>.web-security-academy.net
Cookie: session=<forged-token>
```

Response: `200 OK`, admin panel content returned, including the `delete carlos` action link.

## Root Cause

The server's JWT verification logic branches on the `alg` value present in the attacker-controlled token header, rather than enforcing a single expected algorithm tied to each key. RS256 and HS256 use the same `verify(key, data, signature)` interface in many JWT libraries, but treat the key completely differently: RS256 expects an asymmetric public key used only to *verify*, while HS256 expects a symmetric secret used for both *signing and verifying*. Because the server's RSA public key is, by design, publicly disclosed (that's the point of asymmetric crypto), reusing those same bytes as an HS256 secret lets an attacker both sign and verify tokens — fully defeating the signature's purpose as a trust boundary.

## Impact

### Technical
Complete authentication bypass. Any party with access to the public key endpoint (which is intentionally public) can forge a validly-signed token for any user identity, including privileged accounts, without ever possessing the server's actual private key or any legitimate credentials beyond initial unauthenticated access to `/jwks.json`.

### Business / Real-World
On a real target, this results in full account takeover for any user — most critically, administrative or support-tier accounts, since the attacker chooses the forged identity. Depending on what the `sub`/role claims gate, this can extend to full administrative panel access, data exfiltration across all tenants, or destructive actions (user deletion, privilege changes, financial actions) performed under a forged identity with no corresponding legitimate audit trail.

### Scope
Any endpoint relying on this JWT verification logic for authentication/authorization is affected — in this lab, confirmed on `/admin` and its sub-actions; in a real target, likely every authenticated route sharing the same verification middleware.

## Remediation

- Enforce a single, fixed expected algorithm per key at verification time — never trust the `alg` value from the token itself to select verification behavior. Most modern JWT libraries support explicitly pinning `algorithms: ["RS256"]` in the verify call rather than accepting whatever the token claims.
- Never reuse the same key material across algorithm types. If both symmetric and asymmetric flows are genuinely needed, use entirely separate, unrelated keys for each.
- Consider rejecting tokens whose `alg` doesn't match the `alg` declared/expected for that specific `kid`, independent of global library configuration.

## Lessons Learned & Patterns

- This is the same root cause as `kid` header path traversal and `jwk` header injection: a server trusting attacker-influenced input to determine *which* key or *what kind* of key is used in verification. On an unfamiliar target, the generalizable question is "does anything here let me influence what key material gets used to verify a signature, in any form" — not just "does this app do algorithm confusion specifically."
- The exploitation itself (forge header, forge payload, sign) is simple once the key is in hand. The actual difficulty was entirely in correctly converting the public key into the exact byte representation the server's internal verification code expects as an HMAC secret (PEM line-endings, base64 vs. base64url encoding) — this is inherently trial-and-error since the server's internal key-handling code isn't observable. Scripting the JWKS → symmetric-key conversion removed this as a repeated manual failure point and should be reused for future instances of this bug class.
- Don't assume the privileged identity to forge is always `administrator` — that's specific to this lab's seeded data. On a real target, decode a legitimate low-privilege token first to learn the actual claim structure (role field name, ID conventions) before guessing at a privileged value.
- Always check for and strip/preserve `kid` deliberately rather than by default — whether it matters depends on whether the server's key lookup is keyed off it, which varies by implementation.

## References

- PortSwigger Lab: JWT authentication bypass via algorithm confusion
- https://portswigger.net/web-security/jwt/algorithm-confusion

**Tags:** #PortSwigger #JWT #Authentication #AlgorithmConfusion #KeyConfusion
