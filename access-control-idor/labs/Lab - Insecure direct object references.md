**Lab:** PortSwigger Web Security Academy

https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references

**Date Solved:** 2026-08-18

**Vulnerability:** Insecure Direct Object Reference (IDOR) / Broken Access Control + Password Disclosure

**Difficulty:** Apprentice 

This lab stores user chat logs directly on the server's file system, and retrieves them using static URLs.

**Severity: High (8/10)**

## Summary

The application stores chat transcripts as files with predictable filenames and exposes them through static URLs. An unauthenticated user can directly access another user's transcript by modifying the transcript filename.

The exposed transcript contains the user's plaintext password, allowing the password to be used to access the victim's account.

## Affected Component

`GET /download-transcript/1.txt HTTP/2`

## Steps to Reproduce

1. Open the lab without logging in.
2. Navigate to **Live chat**.
3. Click **View transcript** to download it.
4. In Burp → Proxy → HTTP history, locate:

```livescript
GET /download-transcript/2.txt HTTP/2
```

Notice it the endpoint is 2, the requests for `/download-transcript`starting with 2 hints there is a hidden file in `1`

1. Send the request to Repeater.
2. Change the file reference from `2.txt` to `1.txt`:
3. Send the request (Ctrl+Space).

Observe that the server returns another user's chat transcript despite the request being unauthenticated — The transcript contains the user's plaintext password.

1. Use the disclosed password to log in as `carlos` and solve the lab.

### **Proof of Concept**

**Modified request:**

```html
GET /download-transcript/1.txt HTTP/2
Host: <REDACTED>
```

**Sensitive data exposed:**

```html
You: Ok so my password is <REDACTED>. Is that right?
Hal Pline: Yes it is!
```

No authentication or prior chat message was required to access the transcript.

## Root Cause

The transcript download endpoint does not perform authorization checks before returning the requested file. Transcript filenames are also predictable, allowing an attacker to access other users' transcripts by modifying the file reference.

## Impact

- **Technical:** An unauthenticated attacker can retrieve another user's transcript and obtain their plaintext password.
- **Business / Real-World:** The disclosed credential can enable account takeover and unauthorized access to the victim's account and associated functionality.
- **Scope:** The issue affects the transcript download functionality and the sensitive information contained within stored transcripts.

## Remediation

Require appropriate authentication and authorization before serving private transcripts. Do not use predictable client-controlled filenames as access controls. Verify that the requesting user is authorized to access the requested transcript. Never store or expose plaintext passwords.

## Lessons Learned & Patterns

- IDOR does not require a `?id=` parameter; a filename such as `1.txt` can also function as an object reference.
- A predictable filename alone is not necessarily a vulnerability. The vulnerability exists when changing the reference provides unauthorized access to another user's object.
- Always verify whether authentication is actually required. In this lab, I initially assumed the session cookie meant the request was authenticated, but re-testing showed that the transcript was accessible without authentication.
- Don't assume a request is interesting simply because it uses sequential identifiers. First confirm that changing the identifier accesses another user's resource.
- Always inspect the complete response for sensitive information and assess the impact of what is exposed.

### References

- [PortSwigger — Insecure Direct Object References](https://portswigger.net/web-security/access-control/idor)
- [PortSwigger — Lab: Insecure direct object references](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references)
- [OWASP — Insecure Direct Object Reference Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)

**Tags:** #PortSwigger #IDOR #BrokenAccessControl #PasswordDisclosure
