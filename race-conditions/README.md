# Race Conditions

## Why this folder matters

This is Phase 1 of a $20k-by-June, $10k-by-June-specifically bug bounty plan. Race conditions are one of the two Month 1 fluency topics (the other is JWT) in the three-month training plan, and the critical outcome mapped to this category — **sub-millisecond multi-request asset theft via single-packet/multi-threaded TOCTOU on check-then-act endpoints** (coupon redemption, password reset, balance transfer) — is one of the highest-value, least-saturated bug classes on every major platform. Most hunters never learn single-packet attacks properly because Burp Community doesn't give it to you for free; mastering it here is a direct edge over the average submission queue.

The cold-execution time bar for this topic is **under 45 minutes** per unfamiliar lab (slower than other categories — tooling setup eats time, that's allowed). Every lab in this folder gets solved, written up, and checked against that bar before the topic counts as done. Mastery bar: able to explain the exploit out loud, from memory, to someone with zero context, in under 2 minutes.

$10k by June is the #1 priority. Anything valid found in real engagements gets reported as soon as it's confirmed — not held back chasing a bigger chain. Sitting on a finding risks banking $0.

## Structure

- `labs/` — one Markdown writeup per PortSwigger lab, using the standard template (`writeup-template.md` on the `malikhettige-lab-report-loop` branch of this repo)
- `assets/` — screenshot PoCs referenced by the writeups in `labs/`
- `scripts/` — any Turbo Intruder scripts or standalone Python tooling built while solving these labs. If Burp Community can't do something natively (no single-packet button outside Pro), the workaround script lives here. **Reminder: every script added here must also be added to the Scripts list below, and a copy pushed to the `MalikHettige/scripts-tools` repo.**

## Labs

| # | Lab | Difficulty | Status |
|---|-----|------------|--------|
| 1 | [Limit overrun race conditions](https://portswigger.net/web-security/race-conditions/lab-race-conditions) | Apprentice | Solved — [writeup](labs/01-limit-overrun-race-conditions.md) |
| 2 | [Bypassing rate limits via race conditions](https://portswigger.net/web-security/race-conditions/lab-bypassing-rate-limits-via-race-conditions) | Practitioner | Solved — [writeup](labs/02-bypassing-rate-limits-via-race-conditions.md) |
| 3 | [Multi-endpoint race conditions](https://portswigger.net/web-security/race-conditions/lab-multi-endpoint-race-conditions) | Practitioner | Not solved |
| 4 | [Single-endpoint race conditions](https://portswigger.net/web-security/race-conditions/lab-single-endpoint-race-conditions) | Practitioner | Not solved |
| 5 | [Exploiting time-sensitive vulnerabilities](https://portswigger.net/web-security/race-conditions/lab-exploiting-time-sensitive-vulnerabilities) | Practitioner | Not solved |
| 6 | [Partial construction race conditions](https://portswigger.net/web-security/race-conditions/lab-partial-construction-race-conditions) | Expert | Not solved |

## Scripts

`race-conditions/scripts/` in this repo stays empty on purpose. Anything built goes straight to the `MalikHettige/scripts-tools` repo instead and is linked here.

| Script | Purpose | Used in |
|--------|---------|---------|
| [race-single-packet-attack.py](https://github.com/MalikHettige/Scripts-tools/blob/main/race-conditions/Bypassing%20rate%20limits%20via%20race%20conditions/race-single-packet-attack.py) | Turbo Intruder single-packet burst (gate + `Engine.BURP2`) to race a check-then-increment login lockout counter | Lab 2 |
