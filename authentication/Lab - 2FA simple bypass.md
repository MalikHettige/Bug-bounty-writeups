**Lab:** PortSwigger Web Security Academy

[Lab: 2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)

This lab's two-factor authentication can be bypassed. You have already obtained a valid username and password, but do not have access to the user's 2FA verification code. To solve the lab, access Carlos's account page.

**Date Solved:** 2026-08-21

**Difficulty:** Apprentice 

**Severity:** 8.1 (High) — CWE-306-adjacent for the missing server-side check on the second factor.

## Summary

The application's two-factor authentication can be fully bypassed by navigating directly to a protected page after completing only the first authentication factor. Because the server never verifies that a session has actually passed 2FA before serving sensitive content, an attacker holding valid credentials for a victim account — but not their 2FA code — can access that account in full.

## Affected Component

`https://<LAB_ID>.web-security-academy.net/my-account`

## Steps to Reproduce

1. Log in with Carlos's valid credentials (`carlos:montoya`)
2. Observe that the application redirects to the 2FA challenge page (`/login2`) without yet granting access to protected resources
3. In the address bar, replace `/login2` with `/my-account`
4. Observe the request succeeds — Carlos's account page loads in full, without ever submitting a 2FA code

### **Proof of Concept**

The request with the modified URL

```objectivec
GET /my-account HTTP/2
Host: <Lab_ID>.web-security-academy.net
Cookie: session=<My_session>
```
The following image shows the unanswered code prompt, and that it loaded `/my-account` page showing carlos's actual account data.

<img width="1460" height="736" alt="image" src="https://github.com/user-attachments/assets/297793c8-3d40-42df-87c3-1dc7be4a8c0a" />


**Note**

This endpoint did not enforce a Referer check. Worth stating explicitly: even if one had been present, it wouldn't have been an effective control — Referer is a client-controlled header, freely set to any value in Repeater 

```nix
Referer: https://<host>/login2
```

Its absence here isn't the vulnerability; it's mentioned only to preempt the question of whether a superficial header check would have stopped this.

## Root Cause

After username/password submission, the server immediately establishes an authenticated session tied to that user's identity, before the second factor has been verified. Protected endpoints such as `/my-account` check only whether *a* valid session exists — not whether that session has completed 2FA. The 2FA challenge is enforced entirely by the client-side redirect to `/login2`; no server-side state ("has this session passed 2FA?") is ever checked on subsequent requests.

### **Impact**

**Technical:** An attacker who has obtained valid credentials for a victim (phishing, credential stuffing, breach dump, or any other means) but lacks access to their 2FA device or inbox can still reach full session-level access to that account — completely defeating the purpose of the second factor.

**Business / Real-World:** This collapses two-factor authentication down to effectively single-factor protection. Any leaked or reused password becomes immediately exploitable for full account takeover, since the second factor adds no real barrier. On a financial, healthcare, or admin-facing application, this could mean fraudulent transactions, exposed personal data, or unauthorized privileged actions — all performed as the legitimate user.

**Scope:** Confined to the compromised account's own data and permissions; doesn't extend to underlying infrastructure. It is, however, trivially repeatable against any account whose password leaks, which is the entire point 2FA is supposed to guard against.

## Remediation

Track 2FA completion server-side as part of session state (e.g., a flag such as `mfa_verified=true`, set only after successful code validation). Every protected endpoint must check this flag before returning sensitive content, regardless of how the request arrived. The redirect to `/login2` should be a UI convenience for legitimate users — never the sole enforcement mechanism.

## Lessons Learned & Patterns

- **General takeaway:** Multi-step processes — login → 2FA, or admin action → confirm — are frequently enforced only by UI routing, never by a server-side check re-verified at each step. The fix pattern is always the same: bind a durable, server-tracked flag to the session, and check it at every sensitive endpoint, never trusting that a user could only have arrived via the "intended" path. Standing rule going forward: on any gated or multi-step flow, try navigating straight to the target resource *before* testing anything more elaborate.

**References**

- PortSwigger, "Lab: 2FA simple bypass" — https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass
- PortSwigger, "Authentication vulnerabilities" — https://portswigger.net/web-security/authentication
- CWE-304: Missing Critical Step in Authentication — https://cwe.mitre.org/data/definitions/304.html
- CWE-287: Improper Authentication — https://cwe.mitre.org/data/definitions/287.html
- OWASP Web Security Testing Guide — https://owasp.org/www-project-web-security-testing-guide/

**Tags:** #PortSwigger
