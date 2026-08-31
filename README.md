# Bug Bounty Writeups — Malik Hettige, 17
Writeups from my bug bounty hunting practice and live findings. Focus: IDOR, broken access control, authentication, business logic as foundation for now.

## What's in here
- `portswigger-labs/` — PortSwigger Web Security Academy writeups, organized by vulnerability category.
- [Hack The Box Academy](https://github.com/MalikHettige/Bug-bounty-writeups/tree/main/hack-the-box-academy) — Academy module notes and hands-on labs.
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
  
## Vulnerability Focus (the foundation)
- [Business Logic](https://github.com/MalikHettige/Bug-bounty-writeups/tree/main/business-logic)
- [Authentication](https://github.com/MalikHettige/Bug-bounty-writeups/tree/main/authentication)
- [Access Control (keep warm)](https://github.com/MalikHettige/Bug-bounty-writeups/tree/main/access-control-idor)
- [Classic Request Smuggling (do this before the CRLF paper)](https://portswigger.net/web-security/request-smuggling)
- [SSTI Basics (do this before the blind-detection paper)](https://portswigger.net/web-security/server-side-template-injection)

# Learning paths from PortSwigger, tiered

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

# Tracking pipeline
- [PortSwigger Research](https://portswigger.net/research) — I check this at least once a month to stay current with new web security research.
- [PortSwigger Research RSS](https://portswigger.net/research/rss) — I keep this in a feed reader so I don't rely on remembering to check manually.
- [Top 10 Web Hacking Techniques of 2025](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) — I read the entire list, including the rejected nominees at the bottom, to see what techniques researchers are exploring.
- **r/websecurityresearch** — I search this subreddit directly for community research, techniques, and discussions.

# Class-Specific Primary / Foundational Reading

- **Request Smuggling:** I read Kettle's original 2019 *HTTP Desync Attacks* research before moving on to the 2025/2026 papers. I treat it as the conceptual foundation.
- **SSTI:** I read Kettle's original 2015 *Server-Side Template Injection: RCE for the Modern Web App* before moving on to the later research.
- **Prototype Pollution:** I keep Gareth Heyes' *Server-side prototype pollution: Black-box detection without the DoS* as my reserve research path.
- **SAML:** I study OWASP's SAML Security Cheat Sheet and the [SAML Raider](https://github.com/CompassSecurity/SAMLRaider) Burp extension documentation.
- **ORM-Leak:** I read Django's and Prisma's official query/filter documentation first so I understand correct filter behavior before studying how it can be abused.

# Execution Plan

- **This week:** I join one CTF team through CTFtime and publish my Django-lab work as a short public writeup, even if it's rough. I'm building my connections track alongside my technical development.
- **Next 2 weeks:** I build and test the ORM-Leak lab on my Django environment, starting with the filter-driven endpoint.
- **Ongoing until January:** I continue VDP hunting for live experience and reputation, while studying advanced vulnerability-chain research alongside it rather than replacing hands-on hunting.

## Platforms
- Bugcrowd  (active from January 2027)
- HackerOne (active from January 2027)
- Intigriti (active from January 2027)

## Contact
- X: https://x.com/MalikHettige
- Email: Malikdishan09@gmail.com
