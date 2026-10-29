**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-08-17

**Difficulty:** Apprentice 

**Severity:**  Medium — CVSS 3.1: 6.5

## Summary

An unauthorized request targeting the victim (carlos) sent by an authenticated attacker shows 302 redirect. But in that redirect response, sensitive data is included in the body. 

## Affected Component

`GET /my-account?id=carlos HTTP/2`

## Steps to Reproduce

1. Navigate to my account — get authenticated
2. Locate the `GET /my-account?id=wiener`request
3. Send that request to repeater 
4. Modify `id=wiener` to `id=carlos` and send the request — notice it shows 302 Found with `Location: /login`

Observe that the browser may follow the redirection and show the login page, **but Burp Repeater can still show me the original `302` response and its body** which contains sensitive data.

1. Click search below response pane, type “API”
2. Copy the key, submit and solve the lab

### **Proof of Concept**

Modified request

`GET /my-account?id=carlos HTTP/2
Host: <LAB_HOST>
Cookie: session=<REDACTED>`

Response: 

`Your API Key is: <REDACTED>`

## Root Cause

The application fails to implement proper authorization checks specifically to 302 redirection responses and leads to sensitive data still being generated/returned.

## Impact

- **Technical:** An authenticated attacker can obtain another user's API key without requiring interaction from the victim.
- **Business / Real-World:** Unauthorized disclosure of sensitive user credentials or account information could expose users to further security risks.
- **Scope:** Horizontal access control / sensitive information disclosure affecting user-specific account data.

## Remediation

The application should perform authorization checks before retrieving or including user-specific data in a response. When an unauthorized request occurs, the server should return a response containing no sensitive information, including in `3xx` redirect responses.

## Lessons Learned & Patterns

- A redirect does not make a response safe if sensitive data is already present in its body.
- Always inspect the complete HTTP response, including `3xx` responses.
- User-controlled identifiers should be tested for horizontal access-control issues.
- Authorization should be enforced before sensitive data is retrieved or returned.

**Tags:** #PortSwigger
