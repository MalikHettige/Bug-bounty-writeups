**Platform:** PortSwigger Web Security Academy

**Category:** Authentication 

**Difficulty:** Practitioner 

**Date Solved:** 2026-09-17

**Severity:** 5.3 (Medium)

## Summary

The application is vulnerable to username enumeration due to a logic flaw in its account lockout mechanism. When multiple failed login attempts are made against a valid username, the application returns a distinct lockout message (“You have made too many incorrect login attempts”). Invalid usernames always receive the generic response “Invalid username or password” and never trigger the lockout. This behavioral difference allows an attacker to reliably identify valid usernames, which can then be targeted for password brute-force attacks.

## Affected Component

```powershell
https://[LAB-ID].web-security-academy.net/login
```

## Steps to Reproduce

1. Go straight to Git bash and paste the [username enumeration python script](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Username%20enumeration%20via%20account%20lock/username-enumeration.py)

**Result:** Valid username identified → arlington

> **Note:** Alternatives such as Burp Intruder (Cluster bomb + 5 null payloads) or ffuf with a repeated wordlist can also be used. Burp Community is significantly slower.
> 
2. After waiting for the account lock to expire (~60 seconds), brute force the password against the valid username by running the [password script](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Username%20enumeration%20via%20account%20lock/password-enumeration.py) 
3. Logged in with the discovered credentials (`arlington:qwerty`) and accessed the account page to solve the lab.

## Proof of Concept

## Root Cause
<img width="774" height="469" alt="image" src="https://github.com/user-attachments/assets/0a56388b-cf95-4430-899e-2625ec27125b" />

<img width="1919" height="798" alt="image" src="https://github.com/user-attachments/assets/6a133355-9f58-47b4-a9d4-c2ed178038ec" />

## Remediation

- **Return identical responses** for both valid and invalid usernames on failed login attempts (e.g., always show “Invalid username or password”).
- **Apply rate limiting / lockout at the IP or session level**, not only per username.
- **Implement consistent timing** so response times do not differ between valid and invalid users.
- **Add additional protections**:
    1. CAPTCHA or progressive delays after several failures
    2. Multi-factor authentication (MFA)
    3. Account lockout notifications to the real user
- **Avoid leaking account existence** in any authentication-related feature (login, password reset, registration, etc.).

### Impact

**Technical Impact**

- Allows reliable enumeration of valid usernames
- Significantly increases success rate of password spraying / brute-force attacks
- Enables targeted attacks against specific users
- Can be chained with other authentication weaknesses

**Business / Real-World Impact**

- Facilitates credential stuffing and password spraying campaigns
- Increases risk of account takeover
- Can lead to data breaches, fraud, or lateral movement
- Damages user trust if accounts are compromised
- May violate privacy regulations if usernames/emails are sensitive

**Scope**

- Affects the authentication mechanism (login endpoint)
- Unauthenticated attacker
- Impacts all users of the application
- Can be performed remotely over the network

## Lessons Learned & Patterns

- Account lockout is not a security control by itself if it behaves differently for valid vs invalid users.
- Any observable difference (message, length, status code, timing, headers) can become an enumeration oracle.
- Always test authentication responses under both valid and invalid conditions.
- Lockout mechanisms should be applied consistently (or better: use generic responses + proper rate limiting + CAPTCHA/MFA).
- False positives are common when success detection is weak — always look for strong indicators (302 redirect is usually best).

## References

**Official / Standards**

- CWE-204: Observable Response Discrepancy
- CWE-203: Observable Discrepancy
- OWASP Testing Guide - Testing for Account Enumeration (WSTG-IDNT-04)
- OWASP Top 10 2021 - A07 Identification and Authentication Failures

**PortSwigger**

- Lab: Username enumeration via account lock
- PortSwigger Web Security Academy - Authentication

**Additional Good Sources**

- ZAP Alert - Possible Username Enumeration
- OWASP Cornucopia - Authentication AT4

**Tags:** #PortSwigger #IDOR #AccessControl
