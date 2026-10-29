**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-08-21

**Difficulty:** Practitioner 

**Severity:** High — CWE-862 – Missing Authorization

## Summary

The application protects certain admin functionality by checking the `Referer` header instead of properly verifying the user's role. By forging the `Referer` header, a low-privilege user can perform administrative actions.

## Affected Component

`GET /admin-roles?username=wiener&action=upgrade HTTP/2`

`Referer: https://0aee00820423ca7d8018994500a000e9.web-security-academy.net/admin`

## Steps to Reproduce

1. Log in as `administrator:admin` and go to the Admin panel.
2. Upgrade any user (e.g. carlos) and capture the request in Burp Suite.
3. Observe that the request contains a `Referer` header pointing to `/admin`.
4. Log out and log in as `wiener:peter`.
5. Take the previously captured request and:
    - Replace the session cookie with wiener’s session cookie
    - Change the `username` parameter to `wiener`
    - Keep the `Referer` header as `https://<lab-id>.web-security-academy.net/admin`
6. Send the request.
7. Refresh the page — wiener is now an administrator.

### **Proof of Concept**

```objectivec
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: <lab_ID>.web-security-academy.net
Cookie: session=<Wiener's session cookie>

Referer: https://<lab_ID>.web-security-academy.net/admin
```

## Root Cause

The application trusts the Referer header to decide whether a user is allowed to perform administrative actions, instead of properly checking the user's actual role or permissions.

## Impact

- **Technical:**
- **Business / Real-World:**
- **Scope:**

## Remediation

- Never rely on the Referer header for access control decisions.
- Always verify the user’s actual role and permissions on the server side for every sensitive action.

## Lessons Learned & Patterns

- Access control decisions should never be based on client-controlled headers (Referer, X-Original-URL, etc.).
- Always test sensitive endpoints by forging the Referer header when access is restricted.
- Multi-step or “sub-page” admin functionality is a common place for this type of flaw.

**Tags:** #PortSwigger #AccessControl #BrokenAccessControl #PrivilegeEscalation
