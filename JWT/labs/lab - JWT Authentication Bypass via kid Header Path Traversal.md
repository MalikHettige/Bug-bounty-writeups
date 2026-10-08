**Platform:** PortSwigger Web Security Academy

**Category:** JWT / Authentication

**Difficulty:** Practitioner

**Date Solved:** 2026-10-08

**Severity:** Critical

## Summary
The application verifies JWT signatures using HS256, looking up the key file via the `kid` (Key ID) header field without sanitizing its value. By injecting a path traversal sequence (`../../../../../../dev/null`) into `kid`, the server can be forced to load `/dev/null` — a file guaranteed to be empty on any Linux system — as the signing key. Since the key content is now a known, predictable value (zero bytes), an attacker can forge a validly-signed token using an empty string as the HMAC key.

## Affected Component
`GET /admin` — administrative panel, gated by JWT-based session authentication. Underlying flaw affects the entire session verification mechanism.

## Steps to Reproduce
1. Authenticate as a low-privilege user (`wiener:peter`).
2. In Burp, go to Proxy → HTTP history, locate `GET /my-account?id=wiener`, send to Repeater.
3. In the JSON Web Token panel, edit the header: change `kid` to `../../../../../../dev/null`.
4. Edit the payload: change `sub` from `wiener` to `administrator`.
5. Compute a valid HS256 signature over the modified header and payload using an empty byte string as the HMAC key (PyJWT rejects empty keys by design, so the signature must be computed manually via Python's `hmac` module — see PoC script).
6. Replace the session cookie with the resulting forged token (via Repeater or browser DevTools → Application → Cookies).
7. Navigate to `/admin` — access granted.
8. Locate and send the deletion endpoint (`/admin/delete?username=carlos`) to confirm full exploitability.

## Proof of Concept
Forging script (manual HMAC construction, bypassing PyJWT's empty-key restriction): [Run this script & make sure to replace 'APPLICATION' with portswigger in 16th line](https://github.com/MalikHettige/Scripts-tools/blob/main/JWT/JWT%20authentication%20bypass%20via%20kid%20header%20path%20traversal/forge_empty_key.py)

Sent with `GET /admin` → `200 OK`, admin panel content returned. `GET /admin/delete?username=carlos` executed successfully
<img width="1493" height="814" alt="image" src="https://github.com/user-attachments/assets/53e032ca-c65d-4135-bc8b-20f1f0bb484d" />

## Root Cause
The server constructs a filesystem path directly from the attacker-controlled `kid` header value, without validating or restricting it to a fixed, trusted set of key identifiers. This allows an attacker to traverse outside the intended key directory using `../` sequences and force the server to use an arbitrary, attacker-chosen file — in this case, a predictable empty file — as the cryptographic key for signature verification.

## Impact

### Technical
Complete authentication bypass. The attack requires no knowledge of the server's real secret or private key material — only the ability to predict the content of a file reachable via path traversal (trivial on Linux, where `/dev/null` is a universal constant).

### Business / Real-World
Full account takeover of any user, including administrators. Combines two distinct weaknesses — unsanitized `kid` input and HS256's reliance on key secrecy — into a single critical bypass requiring no credential knowledge of the target account.

### Scope
Every endpoint protected by this JWT verification mechanism is affected, not solely `/admin`.

## Remediation
- Never use client-controlled header values (`kid`, `jku`, `x5u`, etc.) to directly construct filesystem paths or resource lookups.
- Restrict `kid` to a fixed allow-list of known, pre-registered key identifiers; reject any value not present in that list.
- Apply strict input validation/sanitization to reject path traversal sequences (`../`, encoded variants) on any field that influences file or resource resolution, regardless of its apparent purpose.

## Lessons Learned & Patterns
- Same root category as `jwk` header injection and `alg: none` labs: the server trusts attacker-supplied token metadata to determine its own verification behavior, rather than enforcing a fixed, server-controlled process.
- Path traversal isn't limited to obvious file-download endpoints — any field used internally to construct a file path (including JWT header fields like `kid`) is a traversal candidate.
- `/dev/null` is a reliable "known empty file" target on Linux systems for any attack requiring a predictable key/content value.
- PyJWT (and likely other libraries) blocks empty HMAC keys by design — when a lab/target requires this, signature construction must be done manually via the underlying crypto primitives (`hmac`, `hashlib`) rather than the high-level library.

## References
- PortSwigger Lab: JWT authentication bypass via kid header path traversal — https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal
- PortSwigger JWT Attacks Learning Material — https://portswigger.net/web-security/jwt
- OWASP Path Traversal — https://owasp.org/www-community/attacks/Path_Traversal
- RFC 7515 (JSON Web Signature spec, defines `kid`) — https://www.rfc-editor.org/rfc/rfc7515

**Tags:** #PortSwigger #JWT #AuthenticationBypass #PathTraversal #HS256
