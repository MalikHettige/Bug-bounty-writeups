# Hack The Box Writeups

![Hack The Box](https://img.shields.io/badge/Hack%20The%20Box-Writeups-9FEF00?style=flat&logo=hackthebox&logoColor=black)
![Focus](https://img.shields.io/badge/Focus-Offensive%20Security-red)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

A personal collection of my **Hack The Box (HTB)** machine, challenge, and module writeups as I develop practical offensive security skills.

This repository documents my progression from fundamental concepts and beginner machines toward more advanced penetration-testing techniques.

The goal isn't simply to record solutions.

> **The objective is to understand the attack path, the reasoning behind each step, and why the vulnerability exists.**

---

# What I aim for

My goals for this repository are to:

- Build strong offensive security fundamentals
- Develop a consistent enumeration methodology
- Understand common network services
- Improve Linux and Windows security knowledge
- Become comfortable with common penetration-testing tools
- Learn how vulnerabilities translate into practical attack paths
- Develop better problem-solving skills
- Document mistakes instead of hiding them
- Progress from beginner HTB content toward advanced machines
- Build a public record of my practical cybersecurity development

---

# Progress

| Tier | Completed | Status |
|---|---:|---|
| Tier 0 | 2 | In Progress |
| Tier 1 | 0 | Not Started |
| Tier 2 | 0 | Not Started |
| Tier 3 | 0 | Not Started |

### Current Progress

**Machines completed:** 2

**Current focus:** Offensive Security Fundamentals

**Current tier:** Tier 0

---

# 🧪 Writeups

## Tier 0

### Machines

| Machine | Difficulty | Primary Concepts | Writeup |
|---|---|---|---|
| Meow | Easy | Nmap, Telnet, Remote Access | [View Writeup](./Tier-0/Meow/) |
| Fawn | Easy | Nmap, FTP, Anonymous Access | [View Writeup](./Tier-0/Fawn/) |

---

# Topics Covered

As this repository grows, the topics will include:

### Reconnaissance & Enumeration

- Nmap
- Port scanning
- Service enumeration
- Version detection
- Operating-system detection
- NSE scripts
- Full-port scanning
- Network reconnaissance

### Networking

- TCP/IP
- TCP ports
- UDP
- DNS
- HTTP/HTTPS
- FTP
- SSH
- Telnet
- SMB
- RDP
- SMTP
- SNMP

### Linux

- Linux filesystem
- Permissions
- Users and groups
- Processes
- Services
- SUID/SGID
- Cron
- Environment variables
- PATH manipulation
- Linux privilege escalation

### Windows

- Windows filesystem
- Users and groups
- Services
- PowerShell
- Windows permissions
- Registry
- Scheduled tasks
- Windows privilege escalation
- Active Directory

### Web Security

- HTTP
- Authentication
- Authorization
- IDOR/BOLA
- SQL injection
- XSS
- SSRF
- File inclusion
- Command injection
- File upload vulnerabilities
- Business logic
- API security

### Exploitation

- Public exploits
- Manual exploitation
- Proof of concept development
- Shells
- Reverse shells
- Payloads
- Exploit modification

### Post-Exploitation

- Enumeration after initial access
- Credential discovery
- Privilege escalation
- Persistence concepts
- Lateral movement
- Data discovery

---

# Tools I expect to use throughout the journey:

- Nmap
- Burp Suite
- Netcat
- Gobuster
- ffuf
- Feroxbuster
- Nikto
- WhatWeb
- SQLmap
- Metasploit
- Impacket
- Responder
- BloodHound
- CrackMapExec / NetExec
- Wireshark
- John the Ripper
- Hashcat
- Linux command-line utilities
- PowerShell
  
---

# One of the main skills I am developing is a repeatable enumeration process.

A simplified methodology (what I do) :

```text
1. Identify target
        ↓
2. Confirm scope
        ↓
3. Discover open ports
        ↓
4. Identify services
        ↓
5. Identify versions
        ↓
6. Enumerate interesting services
        ↓
7. Identify attack surface
        ↓
8. Form hypotheses
        ↓
9. Test hypotheses
        ↓
10. Gain initial access
        ↓
11. Enumerate from inside
        ↓
12. Privilege escalation
        ↓
13. Capture flags
        ↓
14. Document the attack path
