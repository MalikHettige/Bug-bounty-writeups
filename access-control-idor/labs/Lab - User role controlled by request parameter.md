**Lab:** PortSwigger Web Security Academy -https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter

**Date Solved:** 2026-07-23

**Difficulty:** Apprentice 

**Severity:** 8.1 (High)

## Summary

The application determines administrator privileges by reading a role value directly from a client-accessible cookie, rather than maintaining it as private server-side session state. As a result, any authenticated user can modify this cookie value via browser developer tools, granting themselves full administrator access with no legitimate authorization.

## Affected Component

`https://0a8100020418cb94807cb7d000b2009b.web-security-academy.net/admin`

## Steps to Reproduce

1. Get authenticated
- Click my account on top right
- Log in with credentials (wiener: peter)
1. Capture the request `GET /my-account?id=wiener HTTP/2`
2. Send to repeater (Ctrl + R)
3. Locate the parameter `adnmin` 

Observe that the parameter shows even when the attacker is not logged in as admin

1. Modify the value of it by replacing `false`with `true`
2. Hit enter and search “admin” in the response

Observe that in the repeater, the server trusts that modification!

1. Go back to the application — notice it didn't change anything
2. Go to dev tools (Ctrl + Shift + I) — go to applications tab>cookies section
3. Locate the value column and modify it by replacing false with true
4. Hit enter and refresh the page

Observe that the admin panel appeared 

1. Click admin panel 
2. Delete carlos 

## **Proof of Concept**

<img width="723" height="152" alt="image" src="https://github.com/user-attachments/assets/83370c28-6982-44e4-b196-e93119ca955e" />

<img width="1916" height="773" alt="image" src="https://github.com/user-attachments/assets/12afc8e6-e1d6-4c62-8b67-b4d965e82ae8" />

## Root Cause

The application evaluates admin status by reading a role value stored directly in a cookie, instead of looking up the user's role from server-side session state tied to an opaque session identifier. Because the cookie's contents are fully client-controlled, any user can edit it directly and the server accepts the modified value without independent verification.

**Impact:**

- **Technical:** Any authenticated, non-privileged user can escalate to full administrator privileges by editing a single cookie value in browser dev tools, gaining access to the admin panel and its functions, including deleting other users.
- **Business/Real-World:** Complete failure of role separation — any ordinary account can perform destructive administrative actions, risking data loss, unauthorized account deletion, and loss of trust in the platform's access controls.
- **Scope:** Every authenticated user account; requires no technical sophistication beyond opening browser developer tools.

## Remediation

Never store authorization-relevant data (such as role) in any client-readable or client-modifiable location, including cookies. Maintain role state exclusively server-side, tied to an opaque session identifier, and verify the user's actual role via server-side lookup on every privileged request rather than trusting any value supplied by the client.

## References

- PortSwigger Web Security Academy – Access Control — Overview of access control vulnerabilities, including vertical and horizontal privilege escalation.
- PortSwigger Lab – User role controlled by request parameter — Official lab and solution demonstrating privilege escalation through client-controlled role parameters.
- OWASP Authorization Cheat Sheet — Best practices for server-side authorization and avoiding client-side trust.
- OWASP Web Security Testing Guide – Authorization Testing — Practical methodology for identifying and testing authorization flaws.
- OWASP Top 10 2021 – Broken Access Control — Background on why broken access control is the most critical web application security risk.

### Further Reading

- OWASP ASVS – Access Control (V4)
- PortSwigger – Access Control Vulnerabilities Explained

## Lessons Learned & Patterns

- It is essential for both cookie section in dev tools and admin parameter in request to be modified in order to for admin panel feature to be emerged.
- `GET /my-account?id=wiener HTTP/2`request is suitable for parameter modification
- The dev tools and request server are the only 2 that verifies the user
- General takeaway: different applications genuinely implement authentication/authorization differently, and "trusting a client-supplied value instead of verifying server-side" is a recurring anti-pattern, not a one-off.

**Tags:** #PortSwigger #access control
