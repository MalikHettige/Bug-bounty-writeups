# Tier 0 — Hack The Box Academy

The starting tier. No exploitation, no chaining — just the core loop
every real engagement is built on:

```text
Discover → Identify → Enumerate → Investigate
```

Every machine here exists to drill one habit: **check the obvious thing
before assuming you need something clever.** An open port, a default
credential, an anonymous login — Tier 0 is where you learn to actually
look for those before reaching for an exploit.

## Machines

| Machine | Focus | Key lesson |
|---|---|---|
| [Meow](./Meow) | Telnet, basic enumeration | Enumeration comes before exploitation, always |
| [Fawn](./Fawn) | FTP, anonymous access | Try anonymous/default access before assuming credentials are needed |

## Running theme so far

Both machines followed the identical shape: scan → find one open,
unencrypted, legacy service → walk in through a door that was never
locked. Nothing here required a real exploit. That's the point of Tier 0
— it's testing whether you enumerate properly, not whether you can
write shellcode.
