**Platform:** PortSwigger Web Security Academy

**Lab**: Method-based access control can be circumvented
**Date Solved:** 2026-08-03
**Difficulty:** Practitioner
**Severity:** 8.1 (High)

### Summary

The application implements access control only on the POST method for the privileged action of upgrading a user to admin. By changing the HTTP method to GET, an attacker can successfully perform the same privileged action.

### Affected Component

`GET /admin-roles?username=wiener&action=upgrade`

(This is originally intended to be restricted to authenticated administrators via POST)

### Steps to Reproduce

1. Log in as the administrator (`administrator:admin`).
2. Navigate to the admin panel and promote a user by clicking the “Upgrade” button 
3. In Burp Suite → HTTP history, locate the POST request
    
    ```
    POST /admin-roles HTTP/2
    ...
    username=wiener&action=upgrade
    ```
    
4. Send that request to Repeater (Ctrl + R).
5. Open a private browser window, log in as the low-privileged user (`wiener:peter`).
6. Capture any request with that session and copy the full Cookie header value.
7. Back to repeater (Ctrl + Shift + R), replace the administrator’s cookie with the low-privileged user’s cookie.
8. Send the request 

Observe it shows “Unauthorized” in the response panel because the access control is working as intended — that is when changing the request method is needed to convert from POST to GET.

1. Right-click the request and click Change request method.
2. Send the request again (Ctrl + space).
3. The response is successful and the lab is solved (user wiener is now an administrator).

### Root Cause

The server-side authorization check was implemented only for the POST method, but the same endpoint and parameters were reachable via GET, and no method-agnostic authorization middleware or framework-level access control was enforced. The application trusted the presence of the parameters (username + action=upgrade) without verifying that the request came through the intended HTTP method or that the authenticated user possessed the required role.

### Impact

**Technical:**

- Horizontal + vertical privilege escalation — Any authenticated low-privileged user can promote themselves or any other user to administrator by simply changing the HTTP method.

**Business / Real-World:**

- Complete account takeover of administrative functions.
- In a real application this could lead to full system compromise, data exfiltration, modification of user roles, deletion of accounts, or further lateral movement.
- Particularly dangerous in multi-user systems (SaaS, admin panels, healthcare, e-commerce, etc.) where role separation is critical.

**Scope:**

- Affects every user who has a valid session.
- Requires only knowledge of the endpoint and the ability to change the HTTP method (trivial with any intercepting proxy).

### Remediation

1. Enforce authorization checks independently of the HTTP method (prefer a centralized middleware or framework decorator/annotation that runs for every request).
2. Explicitly reject unexpected HTTP methods on sensitive endpoints (return 405 Method Not Allowed).
3. Prefer using the same HTTP method consistently and avoid accepting privileged actions via GET.
4. Implement role-based access control (RBAC) that is evaluated after authentication, regardless of method.
5. Add automated tests that verify privileged endpoints reject requests from low-privileged users across all supported HTTP methods.

### Lessons Learned & Patterns

- **General takeaway:** Never rely on the HTTP method as a security boundary. Access control must be enforced on the server side for every request that reaches a privileged action, irrespective of GET, POST, PUT, DELETE, etc.
- Classic “method-based access control” flaw — frequently appears when developers protect only the form submission (POST) and forget that the same parameters can be sent via other methods.
- Always test privileged endpoints with:
    - Cookie / session of a lower-privileged user
    - HTTP method changes (POST ↔ GET, PUT, etc.)
    - Parameter pollution and alternative content types
- This pattern is especially common in older frameworks or custom admin panels where method routing and authorization are handled separately.

**Tags:** #PortSwigger #AccessControl #BrokenAccessControl #HTTPMethod #PrivilegeEscalation #WebSecurityAcademy
