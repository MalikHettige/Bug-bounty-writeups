# Lab - Web shell upload via Content-Type restriction bypass

**Platform:** PortSwigger Web Security Academy  
**Category:** File Upload  
**Difficulty:** Apprentice  
**Date Solved:** 2026-10-24  
**Severity:** High in the lab scenario; production severity depends on execution context and accessible data

## Summary

The avatar feature reports that it only accepts JPEG and PNG images. Testing
confirmed that a WebP image was rejected. However, the server enforced this
restriction using the client-controlled multipart part `Content-Type` rather
than validating the uploaded file's actual content or ensuring that the saved
file was safe to serve.

In the authorized lab, changing that part's MIME type to `image/jpeg` allowed
the PHP file to be uploaded with its `.php` filename unchanged. Requesting the
uploaded path then caused the server to execute the script, returning the
lab's designated secret. The lab was solved.

## Affected Component

- Upload endpoint: `POST /my-account/avatar`
- Uploaded-file path: `/files/avatars/<uploaded-filename>`
- Lab: [Web shell upload via Content-Type restriction bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-content-type-restriction-bypass)

The lab hostname, session cookie, and returned secret are omitted because they
are temporary lab-specific data.

## Steps to Reproduce

1. Log in to the authorized lab account and open `/my-account`.
2. Upload an image and observe the multipart request to
   `POST /my-account/avatar`.
3. Confirm the upload flow accepts JPEG and PNG images, while a WebP upload
   produces an error stating that only JPEG and PNG are allowed.
4. In the lab only, intercept the multipart upload for a PHP proof-of-concept
   file. Keep the `.php` filename and change the part's `Content-Type` to
   `image/jpeg`. The executable payload is omitted from this report.
5. Observe that the application reports a successful upload.
6. Request the uploaded file from `/files/avatars/<uploaded-filename>`.
   The server executes the file and responds with the lab secret.

## Proof of Concept

This redacted request outline demonstrates the validation mismatch without
including a live session, host, multipart boundary, executable file body, or
secret. It is not a ready-to-send exploit.

```bash
POST /my-account/avatar HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
Content-Type: multipart/form-data; boundary=<multipart-boundary>

--<multipart-boundary>
Content-Disposition: form-data; name="avatar"; filename="myexploit.php"
Content-Type: image/jpeg

[Lab-only PHP proof-of-concept omitted]
--<multipart-boundary>--

GET /files/avatars/myexploit.php HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
```

**Observed evidence:** The upload returned a success message, and retrieval of
the uploaded `.php` path returned `HTTP/2 200 OK` with the lab secret in the
response body. The secret is intentionally redacted.

For a defensive checklist on validating uploads and confirming that retrieved
files are handled as inert data, see the [PHP Upload Security Testing
Reference](../../resources/php-upload-security-testing.md).

## Root Cause

The server treated the multipart part's client-supplied `Content-Type` as
reliable evidence of the file type. An attacker could label non-image content
as `image/jpeg`, bypassing the allowlist while retaining a PHP extension.
Because the uploaded file was saved under a web-accessible path configured to
execute PHP, retrieval executed the uploaded script.

An extension check alone would not be sufficient either: robust handling must
validate and safely process the actual content, and uploaded files should not
be executable when served.

## Impact

**Technical**

- Remote code execution in the context of the web application process.
- Access to files and resources available to that process; the lab proof of
  concept disclosed the designated secret.
- Potential integrity or availability impact depending on process privileges
  and environment configuration.

**Business / Real-World**

- Sensitive data exposure or compromise of application functionality reachable
  by the web process.
- The practical impact depends on isolation, filesystem permissions, network
  access, and other defense-in-depth controls.

**Scope**

Testing was limited to the authorized PortSwigger lab. No production system
was tested.

## Remediation

- Do not trust multipart `Content-Type` or the supplied filename as proof of
  file type.
- Enforce a narrow server-side allowlist and validate the actual file content
  with an appropriate parser.
- For avatars, decode and re-encode accepted images with a maintained library
  and reject malformed or unexpected content.
- Generate storage names on the server and store uploads outside the web root,
  or serve them through a handler that treats them only as data.
- Disable script execution in upload locations and use least-privilege
  permissions as defense in depth.
- Apply file-size and image-dimension limits, authorization, and CSRF
  protections to the upload workflow.

## Lessons Learned & Patterns

- An error message that lists allowed MIME types describes a policy, not proof
  that the server verifies the underlying file format.
- Distinguish the multipart part's `Content-Type` from the filename extension;
  they are separate attacker-controlled inputs.
- A successful upload is not itself proof of execution. Follow the object's
  retrieval path and inspect how the server handles it, only within authorized
  scope.
- This lab builds on the unrestricted-upload case: a content-type restriction
  can be bypassed if the server trusts the request metadata.
- Keep lab credentials, session cookies, executable payloads, and returned
  secrets out of published notes.

## References

- [PortSwigger: File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [PortSwigger lab: Web shell upload via Content-Type restriction bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-content-type-restriction-bypass)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
- [The PHP upload security testing payload resources](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/resources/php-upload-security-testing.md)

**Tags:** #PortSwigger #FileUpload #ContentType #RCE #CWE434
