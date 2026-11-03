# Bypassing Rate Limits via Race Conditions

**Platform:** PortSwigger Web Security Academy<br>
**Category:** Access Control (Vertical Privilege Escalation) / Authentication / Race Conditions<br>
**Difficulty:** Practitioner<br>
**Date Solved:** 2026-11-03<br>
**Severity:** Critical (lab scenario; leads to full account takeover of an admin user)

## Summary

The login endpoint enforces a per-username lockout after 3 failed attempts, intended to defend against brute-force attacks. The check (has this username failed 3+ times?) and the write (increment the failure counter) are not atomic. Firing a full candidate password list at the `carlos` account as a single simultaneous burst (HTTP/2 single-packet attack) lets every request read the "not yet locked" state before any of them records a failure, bypassing the lockout entirely. One request in the burst matched carlos's real password and returned a 302, confirming the login. This is privilege escalation, not horizontal access — the compromised account (`carlos`) has admin panel access that the attacker's own low-privilege account does not.

## Affected Component

- Endpoint: `POST /login`
- Parameters: `csrf`, `username`, `password`
- Logic: per-username failed-login counter (check-then-increment, not atomic)

## Steps to Reproduce

1. Log in as `wiener:peter` to establish a baseline.
2. From the proxy history, send a failed `POST /login` attempt for wiener to Repeater.
3. Duplicate the tab 19 times (20 total) and group them.
4. Send the group **in sequence**. Confirm lockout triggers after the 3rd failed attempt ("You have made too many incorrect login attempts. Please try again in N seconds.") — this is the baseline proving the limit is enforced under normal conditions.
5. Wait for the lockout to clear.
6. Send the same group of 20 **in parallel**. Observe that more than 3 requests return the normal "Invalid username or password" response instead of the lockout message — this confirms the race window: the limit can be exceeded when requests arrive concurrently.
7. In Repeater, highlight the `password` parameter value and send the request to Turbo Intruder.
8. Change `username` to `carlos`.
9. Load the `race-single-packet-attack.py` template (see script link below).
10. Copy the full candidate password list to the clipboard (the script reads it via `wordlists.clipboard`).
11. Confirm `concurrentConnections=1` and `engine=Engine.BURP2` — this is what makes the burst arrive as a single TCP packet over HTTP/2, closing the race window tightly enough to beat the lockout.
12. Run the attack. Scan the results table for a `302 Found` response — that row's payload is the correct password.
13. Log in as `carlos` with the recovered password through the normal login form (not replayed via Burp — fresh CSRF token required).
14. Access the admin panel and delete the user `carlos` to solve the lab.

## Proof of Concept

**Baseline (sequential, wiener):** lockout triggered after 3rd failed attempt, message: *"You have made too many incorrect login attempts. Please try again in 56 seconds."*

**Race confirmation (parallel, wiener):** of 20 requests sent simultaneously, more than 3 returned "Invalid username or password" instead of the lockout message — proving the counter increment is not atomic with the check.

**Exploitation (Turbo Intruder, single-packet, carlos):**

