# Lab - File path traversal, validation of start of path

**Platform:** PortSwigger Web Security Academy<br>
**Category:** Path Traversal<br>
**Difficulty:** Practitioner<br>
**Date Solved:** 2026-10-25<br>
**Severity:** High — CVSS 3.1: 7.5 (conditional estimate), CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N.

## Summary

The product-image endpoint required the `filename` value to begin with the expected image-directory path. The check did not ensure that the resolved file stayed within that directory. By retaining the expected prefix while adding path components that resolved outside it, the lab request returned `/etc/passwd` contents with `HTTP/2 200 OK`.

The important distinction was that the parameter needed to contain the expected base path; replacing the whole value or changing the parameter name did not meet the endpoint's input contract.

## Affected Component

- Product image endpoint: `GET /image?filename=...`
- Lab: [File path traversal, validation of start of path](https://portswigger.net/web-security/file-path-traversal/lab-validate-start-of-path)

## Steps to Reproduce

1. In the authorized PortSwigger lab, open a product and inspect the request used to display its image.
2. In Burp Suite HTTP history, locate the image request and note the `filename` parameter, including the image-directory prefix and image name.
3. Keep the parameter name and required prefix intact while testing whether the path can resolve outside the intended image directory.
4. Send the modified request in the lab. The response returned `HTTP/2 200 OK` and a large body containing `/etc/passwd` entries.

## Proof of Concept

As requested, this report uses a Bash request example rather than a screenshot. The lab host and exact traversal value are intentionally left as placeholders:

```bash
LAB_URL='https://<your-authorized-lab-host>'
LAB_FILENAME='<expected-image-directory>/<redacted-lab-path>'

curl --http2 --include \
  --get \
  --data-urlencode "filename=${LAB_FILENAME}" \
  "${LAB_URL}/image"
```

**Observed result:** `HTTP/2 200 OK`; the response body contained a long list of account and system entries from `/etc/passwd`.

## Root Cause

The application validated only that the submitted path started with an expected directory string. A string-prefix check is not equivalent to checking the final resolved path: a value can begin with the approved prefix yet resolve elsewhere after filesystem path normalization.

## Impact

**Technical**
- A user could cause the endpoint to return local files readable by the application process, subject to its permissions and filesystem layout.
- The lab demonstrated reading `/etc/passwd`, which commonly contains account metadata rather than password hashes.

**Business / Real-World**
- If sensitive application files or secrets are readable by the vulnerable process, unauthorized disclosure could expose credentials, configuration, or other data.
- Actual impact depends on access controls, path resolution behavior, operating system, and the files readable by the application process.

**Scope**
- Demonstrated only against the isolated PortSwigger Web Security Academy lab. No production system was tested.

## Remediation

- Avoid accepting filesystem paths from users; use server-side identifiers mapped to approved files.
- Do not rely on a raw string-prefix check. Canonicalize the candidate path and verify it remains within the intended directory using a path-aware boundary check.
- Account for path separators, normalization, symbolic links, and platform-specific filesystem behavior.
- Apply least-privilege filesystem permissions to limit the impact of unintended file reads.

## Investigation Notes

- **Initial hypothesis:** The issue seemed similar to a request-validation mismatch, such as confusing a request line with a header check. Here, however, the relevant input was specifically the `filename` parameter that the image handler used.
- **Parameter discovery:** Replacing the parameter name or omitting `filename` led to a missing-parameter response. Supplying a non-existent image did not establish traversal; the key was understanding that the server checked for a required path prefix.
- **Breakthrough:** Keeping the expected image-directory prefix and testing path resolution beyond it satisfied the start-of-path check while escaping its intended directory.

## Lessons Learned & Patterns

- A path that starts with an approved directory string is not necessarily contained within that directory after filesystem resolution.
- Preserve the endpoint's required parameter and expected input structure while assessing how validation is applied.
- Validate the canonical resolved path with a path-aware containment check, not a naive string-prefix comparison.
- `/etc/passwd` is a proof file in the lab, not evidence that password hashes or every system file are exposed.

## References

- [PortSwigger Web Security Academy: File path traversal, validation of start of path](https://portswigger.net/web-security/file-path-traversal/lab-validate-start-of-path)
- [PortSwigger: Directory traversal](https://portswigger.net/web-security/file-path-traversal)
- [Path traversal wordlist](https://github.com/MalikHettige/Bug-bounty-writeups/blob/main/resources/Path-traversal-wordlist.txt)
- [OWASP: Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)

**Tags:** #PortSwigger #PathTraversal #FileDisclosure
