# Blind OS command injection with time delays

**Platform:** PortSwigger Web Security Academy
**Category:** OS Command Injection / Blind Injection
**Difficulty:** Practitioner
**Date Solved:** 2026-10-23
**Severity:** High (command execution demonstrated; real-world impact depends on the process privileges and environment)

## Summary

The feedback submission feature is vulnerable to blind OS command injection. User-supplied feedback details are incorporated into a server-side shell command. The command's output is not returned to the client, so a successful submission still produces the application's ordinary empty JSON response (`{}`). By appending a time-delay command to the `email` value, the lab's shell execution was delayed by approximately ten seconds, providing a time-based side channel that the injected command ran.

The successful lab value was `foo@bar.com||ping -c 10 127.0.0.1||`. In the form-encoded request, spaces appear as `+`, producing `foo@bar.com||ping+-c+10+127.0.0.1||`. The email-like prefix retained the expected shape while the shell interpreted the `||` operator after the application incorporated the value into its command.

## Affected Component

`POST /feedback/submit`

The form accepts feedback fields including `name`, `email`, `subject`, and `message`, as well as a CSRF token. The application uses user-supplied feedback details when invoking a server-side shell command. The `email` field was the injection point demonstrated in this lab.

## Steps to Reproduce

1. Open the lab homepage, select **Submit feedback**, and submit ordinary feedback. Inspect the resulting `POST /feedback/submit` request in Burp Suite.
2. Confirm that the request uses `application/x-www-form-urlencoded` and includes the feedback fields and CSRF token. A normal successful submission returns `{}`; this is the application's acknowledgement, not command output.
3. In the authorized lab request, retain the other valid feedback fields and set the email value to:

   ```text
   foo@bar.com||ping -c 10 127.0.0.1||
   ```

   In the encoded form body, the spaces may be represented as `+`:

   ```text
   email=foo@bar.com||ping+-c+10+127.0.0.1||
   ```

4. Forward the request and compare its response time with a normal feedback submission. The response body remains `{}`, but the injected `ping` causes an approximately ten-second delay and the lab reports as solved.

## Proof of Concept

The successful request body contained this email value:

```text
email=foo@bar.com||ping+-c+10+127.0.0.1||
```

The relevant response remained the normal empty JSON acknowledgement:

```json
{}
```

Because command output is not reflected, the evidence is the time difference between ordinary submission and the modified request—not text in the response body. The delay provides a time-based side channel for confirming execution in this lab.

<img width="1287" height="557" alt="Burp request with the time-delay payload in the feedback email field and the normal empty JSON response; session cookie and CSRF token redacted" src="https://github.com/user-attachments/assets/5ebf83c8-3938-47e9-b319-e8b8a0556a30" />

## Root Cause

The feedback handler builds or invokes a shell command using user-controlled feedback data without preventing shell interpretation. The shell therefore interprets metacharacters included in the `email` value as control syntax rather than treating the entire value only as email data.

The request and command-processing layers should not be confused:

- In `application/x-www-form-urlencoded`, `&` separates HTTP fields, `=` separates a field name from its value, `+` represents a space, and `%40` is percent-encoding for the literal `@` character.
- These transport encodings are decoded when the form is parsed; they are not, by themselves, server-side sanitization.
- After parsing, the application uses the `email` value in a shell command. In a shell, `||` is the logical-OR control operator: the command on its right runs when the preceding command returns a non-zero status. It is not the single pipe operator `|`.

The observation that the email-like prefix worked does not establish exactly which validation or parsing rule allowed the request. Earlier `whoami`, newline, and semicolon attempts returned an error or failed to save, but those outcomes alone do not prove whether validation, command syntax, or another application behavior caused the failure.

## Impact

**Technical**
- An attacker who can submit feedback may be able to cause commands to execute in the context of the web application process.
- Although command output is not directly reflected, time-based behavior can expose a reliable execution signal and may support further exploitation.

**Business / Real-World**
- Depending on process privileges, reachable resources, and available system utilities, command execution could expose or alter application data, affect service availability, or provide a route to further compromise.
- This lab demonstrated a timing side channel using `ping`; it did not test access to sensitive files, other systems, or broader host compromise.

**Scope**
- Demonstrated only against the isolated PortSwigger Web Security Academy lab. No production system was tested.

## Remediation

- Avoid invoking a shell for feedback processing. Use application libraries or APIs for the required functionality.
- If a separate executable is essential, invoke a fixed executable through a process API that passes arguments as discrete values without shell interpretation; never concatenate user-controlled values into a command string.
- Validate each feedback field against its business purpose and expected format. Treat validation as defense in depth, not as a substitute for avoiding shell execution.
- Run the application with least privilege and restrict its process, filesystem, and network capabilities.
- Add regression tests that submit shell metacharacters in each feedback field and verify they are rejected or handled strictly as data, with no command execution or timing difference.

## Lessons Learned & Patterns

- A normal response body such as `{}` does not rule out command execution. When output is suppressed, compare response timing against a baseline.
- Use the time-based behavior as the signal: `whoami` output would not necessarily be visible in a blind vulnerability, while a deliberate delay can be measured without relying on reflected output.
- Form encoding is a transport representation, not proof that values are safe for a shell. Decode the request fields conceptually before reasoning about how the application may use them.
- Shell operators have different semantics: `||` conditionally runs the right-hand command after a non-zero exit, `&&` does so after a zero exit, `;` sequences commands, and `|` connects one command's standard output to another's standard input. Do not assume an operator works without verifying it in the authorized test environment.
- Server errors and failed submissions are ambiguous evidence. Record them as observations, but do not infer a specific filter or validation rule without confirming it.

## References

- [PortSwigger Web Security Academy: Lab — Blind OS command injection with time delays](https://portswigger.net/web-security/os-command-injection/lab-blind-time-delays)
- [PortSwigger: OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [CWE-78: Improper Neutralization of Special Elements used in an OS Command](https://cwe.mitre.org/data/definitions/78.html)

**Tags:** #PortSwigger #OSCommandInjection #BlindInjection #TimeBasedDetection #FeedbackForm