> Script used: [race-single-packet-attack.py](https://github.com/MalikHettige/Scripts-tools/blob/main/race-conditions/Bypassing%20rate%20limits%20via%20race%20conditions/race-single-packet-attack.py)

- Payload list: full PortSwigger candidate list (~30 entries), pulled from clipboard at runtime.
- Result: one row returned `HTTP/2 302 Found`, `Location: /my-account?id=carlos` — correct password identified in a single burst, with no lockout triggered.
- A handful of trailing requests in the same run returned `400 Bad Request` / `"Invalid CSRF token (session does not contain a CSRF token)"` — the server rotated the session's CSRF token mid-attack (likely once account state changed), which killed those specific queued requests. This did not affect the outcome; only one correct password was needed and it was found before the token rotation affected that row.

## Root Cause

Time-of-check to time-of-use (TOCTOU) gap on the per-username lockout counter. The server reads the current failure count, evaluates it against the threshold, and only then writes the incremented count — as two separate steps, not one atomic operation. When many requests for the same username arrive within the same narrow processing window, each one reads the counter before any of the others' increments have been persisted. The result is not "all or nothing": requests resolve in whatever order the server happens to process them, so some land as "Invalid" and some land as "too many attempts," depending on tiny timing differences — but far more slip through as valid-looking attempts than the stated limit should allow. A true single-packet HTTP/2 burst (one TCP write holding all requests at a gate, released together) minimizes that timing jitter further than independently-sent parallel requests can, which is why Turbo Intruder succeeds reliably where a Repeater tab group only partially does.

## Impact

### Technical

- A per-account brute-force defense can be bypassed with a single burst of concurrent requests.
- Combined with a realistic password list, this allows credential stuffing or brute force against any account without triggering the intended lockout.
- This is vertical privilege escalation, not horizontal: the attacker's own account has no admin rights, but the compromised account does.

### Business / Real-World

- Account takeover of any user whose password is in or near a common wordlist, including privileged accounts.
- The same check-then-increment pattern shows up on OTP verification, password reset token validation, and 2FA attempt limits — anywhere a counter gates a sensitive action.
- Reportable as a standalone finding even without a successful password guess: demonstrating that the limit itself can be exceeded (e.g. 5-attempt limit, 10 parallel requests, >5 come back as "Invalid" instead of blocked) is sufficient evidence without needing full account compromise.

### Scope

- Any authenticated login attempt against any account.
- Invisible to sequential testing or manual QA — the limit appears to work correctly unless tested under concurrency.

## Remediation

- Make the check-and-increment atomic: a single database operation (e.g. `UPDATE ... SET fail_count = fail_count + 1 WHERE fail_count < threshold`, checking rows affected) or use row-level locking / a transaction around both steps.
- Consider enforcing the limit with an atomic counter in a fast, serializable store (e.g. Redis `INCR` with expiry) rather than a read-then-write pattern against the primary database.
- Add IP-based or device-based throttling as a secondary layer, so the bypass doesn't fully remove rate limiting even if the per-username counter is raced.
- Monitor for bursts of concurrent requests against a single username as an anomaly signal.

## Lessons Learned & Patterns

- Baseline both directions before attacking: confirm the limit works sequentially, then confirm it breaks under concurrency. Skipping the sequential baseline leaves no comparison point to judge the parallel result against.
- The race outcome isn't binary — in a real burst, expect a mix of "allowed" and "blocked" responses depending on arrival order, not a clean pass/fail. More-than-expected "allowed" responses is the signal, not zero "blocked" responses.
- Turbo Intruder's `race-single-packet-attack.py` + `concurrentConnections=1` + `Engine.BURP2` is the standard tool for this: it holds every request at a gate and releases them together, minimizing timing jitter beyond what manual parallel Repeater sends can achieve.
- `wordlists.clipboard` reads directly from the OS clipboard at runtime — no paste step inside Burp needed. Copy the list immediately before running the attack; anything copied afterward overwrites it.
- Once a 302 (or other success indicator) is found, switch to the actual browser login form to authenticate — don't try to replay the win through Burp with a stale CSRF token.
- In a real engagement: only run this against your own test account. Check program scope before brute-forcing any account you don't own — even a small request count (10-12) is still "brute forcing another user's account" if it's not yours, and lockout mechanics can actually deny a real user access to their own account.
- Residential IP note: a WAF/CDN in front of the app may throttle at the network layer independently of the app's own rate limit. A burst of 10-20 requests is normally safe, but don't scale up without checking program-provided testing infra first.

## References

- PortSwigger Lab: Bypassing rate limits via race conditions
- PortSwigger Research: Smashing the state machine (race conditions)
- OWASP: Testing for Weak Lock Out Mechanism

**Tags:** #PortSwigger #RaceCondition #RateLimitBypass #TOCTOU #SinglePacketAttack #PrivilegeEscalation #TurboIntruder
