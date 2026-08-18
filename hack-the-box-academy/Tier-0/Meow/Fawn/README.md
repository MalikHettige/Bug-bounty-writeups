  # Fawn

**Platform:** Hack The Box
**Tier:** 0
**Difficulty:** Easy
**Category:** FTP / Anonymous Access

## Overview

Fawn is an introductory machine focused on FTP enumeration and anonymous access.

## Enumeration

Scan the target:

```bash
nmap <TARGET_IP>
```

Port `21` was open, indicating an FTP service.

Then identify the service:

```bash
nmap -sV <TARGET_IP>
```

## Initial Access

Connect to FTP:

```bash
ftp <TARGET_IP>
```

Anonymous authentication was allowed:

```text
Username: anonymous
Password: anonymous
```

After logging in:

```bash
ls
```

The flag was accessible.

## Flag

```bash
get flag.txt
bye
cat flag.txt
```

## Attack Path

```text
Nmap
 ↓
Port 21
 ↓
FTP
 ↓
Anonymous access
 ↓
Flag
```

## Key Lessons

* Port `21` commonly indicates FTP.
* Always investigate the authentication options of an exposed service.
* Anonymous access can expose files without requiring a normal account.

## Tools Used

* Nmap
* FTP
* Linux shell

## Takeaway

The main lesson was learning to enumerate a service after discovering it:

```text
Discover → Identify → Enumerate → Access
```
