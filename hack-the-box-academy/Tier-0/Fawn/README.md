# Fawn

**Platform:** Hack The Box
**Tier:** 0
**Difficulty:** Easy
**Category:** Network Enumeration / FTP

## Overview

Fawn is an introductory machine focused on FTP enumeration and anonymous
access. The whole box comes down to one question: does this FTP server
let anyone in without credentials?

## Enumeration

Start the same way every box starts — find out what's actually running:

```bash
nmap -sV <TARGET_IP>
```

The scan revealed:

```text
21/tcp open  ftp
```

Port `21` is the standard port for FTP (File Transfer Protocol) — used
for transferring files, and often unencrypted by default.

## Initial Access

Connect to the FTP service and try the oldest trick in the book —
anonymous login:

```bash
ftp <TARGET_IP>
# Username: anonymous
# Password: (blank, or anything)
```

Anonymous access was allowed, meaning the server was configured to let
unauthenticated users log in and browse files with no credentials at all.

## Flag

Once connected:

```bash
ls
get flag.txt
```

The flag was sitting in the anonymous FTP root — no privilege escalation
needed, just access.

## Attack Path

```text
Nmap
 ↓
Port 21 discovered
 ↓
FTP identified
 ↓
Anonymous login attempted
 ↓
Access granted
 ↓
Flag
```

## Key Lessons

* Anonymous FTP access is a real, still-common misconfiguration —
  always try it before assuming a service needs credentials.
* FTP sends everything in plain text, including any credentials that
  *are* used — never trust an FTP session on an untrusted network.
* **SFTP** (SSH File Transfer Protocol) is the secure evolution of this
  idea — same purpose as FTP, but tunneled through SSH so both the
  login and the data are encrypted.

## Tools Used

* Nmap
* FTP client
* Linux shell

## Takeaway

Fawn reinforces the same loop as Meow, with one addition: **never skip
the "try anonymous/default first" step.** It's the fastest possible win
and costs nothing to check.

```text
Discover → Identify → Try anonymous/default access → Flag
```
