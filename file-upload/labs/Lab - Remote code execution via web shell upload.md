# Lab - Remote code execution via web shell upload

**Platform:** PortSwigger Web Security Academy  
**Category:** File Upload  
**Difficulty:** Apprentice  
**Date Solved:** 2026-10-24  
**Severity:** High in the lab scenario; production severity depends on execution context and accessible data  
**Time Spent:** Approximately 32 minutes

## Summary

The avatar upload accepts a server-side script file without effective type
validation, stores it under a publicly retrievable path, and serves that file
through a handler that executes PHP. A follow-up request to the uploaded file
therefore ran the script and returned the contents of the lab's designated
secret file. The lab was solved.

This demonstrates why upload validation and storage isolation are both
necessary: an upload is especially dangerous when the file is both retrievable
and interpreted as executable code.

## Affected Component

- Upload endpoint: `POST /my-account/avatar`
- Uploaded-file path: `/files/avatars/<uploaded-filename>`
- Lab: [Remote code execution via web shell upload](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload)

The lab host and authenticated session value are intentionally omitted because
they are temporary lab-specific details.

## Steps to Reproduce

1. Log in to the authorized lab account and open `/my-account`.
2. Upload a normal avatar while observing the request in Burp Suite.
3. Note the multipart upload to `/my-account/avatar` and the subsequent
   retrieval of the image from `/files/avatars/`.
4. In the lab only, replace the image with a PHP proof-of-concept file that
   reads the lab-designated secret file. The executable payload is omitted from
   this write-up.
5. The application reports that the file was uploaded. Request the uploaded
   filename from `/files/avatars/`.
6. Observe that the response contains the script's output, confirming the
   server interpreted the uploaded file. Submit the returned value to complete
   the lab.

## Proof of Concept

The following is a redacted request outline, not a ready-to-send exploit. The
session value, lab hostname, multipart boundary, file content, and returned
secret are not included.

```bash
POST /my-account/avatar HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
Content-Type: multipart/form-data; boundary=<multipart-boundary>

--<multipart-boundary>
Content-Disposition: form-data; name="avatar"; filename="myexploit.php"
Content-Type: <client-supplied-part-type>

[Lab-only PHP proof-of-concept omitted]
--<multipart-boundary>--

GET /files/avatars/myexploit.php HTTP/2
Host: <authorized-lab-host>
Cookie: session=<authorized-lab-session>
```

**Observed evidence:** The retrieval request returned `HTTP/2 200 OK` and the
lab secret as the response body. The secret is intentionally redacted.

Changing the multipart part's `Content-Type` to `php` was not necessary in this
lab. A client-supplied part type is metadata, not proof of the file's real
format; whether a retrieved file executes depends on server-side routing and
configuration, including the handler assigned to its extension.

## Root Cause

The upload flow did not enforce an effective server-side allowlist for the
expected avatar format. It retained a user-controlled executable extension and
stored the result at a path where the web server executed PHP requests. The
application therefore trusted uploaded content and placed it in an executable
context.

The vulnerable behavior is not merely that the upload accepted a file named
`.php`: execution of a retrieved upload is also dependent on the web server's
configuration and the storage location.

## Impact

**Technical**

- Remote code execution with the privileges of the PHP/web application process.
- Access to files and application resources available to that process; in this
  lab, the script disclosed the designated secret.
- Potential integrity and availability impact if the execution context permits
  file modification or other side effects.

**Business / Real-World**

- Exposure of sensitive data and possible compromise of application functions
  accessible to the web process.
- Further impact depends on process privileges, network access, isolation, and
  the presence of additional controls. Do not assume that a file-upload issue
  automatically grants operating-system-level control.

**Scope**

The demonstrated impact is limited to the authorized PortSwigger lab instance.
No production system was tested.

## Remediation

- Allow only the minimum required image formats using server-side validation;
  do not trust the filename extension or client-supplied MIME type alone.
- Decode and re-encode accepted images with a maintained image-processing
  library, and reject malformed or unexpected content.
- Generate storage names server-side and normalize/restrict filenames.
- Store uploads outside the web root, or serve them through a download handler
  that treats content as data and cannot execute it.
- Disable script execution in upload directories as defense in depth.
- Apply upload size and dimension limits, authorization, CSRF protection, and
  least-privilege permissions to upload and processing components.

## Lessons Learned & Patterns

- Trace the complete lifecycle: upload request, server response, stored path,
  and later retrieval request.
- A successful upload response confirms storage, not safety. Test in an
  authorized environment whether the uploaded object is served as data or
  interpreted by the server.
- Multipart `Content-Type` is client-controlled and should not be treated as
  authoritative validation.
- RCE impact depends on server-side execution configuration and the privileges
  of the process handling the request.
- Keep lab credentials, session cookies, and returned secrets out of published
  notes.

## References

- [PortSwigger: File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [PortSwigger lab: Remote code execution via web shell upload](https://portswigger.net/web-security/file-upload/lab-file-upload-remote-code-execution-via-web-shell-upload)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)

**Tags:** #PortSwigger #FileUpload #RCE #CWE434
