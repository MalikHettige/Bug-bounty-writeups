# JWT Authentication Bypass via Algorithm Confusion (No Exposed Key)

**Platform:** PortSwigger Web Security Academy

**Category:** Authentication

**Difficulty:** Expert

**Date Solved:** 2026-10-13

**Severity:** Critical

## Summary

The application issues session JWTs signed with RS256, using an RSA key pair that is never exposed through a `/jwks.json`, `/.well-known/jwks.json`, or any other discoverable endpoint. Because the server accepts both RS256 and HS256 on incoming tokens without binding the token to the algorithm it was actually issued with, it is possible to derive a candidate RSA public key offline — without ever fetching one from the server — by collecting two tokens signed with the same private key and running them through PortSwigger's `sig2n` tool. The recovered public key can then be reused as the HMAC secret for an HS256-signed, self-forged token, allowing full authentication bypass to `administrator`.

## Affected Component

Session management / JWT verification logic — specifically the token validation endpoint that accepts the `session` cookie on every authenticated request (including `/admin`).

## Steps to Reproduce

1. Log into the application twice using valid credentials, generating two separate, validly-signed RS256 session tokens (`token1`, `token2`). Both are signed by the same server-side RSA private key.
2. Capture both tokens via Burp Suite (Proxy → HTTP history), one per login session.
3. Since no JWKS endpoint is exposed, run PortSwigger's `sig2n` tool against the two captured tokens to mathematically recover candidate RSA moduli:
   ```
   docker run --rm -it portswigger/sig2n <token1> <token2>
   ```
4. The tool outputs multiple candidate moduli (one per integer multiplier tried), each paired with:
   - A base64-encoded X.509 (SubjectPublicKeyInfo) key
   - A base64-encoded PKCS1 key
   - A pre-tampered JWT for each candidate, already re-signed with that candidate key treated as an HS256 secret
5. For each candidate in turn, replace the application's session cookie with the corresponding tampered JWT and send a `GET /admin` request.
6. Monitor responses for a `200 OK` — this confirms which candidate modulus/key actually matches the server's real public key.
7. Once a `200 OK` is confirmed, take that candidate's base64-encoded X.509/PKCS1 key value and use it as the symmetric (HS256) signing secret in Burp's JWT Editor.
8. Edit the token's claims — set `sub` to `administrator` — and the header's `alg` to `HS256`.
9. Sign the token using the confirmed key as the symmetric secret, and send the request to `/admin`.
10. With `administrator` access confirmed, solve the lab by deleting user `carlos`.

## Proof of Concept

**sig2n output against the two captured tokens**, showing multiple recovered candidate keys and their corresponding pre-tampered JWTs:
<img width="1919" height="849" alt="image" src="https://github.com/user-attachments/assets/ffa885a1-b732-46b5-8e57-7f8f80b05b90" />

Each `Found n with multiplier N` block includes a usable base64 X.509 key, a base64 PKCS1 key, and a ready-to-send tampered JWT — the candidates are tried against `/admin` in sequence until one returns `200 OK`, confirming the correct recovered key.

**Docker environment used to run the `sig2n` container:**
![Uploading image.png…]()

After identifying the correct candidate from the responses above, that key was reused as the HS256 signing secret to forge a token with `"sub": "administrator"`, which was sent to `/admin` and returned a 200 response, confirming privilege escalation. The lab was solved by deleting `carlos` from the resulting admin panel.

## Root Cause

The server fails to bind a JWT's signature algorithm to the key type it was actually issued under. It accepts HS256-signed tokens using the *same key material* that underlies its RS256 public key, rather than enforcing a strict per-key algorithm allowlist (e.g. "this key may only ever verify RS256"). Because RSA public keys are, by definition, not secret, any value usable as an RS256 public key can be trivially repurposed as an HS256 shared secret if the server doesn't distinguish between the two. The absence of an exposed JWKS endpoint only raises the bar slightly — it forces an attacker to *derive* the public key mathematically (via `sig2n`, which exploits the GCD relationship between two RSA signatures sharing a modulus) rather than simply downloading it, but it does not prevent the attack.

## Impact

**Technical**
- Full authentication bypass — any user able to capture two of their own valid session tokens can forge a token for any other account, including `administrator`, without ever needing the server's private key or an exposed public key endpoint.
- Defeats algorithm-agnostic JWT libraries that trust the `alg` header value supplied by the client rather than enforcing an expected algorithm server-side.

**Business / Real-World**
- Complete account takeover for any user, including privileged roles.
- No rate-limiting or secondary factor stands between a captured pair of tokens and full admin access — the entire attack is performed offline once the two tokens are captured.

**Scope**
- Any endpoint protected solely by this session-cookie JWT validation is affected, since the forged token is accepted application-wide, not just on the specific endpoint tested.

## Remediation

- Enforce a strict, server-side expected algorithm per key — reject any token whose `alg` doesn't match what that specific key was issued to sign (e.g. keys used for RS256 should never be accepted for HS256 verification, and vice versa).
- Use algorithm-pinned verification libraries/configurations that take an explicit allowed-algorithms list per key rather than trusting the token's own `alg` header.
- Where possible, avoid relying on the mathematical relationship between RSA public/private material and reused symmetric secrets — maintain cryptographically distinct key material for RS256 vs HS256 flows entirely.
- Rotate the compromised key pair immediately upon discovering this class of issue, since any previously captured token pair would otherwise still permit key recovery.

## Lessons Learned & Patterns

- Not exposing a JWKS endpoint is not sufficient mitigation on its own — if two tokens signed by the same RSA key are ever observable (e.g. by logging in twice), the public key can be mathematically recovered via `sig2n` without the server ever publishing it.
- Any time a server accepts more than one `alg` value for verifying tokens tied to the *same* key material, suspect algorithm confusion — test both the "fetch the key" (`jku`/`jwks.json`) and "derive the key" (`sig2n`, two-token GCD recovery) paths before ruling this class out.
- This technique generalizes: any time you can collect two RS256-signed artifacts from the same issuer with no exposed public key, `sig2n` is worth trying before assuming the attack isn't feasible.

## References

- PortSwigger Lab: JWT authentication bypass via algorithm confusion with no exposed key
- [PortSwigger sig2n tool](https://github.com/silentsignal/rsa_sign2n)
- OWASP: [Testing JSON Web Tokens](https://owasp.org/www-project-web-security-testing-guide/)

**Tags:** #PortSwigger #JWT #AlgorithmConfusion #Authentication #sig2n
