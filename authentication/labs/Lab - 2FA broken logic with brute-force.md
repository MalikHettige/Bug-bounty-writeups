# 2FA Broken Logic

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-17  
**Severity:** Critical

## Summary

The application's 2FA implementation trusts a user-controlled `verify` cookie to determine whose account is being verified at the 2FA step. An attacker who completes Step 1 (password login) with their own account can manipulate the `verify` cookie to target any other user's account, then brute-force the 4-digit 2FA code (0000–9999, only 10,000 combinations). This bypasses 2FA entirely without knowing the victim's password, achieving full account takeover.

## Affected Component

`POST /login2` — the 2FA verification endpoint. Trusts the `verify` cookie value to identify whose 2FA session is active, without cryptographically binding it to the Step 1 authentication session.

## Root Cause

```
Secure 2FA flow:
Step 1 (password) → server creates session tied to verified user
Step 2 (2FA code) → server checks session → confirms same user → grants access

Vulnerable 2FA flow:
Step 1 (password) → server creates session
Step 2 (2FA code) → server reads verify=<cookie value> → TRUSTS IT BLINDLY
                    attacker sets verify=carlos → server checks carlos's 2FA
```

The server decouples the 2FA verification from the Step 1 authentication. The `verify` cookie is user-controlled and unauthenticated — anyone can set it to any username.

## Steps to Reproduce

### Manual path (Burp Suite — for discovery)

1. Log in as `wiener:peter` → intercept in Burp → note `verify=wiener` cookie
2. Go to `/login2` — change `verify=wiener` → `verify=carlos` in Repeater
3. Submit any 2FA code — server now checks carlos's account
4. Use Intruder to brute force `mfa-code` from 0000–9999
5. On correct code → 302 redirect → authenticated as carlos

> **Note:** Burp Community Intruder takes hours for 10,000 codes. Use the Python script below instead.

### Script path (Python — for speed)

```python
# Step 1 — Log in as wiener to get valid session
session.post("/login", data={"username": "wiener", "password": "peter"})

# Step 2 — Prime carlos's 2FA by hitting /login2 with verify=carlos
session.get("/login2", cookies={"verify": "carlos"})

# Step 3 — Brute force 0000-9999 with 20 concurrent threads
# Server returns 302 on correct code
```
Full script: https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Brute-forcing%20a%20stay-logged-in%20cookie/Brute%20force%204-digit%20code.py

## Proof of Concept

<img width="767" height="190" alt="image" src="https://github.com/user-attachments/assets/71d31b48-fa5e-4119-a352-0154c1ebf36e" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/272db856-f68c-4245-ae7b-a59ccc8ee6d2" />

## Impact

### Technical
- Complete bypass of 2FA — victim's password never needed
- Only requirement: attacker has any valid account on the platform
- 10,000 codes brutable in ~2 minutes with 20 threads
- No rate limiting on 2FA endpoint observed

### Business / Real-World
- 2FA exists specifically to protect accounts where password is compromised
- This vulnerability makes 2FA completely non-functional
- An attacker with a leaked password list + this flaw = mass account takeover
- Affects every account on the platform simultaneously

### Severity Justification
Rated **Critical** because:
- 2FA is the last line of defence — bypassing it with no victim interaction is maximum impact
- Fully automated — single script, no manual steps
- No victim action required whatsoever

## Real World Application

**How to find this on real targets:**

```
1. Register your own account
2. Enable 2FA on your account
3. Log in → go through 2FA flow → intercept with Burp
4. Look for any parameter that identifies the user at the 2FA step:
   - Cookie: verify=yourusername
   - Cookie: user=yourusername
   - POST body: username=yourusername
   - Hidden field: account=yourusername
5. Change the value to another known username (e.g. admin, or a second test account)
6. Submit — if the server processes it without error → vulnerable
7. Brute force 4-6 digit code with the script
```

**Where it appears:**
- Homegrown 2FA implementations
- Apps that bolt 2FA onto existing auth without redesigning session management
- Mobile app backends where 2FA was added as an afterthought

## Manual vs Script

| | Burp Intruder (Community) | Python Script |
|---|---|---|
| 10,000 codes | ~3 hours throttled | ~2 minutes |
| Setup | Manual payload position | Single command |
| Reusable | No | Yes |
| Rate limit handling | Manual | Scriptable |

For discovery — Burp. For exploitation — script always wins.

## Remediation

1. **Bind 2FA session to Step 1 session** — after password login, store the authenticated username server-side in the session, never trust a client-supplied value
2. **Never use user-controlled cookies to identify 2FA target** — the session itself should carry this state
3. **Rate limit /login2** — max 5–10 attempts per session before invalidating
4. **Invalidate 2FA session after N failures** — force re-authentication from Step 1
5. **Use cryptographically signed tokens** — tie the 2FA challenge to the authenticated session with an HMAC

## Lessons Learned

- 2FA security depends entirely on the session binding between Step 1 and Step 2
- Any user-controlled value that identifies the target at the 2FA step is exploitable
- 4-digit codes (10,000 combinations) are trivially brutable without rate limiting
- The `verify` cookie pattern appears in real apps more than expected
- Discovery in Burp → exploitation via script is the optimal workflow

## References

- [PortSwigger Lab — 2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic)
- [PortSwigger — 2FA vulnerabilities](https://portswigger.net/web-security/authentication/multi-factor)
- [OWASP — Testing for Multi-Factor Authentication](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Authentication_in_Alternative_Channel)

**Tags:** `#PortSwigger` `#2FA` `#MFA` `#BrokenLogic` `#AccountTakeover` `#Critical` `#Python`
