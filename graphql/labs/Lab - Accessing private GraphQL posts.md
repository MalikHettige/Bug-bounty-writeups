# Accessing Private GraphQL Posts

**Platform:** PortSwigger Web Security Academy
**Category:** API Security / GraphQL / Access Control
**Difficulty:** Apprentice
**Date Solved:** 2026-10-28
**Severity:** Medium

## Summary

The blog application's frontend communicates with its backend through a single `POST /graphql/v1` endpoint rather than conventional REST routes. While the frontend only ever requests the specific fields it displays (title, body, author), the GraphQL schema itself exposes additional fields — including a `postPassword` field used to gate hidden/unlisted posts — that the UI never surfaces but the API will happily return if asked directly. Because GraphQL resolves whatever fields and arguments are included in the query/variables regardless of what the frontend's own JavaScript normally sends, an attacker can bypass the "hidden post" access control entirely by crafting a request that asks for fields and record IDs the application never intended to expose, revealing both the existence of a hidden post and the password required to view it.

## Affected Component

- `POST /graphql/v1` — single GraphQL endpoint backing the entire blog. Accepts arbitrary `query`, `operationName`, and `variables` (including an `id` parameter targeting a specific post) with no server-side restriction on which fields can be requested beyond what the schema technically allows.
- `GET /post?postId=N` — frontend blog post route. Returns `Not Found` for unlisted/hidden post IDs, giving the false impression those posts are inaccessible, while the backend GraphQL API still resolves and returns data for the same ID.

## Steps to Reproduce

1. Browsed the blog normally and used Burp to inspect the traffic behind each post. Every post load triggered a `POST /graphql/v1` request, with the request body containing `operationName`, a `query` string, and a `variables` object (e.g. `{"id": "N"}`), and the response body returning the matching post's JSON (title, body, author, etc.).
2. Tested basic ID manipulation first: changed `variables.id` to an out-of-range value (`1000`). Got back `200 OK` with `"getBlogPost": null` — confirmed the endpoint resolves arbitrary IDs rather than erroring, and a `null` result just means no post exists at that ID (not that the endpoint is protected).
3. Tried hand-editing the `query` string directly in Burp Repeater to add extra fields — this produced `400 "Invalid JSON"` repeatedly. GraphQL query strings are easy to break by hand (nested braces, exact field syntax), and Repeater has no GraphQL-aware editing, making manual queries error-prone and slow.
4. Noticed a discrepancy worth testing further: the frontend route `GET /post?postId=3` returned `Not Found`, while nothing on the backend indicated post ID `3` didn't exist — the frontend's 404 is a routing-level omission, not proof the backend refuses access to it.
5. Installed the **InQL** Burp extension specifically to handle GraphQL queries properly — it parses the schema and lets you select/add fields to a query by name instead of hand-editing JSON strings, avoiding the malformed-query errors from step 3.
6. Used InQL to query `getBlogPost` for `id: 3` requesting the full available field set (rather than only the fields the frontend normally requests). The response included a field the frontend never displays or requests: `"postPassword": "PASSWORD"`.
7. This confirmed the actual vulnerability: the GraphQL schema exposes a `postPassword` field on the `BlogPost` type that exists specifically to gate hidden posts — but nothing server-side stops a client from requesting that field directly, since GraphQL has no inherent concept of "the frontend doesn't ask for this field, so don't allow it."
8. Submitted the retrieved password value to access the hidden post and solve the lab.

## Proof of Concept

**Standard frontend-shaped request (only requests displayed fields):**
```json
POST /graphql/v1 HTTP/2
Content-Type: application/json

{
  "operationName": "getBlogPost",
  "variables": { "id": "3" },
  "query": "query getBlogPost($id: Int!) { getBlogPost(id: $id) { title body author } }"
}
```

**Modified request via InQL — requesting the undisclosed `postPassword` field:**
```json
POST /graphql/v1 HTTP/2
Content-Type: application/json

{
  "operationName": "getBlogPost",
  "variables": { "id": "3" },
  "query": "query getBlogPost($id: Int!) { getBlogPost(id: $id) { title body author postPassword } }"
}
```

**Response:**
```json
{
  "data": {
    "getBlogPost": {
      "title": "...",
      "body": "...",
      "author": "...",
      "postPassword": "PASSWORD"
    }
  }
}
```

