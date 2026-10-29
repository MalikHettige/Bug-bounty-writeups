# Authentication Bypass via OAuth Implicit Flow

**Platform:** PortSwigger Web Security Academy
**Category:** Authentication / OAuth 2.0 / Business Logic
**Difficulty:** Practitioner
**Date Solved:** 2026-10-26
**Severity:** Critical

## Summary

The lab's client application ("WeLikeToBlog") implements OAuth 2.0 using the **implicit grant flow** to let users log in via a third-party identity provider. After the provider redirects back with an access token, the client calls its own backend (`POST /authenticate`) and passes along the `email`, `username`, and `token` values that were parsed client-side out of the OAuth response. The backend never re-validates these identity claims against the access token or the identity provider — it trusts whatever `email`/`username` the client-side request supplies and issues a session for that account.

Because the only "proof of identity" the server checks is attacker-controlled data in the request body, an attacker can run the OAuth flow for their *own* low-privilege account, intercept the `/authenticate` request, swap in the victim's known email and username, and receive a valid, authenticated session cookie for the victim's account — without ever knowing their password.

## Affected Component

- `GET /auth?client_id=...&redirect_uri=.../oauth-callback&response_type=token&nonce=...&scope=openid%20profile%20email` — OAuth implicit-flow authorization request (response_type=token means the token is returned directly in the fragment, never exchanged server-side)
- `GET /oauth-callback` — client-side callback page; its JS pulls the access token out of the URL, calls the OAuth userinfo endpoint (`GET /me`), and extracts `email` / `username` from the response
- `POST /authenticate` — the vulnerable endpoint. Accepts a JSON body of `{email, username, token}` from the client and issues a session **without validating those fields server-side against the token**

## Steps to Reproduce

1. From the lab home page, click **My account** without being logged in. This triggers the OAuth flow and redirects through a chain:
   - `GET /my-account` → `302 Found` → `GET /auth?client_id=k93q0n8viv5xm6uzja911&redirect_uri=https://<lab-id>.web-security-academy.net/oauth-callback&response_type=token&nonce=<nonce>&scope=openid%20profile%20email`
   - This lands on the identity provider's login/consent screen at `/interaction/<interaction-id>`, which shows the consent prompt: *"WeLikeToBlog is requesting access to: Profile and Email."*
   - At this stage the browser is holding three cookies set by the provider: `_interaction`, `_session`, and `_session.legacy`. Note the `_interaction` cookie's value matches the `<interaction-id>` in the URL — this is the provider tracking the in-progress login, not the client app.

2. Log in with valid lab credentials (`wiener:peter`) and click **Continue**. The `_interaction` cookie is swapped for `_interaction_resume` (same value), and the flow proceeds:
   - `GET /auth/<interaction-id>` → confirms the authorization
   - `GET /oauth-callback?...` → `200 OK`

3. **This is the key request.** The response body of `GET /oauth-callback` is not a redirect but an actual HTML page containing an inline `<script>`. Reading that script shows the client-side logic that:
   - Extracts the access token from the URL fragment (`#access_token=...`)
   - Calls `GET /me` using that token to fetch the authenticated user's profile (email + username/subject identifier)
   - Builds a request to the backend with that data

4. Visiting **My account** again confirms a normal login: the page just prints `Your username is: wiener` / `Your email is: wiener@hotmail.com` — i.e., the client app trusts the client-side script's output to decide who's logged in.

5. First attempt — tried a direct IDOR against the account page itself:
   - `GET /my-account?id=carlos` → `302 Found` → `Location: /social-login`
   This fails (forces re-auth), proving the account page itself isn't the vulnerable point — access control there is fine. The actual trust boundary is earlier, in how the *session* gets created in the first place.

