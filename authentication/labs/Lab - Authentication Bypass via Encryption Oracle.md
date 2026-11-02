# Authentication Bypass via Encryption Oracle

**Platform:** PortSwigger Web Security Academy

**Category:** Authentication

**Difficulty:** Expert

**Date Solved:** YYYY-MM-DD

**Severity:** Critical

## Summary

The application exposes two unrelated features that both run through the server's internal encryption key, turning them into a matched pair of cryptographic oracles:

- An **encrypt oracle**: the blog comment form reflects an invalid email address back inside an encrypted `notification` cookie — attacker-chosen plaintext goes in, ciphertext comes out.
- A **decrypt oracle**: the resulting error page decrypts whatever is in the `notification` cookie and prints it back as plain text in the error message — attacker-supplied ciphertext goes in, plaintext comes out.

Because both oracles use the same secret key, an attacker can forge a valid `stay-logged-in` cookie for the `administrator` account without ever learning the key. The attacker decrypts their own legitimate cookie to learn its format (`username:timestamp`), swaps `username` for `administrator` while keeping the timestamp field, re-encrypts the forged value through the encrypt oracle, strips the server's constant prefix, and drops the resulting ciphertext into their own cookie to become `administrator`.

## Affected Component

```ocaml
POST /post/comment           (encrypt oracle — email field reflected into Set-Cookie: notification=)
GET  /                       (decrypt oracle — notification cookie decrypted and echoed in error message)
Cookie: stay-logged-in       (forged by the attack)
```

## Steps to Reproduce

