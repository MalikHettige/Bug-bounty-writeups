# Path Traversal

Learning notes and PortSwigger Web Security Academy labs about path traversal
vulnerabilities and unsafe handling of user-controlled file paths.

## Learning path

- [Path traversal](https://portswigger.net/web-security/file-path-traversal)

## Labs

- [File path traversal, simple case](labs/Lab%20-%20File%20path%20traversal%2C%20simple%20case.md)
- [File path traversal, traversal sequences blocked with absolute path bypass](labs/Lab%20-%20File%20path%20traversal%2C%20traversal%20sequences%20blocked%20with%20absolute%20path%20bypass.md)
- [File path traversal, traversal sequences stripped non-recursively](labs/Lab%20-%20File%20path%20traversal%2C%20traversal%20sequences%20stripped%20non-recursively.md)
- [File path traversal, traversal sequences stripped with superfluous URL-decode](labs/Lab%20-%20File%20path%20traversal%2C%20traversal%20sequences%20stripped%20with%20superfluous%20URL-decode.md)
- [File path traversal, validation of start of path](labs/Lab%20-%20File%20path%20traversal%2C%20validation%20of%20start%20of%20path.md)
- [File path traversal, validation of file extension with null byte bypass](labs/Lab%20-%20File%20path%20traversal%2C%20validation%20of%20file%20extension%20with%20null%20byte%20bypass.md)

## Key concepts

- Treat filenames and paths received from users as untrusted input.
- Resolve requested files against an intended base directory and verify the
  canonical resolved path remains within that directory.
- Prefer server-generated file identifiers over accepting filesystem paths.
- Apply least-privilege access to the process that reads files.

## References

- [PortSwigger: Directory traversal](https://portswigger.net/web-security/file-path-traversal)
- [Path traversal wordlist](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/resources/Path-traversal-wordlist.txt)
- [OWASP: Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)
