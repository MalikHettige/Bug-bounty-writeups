**Lab:** PortSwigger Web Security Academy 

The lab: https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids

**Date Solved:** 2026-08-17

**Difficulty:** Apprentice

**Severity:** High — 8.1/10 (CVSS v3.1)

This lab has a horizontal privilege escalation vulnerability on the user account page, but identifies users with GUIDs.

Objective: find the GUID for `carlos`, then submit his API key as the solution.

## Summary

The application uses a user-controlled `id` parameter to identify the account whose information should be returned. Although user IDs are unpredictable, the application exposes Carlos's ID through the blog functionality. Because the `/my-account` endpoint does not properly verify that the requested account belongs to the authenticated user, an authenticated user can replace their own ID with Carlos's ID and access his account information and API key.

## Affected Component

`GET /my-account?id=b54aa220-73db-4217-aba7-725320fac49b HTTP/2`

## Steps to Reproduce

1. Log in as `wiener` using the credentials `wiener:peter`.
2. Navigate to the **My Account** page.
3. In **Burp Suite → Proxy → HTTP history**, locate the request:`GET /my-account?id=<Wiener's-ID>`
4. Send the request to **Repeater**.
5. Return to the homepage and browse the posts until a post authored by **carlos** is displayed.
6. Click Carlos's hyperlinked username.
7. In Burp's HTTP history, locate the resulting request:`GET /blogs?userId=<Carlos's-ID>`
8. Copy Carlos's `userId` value.
9. In Repeater, replace Wiener's `id` value with Carlos's `userId`.
10. Send the modified request.
11. Observe that the response contains Carlos's account information, including his API key.

**Proof of Concept**

Modified request : 

`GET /my-account?id=b54aa220-73db-4217-aba7-725320fac49b HTTP/2
Host: 0ae6006504ba55948084dfc600a200b4.web-security-academy.net
Cookie: session=ChYClJ59aFnz45tPqnAn7IyZL3peoHmv`

Response pane :

 `Your API Key is: bcKju7Ue6W1JHHxHeFBDSEq0MdPjKpOo`

## Root Cause

The application trusts the client-supplied `id` parameter without verifying that the authenticated user is authorized to access the requested account.

## Impact

- **Technical:** An authenticated attacker can manipulate the `id` parameter to access another user's account information. In this lab, this results in unauthorized disclosure of Carlos's API key.
- **Business / Real-World:** In a real application, this access-control flaw could expose sensitive user information or account-specific data belonging to other users, potentially leading to privacy violations, account compromise, or further unauthorized actions depending on the exposed functionality.
- **Scope:** The vulnerability affects **horizontal access control** between users. An attacker does not need administrative privileges; a normal authenticated account is sufficient to access resources belonging to another user.

## Remediation

The server should **enforce authorization based on the authenticated user's identity rather than trusting a client-supplied user ID**.

For example:

- Derive the current user's identity from the authenticated session.
- Verify that the requested resource belongs to that authenticated user before returning it.
- Deny the request if the user does not have permission to access the specified account.
- Do not rely on unpredictable IDs as an authorization mechanism. Random/UUID-style identifiers make enumeration harder but **do not replace authorization checks**.
- Apply the same authorization checks consistently across related endpoints.

## Lessons Learned & Patterns

- **Unpredictable IDs ≠ authorization:** UUIDs can still be abused if exposed.
- **Look for ID leaks:** Legitimate functionality may reveal otherwise hidden IDs.
- **Follow application relationships:** Posts → owners → user IDs → account endpoints.
- **Test authorization:** Verify whether your session can access another user's resources.
- **Prove impact:** Finding an ID isn't enough; demonstrate unauthorized access with it.

**Tags:** IDOR · Broken Access Control · Authorization · Access Control · Web Security
