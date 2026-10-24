# File Upload Vulnerabilities

Learning notes and PortSwigger Web Security Academy labs covering insecure file
upload handling, storage, and retrieval.

## Learning path

- [File upload vulnerabilities](https://portswigger.net/web-security/file-upload)

## Labs

- [Remote code execution via web shell upload](labs/Lab%20-%20Remote%20code%20execution%20via%20web%20shell%20upload.md)
- [Web shell upload via Content-Type restriction bypass](labs/Lab%20-%20Web%20shell%20upload%20via%20Content-Type%20restriction%20bypass.md)

## Key concepts

- Validate uploads on the server using a narrow allowlist that matches the
  feature's actual requirements. Do not rely on a client-supplied filename or
  `Content-Type` header.
- Store uploaded files outside the web root, or serve them through a handler
  that never interprets user-controlled content as executable code.
- If users only need to upload images, decode and re-encode the image using a
  trusted library, and apply size and dimension limits.
- Generate storage names server-side, enforce authorization and CSRF protection,
  and run upload processing with least privilege.

## Defensive testing reference

- [PHP Upload Security Testing Reference](../resources/php-upload-security-testing.md)

## References

- [PortSwigger: File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
