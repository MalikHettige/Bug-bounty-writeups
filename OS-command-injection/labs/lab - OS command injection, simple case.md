# OS command injection, simple case

**Platform:** PortSwigger Web Security Academy
**Category:** OS Command Injection
**Difficulty:** Apprentice
**Date Solved:** 2026-10-23
**Severity:** High (demonstrated command execution; production severity depends on the execution context and reachable impact)

## Summary

The product stock-check feature is vulnerable to OS command injection. It accepts `productId` and `storeId` in a form-encoded request to `POST /product/stock`. The backend constructs a stock-check command using these values and passes the resulting string to a system shell without safely separating data from command syntax.

Replacing an identifier with the plain text `whoami` did not by itself demonstrate command execution: without shell syntax, it is just an argument to the stock-check command. The successful request used `productId=whoami&storeId=1|whoami`. The ampersand separates the two HTTP form fields; the pipe is part of the `storeId` value and is interpreted later by the shell. It pipes the stock-check command's output into a second `whoami` command, whose output is returned in the HTTP response as `peter-2gMyrH`.

## Affected Component

`POST /product/stock`

The request body is `application/x-www-form-urlencoded` and includes the `productId` and `storeId` parameters. The vulnerable operation is the server-side construction and shell execution of the stock-check command using these values.

## Steps to Reproduce

1. Open a product page and use the stock checker for one or more store options.
2. Intercept the resulting `POST /product/stock` request in Burp Suite and inspect its form body. It contains `productId` and `storeId`.
3. Test the values individually. Substituting plain `whoami` for an identifier does not add shell syntax; the value is only passed as an argument to the intended stock-check command.
4. In the authorized lab request, change the body to:

   ```text
   productId=whoami&storeId=1|whoami
   ```

5. Forward the request. The response includes `peter-2gMyrH`, demonstrating that the appended `whoami` command ran in the server process's operating-system context.

## Proof of Concept

The form body is not itself a shell command. The application parses the form fields first, then the vulnerable backend uses their values to construct a shell command. A simplified representation of the resulting command is:

```text
stockcheck.pl whoami 1|whoami
```

The shell parses this as a stock-check command on the left side of the pipe and a second `whoami` command on the right. The first `whoami` string is merely the supplied `productId` argument; it is not independently executed. The second `whoami`, introduced by the pipe in the `storeId` value, is the injected command. Its output is visible in the HTTP response.

<img width="1920" height="1080" alt="Burp Repeater request demonstrating the injected pipe and the operating-system username in the response; session cookie redacted" src="https://github.com/user-attachments/assets/8de1d6ef-10aa-408d-aab1-d6ff897369bb" />

## Root Cause

The application places attacker-controlled form values into a command string that is interpreted by an operating-system shell. Because the values are not kept separate from shell syntax, a shell metacharacter within a parameter changes the command's structure and causes an additional command to execute.

The two parsing layers are distinct:

- In the HTTP form body, `&` separates `productId` from `storeId`.
- After form parsing, the application incorporates each value into a shell command. The `|` inside the `storeId` value is then interpreted by the shell as a pipe operator; it does not separate the HTTP parameters.

## Impact

**Technical**
- An attacker able to reach the stock-check endpoint can cause the application server to execute an operating-system command in the context of the vulnerable process.
- The command's output is reflected in the response, providing a direct signal that execution occurred.

**Business / Real-World**
- Depending on the service account's permissions and the server's environment, command execution could expose application data, modify accessible files, disrupt the service, or provide a path to further compromise.
- The demonstrated lab request only ran `whoami`; access to other data or systems was not tested and is not claimed here.

**Scope**
- Demonstrated only against the isolated PortSwigger Web Security Academy lab. No production system was tested.

## Remediation

- Avoid invoking an operating-system shell for stock lookups; use an in-process library or a dedicated data/API operation instead.
- If an external executable is unavoidable, invoke it through a process API that passes a fixed executable and discrete argument values without a shell. Do not concatenate user input into a shell command string.
- Validate `productId` and `storeId` against the expected server-side identifiers and reject values outside those formats. Validation is defense in depth, not a substitute for avoiding shell interpretation.
- Run the application with the least privileges required and limit its filesystem, process, and network access.
- Add regression tests confirming that command metacharacters in both parameters remain ordinary rejected input and cannot alter the invoked operation.

## Lessons Learned & Patterns

- A request body can carry ordinary form data while the server later turns those values into executable shell syntax; inspect how the backend uses input, not just the request format.
- Plain text such as `whoami` is not inherently a command injection payload when it is passed as a normal argument. The vulnerable interpretation boundary is the shell, and the pipe in this lab changes the command structure there.
- When a parameter appears to be an identifier, test whether server-side use of that value crosses into a shell command, but do so only on systems where testing is explicitly authorized.
- Preserve the distinction between what a PoC directly proves (here, command execution and the process username) and broader potential impact that depends on permissions and environment.

## References

- [PortSwigger Web Security Academy: Lab — OS command injection, simple case](https://portswigger.net/web-security/os-command-injection/lab-simple)
- [PortSwigger: OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [CWE-78: Improper Neutralization of Special Elements used in an OS Command](https://cwe.mitre.org/data/definitions/78.html)

**Tags:** #PortSwigger #OSCommandInjection #CommandInjection #ShellInjection #InputHandling
