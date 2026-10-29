**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-07-23

**Difficulty:** Apprentice 

**Severity:** 8.1 (High)

## Summary

The `/administrator-panel` endpoint is disclosed via a public `robots.txt` entry intended to hide the path from search engine crawlers. The endpoint itself fails to implement server-side authorization checks, allowing any unauthenticated attacker who discovers the path to escalate privileges and perform admin-level actions, including deleting other users.

## Affected Component

`https://0ae900c50342310b81a6250400850003.web-security-academy.net/administrator-panel`

## Steps to Reproduce

1. In the application, click the address-bar on top
2. Type `/robots.txt` at the very end of the URL

Observe that it was the location that was unprotected to admin panel path

1. Copy the path ( `/administrator-panel`)
2. Remove `/robots.txt` and add the path 
3. Search the victim (carlos) and delete it

**Proof of Concept**


<img width="1158" height="286" alt="image" src="https://github.com/user-attachments/assets/3206e7f6-4ebe-4656-8597-2b70804f7f52" />


## Root Cause

The application fails to implement server side authorization checks to users who request to visit admin-specific endpoints 

## Impact

- **Technical:** An unauthenticated attacker could potentially delete any user, visit endpoints that are restricted to ordinary users and even retrieve hidden resources in application
- **Business / Real-World:** Could harm the reliability of the application, could risk removing all the users
- **Scope:** Every user in the application is effected.

## Remediation

Implement server-side authorization checks to every admin functionality endpoints and verify the authenticated users privilege level or role on every request before granting access to such locations.Do not rely on path obscurity as a security boundary.

## Lessons Learned & Patterns

- Some applications can have the admin panel disclosed on front-end that can be accessed from modifying URL
- Any endpoint can be reached by a guessable or discoverable URL must enforce its own authorization, independent of whether it's "hidden”
- General takeaway: `robots.txt`, `sitemap.xml` and similar crawler-directive files are a reliable recon source for discovering unlinked endpoints - always check them early..

**Tags:** #PortSwigger #AccessControl
