**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-07-27

**Difficulty:** Apprentice 

**Severity:** 8.1 (High)

## Summary

The application allows any authenticated user to modify the roleID by placing a crafted jSON in the `my-account/change-email`endpoint and gives access to access admin panel and perform user deletion.

## Affected Component

URL — `https://0a91006a0360875880a0218d008600c8.web-security-academy.net/admin`

Request endpoint — `POST /my-account/change-email HTTP/2`

## Steps to Reproduce

1. Click ‘my account’ and log in (wiener:peter)
2. Try updating the email with an arbitrary string 

 make sure to include `@` and a domain like `.net` or `.com`

1. Click update email and locate the `POST /my-account/change-email HTTP/2`request

Observe that the `RoleID`parameter shows in the responses and results 1

1. Replace the current jSON with the following payload
2. Hit enter and notice the response shows 2 in the roleid parameter
3. In the application, go to admin panel and delete carlos

**Proof of Concept**

<aside>
💡

`{`

`"email": "test@test.net",
"roleid":2`

`}`

</aside>

## Root Cause

The `/my-account/change-email` endpoint accepts and applies any field present in the JSON request body, including `roleid`, rather than restricting processing to only the intended `email` field. This is a mass assignment vulnerability — the server trusts client-supplied fields it never explicitly asked for, allowing any authenticated user to escalate their own privilege by including an unauthorized field in an otherwise unrelated request.

## Impact

- **Technical:** The attacker can access hidden admin-specific endpoints.
- **Business / Real-World:** The attacker can delete, upgrade or even downgrade any user from the application leading the customers to lose reliability of the security of application.
- Scope: Every authenticated user account; no elevated starting privilege required — any standard registered account can self-escalate to administrator.

## Remediation

Implement server-side allowlisting on the `/my-account/change-email` endpoint so only the `email` field is processed; any unexpected field (such as `roleid`) should be explicitly rejected or ignored. Privilege/role changes must only occur through a dedicated, separately-authorized endpoint that independently verifies the requester holds sufficient privilege before applying the change.

## Lessons Learned & Patterns

- General takeaway: Any endpoint accepting a JSON body should be tested for mass assignment — try adding fields beyond what the UI exposes (role, privilege, price, ownership IDs) to see if the backend blindly applies them.
- (keep your existing bullet about extending JSON with a comma — that's a solid practical technique note)

**Tags:** #PortSwigger #AccessControl #ProxyBypass #URLRouting

---
