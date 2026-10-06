**Platform:** PortSwigger Web Security Academy

**Category:** JWT / Authentication

**Difficulty:** Practitioner

**Date Solved:** 2026-10-07

**Severity:** Critical

## Summary

The application verifies JWT signatures using a public key embedded directly in the token's own header via the `jwk` (JSON Web Key) parameter, rather than exclusively using a key the server already trusts. This allows an attacker to generate their own RSA key pair, sign a forged token with their own private key, and embed the matching public key in the token header — the server verifies the attacker's signature against the attacker's own supplied key, which trivially succeeds, bypassing authentication entirely.

## Affected Component

`GET /admin` — administrative panel, gated by JWT-based session authentication. Underlying flaw affects the entire session verification mechanism.

## Steps to Reproduce

1. Log in as a low-privilege user (`wiener:peter`), capture the resulting JWT session cookie.
2. Send the authenticated request to Burp Repeater; confirm `GET /admin` returns 401 Unauthorized for this session.
3. In Burp's JWT Editor extension (Keys tab), generate a new RSA key pair (2048-bit). Key ID used: `73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15`.
4. In Repeater's JSON Web Token panel, edit the payload: change `sub` from `wiener` to `administrator`.
5. Click **Attack** → select **Embedded JWK**, choosing the newly generated RSA key as the signing key.
6. Burp automatically: embeds the public half of the generated key into the token header's `jwk` field, signs the token using the corresponding private key, and produces the complete forged JWT.
7. Change the request path to `/admin`, send.
8. Response: `200 OK` — admin panel content returned.
9. Located `/admin/delete?username=carlos` in the admin panel response; sent the request to confirm full exploitability. User successfully deleted, lab solved.

## Proof of Concept

Forged token header (post-attack):

```json
{
  "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
    "n": "<attacker-generated public modulus>"
  }
}
```

Payload: `{"iss": "portswigger", "sub": "administrator", "exp": <timestamp>}`

Token signed with attacker-generated private key corresponding to the embedded public key. Server accepted the token as valid, granting admin access.

## Root Cause

The server's JWT verification logic trusts a public key supplied inside the token's own `jwk` header field, instead of restricting verification to a fixed set of keys the server itself issued/controls (e.g., via a pinned JWKS endpoint or hardcoded key). Since the attacker controls both the signing key (private) and the verification key (public, self-embedded), the signature check is rendered meaningless — the attacker is effectively asking the server "please trust this key I just made up," and the server complies.

## Impact

### Technical

Complete authentication bypass with no dependency on cracking, guessing, or leaking any server-side secret. The attack is self-contained: generate a key pair, sign, embed, send. No prior knowledge of the server's real signing material is required at all.

### Business / Real-World

Full account takeover of any user, including administrators, achievable by any party capable of reaching the login flow once (to obtain a baseline token structure) — no credential guessing of the target account needed. This is among the most severe JWT misconfigurations, as it requires zero information about the server's actual cryptographic material.

### Scope

Every endpoint protected by this JWT verification mechanism is affected, not solely `/admin`.

## Remediation

