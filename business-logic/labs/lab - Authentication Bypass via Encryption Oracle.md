# Authentication Bypass via Encryption Oracle

**Platform:** PortSwigger Web Security Academy<br>
**Category:** Business Logic<br>
**Difficulty:** Expert<br>
**Date Solved:** 2026-11-02<br>
**Severity:** Critical<br>

## Summary

The application encrypts the `stay-logged-in` cookie as `username:timestamp` using a block cipher (AES). A completely unrelated feature — the comment submission flow — uses the **same encryption key** to set a `notification` cookie, and reflects the decrypted value of any `notification` cookie it's handed back into an error message. This turns one feature into an **encrypt oracle** (user input in → ciphertext out) and the other into a **decrypt oracle** (ciphertext in → plaintext out), both keyed to the same secret. Chaining them lets you forge a validly-encrypted `administrator:<timestamp>` cookie with no knowledge of the key itself, and use it to fully bypass authentication.

## Affected Component

- `POST /post/comment` — email field is encrypted and reflected via `Set-Cookie: notification=...` on validation failure (**encrypt oracle**)
- `GET /post?postId=x` — decrypts the `notification` cookie and reflects the plaintext in the "Invalid email address: ..." error body (**decrypt oracle**)
- `stay-logged-in` cookie — same cipher/key, format `username:timestamp`, used for persistent authentication

## Steps to Reproduce

1. Log in as `wiener:peter` with "Stay logged in" checked, and post a comment with an intentionally invalid email. Observe two things in Burp: the `stay-logged-in` cookie is opaque/encrypted, and the comment error response sets an equally opaque `notification` cookie.

2. Send the `POST /post/comment` request and the following `GET /post?postId=x` request to Repeater. Rename the tabs `encrypt` and `decrypt`.

3. In `decrypt`, replace the `notification` cookie with your real `stay-logged-in` cookie value and send. The error message reflects it in cleartext, e.g.:
   ```
   wiener:1793601652468
   ```
   This confirms both cookies share the same key, and reveals the plaintext format: `username:timestamp`.

4. In `encrypt`, set the `email` parameter to `administrator:<that timestamp>` and send. Copy the new `notification` cookie — this is ciphertext encrypting your chosen string.

5. Decrypt that cookie via the `decrypt` request. The output is:
   ```
   Invalid email address: administrator:1793601652468
   ```
   The server prepends a fixed 23-character prefix (`"Invalid email address: "`) to anything you submit before encrypting it. That prefix has to be removed at the **ciphertext** level, not the plaintext level, since you only control the plaintext going in, not the server's prefix.

6. AES is a block cipher (16-byte blocks). You can only cleanly delete bytes from ciphertext in whole-block increments. 23 bytes isn't a multiple of 16, so deleting it outright corrupts the surrounding block. Fix: pad the *front* of your submitted plaintext with junk characters so `(junk + 23)` rounds up to a clean multiple of 16.
   ```
   9 junk chars + 23-byte prefix = 32 bytes = 2 full AES blocks
   ```

7. Re-submit via `encrypt` with:
   ```
   xxxxxxxxxadministrator:1793601652468
   ```
   Capture the new `notification` cookie. URL-decode and base64-decode it in Burp Decoder, switch to the Hex view, and delete the **first 32 bytes** (2 full blocks). Re-encode.

8. Paste the stripped ciphertext into the `decrypt` request's `notification` cookie and send. Confirm the response now shows **exactly**:
   ```
   administrator:1793601652468
   ```
   No prefix, no junk characters — a clean forged plaintext.

9. Send a `GET /` request to Repeater. Delete the `session` cookie entirely, and set `stay-logged-in` to the stripped ciphertext from step 8. Send — the response now reflects an authenticated administrator session.

10. Browse to `/admin`, then `/admin/delete?username=carlos` to solve the lab.

## Proof of Concept

Captured notification cookie after padding + stripping (URL-encoded, ready to drop into `stay-logged-in`):

```
gZ2gc2v3oIbmnPGLwSeurdvKcgLXmpv9WKG7qnGzS30%3D
```

Decrypted via the oracle, this returns exactly:

```
administrator:1793601652468
```

Used as the `stay-logged-in` cookie value with the `session` cookie removed, this authenticates as `administrator` with no credentials and no interaction from the victim.

## Root Cause

```
stay-logged-in cookie:   encrypt(username:timestamp)   — key K
notification cookie:     encrypt(user input)            — SAME key K
decrypt endpoint:        decrypt(notification cookie) → reflected in error

Gap: one encryption key is reused across two unrelated features, and
     one of those features exposes both an encrypt path (attacker
     plaintext in, ciphertext out) and a decrypt path (attacker
     ciphertext in, plaintext out) to unauthenticated/low-privilege
     users. Together they form a full encryption oracle against a
     cipher that also protects the authentication cookie.
```

## Impact

**Technical**
- Full authentication bypass — forge a session for any arbitrary username, including `administrator`, without credentials
- No rate limiting or detection on the oracle requests observed during testing

**Business / Real-World**
- Complete account takeover for any user, including privileged/admin accounts
- Zero-interaction — doesn't require tricking a victim, phishing, or any action from the targeted account

**Scope**
- Any endpoint protected by `stay-logged-in`-based persistent authentication

## Remediation

1. Never reuse a single encryption key across unrelated application features — scope keys per purpose (session cookies vs. notification/error cookies should use separate keys, or separate mechanisms entirely)
2. Don't expose raw encrypt/decrypt primitives to user input anywhere in the app, even indirectly through error messages — avoid reflecting decrypted attacker-supplied data back to the client
3. Use authenticated encryption (e.g. AES-GCM) with a MAC, so tampered/forged ciphertext fails integrity checks instead of silently decrypting
4. Prefer signed, non-encrypted session tokens (e.g. a server-side session ID, or a signed-only JWT) over client-side encrypted state where there's no real need for confidentiality

## Lessons Learned & Patterns

- Any two cookies/tokens from the same app that look like opaque binary blobs (no `eyJ` JWT prefix, byte length always a multiple of 16) are worth cross-testing for shared-key reuse.
- The generic hunting pattern isn't "find a comment box" — it's "find any feature that reflects user input through encryption, and any feature that reflects decrypted attacker-supplied ciphertext," then test whether they share a key.
- The padding math is empirical, not something to guess: measure the server's injected prefix length directly from its own error text, then round up to the cipher's block size to know exactly how much junk to prepend before the next encrypt call.
- This bug class is rare in real programs — most apps use standard auth libraries (Auth0, Firebase, Passport, signed JWTs) with no custom encrypt/decrypt surface at all. It shows up mainly on **custom-rolled auth stacks** that reuse one in-house crypto helper across features. Worth testing opportunistically on legacy/custom auth, not worth building a primary hunting strategy around.
- When it does hit, it pays like a top-tier Critical (full zero-interaction ATO), which is why it's worth keeping in the toolkit despite being uncommon.

## References

- PortSwigger Lab: Authentication bypass via encryption oracle
- Script used: [`oracle_stripper.py`](https://github.com/MalikHettige/scripts-tools/blob/main/business-logic/Authentication%20bypass%20via%20encryption%20oracle/oracle_stripper.py)

**Tags:** #PortSwigger #BusinessLogic #EncryptionOracle #AuthenticationBypass #AccountTakeover #Expert