Screenshot of the confirmed response in Burp/InQL:

<img width="1167" height="595" alt="image" src="https://github.com/user-attachments/assets/754b78cd-1d0c-4264-a0ba-33c65e3099f6" />

Submitted the recovered password to unlock the hidden post and solve the lab.

## Root Cause

GraphQL's core design lets a client request exactly the fields it needs, resolved by the schema rather than fixed per-endpoint like REST. That flexibility becomes a vulnerability when the schema defines a field that's meant to be internal-only (here, `postPassword`, effectively a secret/gate value) without a corresponding **field-level authorization check**. The application relied entirely on the frontend simply "not asking" for that field as its only protection — security by omission, not by enforcement. Since GraphQL schemas are discoverable (via introspection, a leaked schema file, or extensions like InQL that enumerate available fields), any field without explicit resolver-level access control is reachable by any client that knows — or can discover — its name.

## Impact

**Technical**
- Full bypass of the "hidden post" access control, exposing content and gating credentials (`postPassword`) that were never meant to be client-visible
- No authentication or privilege escalation required — any unauthenticated or low-privilege client can query the field directly
- Demonstrates a class of bug (over-fetching via unrestricted field access) that scales to any sensitive field defined in a GraphQL schema, not just this one

**Business / Real-World**
- In a real application, the equivalent field could just as easily be `passwordHash`, `email`, `isAdmin`, `internalNotes`, an API key, or billing/PII data — this lab's `postPassword` is a stand-in for a much broader class of schema-level data exposure
- Particularly dangerous because it requires no exploit chain — a single crafted query against a discoverable schema is enough
- GraphQL introspection being enabled (common in non-production-hardened deployments) makes schema/field discovery essentially free for an attacker

**Scope**
- Any record type in the GraphQL schema with a field lacking proper field-level authorization, not limited to blog posts

## Remediation

- Enforce field-level authorization in resolvers — a field like `postPassword` should check the requesting user's permissions server-side before returning any value, independent of what the frontend normally requests.
- Disable GraphQL introspection in production, or restrict it to authenticated/internal clients only, to reduce schema discoverability.
- Never rely on "the UI doesn't request this field" as an access control mechanism — GraphQL makes every defined field reachable by design; access control must live in the resolver/schema layer, not the client.
- Consider separating genuinely sensitive fields (credentials, secrets, gating values) into a schema that requires explicit elevated scope/permission to query at all, rather than co-locating them on a publicly queryable type.

## Lessons Learned & Patterns

- **Don't hand-edit GraphQL queries in Repeater.** Malformed query strings produce generic `400 Invalid JSON` errors that don't explain what's actually wrong — burned time on this before switching to a GraphQL-aware tool. **InQL** (or GraphQL Voyager / Altair for schema exploration) should be the first tool reached for on any GraphQL target, not Repeater with manual string editing.
- **A frontend 404 does not mean the backend enforces the same restriction.** `GET /post?postId=3` returning `Not Found` was purely a frontend routing gap — the backend GraphQL resolver had no issue returning data for `id: 3`. Always test backend endpoints independently of what the frontend UI exposes or blocks.
- **`null` on a GraphQL query is informative, not a dead end.** Getting `"getBlogPost": null` for an out-of-range ID confirmed the resolver executes and distinguishes "no record" from "access denied" — useful for ID enumeration since a consistent `null` response pattern can be scripted against.
- **Schema fields the frontend never requests are exactly where to look for over-fetching bugs.** The generalizable technique: pull the full schema via introspection (`__schema`/`__type` query) or a tool like InQL that generates one, diff it against what the frontend's actual queries request, and test every unused field directly — not just `postPassword`, but anything resembling a credential, PII, or internal-only field in any GraphQL target.
- **ID enumeration across a GraphQL endpoint is scriptable, not something to do by clicking through the UI.** Loop candidate `id` values against the GraphQL query directly (and cross-check against the frontend route to spot the "hidden from UI but live in the backend" pattern) rather than manually visiting every post in the browser.

## References

- PortSwigger Lab: Accessing private GraphQL posts
- PortSwigger Web Security Academy: GraphQL API vulnerabilities
- OWASP: GraphQL Cheat Sheet (Authorization section)

**Tags:** #PortSwigger #GraphQL #APISecurity #AccessControl #BrokenAccessControl
