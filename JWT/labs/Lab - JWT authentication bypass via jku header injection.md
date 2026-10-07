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

1. Log in as a low-privileged user and capture the issued JWT
2. Generate an RSA key pair locally 

This requires Burp JWT Editor extension so make sure to install it, then there is the **JWT editor** panel. In there, click **New RSA Key** and click **Generate**. 

3. Host a JWKS document containing the new **public** key at an attacker-controlled URL (e.g. exploit server `/jwks.json`). 

In the lab go to **exploit sever**  and add **`/jwks.json`** to the File box

4. Go back to repeater>JWT Editor, modify the token: 
- Add a new line in header `"jku": "EXPLOIT_SERVER_URL/jwks.json"`
- In payload, set `sub`claim to `administrator`.
5. Click Sign and make sure the “don’t modify the header” is selected.
6. Replace the original token in the request/cookie with the forged one.
7. Send the request to a privileged endpoint (e.g. `/admin`) — access is granted.

## Proof of Concept

- Request/response showing admin panel access with the forged token (screenshot/HTTP trace attached).

**Body value in exploit server**

```jsx
{
    "keys": [
        PASTE_PUBLIC_JWK_HERE
    ]
}
```
<img width="1455" height="787" alt="image" src="https://github.com/user-attachments/assets/d7397d5a-441b-49cb-bddb-9f564102ed5d" />

## Root Cause

The server resolves the signing key dynamically from a URL supplied inside the token itself (`jku` header) rather than validating against a fixed, trusted key or a strict allowlist of key-source domains. This inverts trust: the attacker, who controls the token, also controls what's treated as the trusted verification key.

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
