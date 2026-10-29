**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-07-27

**Difficulty:** Practitioner 

**Severity:** 7.5 (High)

## Summary

A non-standard http header allows an unauthenticated attacker to bypass the server side proxy’s access control by deleting a user in an admin’s path.

## Affected Component

`POST ?username=carlos HTTP/2`

## Steps to Reproduce

1. Confirm direct access to `/admin` is blocked by the front-end/proxy.
2. In Repeater, send a request with the starting line: `POST ?username=carlos HTTP/2`
3. Add the header on the next line: `X-Original-Url: /admin/delete`
4. Send the request. A `302` response confirms the bypass succeeded and the user was deleted.

### **Proof of Concept**

Starting line : `POST ?username=carlos HTTP/2`

Header : `X-Original-Url: /admin/delete`

## Root Cause

The reverse proxy enforces access control based on the URL path in the request line, while the backend determines actual routing using the `X-Original-Url` header when present. This creates a discrepancy: the proxy evaluates one path (which appears permitted) while the backend serves an entirely different, restricted path — allowing the proxy's access control to be bypassed entirely.

**Impact:**

- Technical: An unauthenticated attacker can bypass proxy-enforced access control using a crafted `X-Original-Url` header, reaching backend-only administrative functionality — including deleting arbitrary user accounts — without any valid credentials.
- Business/Real-World: Complete compromise of account integrity; any external, unauthenticated party can delete customer accounts at will, with direct data-loss and trust consequences.
- Scope: Every user account on the platform; requires zero authentication and zero prior access — the lowest possible barrier to exploitation.

## Remediation

Enforce authorization in the same layer that performs routing, rather than relying on a separate proxy to gatekeep access to a path that the backend can be redirected away from via headers. Do not trust client-supplied routing headers (`X-Original-Url` and similar) for access-control decisions — strip or ignore them at the trust boundary before requests reach the backend.

### Lessons Learned:

- Key pattern: When a proxy and backend disagree about which URL a request actually targets — especially via headers like `X-Original-Url`, `X-Rewrite-Url`, or `X-Forwarded-*` — access control enforced only at the proxy layer can be bypassed entirely.
- Wrong hypothesis, worth keeping: adding the header alone (`X-Original-Url: /admin`) without correctly separating the query string produced a 200 in Repeater but didn't actually reproduce the exploit — the precise combination (empty path + query in the request line, target path in the header) was required.
- General takeaway: Authorization must be enforced at the same layer that ultimately decides what gets served. Any split between "who checks access" and "who actually routes" is a potential bypass surface.

**Tags:** #PortSwigger 
>
