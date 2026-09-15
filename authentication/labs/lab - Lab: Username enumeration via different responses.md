# Username Enumeration via Different Responses

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Apprentice  
**Date Solved:** 2026-09-15  
**Severity:** Medium

---

## Summary

The login endpoint on this application returns two distinct error messages depending on whether a submitted username exists in the system:

- Invalid username → `"Invalid username"`
- Valid username + wrong password → `"Incorrect password"`

This behavioural difference allows an attacker to enumerate valid usernames without any authentication. Once a valid username is confirmed, the password can be brute-forced by watching for an HTTP 302 redirect — which only occurs on a successful login. Both phases were automated using concurrent Python scripts, completing the full attack in under 30 seconds.

---

## Affected Component

`POST /login` — the login form at the root of the application. No CSRF token was present. Field names: `username`, `password`.

---

## Steps to Reproduce

### Phase 1 — Username Enumeration

1. Open the lab and navigate to `/login`
2. Confirm the form fields: `username` and `password` (no CSRF token)
3. Save the PortSwigger-provided candidate username wordlist to `usernames.txt`
4. Run `username-enum-different-responses.py` with the wordlist pointed at the target URL
5. Script sends POST requests concurrently (10 threads), checking each response for `"Incorrect password"` instead of `"Invalid username"`
6. Valid username identified: **`an`**

### Phase 2 — Password Brute-Force

1. Save the PortSwigger-provided candidate password wordlist to `passwords.txt`
2. Update `password-brute.py` with the confirmed username `an`
3. Run the script — it POSTs each password concurrently with `allow_redirects=False`
4. A successful login returns HTTP **302** instead of 200
5. Valid password identified: **`harley`**

### Phase 3 — Access

1. Navigate to `/login`
2. Enter credentials: `an` / `harley`
3. Successfully authenticated — lab solved ✅

---

## Proof of Concept

**Phase 1 output — username found:**
```
[FOUND - diff message] an
```

**Phase 2 output — password found:**
```
[302 - LOGIN SUCCESS] password: harley
```

> 📸 _Screenshot of solved lab banner — to be added on next run_

**Scripts used:**
- [`username-enum-different-responses.py`](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Lab%20-%202FA%20broken%20logic/Username%20Enumeration%20via%20Different%20Responses/username-enum-different-responses.py) — Phase 1
- [`password-brute.py`](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Lab%20-%202FA%20broken%20logic/Username%20Enumeration%20via%20Different%20Responses/password-brute.py) — Phase 2

---

## Root Cause

The application uses two separate code branches for failed login attempts:

- Branch A: username not found → returns `"Invalid username"`
- Branch B: username found, wrong password → returns `"Incorrect password"`

A secure implementation would collapse both into a single generic message: `"Invalid username or password"` — making it impossible to distinguish the two cases externally.

---

## Impact

### Technical

- An unauthenticated attacker can enumerate all valid usernames on the platform silently
- With a valid username confirmed, a targeted brute-force attack on the password becomes viable
- No rate limiting or lockout was observed during testing
- Full account takeover achievable in under 60 seconds with common wordlists

### Business / Real-World

- Exposes the existence of user accounts — including potentially sensitive ones (admin, internal users)
- Enables targeted credential stuffing attacks against real users
- In a real application, this directly enables account takeover at scale with no technical sophistication required
- Regulatory exposure under GDPR / data protection laws if user account existence is leaked

### Scope

In a real bug bounty context this would apply to any unauthenticated login endpoint that:
- Returns different error messages for invalid username vs invalid password
- Lacks rate limiting or CAPTCHA
- Accepts username/password via a POST form or JSON body

---

## Remediation

1. **Unify error messages** — return identical response text for both invalid username and wrong password: `"Invalid username or password"`
2. **Equalise response timing** — even if messages match, timing differences can leak the same information; use constant-time comparison
3. **Implement rate limiting** — lock accounts or introduce delays after N failed attempts per IP or username
4. **Add CAPTCHA** on the login form after repeated failures
5. **Monitor and alert** on high-volume login failures from a single IP

---

## Lessons Learned & Patterns

- Always check **error message wording** on login forms — even subtle differences (`"Invalid username"` vs `"Incorrect password"`) are exploitable
- **Burp Community Intruder throttles to ~1 req/sec** — for lists of 100+ items, Python with `ThreadPoolExecutor` is the practical alternative: 10 threads finishes in ~10 seconds
- `allow_redirects=False` in Python requests is the cleanest way to detect a successful login — a 302 is unambiguous
- This vulnerability pattern appears in real apps more often than expected, especially in older codebases or homegrown auth systems
- Two-phase attacks (enumerate → brute-force) are more efficient and stealthier than spraying username+password combinations blindly

---

## References

- [PortSwigger Lab — Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses)
- [PortSwigger Web Security Academy — Authentication vulnerabilities](https://portswigger.net/web-security/authentication)
- [OWASP — Testing for Account Enumeration (OTG-IDENT-004)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)

---

**Tags:** `#PortSwigger` `#Authentication` `#UsernameEnumeration` `#BruteForce` `#Apprentice` `#Python`