1. Log in with the low-privilege credentials provided for the lab and capture the legitimate `stay-logged-in` cookie value.
2. Submit a blog comment with an invalid email address (e.g. `AAAAAAAAAAAAAAAA`) via `POST /post/comment`. The server rejects it and sets a `notification` cookie containing `"Invalid email address: " + <your input>`, AES-encrypted under the server's internal key — this is the **encrypt oracle**.
3. Reload the page. The server decrypts the `notification` cookie and reflects the plaintext into the visible error message — this is the **decrypt oracle**.
4. Swap your real `stay-logged-in` cookie value into the `notification` cookie and reload. The decrypted output reveals the cookie's internal format: `administrator-check:<username>:<timestamp>` (format recovered from the decrypted legitimate cookie — record the exact structure observed).
5. Build the target plaintext by substituting `administrator` for the real username, keeping the original timestamp field. Pad the chosen input with throwaway characters so the removable portion (server's fixed 23-character `"Invalid email address: "` prefix plus padding) lands on a 16-byte AES block boundary.
6. Submit the padded forged value through the comment form (step 2) to obtain its ciphertext via the encrypt oracle.
7. Strip the leading block(s) corresponding to the prefix from the raw ciphertext, leaving only the ciphertext for `administrator:<timestamp>`.
8. Feed the stripped ciphertext back through the decrypt oracle (step 3) to confirm it decrypts cleanly to `administrator:<timestamp>` with no leftover prefix bytes.
9. Replace your own `stay-logged-in` cookie with the stripped, confirmed ciphertext and reload the application.
10. Observe the session now carries `administrator` privileges; access the admin panel to confirm and solve the lab.

## Proof of Concept

#### Oracle pairing

```ocaml
Encrypt oracle:
POST /post/comment
email=<chosen plaintext>
  -> Set-Cookie: notification=<AES-CBC ciphertext of "Invalid email address: " + plaintext>

Decrypt oracle:
GET /
Cookie: notification=<any ciphertext>
  -> page reflects decrypted plaintext in the error banner
```

#### Forgery

```ocaml
1. Decrypt real stay-logged-in cookie via decrypt oracle
   -> reveals format: <username>:<timestamp>

2. Build target plaintext: "administrator:<same timestamp>"
   padded so (prefix_len + padding_len) % 16 == 0

3. Encrypt padded plaintext via encrypt oracle
   -> ciphertext = AES( "Invalid email address: " + padded_target )

4. Strip the first N bytes (N = multiple of 16 covering the prefix)
   from the raw ciphertext
   -> remaining ciphertext = AES("administrator:<timestamp>") block-aligned

5. Confirm via decrypt oracle: stripped ciphertext decrypts to
   "administrator:<timestamp>" with no residual prefix

6. Set stay-logged-in = stripped ciphertext, reload
   -> session is now administrator
```

> Block ciphers (here AES-CBC, 16-byte blocks) only let you cleanly remove a prefix if the prefix-plus-padding length is an exact multiple of the block size. Padding the chosen plaintext with throwaway characters first is what makes the prefix strippable at the byte level.

<!-- Add screenshot references here, e.g. ![Decrypted cookie revealing username:timestamp format](assets/<filename>.png) -->

## Root Cause

Two independently-reasonable features — email validation on a comment form, and an error message that echoes a cookie's content — share the same server-side encryption key with no separation of purpose or scope. Neither endpoint is dangerous in isolation; the vulnerability exists only because:

- The server will encrypt arbitrary attacker-chosen plaintext on request (encrypt oracle).
- The server will decrypt and reflect arbitrary attacker-chosen ciphertext on request (decrypt oracle).
- Nothing authenticates or scopes what may legitimately be encrypted or decrypted through either path, so an attacker can use the pair to produce valid ciphertext for any plaintext of their choosing — including a forged `administrator` session cookie — without ever learning the key.

This is a cryptographic design flaw (encryption oracle / chosen-plaintext attack surface), not a key-strength or algorithm weakness: AES itself is not broken here.

## Impact

**Technical**
- Full authentication bypass: an attacker holding only a standard low-privilege account can forge a valid session cookie for any other user, including `administrator`.
- No credentials, password reset, or prior admin access of any kind are required.
- The attack needs only an intercepting proxy and basic block-alignment arithmetic; no key material is ever recovered or required.

**Business / Real-World**
- This is as close to worst-case severity as a business-logic/crypto flaw gets: it is a complete authentication bypass to the most privileged account in the application.
- On a live program this would typically be rated Critical, since the blast radius is "attacker becomes the most powerful user in the system," not narrower unauthorized access to one other user's data.
- Any admin-only functionality (user management, configuration, data export) becomes reachable the moment the forged cookie is set.

**Scope**
- Affects the application's entire authentication/session model, since the `stay-logged-in` cookie format and encryption key are shared platform-wide.
- Any account reachable via the comment form's email-reflection path can be impersonated once its username is known (here, `administrator`, which is typically guessable or already known).

## Remediation

1. **Never expose both encrypt and decrypt operations on the same key to user-controllable input.** If a feature must encrypt/decrypt attacker-influenced data, use a key and context fully separated from authentication tokens.
2. **Authenticate ciphertext, don't just encrypt it.** Use an authenticated encryption mode (e.g. AES-GCM) or a MAC over the plaintext so tampered or forged ciphertext fails integrity checks before decryption is even attempted.
3. **Never reflect decrypted session/cookie content back to the user**, even in an error message. Treat any value that round-trips through the server's crypto as sensitive, not safe to echo.
4. **Bind session tokens to more than a username and timestamp.** Include a server-side nonce, session ID, or signature that cannot be reconstructed purely from captured plaintext structure.

```ocaml
# Authenticated encryption example (conceptual)
ciphertext, tag = AES_GCM_encrypt(key, plaintext, associated_data=session_context)

on decrypt:
    if not verify_tag(tag, associated_data):
        reject()
    plaintext = AES_GCM_decrypt(key, ciphertext)
```

## Lessons Learned & Patterns

- **Hunt for reflected, round-tripped values.** Any endpoint where user input triggers a validation error, and that error either (a) reflects the input directly, or (b) sets/updates a cookie that later gets reflected elsewhere, is worth testing as a potential encrypt/decrypt oracle pair.
- **Likely locations:** registration forms, profile update forms, "contact us" forms, search boxes with unusual validation, password-reset email fields, newsletter signups — anywhere a field is validated and the app shows back what was typed.
- **Spot the companion half:** look for any long-lived, encoded-looking cookie (long string, ends in `=`/`%3d`, high-entropy characters) elsewhere in the app. If an error-reflection point also exists, cross-paste values between the two to test whether they share a key.
- **What matters is behavior, not naming.** A cookie called `notification`, `last-action`, or `flash-message` is equally suspect — the signal is "does this value change based on my input and get reflected back," not the cookie's label.
- Block-cipher prefix stripping requires padding the input so the removable prefix length is a multiple of the block size (16 bytes for AES) — this is a mechanical, tool-assisted step, not a conceptual one. Byte arithmetic here is a good candidate to script or check with a quick calculation rather than doing by hand.
- This is the deepest lab solved in this topic to date — unlike hypothesis-and-poke labs, it required sequential, deliberate technical execution: recover the oracle pair, recover the format, forge the plaintext, align to the block boundary, re-encrypt, verify, deploy.

## References

- [PortSwigger — Authentication bypass via encryption oracle](https://portswigger.net/web-security/authentication/other-mechanisms/lab-auth-bypass-via-encryption-oracle)
- [PortSwigger — Authentication vulnerabilities](https://portswigger.net/web-security/authentication)
- [OWASP WSTG — Testing for Weak Cryptography](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/)
- [MITRE CWE-310 — Cryptographic Issues](https://cwe.mitre.org/data/definitions/310.html)
- [MITRE CWE-287 — Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)

**Tags:** #PortSwigger #Authentication #EncryptionOracle #CryptographicAttack #SessionForgery #CriticalSeverity
