# Username Enumeration via Subtly Different Responses

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-15  
**Severity:** Medium

## Summary

The login endpoint returns what appears to be an identical error message for both valid and invalid usernames — `"Invalid username or password."` — making this vulnerability invisible to the naked eye and nearly undetectable in Burp's UI. The subtle difference is a **single trailing space** appended to the message when a valid username is submitted. By anchoring detection on the exact absence of the known fixed string rather than comparing full response bodies, a valid username was enumerated and the account password subsequently brute-forced via HTTP 302 redirect detection.

### Burp Alternative
Solving this in Burp Suite:
Send the login request to Intruder, set username as the payload position. After running the attack, add a column — right-click any response → "Show response in browser" won't help here. Instead go to Options → Grep - Match, add the exact string Invalid username or password. and check "Flag result if expression is not found". The one request where the box is unchecked is your valid username. Burp Pro users can also sort by response length after enabling "Store requests/responses" — the valid username will be 1 byte off. Community users will wait 2–3 minutes for the same result Python finds in 10 seconds.

## Affected Component

`POST /login` — unauthenticated login form. No CSRF token present. Fields: `username`, `password`.

## Steps to Reproduce

### Phase 1 — Username Enumeration

1. Open the lab and navigate to `/login`
2. Inspect the error message for a fake username — returns `"Invalid username or password."`
3. Confirm response bodies are too noisy to diff directly (dynamic analytics IDs and session tokens change per request)
4. Key insight: check whether the exact string `"Invalid username or password."` is **absent** from the response — a trailing space variant won't match
5. Run `username-enum-subtly-different-responses.py` with 10 concurrent threads
6. Valid username identified: **`ag`**

### Phase 2 — Password Brute-Force

1. Update `password-brute.py` with confirmed username `ag`
2. Run script — iterates password wordlist concurrently with `allow_redirects=False`
3. Successful login returns HTTP **302**
4. Valid password identified: **`jessica`**

### Phase 3 — Access

1. Navigate to `/login`
2. Enter credentials: `ag` / `jessica`
3. Successfully authenticated as `ag` — lab solved ✅


## Proof of Concept

**Phase 1 — Username found:**
https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Lab%20-%202FA%20broken%20logic/username-enum-subtly-different-responses/username-enum-subtly-different-responses.py
```
[FOUND] ag
```

**Phase 2 — Password found:**
https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Lab%20-%202FA%20broken%20logic/username-enum-subtly-different-responses/password-brute.py
```
[LOGIN SUCCESS] jessica
```

**Phase 3 — Lab solved:**  
<img width="1919" height="863" alt="image" src="https://github.com/user-attachments/assets/3ff82feb-b4db-4d3d-bdea-ab722a4fd912" />

## Root Cause

The application has two subtly different code paths for failed logins:

- Invalid username → `"Invalid username or password."` (no trailing space)
- Valid username, wrong password → `"Invalid username or password. "` (trailing space)

The difference is a single whitespace character — likely introduced by a copy-paste inconsistency or a template rendering difference between two separate error branches. Visually and functionally the responses appear identical, but at the byte level they differ, enabling enumeration.


## Why Standard Approaches Failed Here

| Approach | Why It Failed |
|---|---|
| Raw byte count | Username is reflected in the page — longer username = bigger response, masking the difference |
| Full body diff | Dynamic analytics IDs and session cookies change every request |
| repr() of error line | Trailing space invisible without explicit hex comparison |
| Hex dump of error line | Both lines had identical hex — space was elsewhere in page structure |

**What worked:** checking for the **absence** of the exact known string `"Invalid username or password."` — if it's missing, the response has a different variant.

## Impact

### Technical
- Valid usernames enumerable silently with no visible behavioural difference
- No rate limiting or lockout observed
- Full account takeover in under 30 seconds with standard wordlists
- Undetectable with standard Burp Community tooling without custom scripting

### Business / Real-World
- Silent enumeration means no alerts triggered on the target side
- More dangerous than obvious enumeration — harder for defenders to detect and patch
- Combines with credential stuffing or targeted attacks for full account compromise

### Scope
Applies to any login endpoint where error messages appear identical but differ by whitespace or invisible characters, with no rate limiting in place.

## Remediation

1. **Single unified error message** — use one string constant referenced from one place in code, never copy-pasted
2. **Constant-time response** — equalise response size and timing regardless of whether the username exists
3. **Rate limiting** — limit failed attempts per IP and per username
4. **CAPTCHA** after repeated failures
5. **Code review** — audit all error message strings for whitespace inconsistencies

## Lessons Learned & Patterns

- "Identical" responses are rarely truly identical — always verify at the hex/byte level
- When body diffing fails due to dynamic content, anchor on the **absence of a known fixed string**
- Trailing spaces, capitalisation differences, and punctuation changes are all valid enumeration signals
- Legacy codebases with copy-pasted error strings are especially prone to this

## References

- [PortSwigger Lab — Username enumeration via subtly different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses)
- [PortSwigger Web Security Academy — Authentication vulnerabilities](https://portswigger.net/web-security/authentication)
- [OWASP — Testing for Account Enumeration (OTG-IDENT-004)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)

---

**Tags:** `#PortSwigger` `#Authentication` `#UsernameEnumeration` `#BruteForce` `#Practitioner` `#Python`
