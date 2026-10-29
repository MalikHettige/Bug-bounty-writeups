**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-08-23

**Difficulty:** Apprentice 

**Severity:** 8.1 (High)

## Summary
The application fails to properly implement or enforce server-side authorization checks and exposes the location of a restricted administrator endpoint within leaked information in homepage source code 

## Affected Component

`https://0a4b00f303a64b6e81abd93800d50072.web-security-academy.net/admin-q9kn79`

## Steps to Reproduce

1. Right click and view the home-page source
2. Press CTRL+ F to find and search “admin” 

look for a script reference containing the hidden admin path, observe this would mean the script is leaked from back-end hence

3. Locate the ‘href’ tag and copy its value
   
Example: <a href="/[random string]">

4. Append the path to the application's base URL
5. Delete carlos and solve the lab

**Proof of Concept**

<img width="775" height="259" alt="image" src="https://github.com/user-attachments/assets/7e69ca37-5f30-439e-acaa-4863fa1e216b" />

Homepage source → leaked admin path → accessible administrator panel


## Root Cause
The application relies on the secrecy of the administrator endpoint URL instead of implementing proper authorization controls. Although the administrative location is not directly linked in the interface, the endpoint remains accessible because the server does not verify whether the requesting user has administrative privileges.
Sensitive functionality should never depend on hidden URLs as a security mechanism.

## Impact

- **Technical:** Any user with can potentially access restricted endpoints, discover hidden administrator-specific functionalities.
- **Business / Real-World:** Such successful exploitations could allow attackers to take authorized administrative actions, delete or altar accounts and could even lead to integrity and availibility issues.
- **Scope:** The vulnerability effects any restricted endpoints like administrative path where the URL is exposed through client-side resources without server-side authorization checks.

## Remediation

Implement server-side authorization checks to every admin functionality endpoints and verify the authenticated users privilege level or role on every request before granting access to such locations.Do not rely on path obscurity as a security boundary.

## References

- PortSwigger Web Security Academy — Access Control
- Broken access control theory, vertical privilege escalation, and authorization testing.
- OWASP Web Security Testing Guide — Authorization Testing
- Testing methodology for access control weaknesses.
- OWASP Authorization Cheat Sheet
- Recommended authorization implementation practices.
- OWASP Top 10: A01 Broken Access Control
- Common access control failures and prevention techniques.

## Lessons Learned & Patterns

- During testing always try to inspect the page source code, JS files, crouwler locations like robots.txt and client side routes because some sensitive paths can often be discovered through publicly accessible resources.
- General takeaway:Administrative endpoints should never be considered secure because they are hidden.

## Personal Learning Note

I initially overlooked this pattern because I was not familiar enough with reading scripts. The key lesson is not to become a full developer immediately, but to understand enough JavaScript/Python/backend code patterns to recognize:

- Endpoint references
- API routes
- Authentication logic
- Authorization checks
- Hidden functionality

For bug bounty, code-reading ability is a force multiplier because many vulnerabilities are discovered through understanding how applications expose functionality...

#PortSwigger #BrokenAccessControl #VerticalPrivilegeEscalation #CWE862 #WebSecurity
