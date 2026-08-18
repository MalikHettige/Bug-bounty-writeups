**Lab:** PortSwigger Web Security Academy 

https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter

**Date Solved:** 2026-08-17

**Difficulty:** Apprentice 

**Severity:** CVSS: 6.5 (Medium)

## Summary

The server fails to enforce authorization on the `id` parameter, allowing an authenticated user to access another user's account information and API key by modifying the parameter value.

## Affected Component

`GET /my-account?id=carlos HTTP/2`

## Steps to Reproduce

1. Click ‘My Account’ to log in (`wiener:peter`)
2. Input credentials and hit submit

Observe that it shows API key of the authenticated user

1. Go to HTTP history in proxy panel in Burp
2. Locate the affected endpoint request
3. Send to repeater
4. In the starting line, modify the value of id parameter with the victim’s
5. Send the request (Ctrl+Space)
6. Notice it returned as 200 OK — meaning the server allowed the modified request
7. Click the search box below response pane and type “API” 
8. Copy the key, submit and solve the lab

**Proof of Concept**

<img width="595" height="78" alt="image" src="https://github.com/user-attachments/assets/99887425-d58f-4aa7-9706-844389bfbb06" />


The modified request

`GET /my-account?id=carlos HTTP/2
Host: 0a7d00b7034cbba1817f16d1007e00b4.web-security-academy.net
Cookie: session=y21h0lgVsusYYBW9Z2mNJEe5Ju7cNgke`

The response returned Carlos's account information, including his API key, despite the request being authenticated as Wiener.

## Root Cause

The server relies on the client-supplied `id` parameter to determine which user's account data is returned, without verifying that the authenticated user is authorized to access that account.

## Impact

- **Technical:** An authenticated attacker can modify the `id` parameter to access another user's account information and API key.
- **Business / Real-World:** This could expose sensitive account credentials or account-related information belonging to other users, potentially enabling further unauthorized actions depending on how the exposed API key can be used.
- **Scope:** Potentially affects any user whose identifier can be supplied through the vulnerable endpoint.

## Remediation

Implement server-side authorization checks for the requested user ID. The application should verify that the authenticated session is authorized to access the requested account before returning its data. Never rely solely on a client-controlled identifier for authorization decisions.

## Lessons Learned & Patterns

- **General takeaway:** A user-controlled identifier should never be trusted as proof that the authenticated user is authorized to access that resource.
- **Testing pattern:** When an endpoint contains parameters such as `id`, `user_id`, `account_id`, `profile_id`, or similar identifiers, test whether changing the value allows access to another user's object.
- **Key distinction:** Authentication answers **"Who are you?"** while authorization answers **"Are you allowed to access this?"**

**Tags:** IDOR · Broken Access Control · Authorization · Access Control · Web Security
