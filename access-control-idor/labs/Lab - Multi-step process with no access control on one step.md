**Lab:** PortSwigger Web Security Academy

This lab has an admin panel with a flawed multi-step process for changing a user's role. I can familiarize myself by accessing the admin panel by logging in using the credentials `administrator:admin`.

https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step

**Date Solved:** 2026-08-21

**Difficulty:** Practitioner 

**Severity:** **8.0–8.1, High** — CWE-862: Missing Authorization

## Summary

The application implements a multi-step process for changing a user’s role. While the initial step is protected, the final confirmation endpoint (POST /admin-roles) lacks proper access control. An authenticated low-privilege user can directly call this endpoint and escalate their privileges to administrator.

## Affected Component

`POST /admin-roles HTTP/2`

## Steps to Reproduce

1. Navigate to My account and log in as `wiener`
2. Find the `GET /my-account?id=wiener HTTP/2`request and copy `wiener`’s session ID
3. Log out and log in as the admin 
4. Click admin panel on top-right and upgrade a non-admin user
5. Find that `POST /admin-roles HTTP/`and send it to repeater

That request must have these parameters at the bottom

```jsx
action=upgrade&confirmed=true&username=<non admin username>
```

1.  Replace admin’s session ID with wiener’s and replace that non admin’s username with `wiener`
2. Send the request — Refresh the page and solve the lab

### **Proof of Concept**

Request after admin’s cookie was modified

```objectivec
POST /admin-roles HTTP/2
Host: <LAB_ID>.web-security-academy.net
Cookie: session=<wiener_session_cookie>
Content-Type: application/x-www-form-urlencoded

action=upgrade&confirmed=true&username=wiener
```

## Root Cause

Access control is only enforced on the first step of the role-change workflow. The final confirmation endpoint does not verify whether the current user has administrative privileges. It only requires the user to be authenticated.

## Impact

- Any authenticated user can escalate their privileges to administrator.
- Full control over administrative functions becomes possible.
- In a real-world application, this could lead to complete compromise of the admin panel and sensitive operations.

## Remediation

- Enforce authorization checks on **every** step of multi-step sensitive processes.
- Verify the user’s role/permissions on the final confirmation endpoint, not only on the initial request.
- Consider using server-side state or short-lived tokens tied to the administrative session instead of relying solely on client-supplied parameters.

## Lessons Learned & Patterns

Multi-step processes are a frequent source of broken access control issues. Developers often protect the first page or form but forget to re-validate permissions on the final action endpoint (especially endpoints containing parameters like confirmed=true, action=upgrade, etc.).

**Pattern to watch for:**
Any workflow involving confirmation steps for sensitive actions (role changes, deletions, transfers, privilege upgrades, etc.).

## References

- https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control-on-one-step
- CWE-862: Missing Authorization

**Tags:** #PortSwigger
