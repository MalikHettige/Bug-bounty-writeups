# Insufficient Workflow Validation

**Platform:** PortSwigger Web Security Academy

**Category:** Business Logic 

**Difficulty:** Practitioner 

**Date Solved:** 2026-09-23

**Severity:** Medium 

## Summary

The application failed to enforce the expected order of operations during the checkout workflow. By directly requesting the final `order-confirmation` endpoint, it was possible to skip the required preceding checkout steps. The server accepted the request and completed the workflow without verifying that the required previous state had been reached. This demonstrates an **insufficient workflow validation** flaw caused by relying on the expected client-side request sequence rather than enforcing workflow state server-side.

## Affected Component

```ocaml
https://[LAB-ID].web-security-academy.net/cart
```

```ocaml
GET /cart/order-confirmation?order-confirmed=true HTTP/2
```

## Steps to Reproduce

1. In the home-page, open an item
2. In burp proxy go to HTTP history and locate `GET /product?productId=7 HTTP/2` (my item was product=7)
3. Send it to repeater (Ctrl+R)
4. Replace the starting line of the request with the following POC 
5. Append the URL in Referer header with `/cart`
6. Send the request (Ctrl+space) 
7. Observe the response pane confirms the bug by showing **200OK**  
8. Go back to the application and refresh the page 
9. The lab is solved because the application accepted the final workflow step without requiring the preceding checkout stages.

## Proof of Concept

#### Captured request

```ocaml
GET /product?productId=7 HTTP/2

Referer: https://0a790054030ab50f804a5dcb001e008d.web-security-academy.net/product?productId=7
```

#### Modified request

```ocaml
GET /cart/order-confirmation?order-confirmed=true HTTP/2

Referer: https://0a790054030ab50f804a5dcb001e008d.web-security-academy.net/product?productId=7
```

> The important change is that the request directly invokes the final `order-confirmation` workflow step instead of completing the expected preceding checkout operations.

<img width="1471" height="868" alt="image" src="https://github.com/user-attachments/assets/ba899c58-07df-4a8c-95ff-ab47c614c752" />


## Root Cause

The application relied on the expected sequence of client-side requests instead of enforcing the workflow state on the server. The `order-confirmation`endpoint did not sufficiently verify that all required preceding actions had been completed before processing the request. The missing server-side state validation allowed a later workflow step to be invoked independently of its prerequisites. Conceptually, the intended workflow was similar to supposedly: In checkout complete required purchase steps before order confirmation. However, the application effectively allowed any authenticated attacker to jump Directly to the request to order-confirmation leading the order to be completed. 

## Impact

- Skip required business-process steps.
- Invoke later stages of a transaction directly.
- Bypass controls implemented only through the normal application flow.
- Cause the application to accept an invalid transaction state.

## **Technical**

An attacker could:

- Skip required workflow stages.
- Directly invoke a later-stage endpoint.
- Bypass controls implemented through the normal application flow.
- Cause the application to accept an invalid workflow state.
- Potentially complete a transaction without satisfying the intended prerequisites.

## **Business / Real-World**

In a real-world application, insufficient workflow validation could allow an attacker to bypass mandatory purchasing or transaction steps.

Depending on the affected workflow, this could result in:

- Unauthorized purchases or transactions.
- Financial loss to the company (considering the free-purchase bug)
- Incorrect order states.
- Abuse of discounts, credits, or other transaction controls.
- Inventory or fulfillment inconsistencies.

For this lab, the demonstrated impact is the ability to complete the purchase workflow without following the required checkout process.

## **Scope**

The affected functionality is the application's checkout/order-confirmation workflow, specifically the transition to:

```
/cart/order-confirmation
```

## Remediation

The application should:

1. Maintain the current workflow state server-side.
2. Validate the expected previous state before every sensitive transition.
3. Reject requests that attempt to skip required stages.
4. Avoid relying on hidden fields, URLs, JavaScript, or UI navigation to enforce workflow order.
5. Ensure that completing an endpoint directly cannot produce a valid transaction without its required prerequisites.

```ocaml
if current_state != EXPECTED_PREVIOUS_STATE:
reject_request()

otherwise:
perform_transition()
```

## Lessons Learned & Patterns

- When testing business logic, identify the **workflow states and transitions**, then test whether the server actually enforces them.

A particularly useful test is to capture a legitimate later-stage request and replay it without performing the preceding workflow steps. If the server accepts the request anyway, investigate for **workflow bypass / insufficient workflow validation**.

## References

- **PortSwigger — Insufficient workflow validation** — https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-insufficient-workflow-validation
- **OWASP WSTG — Circumvention of Workflows** — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Workflows
- **OWASP — Business Logic Security Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html
- **OWASP — REST Security Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- **MITRE CWE-841 — Improper Enforcement of Behavioral Workflow** — https://cwe.mitre.org/data/definitions/841.html

**Tags:** #PortSwigger #IDOR #AccessControl
