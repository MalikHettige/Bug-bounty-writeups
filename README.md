# Bug Bounty Writeups — Malik Hettige, 17
Writeups from my bug bounty hunting practice and live findings. Focus: IDOR, broken access control, authentication, business logic as foundation for now.

## What's in here
- `portswigger-labs/` — PortSwigger Web Security Academy writeups, organized by vulnerability category.
- `hack-the-box-academy/` — Academy module notes and hands-on labs.
- `tryhackme/` — Web Fundamentals and web security learning notes.
- `pentesterlab/` — PentesterLab exercise writeups and notes.
- `overthewire/` — Linux and command-line challenge writeups.
- `burp-suite-certified-practitioner/` — Exam preparation notes, labs, and methodology.
- `bug-hunter-skill-progression/` — Personal roadmap, checklists, and progress tracking.
- `random-lessons/` — Security concepts, research notes, and miscellaneous documentation.
- `writeup-template.md` — Standard template used for documenting writeups.
- `README.md` — Repository overview and structure.
- `LICENSE` — MIT License for this repository.
- `.gitignore` — Excludes unnecessary files from version control.
  
## Vulnerability Focus
- Broken Access Control
- Authentication Bypass
- IDOR
- Business Logic

  ### Learning paths from PortSwigger, tiered

| Priority | Path | Why it matters here |
| --- | --- | --- |
| P0 | HTTP Request Smuggling | Direct foundation under CRLF desync |
| P0 | Authentication | Session/identity mechanics under Stage 2 |
| P0 | Business logic vulnerabilities | Stage 5 |
| P0 | Server-side template injection | Direct foundation under blind SSTI/RCE |
| P1 | SQL injection, especially the blind techniques | This is the actual intellectual root of both the SSTI paper and the ORM-Leak exfil technique — error-based/boolean-based oracle-hunting is one skill applied twice |
| P1 | Server-side prototype pollution | RCE fallback path |
| P1 | OAuth authentication | Identity-flow foundation that transfers conceptually toward SAML, even though SAML itself isn't in Academy |
| P1 | JWT | Token/identity foundation, connects to my existing playbook material |
| P2 | Web cache poisoning | Pairs naturally with smuggling |
| P2 | SSRF | Cloud/internal pivoting — matches interests I've already shown |
| P2 | Insecure deserialization | General "reach RCE through object handling" pattern, complements the RCE course already in my Notion |

## Platforms
- Bugcrowd  (active from January 2027)
- HackerOne (active from January 2027)
- Intigriti (active from January 2027)

## Contact
- X: https://x.com/MalikDisha8108
- Email: Malikdishan09@gmail.com
