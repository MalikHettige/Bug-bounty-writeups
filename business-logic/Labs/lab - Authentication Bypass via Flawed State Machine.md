# Authentication Bypass via Flawed State Machine

**Platform:** PortSwigger Web Security Academy

**Category:** Business Logic

**Difficulty:** Practitioner

**Date Solved:** YYYY-MM-DD

**Severity:** High

## Summary

The application assigns a user's session role through a multi-step post-login sequence: `POST /login` → `GET /role-selector` → home page. The role-selection step is not enforced server-side as a mandatory prerequisite for reaching authenticated pages. By dropping the `GET /role-selector` request after a successful login and navigating directly to the home page, the session is left in an unintended default state that carries **administrator** privileges instead of the lowest-privilege default or an access-denied response.

This is a **flawed state machine** vulnerability: the server trusts the client to walk the workflow in order and fails *open* when a step is skipped. A standard low-privilege user can escalate to full administrator with no payload, injection or brute force required.

## Affected Component

```ocaml
https://[LAB-ID].web-security-academy.net/role-selector
```

```ocaml
POST /login HTTP/2
GET /role-selector HTTP/2
```

The role-selection step and the session role state it is responsible for setting.

## Steps to Reproduce

1. Start Burp Suite and enable the proxy intercept.
2. In the browser, log in as the standard low-privilege user (`wiener:peter`).
3. Forward the `POST /login` request normally; the server responds with a redirect to `/role-selector`.
4. Intercept the subsequent `GET /role-selector` request and click **Drop** so the role-selection step never completes.
5. Turn intercept off, then manually navigate to the application's home page (`/`) through the URL bar.
6. Observe that the session now has administrator-level access, even though no role was ever selected. The **Admin panel** link appears in the navigation.
7. Open the admin panel (`/admin`) and delete the user `carlos` to confirm the privileged action succeeds and solve the lab.

## Proof of Concept

#### Intended workflow

```ocaml
POST /login HTTP/2            -> 302 Location: /role-selector
GET  /role-selector HTTP/2    -> user chooses a role, server records it in the session
GET  /                        -> authenticated home page with the chosen role
```

#### Attack workflow

```ocaml
POST /login HTTP/2            -> 302 Location: /role-selector   (forwarded)
GET  /role-selector HTTP/2                                      (DROPPED in Burp)
GET  /                        -> authenticated home page, session role = administrator
GET  /admin                   -> 200 OK, admin panel accessible
GET  /admin/delete?username=carlos -> user deleted
```

> The important change is that the `role-selector` request is never allowed to reach the server. The session is authenticated but has no confirmed role, and the server resolves that missing state to `administrator`.

<!-- Add screenshot references here, e.g. ![Admin panel after dropping /role-selector](assets/<filename>.png) -->

## Root Cause

The server treats arrival at the authenticated home page as implicit confirmation that the role-selection step was completed. It does not verify that an explicit, valid role choice was recorded for the session before granting role-gated access.

When the step is skipped, the session's role falls back to an unvalidated internal default that happens to be `administrator`. The workflow therefore **fails open** rather than failing closed (redirecting back to role selection, or defaulting to the lowest privilege level). Two defects combine here:

- **Insufficient workflow validation:** step order is enforced only by the client-side navigation flow, not by server-side state.
- **Insecure default:** an undefined role resolves to the highest privilege level.

## Impact

**Technical**
- Any authenticated user can escalate to administrator by interrupting a single request in the login flow.
- Grants access to all administrative functionality, including user management and account deletion.
- Requires no payload, injection or special tooling beyond an intercepting proxy.

**Business / Real-World**
- Full compromise of the application's authorization model; role assignment can no longer be trusted.
- Unauthorized modification or deletion of user accounts and data, with integrity, confidentiality and availability consequences.
- In a multi-tenant or regulated environment, privilege escalation of this kind would typically be rated High to Critical depending on what the administrator role can reach.

**Scope**
- Affects every account that can authenticate, because the bypass happens in the shared post-login flow.
- Applies to any endpoint gated on the session role, not just the admin panel.

## Remediation

1. **Assign the role atomically with session creation.** Do not rely on a separate, skippable step reachable through direct navigation.
2. **Fail closed.** Any session without an explicitly confirmed role must default to the lowest privilege level, or to no access at all, never to an undefined or elevated state.
3. **Validate on every role-gated endpoint.** Confirm server-side that a valid role selection exists for the session, regardless of how the user navigated there.
4. **Track workflow state server-side.** Reject any transition whose required previous state has not been reached.

```ocaml
if session.role is None:
    redirect_to("/role-selector")   # or deny access

otherwise:
    authorize(session.role)
```

## Lessons Learned & Patterns

- Multi-step flows (onboarding, role or workspace selection, verification steps, checkout) are a recurring source of state-machine bugs. For each one, intercept and **drop a single step**, then navigate directly to a later step and observe how the server resolves the missing state.
- Test what the server does with **missing** state, not only with *wrong* state. Insecure defaults (null resolving to admin, empty resolving to allowed) are a distinct bug class from tampered values.
- Pattern question to ask on every target: *what step is the server assuming already happened, and what happens if it didn't?*
- Related labs in this topic: Insufficient Workflow Validation (skipping to a later step), Inconsistent Security Controls (state differs by path).

## References

- [PortSwigger — Authentication bypass via flawed state machine](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine)
- [PortSwigger — Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws)
- [OWASP WSTG — Testing for the Circumvention of Work Flows](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/06-Testing_for_the_Circumvention_of_Workflows)
- [OWASP — Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [MITRE CWE-841 — Improper Enforcement of Behavioral Workflow](https://cwe.mitre.org/data/definitions/841.html)

**Tags:** #PortSwigger #BusinessLogic #StateMachine #PrivilegeEscalation #AuthenticationBypass
