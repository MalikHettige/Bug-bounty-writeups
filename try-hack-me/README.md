# TryHackMe Room Notes
Directory created: 23:10:2026
Notes and technical breakdowns from TryHackMe rooms, written up as I complete them — covering the underlying vulnerability, root cause, exploitation steps, and detection/mitigation, not just room walkthrough answers.

## Purpose

This directory is separate from `/business-logic` and the rest of the bug-bounty writeups — TryHackMe rooms are often CVE-specific, runtime/infrastructure-level, or exploit-dev focused rather than web application business logic, so they get their own space.

## Format

Each room gets its own file, named after the room/vulnerability:

```
room-name.md
```

Each file generally covers:
- What the vulnerability is and why it matters
- Root cause (the actual underlying flaw, not just symptoms)
- Exploitation steps/commands, with explanations
- Detection and mitigation
- Key terms worth remembering

## Index

| Room | Vulnerability | CVE(s) | Status |
|---|---|---|---|
| PHP2Shell | [PHP runtime memory corruption → unauthenticated RCE](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/try-hack-me/PHP2Shell%20-%20Room%20Notes.md) | CVE-2026-109618, CVE-2026-109619 | Complete |

## Note

These are learning notes, not bug bounty findings — no live target is implicated. Kept here for reference and pattern-recognition across unrelated hunting work.
