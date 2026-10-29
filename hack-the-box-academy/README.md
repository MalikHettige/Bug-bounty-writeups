# Hack The Box Writeups

![Hack The Box](https://img.shields.io/badge/Hack%20The%20Box-Writeups-9FEF00?style=flat&logo=hackthebox&logoColor=black)
![Focus](https://img.shields.io/badge/Focus-Offensive%20Security-red)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

Personal collection of **Hack The Box (HTB)** machine, challenge, and module writeups as I develop practical offensive security skills — progressing from fundamentals toward advanced penetration testing.

> **The objective is to understand the attack path, the reasoning behind each step, and why the vulnerability exists** — not just to record solutions.

---

## Goals

- Build strong offensive security fundamentals and a consistent enumeration methodology
- Understand common network services, Linux/Windows internals, and common pentesting tools
- Learn how vulnerabilities translate into practical attack paths
- Document mistakes instead of hiding them
- Progress from beginner HTB content toward advanced machines
- Build a public record of practical cybersecurity development

---

## Progress

| Tier | Completed | Status |
|---|---:|---|
| Tier 0 | 2 | In Progress |
| Tier 1 | 0 | Not Started |
| Tier 2 | 0 | Not Started |
| Tier 3 | 0 | Not Started |

**Current focus:** Offensive Security Fundamentals — Tier 0

---

## 🧪 Writeups

### Tier 0

| Machine | Difficulty | Primary Concepts | Writeup |
|---|---|---|---|
| Meow | Easy | Nmap, Telnet, Remote Access | [View Writeup](./Tier-0/Meow/) |
| Fawn | Easy | Nmap, FTP, Anonymous Access | [View Writeup](./Tier-0/Fawn/) |

---

## Topics Covered

**Recon & Enumeration:** Nmap, port scanning, service/version/OS detection, NSE scripts, full-port scanning

**Networking:** TCP/IP, TCP/UDP, DNS, HTTP/HTTPS, FTP, SSH, Telnet, SMB, RDP, SMTP, SNMP

**Linux:** Filesystem, permissions, users/groups, processes, services, SUID/SGID, cron, env vars, PATH manipulation, privilege escalation

**Windows:** Filesystem, users/groups, services, PowerShell, permissions, registry, scheduled tasks, privilege escalation, Active Directory

**Web Security:** HTTP, authN/authZ, IDOR/BOLA, SQLi, XSS, SSRF, file inclusion, command injection, file upload vulns, business logic, API security

**Exploitation:** Public exploits, manual exploitation, PoC development, shells/reverse shells, payloads, exploit modification

**Post-Exploitation:** Enumeration after access, credential discovery, privilege escalation, persistence, lateral movement, data discovery

---

## Tools

Nmap, Burp Suite, Netcat, Gobuster, ffuf, Feroxbuster, Nikto, WhatWeb, SQLmap, Metasploit, Impacket, Responder, BloodHound, CrackMapExec/NetExec, Wireshark, John the Ripper, Hashcat, Linux CLI utilities, PowerShell

---

## Enumeration Methodology

One of the main skills I'm developing is a repeatable enumeration process:

```text
1. Identify target
2. Confirm scope
3. Discover open ports
4. Identify services
5. Identify versions
6. Enumerate interesting services
7. Identify attack surface
8. Form hypotheses
9. Test hypotheses
10. Gain initial access
11. Enumerate from inside
12. Privilege escalation
13. Capture flags
14. Document the attack path
```
