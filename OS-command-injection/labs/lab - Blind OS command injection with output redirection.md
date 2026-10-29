# Blind OS command injection with output redirection

**Platform:** PortSwigger Web Security Academy
**Category:** OS Command Injection / Blind Injection
**Difficulty:** Practitioner
**Date Solved:** 2026-10-23
**Severity:** High (command execution and retrieval of command output demonstrated; real-world impact depends on process privileges and application configuration)

## Summary

The feedback feature is vulnerable to blind OS command injection. The server uses user-controlled feedback data in a shell command, but does not include command output in the feedback response. In this lab, output from a harmless identity command was redirected to a text file in a directory served by the application. A separate image-loading endpoint then returned that file's contents.

This demonstrates a different capability from time-delay testing: a delay can indicate that a command ran, while a writable, readable file location can provide a channel to retrieve its output. The feedback request continued to return the normal empty JSON response (`{}`); the command output was read separately.

## Affected Components

- `POST /feedback/submit` — accepts user-supplied feedback fields, including `email`, and incorporates feedback data into a server-side shell command.
- `GET /image?filename=<output-file>` — serves files from the application's image location, which in the lab made the redirected output retrievable.

## Steps to Reproduce

1. Submit ordinary feedback from the homepage and inspect the `POST /feedback/submit` request.
2. Confirm that the normal successful response is `{}` and does not contain command output.
3. In the authorized lab, modify the `email` value so that output from the lab's harmless identity command is directed to a text file in the application's web-accessible image location. The exact command string is omitted here.
4. Forward the feedback request. The response remains `{}`; this confirms only the application's ordinary acknowledgement and is not where the command output appears.
5. Request the text file through the image-loading endpoint, using the same filename chosen for the output file (for example, `solved.txt`).
6. Observe the returned file contents: `peter-l648Ef`. This is the command output retrieved through the separate file-serving feature.

## Proof of Concept

The test involved two requests:

1. A modified `POST /feedback/submit` request that directed the identity command's output to a text file in the application's served image directory.
2. A `GET /image?filename=...` request for that same text file.

The feedback endpoint returned HTTP `200 OK` with `{}`. The image-loading request returned HTTP `200 OK` with:

```text
peter-l648Ef
```

This report intentionally omits the executable injection string. The evidence is the matching output returned by the separate file read in the isolated lab.

## Root Cause

The feedback handler passes attacker-controlled data into a shell command without safely separating data from shell syntax. This permits command execution and shell output redirection. The impact is amplified by the application's ability to write command output into a location that is also readable through a separate web feature.

The vulnerable trust boundary spans two features: feedback processing can write to the filesystem, while the image-serving endpoint exposes files from the same application-managed location. A file intended to contain generated content should not become a bridge for retrieving command output.

## Impact

**Technical**
- Blind command execution can be used to write command output to a file.
- A separate file-serving endpoint can expose that output, converting an otherwise blind execution path into a data retrieval channel.

**Business / Real-World**
- Depending on the server process's permissions and the information accessible to it, an attacker could retrieve sensitive data, alter application-served content, or use command execution for further compromise.
- The lab demonstrated retrieval of the process identity only. It did not test access to credentials, user data, or other systems.

**Scope**
- Demonstrated only against the isolated PortSwigger Web Security Academy lab. No production system was tested.

## Remediation

- Avoid invoking an operating-system shell to process feedback. Use application libraries or APIs for the intended operation.
- If an external executable is essential, invoke a fixed executable with discrete arguments through a process API that does not interpret a shell command string.
- Do not allow user-controlled data to select arbitrary filesystem paths. Enforce a strict mapping from opaque identifiers to approved files and canonicalize paths before access.
- Keep writable application data outside web-served directories. If files must be served, allow-list expected names and types and prevent access to arbitrary files.
- Apply least privilege so the feedback handler cannot write to locations exposed by unrelated application features.
- Add regression tests that verify feedback fields cannot alter process execution and that file-serving routes cannot retrieve unapproved files.

## Lessons Learned & Patterns

- Blind command injection can leak output when the application has a second feature that reads files written by the vulnerable process.
- Time delays confirm behavior indirectly; output redirection plus an independently readable file can disclose command results. These are distinct proof techniques.
- For a file-based channel, the output filename used by the write operation must match the filename requested through the read feature.
- An empty success response such as `{}` is not proof that nothing else happened server-side; verify observable side effects using safe, authorized evidence.
- Treat writable directories and file-serving endpoints as one security boundary when assessing whether generated files can be read or overwritten.

## References

- [PortSwigger Web Security Academy: Lab — Blind OS command injection with output redirection](https://portswigger.net/web-security/os-command-injection/lab-blind-output-redirection)
- [PortSwigger: OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [CWE-78: Improper Neutralization of Special Elements used in an OS Command](https://cwe.mitre.org/data/definitions/78.html)

**Tags:** #PortSwigger #OSCommandInjection #BlindInjection #OutputRedirection #FileDisclosure
