**Lab:** PortSwigger Web Security Academy

**Date Solved:** 2026-08-25

**Difficulty:** Practitioner 

**Severity**: High — CVSS 8.1 (High, lab-context assessment)

## Summary
The password-change endpoint leaks whether the supplied current password is valid through distinguishable responses. By fuzzing the current-password parameter and identifying the response anomaly, an attacker can brute-force the victim’s password and potentially achieve account takeover.

## Affected Component

`POST https://<LAB_ID>.web-security-academy.net/my-account/change-password HTTP/1.1`

## Steps to Reproduce

1. Navigate to my account
2. Log in as wiener

Observe the `change-password`page loads in right after getting authenticated

1. In Current password box input the current password (`peter`)
2. Input 2 different arbitrary strings for ‘New password’ and ‘Confirm new password’ and click **Change password**

Note that the mismatched new passwords prevent the account-locking behavior that happens when the new passwords match.

1. In ZAP’s History tab, look for the affected component request 

History tab is one of top tabs and it is easier to locate the request when sort out with Method

1. Click the request and then click request in main toolbar 
2. Right click the Request and click ‘Open in requester lab’ or Ctrl + W
3. In requester tab, replace the username value with the victim’s — from wiener to `carlos`
4. Click send button, right click that request again and click Fuzz 
5. In the Fuzzer window, select the value of `current-password=` , click add 
6. After payload window appears click add again 
7. Type: strings, in contents paste the candidates usernames
8. Hit ok in both windows and start Fuzzer 
9. Confirm the Fuzzer is complete in Fuzzer control bar (it shows 100% in a horizontal progress-bar)

When `username=carlos`was set along with 

`current-password=<the_payload_from_the_candidate_list)>`,
`new-password-1` and `new-password-2` to **two different values**.

The two possible outcomes are either

Wrong current password → response contains "Current password is incorrect"  or
Correct current password → response contains "**`New passwords do not match`**" 

1. Find the correct password in the results
- Click the column header `Size Resp. Body`to sort the results.
- Look for the one row that has a different size and click it
- Go to response tab, click anywhere inside the Response Body and search or just Ctrl+F for the phrase “`New passwords do not match.`”
1. After confirming, right click the the response body and click Open URL in Browser + select the browser (Firefox would be a good choice)

### **Proof of Concept**

The password-change endpoint allows repeated attempts against the current password while providing distinguishable responses for valid and invalid credentials. By fuzzing the `current-password` parameter and comparing responses, the valid password can be identified from the anomalous response.


<img width="1661" height="290" alt="image" src="https://github.com/user-attachments/assets/35215881-2ec0-48b0-abe5-9bd5ccab1ab7" />


#### Captured request

```coffeescript
POST
https://<LAB_ID>.web-security-academy.net/my-account/change-passwordHTTP/1.1
host:<LAB_ID>.web-security-academy.net

username=wiener&current-password=peter&new-password-1=test1&new-password-2=test2
```

#### Comparison (In responses)

```haskell
Invalid candidate
→ 200 OK
→ "Current password is incorrect"

Correct candidate
→ 200 OK
→ "New passwords do not match"
```

**Note:** The valid password did not return a `302` redirect in this lab. Instead, the server returned `200 OK` with the message **“`New passwords do not match`.”** 
This difference is the important indicator: it shows that the current password was accepted, while the intentionally mismatched new passwords triggered the validation message. Therefore, the response body—not the HTTP status code—was used to identify the correct password.

**Another note:** In a real-world assessment, we generally won't know the exact response string in advance. First establish a baseline, then send controlled variations and compare the responses for differences in status codes, response length, body content, headers, redirects, or application behavior. Once a reliable difference is discovered, that behavior can be used as the **response oracle** for filtering or identifying interesting results during automated testing.

## Root Cause

The password-change endpoint creates a **password oracle** because it produces distinguishable responses depending on whether the supplied current password is valid.

## Impact

- **Technical:** Enables brute-force discovery of the victim’s current password through the password-change functionality, potentially leading to account takeover.
- **Business / Real-World:** An attacker could gain unauthorized access to a victim’s account and any sensitive data or functionality available to that account.
- **Scope:** Password-change functionality affecting the authenticated user's account.

## Remediation

Ensure the password-change flow does not expose a distinguishable response that allows an attacker to determine whether the current password was correct, while also enforcing appropriate anti-automation protections.

## Lessons Learned & Patterns

- **General takeaway:** A password-change flow can become a **password-validity oracle** when different responses reveal whether the current password is correct.
- **Don't rely on status codes:** The correct candidate returned `200 OK`, just like the incorrect candidates. The useful signal was the **different response body**: `New passwords do not match`.
- **Find the oracle before fuzzing:** Establish a baseline with a known-wrong password, then use a known-correct password with intentionally mismatched new passwords. Compare the responses to discover the application's distinguishing behavior.
- **Automate the discovered signal:** Once the oracle is understood, place the candidate values in the `current-password` parameter and use the distinctive response as the filter/match condition.
- **Verify the outlier:** A different response size or result only identifies a candidate worth investigating. Inspect the response and manually confirm that the difference actually represents a valid current password.
- **Reusable lab pattern:** `Baseline → understand the logic → create the oracle → fuzz → identify the outlier → inspect → verify`.

## References

- [PortSwigger Web Security Academy — Lab: Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Web Security Testing Guide — Testing for Weak Password Change or Reset Functionalities](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/09-Testing_for_Weak_Password_Change_or_Reset_Functionalities)

**Tags:** #Authentication #BruteForce #AccountTakeover #PasswordSecurity #RateLimiting #BusinessLogic #PortSwigger
