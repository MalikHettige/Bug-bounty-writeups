# Methodology: File-Write Primitive + SSRF Chaining to RCE

**Source:** HackerOne report #1547877 (Aiven Ltd) — $5,000 bounty, Critical. Kafka Connect's JDBC sink connector allowed writing arbitrary SQLite database files to disk; a separate HTTP sink connector allowed SSRF to localhost, reaching an unauthenticated Jolokia (JMX-over-HTTP) interface on port 6725. The Jolokia interface exposed a `jvmtiAgentLoad` operation that could load a Java agent — the attacker embedded a reverse-shell Java agent as a BLOB inside the written SQLite file, then used the SSRF'd Jolokia call to load it, achieving full RCE.

**Phase:** Post-primitive-discovery chaining — after confirming either a file-write/upload primitive OR an SSRF primitive individually, actively look for the other one on the same target before writing up either as a standalone low/medium finding.

**Trigger:** Any component that can write attacker-influenced file content to disk (not just classic upload forms — JDBC drivers, import/export features, log file writers, cache files, temp file handling all count) co-existing with any component that can make outbound HTTP requests to attacker-chosen or at least partially-controllable destinations (SSRF, webhook configs, URL-fetch features, connector/integration configs).

**Action:**
1. Confirm the file-write primitive and what file types/content you can control.
2. Confirm the SSRF primitive and whether it can reach localhost/internal-only addresses.
3. Enumerate internal-only services reachable via the SSRF — specifically management/diagnostic interfaces that assume "localhost-only = safe" (JMX/Jolokia, admin consoles, metrics endpoints, debug ports), since these frequently have zero authentication.
4. Check whether any reachable internal interface has an operation that can consume/execute a file from disk (load an agent, import a config, execute a script). If so, combine: write a malicious payload to disk via primitive #1, trigger its execution via the internal interface reached through primitive #2.

**Backups:**
- If no internal interface accepts file execution directly, check whether the SSRF can at least read internal-only config/credentials that unlock a different path.
- If the file-write primitive can't control file type/extension, check whether it can still overwrite an existing config/script file the app already trusts and executes.
