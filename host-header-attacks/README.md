# HTTP Host Header Attacks

Writeups on vulnerabilities arising from applications trusting the client-supplied `Host` header (and related headers like `X-Forwarded-Host`) for security-relevant logic — password reset link generation, cache keys, SSO redirects, and other absolute-URL construction.

## Labs

- [Basic password reset poisoning via Host header injection](<labs/Lab - Basic password reset poisoning via Host header injection.md>) — Full unauthenticated account takeover: the password reset endpoint accepts an arbitrary username and trusts the `Host` header to build the reset link, letting an attacker redirect a victim's real reset token to attacker-controlled infrastructure with zero victim interaction.
- [Host header authentication bypass](<labs/Lab - Host header authentication bypass.md>) — Admin panel access control gated on `Host: localhost` as a stand-in for verified internal network origin. Setting that header externally grants full admin read/write access, including arbitrary user deletion, from an unauthenticated public position.

## Core idea

The `Host` header is attacker-controlled input, not trusted server metadata. Any logic that uses it to build a URL, cache key, or redirect target inherits that untrustworthiness. Severity hinges on whether the attacker can trigger the vulnerable action against an arbitrary victim (worse — no social engineering needed) or only against themselves/with victim interaction required (lower severity, phishing-adjacent).
