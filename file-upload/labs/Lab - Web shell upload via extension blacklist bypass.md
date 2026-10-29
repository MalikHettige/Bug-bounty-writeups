# Lab - Web shell upload via extension blacklist bypass

**Platform:** PortSwigger Web Security Academy
**Category:** File Upload
**Difficulty:** Practitioner
**Date Solved:** 2026-10-25
**Severity:** Critical (CVSS 3.1 ≈ 9.1)

## Summary

The avatar upload feature used a filename-extension blacklist that rejected a standard PHP extension but accepted a custom suffix. The lab's Apache configuration could be influenced through a per-directory configuration file, allowing the uploaded file with that suffix to be handled as PHP. Requesting the uploaded file then returned the lab's designated secret.

The result demonstrates why an extension blacklist is not a sufficient file-upload control: the effective behavior of an uploaded file can depend on the web server's handler configuration, not just its filename.

## Affected Component

- Upload endpoint: `POST /my-account/avatar`
- Uploaded-file path: `/files/avatars/<uploaded-filename>`
- Lab: [Web shell upload via extension blacklist bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass)

The lab hostname, session data, executable payload, and returned secret are omitted.

## Steps to Reproduce

1. In the authorized lab, upload a normal PNG image and inspect the multipart upload request.
2. Attempt a lab-only PHP proof-of-concept file using a conventional script extension. The application rejects it, confirming that the upload applies an extension-based restriction.
3. Inspect the response headers to identify Apache. This platform evidence made a per-directory configuration test relevant; it would not establish that the same technique applies to other web servers.
4. In the isolated lab, use the upload behavior and server configuration to associate an accepted custom suffix with PHP handling. The exact configuration directive and executable file body are intentionally omitted.
5. Request the uploaded file from its avatar URL. The response contains the expected lab secret, confirming server-side execution.

## Proof of Concept

The following is a redacted account of the two requests. It omits the configuration-file contents, executable PHP body, session data, and lab secret; it is not a ready-to-send exploit.

```http
POST /my-account/avatar HTTP/2
Content-Disposition: form-data; name="avatar"; filename="myexploit.[accepted-suffix]"
Content-Type: image/png

[Lab-only file content omitted]
```

The upload returned `HTTP/2 200 OK` and confirmed that the avatar file had been stored. A subsequent request to `/files/avatars/<uploaded-filename>` returned `HTTP/2 200 OK` with the lab's expected secret, demonstrating that the server processed the uploaded file rather than serving its source.

## Root Cause

The application relied on a blacklist of known script extensions and allowed a user-controlled configuration file to affect how files in the upload directory were handled. The upload and retrieval paths therefore formed a single trust boundary: an uploaded file could change server interpretation of another uploaded file.

The Apache response header was useful for selecting a platform-specific hypothesis, but server identification alone does not prove that per-directory overrides are enabled. In this lab, the observed execution result confirmed that the configuration change took effect.

## Impact

**Technical**
- A user able to upload files could cause an accepted file to be interpreted as server-side code.
- The demonstrated lab file disclosed the lab's designated secret when requested.

**Business / Real-World**
- If equivalent behavior existed in a production upload path, code execution could expose or alter data available to the web-server process.
- The extent of impact would depend on upload authorization, server configuration, process privileges, and the data and services reachable from that process.

**Scope**
- Demonstrated only against the isolated PortSwigger Web Security Academy lab. No production system was tested.

## Remediation

- Do not rely on a blacklist of executable extensions. Enforce a narrow server-side allowlist based on the feature's requirements and validate file content with a trusted parser.
- Do not allow uploaded files to define or override web-server configuration. Disable per-directory overrides for upload locations and reject configuration filenames.
- Store uploads outside the web root and serve them through a handler that treats them only as inert data.
- Generate storage names server-side, apply least privilege, and prevent users from selecting paths or handlers.
- Add regression tests for configuration filenames, alternate extensions, and file retrieval behavior.

## Investigation Notes

- **Baseline question:** Would a standard PHP file be rejected, and which part of the upload policy was being enforced? The initial rejection provided evidence that the conventional extension was blocked, but did not establish that all executable content was safely handled.
- **Platform hypothesis:** The Apache header suggested that testing a per-directory configuration boundary was relevant. This was a platform-specific hypothesis, not a general upload bypass.
- **Bypass hypothesis:** A configuration file might not be covered by a blacklist focused on executable payload extensions. The successful lab result confirmed that the server honored the uploaded configuration.
- **Verification:** The upload success response alone was insufficient. Requesting the stored file and observing the lab's expected output provided evidence that the server interpreted it as code.

## Lessons Learned & Patterns

- Test the complete upload-and-retrieval path; an accepted upload does not by itself establish whether a file will be stored safely or executed.
- A filename extension is not a reliable indicator of how a server will handle a file when configuration can change handler mappings.
- Platform identification helps narrow hypotheses, but verify the relevant server feature and effective configuration before concluding it is exploitable.
- Treat uploaded configuration files as a separate risk from uploaded content, and prevent untrusted users from changing server behavior.
- Distinguish evidence of upload acceptance from evidence of server-side execution.

## References

- [PortSwigger Web Security Academy: Web shell upload via extension blacklist bypass](https://portswigger.net/web-security/file-upload/lab-file-upload-web-shell-upload-via-extension-blacklist-bypass)
- [TechEarl: File upload vulnerabilities - double extension and the Apache AddHandler trap](https://techearl.com/file-upload-vulnerabilities#pattern-4-double-extension-and-the-apache-addhandler-trap)
- [Repository: PHP Upload Security Testing Reference](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/resources/php-upload-security-testing.md)
- [Repository: Command Injection Template](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/resources/command-injections-template.py)
- [Apache HTTP Server: .htaccess files](https://httpd.apache.org/docs/current/howto/htaccess.html)
- [OWASP: File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [CWE-434: Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)

**Tags:** #PortSwigger #FileUpload #Apache #WebShell #ExtensionBlacklist