6. Repeated the OAuth login while watching the network tab closely. Two requests stood out around the callback: `GET /me` (fetches the OAuth-provider profile for the logged-in attacker) and `POST /authenticate` (the client backend's login call). Inspected the `POST /authenticate` request body — it's JSON containing `email`, `username`, and the OAuth `token`:

   ```http
   POST /authenticate HTTP/2
   Host: 0abb00140420cc6980eb0d69009a00ea.web-security-academy.net
   Content-Type: application/json

   {"email":"wiener@hotmail.com","username":"wiener","token":"<access_token>"}
   ```

7. Sent this request to Burp Repeater. Replaced `email` and `username` with the victim's known values (`carlos` / `carlos`'s email — disclosed in the lab description), leaving the `token` untouched (it still belongs to the attacker's own authenticated session, but the backend never checks that it matches the claimed identity):

   ```http
   POST /authenticate HTTP/2
   ...
   {"email":"carlos@carlos-montoya.net","username":"carlos","token":"<attacker's own access_token>"}
   ```

8. The server responded `302 Found` with a fresh `Set-Cookie: session=...` header — a **valid authenticated session for Carlos**, generated purely from attacker-supplied JSON fields.

9. Replaced the browser's `session` cookie with this new value (via DevTools → Application → Cookies, as shown in the PoC) and reloaded **My account**. The page now showed Carlos's account. Lab solved.

## Proof of Concept

```http
POST /authenticate HTTP/2
Host: 0abb00140420cc6980eb0d69009a00ea.web-security-academy.net
Content-Type: application/json
Cookie: _interaction_resume=w8yOEBL2f8pI9MHrzv4tS; ...

{"email":"carlos@carlos-montoya.net","username":"carlos","token":"<attacker-owned access_token>"}
```

**Response:**

```http
HTTP/2 302 Found
Location: /
Set-Cookie: session=vDne40nikGgdJXs9IpNkp0QXJxwvoLY; Secure; HttpOnly
```

Swapping this `session` cookie into the browser grants full access to `carlos`'s account — confirmed via the DevTools Application → Cookies panel and the "Congratulations, you solved the lab!" banner.

## Root Cause

OAuth's implicit flow was never designed to carry identity assertions as free-form client-supplied data — the access token is meant to be the *only* thing the client trusts, and any identity claims must be re-derived server-side by calling the provider's userinfo endpoint with that token. Here, the client-side JavaScript does the userinfo lookup (`GET /me`) and then **re-submits the result as plain, editable JSON** to its own backend. The backend's `/authenticate` handler treats `email` and `username` in that JSON as ground truth and never:

- Verifies the `token` actually belongs to the account named by `email`/`username` (e.g., by independently calling `/me` with that token server-side and comparing)
- Validates the token's audience/scope against the client app
- Checks that the `token` wasn't just a token for *any* authenticated attacker account being paired with someone else's identity strings

In short: **authentication was delegated to the client**, and the client is attacker-controlled.

## Impact

**Technical**
- Full account takeover for any user whose email/username is known or guessable, with zero knowledge of their password
- No interaction from the victim required
- Trivial to script/automate at scale once the request shape is known

**Business / Real-World**
- Complete compromise of the authentication layer — the "Login with social media" feature becomes a universal skeleton key
- Attacker gains persistent access (a real, valid session cookie) rather than a one-off glitch, so the compromise survives until the session expires or is revoked
- Reputational/trust damage: users who deliberately chose OAuth login for its perceived security are the ones directly exposed

**Scope**
- Every account reachable via the OAuth login path on the affected client application

## Remediation

- Never trust identity claims sent from client-side code. After receiving the access token, the **server** should call the provider's userinfo endpoint itself and use *that* response as the sole source of `email`/`username` — the client should not be able to pass those fields at all.
- Prefer the **authorization code flow** (with PKCE) over implicit flow — it keeps the token exchange server-to-server and removes the token/identity data from the browser-accessible fragment entirely.
- Bind the session strictly to the `sub` (subject identifier) returned by the provider, not to a mutable email/username string.
- Validate the `nonce` and `state` parameters to prevent replay/CSRF on the OAuth flow itself.

## Lessons Learned & Patterns

- **Chain-first reflex confirmed useful but not sufficient here** — tried the obvious IDOR (`/my-account?id=carlos`) first since that's the fast win pattern, and it correctly failed because access control on the account page wasn't the flaw. The real bug was one layer upstream, in how the *session itself* gets minted. Lesson: when a direct IDOR on the "final" resource fails, walk back through the request chain that *produces* the session/token — the trust boundary is often earlier than the endpoint you're staring at.
- **Any response body is worth reading, not just status codes.** The `GET /oauth-callback` request returning `200 OK` with an inline `<script>` (instead of a plain redirect) was the tell — that script is doing security-relevant client-side work (extracting the token, calling `/me`, building the login request). Always view-source / read response bodies on redirects and callback endpoints, don't just skim the response code.
- **Cookie naming conventions are a map of the flow.** Watching `_interaction` → `_interaction_resume` (same value, different name) across requests confirmed exactly where in the provider's state machine the request sat — useful for distinguishing provider-side session cookies from the client app's own `session` cookie, especially when juggling multiple origins in one flow.
- **General pattern for OAuth implicit-flow bugs:** look for any endpoint where the *client* tells the backend who the user is (email/username/user_id in a POST body) alongside a token, rather than the backend deriving identity purely from the token. That's the signature of "client-side identity trust" — swap the identity fields, keep your own valid token, and test.
- **Reusable technique:** your own valid token + victim's identity strings = account takeover, whenever identity data and the token travel as separate, independently-editable fields in the same request.

## References

- PortSwigger Lab: Authentication bypass via OAuth implicit flow
- OWASP: OAuth 2.0 Threat Model and Security Considerations (RFC 6819)

**Tags:** #PortSwigger #OAuth #AuthenticationBypass #AccountTakeover #BusinessLogic
