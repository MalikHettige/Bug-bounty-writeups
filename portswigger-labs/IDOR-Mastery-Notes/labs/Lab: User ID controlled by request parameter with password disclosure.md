**Lab:** PortSwigger Web Security Academy

**URL:** https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure

**Date Solved:** 2026-08-17

**Difficulty:** Apprentice 

**Vulnerability:** Insecure Direct Object Reference (IDOR) / Broken Access Control with Password Disclosure

**Severity:** 8.1/10 (CVSS-High)

This lab has user account page that contains the current user's existing password, prefilled in a masked input.

## Summary

The `/my-account` endpoint trusts the user-controlled `id` parameter, allowing an authenticated user to access another user's account page. The administrator's existing password is also exposed in the HTML response.

## Affected Component

`GET /my-account?id=administrator HTTP/2`

`https://0a8d00c104b574e480c47760002e0054.web-security-academy.net/my-account?id=administrator`

## Steps to Reproduce

1. Navigate to my account and get authenticated
2. Locate the `GET /my-account?id=wiener HTTP/2`in HTTP history in burp’s proxy tab
3. Send it to repeater and replace its id with `administrator`
4. In the request, locate the `Referer:`parameter which has the URL — replace that id value with `administrator` as well.
5. Send the request (Ctrl+Space) & inspect the `200 OK` response.
6. Search the response for `password`. (Ctrl+F)
7. Copy the disclosed password and log in as admin 
8. Delete carlos and solve the lab

**Proof of Concept**

Modified request: 

`GET /my-account?id=administrator HTTP/2 
Host: <REDACTED>
Cookie: session=<REDACTED> 
Referer: https://<REDACTED>/my-account?id=administrator`

The HTML code: 

```html
<input required type="hidden" name="csrf" value="<REDACTED>">
<input required type=password name=password value='<REDACTED>'/>
<button class='button' type='submit'> Update password 
```

## Root Cause

The application fails to perform proper server-side authorization checks on the `id` parameter and unnecessarily returns the user's existing password in the HTML response.

## Impact

**Technical:** An authenticated low-privileged user can exploit an IDOR vulnerability to access the administrator’s account details and retrieve the administrator’s plaintext password, leading to full account takeover.

**Business / Real-World:** This results in complete compromise of the administrator account, enabling unauthorized access to sensitive data, administrative functionality, and potential full system compromise.

**Scope:** Affects authenticated users with low privileges who can manipulate the `id` parameter to access higher-privileged user accounts (e.g., administrator).

## Remediation

Enforce server-side authorization for account access; do not trust user-controlled account identifiers; never return existing passwords to the client; store passwords using secure one-way hashing.

## Lessons Learned & Patterns

- The severity of an IDOR vulnerability is not determined solely by the ability to change object identifiers, but by the sensitivity and privilege level of the underlying resource being exposed (e.g., credentials, PII, or administrative state).
- Effective exploitation often requires analyzing the raw HTTP response (including hidden fields, DOM attributes, and unrendered HTML), as client-side rendering may mask critical data leakage that is still present in the source.
- HTML input attributes such as `type="password"` provide only a UI-level masking mechanism and do not constitute a security control; any value embedded in the response body is fully retrievable regardless of how the browser chooses to display it.

**Tags:** #PortSwigger
