# Broken Brute-Force Protection: IP Block

**Platform:** PortSwigger Web Security Academy  
**Category:** Authentication  
**Difficulty:** Practitioner  
**Date Solved:** 2026-09-16  
**Severity:** High

## Summary

The application blocks an IP after 3 consecutive failed login attempts. However, the counter resets on any successful login — including from a different account. By interleaving valid `wiener:peter` logins between each `carlos` brute-force attempt, the counter never reaches the lockout threshold. Full account takeover on `carlos` achieved by cycling through the password wordlist one attempt at a time.

## Affected Component

`POST /login` — IP-based brute-force protection. Counter resets on successful login regardless of which account authenticates.

## Root Cause

```
Developer assumed: "if they get locked out, they can't brute-force"
Reality:           counter is shared state, reset by ANY successful login
```

The lockout logic counts consecutive failures per IP. A successful login — even on a completely different account — resets that counter to zero. The protection and the authentication handler are decoupled.

## Steps to Reproduce

Pattern per iteration:
```
1. POST /login  username=carlos   password=<candidate>  → 200 (wrong) or 302 (correct)
2. POST /login  username=wiener   password=peter        → 302 (resets counter)
3. Repeat
```

Counter never reaches lockout. All 100 passwords tested successfully.

**Result:** `carlos` password found → authenticated → lab solved ✅

## Proof of Concept
Script to execute: https://github.com/MalikHettige/Scripts-tools/blob/main/authentication/broken-brute-force-ip-block/broken-brute-force-ip-block/ip-block-bypass.py

**Script output (truncated):**
```
[7]  carlos:111111 → 200
[8]  carlos:1234567 → 200
...
[66] carlos:131313 → 200
[LOGIN SUCCESS] carlos:<password>
```

## Impact

### Technical
- IP lockout fully bypassed — all passwords testable without triggering block
- Attack requires only one known valid account on the platform (attacker's own)
- Doubles the number of requests but completely neutralises the protection
- Fully automatable — single Python script handles the entire attack

### Business / Real-World
- Any account with a known username is brute-forceable
- Attacker only needs their own account (freely registerable on most platforms)
- In production: full ATO on any weak-password account

### Severity Justification
Rated **High** because the protection mechanism is completely non-functional — not weakened, but entirely bypassed with a trivially simple technique.

## Remediation

1. **Lock at account level, not IP level** — count failed attempts per username, not per IP
2. **Don't reset on successful login from different account** — counter should be per-account, not per-session
3. **Progressive delays** — add exponential backoff per account after failures
4. **CAPTCHA** after N failures regardless of IP or account switching
5. **Anomaly detection** — flag IPs that alternate between accounts rapidly

## Methodology Notes (Real Bug Bounty)

**Testing checklist for IP-based rate limits:**
```
□ Hit the limit intentionally — confirm it exists and what the threshold is
□ Log in with your test account immediately after — does counter reset?
□ If yes → IP block bypass confirmed
□ Also test: changing IP via X-Forwarded-For (previous lab technique)
□ Also test: waiting N seconds — does counter expire on its own?
```

**Reporting without a victim:**
- Create test account (attacker account = wiener equivalent)
- Show counter resets after logging into your test account
- Demonstrate you can attempt all passwords on a second test account
- Full ATO proven on accounts you own — no real users touched

## Lessons Learned

- IP-based brute-force protection is weak by design — IPs are spoofable and shareable
- Counter reset logic is almost always an afterthought — always test what resets it
- A successful login on ANY account resetting the counter is a design flaw, not a feature
- 200 = wrong password (stay on page), 302 = correct (redirect) — always your signal
- The most elegant bypasses are the simplest — one extra request per attempt

## References

- [PortSwigger Lab — Broken brute-force protection: IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block)
- [OWASP — Testing for Weak Lock Out Mechanism](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/03-Testing_for_Weak_Lock_Out_Mechanism)

**Tags:** `#PortSwigger` `#Authentication` `#BruteForce` `#IPBlock` `#RateLimitBypass` `#Practitioner` `#Python`
