# Host Header Authentication Bypass — Unauthorized Admin Panel Access

**Platform:** PortSwigger Web Security Academy
**Category:** HTTP Host Header Attacks / Access Control
**Difficulty:** Apprentice
**Date Solved:** 2026-10-31
**Severity:** Critical

## Summary

The application's admin panel restricts access based on an assumption that requests originating with `Host: localhost` must come from a trusted internal network position. This logic conflates "the client-supplied Host header says localhost" with "this request actually originated from the server's local network" — two entirely unrelated facts. Since the `Host` header is fully attacker-controlled, any external, unauthenticated party can set `Host: localhost` on a request to the admin panel and be treated as a trusted local user, gaining full administrative access — including the ability to delete arbitrary user accounts — from anywhere on the public internet.

## Affected Component

`GET /admin` and `GET /admin/delete?username={target}` — admin panel and user-deletion action, gated by Host-header-based "local user" authorization logic.

## Steps to Reproduce

1. **Baseline.** Requested the home page (`GET /`) and confirmed via Repeater that an arbitrary `Host` header value did not break the response — the server does not validate `Host` against an expected domain for general requests.

2. **Recon.** Checked `/robots.txt`:
   ```
   User-agent: *
   Disallow: /admin
   ```
   This disclosed the existence of an admin panel at `/admin`, despite it being disallowed from search indexing rather than genuinely access-controlled.

3. **Confirm the access restriction and its basis.** Requested `/admin` directly and received:
   > "Admin interface only available to local users"

   This message reveals the server's authorization logic is based on perceived request origin ("local"), not credentials, roles, or session state — a strong signal that some client-controllable signal (most commonly the `Host` header) is being used as a trust proxy for network position.

4. **Exploit.** Sent `GET /admin` to Burp Repeater and changed the `Host` header from the real application domain to `localhost`. The request succeeded, returning the full admin interface — including a user list with per-user "Delete" actions (`/admin/delete?username={username}`).

5. **Confirm impact.** Modified the request line to:
   ```
   GET /admin/delete?username=carlos HTTP/2
   Host: localhost
   ```
   Sent directly from Repeater — no browser interaction required. The request succeeded, deleting carlos's account and confirming full administrative write-access was obtainable purely through Host header manipulation.

## Proof of Concept

- `robots.txt` disclosing `/admin` as a restricted path.
- Direct `/admin` request returning the "local users only" rejection message, confirming origin-based (not credential-based) access control.
- `GET /admin` with `Host: localhost` returning the full admin panel HTML, including the user list and delete action URLs for `wiener` and `carlos`.
- `GET /admin/delete?username=carlos` with `Host: localhost` executing successfully, confirming write-level administrative capability was reachable via this bypass, not merely read access to the panel's existence.

*(Attach: robots.txt screenshot, rejected /admin screenshot, bypassed /admin panel screenshot showing user list, delete-request screenshot, lab-solved confirmation.)*

## Root Cause

The application's authorization logic for the admin interface checks the `Host` header against `localhost` (or an equivalent "internal" value) as a substitute for genuine network-level verification of request origin. The `Host` header is set entirely by the requesting client and carries no cryptographic or network-layer guarantee of actual origin — it is simply a string the server chooses to trust without any corroborating evidence (such as verifying the request arrived on an internal-only network interface, or validating a properly configured reverse-proxy-injected header that cannot be set by external clients).

## Impact

### Technical
- Complete bypass of administrative access control from any external, unauthenticated position — no credentials, session, or prior access of any kind required.
- Full read access to the admin interface's contents (user list) and full write access to its destructive actions (user deletion), confirmed via direct exploitation rather than access alone.
- Trivially reproducible with a single header change — no complex chaining, timing, or race conditions required.

### Business / Real-World
- This represents one of the most severe access-control failure patterns possible: an entire administrative surface, intended to be reachable only by trusted internal operators, is fully exposed to the public internet via a single, easily guessed header manipulation.
- Any administrative action exposed through this panel — not just user deletion, but potentially configuration changes, data exports, privilege grants, or further destructive operations — is equally exposed. The blast radius is bounded only by what the admin panel itself is capable of doing.
- This pattern (checking `Host` or a similar client-controlled header for "internal/trusted" status) is a well-documented, recurring real-world misconfiguration — not unique to lab environments — frequently found behind reverse proxies and load balancers that were intended to strip or override such headers but fail to do so correctly.

### Scope
Confirmed on the admin panel's index and delete-user action. In a real engagement, every action exposed through this same panel should be tested for the same bypass, and the same Host-based trust check should be tested against any other endpoint in the application that might apply similar "internal only" logic.

## Remediation

1. Never use a client-controllable header (`Host`, `X-Forwarded-For`, or similar) as the sole basis for determining trusted network origin. Internal-only access should be enforced at the network/infrastructure layer (firewall rules, network segmentation, mutual TLS, or a reverse proxy that strips/overwrites client-supplied headers before forwarding).
2. If a reverse proxy is relied upon to inject a trusted internal-origin header, ensure the proxy unconditionally overwrites any client-supplied value for that header name — never simply appending or trusting a pre-existing value.
3. Layer genuine authentication and authorization (role-based access control tied to an authenticated session) on top of any network-level restriction, rather than relying on network position as the sole control for sensitive administrative functionality.
4. Explicitly validate the `Host` header against a strict allowlist of expected production domain values for all requests, rejecting anything else outright — this would have independently prevented this specific bypass even if the "local user" logic remained flawed elsewhere.

## Lessons Learned & Patterns

- "Local" or "internal" access restrictions implemented by checking a client-supplied header value (rather than genuine network-layer verification) are a recurring, high-severity misconfiguration — always worth testing explicitly whenever an error message references origin-based restrictions ("local users only," "internal access only," "VPN required," etc.) rather than a credential/permission denial.
- The specific error message wording is a strong signal of the underlying authorization mechanism: a message about *who* you are (role/permission) suggests credential-based logic; a message about *where* you're connecting from suggests origin-based logic — the latter is a strong candidate for Host-header (or similar header) manipulation.
- `robots.txt` remains a reliable, low-effort recon step for discovering unlinked but existing sensitive paths — disallowing a path from search indexing is not the same as restricting access to it.
- When the simple `Host: localhost` check doesn't work on a target, the same underlying vulnerability class can still exist via a different trusted header (`X-Forwarded-For`, `X-Real-IP`, `X-Originating-IP`, or a custom proxy-injected header) — an HTTP `TRACE` request can sometimes reveal headers silently added by middleware before reaching the backend, exposing which header name is actually being trusted.

## References

- PortSwigger Lab: Host header authentication bypass
- PortSwigger Web Security Academy: HTTP Host header attacks — https://portswigger.net/web-security/host-header

**Tags:** #PortSwigger #HostHeaderAttack #AccessControlBypass #AdminPanel #BrokenAccessControl