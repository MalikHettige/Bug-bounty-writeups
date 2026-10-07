**Platform:** PortSwigger Web Security Academy

**Category:** Authentication / JWT

**Difficulty:** Practitioner

**Date Solved:** 2026-10-07

**Severity:** Critical

## Summary

The application's JWT verification logic trusts the `jku` (JWK Set URL) header claim without restricting it to a pinned or allowlisted host. An attacker can set `jku` to point at a self-hosted JSON Web Key Set, sign a forged token with a matching private key, and have the server accept it as valid — enabling full authentication bypass to any user, including administrators.

## Affected Component

JWT verification middleware on the session/authentication layer (endpoint that validates the session cookie/Authorization header on each request).

## Steps to Reproduce

1. Get authenticated as a low-privileged user (wiener) in `https://TARGET_URL/my-account`
2. Go to Burp and proxy panel, in HTTP history look for `GET /my-account?id=USERNAME HTTP/2` request
3. Copy the first segment of the cookie (double click the first line of the cookie and the first portion will get selected), right click and decode it. Observe that the application uses `RS256` (ex: `{"kid":"372129e6-8fff-4cdb-9140-65a5ee8e59d3","alg":"RS256"}`). Application usage on JWT-based session cookie is confirmed.
4. In Burp's JWT Editor extension, generate a new `2048-bit` RSA key pair. Note the `kid` value (e.g. `0fd329e6-dbd7-4ac5-b55e-87252f2aa470`).
5. Copy the public key as JWK (right-click key → **Copy Public Key as JWK)**.
6. Host the following JWKS document at an attacker-controlled URL:
- In exploit server, paste the following exploit server body and replace `PASTE_PUBLIC_JWK_HERE` with the copied public key
- Input `/jwks.json` in the **File:** box
- Paste that 2-line head values in the POC
- Click store
7. back to Burp Repeater, in the JSON Web Token tab, replace the entire value of **header** with the one in POC.
8. In payload section, set `"sub": "administrator"`.
9. Click Sign, make sure "Don't modify header" is checked, select the generated RSA key and click **OK**
10. Send the request.
The server fetches the JWKS from the attacker URL, finds the public key matching `kid`, verifies the signature (which passes because the attacker signed with the matching private key), trusts `sub: administrator`, and grants admin access.

## Proof of Concept
**Body value in exploit server**

```jsx
{
    "keys": [
        PASTE_PUBLIC_JWK_HERE
    ]
}
```

**Head section in exploit server** 
```pascal
HTTP/1.1 200 OK
Content-Type: application/json
```
**Exploit server would look like this:**

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/65b0509c-316c-4df0-8c40-6a3be8a92e2e" />

**Value of header in JWT web token**
```jsx
{
    "kid": "PASTE_YOUR_KID_HERE",
    "typ": "JWT",
    "alg": "RS256",
    "jku": "https://attacker.com/jwks.json"
}
```
**Request/response showing admin panel access with the forged token (screenshot/HTTP trace attached)**
<img width="1455" height="787" alt="image" src="https://github.com/user-attachments/assets/d7397d5a-441b-49cb-bddb-9f564102ed5d" />

## Root Cause

The server resolves the signing key dynamically from a URL supplied inside the token itself (`jku` header) rather than validating against a fixed, trusted key or a strict allowlist of key-source domains. This inverts trust: the attacker, who controls the token, also controls what's treated as the trusted verification key.

## So how can this decoded cookie segment trigger an attacker to bypass authentication? Especially via jku Header Injection?

## Impact

### **Technical**

Complete authentication bypass. Arbitrary token forgery for any user ID or role claim present in the application's JWT schema.

### **Business / Real-World**

Full account takeover of any user, including administrators — unauthorized access to all protected functionality and data reachable via the session layer. Equivalent to a master key for the application's auth system.

### **Scope**

All endpoints protected by this JWT verification logic; any user account.

## Remediation

- Do not fetch signing keys from a URL supplied in the token. Pin verification to a small set of server-held public keys (or a strict, hardcoded allowlist of trusted JWKS hosts, verified over TLS with certificate pinning).
- Reject tokens with unexpected/unauthorized `jku`, `jwk`, or `x5u` headers.
- Enforce algorithm allowlisting (reject `alg: none`, mismatched `alg`).
- Monitor/alert on JWT verification requests to unexpected external hosts.

## Lessons Learned & Patterns

- Any JWT header claim that influences *where the verification key comes from* (`jku`, `jwk`, `x5u`) is attacker-controlled input and must never be trusted without strict allowlisting.
- Pattern to always test on new JWT implementations: does changing `jku` to an attacker URL even get fetched at all (confirms SSRF/trust issue) before attempting full forgery.
- In the wild, treat `jku`/`x5u` SSRF and full auth bypass as two separate potential findings — report whichever you can actually prove.

## References

- PortSwigger Lab: JWT authentication bypass via jku header injection
- RFC 7519 (JWT), RFC 7517 (JWK)

**Tags:** #PortSwigger #JWT #AuthenticationBypass #jku
