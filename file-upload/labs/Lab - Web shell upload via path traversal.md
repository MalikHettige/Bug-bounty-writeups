# Lab - Web shell upload via path traversal

**Platform:** PortSwigger Web Security Academy  
**Category:** File Upload / Path Traversal  
**Difficulty:** Practitioner  
**Date Solved:** 2026-10-25  
**Severity:** High in the lab scenario; production severity depends on execution context and accessible data

## Summary

The avatar upload accepted a PHP file, but files uploaded into the normal
`/files/avatars/` directory were served as plain text rather than executed.
The upload handler used the supplied filename when constructing its storage
path and attempted to strip directory traversal sequences. URL-encoding the
slash in the filename bypassed that filtering. After the server decoded the
filename, the traversal component moved the file out of the non-executable
avatar directory and into `/files/`, where PHP execution was enabled.

Requesting the uploaded file from `/files/exploit.php` executed the lab-only
proof of concept and returned the lab's designated secret. The lab was solved.

## Affected Component

- Upload endpoint: `POST /my-account/avatar`
- Normal avatar path: `/files/avatars/<uploaded-filename>`
- Traversal destination in the lab: `/files/<uploaded-filename>`
- Lab: [Web shell upload via path traversal](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-path-traversal)

The lab hostname, session cookie, and returned secret are omitted because they
are temporary lab-specific data.

## Steps to Reproduce

1. Log in to the authorized lab account and upload a normal avatar. Observe the
   upload request and the image retrieval path under `/files/avatars/`.
2. In the lab only, upload a PHP proof-of-concept file. The executable payload
   is omitted from this report.
3. Request the PHP file from its normal `/files/avatars/` location. Observe
   that the PHP source is returned as plain text, indicating that this
   directory does not execute PHP.
4. Intercept the avatar upload and modify the multipart filename to include a
   traversal sequence with its slash URL-encoded. The executable payload is
   unchanged; only the destination filename is being tested.
5. Observe the upload confirmation and account for the decoded traversal
   sequence in the resulting path.
6. Request the resulting file from `/files/exploit.php`. In the lab, this
   location executes the PHP file and returns the designated secret.

## Proof of Concept

This redacted request outline shows the relevant path-handling behavior. It
omits the live host, session, executable file body, and returned secret; it is
not a ready-to-send exploit.

```bash
POST /my-account/avatar HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
Content-Type: multipart/form-data; boundary=<multipart-boundary>

--<multipart-boundary>
Content-Disposition: form-data; name="avatar"; filename="..%2fexploit.php"
Content-Type: <part-content-type>

[Lab-only PHP proof-of-concept omitted]
--<multipart-boundary>--

GET /files/exploit.php HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
```

**Observed evidence:** The initial request to the uploaded file in
`/files/avatars/` returned its PHP source as text. After changing the upload
filename, the file was reachable at `/files/exploit.php`; requesting that path
returned `HTTP/2 200 OK` with the lab secret as the response body. The secret
is intentionally redacted.

The avatar form field name identifies the form input; it does not guarantee
that the uploaded file remains within an avatar directory. In this lab, the
server's path construction and decoding order made the client-supplied filename
influence the final storage path. The file's execution behavior then depended
on the server configuration for the destination directory.

## Root Cause

The upload handler incorporated a user-controlled filename into a filesystem
path and relied on incomplete traversal filtering. The filter processed the
encoded filename differently from the later URL-decoding or path-resolution
step, allowing traversal syntax to survive validation and affect the
destination.

The application also relied on directory-specific execution configuration as
a boundary: PHP was not executed in the avatar subdirectory, but was executable
in its parent directory. Moving an uploaded script across that boundary
changed a harmless source disclosure into server-side code execution.

## Impact

**Technical**

- The demonstrated chain resulted in PHP execution as the web application
  process from an upload feature.
- The lab proof of concept disclosed its designated secret.
- Other impact depends on the privileges, filesystem access, and network
  reachability of the process handling the request.

**Business / Real-World**

- Sensitive data or application functionality available to the web process
  could be exposed or affected.
- Impact is contingent on the upload path being writable and the destination
  being executable; path traversal alone does not guarantee code execution.

**Scope**

Testing was limited to the authorized PortSwigger lab. No production system
was tested.

## Remediation

- Do not use a client-supplied filename as a filesystem path component.
  Generate an opaque storage name server-side and discard path separators.
- Canonicalize and validate paths after decoding, then verify the resolved
  destination remains within the intended upload directory.
- Avoid security checks based on string filtering alone; validate the final
  resolved path and reject traversal outside the configured storage root.
- Store uploads outside the web root and serve them through a handler that
  treats files as inert data.
- Disable PHP and other script execution throughout all upload storage paths,
  including parent directories.
- Apply least-privilege filesystem permissions and retain content validation,
  size limits, authorization, and CSRF protections.

## Lessons Learned & Patterns

- An upload's form field name is not a security boundary for its storage path.
- Follow the complete path lifecycle: raw multipart filename, any decoding or
  normalization, server-side path construction, resolved storage location,
  and retrieval behavior.
- A file returned as source from one directory may execute from another if
  server configuration differs by path.
- When confirming a traversal destination, test the canonical resulting path
  as well as the original encoded retrieval path; application routing and
  decoding can differ between upload and retrieval.
- Keep lab credentials, session cookies, executable payloads, and returned
  secrets out of published notes.
- For defensive validation guidance, see the
  [PHP Upload Security Testing Reference](../../resources/php-upload-security-testing.md).

## References

- [PortSwigger lab: Web shell upload via path traversal](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-path-traversal)
- [PortSwigger: File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [PortSwigger: Path traversal](https://portswigger.net/web-security/file-path-traversal)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)

**Tags:** #PortSwigger #FileUpload #PathTraversal #RCE #CWE434 #CWE22
