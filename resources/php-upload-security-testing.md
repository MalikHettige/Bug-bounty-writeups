# PHP Upload Security Testing Reference

Use this checklist to assess PHP-backed upload features in systems you own or
are explicitly authorized to test. It focuses on validation and safe handling;
it does not provide executable web shells, command-execution payloads, or
post-compromise instructions.

## What to verify

- **Extension policy:** Define a narrow allowlist that matches the feature.
  Reject unneeded extensions and ambiguous or malformed filenames.
- **Actual content:** Validate the file using a suitable parser. Do not treat a
  filename, multipart `Content-Type`, or client-provided metadata as proof of
  the file's format.
- **Safe image processing:** For image features, decode and re-encode accepted
  images with a maintained library. Reject malformed files and enforce
  reasonable size and dimension limits.
- **Storage location:** Store uploads outside the web root where possible. If
  they must be downloadable, serve them through an application handler that
  treats them as data.
- **Execution behavior:** Ensure uploaded files cannot be interpreted as PHP.
  Disable script execution in upload storage as defense in depth.
- **File naming:** Generate storage names on the server. Avoid using a supplied
  path or filename directly.
- **Access controls:** Confirm upload and retrieval authorization, CSRF
  protection, and least-privilege filesystem permissions.
- **Processing controls:** Keep parsers updated and isolate file-processing
  workloads where appropriate.

## Safe verification approach

1. Obtain explicit authorization and define the permitted test environment.
2. Use benign test files and test accounts. Never upload executable code or
   access another user's data during production testing.
3. Compare the server's decisions for permitted and disallowed formats. Where
   allowed, use harmless mismatched metadata to confirm the server validates
   content rather than trusting request headers.
4. Inspect the upload response and retrieval behavior. Confirm retrieved
   content is served as inert data and cannot invoke a server-side interpreter.
5. Record the endpoint, test file type, response status, and relevant response
   headers without including credentials or personal data.
6. Stop if behavior indicates code execution, unintended data access, or impact
   outside the agreed scope. Report the evidence through the authorized
   disclosure channel.

## Defensive acceptance criteria

- Only required formats are accepted after server-side content validation.
- Client-controlled MIME metadata cannot override validation results.
- Uploaded objects receive server-generated names and are stored outside
  executable paths.
- Download responses use safe content handling and do not invoke PHP.
- Upload size, processing resource use, authorization, and CSRF are controlled.

## References

- [PortSwigger: File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
