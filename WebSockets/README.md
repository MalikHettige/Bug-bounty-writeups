# WebSockets

Learning notes and PortSwigger Web Security Academy labs about WebSocket
protocols, message handling, and application security.

## Learning path

- [WebSockets](https://portswigger.net/web-security/websockets)

## Labs

- [Manipulating WebSocket messages to exploit vulnerabilities](labs/Lab%20-%20Manipulating%20WebSocket%20messages%20to%20exploit%20vulnerabilities.md)
- [Cross-site WebSocket hijacking](labs/Lab%20-%20Cross-site%20WebSocket%20hijacking.md)
- [Manipulating the WebSocket handshake to exploit vulnerabilities](labs/Lab%20-%20Manipulating%20the%20WebSocket%20handshake%20to%20exploit%20vulnerabilities.md)

## Research Notes & Disclosed Reports

- [The Loud Failure: How a Broken WebSocket Leaked a Master Key to the Backend](https://github.com/MalikHettige/Research-notes/blob/main/websocket/Broken%20WebSocket-Leaked-a-Master-Key.md) — third-party BaaS token leak via a broken WebSocket connection error, pivoted into an over-privileged backend token.
- [CVE-2025-10148: Predictable WebSocket Mask (curl)](https://github.com/MalikHettige/Bug-bounty-reports/blob/main/disclosed-report-analysis/WebSocket/Predictable-WebSocket-Mask.md) — disclosed HackerOne report analysis: reused masking key violating RFC 6455 §5.3.

## Key concepts

- Treat WebSocket messages as untrusted input, just like HTTP request data.
- Enforce validation and context-appropriate output encoding on the server.
- Validate authorization for every sensitive action carried over a WebSocket.
- Avoid rendering untrusted message content as HTML; use safe text APIs by default.

## References

- [PortSwigger Web Security Academy: WebSockets](https://portswigger.net/web-security/websockets)
- [PortSwigger: WebSocket vulnerabilities](https://portswigger.net/web-security/websockets)
- [OWASP WebSocket Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html)
- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP Cross Site Scripting (XSS)](https://owasp.org/www-community/attacks/xss/)
- [CWE-79: Improper Neutralization of Input During Web Page Generation](https://cwe.mitre.org/data/definitions/79.html)
