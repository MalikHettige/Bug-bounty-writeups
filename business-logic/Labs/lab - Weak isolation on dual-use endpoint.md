# Weak isolation on dual-use endpoint

**Header block:**
- Platform: PortSwigger Web Security Academy
- Category: Business Logic
- Difficulty: Practitioner
- Date Solved: 23-09-2026
- Severity: **8.1 (High)** — `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`. Reasoning: network-reachable, trivial once known (AC:L), requires *some* authenticated session but not privilege (PR:L — needed to be logged in as wiener, any low-priv account works), no victim interaction, stays within the app's own authority (S:U), full account compromise including admin's data (C:H), full ability to take over any account including admin (I:H), no direct availability impact (A:N).

**Affected Component:** 
`POST /my-account/change-password`

**Root Cause — bullets to draft from:**
- The endpoint performs two logically separate checks that were never actually bound together: (1) does the supplied `current-password` match, (2) which account (`username` parameter) gets modified
- Removing the `current-password` parameter entirely causes check (1) to be skipped rather than fail safely — a "fail open" instead of "fail closed" bug
- The `username` parameter is trusted at face value to determine the target account, independent of the actual logged-in session
- Net effect: the endpoint conflates "prove you own this account" with "you supplied the right old password" — and since those two things are separately client-controlled, removing one defeats the other

**Steps to Reproduce — bullets:**
1. Log in as `wiener:peter`, go to My Account, initiate a password change, capture the request in Burp
2. In Repeater, delete the `current-password` parameter entirely (not blank it) and resend — password changes successfully with no old password required
3. Set `username=administrator`, keep `current-password` removed, choose a new password, send
4. Log out, log back in as `administrator` using the password you just set
5. Navigate to the admin panel, delete `carlos` to confirm full takeover

**POC**
The modified body of `POST /login HTTP/2` request
```ocaml
csrf=[REDACTED]&username=administrator&password=mal
```

<img width="1919" height="768" alt="image" src="https://github.com/user-attachments/assets/c3fb63d0-7e65-4702-9d91-c0acaccfe271" />

**Impact — bullets:**
- Technical: complete account takeover of any user, including admin, requiring only knowledge of the target's username — no valid password, reset token, or admin access needed
- Business/Real-World: full authentication bypass for any account; an attacker can lock out legitimate users, access sensitive account data, and gain full administrative control of the application
- Scope: every account in the application, admin included; the only precondition is holding any authenticated low-privilege session and knowing the target's username (often guessable or enumerable)

**Remediation — bullets:**
- Never determine the target account from a client-supplied `username` parameter on a self-service endpoint — derive it from the authenticated session instead
- Treat a missing `current-password` as a hard rejection, not a bypassable/optional check
- Require re-authentication (step-up auth) for sensitive account-modifying actions regardless of which parameters are present in the request

**Lessons Learned — bullets:**
- Dual-use / multi-function endpoints are worth testing by *removing* individual parameters, not just altering their values — missing-parameter behavior (fail open vs. fail closed) is a first-class test case for any state-changing endpoint
- Any parameter identifying "whose data this affects" must never be trusted independently of session identity when the action is meant to be self-service only

**References:**
- PortSwigger Lab: https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint
- CWE-620: Unverified Password Change — maps precisely to this root cause (app fails to verify the user knows the original password before setting a new one)

**Tags:** `#PortSwigger #BusinessLogic #AccountTakeover #BrokenAuthentication`
