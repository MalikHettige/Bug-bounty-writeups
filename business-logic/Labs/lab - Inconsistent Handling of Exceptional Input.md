# Inconsistent Handling of Exceptional Input

**Platform:** PortSwigger Web Security Academy
**Category:** Business Logic
**Difficulty:** Practitioner
**Date Solved:** 2026-09-21
**Severity:** High


## Summary

The application grants admin access to users with `@dontwannacry.com` email addresses. The registration endpoint silently truncates emails longer than 255 characters at the database level. By crafting an email that exceeds 255 characters and placing `@dontwannacry.com` at exactly position 239–255, the truncated result ends with `@dontwannacry.com` — granting admin access without owning that domain.

## How to Find the Truncation Limit

This is the most important question for real hunting. Three ways:

**Method 1 — Try and observe:**
Register with a 300-character email → check My Account → if the stored email is shorter than what you entered, truncation is happening. Count the stored length to find the exact limit.

**Method 2 — HTML source:**
View source on the registration form and look for:
```html
<input type="email" maxlength="255">
```
`maxlength` reveals the frontend limit — but the backend may differ.

**Method 3 — Common limits to test:**
```
255  → most common (MySQL VARCHAR default)
254  → RFC 5321 email spec limit
256  → power of 2, sometimes used
128  → shorter VARCHAR
```
Always test 255 first. If truncation occurs, the limit is likely 255.

**How to calculate the padding:**
```python
target = '@dontwannacry.com'           # 17 chars
limit = 255
padding = limit - len(target)          # 255 - 17 = 238 'a's
email = ('a' * 238) + target + '@your-exploit-server.net'
```

## Real World Application

**"My email is name@gmail.com — how do I do the email client thing?"**

In labs, PortSwigger provides an exploit server with a fake email client. In real bug bounty, you need to receive the confirmation email yourself. Options:

**Option 1 — Use a domain you own:**
Buy a cheap domain ($1-5/year on Namecheap) → set up email forwarding → you receive any email sent to `anything@yourdomain.com`

**Option 2 — Subdomain services:**
Use `@yourusername.burpcollaborator.net` (Burp Pro) — receives emails automatically

**Option 3 — Prove without receiving:**
On real targets, you don't always need to complete registration. You can:
- Register with the long email
- Check what gets stored (view profile/account page)
- If the stored email is truncated to `@privilegeddomain.com` → that's your PoC
- Report it without needing to actually receive the email

**The key insight:** you need to prove the truncation occurs and results in a privileged email. Showing the stored truncated value in a screenshot is usually enough for a valid report.

## Email Format — What the App Sees

Email structure: `local-part @ domain`

```
Limits per RFC 5321 (the email standard):
local-part:  max 64 characters
domain:      max 255 characters
total email: max 254 characters

Database reality (what apps actually enforce):
VARCHAR(255): truncates at 255 characters
VARCHAR(254): truncates at 254 characters
```

**What gets truncated:** the app reads left to right. When it hits the limit it cuts everything after. So:

```
Input (291 chars):
aaa...aaa@dontwannacry.com.exploit-server.net

Stored (255 chars, truncated):
aaa...aaa@dontwannacry.com
          ^^^^^^^^^^^^^^^^ this is all the server sees
```

The exploit server domain disappears. The server only sees `@dontwannacry.com`.

## Steps to Reproduce

1. Identify the privileged email domain from registration page hint:
   "If you work for DontWannaCry, please use your @dontwannacry.com email address"

2. Calculate the padding needed:
```python
padding = 255 - len('@dontwannacry.com')  # = 238
email = ('a' * 238) + '@dontwannacry.com' + '.YOUR-EXPLOIT-SERVER.net'
```

3. Register with crafted email → confirm via email client → log in

4. Check My Account — stored email shows:
```
aaa...aaa@dontwannacry.com  (truncated, 255 chars)
```

5. Navigate to `/admin` → admin panel accessible → delete carlos ✅

## Proof of Concept

**Registered as:** `das`
**Email stored after truncation:**
```
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaa@dontwannacry.com
```
<img width="1919" height="763" alt="image" src="https://github.com/user-attachments/assets/25d7dc3c-205a-4ff8-a927-29f6e290d3c0" />

## Root Cause

```
Check at registration:  does email end with @dontwannacry.com? → NO (full email checked)
Database storage:       VARCHAR(255) silently truncates to 255 chars
Check at admin access:  does stored email end with @dontwannacry.com? → YES
Gap:                    validation uses original input, access check uses stored value
```

## Real World Hunting Checklist

```
1. Find any email domain restriction ("employees use @company.com")
2. Register with a very long email (300+ chars)
3. Check My Account — is the stored email shorter?
4. If yes: calculate padding to end at @privileged-domain.com
5. Re-register with crafted email
6. Access restricted area
```

Also test:
- Username truncation (same attack, different field)
- Any field with a length limit that feeds into an access control check

## Methodology Entry

```
### Input Truncation → Privilege Escalation
WHERE:  registration with email domain restriction
WHAT:   register with 300+ char email ending in @privileged.com.yourserver.net
        calculate: padding = 255 - len('@privileged.com') = X
        email = ('a' * X) + '@privileged.com' + '.yourserver.net'
SIGNAL: stored email in My Account is shorter than what you entered
FIND:   maxlength in HTML, or test 255/254/256 char lengths
REAL:   own a domain to receive confirmation, or prove via stored truncated value
```

## Remediation

1. Validate email domain AFTER storage, not before — so truncation is caught
2. Reject emails longer than the storage limit at input, don't silently truncate
3. Use `CHECK` constraints in the database to enforce email format on stored values

**Tags:** `#PortSwigger` `#BusinessLogic` `#InputValidation` `#Truncation` `#EmailBypass` `#Practitioner`
