# PHP2Shell (CVE-2026-109618 / CVE-2026-109619) — Room Notes

How I discovered it: [An X tweet](https://x.com/tryhackme/status/2113288042643357828?s=20)
THM room: https://tryhackme.com/room/cvephp2shell

## What PHP2Shell Is

PHP powers an estimated 70% of websites (WordPress, Wikipedia, major e-commerce stacks included). PHP2Shell is the name given to a pair of critical memory-management vulnerabilities in the PHP runtime itself — affecting versions 5.4 and later — that let an **unauthenticated** attacker send crafted requests to a vulnerable server and potentially execute arbitrary code, no login required.

- **CVE-2026-109618** — Memory disclosure. PHP can leak unintended worker-memory contents back to the attacker via an HTTP response header.
- **CVE-2026-109619** — Remote code execution. Corrupted internal state can hijack program execution flow.

Both scored **9.2 Critical (CVSS v4.0)**. Fixed in PHP **8.5.12, 8.4.27, 8.3.36, 8.2.35** (released Oct 21, 2026). Exploitation attempts were observed in the wild within hours of disclosure — treat as a live threat, not theoretical.

> Attribution note: confirm the credited researchers against the official Red Hat/PHP advisory before publishing — don't repeat secondhand claims without checking the primary source.

## Why This Category Matters

This isn't an application bug — patching WordPress, Drupal, Joomla, or Laravel does nothing, because the flaw sits in the PHP runtime underneath all of them. A CMS is just the common, high-value target that makes this worth attacker attention at scale.

## The Vulnerable Feature: Upload Progress Tracking

The entry point isn't exotic — it's a legitimate, everyday PHP feature. During a file upload, the browser sends `multipart/form-data`, letting one request carry both form fields and file bytes. PHP can track upload progress by recognizing a specific hidden field:

```html
<input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="profile-picture-upload">
```

This value gets written into server-side `$_SESSION` data (not the same as the browser's cookie — the cookie just carries the session identifier PHP uses to look that data up).

**The chain to remember:**
`HTTP upload → multipart parser → PHP upload-progress feature → server-side session data → application response`

## Root Cause: The Bailout

PHP caps per-request memory via `memory_limit`. When a request exceeds it, PHP can't continue normally — it performs a **bailout**: using `longjmp()` to jump straight to a safe recovery point, abandoning whatever it was doing. This is the mechanism behind the familiar "Allowed memory size exhausted" fatal error. Critically, a bailout is an **emergency exit, not an orderly shutdown** — it skips the normal cleanup that would free memory and clear pointers.

**The flaw is a timing window:** if the out-of-memory condition hits *after* a block of memory has been freed but *before* the pointer referencing it is cleared, the bailout leaves that pointer dangling — pointing at memory that's no longer valid. This is **CWE-824: Access of Uninitialised Pointer**.
PHP hits memory limit → bailout interrupts normal cleanup → internal state left inconsistent → later code may use an invalid pointer

## Why It's Exploitable Across Requests: Prefork + mod_php

Apache's `prefork` MPM spawns a pool of separate worker *processes* (not threads) and reuses each one across many requests. `mod_php` — the classic embedded way of running PHP in Apache — requires `prefork` specifically, because PHP's interpreter isn't thread-safe.
Because workers are **reused, not restarted**, a dangling pointer left behind by one request's bailout **persists in that worker's memory** until it eventually recycles. A later, unrelated request handled by the same worker can end up referencing newly allocated data through the stale pointer instead of the original memory — turning a one-off memory bug into a repeatable, remotely-triggerable primitive.
Bailout leaves invalid state → a later request on the same worker encounters the stale state → memory disclosure or execution-flow corruption

## Recon Steps

```bash
docker ps --format '{{.Names}}  {{.Image}}  {{.Status}}'
# Confirms the target container is running: php2shell-target, image php:8.4.26-apache

docker exec php2shell-target php -v
# Confirms vulnerable PHP version (8.4.26) inside the container

curl -s http://127.0.0.1:8088/index.php
# Confirms the app is reachable; -s suppresses progress output

docker exec php2shell-target cat /var/www/html/index.php
# Source is trivial: <?php echo "OK\n"; ?>
# Confirms the bug lives in the PHP runtime, not application logic — the app has none
```

## Exploitation

```bash
python3 exploit.py -u http://127.0.0.1:8088/index.php
```

**Stage 1 — Heap leak.** Repeated requests rotate across worker processes ("rotating worker over HTTP") hunting for one holding leaked state. Recovers the heap chunk base address.

**Stage 2 — libphp leak.** Same technique, recovers the base address of the PHP shared library in memory.

Both addresses are read directly out of a `Set-Cookie` response header — not guessed, not brute-forced. They differ on every run because of **ASLR** (Address Space Layout Randomization); the exploit's job is to *read* the current run's addresses each time, not defeat ASLR by prediction.

**Stage 3 — Corruption and execution.** With heap and library both located, the second CVE (109619) uses those addresses to turn the memory corruption into controlled execution. The exploit writes a target command (`cmd='id>/out/p1'` in this run) and triggers it.

**Proof of execution:**
PROOF: uid=33(www-data) gid=33(www-data) groups=33(www-data)
Confirms arbitrary command execution as the web server user (`www-data`), via an unauthenticated HTTP request, with zero application-layer involvement.

## Detection, Mitigation, Real Fix

**The only complete fix:** update the PHP runtime itself — not the CMS/application — to 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35, and **restart every worker process** afterward (otherwise old vulnerable code stays resident in memory, patch notwithstanding).

**Interim mitigations (none are a substitute for patching):**
- `session.upload_progress.enabled = 0` + restart all workers — removes the feature the attack relies on, blocks most reported techniques.
- `opcache.enable = 0` — frustrates the code-execution path.
- `fatal_error_backtraces = 0` (PHP 8.5 only) — addresses CVE-2026-109619 specifically.
- Reject `multipart/form-data` at the network edge — blocks the delivery mechanism, at the cost of breaking legitimate file uploads.
- Run the PHP process with least privilege — limits blast radius if the chain lands anyway.

**What does NOT help:** a PHP-based WAF. It only inspects traffic once PHP hands control to the application — but this exploit completes entirely during request parsing, before the application layer (and therefore the WAF) ever sees it. Protection has to sit either in the patched runtime itself, or in front of PHP at the network layer.

**Detection signals to alert on:**
- Abnormally large `PHPSESSID` values in `Set-Cookie` response headers (vs. PHP's normal fixed-length identifiers)
- Large multipart POST bodies with very high field counts carrying `PHP_SESSION_UPLOAD_PROGRESS`
- PHP worker crashes / out-of-memory errors in logs

Any one of these is worth flagging; the combination is a strong signal.

## Key Terms

- **Bailout** — PHP's emergency exit via `longjmp()` when memory_limit is exceeded; skips normal cleanup.
- **Dangling pointer** — a pointer left referencing memory that's already been freed.
- **CWE-824** — Access of Uninitialised Pointer; the weakness class behind this bug.
- **prefork / mod_php** — Apache's process-based worker model, required for classic embedded PHP; workers persist across requests, which is why the dangling state survives long enough to be exploited remotely.
- **ASLR** — Address Space Layout Randomization; why addresses differ per run and must be leaked fresh each time rather than guessed.

## Reference
- https://access.redhat.com/security/cve/cve-2026-109619
  
<img width="1919" height="960" alt="image" src="https://github.com/user-attachments/assets/7fe229f7-4b0d-422f-bfed-dbd8368a807f" />
