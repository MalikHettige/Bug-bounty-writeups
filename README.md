# Bug Bounty Writeups

Writeups from hands-on web security training and live bug bounty work, written by **Malik Hettige**. Core focus: **IDOR / broken access control, authentication, and business logic vulnerabilities** as the foundation, built on top of a structured path through PortSwigger's Web Security Academy.

Every writeup follows the same format: summary, affected component, step-by-step reproduction, proof of concept, root cause, impact (technical + business), remediation, and lessons learned — not just "here's the bug," but the actual methodology and reasoning behind finding it, so the pattern transfers to real targets.

**Live bug bounty reports (real programs):** [Bug-bounty-reports](https://github.com/MalikHettige/Bug-bounty-reports)
**Research notes (external writeups, deep-dives):** [Research-notes](https://github.com/MalikHettige/Research-notes)

---

## Learning paths

### Completed
| Path | Labs |
| --- | --- |
| **OAuth 2.0** | [Authentication bypass via implicit flow](OAuth-2.0/labs/Lab%20-%20Authentication%20bypass%20via%20OAuth%20implicit%20flow.md) · [Account hijacking via redirect_uri](<OAuth-2.0/labs/Lab - OAuth account hijacking via redirect_uri.md>) · [Forced profile linking](<OAuth-2.0/labs/Lab - Forced OAuth profile linking.md>) · [SSRF via OpenID dynamic client registration](<OAuth-2.0/labs/Lab - SSRF via OpenID dynamic client registration.md>) · [Stealing tokens via open redirect](<OAuth-2.0/labs/lab - Stealing OAuth Access Tokens via an Open Redirect.md>) · [Stealing tokens via proxy page](<OAuth-2.0/labs/Lab - Stealing OAuth Access Tokens via a Proxy Page.md>) |
| **GraphQL** | [Accessing private posts](<graphql/labs/Lab - Accessing private GraphQL posts.md>) · [Accidental field exposure](<graphql/labs/Lab - Accidental exposure of private GraphQL fields.md>) · [Hidden endpoint discovery](<graphql/labs/Lab - Finding a hidden GraphQL endpoint.md>) · [Brute-force bypass via aliasing](<graphql/labs/Lab - Bypassing GraphQL brute force protections.md>) · [CSRF via content-type confusion](<graphql/labs/Lab - Performing CSRF exploits over GraphQL.md>) |

### In progress
| Path | Labs so far |
| --- | --- |
| **HTTP Host Header Attacks** | [Password reset poisoning via Host header injection](<host-header-attacks/labs/Lab - Basic password reset poisoning via Host header injection.md>) |

### Queued (priority order)
| Priority | Path | Why it matters |
| --- | --- | --- |
| P0 | HTTP Request Smuggling | Foundation under CRLF/desync attacks |
| P0 | Authentication | Session/identity mechanics |
| P0 | Business logic vulnerabilities | Core focus area |
| P0 | Server-side template injection | Foundation under blind SSTI → RCE |
| P1 | [File upload vulnerabilities](file-upload/) | Validation, storage, execution risks in upload flows |
| P1 | SQL injection (blind techniques especially) | Oracle-hunting skill shared with SSTI/ORM-leak exfiltration |
| P1 | Server-side prototype pollution | RCE fallback path |
| P1 | JWT | Token/identity foundation |
| P2 | Web cache poisoning | Pairs with request smuggling |
| P2 | SSRF | Cloud/internal network pivoting |
| P2 | Insecure deserialization | General object-handling → RCE pattern |

---

## Repository structure

```
.
├── access-control-idor/     # IDOR, broken access control
├── API-testing/              # Mass assignment, SSPP, API endpoint abuse
├── authentication/            # 2FA bypass, brute-force, password reset
├── business-logic/            # Workflow/logic flaws
├── CORS/                      # CORS misconfiguration
├── file-upload/                # Web shell upload, RCE via upload
├── graphql/                    # GraphQL-specific vulnerabilities
├── host-header-attacks/        # Host header trust failures
├── JWT/                         # JWT forgery, signature bypass
├── OAuth-2.0/                   # OAuth flow abuse, token theft
├── OS-command-injection/         # OS command injection
├── path-traversal/               # File path traversal
├── sql/                            # SQL injection
├── WebSockets/                     # WebSocket handshake/message manipulation
├── bug-hunter-skill-progression/    # Personal roadmap and skill tracking
├── hack-the-box-academy/             # HTB Academy module notes
├── try-hack-me/                       # TryHackMe notes
├── resources/                          # Reference material (e.g. PHP upload security)
├── writeup-template.md                 # Standard writeup template
└── LICENSE
```

Each vulnerability-class folder follows the same pattern: `<category>/labs/Lab - <name>.md`, with a sibling `assets/` folder for PoC screenshots where used.

---

## Methodology

Writeups prioritize **chaining over single-bug reporting** for critical-severity targets — training to recognize how a low-impact finding (an open redirect, an over-exposed field, a header trust failure) becomes a full account takeover when combined with a second weakness. Submission strategy on live programs is mixed-severity: valid findings get reported as soon as they're confirmed rather than held for a bigger chain.

## Platforms
- Bugcrowd, HackerOne, Intigriti, HackenProof, YesWeHack

## Contact
- X: [@MalikHettige](https://x.com/MalikHettige)
- Email: malikdishan09@gmail.com

## License
MIT — see [LICENSE](LICENSE).
