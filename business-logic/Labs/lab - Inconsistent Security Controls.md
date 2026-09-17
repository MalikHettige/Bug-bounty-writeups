# Inconsistent Security Controls

**Platform:** PortSwigger Web Security Academy  
**Category:** Business Logic  
**Difficulty:** Apprentice  
**Date Solved:** 2026-09-18  
**Severity:** High

---

## Summary

The application restricts admin access to users with `@dontwannacry.com` email addresses. However, the email update functionality allows any user to change their email to any domain without re-verification. By registering with a legitimate email, then updating it to an `@dontwannacry.com` address, admin access is granted — bypassing the intended restriction entirely.

---

## How to Find the Target Domain

The registration page explicitly states:
> "If you work for DontWannaCry, please use your @dontwannacry.com email address"

This is the signal. Any time an app:
- Mentions a privileged email domain on the registration page
- Shows "only available to @company.com users" on restricted pages
- Has source code comments referencing internal domains

→ Test whether email can be updated to that domain post-registration.

---

## Steps to Reproduce

1. Register account with any email (use the lab's email client)
2. Confirm registration via email client link
3. Log in → My Account → update email to `anything@dontwannacry.com`
4. Navigate to `/admin` → admin panel now accessible
5. Delete carlos → lab solved 

## POC

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6ff12145-e541-474e-9438-fd10dbca05c2" />


## Root Cause

```
Security check at registration:  "does email match @dontwannacry.com?"
Security check at email update:  NONE
Security check at /admin access: "does current email match @dontwannacry.com?" ✅

Gap: email update bypasses the registration check
     admin access check uses current email, not verified email
```

---

## Real World Application

```
1. Look for hints about privileged domains:
   - Registration page text
   - Error messages on restricted pages  
   - HTML source comments
   - robots.txt, JS files

2. Register → log in → find email update endpoint
3. Change to @privileged-domain.com
4. Access restricted area

Also test:
□ Does email require verification after update?
□ Can you use a subdomain? attacker@dontwannacry.com.evil.com
□ Can you use a similar domain? @d0ntwannacry.com
```

---

## Methodology Entry

```
### Inconsistent Security Controls
WHERE:  registration page hints at privileged domain OR
        restricted page error mentions required email domain
WHAT:   register → update email to @privileged-domain → access /admin
SIGNAL: admin panel appears, restricted page loads
ALSO:   try subdomain tricks: @legit.com.attacker.com
```

---

## Remediation

1. Re-verify email ownership after any email change
2. Never grant access based on unverified email domain
3. Use role-based access control — not email domain matching

---

**Tags:** `#PortSwigger` `#BusinessLogic` `#AccessControl` `#EmailBypass` `#Apprentice`
