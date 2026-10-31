# Basic Password Reset Poisoning via Host Header Injection — Full Account Takeover

**Platform:** PortSwigger Web Security Academy
**Category:** HTTP Host Header Attacks / Authentication
**Difficulty:** Apprentice
**Date Solved:** 2026-10-31
**Severity:** Critical

## Summary

The application's password reset email generation trusts the client-supplied `Host` header when constructing the absolute URL included in the reset email, instead of using a hardcoded, server-trusted domain value. Because the password reset flow can be triggered by an attacker for **any arbitrary username** — including a victim who takes no action at all — an attacker can submit a reset request for a target user with the `Host` header set to an attacker-controlled domain. The server generates the victim's real password reset token but embeds it in a link pointing to the attacker's domain. Any automated or manual fetch of that link (including the victim's own email client, link-preview systems, or the attacker directly requesting the link themselves to verify it) causes the token to leak to the attacker's server logs, which the attacker then uses to take over the victim's account — with zero interaction required from the victim and zero prior authentication required from the attacker.

## Affected Component

`POST /forgot-password` — password reset request handler; downstream email-generation logic that builds the reset link using the request's `Host` header.

## Steps to Reproduce

1. **Baseline.** Triggered a password reset for own account (`wiener`) via the normal "Forgot your password?" UI flow. Observed the resulting email, delivered via the lab's exploit-server email client, containing a link of the form:
   ```
   https://<lab-domain>/forgot-password?temp-forgot-password-token=<token>
   ```

2. **Confirm Host header is trusted.** Captured the `POST /forgot-password` request (body: `username=wiener`) in Burp and resent it via Repeater with the `Host` header changed to an arbitrary value (`evil-test.com`), body unchanged. The request succeeded (`200 OK`) with no validation rejection. A new email arrived whose reset link now read:
   ```
   https://evil-test.com/forgot-password?temp-forgot-password-token=<new-token>
   ```
   This confirms the server does not validate the `Host` header against an expected domain allowlist before using it to construct outbound content.

3. **Exploit — poison a victim's reset link.** Resent the same `POST /forgot-password` request with two changes simultaneously:
   - `Host` header set to an attacker-controlled, request-logging domain (the lab's exploit server)
   - Body parameter changed to `username=carlos` (the target victim)

   The attacker initiates this request directly — no victim interaction, click, or prior action is required at any point in the chain.

4. **Harvest the leaked token.** Checked the attacker-controlled server's access log. A logged request appeared:
   ```
   GET /forgot-password?temp-forgot-password-token=<carlos-token> HTTP/1.1" 404 "user-agent: ...(Victim)..."
   ```
   confirming the victim's real, valid password reset token was delivered directly into attacker-controlled infrastructure — the server generated and "sent" it believing the attacker's domain to be legitimate.

5. **Account takeover.** Constructed a valid reset URL using the real lab domain with the leaked token substituted in:
   ```
   https://<lab-domain>/forgot-password?temp-forgot-password-token=<carlos-token>
   ```
   Visited this URL, was presented with a password-reset form for carlos's account, set a new password, and logged in as carlos — full account takeover achieved with no credentials, no victim interaction, and no prior access to the account.

## Proof of Concept

- Baseline reset email, confirming normal link structure and token parameter name (`temp-forgot-password-token`).
- Host-header-poisoned test request (`Host: evil-test.com`) and the resulting email showing the attacker-controlled domain embedded in the link — proves the trust failure in isolation.
- Victim-targeted poisoned request (`Host: <attacker-server>`, `username=carlos`) and the resulting access log entry showing carlos's real token delivered to attacker infrastructure.
- Successful login as carlos following password reset via the harvested token.

*(Attach: baseline email screenshot, poisoned-Host test email screenshot, access log entry screenshot, successful carlos login screenshot.)*

## Root Cause

The application derives the domain used in password-reset email links from the incoming request's `Host` header rather than from a hardcoded, server-side-trusted configuration value. Combined with the fact that the password reset endpoint accepts an arbitrary `username` parameter with no requirement that the requester be authenticated as — or otherwise prove control over — that account, this allows any unauthenticated party to both select an arbitrary victim and redirect that victim's sensitive reset token to infrastructure the attacker controls.

## Impact

### Technical
- Full, unauthenticated account takeover for any user whose username is known or guessable, requiring zero interaction from the victim.
- The attacker never needs to see the victim's actual inbox — the token is captured entirely through attacker-controlled infrastructure.
- Scales trivially: the same technique applies to every account on the platform; an attacker could iterate through a username list and harvest reset tokens en masse.

### Business / Real-World
- This is one of the most severe outcomes possible in a web application: complete authentication bypass via account takeover, requiring no credentials, no social engineering, and no victim action whatsoever.
- Because the attacker — not the victim — initiates the vulnerable request, this bypasses the usual mitigating factor in most CSRF/phishing-adjacent attacks (that they require some victim interaction or carelessness). Here, the victim is entirely passive.
- If usernames/emails are enumerable or guessable (common in many applications via registration-error-message differences, sequential IDs, or public directories), this becomes a mass account-takeover primitive rather than a single-target attack.

### Scope
Confirmed against the `forgot-password` flow specifically. In a real engagement, the same Host-header-trust pattern should be tested against every feature that generates outbound links referencing "the application's own domain" — email verification, invite links, SSO callback URLs, and any webhook or notification system — since the root architectural flaw (trusting `Host` for URL generation) is rarely isolated to just one endpoint.

## Remediation

1. Never derive security-relevant absolute URLs (password reset links, email verification links, SSO redirect URLs) from the `Host` header. Use a hardcoded, server-side-configured canonical domain value instead.
2. If multiple domains must legitimately be supported (e.g. staging vs. production), validate the `Host` header against a strict server-side allowlist and reject any request with a non-matching value before processing it.
3. Consider binding password reset tokens to additional context (e.g. the session that originally requested the reset) so that a token generated for one request cannot be freely redeemed from a completely different context/domain.
4. Rate-limit and monitor for password reset requests targeting many distinct usernames from a single source in a short window, which would indicate exactly this style of mass token-harvesting attempt.

## Lessons Learned & Patterns

- The `Host` header is fully attacker-controlled data, not trusted infrastructure metadata — any application logic that uses it to construct security-relevant content (URLs, cache keys, redirect targets) inherits that untrustworthiness.
- The severity of Host header poisoning hinges heavily on whether the *attacker* can initiate the vulnerable action against an arbitrary victim, versus requiring the *victim* to click something first. The former (demonstrated here) is categorically worse — it removes the social-engineering dependency entirely.
- Free, purpose-built request-logging services (webhook.site) are sufficient substitutes for Burp Collaborator (Pro-only) when testing out-of-band interactions like this on Community Edition — no paid tooling is required to execute or prove this class of finding.
- This technique only applies to link/token-based flows (password reset, email verification, magic-link login) — it does not apply to numeric/code-based OTP verification, which is a separate vulnerability class entirely (rate-limiting, brute-force, code entropy) requiring different testing techniques.

## References

- PortSwigger Lab: Basic password reset poisoning
- PortSwigger Web Security Academy: HTTP Host header attacks — https://portswigger.net/web-security/host-header

**Tags:** #PortSwigger #HostHeaderAttack #PasswordResetPoisoning #AccountTakeover #Authentication