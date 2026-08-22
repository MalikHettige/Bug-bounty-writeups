**Lab:** [PortSwigger Web Security Academy](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)

**Date Solved:** 2026-08-22

**Difficulty:** Apprentice 

Goal: Reset **Carlos’s** password — then log in as Carlos and open his account page.

**Severity:**  High (8.1)

**CWE:** CWE-639 – Authorization Bypass Through User-Controlled Key / CWE-862 – Missing Authorization

## Summary

The password reset functionality fails to properly bind the final password-change request to the reset token. The server trusts the client-supplied `username` parameter in the `POST /forgot-password` request. An attacker who initiates a password reset for their own account can change the `username` parameter to any other valid user (e.g. `carlos`) and set a new password for that account, resulting in full account takeover.

## Affected Component

`POST /forgot-password?temp-forgot-password-token=<TOKEN>` 

## Steps to Reproduce

1. Log in as wiener (or simply go to the login page) and click **Forgot your password?**.
2. Enter the username wiener and submit the form.
3. Open the **Email client**, click the password reset link, and set a new password (e.g. password123).
4. Intercept the final `POST /forgot-password?temp-forgot-password-token=`... request in Burp Suite.
5. In the request body, change the username parameter from wiener to carlos.
6. Optionally clear the value of the temp-forgot-password-token parameter (leave the parameter name).
7. Forward the modified request.
8. Log out (if needed) and log in with:
    - Username: carlos
    - Password: the one you set in step 3
9. Access the **My account** page to solve the lab.

### **Proof of Concept**

```nix
POST /forgot-password?temp-forgot-password-token= HTTP/2
Host: <LAB_ID>.web-security-academy.net
Cookie: session=<wiener_session>
Content-Type: application/x-www-form-urlencoded

temp-forgot-password-token=&username=carlos&new-password-1=password123&new-password-2=password123
```

**Result:** The server responds with 302 Found and successfully updates the password for the user carlos.

Logging in with the credentials carlos:password123 grants full access to Carlos’s account, confirming complete account takeover.
## Root Cause

## Impact

- **Technical:** Any authenticated user (or an attacker who can trigger a password reset) can reset the password of arbitrary accounts without knowing the victim’s reset token or current password.
- **Business / Real-World:** Complete account takeover of any user, including high-privilege accounts. This can lead to data theft, unauthorized actions, privilege escalation, and further compromise of the application.
- **Scope:** Affects all users of the application who have password reset functionality enabled.

## Remediation

- Always validate the reset token on the final password-change request.
- Derive the target username/account from the server-side token, never from client-supplied parameters.
- Invalidate the token immediately after successful use.
- Ensure the token is cryptographically strong, single-use, and time-limited.

## Lessons Learned & Patterns

- Never trust client-supplied identity parameters (`username`, `email`, `user_id`, etc.) in sensitive multi-step flows such as password reset, email change, or account recovery. The server must enforce the binding between the token and the account on every step.

**Pattern to look for:**

- Final confirmation requests in multi-step authentication or account recovery flows that still accept a user identifier parameter.

### **References:**

- PortSwigger Lab – Password reset broken logic
- CWE-639: Authorization Bypass Through User-Controlled Key
- CWE-862: Missing Authorization

**Tags:** `#PortSwigger` `#Authentication` `#BrokenAuthentication` `#PasswordReset` `#IDOR` `#AccountTakeover` `#BrokenAccessControl`
