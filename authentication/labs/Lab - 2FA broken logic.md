**Lab:** 2FA broken logic 2FA broken logic

This lab's **two-factor authentication** is vulnerable due to its flawed logic. To solve the lab, access Carlos's account page.

**Goal:** Bypass the 2FA and log in as carlos.

**Date Solved:** 2026-08-25

**Difficulty:** Practitioner 

**Severity**: High (8.1)

**CWE:** CWE-287 – Improper Authentication / CWE-639 – Authorization Bypass Through User-Controlled Key

## Summary

The two-factor authentication mechanism relies on a client-controlled verify cookie to determine which user’s 2FA code is being validated. An attacker can change this cookie to a victim’s username (carlos), generate a 2FA code for that account, and brute-force the 4-digit code, completely bypassing the password requirement.

## Affected Component

```nix
POST /login2
Cookie: verify=carlos
```

## Steps to Reproduce

1. Log in with valid credentials (`wiener:peter`) and reach the 2FA page.
2. Observe that a verify cookie is set to the current username.
3. Send a request to `/login2` with the cookie `verify=carlos` to generate a 2FA code for Carlos.
4. Brute-force the `mfa-code` parameter (0000–9999) while keeping `verify=carlos.`
5. When a 302 response is received, load the response in the browser and access **My account**.

### **Proof of Concept**

A **Python script** is provided to reliably reproduce the issue : 2fa_broken_logic.py

1. Log in with any valid account and copy the session cookie.
2. Update the `LAB_URL` and `SESSION_COOKIE` variables in the script.
3. Run the script:Bash
    
    ```glsl
    python 2fa_broken_logic.py
    ```
    
4. The script will generate a 2FA code for the victim and brute-force it.
5. Once a 302 response is received, the attacker is authenticated as the victim.

**Note on tooling choice:** OWASP ZAP's Fuzzer was considered for the 4-digit code brute-force step, but a custom Python script was used instead. This lab requires up to 10,000 sequential requests with an early-exit condition — a scripting problem more than a GUI-fuzzing one. ZAP (and Burp's free-tier Intruder) both apply meaningful per-request throttling that becomes the bottleneck at this volume, whereas a threaded Python script controls concurrency directly. The script's core logic mirrors the actual vulnerability: it issues a `GET /login2` with `verify=carlos` to generate a code for the target account using only the attacker's own valid session, then brute-forces `POST /login2` submissions until a `302` redirect confirms success.

## Root Cause

The application uses a client-controlled cookie (verify) to determine which user’s 2FA code should be validated. This value is not bound to the server-side session that completed the password authentication step. As a result, an attacker can set verify=carlos, force the generation of a 2FA code for the victim, and brute-force the code without ever knowing the victim’s password.

### Impact

- **Technical:** Complete bypass of 2FA and password authentication, leading to account takeover of any user.
- **Business / Real-World:** Any user account can be compromised without knowing the password or having access to the victim’s email/phone.
- **Scope:** All users of the application.

### Remediation

- Bind the 2FA verification to the server-side session that completed the password step.
- Never trust a client-controlled parameter (verify cookie) to determine the account being authenticated.
- Implement rate limiting and account lockout on the 2FA verification endpoint.

### Lessons Learned & Patterns

- Multi-factor authentication is only as strong as its weakest implementation detail.
- Always check whether the second factor is properly bound to the authenticated session rather than a client-side value.
- Client-controlled identifiers in authentication flows are a common source of broken authentication vulnerabilities.

### References

You can add these to your write-up:

- PortSwigger Web Security Academy – 2FA broken logic
- CWE-287: Improper Authentication
- CWE-639: Authorization Bypass Through User-Controlled Key
- OWASP Authentication Cheat Sheet
- PortSwigger – Multi-factor authentication vulnerabilities

**Tags:** #PortSwigger #Authentication #2FA #BrokenAuthentication #AccountTakeover #BruteForce
