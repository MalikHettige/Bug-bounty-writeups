**Platform:** PortSwigger Web Security Academy

**Category:** JWT

**Difficulty:** Practitioner 

**Date Solved:** 2026-10-06

**Severity:** Critical

## Summary
The application signs JWT session cookies using HS256 (HMAC-SHA256), a symmetric algorithm where the same secret key both signs and verifies tokens. The secret key chosen by the application is a common, weak value present in public wordlists, allowing it to be cracked offline in seconds. Once obtained, the secret can be used to forge arbitrary, validly-signed session tokens for any user, including administrator.

## Affected Component
`/admin` — administrative panel, gated by JWT-based session authentication. Underlying flaw affects the entire session mechanism, not just this one endpoint.
```
https://target.com/admin
```

## Steps to Reproduce

1. In the homepage, click **my account** and get authenticated 
2. In burp, go to proxy tab, HTTP history and look for `GET /my-account?id=YOUR_ID HTTP/2` request.
- Make sure you have **JWT editor** burp extension installed and enabled. Install it here: https://github.com/portswigger/jwt-editor if you haven't    
4. Send to repeater (Ctrl + R) and click **JSON web token** section right above the request. 
5. Look for the value of `"alg"` in header section, Confirm `alg: HS256` (symmetric algo = brute-forceable in principle, doesn't prove the secret is weak yet)
6. Run [this script](https://github.com/MalikHettige/Scripts-tools/blob/main/JWT/JWT%20authentication%20bypass%20via%20weak%20signing%20key/cracking_script.py), replace **"PASTE_YOUR_FULL_JWT_HERE"** with JWT-based cookie. 
- Read the README for more information. Use Git bash, paste the script and paste `python crack_jwt.py`
7. The bottom of the results may show **`[+] FOUND SECRET: secret1`,** observe the key is obtained
8. Now generate the cookie for the victim/administrator by running [this script](https://github.com/MalikHettige/Scripts-tools/blob/main/JWT/JWT%20authentication%20bypass%20via%20weak%20signing%20key/forge_the_admin_token.py)
- Make sure to replace `APPLICATION_ISSUER` with `portswigger`
9. After it’s completed. The raw cookie will be shown at the bottom. Copy the cookie
10. Go back to repeater, replace the cookie, replace `/my-account?id=YOUR_ID` path in request line with the path for admin panel which is `/admin` and send
11. It returns `200OK`, observe it worked as expected, search for the victim’s username (`carlos`) and look for the deletion path like `/admin/delete?username=carlos`
12. Replace it with the request’s path —user deleted. Lab solved

This can also be done in web-dev tools —> applications —> cookie —> cookie value replaced —> append the URL with `/admin`and have the UI version of admin panel to delete any user.

## Proof of Concept
Forged token payload:
```
{"iss": "portswigger", "sub": "administrator", "exp": 9999999999}
```
Signed with recovered secret `secret1` using HS256. Token accepted by server; `/admin` returned `200 OK` with full admin panel content. `GET /admin/delete?username=carlos` executed successfully, confirming write-level impact (not just read access).

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b68e5de5-64a3-4687-9fbd-f0cd9e0d4b4a" />

## Root Cause
The application uses HS256 for JWT signing — a symmetric algorithm where the signing and verification process both depend on one shared secret string. The developer selected an extremely weak, common secret (`secret1`), present in publicly available secret wordlists. This is not a flaw in HS256 itself (correctly implemented with a strong, high-entropy secret it's secure) — it's an implementation/configuration mistake: weak secret selection.

## Impact

### Technical
Full authentication bypass. Possession of the cracked secret allows an attacker to mint arbitrarily-privileged, correctly-signed tokens with no further exploitation required — not a workaround or edge case, but genuine cryptographic forgery using the server's real signing key.

### Business / Real-World
Complete account takeover for any user on the platform, administrators included. An attacker could access, modify, or delete any account's data, impersonate any user indefinitely (tokens can be forged with arbitrarily distant expiry), and gain full administrative control. If this secret is reused across other services (common in real deployments), the blast radius extends beyond this single application.

### Scope
Every endpoint protected by this JWT session mechanism is affected, not solely `/admin`.

## Remediation
- Replace the weak secret with a cryptographically random, high-entropy value (minimum 256 bits, generated via a secure random source — never a dictionary word or short string).
- Consider migrating to an asymmetric algorithm (RS256/ES256) so the signing key never needs to be shared with verification infrastructure.
- Rotate the compromised secret immediately and invalidate all existing sessions.
- Implement secret-strength validation/linting as part of the CI/deployment pipeline to catch weak secrets before production.

## Lessons Learned & Patterns
- Always check the `alg` value in a JWT header — if it's `HS256` (or any `HSxxx` symmetric variant), immediately attempt a secret brute-force using a public wordlist as a default test, not just when hinted.
- A correctly-implemented verification process (signature genuinely checked, nothing skipped) can still be fully broken if the underlying secret is weak — this is a distinct vulnerability class from missing/bypassed verification (see: unverified signature, alg:none labs).
- Terminology matters for report credibility: HS256 uses a shared **secret key** (symmetric); RS256/ES256 use a **private/public key pair** (asymmetric). These are not interchangeable terms.
- Worth checking in RW whether a cracked/weak secret is reused across multiple services — significantly raises severity and blast radius.

## References
- PortSwigger Lab: JWT authentication bypass via weak signing key — https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key
- PortSwigger JWT Attacks Learning Material — https://portswigger.net/web-security/jwt
- OWASP JWT Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- Wallarm JWT Secrets Wordlist — https://github.com/wallarm/jwt-secrets
- RFC 7519 (JSON Web Token spec) — https://www.rfc-editor.org/rfc/rfc7519

**Tags:** #PortSwigger #JWT #WeakSecret #AuthenticationBypass #HS256
