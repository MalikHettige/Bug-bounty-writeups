# Meow

**Platform:** Hack The Box
**Tier:** 0
**Difficulty:** Easy
**Category:** Network Enumeration / Telnet

## Overview

Meow is an introductory machine focused on basic network enumeration and Telnet.

## Enumeration

First, scan the target:

```bash
nmap <TARGET_IP>
```

The scan revealed:

```text
23/tcp open  telnet
```

Port `23` indicated that a Telnet service was running.

To gather more information:

```bash
nmap -sV <TARGET_IP>
```

## Initial Access

Connect to the Telnet service:

```bash
telnet <TARGET_IP>
```

Using the credentials provided by the HTB task, access to the machine was obtained.

## Flag

After gaining access:

```bash
ls
cat flag.txt
```

The flag was located in the current directory.

## Attack Path

```text
Nmap
 ↓
Port 23 discovered
 ↓
Telnet identified
 ↓
Telnet connection
 ↓
Remote access
 ↓
Flag
```

## Key Lessons

* Start with enumeration rather than immediately attempting exploitation.
* An open port is an entry point for investigation, not automatically a vulnerability.
* Learn to associate common ports with services, while remembering that ports can be non-standard.

## Tools Used

* Nmap
* Telnet
* Linux shell

## Takeaway

The main lesson from Meow was learning the basic enumeration workflow:

```text
Discover → Identify → Enumerate → Investigate
```