- Never derive the verification key from attacker-controllable token fields (`jwk`, `jku`, `x5u`, `x5c`). The server should verify exclusively against a fixed, pre-registered set of trusted keys.
- If supporting external key rotation, validate that any referenced key originates from a trusted, pinned source (e.g., an allow-listed JWKS URL under the application's own control) — never trust a key embedded directly in the token being verified.
- Explicitly whitelist accepted algorithms and reject any token attempting to introduce unexpected header parameters that influence verification behavior.

## Lessons Learned & Patterns

- General pattern: "server trusts attacker-supplied data as if it were trusted infrastructure" — same root shape as the `X-Custom-IP-Authorization` header trust bypass (earlier lab) and the `kid` path-injection variant of this same vulnerability class. Worth testing for this pattern broadly, not just in JWT contexts.
- `jwk` (key embedded in header) and `jku`/`x5u` (URL pointing to a key) are both attacker-reachable fields when verification logic isn't locked down — all three deserve testing on any RS256-based JWT implementation.
- This attack requires no cracking/brute-forcing at all, unlike the weak-secret lab — it's purely a logic flaw in what the server chooses to trust, making it in some ways a "cleaner" bypass to demonstrate and explain to a non-technical stakeholder (no wordlists, no crypto math to justify).

## References

- PortSwigger Lab: JWT authentication bypass via jwk header injection — https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection
- PortSwigger JWT Attacks Learning Material — https://portswigger.net/web-security/jwt
- RFC 7517 (JSON Web Key spec) — https://www.rfc-editor.org/rfc/rfc7517
- OWASP JWT Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

**Tags:** #PortSwigger #JWT #AuthenticationBypass #KeyInjection #RS256

# JWT Authentication Bypass via jwk Header Injection

**Platform:** PortSwigger Web Security Academy
**Category:** JWT / Authentication
**Difficulty:** Practitioner
**Date Solved:** 2026-10-07
**Severity:** Critical

## Summary

The application verifies JWT signatures using a public key embedded directly in the token's own header via the `jwk` (JSON Web Key) parameter, rather than exclusively using a key the server already trusts. This allows an attacker to generate their own RSA key pair, sign a forged token with their own private key, and embed the matching public key in the token header — the server verifies the attacker's signature against the attacker's own supplied key, which trivially succeeds, bypassing authentication entirely.

## Affected Component

`GET /admin` — administrative panel, gated by JWT-based session authentication. Underlying flaw affects the entire session verification mechanism.

## Steps to Reproduce

1. Log in as a low-privilege user (`wiener:peter`), capture the resulting JWT session cookie.
2. Send the authenticated request to Burp Repeater; confirm `GET /admin` returns 401 Unauthorized for this session.
3. In Burp's JWT Editor extension (Keys tab), generate a new RSA key pair (2048-bit). Key ID used: `73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15`.
4. In Repeater's JSON Web Token panel, edit the payload: change `sub` from `wiener` to `administrator`.
5. Click **Attack** → select **Embedded JWK**, choosing the newly generated RSA key as the signing key.
6. Burp automatically: embeds the public half of the generated key into the token header's `jwk` field, signs the token using the corresponding private key, and produces the complete forged JWT.
7. Change the request path to `/admin`, send.
8. Response: `200 OK` — admin panel content returned.
9. Located `/admin/delete?username=carlos` in the admin panel response; sent the request to confirm full exploitability. User successfully deleted, lab solved.

## Proof of Concept

Forged token header (post-attack):

```json
{
  "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
    "n": "<attacker-generated public modulus>"
  }
}
```

Payload: `{"iss": "portswigger", "sub": "administrator", "exp": <timestamp>}`

Token signed with attacker-generated private key corresponding to the embedded public key. Server accepted the token as valid, granting admin access.

## Root Cause

The server's JWT verification logic trusts a public key supplied inside the token's own `jwk` header field, instead of restricting verification to a fixed set of keys the server itself issued/controls (e.g., via a pinned JWKS endpoint or hardcoded key). Since the attacker controls both the signing key (private) and the verification key (public, self-embedded), the signature check is rendered meaningless — the attacker is effectively asking the server "please trust this key I just made up," and the server complies.

## Impact

### Technical

Complete authentication bypass with no dependency on cracking, guessing, or leaking any server-side secret. The attack is self-contained: generate a key pair, sign, embed, send. No prior knowledge of the server's real signing material is required at all.

### Business / Real-World

Full account takeover of any user, including administrators, achievable by any party capable of reaching the login flow once (to obtain a baseline token structure) — no credential guessing of the target account needed. This is among the most severe JWT misconfigurations, as it requires zero information about the server's actual cryptographic material.

### Scope

Every endpoint protected by this JWT verification mechanism is affected, not solely `/admin`.

## Remediation

- Never derive the verification key from attacker-controllable token fields (`jwk`, `jku`, `x5u`, `x5c`). The server should verify exclusively against a fixed, pre-registered set of trusted keys.
- If supporting external key rotation, validate that any referenced key originates from a trusted, pinned source (e.g., an allow-listed JWKS URL under the application's own control) — never trust a key embedded directly in the token being verified.
- Explicitly whitelist accepted algorithms and reject any token attempting to introduce unexpected header parameters that influence verification behavior.

## Lessons Learned & Patterns

- General pattern: "server trusts attacker-supplied data as if it were trusted infrastructure" — same root shape as the `X-Custom-IP-Authorization` header trust bypass (earlier lab) and the `kid` path-injection variant of this same vulnerability class. Worth testing for this pattern broadly, not just in JWT contexts.
- `jwk` (key embedded in header) and `jku`/`x5u` (URL pointing to a key) are both attacker-reachable fields when verification logic isn't locked down — all three deserve testing on any RS256-based JWT implementation.
- This attack requires no cracking/brute-forcing at all, unlike the weak-secret lab — it's purely a logic flaw in what the server chooses to trust, making it in some ways a "cleaner" bypass to demonstrate and explain to a non-technical stakeholder (no wordlists, no crypto math to justify).

## References

- PortSwigger Lab: JWT authentication bypass via jwk header injection — https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection
- PortSwigger JWT Attacks Learning Material — https://portswigger.net/web-security/jwt
- RFC 7517 (JSON Web Key spec) — https://www.rfc-editor.org/rfc/rfc7517
- OWASP JWT Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

**Tags:** #PortSwigger #JWT #AuthenticationBypass #KeyInjection #RS256

# JWT Authentication Bypass via jwk Header Injection

**Platform:** PortSwigger Web Security Academy
**Category:** JWT / Authentication
**Difficulty:** Practitioner
**Date Solved:** 2026-10-07
**Severity:** Critical

## Summary
The application verifies JWT signatures using a public key embedded directly in the token's own header via the `jwk` (JSON Web Key) parameter, rather than exclusively using a key the server already trusts. This allows an attacker to generate their own RSA key pair, sign a forged token with their own private key, and embed the matching public key in the token header — the server verifies the attacker's signature against the attacker's own supplied key, which trivially succeeds, bypassing authentication entirely.

## Affected Component
`GET /admin` — administrative panel, gated by JWT-based session authentication. Underlying flaw affects the entire session verification mechanism.

## Steps to Reproduce

1. Log in as a low-privilege user (`wiener:peter`), capture the resulting JWT session cookie.
2. Send the authenticated request to Burp Repeater; confirm `GET /admin` returns 401 Unauthorized for this session.
3. In Burp's JWT Editor extension (Keys tab), generate a new RSA key pair (2048-bit). Key ID used: `73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15`.
4. In Repeater's JSON Web Token panel, edit the payload: change `sub` from `wiener` to `administrator`.
5. Click **Attack** → select **Embedded JWK**, choosing the newly generated RSA key as the signing key.
6. Burp automatically: embeds the public half of the generated key into the token header's `jwk` field, signs the token using the corresponding private key, and produces the complete forged JWT.
7. Change the request path to `/admin`, send.
8. Response: `200 OK` — admin panel content returned.
9. Located `/admin/delete?username=carlos` in the admin panel response; sent the request to confirm full exploitability. User successfully deleted, lab solved.

## Proof of Concept
Forged token header (post-attack):

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/27d4e409-c965-4426-bc40-bfcad9e1b90e" />

```json
{
  "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "e": "AQAB",
    "kid": "73e4bfa3-76a0-4b8a-a2c9-e16e05b08f15",
    "n": "<attacker-generated public modulus>"
  }
}
```
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/ae6c9622-9dbe-4f98-bcf3-60d7e3aaed22" />

Payload: `{"iss": "portswigger", "sub": "administrator", "exp": <timestamp>}`
Token signed with attacker-generated private key corresponding to the embedded public key. Server accepted the token as valid, granting admin access.

## Root Cause
The server's JWT verification logic trusts a public key supplied inside the token's own `jwk` header field, instead of restricting verification to a fixed set of keys the server itself issued/controls (e.g., via a pinned JWKS endpoint or hardcoded key). Since the attacker controls both the signing key (private) and the verification key (public, self-embedded), the signature check is rendered meaningless — the attacker is effectively asking the server "please trust this key I just made up," and the server complies.

## Impact

### Technical
Complete authentication bypass with no dependency on cracking, guessing, or leaking any server-side secret. The attack is self-contained: generate a key pair, sign, embed, send. No prior knowledge of the server's real signing material is required at all.

### Business / Real-World
Full account takeover of any user, including administrators, achievable by any party capable of reaching the login flow once (to obtain a baseline token structure) — no credential guessing of the target account needed. This is among the most severe JWT misconfigurations, as it requires zero information about the server's actual cryptographic material.

### Scope
Every endpoint protected by this JWT verification mechanism is affected, not solely `/admin`.

## Remediation
- Never derive the verification key from attacker-controllable token fields (`jwk`, `jku`, `x5u`, `x5c`). The server should verify exclusively against a fixed, pre-registered set of trusted keys.
- If supporting external key rotation, validate that any referenced key originates from a trusted, pinned source (e.g., an allow-listed JWKS URL under the application's own control) — never trust a key embedded directly in the token being verified.
- Explicitly whitelist accepted algorithms and reject any token attempting to introduce unexpected header parameters that influence verification behavior.

## Lessons Learned & Patterns
- General pattern: "server trusts attacker-supplied data as if it were trusted infrastructure" — same root shape as the `X-Custom-IP-Authorization` header trust bypass (earlier lab) and the `kid` path-injection variant of this same vulnerability class. Worth testing for this pattern broadly, not just in JWT contexts.
- `jwk` (key embedded in header) and `jku`/`x5u` (URL pointing to a key) are both attacker-reachable fields when verification logic isn't locked down — all three deserve testing on any RS256-based JWT implementation.
- This attack requires no cracking/brute-forcing at all, unlike the weak-secret lab — it's purely a logic flaw in what the server chooses to trust, making it in some ways a "cleaner" bypass to demonstrate and explain to a non-technical stakeholder (no wordlists, no crypto math to justify).

## References

- PortSwigger Lab: JWT authentication bypass via jwk header injection — https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection
- PortSwigger JWT Attacks Learning Material — https://portswigger.net/web-security/jwt
- RFC 7517 (JSON Web Key spec) — https://www.rfc-editor.org/rfc/rfc7517
- OWASP JWT Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

**Tags:** #PortSwigger #JWT #AuthenticationBypass #KeyInjection #RS256
