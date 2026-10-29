# SQL injection

**Program / Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-07-17

**Difficulty:** Practitioner

**Severity:** 7.5 (High)

## Summary

The `storeId` request which is usually sent by the stock feature in an XML format has a stock-id parameter and it can be bypass WAF by obfuscating a crafted payload using XML entities.

## Affected Component

`POST /product/stock HTTP/2`

## Steps to Reproduce

1. Click any item
2. Scroll down to the stock check feature
3. Click it
4. Observe that the `GET /product?productId=1 HTTP/2` and `GET /academyLabHeader HTTP/2`requests appear.
5. Send `storeId`request to repeater (ctrl + R)
6. Add `<storeId><@hex_entities>1 UNION SELECT username || '~' || password FROM users</@hex_entities></storeId>`payload to the value of `storeId` 
7. Send the request; retrieve the credentials
8. Authenticate as administrator using retrieved credentials, confirming full account takeover.

**Proof of Concept**



![PoC — Repeater response showing extracted usernames and passwords via UNION-based SQL injection](https://github.com/Malikdishan416/bug-bounty-writeups/blob/main/portswigger-labs/SQL%20injection/1st-SQL-burp.png?raw=true)

## Root Cause

The application constructed SQL queries by directly concatenating the `storeId` value without parameterization. The WAF attempted to block injection via blacklist pattern-matching on raw syntax (e.g. `UNION SELECT`), but did not decode or normalize XML entities before inspection — allowing an entity-encoded payload to bypass the filter and reach the database layer unsanitized.

### **Impact:**

- **Technical:** Unauthenticated SQL injection allowing full read access to the `users` table via UNION-based extraction.
- **Business/Real-World:** Complete compromise of all user accounts, including administrator — enabling account takeover, data exfiltration, and potential lateral movement depending on admin privileges.
- **Scope:** Every account in the database; no authentication required to trigger the vulnerability.

## Remediation

Use parameterized queries / prepared statements for all database calls involving user-supplied input, regardless of transport encoding. As defense-in-depth, restrict `storeId` to a numeric type at the input-validation layer, and configure the WAF to normalize/decode all encodings before pattern inspection.

## Lessons Learned & Patterns

- Key pattern to look for in future targets: Try obfuscating the payloads using XML entities to test if there are vulnerable
- General takeaway: Input filters that pattern-match on raw syntax are frequently blind to alternate encodings of the same payload. Any time a WAF or filter is present, test whether it normalizes input *before* or *after* inspection — that ordering gap is a reusable bypass class, not just this lab's trick.

## References

- PortSwigger Web Security Academy — SQL injection with filter bypass via XML encoding (lab page)
- PortSwigger — SQL injection cheat sheet
- PortSwigger — Hackvertor extension (BApp Store)
- CWE-89 — Improper Neutralization of Special Elements used in an SQL Command
- OWASP — SQL Injection

#SQLInjection #WAFBypass #XMLEncoding #PortSwigger
