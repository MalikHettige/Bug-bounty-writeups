# Username Enumeration via Response Timing

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-16  
**Severity:** High (when chained to brute-force)

## Summary

The login endpoint leaks valid usernames through response timing differences. When a valid username is submitted, the server runs bcrypt password comparison — an intentionally slow operation. Invalid usernames skip bcrypt entirely and return immediately. This ~300–400ms gap is detectable and exploitable even when error messages and response sizes are identical. Combined with `X-Forwarded-For` IP spoofing to bypass rate limiting, a full username enumeration and password brute-force was completed achieving account takeover on `alterwind`.

## Affected Component

`POST /login` — unauthenticated login form. Rate limiting present (bypassable via `X-Forwarded-For`). Fields: `username`, `password`.

## Why This Works (Root Cause)

```
Invalid username → server checks DB → not found → returns immediately (~50ms)
Valid username   → server checks DB → found → runs bcrypt on password → slow (~400ms+)
```

bcrypt is designed to be slow to prevent brute-force. But that slowness leaks username validity — the server only runs bcrypt when the username exists. A longer password amplifies the gap because bcrypt has to process more data.

## Steps to Reproduce

### Phase 0 — Establish timing baseline

Send requests with a 500-character dummy password to amplify bcrypt delay:

```
fakeuser123 + AAAA*500 → ~1.374s
wiener      + AAAA*500 → ~1.678s
```

Gap confirmed: ~300ms. Valid username runs bcrypt, invalid doesn't.

### Phase 1 — Username enumeration via timing

Run timing attack against full username wordlist:
- 3 samples per username, averaged to reduce network jitter
- `X-Forwarded-For` header rotated per request to bypass IP rate limit
- Sort results by slowest response

```
alterwind → 4.077s   ← outlier, 2x slower than everyone else
al        → 2.138s
alabama   → 2.135s
```

Valid username confirmed: **`alterwind`**

### Phase 2 — Password brute-force

Iterate password wordlist against `alterwind` with rotating `X-Forwarded-For`:

```
[192.168.0.19] qwertyuiop → 302
[LOGIN SUCCESS] qwertyuiop
```

### Phase 3 — Access

Login with `alterwind:qwertyuiop` → authenticated → lab solved 

---

## Proof of Concept

**Timing baseline:**
Run this code to demonstrate response ms difference : https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/username-enum-response-timing/response-timing-demonstration.py
```
fakeuser123 → 1.374s
wiener      → 1.678s
```

**Username enumeration output:** 

https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/username-enum-response-timing/username-enum-timing.py
```
Top 5 slowest:
  alterwind → 4.077s   ← valid
  al        → 2.138s
  alabama   → 2.135s
  alaska    → 2.123s
  alerts    → 2.123s
```

**Password found:**

https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/username-enum-response-timing/password-brute.py

<img width="742" height="437" alt="image" src="https://github.com/user-attachments/assets/a53f5892-bd46-4c6b-b569-4100de0d5dcf" />

**Lab solved:**  

<img width="1919" height="824" alt="image" src="https://github.com/user-attachments/assets/ad705a62-1ff0-4625-b7d1-1aefb6772db6" />
---

## Rate Limit Bypass

The app blocks by IP after N failed attempts. Bypassed using `X-Forwarded-For` header rotation:

```python
fake_ip = f"192.168.{i // 256}.{i % 256}"
headers = {"X-Forwarded-For": fake_ip}
```

Each request appears to come from a different IP. Counter never increments for the same "IP" twice.

---

## Impact

### Technical
- Valid usernames enumerable silently via timing — no message or size difference visible
- Rate limiting fully bypassed via `X-Forwarded-For` spoofing
- Full ATO achieved: username enumerated → password brute-forced → account accessed
- Undetectable in standard security monitoring — requests look like normal login attempts

### Business / Real-World
- Any account on the platform enumerable given enough time
- Combined with common password lists — accounts with weak passwords fully compromised
- No user interaction required — fully automated attack
- In production: PII, payment data, admin access all at risk

### Severity Justification
Rated **High** because:
- Complete ATO chain demonstrated end to end
- Rate limiting — the only protection — is bypassable via a single header
- Attack is fully automatable and stealthy

---

## Remediation

1. **Constant-time response** — run bcrypt regardless of whether the username exists; use a dummy hash for invalid usernames so timing is always equal
2. **Rate limit by attempt, not IP** — counting by `X-Forwarded-For` is bypassable; use account-level lockout or device fingerprinting
3. **Reject or ignore `X-Forwarded-For`** from untrusted sources — only trust it from known proxy IPs
4. **CAPTCHA** after N failures regardless of IP
5. **Response padding** — equalise response size and timing across all login outcomes

---

## Methodology Notes (Real Bug Bounty)

**When to use timing attacks:**
```
Same error message for all cases?     → check timing
Same response size for all cases?     → check timing
Headers identical?                    → check timing
All else fails?                       → timing is last resort
```

**How to find timing gaps on real targets:**
1. Create test account → use as valid username baseline
2. Open DevTools → Network tab → submit login
3. Compare Time column: your account vs fake username
4. 200ms+ gap = exploitable

**Real username sources (no wordlist needed):**
```
LinkedIn        → employee names → email format
GitHub org      → contributor usernames  
Password reset  → "email not found" = enumeration
Registration    → "email taken" = enumeration
Common accounts → admin, support, api, test, staging
```

**Reporting without a victim:**
- Prove timing gap using your own test account
- Enumerate common usernames (admin, support) to show impact
- Brute-force your own test account with a weak password to demonstrate full ATO chain
- Triager sees complete impact — no real users touched

---

## Lessons Learned

- Timing attacks are rare but powerful — know them for hardened targets
- bcrypt's slowness, a security feature, becomes an information leak when not handled carefully
- `X-Forwarded-For` rate limiting is security theatre — always test it first when you hit a rate limit
- A 30-minute lab timer is itself a lesson: in real hunting, work fast and save progress
- Browser session = cookie, not IP — switching browsers gives a clean session

---

## References

- [PortSwigger Lab — Username enumeration via response timing](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing)
- [PortSwigger — Authentication vulnerabilities](https://portswigger.net/web-security/authentication)
- [OWASP — Testing for Account Enumeration](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)
- [OWASP — Blocking Brute Force Attacks](https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks)

---

**Tags:** `#PortSwigger` `#Authentication` `#TimingAttack` `#UsernameEnumeration` `#XForwardedFor` `#RateLimitBypass` `#Practitioner` `#Python`
